"""Independent STEP checks. Does not assert physical clamp force or PLA life."""
from pathlib import Path
import sys,json,math
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
globals().update({k:ns[k] for k in ('t','solids','cylinder','BRepCheck_Analyzer','TopExp_Explorer','TopAbs_FACE','TopoDS','BRepAdaptor_Surface','GeomAbs_Cylinder')})
ss=solids(r/'Thruster-R9-forward-fan.step')
old,oldrings,oldh=ns['read'](r.parent/'bolt-free-retention-2026-10-24/Thruster-R7-bolt-free.step')
checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def common(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
def sig(s):return tuple(round(v,4) for pair in t.limits(s) for v in pair)+(round(t.volume(s),3),round(t.area(s),3))
p={};extra=[]
for s in ss:
 lo,hi=t.limits(s);dx,dy,dz=span(s)
 if lo[1]<-30 and dx>90:n='nozzle'
 elif dz>70 and dx<60:n='fan'
 elif dx>80 and lo[1]>10:n='cover'
 elif 27<dx<29 and dy>25:n='rotor'
 elif 27<dx<29 and dy<6:n='stator'
 elif 40<dx<43 and 6<dy<8 and 5<dz<7:n='jaw'
 else:extra.append(s);continue
 assert n not in p,n;p[n]=s
check('six mechanical parts and forty fasteners',len(p)==6 and len(extra)==40,total=len(ss),parts=list(p),hardware=len(extra))
assert len(p)==6
for n in ('nozzle','cover','rotor','stator'):
 dv=abs(t.volume(p[n])-t.volume(old[n]));da=abs(t.area(p[n])-t.area(old[n]));db=max(abs(a-b) for aa,bb in zip(t.limits(p[n]),t.limits(old[n])) for a,b in zip(aa,bb))
 check(n+' geometry and placement unchanged',dv<.01 and da<.01 and db<.001,volume_delta_mm3=dv,area_delta_mm2=da,bounds_delta_mm=db)
oldsign=[sig(q) for q in oldh];stationary=[q for q in extra if sig(q) in oldsign];newhardware=[q for q in extra if sig(q) not in oldsign]
check('all thirty-six original stationary fasteners preserved',len(stationary)==36 and len(set(sig(q) for q in stationary))==36)
check('exactly four new clamp fasteners',len(newhardware)==4,dimensions=[span(q) for q in newhardware])
bolts=[q for q in newhardware if span(q)[2]>18];nuts=[q for q in newhardware if 2.39<span(q)[2]<2.41]
check('two M3x16 bolts and two AF5.5 nuts',len(bolts)==2 and len(nuts)==2 and all(abs(span(q)[1]-5.5)<.001 for q in nuts))
keys=[];bore=[];ex=TopExp_Explorer(p['fan'],TopAbs_FACE)
while ex.More():
 f=TopoDS.Face(ex.Current());sf=BRepAdaptor_Surface(f)
 if sf.GetType()==GeomAbs_Cylinder:
  c=sf.Cylinder();a=c.Axis();o=a.Location()
  if abs(c.Radius()-2.75)<1e-5 and abs(a.Direction().Y())>.9999:keys.append((round(o.X(),5),round(o.Z(),5)))
  if abs(c.Radius()-1.65)<1e-5 and abs(a.Direction().Y())>.9999:bore.append(t.limits(f))
 ex.Next()
check('four solid 5.5 mm keys preserve 18 mm motor pattern',sorted(set(keys))==[(-9.,0.),(0.,-9.),(0.,9.),(9.,0.)],axes_mm=sorted(set(keys)))
check('3.3 mm shaft bore provides 3.05 mm nominal grip',bool(bore) and min(b[0][1] for b in bore)>16.24 and max(b[1][1] for b in bore)>19.29,bore_bounds=bore)
shaft=cylinder(1.5875,(0,16.25,0),(0,1,0),3.05)
check('3.175 mm reference shaft clears both unloaded jaws',common(p['fan'],shaft)<1e-5 and common(p['jaw'],shaft)<1e-5)
check('jaw split retains 0.3 mm nominal closing gap',abs(t.limits(p['jaw'])[0][2]-.3)<.001 and t.distance(p['fan'],p['jaw'])>.19,minimum_peripheral_gap_mm=t.distance(p['fan'],p['jaw']))
empty=cylinder(11.31,(0,5.59,0),(0,1,0),4.42)
check('no printed spacer in motor interior',sum(common(q,empty) for q in (p['fan'],p['jaw']))<1e-5)
def invalid_faces(q):
 a=BRepCheck_Analyzer(q);ex=TopExp_Explorer(q,TopAbs_FACE);out=[]
 while ex.More():
  f=ex.Current()
  if not a.IsValid(f):out.append(tuple(round(v,5) for pair in t.limits(f) for v in pair))
  ex.Next()
 return sorted(out)
bad=invalid_faces(p['fan']);oldbad=invalid_faces(old['propeller'])
shifted_bad=[tuple(round(v+(8.0 if i in (1,4) else 0),5) for i,v in enumerate(q)) for q in oldbad]
check('all edited fan faces valid; any inherited tip slivers translate with blades',all(q in shifted_bad for q in bad),invalid_face_bounds=bad)
check('upper jaw and four new fasteners pass complete B-rep validity',all(BRepCheck_Analyzer(q).IsValid() for q in [p['jaw']]+newhardware))
clashes=[]
rotating=[('fan',p['fan']),('jaw',p['jaw'])]+[('new hardware '+str(i),q) for i,q in enumerate(newhardware)]
for i,(an,a) in enumerate(rotating):
 for bn,b in rotating[i+1:]+[(n,p[n]) for n in ('rotor','stator','nozzle','cover')]:
  vol=common(a,b)
  if vol>1e-4:clashes.append((an,bn,vol))
check('all new rotating geometry has zero nominal penetration',not clashes,clashes_mm3=clashes)
# Includes 0.0625 mm radial allowance for taking up the nominal bore clearance.
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
core=cylinder(22.27,(0,-3.001,0),(0,1,0),22.302)
ring=t.boolean(t.BRepAlgoAPI_Cut,cylinder(35.57,(0,13.0,0),(0,1,0),6.61),cylinder(21.93,(0,12.99,0),(0,1,0),6.63))
sweep=t.boolean(BRepAlgoAPI_Fuse,core,ring)
escaped={n:abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,q,sweep))) for n,q in rotating}
check('360-degree conservative envelope contains all rotating parts',max(escaped.values())<1e-4,escaped_mm3=escaped)
gaps={n:t.distance(sweep,p[n]) for n in ('nozzle','cover','stator')}
check('continuous full-turn envelope clears unchanged stationary structure',gaps['nozzle']>.60 and gaps['cover']>.69 and gaps['stator']>2.9,gaps_mm=gaps)
region=cylinder(27.01,(0,-6.2,0),(0,1,0),26)
a=t.boolean(t.BRepAlgoAPI_Cut,p['fan'],region);b=t.boolean(t.BRepAlgoAPI_Cut,old['propeller'],region)
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Vec
back=gp_Trsf();back.SetTranslation(gp_Vec(0,-8.0,0));a=BRepBuilderAPI_Transform(a,back,True).Shape()
dv=abs(t.volume(a)-t.volume(b));da=abs(t.area(a)-t.area(b))
from profile_check import profile_check
profile=profile_check(r)
check('outer blade sampled surfaces agree within 0.02 mm after 8 mm translation',profile['passed'],surface_comparison=profile,step_mass_integration_diagnostics={'volume_delta_mm3':dv,'area_delta_mm2':da})
fastener_gaps=[t.distance(sweep,q) for q in stationary]
check('all stationary fasteners clear the full-turn envelope',len(fastener_gaps)==36 and min(fastener_gaps)>4.8,minimum_gap_mm=min(fastener_gaps))
(r/'verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
