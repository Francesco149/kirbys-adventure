"""env.py — the TAS workbench: a movie (per-frame inputs from power-on) driven on a deterministic core,
with checkpoints, rewind, named RAM variables, screenshots and a parallel beam search.

Input spec language (used by the agent, the movie file and the search):
  token      := buttons ['*' count]          e.g.  R*20   RA*8   .*30   T
  buttons    := '.' (nothing) | letters from  A B U D L R T(start) S(select) X(soft reset, console button)
  group      := '(' tokens ')' 'x' count     e.g.  (B*2 .*2)x10   (mash B)
Frames are applied left to right; whitespace or commas separate tokens.
"""
import ast
import base64
import hashlib
import io
import json
import math
import os
import re
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from PIL import Image, ImageDraw

import nes

LETTERS = {"A": nes.A, "B": nes.B, "S": nes.SELECT, "T": nes.START,
           "U": nes.UP, "D": nes.DOWN, "L": nes.LEFT, "R": nes.RIGHT, "X": nes.RESET}
ORDER = "XUDLRABST"
LAG_COUNTER = 0x603D   # Kirby's Adventure: +1 on every frame the main loop completes; unchanged = lag/loading


def mask_str(m):
    s = "".join(c for c in ORDER if m & LETTERS[c])
    return s or "."


_TOK = re.compile(r"\s*(?:(\()|(\))\s*x\s*(\d+)|([.ABUDLRSTX]+)(?:\s*\*\s*(\d+))?)\s*,?")


def parse_spec(spec, limit=200_000):
    """Input spec → list of masks."""
    spec = spec.strip()
    stack = [[]]
    pos = 0
    while pos < len(spec):
        m = _TOK.match(spec, pos)
        if not m or m.end() == pos:
            raise ValueError(f"bad input spec near: {spec[pos:pos + 20]!r}")
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            if len(stack) == 1:
                raise ValueError("unbalanced ')'")
            body = stack.pop()
            stack[-1].extend(body * int(m.group(3)))
        else:
            letters = m.group(4)
            mask = 0
            for ch in letters:
                if ch != ".":
                    mask |= LETTERS[ch]
            stack[-1].extend([mask] * int(m.group(5) or 1))
        if len(stack[-1]) > limit:
            raise ValueError(f"spec longer than {limit} frames")
    if len(stack) != 1:
        raise ValueError("unbalanced '('")
    return stack[0]


def parse_fm2(path):
    """FCEUX .fm2 → masks (commands: bit0 soft reset → X; a hard reset on frame 0 is our power-on)."""
    masks = []
    for line in open(path, errors="replace"):
        if not line.startswith("|"):
            continue
        parts = line.split("|")
        cmd = int(parts[1] or 0)
        pad = parts[2]
        m = 0
        for ch, k in zip(pad, ["R", "L", "D", "U", "T", "S", "B", "A"]):
            if ch not in ". ":
                m |= LETTERS[k]
        if cmd & 1:
            m |= nes.RESET
        masks.append(m)
    return masks


def rle(masks):
    """masks → compact spec (run-length)."""
    out, i = [], 0
    while i < len(masks):
        j = i
        while j < len(masks) and masks[j] == masks[i]:
            j += 1
        n = j - i
        out.append(mask_str(masks[i]) + (f"*{n}" if n > 1 else ""))
        i = j
    return " ".join(out)


# ---------------------------------------------------------------- RAM variables + safe expressions
_ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp, ast.IfExp, ast.Call,
            ast.Name, ast.Load, ast.Constant, ast.Subscript, ast.Slice, ast.Tuple,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.BitAnd, ast.BitOr,
            ast.BitXor, ast.LShift, ast.RShift, ast.USub, ast.UAdd, ast.Not, ast.Invert, ast.And, ast.Or,
            ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn)
_FUNCS = {"min": min, "max": max, "abs": abs, "int": int,
          "s8": lambda v: v - 256 if v >= 128 else v,
          "s16": lambda v: v - 65536 if v >= 32768 else v}


def compile_expr(src, names):
    tree = ast.parse(src, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED):
            raise ValueError(f"not allowed in expressions: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in names and node.id not in _FUNCS \
                and node.id not in ("ram", "frame", "start", "lag"):
            raise ValueError(f"unknown name {node.id!r}; known: {', '.join(sorted(names))}")
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id in _FUNCS):
            raise ValueError("only min/max/abs/int/s8/s16 calls are allowed")
    return compile(tree, "<expr>", "eval")


