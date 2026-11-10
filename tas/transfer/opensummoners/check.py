#!/usr/bin/env python3
"""check.py — verify final.spec: two fresh replays in ONE batch, the goal predicates in order, equal hashes.

    python3 check.py            (writes final.jsonl, replays it twice, prints the verdict, copies key shots to shots/)

Evidence per predicate: `--trap` first-hit frames (scene entries, room loads), hardware write watchpoints
(`w2760`, `dlg` armed at 2700; `lx`, `ly` armed at 2812, which also re-arms the first two) and state dumps
at the key frames (pointer chains evaluated by rt.Dump).
"""
import os
import shutil
import sys

import rt

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = " ".join(l.split("#")[0].strip() for l in open(os.path.join(HERE, "final.spec")) if l.split("#")[0].strip())
KEY = [690, 780, 1100, 1300, 2400, 2700, 2811, 2960, 3109, 3222, 3290, 3505, 3615, 3700, 3900, 4000, 4100, 4140]   # dump + shot frames
BEDROOM = 210141
HOUSE = 210140


def at(seq, f):
    """value of a watched word at the end of frame f (None before its first logged write)"""
    v = None
    for fr, val in seq:
        if fr > f:
            break
        v = val
    return v


def first(seq, pred, lo=0):
    return next((f for f, v in seq if f >= lo and pred(v)), None)


