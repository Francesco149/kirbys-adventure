#!/usr/bin/env python
"""drive.py — drive the workbench from a shell or a script (a coding agent's session, a subagent, a cron job).

Stateless: every call opens the run directory, restores the movie's end from on-disk keyframes (< 1 s), does one
thing, and persists. No daemon, no API key. The same run directory layout as the API harness (agent.py).

    kt() { tas/kt "$@"; }                         # from the repository root
    kt new  demo --from 1-1-speed:r44_start      # or power-on, <run>@<frame>, a movie file
    kt play demo "R*40 RA*8" --view strip        # status line + events; pictures go to runs/demo/view/*.png
    kt look demo --scale 3 [--crop x0,y0,x1,y1]
    kt rewind demo --to 1500      |  kt ck demo save NAME [note] | load NAME | list
    kt ram demo status|objects|list|mark|diff|read ADDR [N]|define NAME --addr 61CA / --expr "..." [--event]
    kt room demo                                 # collision map + doors of the current room (Kirby)
    kt search demo --goal "room != 44" --avoid "hp < 47" --mode explore --cell "(room, x//16, y//16)" --apply
    kt go demo --until "room == 42"              # room after room with explore, until the predicate holds
    kt check demo tasks/secret-ufo.md            # ordered steps + forbid, on a replay from power-on
    kt verify demo                               # fresh-process replay == live state?
    kt render demo out.mp4 --from 1400 --to 2600 [--scale 3]

Python (bigger strides: script a whole segment in one call):
    import drive; r = drive.Run("demo"); r.play("R*40"); res = r.explore(goal=..., cell=...); r.apply(res)
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "labkit"))

import env as E          # noqa: E402
import nes               # noqa: E402
import xsearch           # noqa: E402

# Scripts fed on stdin (python - <<EOF) have __main__.__file__ == "<stdin>"; spawned search workers would try to
# re-import that path and die. Without a __file__ they skip the re-import.
_main = sys.modules.get("__main__")
if _main is not None and getattr(_main, "__file__", None) and not os.path.exists(_main.__file__):
    del _main.__file__

# the recipe's traversal alphabet for normal Kirby (8-frame macro-actions; run = double-tap)
KIRBY_ACTIONS = ["R*8", ". R*7", "R . R*6", "L*8", "L . L*6", "RA*8", "LA*8", "UR*8", "UL*8", "U*8", "D*8", "DR*8",
                 "U*5 .*3", "B*2 .*16 U*6", ". B*12 .*2", ".*8"]
KIRBY_CELL = "(room, x//16, y//16)"
KIRBY_FINE = "(x//3, y//3)"


def run_path(name):
    return os.path.abspath(name) if os.sep in name else os.path.join(HERE, "runs", name)


class Run(E.Env):
    KEY_EVERY = 1500

    def __init__(self, name, core="fceumm"):
        d = run_path(name)
        if not os.path.isdir(d):
            raise SystemExit(f"no run {d}; create it with: kt new {name} --from ...")
        self.run_dir = d
        for sub in ("checkpoints", "keys", "view"):
            os.makedirs(os.path.join(d, sub), exist_ok=True)
        # one command per run at a time: a search that outlived its shell (timed out, moved to the background)
        # would otherwise keep writing into the movie under the next command
        import fcntl
        self._lock = open(os.path.join(d, ".lock"), "w")
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise SystemExit(f"run {name} is busy: another kt command is still working on it (a search that timed "
                             f"out in your shell keeps running). Wait for it, or kill it: pkill -f 'drive.py .* {name}'")
        rp = os.path.join(d, "ram.json")
        if not os.path.exists(rp):
            shutil.copy(os.path.join(HERE, "knowledge", "ram-seed.json"), rp)
        self.core_name = core
        self.core = nes.Core(core)
        self.vars = E.RamVars(rp)
        self.movie, self.lagf = [], []
        self.snaps = {0: self.core.save()}
        self.ck_path = os.path.join(d, "checkpoints.json")
        self.cks = json.load(open(self.ck_path)) if os.path.exists(self.ck_path) else {}
        self.search_pool = None
        self.last_lag = 0
        mp = os.path.join(d, "movie.txt")
        masks = E.parse_spec(open(mp).read()) if os.path.exists(mp) else []
        self._load_fast(masks)

    # ---- on-disk keyframes: <frame>-<sha of the movie prefix>.state ----
    @staticmethod
    def _prefix_shas(masks, every):
        h = hashlib.sha1()
        out = {}
        for i in range(0, len(masks) - len(masks) % every, every):
            h.update(b"".join(m.to_bytes(2, "little") for m in masks[i:i + every]))
            out[i + every] = h.copy().hexdigest()[:12]
        return out

    def _key_file(self, frame, sha):
        return os.path.join(self.run_dir, "keys", f"{frame:08d}-{sha}.state")

    def _load_fast(self, masks):
        shas = self._prefix_shas(masks, self.KEY_EVERY)
        for f, sha in shas.items():
            p = self._key_file(f, sha)
            if os.path.exists(p):
                self.snaps[f] = (open(p, "rb").read(), f, 0)
        have = max(self.snaps)
        self.movie = list(masks[:have])
        self.lagf = [0] * have
        self.core.load(self.snaps[have])
        if len(masks) > have:
            self.play_masks(masks[have:], watch_events=False)
        elif have:
            self._restore_to(have)          # replays >= 1 frame so the picture is fresh

    def _write_keys(self):
        shas = self._prefix_shas(self.movie, self.KEY_EVERY)
        want = set()
        for f, sha in shas.items():
            p = self._key_file(f, sha)
            want.add(os.path.basename(p))
            if not os.path.exists(p) and f in self.snaps:
                open(p, "wb").write(self.snaps[f][0])
        kd = os.path.join(self.run_dir, "keys")
        for fn in os.listdir(kd):
            if fn not in want:
                os.unlink(os.path.join(kd, fn))

    def persist(self):
        super().persist()
        self._write_keys()

    def truncate(self, n):
        super().truncate(n)
        self.persist()

    def pool(self, workers=16):
        if self.search_pool is None:
            import multiprocessing as mp
            from concurrent.futures import ProcessPoolExecutor
            self.search_pool = ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("spawn"),
                                                   initializer=E._w_init, initargs=(self.core_name, self.vars.path))
        return self.search_pool

    def close(self):
        if self.search_pool is not None:
            procs = list((getattr(self.search_pool, "_processes", None) or {}).values())
            self.search_pool.shutdown(wait=False, cancel_futures=True)
            for p in procs:
                p.terminate()
            self.search_pool = None

    # ---- conveniences for scripts ----
    def v(self):
        return self.vars.read(self.core.mem, self.frame)

    def ev(self, expr):
        code = E.compile_expr(expr, set(self.vars.defs))
        return eval(code, {"__builtins__": {}}, dict(self.v(), ram=self.core.mem, frame=self.frame, lag=0, **E._FUNCS))

    def play(self, spec, capture_every=0):
        return self.play_masks(E.parse_spec(spec), capture_every=capture_every)

    def explore(self, goal, cell=KIRBY_CELL, actions=None, polish=0, fine=KIRBY_FINE, **kw):
        """Score-free search. polish=N: afterwards spend up to N seconds on a beam over the learned
        frames-to-goal field and keep the shorter path."""
        log = kw.get("log")
        r = xsearch.explore(self, actions or KIRBY_ACTIONS, goal, cell, **kw)
        togo = r.pop("togo", {})
        if polish and r.get("found"):
            p = xsearch.polish(self, actions or KIRBY_ACTIONS, goal, cell, togo, avoid=kw.get("avoid"), fine=fine,
                               time_limit=polish, bound=r["frames"], log=log)
            r["explore_frames"] = r["frames"]
            r["polish"] = {k: v for k, v in p.items() if k not in ("masks", "spec")}
            if p.get("found") and p["frames"] < r["frames"]:
                r.update(frames=p["frames"], masks=p["masks"], spec=p["spec"])
            r["seconds"] = round(r["seconds"] + p["seconds"], 1)
        return r

    def simplify(self, masks, goal, **kw):
        """Tighten (mode="frames") or smooth (mode="smooth", slack=0.1) a path that reaches `goal` from here."""
        return xsearch.simplify(self, masks, goal, **kw)

    def apply(self, res):
        if res.get("masks"):
            return self.play_masks(res["masks"])
        return [], []

    def shot(self, name="last", scale=2, crop=None):
        p = os.path.join(self.run_dir, "view", name + ".png")
        f = self.core.frame
        if f is None:
            self.core.step(0, render=True)        # only at frame 0; not part of the movie
            f = self.core.frame
            self.core.load(self.snaps[0])
        open(p, "wb").write(E.png(f, scale, tuple(crop) if crop else None))
        return p

    def objects(self):
        """Live object slots: (slot, script id, collision class, x, y, $61CA+slot). A slot is live when its
        script id ($6128+slot) is below $80; collision class 0 objects (Warp Stars, items, the UFO pickup)
        count too, which the old class-based listing hid."""
        mem, rows = self.core.mem, []
        for sl in range(18):
            sid = mem[0x6128 + sl]
            if sid >= 0x80 or sl == 0:
                continue
            rows.append((sl, sid, mem[0x6200 + sl], mem[0x6086 + sl] * 256 + mem[0x6074 + sl],
                         mem[0x60AA + sl] * 256 + mem[0x6098 + sl], mem[0x61CA + sl]))
        return rows

    def go(self, until, var="room", actions=None, cell=KIRBY_CELL, avoid=None, per_step=90, refine=8, max_steps=16,
           settle=0, polish=0, log=print):
        """Chain explore searches: each step's goal is '`var` takes a value not seen yet in this call'. Stops when
        `until` holds, a step fails, or max_steps. Returns the per-step rows."""
        seen = [self.ev(var)]
        rows = []
        while not self.ev(until) and len(rows) < max_steps:
            f0 = self.frame
            goal = f"{var} not in ({', '.join(map(str, seen))},)"
            r = self.explore(goal, cell=cell, actions=actions, avoid=avoid, time_limit=per_step, refine=refine,
                             polish=polish)
            row = {"from": seen[-1], "found": r["found"], "frames": r.get("frames"), "seconds": r["seconds"],
                   "cells": r["cells"]}
            if not r["found"]:
                row["newest_cells"] = r.get("newest_cells")
                rows.append(row)
                log(json.dumps(row))
                break
            self.apply(r)
            if settle:
                self.play(f".*{settle}")
            row["to"] = self.ev(var)
            row["status"] = self.status_line()
            seen.append(row["to"])
            rows.append(row)
            log(json.dumps(row))
            if self.frame == f0:
                break
        return rows


# ------------------------------------------------------------------------------------------------ CLI
def _strip(run, caps, name="strip"):
    p = os.path.join(run.run_dir, "view", name + ".png")
    open(p, "wb").write(E.contact_sheet([c[1] for c in caps], [f"f{c[0]}" for c in caps], cols=4))
    return p


def start_masks(src):
    """A start: power-on | a movie file | <run>@<frame> | <run>:<checkpoint>."""
    if src == "power-on":
        return []
    if os.path.isfile(src):
        return E.parse_spec(open(src).read())
    if "@" in src:
        r, n = src.split("@", 1)
        return E.parse_spec(open(os.path.join(run_path(r), "movie.txt")).read())[:int(n)]
    r, ck = src.split(":", 1)
    return E.parse_spec(open(os.path.join(run_path(r), "checkpoints", ck + ".movie")).read())


def cmd_new(a):
    d = run_path(a.run)
    if os.path.exists(os.path.join(d, "movie.txt")) and not a.force:
        raise SystemExit(f"{d} already has a movie (use --force to replace it)")
    os.makedirs(d, exist_ok=True)
    src = a.start
    masks = start_masks(src)
    open(os.path.join(d, "movie.txt"), "w").write(E.rle(masks) + "\n")
    run = Run(a.run)
    run.persist()
    print(f"run {a.run}: {run.frame} frames from {src}\n{run.status_line()}\npicture: {run.shot()}")


def cmd_play(a):
    run = Run(a.run)
    spec = open(a.file).read() if a.file else a.inputs
    masks = E.parse_spec(spec)
    every = 0
    if a.view == "strip":
        every = max(1, a.every or max(1, len(masks) // 8))
        if len(masks) / every > 16:
            every = -(-len(masks) // 16)
    caps, events = run.play_masks(masks, capture_every=every)
    print(f"played {len(masks)} frames ({run.last_lag} lag).\n{run.status_line()}")
    if events:
        print("events: " + "; ".join(events[:60]) + (" …" if len(events) > 60 else ""))
    if a.view == "end":
        print("picture:", run.shot())
    elif a.view == "strip":
        print("strip:", _strip(run, caps))


def cmd_look(a):
    run = Run(a.run)
    crop = [int(x) for x in a.crop.split(",")] if a.crop else None
    print(run.status_line())
    print("picture:", run.shot(a.name, a.scale, crop))


def cmd_strip(a):
    """Contact sheet of frames [--from, --to] of the movie as it is (nothing is changed)."""
    run = Run(a.run)
    end = run.frame if a.to is None else min(a.to, run.frame)
    n = max(1, end - a.start)
    every = a.every or max(1, -(-n // 16))
    full = list(run.movie)
    run.movie = full[:a.start]              # reposition without touching the files
    run.lagf = [0] * a.start
    run._restore_to(a.start) if a.start else run.core.load(run.snaps[0])
    caps = []
    for i, m in enumerate(full[a.start:end]):
        want = (i + 1) % every == 0 or i == n - 1
        run.core.step(m, render=want)
        if want:
            caps.append((a.start + i + 1, run.core.frame.copy()))
    print(f"frames {a.start}-{end}, every {every}: {_strip(run, caps[:16], a.name)}")


def cmd_rewind(a):
    run = Run(a.run)
    run.truncate(a.to if a.to is not None else run.frame - a.frames)
    print(f"now at frame {run.frame}.\n{run.status_line()}\npicture: {run.shot()}")


def cmd_ck(a):
    run = Run(a.run)
    if a.action == "save":
        run.ck_save(a.name, " ".join(a.note))
        print(f"saved {a.name} at frame {run.frame}")
    elif a.action == "load":
        run.ck_load(a.name)
        print(f"loaded {a.name}.\n{run.status_line()}\npicture: {run.shot()}")
    else:
        for k, v in sorted(run.cks.items(), key=lambda kv: kv[1]["frame"]):
            print(f"{k}: frame {v['frame']} — {v.get('note', '')} [{v.get('status', '')}]")


def cmd_ram(a):
    run = Run(a.run)
    mem = run.core.mem
    regions = [(0, 0x800), (0x6000, 0x8000)]
    markp = os.path.join(run.run_dir, "view", "mark.json")
    if a.action == "status":
        print(run.status_line())
    elif a.action == "objects":
        print(f"live objects at frame {run.frame} (script id < $80)\nslot script class     x     y  $61CA+s")
        for sl, sid, cl, x, y, hp in run.objects():
            print(f"{sl:4d} {sid:6d} {cl:5d} {x:5d} {y:5d}   {hp:3d}" + ("  <- Kirby" if sl == 1 else ""))
    elif a.action == "read":
        base0 = E.parse_addr(a.args[0])
        n = int(a.args[1]) if len(a.args) > 1 else 16
        for base in range(base0, base0 + n, 16):
            print(f"${base:04X}: " + " ".join(f"{mem[i]:02X}" for i in range(base, min(base + 16, base0 + n))))
    elif a.action == "mark":
        json.dump({"frame": run.frame, "ram": [mem[i] for lo, hi in regions for i in range(lo, hi)]}, open(markp, "w"))
        print(f"marked RAM at frame {run.frame}")
    elif a.action == "diff":
        mk = json.load(open(markp))
        addrs = [i for lo, hi in regions for i in range(lo, hi)]
        rows = [f"${ad:04X}: {old:02X} → {mem[ad]:02X} ({mem[ad] - old:+d})" for ad, old in zip(addrs, mk["ram"])
                if old != mem[ad]]
        print(f"{len(rows)} bytes changed between frame {mk['frame']} and {run.frame}")
        print("\n".join(rows[:a.limit]) + ("\n…" if len(rows) > a.limit else ""))
    elif a.action == "define":
        run.vars.define(a.args[0], addr=a.addr, size=a.size, signed=a.signed, expr=a.expr, desc=a.desc, event=a.event)
        print(f"defined {a.args[0]}.\n{run.status_line()}")
    elif a.action == "remove":
        run.vars.remove(a.args[0])
    else:
        print(run.vars.describe())


def cmd_room(a):
    import contextlib
    import io
    run = Run(a.run)
    os.environ["KIRBY_RUN"] = run.run_dir
    os.makedirs(os.path.join(run.run_dir, "lab"), exist_ok=True)
    os.chdir(os.path.join(run.run_dir, "lab"))       # lab.py makes ./out on import
    import lab
    import roominfo
    lab._vars = run.vars
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        roominfo.info(run.core)
    print(buf.getvalue() + "objects (slot, script, class, x, y, $61CA+s): " + str(run.objects()))


def _search(run, a):
    actions = a.actions or KIRBY_ACTIONS
    if a.mode == "explore":
        return run.explore(a.goal, cell=a.cell, actions=actions, avoid=a.avoid, score=a.score, polish=a.polish,
                           time_limit=a.time_limit, refine=a.refine, max_len=a.max_len, seed=a.seed,
                           log=lambda s: print("  " + s, flush=True))
    return run.search(actions, goal=a.goal, score=a.score, avoid=a.avoid, max_depth=a.max_depth, beam=a.beam,
                      time_limit=a.time_limit, mode=a.mode, samples=a.samples, seed=a.seed)


def cmd_search(a):
    run = Run(a.run)
    try:
        r = _search(run, a)
        masks = r.pop("masks", None)
        print(json.dumps(r))
        if a.save and masks:
            open(a.save, "w").write(E.rle(masks) + "\n")
        if a.apply and masks and (r.get("found") or not a.goal):
            _, events = run.play_masks(masks)
            print(f"applied.\n{run.status_line()}")
            if events:
                print("events: " + "; ".join(events[:40]))
            print("picture:", run.shot())
        elif a.apply:
            print("not applied: the goal was not reached")
    finally:
        run.close()


def cmd_simplify(a):
    """Re-optimise the movie's tail: from frame --from to the end, which must reach --goal."""
    run = Run(a.run)
    try:
        goal, avoid = a.goal, a.avoid
        if a.task:                           # the task's steps not yet met at --from, in order, plus its forbids
            t, res, _ = _check_proc(run.run_dir, a.task)
            if not res["ok"]:
                raise SystemExit("the movie does not pass the task check; simplify needs a passing movie")
            goal = [e for (n, e), (_, f) in zip(t["steps"], res["steps"]) if f > a.start]
            fb = " or ".join(f"({e})" for _, e in t["forbid"])
            avoid = " or ".join(x for x in (f"({avoid})" if avoid else "", fb) if x) or None
        if not goal:
            raise SystemExit("give --goal or --task")
        tail = run.movie[a.start:]
        # cut in memory only (E.Env.truncate, not Run.truncate, which persists): movie.txt keeps the whole movie
        # until the result is applied, so an interrupted search (timeout, Ctrl-C, a kill) leaves the run as it was
        E.Env.truncate(run, a.start)
        r = run.simplify(tail, goal, avoid=avoid, mode=a.mode, slack=a.slack, time_limit=a.time_limit,
                         log=lambda s: print("  " + s, flush=True))
        masks = r.pop("masks")
        r.pop("spec")
        print(json.dumps(r))
        run.play_masks(masks if not a.dry else tail)
        print(("applied.\n" if not a.dry else "dry run, movie unchanged.\n") + run.status_line())
    finally:
        run.close()