class RamVars:
    """Named RAM variables: raw ones {addr, size, signed} and derived ones {expr}."""

    def __init__(self, path):
        self.path = path
        self.defs = json.load(open(path)) if os.path.exists(path) else {}
        self._compile()

    def _compile(self):
        self._derived = {}
        for name, d in self.defs.items():
            if "expr" in d:
                self._derived[name] = compile_expr(d["expr"], set(self.defs))

    def define(self, name, addr=None, size=1, signed=False, expr=None, desc="", event=False):
        if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
            raise ValueError("names are lower_snake_case")
        d = {"desc": desc, "event": bool(event)}
        if expr:
            d["expr"] = expr
        else:
            a = int(str(addr), 0)
            if not (0 <= a < 0x800 or 0x6000 <= a < 0x8000):
                raise ValueError("addr must be in $0000-$07FF (system RAM) or $6000-$7FFF (cart WRAM)")
            d.update(addr=f"0x{a:04X}", size=int(size), signed=bool(signed))
        old = self.defs.get(name)
        self.defs[name] = d
        try:
            self._compile()
        except Exception:
            if old is None:
                del self.defs[name]
            else:
                self.defs[name] = old
            self._compile()
            raise
        json.dump(self.defs, open(self.path, "w"), indent=1)

    def remove(self, name):
        self.defs.pop(name, None)
        self._compile()
        json.dump(self.defs, open(self.path, "w"), indent=1)

    def read(self, ram, frame=0):
        """ram: a nes.Mem view (Python ints, CPU addresses)."""
        out = {}
        for name, d in self.defs.items():
            if "addr" in d:
                a = int(d["addr"], 16)
                v = ram[a] if d["size"] == 1 else ram[a] | (ram[a + 1] << 8)
                if d["signed"]:
                    bits = 8 * d["size"]
                    if v >= 1 << (bits - 1):
                        v -= 1 << bits
                out[name] = v
        env = dict(out, ram=ram, frame=frame, **_FUNCS)
        for name, code in self._derived.items():
            try:
                out[name] = eval(code, {"__builtins__": {}}, env)
            except Exception:
                out[name] = None
            env[name] = out[name]
        return out

    def describe(self):
        lines = []
        for name, d in self.defs.items():
            where = d.get("expr") or f"{d['addr']}{'/16' if d.get('size') == 2 else ''}{' signed' if d.get('signed') else ''}"
            lines.append(f"{name} = {where}{' [event]' if d.get('event') else ''} — {d.get('desc', '')}")
        return "\n".join(lines)


def png(frame, scale=2, crop=None):
    img = Image.fromarray(frame)
    if crop:
        img = img.crop(crop)
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    b = io.BytesIO()
    img.save(b, "PNG", optimize=True)
    return b.getvalue()


