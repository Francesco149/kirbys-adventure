"""lab.py — helpers for the agent's own scripts (run by the `python` tool inside a sandbox).

The sandbox has: this code (read-only), numpy, pillow, torch (CPU), scikit-learn; the run's checkpoints,
movie and ram.json (read-only); a writable working dir (the cwd, `lab/` of the run). No network — Jev is
reachable only through `lab.jev()` (a harness proxy with its own small budget). Up to ~16 CPU cores.

    import lab
    c = lab.load("ms-1-1")          # nes.Core positioned at a checkpoint (or lab.load() = current movie end)
    v = lab.vars(c)                 # named RAM vars, like the status line
    c.mem[0x6021]                   # any RAM byte ($0000-$07FF, $6000-$7FFF)
    for m in lab.parse("R*20 RA*8"): c.step(m)
    st = c.save(); c.load(st)       # savestates (bytes, frame, lag)
    lab.save_spec("my_try", masks)  # → out/my_try.txt; then `play` with inputs_file="my_try"
    lab.jev(state_text, questions, png=lab.png(c.frame))   # Jev decision via the harness proxy
    lab.show(c.frame, "pic")        # → out/pic.png (pass to the python tool's `show` to see it)
"""
import io
import json
import os
import socket

import env as E
import nes

RUN = os.environ.get("KIRBY_RUN", os.path.dirname(os.getcwd()))
OUT = os.path.join(os.getcwd(), "out")
os.makedirs(OUT, exist_ok=True)
parse = E.parse_spec
rle = E.rle
A, B, SELECT, START, UP, DOWN, LEFT, RIGHT = nes.A, nes.B, nes.SELECT, nes.START, nes.UP, nes.DOWN, nes.LEFT, nes.RIGHT
_vars = None


def ramvars():
    global _vars
    if _vars is None:
        _vars = E.RamVars(os.path.join(RUN, "ram.json"))
    return _vars


def vars(core):
    return ramvars().read(core.mem, core.frames)


def checkpoints():
    p = os.path.join(RUN, "checkpoints.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def movie(name=None):
    """Masks of a checkpoint's movie, or of the current movie."""
    if name is None:
        return E.parse_spec(open(os.path.join(RUN, "movie.txt")).read())
    return E.parse_spec(open(os.path.join(RUN, "checkpoints", name + ".movie")).read())


def load(name=None, core="mesen"):
    """A fresh core at checkpoint `name` (fast: loads its savestate) or at the end of the current movie (replays)."""
    c = nes.Core(core)
    if name is not None:
        ck = checkpoints()[name]
        raw = open(os.path.join(RUN, "checkpoints", name + ".state"), "rb").read()
        c.load((raw, ck["frame"], 0))   # c.frame (the picture) stays None until the next c.step()
        return c
    for m in movie():
        c.step(m, render=False)
    return c


def save_spec(name, masks):
    p = os.path.join(OUT, name + ".txt")
    open(p, "w").write(E.rle(list(masks)) + "\n")
    return p


def png(frame, scale=1):
    return E.png(frame, scale)


def show(frame, name, scale=2):
    p = os.path.join(OUT, name + ".png")
    open(p, "wb").write(E.png(frame, scale))
    return p


def jev(state, questions, png=None):
    """Jev decision through the harness proxy. Returns the answers dict (or raises on error/budget)."""
    sock = os.path.join(os.getcwd(), ".jev.sock")
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock)
    import base64
    req = {"state": state, "questions": questions}
    if png is not None:
        req["png_b64"] = base64.b64encode(png).decode()
    s.sendall(json.dumps(req).encode() + b"\n")
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    s.close()
    r = json.loads(buf)
    if "error" in r:
        raise RuntimeError(r["error"])
    return r["answers"]
