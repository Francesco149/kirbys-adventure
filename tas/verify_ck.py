"""verify_ck.py — does checkpoint <name> replay from power-on? Compares, in two fresh processes, the RAM after
replaying the checkpoint's movie from power-on vs. after loading its savestate (+1 frame each, same input).
   KIRBY_CORE=fceumm python verify_ck.py runs/main ms-1-1"""
import hashlib
import json
import multiprocessing as mp
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import env as E
import nes


CORE = os.environ.get("KIRBY_CORE", "fceumm")


def replay(movie):
    c = nes.Core(CORE)
    for m in movie:
        c.step(m, render=False)
    c.step(0, render=False)
    return hashlib.sha1(c.ram_bytes()).hexdigest(), c.frames


def from_state(raw, frame):
    c = nes.Core(CORE)
    c.load((raw, frame, 0))
    c.step(0, render=False)
    return hashlib.sha1(c.ram_bytes()).hexdigest(), c.frames


if __name__ == "__main__":
    run, name = sys.argv[1], sys.argv[2]
    ck = json.load(open(os.path.join(run, "checkpoints.json")))[name]
    movie = E.parse_spec(open(os.path.join(run, "checkpoints", name + ".movie")).read())
    raw = open(os.path.join(run, "checkpoints", name + ".state"), "rb").read()
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(2, mp_context=ctx) as ex:
        a = ex.submit(replay, movie)
        b = ex.submit(from_state, raw, ck["frame"])
        (ha, fa), (hb, fb) = a.result(), b.result()
    print(f"{name}: movie {len(movie)} frames, checkpoint frame {ck['frame']}: "
          f"{'MATCH' if ha == hb and fa == fb else 'MISMATCH'} ({ha[:10]} vs {hb[:10]})")
