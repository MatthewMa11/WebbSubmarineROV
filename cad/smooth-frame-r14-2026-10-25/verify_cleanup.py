from pathlib import Path
import sys,json,collections,math
r=Path(__file__).resolve().parent;v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
n={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],n)
t=n['t'];cyl=n['cylinder'];read=n['solids']
ss=read(Path(sys.argv[1]) if len(sys.argv)>1 else r/'Thruster-R14-smooth-frame.step')
old=read(r.parent/'concave-cap-r13-2026-10-25/Thruster-R13-concave-cap.step')
def frame(parts):return next(s for s in parts if t.limits(s)[0][1]<-29 and t.limits(s)[1][0]>50)
h=frame(ss);oh=frame(old);checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def sig(q):return tuple(round(x,4) for pair in t.limits(q) for x in pair)+(round(t.volume(q),3),round(t.area(q),3))
def common(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
check('other46 parts including cone fan actual metal and bolts are unchanged',len(ss)==len(old)==47 and collections.Counter(sig(s) for s in ss if not s.IsSame(h))==collections.Counter(sig(s) for s in old if not s.IsSame(oh)))
# Four small probes at the tips of the pictured obsolete crescent features.
probes=[]
for d in [(0,1),(-1,0),(0,-1),(1,0)]:
 p=(d[0]*48.3,16.5,d[1]*48.3);q=cyl(.25,p,(0,1,0),.5)
 probes.append(dict(old=common(oh,q),new=common(h,q)))
check('all four obsolete crescent tips removed in actual geometry',all(p['old']>.08 and p['new']<1e-5 for p in probes),probes=probes)
# The annular skin must contain an inset sample at each radius on the quintic profile.
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
samples=[]
for u in [.05,.2,.35,.5,.65,.8,.95]:
 y=12+18*u;radius=46.2977716548645+(43-46.2977716548645)*(10*u**3-15*u**4+6*u**5)
 # Diagonal meridians avoid the four necessary current bolt posts.
 for angle in [45,135,225,315]:
  a=math.radians(angle);rr=radius-.03
  inside=BRepClass3d_SolidClassifier(h,gp_Pnt(rr*math.cos(a),y,rr*math.sin(a)),1e-7).State()==TopAbs_IN
  rr=radius+.03;outside=BRepClass3d_SolidClassifier(h,gp_Pnt(rr*math.cos(a),y,rr*math.sin(a)),1e-7).State()!=TopAbs_IN
  samples.append(inside and outside)
check('smooth quintic fairing follows designed profile at28 points',all(samples),count=len(samples))
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Sphere,GeomAbs_Torus
roots=[];rounds=[];ex=TopExp_Explorer(h,TopAbs_FACE)
while ex.More():
 f=TopoDS.Face(ex.Current());a=BRepAdaptor_Surface(f);lo,hi=t.limits(f)
 if a.GetType()==GeomAbs_Sphere:
  s=a.Sphere();c=s.Location()
  if abs(s.Radius()-5)<1e-4 and abs(c.Y()-35.5)<1e-4:roots.append((round(c.X(),4),round(c.Z(),4)))
 if lo[1]>30 and hi[1]<36:rounds.append(t.area(f))
 ex.Next()
check('four necessary bolt posts have rounded5mm roots',len(set(roots))==4,root_axes=roots)
# Current mechanical interface region must match R13, including roof, pockets and pilots.
zone=cyl(60,(0,40.8,0),(0,1,0),10)
a=t.boolean(t.BRepAlgoAPI_Common,h,zone);b=t.boolean(t.BRepAlgoAPI_Common,oh,zone)
da=abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,a,b)));db=abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,b,a)))
check('working R13 nut pockets roof seats and pilots retained',max(da,db)<1e-4,symmetric_difference_mm3=[da,db])
(r/'cleanup-verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
