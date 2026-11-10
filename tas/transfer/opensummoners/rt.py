#!/usr/bin/env python3
"""rt.py — replay-only "play / look / ram / search / check" for Fortune Summoners under rhost (wine).

No savestates: every probe is a whole replay from boot.  A candidate = a compact macro SPEC
that compiles to a rhost trace.jsonl (frame-keyed DirectInput key LEVELS).  A batch = several
candidates replayed in parallel by ONE `rhost.py run ... --target wine` call (one batch at a time).

SPEC (whitespace-separated tokens, absolute flip frames):
    F:KEYS/D          hold KEYS (names joined by '+') from frame F for D frames
    F:KEYS/D%P*N      the same, N times, every P frames  (e.g. 700:enter/3%40*12)
    # ...             comment to end of token list is NOT supported; keep specs plain
  KEYS: enter up down left right esc bksp x c z space, or a raw DIK number (0x2d).

State (named variables) is read two ways:
    dumps  (--dump F,..)  full .data+heap dumps -> pointer CHAINS evaluated in Python (VARS below)
    ww     (--ww name=VA,.. --ww-from F) up to 4 hardware WRITE watchpoints: rhost logs every value change of
           a word with its frame = a per-frame trace of 4 heap variables (addresses resolved from a dump; they
           are stable across runs with the same room history -- cross-check against a dump of the run itself)
    watch  (--watch VA,.. --log-every N) rhost prints *(VA) every N frames; plus tick/rng per line.
           Heap addresses are run-to-run stable (fixed arena), so a chain resolved once from a dump
           would be watchable per frame -- BUT rhost reads watched addresses from frame 0, when the heap
           page is not mapped yet: an access violation, and the batch hangs in winedbg (b02, 2026-11-10).
           So watch only .data globals; chains need dumps.

CLI:
    rt.py run  NAME=SPEC [NAME=SPEC ..] [--frames N] [--dump F,F|end] [--shot F,F] [--shot-every N]
               [--watch VA,VA] [--log-every N] [--vars a,b] [--extra "raw rhost args"] [--tag T]
    rt.py file TRACE.jsonl [same options]      replay an existing trace file
    rt.py vars DUMP.rhs [--vars a,b]           evaluate the named variables on one dump
    rt.py diff A.rhs B.rhs [--region data|arena|all] [--max N]   differing words (mark -> act -> diff)
    rt.py cost                                  batches / replays / seconds so far (batches.jsonl)
Python: import rt; rt.batch({name: spec, ...}, frames=..., dump=[..], shot=[..], watch=[..]) -> results
"""
import argparse
import json
import os
import re
import struct
import subprocess
import sys
import time
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
OSS = "/opt/src/OpenSummoners"                      # READ-ONLY for us
CAP = "/opt/src/nix-lab/utils/cap-run.sh"
CANDS = os.path.join(HERE, "cands")
LEDGER = os.path.join(HERE, "batches.jsonl")

DIK = {"enter": 0x1c, "up": 0xc8, "down": 0xd0, "left": 0xcb, "right": 0xcd, "esc": 0x01, "bksp": 0x0e,
       "x": 0x2d, "c": 0x2e, "z": 0x2c, "space": 0x39, "a": 0x1e, "s": 0x1f, "d": 0x20, "v": 0x2f,
       "lshift": 0x2a, "lctrl": 0x1d, "tab": 0x0f}

