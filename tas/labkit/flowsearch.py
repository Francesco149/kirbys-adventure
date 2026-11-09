
import lab, numpy as np, time, heapq
from multiprocessing import get_context
SOLID=0x0D
ONEWAY=set()  # tiles that can't be entered from above. Normal Kirby drops through thin platforms (0x0f) with Down
              # and climbs ladders (0x23) both ways, so nothing (w12 runs); a UFO can't drop through: use {0x0f}
BREAK={0x1c,0x1d,0x1e}
BOMB={0x20,0x21,0x22}
BOMBPASS=True
def grid(c):
    m=lambda a:int(c.mem[a])
    W=m(0x67EE);H=m(0x67EF); col=[m(0x7F00+i) for i in range(256)]
    G=np.zeros((H*12,W*16),dtype=np.int16)
    for sy in range(H):
        for sx in range(W):
            base=0x68C8+(sy*W+sx)*192
            for ty in range(12):
                for tx in range(16):
                    G[sy*12+ty,sx*16+tx]=col[m(base+ty*16+tx)]
    return G
def distfield(G,tx,ty):
    H,W=G.shape; INF=10**6
    D=np.full((H,W),INF,dtype=np.int64)
    D[ty,tx]=0; pq=[(0,ty,tx)]
    while pq:
        d,y,x=heapq.heappop(pq)
        if d>D[y,x]: continue
        for dy,dx,c in ((0,1,10),(0,-1,10),(1,0,10),(-1,0,10),(1,1,14),(1,-1,14),(-1,1,14),(-1,-1,14)):
            ny,nx=y+dy,x+dx
            if 0<=ny<H and 0<=nx<W and G[ny,nx]!=SOLID and (BOMBPASS or int(G[ny,nx]) not in BOMB):
                if ny>y and int(G[ny,nx]) in ONEWAY: continue   # entering a one-way tile from above
                if dx and dy and (G[y,nx]==SOLID or G[ny,x]==SOLID): continue
                c2=c+(40 if int(G[ny,nx]) in BREAK or int(G[ny,nx]) in BOMB else 0)
                if d+c2<D[ny,nx]: D[ny,nx]=d+c2; heapq.heappush(pq,(d+c2,ny,nx))
    return D
_c=None
def _init(ck):
    global _c
    _c=lab.load(ck)
def _sig(c):
    n=int(c.mem[0x67EE])*int(c.mem[0x67EF])*192
    return hash(bytes(c.wram[0x8C8:0x8C8+n].tolist()))
def _run(args):
    st,acts=args
    c=_c; out=[]
    for a in acts:
        c.load(st)
        for m in a: _=c.step(m)
        v=lab.vars(c); v['sig']=_sig(c)
        out.append((c.save(),v))
    return out
def score_of(v,D,fine):
    x,y=v['x'],v['y']
    ty=min(max(y//16,0),D.shape[0]-1); tx=min(max(x//16,0),D.shape[1]-1)
    return -(int(D[ty,tx])*16//10) - fine(v)
def flow(ck, target, actions, beam=256, depth=60, goal=None, avoid=None, fine=None, workers=16, key=None, G_edit=None):
    """target in pixels; goal/avoid/fine take vars dict. Returns masks (best or goal)."""
    c=lab.load(ck); G=grid(c)
    if G_edit: G_edit(G)
    D=distfield(G,target[0]//16,target[1]//16)
    fine=fine or (lambda v:0)
    acts=[lab.parse(a) for a in actions]
    v0=lab.vars(c); print('start',v0['x'],v0['y'],'dist',D[min(v0['y']//16,D.shape[0]-1),min(v0['x']//16,D.shape[1]-1)])
    pool=get_context('spawn').Pool(workers,initializer=_init,initargs=(ck,))
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
                    print('GOAL depth',dep+1,'frames',len(masks),'t',round(time.time()-t0))
                    return masks
                if avoid and avoid(v): continue
                cand.append((score_of(v,D,fine),ns,nseq,v))
        cand.sort(key=lambda t:-t[0])
        seen=set(); states=[]
        for sc,ns,nseq,v in cand:
            k=(key(v) if key else (v['x']//3,v['y']//3,v['sig']))
            if k in seen: continue
            seen.add(k); states.append((ns,nseq,v))
            if len(states)>=beam: break
        if not states: break
        best=cand[0]
        if dep%5==0: print('dep',dep+1,'best',best[0],best[3]['x'],best[3]['y'],'hp',best[3]['hp'],'t',round(time.time()-t0))
    finally:
        pool.terminate()
    print('no goal; best',best[0],best[3]['x'],best[3]['y'])
    return [m for i in best[2] for m in acts[i]]