def contact_sheet(frames, labels, cols=4, scale=1):
    w, h = 256 * scale, 240 * scale
    rows = math.ceil(len(frames) / cols)
    sheet = Image.new("RGB", (cols * w, rows * (h + 12)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (f, lab) in enumerate(zip(frames, labels)):
        img = Image.fromarray(f)
        if scale != 1:
            img = img.resize((w, h), Image.NEAREST)
        x, y = (i % cols) * w, (i // cols) * (h + 12)
        sheet.paste(img, (x, y + 12))
        d.text((x + 2, y), lab, fill=(255, 255, 0))
    b = io.BytesIO()
    sheet.save(b, "PNG", optimize=True)
    return b.getvalue()


# ---------------------------------------------------------------- the workbench
class Env:
    SNAP_EVERY = 30

    def __init__(self, run_dir, core="fceumm"):
        self.run_dir = run_dir
        os.makedirs(os.path.join(run_dir, "checkpoints"), exist_ok=True)
        self.core_name = core
        self.core = nes.Core(core)
        self.vars = RamVars(os.path.join(run_dir, "ram.json"))
        self.movie = []                   # masks applied so far (index = frame)
        self.lagf = []                    # 1 where that frame was a lag/loading frame
        self.snaps = {0: self.core.save()}
        self.ck_path = os.path.join(run_dir, "checkpoints.json")
        self.cks = json.load(open(self.ck_path)) if os.path.exists(self.ck_path) else {}
        mpath = os.path.join(run_dir, "movie.txt")
        if os.path.exists(mpath):
            self.goto_movie(parse_spec(open(mpath).read()))
        self.search_pool = None

    # ---- movie / position ----
    @property
    def frame(self):
        return len(self.movie)

    def persist(self):
        tmp = os.path.join(self.run_dir, "movie.txt.tmp")
        open(tmp, "w").write(rle(self.movie) + "\n")
        os.replace(tmp, os.path.join(self.run_dir, "movie.txt"))

    def _restore_to(self, n):
        """Put the core at frame n of the current movie (n <= len(movie))."""
        base = max(f for f in self.snaps if f < n) if n > 0 else 0   # replay >= 1 frame so the picture is fresh
        self.core.load(self.snaps[base])
        if n == 0:
            self.core.frame = None
        for f in range(base, n):
            self.core.step(self.movie[f], render=(f == n - 1))
            if (f + 1) % self.SNAP_EVERY == 0 and f + 1 not in self.snaps:
                self.snaps[f + 1] = self.core.save()

    def truncate(self, n):
        n = max(0, min(n, len(self.movie)))
        self.movie = self.movie[:n]
        self.lagf = self.lagf[:n]
        for f in [f for f in self.snaps if f > n]:
            del self.snaps[f]
        self._restore_to(n)

    def goto_movie(self, masks):
        """Switch to another movie, reusing snapshots up to the common prefix."""
        common = 0
        for a, b in zip(self.movie, masks):
            if a != b:
                break
            common += 1
        self.truncate(common)
        if len(masks) > common:
            self.play_masks(masks[common:], capture_every=0, watch_events=False)

    def play_masks(self, masks, capture_every=0, watch_events=True):
        """Append masks to the movie and run them. Returns (captures, events)."""
        caps, events = [], []
        before = self.vars.read(self.core.mem, self.frame) if watch_events else None
        evnames = [n for n, d in self.vars.defs.items() if d.get("event")]
        n = len(masks)
        self.last_lag = 0
        for i, m in enumerate(masks):
            want = capture_every and ((i + 1) % capture_every == 0 or i == n - 1)
            c0 = self.core.mem[LAG_COUNTER]
            self.core.step(m, render=bool(want) or i == n - 1)
            lagged = int(self.core.mem[LAG_COUNTER] == c0)
            self.lagf.append(lagged)
            self.last_lag += lagged
            self.movie.append(m)
            if self.frame % self.SNAP_EVERY == 0:
                self.snaps[self.frame] = self.core.save()
            if want:
                caps.append((self.frame, self.core.frame.copy()))
            if watch_events and evnames:
                now = self.vars.read(self.core.mem, self.frame)
                for k in evnames:
                    if now.get(k) != before.get(k):
                        events.append(f"f{self.frame}: {k} {before.get(k)}→{now.get(k)}")
                before = now
        if len(self.snaps) > 4000:        # keep memory bounded (~140 MB of mesen states)
            keep = sorted(self.snaps)
            for f in keep[1:-2000:2]:
                del self.snaps[f]
        self.persist()
        return caps, events

    def status(self):
        v = self.vars.read(self.core.mem, self.frame)
        return {"frame": self.frame, "time": f"{self.frame / self.core.fps:.2f}s", "lag": sum(self.lagf), **v}

    def status_line(self):
        return " ".join(f"{k}={v}" for k, v in self.status().items())

    # ---- checkpoints ----
    def ck_save(self, name, note=""):
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,60}", name):
            raise ValueError("checkpoint names: letters, digits, _ . - (max 60)")
        st = self.core.save()
        open(os.path.join(self.run_dir, "checkpoints", name + ".state"), "wb").write(st[0])
        open(os.path.join(self.run_dir, "checkpoints", name + ".movie"), "w").write(rle(self.movie))
        self.cks[name] = {"frame": self.frame, "note": note, "saved": time.strftime("%Y-%m-%d %H:%M:%S"),
                          "status": self.status_line()}
        json.dump(self.cks, open(self.ck_path, "w"), indent=1)

    def ck_load(self, name):
        if name not in self.cks:
            raise ValueError(f"no checkpoint {name!r}")
        masks = parse_spec(open(os.path.join(self.run_dir, "checkpoints", name + ".movie")).read())
        self.goto_movie(masks)
        self.persist()

    def ck_movie(self, name):
        return parse_spec(open(os.path.join(self.run_dir, "checkpoints", name + ".movie")).read())

    # ---- verification ----
    def verify_async(self):
        """Replay the movie from power-on on a fresh core in a fresh process (never a second core in this
        process: libretro cores are global, a second one hijacks this one's callbacks). Returns (future of the
        replay's RAM hash, this core's RAM hash now)."""
        import multiprocessing as mp
        ex = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context("spawn"))
        fut = ex.submit(_verify_job, self.core_name, list(self.movie))
        ex.shutdown(wait=False)
        return fut, hashlib.sha1(self.core.ram_bytes()).hexdigest()

    def export_fm2(self, path):
        """FCEUX movie (power-on, no SRAM). Column order RLDUTSBA."""
        lines = ["version 3", "emuVersion 22020", "rerecordCount 0", "palFlag 0",
                 "romFilename Kirby's Adventure (USA) (Rev A)", "guid 00000000-0000-0000-0000-000000000000",
                 "fourscore 0", "microphone 0", "port0 1", "port1 0", "port2 0", "FDS 0", "NewPPU 0",
                 "comment author Claude Opus 5.5 (autonomous) + nes.py/" + self.core_name]
        for m in self.movie:
            row = "".join(c if m & LETTERS[k] else "." for c, k in
                          zip("RLDUTSBA", ["R", "L", "D", "U", "T", "S", "B", "A"]))
            lines.append(f"|{1 if m & nes.RESET else 0}|{row}|||")
        open(path, "w").write("\n".join(lines) + "\n")

    # ---- search ----
    def search(self, actions, goal=None, score=None, max_depth=8, beam=24, start=None, workers=16,
               time_limit=120, avoid=None, mode="beam", samples=2000, seed=0):
        """Beam search over macro-actions from the current position (or checkpoint `start`).
        goal: expr; first frame where it is true ends the search (fewest frames wins).
        score: expr maximised after each action (beam ranking). avoid: expr that prunes a branch."""
        names = set(self.vars.defs)
        for e in (goal, score, avoid):
            if e:
                compile_expr(e, names)
        acts = [parse_spec(a) for a in actions]
        if not acts or any(not a for a in acts):
            raise ValueError("actions must be non-empty input specs")
        if start:
            self.ck_load(start)
        root = self.core.save()
        if self.search_pool is None:
            # spawn, not fork: a forked child inherits this process's initialised core and the re-init leaves it
            # ignoring input (every candidate then dedups to one state)
            import multiprocessing as mp
            self.search_pool = ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("spawn"),
                                                   initializer=_w_init, initargs=(self.core_name, self.vars.path))
        t0 = time.time()
        if mode == "random":
            return self._random_search(acts, goal, score, avoid, max_depth, samples, seed, root, workers, t0)
        beam_list = [((), root)]
        seen = set()
        explored = 0
        best_any = None
        for depth in range(max_depth):
            jobs = [(seq, st, ai) for seq, st in beam_list for ai in range(len(acts))]
            futs = list(self.search_pool.map(_w_run, [(st[0], st[1], acts[ai], goal, score, avoid, self.vars.path,
                                                      os.path.getmtime(self.vars.path) if os.path.exists(self.vars.path) else 0)
                                                     for seq, st, ai in jobs], chunksize=max(1, len(jobs) // (workers * 4))))
            explored += sum(len(acts[ai]) for _, _, ai in jobs)
            hits = []
            nxt = []
            for (seq, st, ai), r in zip(jobs, futs):
                if r is None:
                    continue
                if r["goal_at"] is not None:
                    hits.append((len(sum((acts[x] for x in seq), [])) + r["goal_at"], seq + (ai,), r))
                    continue
                if r["pruned"] or r["hash"] in seen:
                    continue
                seen.add(r["hash"])
                nxt.append((r["score"], seq + (ai,), (r["state"], st[1] + len(acts[ai]), st[2])))
            if hits:
                hits.sort(key=lambda h: h[0])
                frames, seq, r = hits[0]
                masks = sum((acts[x] for x in seq[:-1]), []) + acts[seq[-1]][:r["goal_at"]]
                return {"found": True, "frames": frames, "spec": rle(masks), "masks": masks, "depth": depth + 1,
                        "explored_frames": explored, "seconds": round(time.time() - t0, 1)}
            if not nxt:
                break
            nxt.sort(key=lambda x: -x[0] if x[0] is not None else math.inf)
            beam_list = [(seq, st) for _, seq, st in nxt[:beam]]
            best_any = nxt[0]
            if time.time() - t0 > time_limit:
                break
        if best_any is None:
            return {"found": False, "explored_frames": explored, "seconds": round(time.time() - t0, 1)}
        score_v, seq, _ = best_any
        masks = sum((acts[x] for x in seq), [])
        return {"found": False, "best_score": score_v, "spec": rle(masks), "masks": masks, "depth": len(seq),
                "explored_frames": explored, "seconds": round(time.time() - t0, 1)}


    def _random_search(self, acts, goal, score, avoid, depth, samples, seed, root, workers, t0):
        """BasicBot-style: sample random action sequences from the root, keep the best."""
        import random
        rng = random.Random(seed)
        seqs = [tuple(rng.randrange(len(acts)) for _ in range(depth)) for _ in range(int(samples))]
        mt = os.path.getmtime(self.vars.path) if os.path.exists(self.vars.path) else 0
        jobs = [(root[0], root[1], sum((acts[i] for i in sq), []), goal, score, avoid, self.vars.path, mt, False)
                for sq in seqs]
        res = list(self.search_pool.map(_w_run, jobs, chunksize=max(1, len(jobs) // (workers * 4))))
        explored = sum(len(j[2]) for j in jobs)
        hits = [(r["goal_at"], j[2]) for r, j in zip(res, jobs) if r["goal_at"] is not None]
        if hits:
            f, masks = min(hits, key=lambda h: h[0])
            masks = masks[:f]
            return {"found": True, "frames": f, "spec": rle(masks), "masks": masks, "hits": len(hits),
                    "samples": len(jobs), "explored_frames": explored, "seconds": round(time.time() - t0, 1)}
        ok = [(r["score"], j[2]) for r, j in zip(res, jobs) if not r["pruned"]]
        if not ok:
            return {"found": False, "samples": len(jobs), "all_pruned": True, "seconds": round(time.time() - t0, 1)}
        sc, masks = max(ok, key=lambda x: x[0])
        return {"found": False, "best_score": sc, "spec": rle(masks), "masks": masks, "samples": len(jobs),
                "explored_frames": explored, "seconds": round(time.time() - t0, 1)}


def _verify_job(core_name, masks):
    c = nes.Core(core_name)
    for m in masks:
        c.step(m, render=False)
    return hashlib.sha1(c.ram_bytes()).hexdigest()


# ---- search workers (one core per process) ----
_W = {}


def _w_init(core_name, vars_path):
    _W["core"] = nes.Core(core_name)
    _W["vars"] = RamVars(vars_path)
    _W["mtime"] = os.path.getmtime(vars_path) if os.path.exists(vars_path) else 0
    _W["exprs"] = {}


def _w_run(args):
    raw, frames, masks, goal, score, avoid, vars_path, mtime = args[:8]
    want_state = args[8] if len(args) > 8 else True
    if mtime != _W["mtime"]:
        _W["vars"] = RamVars(vars_path)
        _W["mtime"] = mtime
        _W["exprs"] = {}
    c, V = _W["core"], _W["vars"]
    c.load((raw, frames, 0))
    names = set(V.defs)

    def comp(e):
        if e not in _W["exprs"]:
            _W["exprs"][e] = compile_expr(e, names)
        return _W["exprs"][e]

    g = comp(goal) if goal else None
    s = comp(score) if score else None
    a = comp(avoid) if avoid else None
    lag = 0
    for i, m in enumerate(masks):
        c0 = c.mem[LAG_COUNTER]
        c.step(m, render=False)
        lag += c.mem[LAG_COUNTER] == c0
        if g or a:
            env = dict(V.read(c.mem, frames + i + 1), ram=c.mem, frame=frames + i + 1, lag=lag, **_FUNCS)
            if g and eval(g, {"__builtins__": {}}, env):
                return {"goal_at": i + 1, "pruned": False, "score": None, "hash": None, "state": None}
            if a and eval(a, {"__builtins__": {}}, env):
                return {"goal_at": None, "pruned": True, "score": None, "hash": None, "state": None}
    env = dict(V.read(c.mem, frames + len(masks)), ram=c.mem, frame=frames + len(masks), lag=lag, **_FUNCS)
    sc = float(eval(s, {"__builtins__": {}}, env)) if s else 0.0
    if not want_state:
        return {"goal_at": None, "pruned": False, "score": sc, "hash": None, "state": None}
    st = c.save()
    return {"goal_at": None, "pruned": False, "score": sc, "hash": hashlib.sha1(c.ram_bytes()).hexdigest(),
            "state": st[0]}


def b64png(data):
    return base64.b64encode(data).decode()
