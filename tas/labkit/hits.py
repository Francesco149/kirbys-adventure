# usage: hits.py RUN FROM_FRAME BB:AAAA ...   -> for each target: run count in movie[FROM:] and first frame
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import sys, os, glob; sys.path.insert(0,ROOT + "/disasm"); sys.path.insert(0,ROOT + "/tas")
import kdcore, env as E
run=sys.argv[1]; f0=int(sys.argv[2]); tg=sys.argv[3:]
d=f"{ROOT}/tas/runs/{run}"
mv=E.parse_spec(open(d+"/movie.txt").read())
keys=sorted((int(os.path.basename(p).split("-")[0]),p) for p in glob.glob(d+"/keys/*.state"))
base,p=max(k for k in keys if k[0]<=f0)
c=kdcore.Core(instrument=False)
c.load((open(p,"rb").read(),base,0))
for i in range(base,f0): c.step(mv[i])
c.instrument(True); c.reset_stats()
offs=[kdcore.off_of(int(t[:2],16),int(t[3:],16)) for t in tg]
first={}
for i in range(f0,len(mv)):
    c.step(mv[i])
    for t,o in zip(tg,offs):
        if t not in first and c.count[o]>0: first[t]=i+1
for t,o in zip(tg,offs):
    print(t, int(c.count[o]), "first", first.get(t))