def cmd_go(a):
    run = Run(a.run)
    try:
        rows = run.go(a.until, var=a.var, actions=a.actions or None, cell=a.cell, avoid=a.avoid, per_step=a.per_step,
                      refine=a.refine, max_steps=a.max_steps, settle=a.settle, polish=a.polish)
        ok = bool(run.ev(a.until))
        print(f"{'reached' if ok else 'STOPPED before'}: {a.until} after {len(rows)} steps.\n{run.status_line()}")
        print("picture:", run.shot())
    finally:
        run.close()


def _check_proc(run_dir, task_path):
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor
    import task as TK
    t = TK.load(task_path)
    masks = E.parse_spec(open(os.path.join(run_dir, "movie.txt")).read())
    pre = start_masks(t["start"])
    if masks[:len(pre)] != pre:
        raise SystemExit(f"the movie does not begin with the task's start prefix ({t['start']}, {len(pre)} frames)")
    with ProcessPoolExecutor(1, mp_context=mp.get_context("spawn")) as ex:
        r = ex.submit(TK.check_job, "fceumm", os.path.join(run_dir, "ram.json"), masks, t["steps"], t["forbid"],
                      len(pre)).result()
    r["start_frame"] = len(pre)
    return t, r, len(masks)


def cmd_check(a):
    import task as TK
    t, r, n = _check_proc(run_path(a.run), a.task)
    print(f"task {t['name']}: {'PASS' if r['ok'] else 'FAIL'} (replay from power-on, {n} frames; steps judged "
          f"after the start prefix, frame {r['start_frame']})")
    print(TK.describe(t, r))
    json.dump({"task": t["name"], "frames": n, "check": r, "t": time.strftime("%Y-%m-%d %H:%M:%S")},
              open(os.path.join(run_path(a.run), "result.json"), "w"), indent=1)
    sys.exit(0 if r["ok"] else 1)


