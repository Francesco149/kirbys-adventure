"""lab.py — helpers for the agent's own scripts (run by the `python` tool inside a sandbox).

The sandbox has: this code (read-only), numpy, pillow, torch (CPU), scikit-learn; the run's checkpoints,
movie and ram.json (read-only); a writable working dir (the cwd, `lab/` of the run). No network — Jev is
reachable only through `lab.jev()` (a harness proxy with its own small budget). Up to ~16 CPU cores.

    import lab
    c = lab.load("ms-1-1")          # the process's core positioned at a checkpoint (lab.load() = movie end;
                                    # lab.power_on() = frame 0). ONE core per process: parallelise with
                                    # multiprocessing get_context("spawn") workers that each call lab.load()
    v = lab.vars(c)                 # named RAM vars, like the status line
    c.mem[0x6021]                   # any RAM byte ($0000-$07FF, $6000-$7FFF)
    for m in lab.parse("R*20 RA*8"): c.step(m)
    st = c.save(); c.load(st)       # savestates (bytes, frame, lag)
    lab.save_spec("my_try", masks)  # → out/my_try.txt; then `play` with inputs_file="my_try"
    lab.jev(state_text, questions, png=lab.png(c.frame))   # Jev decision via the harness proxy
    lab.parse_fm2(lab.KNOWLEDGE + "/movies/3226M.fm2")     # reference TAS inputs (PRG0; see knowledge)
    c.mem[0x603D]                   # +1 per non-lag frame: lag = frames where it did not change
    lab.show(c.frame, "pic")        # → out/pic.png (pass to the python tool's `show` to see it)
"""
import io
import json
import os
import socket

import env as E
import nes

RUN = os.environ.get("KIRBY_RUN", os.path.dirname(os.getcwd()))
CORE = os.environ.get("KIRBY_CORE", "fceumm")     # the run's core; movies/states only replay on their own core
OUT = os.path.join(os.getcwd(), "out")
os.makedirs(OUT, exist_ok=True)
parse = E.parse_spec
rle = E.rle
parse_fm2 = E.parse_fm2          # e.g. lab.parse_fm2(KNOWLEDGE + "/movies/3226M.fm2")
KNOWLEDGE = os.path.join(os.path.dirname(os.path.abspath(E.__file__)), "knowledge")
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


_CORE = {}


def core():
    """This process's emulator core (one per process — libretro cores are global). For parallel work use
    multiprocessing with the 'spawn' context; each spawned worker calls lab.core()/lab.load() itself."""
    if "c" not in _CORE:
        _CORE["c"] = nes.Core(CORE)
        _CORE["power_on"] = _CORE["c"].save()
    return _CORE["c"]


def power_on():
    c = core()
    c.load(_CORE["power_on"])
    return c


def load(name=None):
    """Position this process's core at checkpoint `name` (loads its savestate) or at the end of the current
    movie (replays from power-on). Returns the core; c.frame (the picture) is None until the next c.step()."""
    c = core()
    if name is not None:
        ck = checkpoints()[name]
        raw = open(os.path.join(RUN, "checkpoints", name + ".state"), "rb").read()
        c.load((raw, ck["frame"], 0))
        return c
    power_on()
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
