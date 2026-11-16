# rbrute.py RUN CKPT "TARGETS" "AVOID" N LEN "tok1|tok2|..." [prefix]
# random specs from tokens; reports for each target the shortest spec found
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import sys, json, random; sys.path.insert(0,ROOT + "/disasm"); sys.path.insert(0,ROOT + "/tas")
import kdcore, env as E
run, ck, targets, avoid, N, L, toks = sys.argv[1:8]; prefix = sys.argv[8] if len(sys.argv)>8 else ""
toks=toks.split("|"); N=int(N); L=int(L)
d=f"{ROOT}/tas/runs/{run}"
cks=json.load(open(d+"/checkpoints.json")); f0=cks[ck]["frame"]
st=(open(f"{d}/checkpoints/{ck}.state","rb").read(), f0, 0)
c=kdcore.Core(instrument=True); m=c.mem
tg=targets.split(); offs=[kdcore.off_of(int(t[:2],16),int(t[3:],16)) for t in tg]
best={}
random.seed(int(__import__('os').environ.get("SEED","1")))
for it in range(N):
    sp=(prefix+" "+" ".join(random.choice(toks) for _ in range(L))).strip()
    c.load(st); c.reset_stats()
    for i,mk in enumerate(E.parse_spec(sp)):
        c.step(mk)
        if avoid and eval(avoid,{"m":m}): break
        for t,o in zip(tg,offs):
            if c.count[o]>0 and (t not in best or best[t][0]>i+1):
                best[t]=(i+1,sp); print("HIT",t,i+1,sp,flush=True)
        if all(c.count[o]>0 for o in offs): break
print("best",{t:b[0] for t,b in best.items()})