# ---- named state variables: pointer chains.  [root VA, hop, hop, ..., final offset]:
#      p = u32(root); for each hop h but the last: p = u32(p + h); value = read(p + last)
#      ("s" suffix = signed 32).  A NULL anywhere -> None.
WORLD = 0x8a9b50
VARS = {
    "world":   ([WORLD], "x"),                              # *(0x8a9b50): 0 before any room exists
    "room_id": ([WORLD, 0x1038, 0x0], "d"),                 # world->roominfo->id (packed area*1000+room)
    "room":    ([WORLD, 0x2784], "x"),                      # world->room (party owner)
    "leader":  ([WORLD, 0x2784, 0x200c], "x"),              # room->leader (party slot)
    "lead_ch": ([WORLD, 0x2784, 0x200c, 0x9f4], "x"),       # leader->ch (the character)
    "lx":      ([WORLD, 0x2784, 0x200c, 0x9f4, 0x40, 0x4], "d"),   # character body[0].world_x (px*100)
    "ly":      ([WORLD, 0x2784, 0x200c, 0x9f4, 0x40, 0x8], "d"),   # character body[0].world_y
    "ch_f200": ([WORLD, 0x2784, 0x200c, 0x9f4, 0x200], "d"),       # character +0x200 (docs: 0 player AI, 1 NPC behaviour)
    "ev_actor": ([WORLD, 0x1054, 0x4], "x"),                       # event runner: actor whose script runs
    "ev_mode": ([WORLD, 0x1054, 0x14], "d"),                       # event runner mode
    "scene_kind": ([WORLD, 0x1030], "d"),
    # found by mark -> act -> diff (b03: m30 f3500 dialogue-open vs f3750 free roam, minus the noise set):
    "w2760":   ([WORLD, 0x2760], "d"),                      # world+0x2760
    "r4084":   ([WORLD, 0x2784, 0x4084], "d"),              # room+0x4084
    "dlg":     ([WORLD, 0x1044, 0x54], "x"),                # room loop +0x54: the open dialogue box object (0 = none)
    "ev2e4":   ([WORLD, 0x1054, 0x2e4], "d"),               # event runner +0x2e4
}


# ------------------------------------------------------------------ spec -> trace
def parse_spec(spec):
    """-> list of (start, end, dik) hold intervals"""
    iv = []
    for tok in spec.split():
        m = re.fullmatch(r"(\d+):([a-z0-9x+]+)/(\d+)(?:%(\d+)\*(\d+))?", tok)
        if not m:
            raise SystemExit(f"bad spec token: {tok!r}")
        f, keys, d, p, n = int(m[1]), m[2].split("+"), int(m[3]), int(m[4] or 0), int(m[5] or 1)
        for k in range(n):
            for key in keys:
                dik = DIK[key] if key in DIK else int(key, 0)
                iv.append((f + k * p, f + k * p + d, dik))
    return iv


def compile_trace(spec, edition="enold"):
    iv = parse_spec(spec)
    edges = sorted({f for a, b, _ in iv for f in (a, b)})
    lines = [f"# rt.py spec: {spec}", json.dumps({"meta": {"edition": edition}})]
    prev = None
    for f in edges:
        held = sorted({k for a, b, k in iv if a <= f < b})
        if held != prev:
            lines.append(json.dumps({"frame": f, "keys": held}))
            prev = held
    return "\n".join(lines) + "\n"


def last_frame(spec):
    return max((b for _, b, _ in parse_spec(spec)), default=0)


# ------------------------------------------------------------------ dumps (RHS2; own reader: the repo is read-only,
# importing its rhs.py would write a .pyc there)
class Dump:
    def __init__(self, path):
        b = open(path, "rb").read()
        magic, self.frame, self.cw, n = struct.unpack_from("<4I", b, 0)
        assert magic == 0x32534852, f"{path}: not RHS2"
        off = 16
        self.ranges = [struct.unpack_from("<2I", b, off + 8 * i) for i in range(n)]
        off += 8 * n
        self.mem = []
        for lo, hi in self.ranges:
            self.mem.append((lo, hi, b[off:off + (hi - lo)]))
            off += hi - lo

    def u32(self, va):
        for lo, hi, m in self.mem:
            if lo <= va and va + 4 <= hi:
                return struct.unpack_from("<I", m, va - lo)[0]
        return None

    def chain(self, ch):
        """-> (final address, value) or (None, None)"""
        if len(ch) == 1:
            return ch[0], self.u32(ch[0])
        p = self.u32(ch[0])
        for h in ch[1:-1]:
            if not p:
                return None, None
            p = self.u32(p + h)
        if not p:
            return None, None
        return p + ch[-1], self.u32(p + ch[-1])

    def var(self, name):
        ch, fmt = VARS[name]
        addr, v = self.chain(ch)
        if v is None:
            return addr, None
        if fmt == "d" and v >= 0x80000000:
            v -= 1 << 32
        return addr, v


def fmt_var(name, v):
    if v is None:
        return "-"
    return f"{v:x}" if VARS[name][1] == "x" else str(v)


