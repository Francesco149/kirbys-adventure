import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import sys
sys.path.insert(0,ROOT + '/disasm')
import numpy as np, packed
rom=open(ROOT + '/roms/usa-rev-a.nes','rb').read()
prg=np.frombuffer(rom[16:16+0x80000],dtype=np.uint8)
def b(bank,addr): return int(prg[bank*0x2000+(addr&0x1FFF)])
NR=327
def stream(bank,addr):
    off=bank*0x2000+(addr&0x1FFF); return packed.unpack(prg,off,min(off+0x4000,len(prg)))
def tileset(n):
    ts=b(0x12,0x8618+n)
    lo,hi,bk=b(0x12,0x8A4F+ts),b(0x12,0x8A1E+ts),b(0x12,0x89ED+ts)&0x7f
    s=stream(bk,hi<<8|lo); return ts,s
def room(n):
    lo,hi,bk=b(0x12,0x88A6+n),b(0x12,0x875F+n),b(0x12,0x84D1+n)&0x7f
    s=stream(bk,hi<<8|lo)
    w,h=s[0],s[1]
    scr=s[8:8+w*h]
    mp=s[0xDA:]
    ts,t=tileset(n)
    props=t[1088:1344] if t and len(t)>=1344 else None
    return dict(w=w,h=h,scr=scr,map=mp,props=props,ts=ts)
