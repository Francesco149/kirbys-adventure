
import lab, numpy as np, time
from multiprocessing import get_context
import flowsearch as fs
_c=None;_T=None;_S=None;_cache={}
def _init(ck,T,S):
    global _c,_T,_S
    _c=lab.load(ck);_T=T;_S=S
def _D(c,sig):
    if sig not in _cache:
        G=fs.grid(c)
        for a in _S: G[G==a]=0x0D
        _cache[sig]=fs.distfield(G,_T[0]//16,_T[1]//16)
    return _cache[sig]
def _run(args):
    st,acts=args
    c=_c; out=[]
    for a in acts:
        c.load(st)
        for m in a: _=c.step(m)
        v=lab.vars(c); sig=fs._sig(c); v['sig']=sig
        try:
            D=_D(c,sig)
            assert D.size>0
        except Exception:
            D=np.zeros((1,1),dtype=np.int64)
        ty=min(max(v['y']//16,0),D.shape[0]-1); tx=min(max(v['x']//16,0),D.shape[1]-1)
        v['score']=-(int(D[ty,tx])*16//10)
        out.append((c.save(),v))
    return out
def flow(ck,target,actions,solids=(),beam=256,depth=60,goal=None,avoid=None,workers=16):
    c=lab.load(ck); acts=[lab.parse(a) for a in actions]; v0=lab.vars(c)
    pool=get_context('spawn').Pool(workers,initializer=_init,initargs=(ck,target,list(solids)))
    states=[(c.save(),[],v0)]; best=None; t0=time.time()
    try:
      for dep in range(depth):
        res=pool.map(_run,[(s[0],acts) for s in states],chunksize=max(1,len(states)//(workers*4)))
        cand=[]
        for (st,seq,_),outs in zip(states,res):
            for ai,(ns,v) in enumerate(outs):
                nseq=seq+[ai]
                if goal and goal(v):
                    masks=[m for i in nseq for m in acts[i]]
                    print('GOAL depth',dep+1,'frames',len(masks),'t',round(time.time()-t0)); return masks
                if avoid and avoid(v): continue
                cand.append((v['score'],ns,nseq,v))
        cand.sort(key=lambda t:-t[0])
        seen=set(); states=[]
        for sc,ns,nseq,v in cand:
            k=(v['x']//3,v['y']//3,v['sig'])
            if k in seen: continue
            seen.add(k); states.append((ns,nseq,v))
            if len(states)>=beam: break
        if not states: break
        best=cand[0]
        if dep%5==0: print('dep',dep+1,'best',best[0],best[3]['x'],best[3]['y'],'hp',best[3]['hp'],'t',round(time.time()-t0),flush=True)
    finally: pool.terminate()
    print('no goal; best',best[0],best[3]['x'],best[3]['y'])
    return [m for i in best[2] for m in acts[i]]