def _looks_ext(v):
    """a pointer outside rhost's deterministic zones (system DLL / wine heap): run-to-run noise"""
    return 0x00a00000 <= v < 0x20000000 or 0x60000000 <= v < 0x80000000 or 0x90000000 <= v < 0xfff00000


def diff_dumps(pa, pb, region="all", maxn=60, keep_ext=False):
    """words that differ between two dumps, over the address ranges both contain"""
    a, b = Dump(pa), Dump(pb)
    out = []
    for i, (lo, hi, ma) in enumerate(a.mem):
        reg = "data" if i == 0 else "arena"
        if region != "all" and region != reg:
            continue
        for lo2, hi2, mb in b.mem:
            l, h = max(lo, lo2), min(hi, hi2)
            if l >= h:
                continue
            sa, sb = ma[l - lo:h - lo], mb[l - lo2:h - lo2]
            if sa == sb:
                continue
            n = (h - l) & ~3
            wa, wb = array("I"), array("I")
            wa.frombytes(sa[:n]); wb.frombytes(sb[:n])
            for k in range(n // 4):
                if wa[k] != wb[k] and (keep_ext or not (_looks_ext(wa[k]) and _looks_ext(wb[k]))):
                    out.append((l + 4 * k, wa[k], wb[k], reg))
    return out


# ------------------------------------------------------------------ batches
def busy():
    r = subprocess.run(["pgrep", "-af", "rhost.py|rhost.exe"], capture_output=True, text=True).stdout
    return [l for l in r.splitlines() if "pgrep" not in l and "rt.py" not in l]


def run_traces(paths, frames=None, dump=None, shot=None, shot_every=None, watch=None, log_every=None,
               extra=None, jobs=8, tag="", timeout=1500, ww=None, ww_from=0):
    """ONE rhost wine batch over trace files -> (batch dir, {name: info})"""
    if busy():
        raise SystemExit("another rhost batch is running:\n" + "\n".join(busy()))
    cmd = [CAP, "python3", "tools/rhost/rhost.py", "run", *paths, "--target", "wine", "-j", str(jobs),
           "--wine-timeout", str(timeout)]
    if frames:
        cmd += ["--frames", str(frames)]
    if dump:
        cmd += ["--dump-at", ",".join(str(x) for x in dump)]
    if shot:
        cmd += ["--shot-at", ",".join(str(x) for x in shot)]
    if shot_every:
        cmd += ["--shot-every", str(shot_every)]
    if log_every:
        cmd += ["--log-every", str(log_every)]
    ex = extra or ""
    for w in watch or []:
        va = w if isinstance(w, int) else int(w, 16)
        if not 0x854000 <= va < 0x8ab2e0:   # rhost reads the address from frame 0 on: an unmapped heap page
            raise SystemExit(f"--watch {va:x}: only retail .data/.bss (0x854000..0x8ab2e0) is safe to watch "
                             "(a heap address faults at frame 0 and the batch hangs in winedbg)")
    if ww:      # {name: VA or (VA, arm frame)}: hardware write watchpoints (max 4) = a per-frame value trace.
        # Arming one slot re-arms every slot armed before it, so a later slot doubles as a RE-ARM
        # (under wine the watchpoints stop firing after a while: b04/b05).
        assert len(ww) <= 4, "4 hardware watchpoints"
        ww = {n: (v if isinstance(v, tuple) else (v, ww_from)) for n, v in ww.items()}
        ex += " --watch-write " + ",".join(f"{va:x}@{fr}" for va, fr in ww.values())
    if watch:
        ex += " --watch " + ",".join(f"{w:x}" if isinstance(w, int) else w for w in watch)
    if ex.strip():
        cmd += [f"--extra={ex.strip()}"]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=OSS, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    wall = time.time() - t0
    m = re.search(r"\[wine batch (\S+): .*→ (\S+)\]", p.stdout)
    if not m:
        sys.stdout.write(p.stdout[-3000:] + p.stderr[-3000:])
        raise SystemExit("no batch line in rhost.py output")
    bdir = m[2]
    res = {}
    for path in paths:
        name = os.path.splitext(os.path.basename(path))[0]
        res[name] = read_run(os.path.join(bdir, name), ww)
    with open(LEDGER, "a") as f:
        f.write(json.dumps({"batch": m[1], "tag": tag, "runs": len(paths), "wall_s": round(wall, 1),
                            "frames": [r.get("result", {}).get("frame") for r in res.values()],
                            "fps": [r.get("result", {}).get("fps") for r in res.values()],
                            "wall_ms": [r.get("result", {}).get("wall_ms") for r in res.values()]}) + "\n")
    return bdir, res


def read_run(rdir, ww=None):
    info = {"dir": rdir, "result": {}, "frames": {}, "dumps": {}, "shots": [], "notes": [], "ww": {}, "traps": []}
    wname, last = {}, {}
    for n, v in (ww or {}).items():
        wname.setdefault(v[0] if isinstance(v, tuple) else v, n)
    log = os.path.join(rdir, "rhost.log")
    if os.path.exists(log):
        for line in open(log, errors="replace"):
            if line.startswith("RESULT"):
                info["result"] = dict(kv.split("=", 1) for kv in line.split()[1:] if "=" in kv)
            elif line.startswith("frame "):
                m = re.match(r"frame (\d+) tick=(\d+) vclock=\d+ rng=(\w+)", line)
                if m:
                    row = {"tick": int(m[2]), "rng": m[3]}
                    tail = line.split(")")[-1]
                    for kv in tail.split():
                        if "=" in kv:
                            k, v = kv.split("=")
                            row[k] = int(v)
                    info["frames"][int(m[1])] = row
            elif line.startswith("watch "):
                m = re.match(r"watch (\w+) f(\d+) eip=(\w+) val=(\w+)", line)
                if m:      # the value AFTER the write that hit during frame f (several per frame possible: keep the last)
                    seq = info["ww"].setdefault(wname.get(int(m[1], 16), m[1]), [])
                    f, v = int(m[2]), int(m[4], 16)
                    if seq and seq[-1][0] == f:
                        seq[-1] = (f, v)
                    elif not seq or seq[-1][1] != v or f > last.get(m[1], f) + 1:
                        # a repeat of the same value after a gap is kept: the watch missed a change in between
                        seq.append((f, v))
                    last[m[1]] = f
            elif line.startswith("trap "):
                m = re.match(r"trap (\w+) f(\d+)", line)
                info["traps"].append((int(m[2]), m[1].lstrip("0")))
            elif line.startswith("trap-count"):
                info["notes"].append(line.strip())
            elif re.search(r"FATAL|AV f|MessageBox", line):
                info["notes"].append(line.strip()[:300])
    if os.path.isdir(rdir):
        for fn in sorted(os.listdir(rdir)):
            if fn.startswith("state_") and fn.endswith(".rhs"):
                info["dumps"][fn[6:-4]] = os.path.join(rdir, fn)
            elif fn.startswith("shot_"):
                info["shots"].append(os.path.join(rdir, fn))
    return info


def batch(cands, tag="b", **kw):
    """cands: {name: spec}.  Writes cands/<tag>/<name>.jsonl, replays them in ONE batch."""
    d = os.path.join(CANDS, tag)
    os.makedirs(d, exist_ok=True)
    paths = []
    for name, spec in cands.items():
        p = os.path.join(d, f"{name}.jsonl")
        open(p, "w").write(compile_trace(spec))
        paths.append(p)
    if not kw.get("frames"):
        kw["frames"] = max(last_frame(s) for s in cands.values()) + 120
    return run_traces(paths, tag=tag, **kw)


def report(res, names=None, watch_frames=None, bdir=None):
    names = names or [n for n in VARS]
    if bdir:
        print(f"batch dir: {bdir}")
    for cname, info in res.items():
        r = info["result"]
        if not r:
            print(f"{cname:24s} NO RESULT  {info['notes'][:3]}")
            continue
        print(f"{cname:24s} {r.get('status')} f={r.get('frame')} tick={r.get('tick')} rng={r.get('rng')} "
              f"sem={r.get('state_sem')} semv={r.get('state_semv')} {r.get('fps')}fps {r.get('wall_ms')}ms")
        for note in info["notes"][:6]:
            print("    ! " + note)
        for tagname, path in sorted(info["dumps"].items()):
            d = Dump(path)
            print(f"    dump {tagname}: " + " ".join(f"{n}={fmt_var(n, d.var(n)[1])}" for n in names))
        if info["traps"]:
            print("    traps: " + " ".join(f"{va}@f{f}" for f, va in info["traps"][:40]))
        for n, seq in info["ww"].items():
            sv = lambda v: str(v - (1 << 32) if v >= 0x80000000 else v) if v < 0x1000000 or v >= 0x80000000 else f"{v:x}"
            if len(seq) <= 14:
                print(f"    ww {n}: " + " ".join(f"f{f}={sv(v)}" for f, v in seq))
            else:
                print(f"    ww {n}: {len(seq)} changes: " + " ".join(f"f{f}={sv(v)}" for f, v in seq[:5]) + " ... "
                      + " ".join(f"f{f}={sv(v)}" for f, v in seq[-4:]))
        if watch_frames:
            for f in watch_frames:
                row = info["frames"].get(f)
                if row:
                    print(f"    f{f}: " + " ".join(f"{k}={v}" for k, v in row.items()))


def first_frame(info, pred):
    """first logged frame whose row satisfies pred(row) (needs --log-every)"""
    for f in sorted(info["frames"]):
        if pred(info["frames"][f]):
            return f
    return None


def _ints(s):
    return [x if x == "end" else int(x) for x in s.split(",")] if s else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("run", "file"):
        p = sub.add_parser(c)
        p.add_argument("items", nargs="+")
        p.add_argument("--frames", type=int); p.add_argument("--dump"); p.add_argument("--shot")
        p.add_argument("--shot-every", type=int); p.add_argument("--watch"); p.add_argument("--log-every", type=int)
        p.add_argument("--vars"); p.add_argument("--extra"); p.add_argument("--tag", default="cli")
        p.add_argument("--at", help="print the watch/log rows at these frames")
        p.add_argument("--ww", help="name=VA[@armframe],.. (max 4): hardware write watchpoints -> every value change with its frame")
        p.add_argument("--ww-from", type=int, default=0, help="arm the watchpoints at this frame")
    p = sub.add_parser("vars"); p.add_argument("dump"); p.add_argument("--vars")
    p = sub.add_parser("diff"); p.add_argument("a"); p.add_argument("b"); p.add_argument("--region", default="all")
    p.add_argument("--max", type=int, default=60)
    sub.add_parser("cost")
    a = ap.parse_args()
    if a.cmd in ("run", "file"):
        kw = dict(frames=a.frames, dump=_ints(a.dump), shot=_ints(a.shot), shot_every=a.shot_every,
                  watch=a.watch.split(",") if a.watch else None, log_every=a.log_every, extra=a.extra,
                  ww={k: ((int(v.split("@")[0], 16), int(v.split("@")[1])) if "@" in v else int(v, 16))
                      for k, v in (i.split("=") for i in a.ww.split(","))} if a.ww else None,
                  ww_from=a.ww_from)
        if a.cmd == "run":
            bdir, res = batch(dict(i.split("=", 1) for i in a.items), tag=a.tag, **kw)
        else:
            bdir, res = run_traces([os.path.abspath(i) for i in a.items], tag=a.tag, **kw)
        report(res, a.vars.split(",") if a.vars else None, _ints(a.at), bdir)
    elif a.cmd == "vars":
        d = Dump(a.dump)
        for n in (a.vars.split(",") if a.vars else VARS):
            addr, v = d.var(n)
            print(f"{n:10s} @{addr and hex(addr)} = {fmt_var(n, v)}")
    elif a.cmd == "diff":
        rows = diff_dumps(a.a, a.b, a.region)
        print(f"{len(rows)} differing words")
        for va, x, y, reg in rows[:a.max]:
            print(f"  {va:08x} {reg:5s} {x if x is None else format(x, '08x')} {y if y is None else format(y, '08x')}")
    elif a.cmd == "cost":
        rows = [json.loads(l) for l in open(LEDGER)]
        print(f"batches={len(rows)} replays={sum(r['runs'] for r in rows)} batch_wall_s={sum(r['wall_s'] for r in rows):.0f}")
        for r in rows:
            print(f"  {r['batch']} {r['tag']:14s} runs={r['runs']} wall={r['wall_s']}s frames={r['frames']} fps={r['fps']}")


if __name__ == "__main__":
    main()