def main():
    os.makedirs(os.path.join(HERE, "cands", "final"), exist_ok=True)
    tr = rt.compile_trace(SPEC)
    open(os.path.join(HERE, "final.jsonl"), "w").write(tr)
    paths = []
    for n in ("final_a", "final_b"):
        p = os.path.join(HERE, "cands", "final", n + ".jsonl")
        open(p, "w").write(tr)
        paths.append(p)
    frames = rt.last_frame(SPEC) + 120
    # 4 hardware watchpoints; arming a later slot re-arms the earlier ones (they stop firing when a dialogue closes)
    ww = {"w2760": (0x20075b90, 2700), "dlg": (0x20070e44, 2700), "lx": (0x20397084, 2812), "roomp": (0x20074468, 3510)}
    bdir, res = rt.run_traces(paths, frames=frames, dump=KEY + [frames - 1], shot=KEY + [frames - 1], ww=ww,
                              extra="--trap 56aea0,564780,586010 --trap-max 40", tag="final")
    rt.report(res, ["world", "room_id", "lx", "ly", "w2760", "dlg"], bdir=bdir)
    ok = True

    def verdict(name, cond, detail):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {name}: {detail}")

    for n, info in res.items():
        print(f"== predicates, {n}")
        r = info["result"]
        traps = info["traps"]
        hit = lambda va, k=0: ([f for f, v in traps if v == va] + [None] * 8)[k]
        D = {int(t[1:]): rt.Dump(p) for t, p in info["dumps"].items() if t.startswith("f")}
        var = lambda f, name: D[f].var(name)[1]
        w, dl, lx, rp = (info["ww"].get(k, []) for k in ("w2760", "dlg", "lx", "roomp"))
        end = frames - 1
        verdict("never: crash / abort", r.get("status") == "ok" and not any("AV f" in x for x in info["notes"]), f"status={r.get('status')}")
        verdict("P1 title scene entered", hit("56aea0") is not None and var(690, "world") == 0, f"trap 0x56aea0 first hit f{hit('56aea0')}; world=0 at f690")
        verdict("P2 new-game config scene entered", hit("564780") and hit("564780") > hit("56aea0"), f"trap 0x564780 f{hit('564780')}")
        verdict("P3 in game (first room loaded)", hit("586010") and var(1300, "room_id") == 210110, f"room setup 0x586010 f{hit('586010')}; room_id={var(1300, 'room_id')} at f1300")
        verdict("P4 house interior", hit("586010", 2) and var(2700, "room_id") == HOUSE and var(2700, "w2760") == 1,
                f"3rd room setup f{hit('586010', 2)}; room_id={var(2700, 'room_id')} w2760={var(2700, 'w2760')} (still scripted) at f2700")
        c = first(w, lambda v: v == 0, 2700)
        verdict("P5 control (w2760==0 and dlg==0 in the house)", c and at(dl, c) == 0 and var(2811, "room_id") == HOUSE and var(2811, "w2760") == 0,
                f"first frame f{c}; dump f2811: w2760={var(2811, 'w2760')} dlg={var(2811, 'dlg')} lx={var(2811, 'lx')}")
        m = first(lx, lambda v: v > 19200 + 1000, 2812)
        verdict("P5b control is real: Right moves the leader", m, f"lx > 20200 first at f{m} (Right held from f2815)")
        top = first(lx, lambda v: v >= 87500, 2812)
        verdict("P6 crossed the room and climbed the stairs", top and var(3109, "ly") == 36000 and var(3109, "room_id") == HOUSE,
                f"lx>=87500 first at f{top} (spawn 19200,52000); dump f3109 lx={var(3109, 'lx')} ly={var(3109, 'ly')}")
        verdict("P6b jumped onto the kitchen floor", var(3222, "ly") == 32800, f"dump f3222 lx={var(3222, 'lx')} ly={var(3222, 'ly')}")
        t = first(w, lambda v: v == 1, 2812)
        d = first(dl, lambda v: v != 0, t or 10**9)
        verdict("P7 (G3) talked to the mother: script starts, dialogue box opens", t and d and var(3290, "dlg") not in (0, None),
                f"w2760 -> 1 at f{t} (X pressed f3225), dlg != 0 at f{d}; dump f3290 w2760={var(3290, 'w2760')} dlg={var(3290, 'dlg'):x}")
        verdict("P8 conversation over, control back", var(3505, "w2760") == 0 and var(3505, "dlg") == 0 and var(3505, "room_id") == HOUSE,
                f"dump f3505 w2760={var(3505, 'w2760')} dlg={var(3505, 'dlg')} room_id={var(3505, 'room_id')}")
        nload = [f for f, v in traps if v == "586010"]
        u = first(w, lambda v: v == 1, 3511)
        verdict("P9 (G2) left the first room through the bedroom door", len(nload) == 4 and var(3700, "room_id") == BEDROOM and var(3615, "room_id") == HOUSE,
                f"door script starts (w2760 -> 1) f{u} (Up pressed f3621), 4th room setup f{hit('586010', 3)}; "
                f"room_id {var(3615, 'room_id')} at f3615 -> {var(3700, 'room_id')} at f3700")
        free = next((f for f in (3900, 4000, 4100, 4140) if var(f, "room_id") == BEDROOM and var(f, "w2760") == 0 and var(f, "dlg") == 0), None)
        verdict("P10 control in the second room", free and var(end, "lx") != var(4140, "lx"),
                f"w2760==0 and dlg==0 in {BEDROOM} at dump f{free}; Right from f4150: lx {var(4140, 'lx')} -> {var(end, 'lx')}")
        verdict("never: back to title / extra room loads", len(nload) == 4 and var(end, "world") not in (0, None),
                f"room setups at {nload}, world={var(end, 'world'):x} at the end")
    a, b = (res[n]["result"] for n in ("final_a", "final_b"))
    same = all(a.get(k) == b.get(k) for k in ("frame", "tick", "rng", "state_semv"))
    verdict("determinism: two replays, same frame/tick/rng/state_semv", same,
            " ".join(f"{k}={a.get(k)}/{b.get(k)}" for k in ("frame", "tick", "rng", "state_semv")))
    print(f"  (state_sem {a.get('state_sem')}/{b.get('state_sem')}, state_full {a.get('state_full')}/{b.get('state_full')}: "
          "these include wine-volatile words; rhost's wine gate is state_semv)")
    os.makedirs(os.path.join(HERE, "shots"), exist_ok=True)
    for s in res["final_a"]["shots"]:
        shutil.copy(s, os.path.join(HERE, "shots", "final_" + os.path.basename(s)))
    print("VERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
