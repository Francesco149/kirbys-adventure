
import sys,os;sys.path.insert(0,os.getcwd())
import lab,flow2
if __name__=="__main__":
    ck,tx,ty,cur,prev,name=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
    beam=int(sys.argv[7]) if len(sys.argv)>7 else 256
    depth=int(sys.argv[8]) if len(sys.argv)>8 else 80
    sol=[int(a,16) for a in os.environ.get('SOLIDS','').split(',') if a]
    acts=os.environ["ACTS"].split("|")
    m=flow2.flow(ck,(tx,ty),acts,solids=sol,beam=beam,depth=depth,
        goal=lambda v:v['room'] not in (cur,prev) and v['hp']<48,
        avoid=lambda v:v['hp']>47 or v['room']==prev)
    lab.save_spec(name,m); print('frames',len(m))