def _lint_job(core_name, vars_path, masks, exprs):
    c = nes.Core(core_name)
    rv = E.RamVars(vars_path)
    code = [E.compile_expr(e, set(rv.defs)) for e in exprs]
    first, count = [None] * len(code), [0] * len(code)
    for f, m in enumerate(masks, 1):
        c.step(m, render=False)
        env = dict(rv.read(c.mem, f), ram=c.mem, frame=f, **E._FUNCS)
        for i, cd in enumerate(code):
            try:
                ok = bool(eval(cd, {"__builtins__": {}}, env))
            except Exception:  # noqa: BLE001
                ok = False
            if ok:
                count[i] += 1
                if first[i] is None:
                    first[i] = f
    return first, count


def cmd_lint(a):
    """Dry-run a task's predicates on existing movies: where does each step first hold, how often, and do the
    forbids fire? A step that never holds on a movie known to do that thing is a wrong predicate."""
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor
    import task as TK
    t = TK.load(a.task)
    rows = [("step", n, e) for n, e in t["steps"]] + [("forbid", n, e) for n, e in t["forbid"]]
    runs = a.on or [t["start"].replace("@", ":").split(":")[0]]
    vp = os.path.join(HERE, "knowledge", "ram-seed.json")
    with ProcessPoolExecutor(min(8, len(runs)), mp_context=mp.get_context("spawn")) as ex:
        futs = {}
        for r in runs:
            mp_ = r if os.path.isfile(r) else os.path.join(run_path(r), "movie.txt")
            masks = E.parse_spec(open(mp_).read())
            futs[r] = (len(masks), ex.submit(_lint_job, "fceumm", a.vars or vp, masks, [e for _, _, e in rows]))
        for r, (n, fut) in futs.items():
            first, count = fut.result()
            print(f"on {r} ({n} frames):")
            for (kind, name, e), f, k in zip(rows, first, count):
                print(f"  {kind:6s} {name}: " + (f"first at frame {f}, holds on {k} frames" if f else "never holds"))
    pre = len(start_masks(t["start"]))
    print(f"start prefix: {pre} frames ({t['start']}); `check` judges steps only after it, so a step that a "
          f"library movie already satisfies elsewhere is fine, but make sure each step is specific enough that "
          f"only the intended event satisfies it after frame {pre}.")


