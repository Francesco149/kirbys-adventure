import sys, collections
sys.path.insert(0, '.')
import kd, numpy as np, sprites as SP, packed as PK
d, ev, m = kd.load()
prg = m.prg
rd = ev.dcount
# pointers into poses / sprite groups from every poseptr table and ptr16 table
ptr_to = collections.defaultdict(list)
for e in d.data:
    f = e["format"] or ""
    if f.startswith("poseptr"):
        for i, t in enumerate(SP.table_targets(prg, e)):
            if t is not None: ptr_to[t].append(f"{e['name']}[{i}]" + ("" if rd[e['off']+2*i] else "(unread)"))
    elif f.startswith("packlo"):
        try:
            for i, t in enumerate(PK.table_targets(prg, d, e)):
                if t not in (None, -1): ptr_to[t].append(f"{e['name']}[{i}]" + ("" if rd[e['off']+i] else "(unread)"))
        except ValueError: pass
tot = collections.Counter()
for e in d.data:
    f = e["format"] or ""
    s, n = e["off"], e["len"]
    unread = int((rd[s:s+n] == 0).sum()) if f in ("poses","sprites","packed") else 0
    if not unread: continue
    if f in ("poses", "sprites"):
        items = SP.parse(prg, s, n, f)
        ends = [(o, o + (2 if f=='poses' else 1) + 4*k) for o, k in items]
    else:
        ends = [(s, s+n)]
    for o, e2 in ends:
        u = int((rd[o:e2] == 0).sum())
        if u == 0: continue
        state = "unread" if u == e2-o else f"part {u}/{e2-o}"
        tot[(f, state=="unread")] += u
        print(f"{f:7} {o>>13:02X}:{m.cpu(o):04X} len {e2-o:4} {state:12} {e['name']}  <- {', '.join(ptr_to.get(o, ['NO POINTER']))}")
print(tot)