def block(r,x,y):
    """block number at pixel x,y"""
    cx,cy=x//256,y//192
    if cx>=r['w'] or cy>=r['h'] or x<0 or y<0: return None
    sc=r['scr'][cx+cy*r['w']]
    i=sc*192+((y%192)//16)*16+(x%256)//16
    return r['map'][i] if i<len(r['map']) else None
def prop(r,x,y):
    bl=block(r,x,y)
    if bl is None: return None
    p=r['props'][bl]
    return 0 if p>=0x7f else p
def shape(p): return b(0x12,0x83D3+p)
def pclass(p): return b(0x3F,0xF777+p)>>1
def objs(n):
    bk=b(0x12,0x8A80+n); a=b(0x12,0x8BC7+n)<<8|b(0x12,0x8D0E+n)
    if a==0: return []
    base=a
    cells=b(bk,base); ends=[b(bk,base+2+i) for i in range(cells)]
    nobj=ends[-1] if ends else 0
    xy=[b(bk,base+2+cells+i) for i in range(nobj)]
    kd=[b(bk,base+2+cells+nobj+i) for i in range(nobj)]
    out=[];start=0
    r=None
    for c,e in enumerate(ends):
        for i in range(start,e):
            out.append((c,xy[i],kd[i]))
        start=e
    return out
def kind_type(k): return b(0x13,0xA9D2+k)
def kind_vars(k): return b(0x13,0xAAD2+k)
def placements(types):
    res=[]
    for n in range(NR):
        try: L=objs(n)
        except Exception: continue
        w=None
        for c,xy,k in L:
            t=kind_type(k)
            if t in types:
                if w is None:
                    try: w=room(n)['w']
                    except Exception: w=1
                cx,cy=c%max(w,1),c//max(w,1)
                x=cx*256+8+16*(xy>>4); y=cy*256+8+16*(xy&15)
                res.append((n,k,t,kind_vars(k),x,y))
    return res
CH={0:'.',1:'#'}
def show(n,x0=None,y0=None,x1=None,y1=None,marks=()):
    r=room(n); W,H=r['w']*256,r['h']*192
    x0=x0 or 0;y0=y0 or 0;x1=x1 or W;y1=y1 or H
    for y in range(y0-y0%16,y1,16):
        row=''
        for x in range(x0-x0%16,x1,16):
            m=[c for (mx,my,c) in marks if mx//16==x//16 and my//16==y//16]
            if m: row+=m[0]; continue
            p=prop(r,x,y)
            if p is None: row+=' ';continue
            s=shape(p); c=pclass(p)
            ch='~' if s&0x80 else ('#' if c==1 else '.' if c==0 else '=' if c in(2,3) else '/' if c<10 else '^')
            if s&0x80 and c==1: ch='%'
            row+=ch
        print('%4d '%y+row)
def cls(r,x,y):
    p=prop(r,x,y)
    if p is None: return None
    return pclass(p)
def water(r,x,y):
    p=prop(r,x,y)
    return p is not None and bool(shape(p)&0x80)
def segment(r,x,y):
    """drop to floor, then walk segment: returns (y_stand, xl, xr, end_left, end_right, ceil_min)"""
    H=r['h']*192
    yy=y
    while yy<H:
        c=cls(r,x,yy+8)
        if c is not None and 1<=c<=9: break
        yy+=16
    if yy>=H: return None
    bx=x//16
    def ok(cx):
        c0=cls(r,cx*16+8,yy); c1=cls(r,cx*16+8,yy+8)
        return c0 is not None and c0!=1 and c1 is not None and 1<=c1<=9
    l=bx
    while ok(l-1): l-=1
    rr=bx
    while ok(rr+1): rr+=1
    def why(cx):
        c0=cls(r,cx*16+8,yy)
        if c0 is None: return 'edge'
        if c0==1: return 'wall'
        return 'ledge'
    ceil=[]
    for cx in range(l,rr+1):
        d=None
        for k in range(1,12):
            c=cls(r,cx*16+8,yy-16*k)
            if c is None: break
            if c==1 or c in (10,11): d=16*k-16; break
        ceil.append(d)
    return yy,l*16,rr*16+15,why(l-1),why(rr+1),ceil
def sshape(p):
    s=shape(p)&0x9f if False else shape(p)
    v=s&0x1f
    return s  # raw
def ground(r,x,y):
    """the obj_shape_off test: shape (raw byte) signed >= 2"""
    p=prop(r,x,y)
    if p is None: return None
    s=shape(p); s=s-256 if s>=128 else s
    return s>=2
def scan(types):
    for (n,k,t,v,x,y) in placements(types):
        r=room(n)
        below=cls(r,x,y+16); here=cls(r,x,y)
        s=segment(r,x,y)
        info=''
        if s:
            yy,xl,xr,el,er,ceil=s
            bad=[]
            for cx in range(xl,xr+1,16):
                g=ground(r,cx+8,yy+16)  # floor block row: block below body
                w=water(r,cx+8,yy+16) or water(r,cx+8,yy)
                if not g or w: bad.append((cx,'ng' if not g else '','w' if w else '', hex(prop(r,cx+8,yy+16))))
            info='seg y%d %d-%d %s/%s ceil%s bad%s'%(yy,xl,xr,el,er,[c for c in ceil],bad)
        print(n,hex(k),hex(t),'v%02x'%v,x,y,'here',here,'below',below,info)
def extra(p): return b(0x12,0x8452+p)
def floorinfo(types):
    for (n,k,t,v,x,y) in placements(types):
        r=room(n); s=segment(r,x,y)
        if not s: print(n,'none'); continue
        yy,xl,xr,el,er,ceil=s
        fl=[]
        for cx in range(xl-16,xr+17,16):
            p=prop(r,cx+8,yy+8)
            if p is None: fl.append('--'); continue
            fl.append('%x/%x/%x'%(shape(p),pclass(p),extra(p)))
        print(n,hex(k),x,yy,xl,xr,el,er,' '.join(fl))
def show2(n,x0=None,y0=None,x1=None,y1=None,types=None):
    P=[(x,y,'T') for (m,k,t,v,x,y) in placements(types or set()) if m==n]
    r=room(n); W,H=r['w']*256,r['h']*192
    x0=x0 or 0;y0=y0 or 0;x1=x1 or W;y1=y1 or H
    print('     '+''.join(str((x//16)%10) for x in range(x0-x0%16,x1,16)))
    for y in range(y0-y0%16,y1,16):
        row=''
        for x in range(x0-x0%16,x1,16):
            m=[c for (mx,my,c) in P if mx//16==x//16 and my//16==y//16]
            if m: row+=m[0]; continue
            p=prop(r,x,y)
            if p is None: row+=' ';continue
            s=shape(p); c=pclass(p)
            if s&0x1f in (9,0xa,0xb) : ch='*'
            elif s&0x80: ch='%' if c==1 else '~'
            else: ch='#' if c==1 else '.' if c==0 else '=' if c in(2,3) else '/' if c<10 else '^'
            row+=ch
        print('%4d '%y+row)