def cmd_verify(a):
    run = Run(a.run)
    fut, here = run.verify_async()
    there = fut.result()
    print(f"{run.frame} frames: {'MATCH' if here == there else 'MISMATCH'} ({here[:10]} live vs {there[:10]} replay)")


def cmd_render(a):
    d = run_path(a.run)
    cmd = [sys.executable, os.path.join(HERE, "render.py"), os.path.join(d, "movie.txt"), a.out, "--from", str(a.start),
           "--scale", str(a.scale)] + (["--to", str(a.to)] if a.to is not None else [])
    subprocess.run(cmd, check=True, cwd=HERE)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("new"); p.add_argument("run"); p.add_argument("--from", dest="start", default="power-on")
    p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_new)
    p = sp.add_parser("play"); p.add_argument("run"); p.add_argument("inputs", nargs="?")
    p.add_argument("--file"); p.add_argument("--view", default="end", choices=["end", "strip", "none"])
    p.add_argument("--every", type=int); p.set_defaults(fn=cmd_play)
    p = sp.add_parser("look"); p.add_argument("run"); p.add_argument("--scale", type=int, default=2)
    p.add_argument("--crop"); p.add_argument("--name", default="last"); p.set_defaults(fn=cmd_look)
    p = sp.add_parser("strip"); p.add_argument("run"); p.add_argument("--from", dest="start", type=int, default=0)
    p.add_argument("--to", type=int); p.add_argument("--every", type=int); p.add_argument("--name", default="strip")
    p.set_defaults(fn=cmd_strip)
    p = sp.add_parser("rewind"); p.add_argument("run"); p.add_argument("--to", type=int)
    p.add_argument("--frames", type=int, default=0); p.set_defaults(fn=cmd_rewind)
    p = sp.add_parser("ck"); p.add_argument("run"); p.add_argument("action", choices=["save", "load", "list"])
    p.add_argument("name", nargs="?"); p.add_argument("note", nargs="*"); p.set_defaults(fn=cmd_ck)
    p = sp.add_parser("ram"); p.add_argument("run")
    p.add_argument("action", choices=["status", "objects", "read", "mark", "diff", "define", "remove", "list"])
    p.add_argument("args", nargs="*"); p.add_argument("--addr"); p.add_argument("--size", type=int, default=1)
    p.add_argument("--signed", action="store_true"); p.add_argument("--expr"); p.add_argument("--desc", default="")
    p.add_argument("--event", action="store_true"); p.add_argument("--limit", type=int, default=96)
    p.set_defaults(fn=cmd_ram)
    p = sp.add_parser("room"); p.add_argument("run"); p.set_defaults(fn=cmd_room)
    p = sp.add_parser("search"); p.add_argument("run"); p.add_argument("--actions", nargs="*")
    p.add_argument("--goal"); p.add_argument("--score"); p.add_argument("--avoid")
    p.add_argument("--mode", default="explore", choices=["explore", "beam", "random"])
    p.add_argument("--cell", default=KIRBY_CELL); p.add_argument("--max-depth", type=int, default=60)
    p.add_argument("--beam", type=int, default=256); p.add_argument("--samples", type=int, default=4000)
    p.add_argument("--time-limit", type=int, default=75); p.add_argument("--refine", type=float, default=8)
    p.add_argument("--max-len", type=int, default=8); p.add_argument("--seed", type=int, default=0)
    p.add_argument("--polish", type=int, default=0, help="explore: seconds of learned-field beam afterwards")
    p.add_argument("--apply", action="store_true"); p.add_argument("--save"); p.set_defaults(fn=cmd_search)
    p = sp.add_parser("simplify"); p.add_argument("run"); p.add_argument("--from", dest="start", type=int, required=True)
    p.add_argument("--goal"); p.add_argument("--task"); p.add_argument("--avoid"); p.add_argument("--mode", default="frames", choices=["frames", "smooth"])
    p.add_argument("--slack", type=float, default=0.0); p.add_argument("--time-limit", type=int, default=120)
    p.add_argument("--dry", action="store_true"); p.set_defaults(fn=cmd_simplify)
    p = sp.add_parser("go"); p.add_argument("run"); p.add_argument("--until", required=True)
    p.add_argument("--var", default="room"); p.add_argument("--actions", nargs="*"); p.add_argument("--cell", default=KIRBY_CELL)
    p.add_argument("--avoid"); p.add_argument("--per-step", type=int, default=75)
    p.add_argument("--refine", type=float, default=8); p.add_argument("--max-steps", type=int, default=16)
    p.add_argument("--settle", type=int, default=0); p.add_argument("--polish", type=int, default=0)
    p.set_defaults(fn=cmd_go)
    p = sp.add_parser("check"); p.add_argument("run"); p.add_argument("task"); p.set_defaults(fn=cmd_check)
    p = sp.add_parser("lint"); p.add_argument("task"); p.add_argument("--on", nargs="*", help="runs or movie files")
    p.add_argument("--vars", help="ram.json with the variables (default: the seed)"); p.set_defaults(fn=cmd_lint)
    p = sp.add_parser("verify"); p.add_argument("run"); p.set_defaults(fn=cmd_verify)
    p = sp.add_parser("render"); p.add_argument("run"); p.add_argument("out"); p.add_argument("--from", dest="start", type=int, default=0)
    p.add_argument("--to", type=int); p.add_argument("--scale", type=int, default=3); p.set_defaults(fn=cmd_render)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
