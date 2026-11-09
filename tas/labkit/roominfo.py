"""roominfo.info(c): collision map of the current room (legend of every attribute value) + door px coords."""
import sys,os;sys.path.insert(0,os.getcwd())
import lab,numpy as np,flowsearch as fs
def info(c):
    G=fs.grid(c); v=lab.vars(c)
    vals=sorted(set(G.flatten().tolist()))
    ch={}; spec={0xff:'.',0x28:'D',0x30:'~',0x0d:'#',0x0f:'f',0x23:'H',0x20:'b'}
    pool='0123456789abcdeghijklmnopqrstuvwxyz'
    i=0
    for a in vals:
        if a in spec: ch[a]=spec[a]
        else: ch[a]=pool[i]; i+=1
    print('room',v['room'],'kirby',v['x'],v['y'],'tile',v['x']//16,v['y']//16,'shape',G.shape)
    print('legend',{ch[a]:hex(a) for a in vals})
    kx,ky=v['x']//16,v['y']//16
    for r in range(G.shape[0]):
        print('%2d '%r+''.join('K' if (r==ky and q==kx) else ch[int(G[r,q])] for q in range(G.shape[1])))
    print('doors',[(int(r),int(q),int(q)*16+8,int(r)*16+9) for r,q in zip(*np.where(G==0x28))])
if __name__=="__main__":
    info(lab.load(sys.argv[1] if len(sys.argv)>1 else None))
