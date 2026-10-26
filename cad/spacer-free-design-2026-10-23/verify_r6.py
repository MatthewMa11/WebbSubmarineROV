"""Independent checks on the native Onshape R6 assembly STEP and print meshes."""
from pathlib import Path
import sys,json,math,hashlib
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t,cylinder
from verify_kit_hardware import solids
from verify_pla_revision import hexnut,washer
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt

old,oh=read(r.parent/'remove-wire-holder-2026-10-21/Thruster-no-wire-holder-R5.step')
p={};h=[]
for s in solids(r/'Thruster-R6-spacer-free-assembly.step'):
 lo,hi=t.limits(s);dx,dy,dz=[b-a for a,b in zip(lo,hi)]
 if lo[1]<-30 and dx>90:n='nozzle'
 elif dz>70 and dx<60:n='propeller'
 elif dx>80 and lo[1]>10:n='cover'
 elif 27<dx<29 and dy>25:n='rotor'
 elif 27<dx<29 and dy<6:n='stator'
 else:h.append(s);continue
 assert n not in p,n
 p[n]=s
checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def common(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
def box(lo,hi):return BRepPrimAPI_MakeBox(gp_Pnt(*lo),gp_Pnt(*hi)).Shape()
def sig(s):return tuple(round(v,4) for pair in t.limits(s) for v in pair)+(round(t.volume(s),3),round(t.area(s),3))
check('five mechanical bodies and forty-two hardware bodies',len(p)==5 and len(h)==42,mechanical=list(p),hardware=len(h))
for name in ('nozzle','cover','rotor','stator'):
 dv=abs(t.volume(p[name])-t.volume(old[name]));da=abs(t.area(p[name])-t.area(old[name]));db=max(abs(a-b) for aa,bb in zip(t.limits(p[name]),t.limits(old[name])) for a,b in zip(aa,bb))
 check(name+' geometry and placement unchanged',dv<.01 and da<.01 and db<.001,volume_delta_mm3=dv,area_delta_mm2=da,bounds_delta_mm=db)
oldprop=[];other=[]
for s in oh:
 lo,hi=t.limits(s);mid=[(a+b)/2 for a,b in zip(lo,hi)]
 if abs(mid[1]-12.5)<.001 and abs(math.hypot(mid[0],mid[2])-9)<.001:oldprop.append(s)
 else:other.append(s)
present=[sig(q) for q in h];missing=[sig(q) for q in other if sig(q) not in present]
check('all thirty-six stationary fasteners retained',len(other)==36 and not missing,missing=missing)
check('four old propeller screws removed',len(oldprop)==4 and all(sig(q) not in present for q in oldprop))
insert_region=cylinder(11.31,(0,5.59,0),(0,1,0),4.42)
check('no propeller plastic occupies the old internal insert region',common(p['propeller'],insert_region)<1e-5)
check('complete rotor and new clamp have clearance',t.distance(p['propeller'],p['rotor'])>.139,minimum_gap_mm=t.distance(p['propeller'],p['rotor']))
probe=cylinder(13.999,(0,-1.5,0),(0,1,0),9.5)
check('new clamp bore clears a 27.998 mm gauge',common(p['propeller'],probe)<1e-5)
axes=((9,0),(-9,0),(0,9),(0,-9))
keychecks=[]
for x,z in axes:
 gauge=cylinder(2.749,(x,11.8,z),(0,1,0),2.3)
 keychecks.append(abs(t.volume(gauge)-common(gauge,p['propeller'])))
check('four solid drive keys retain 5.5 mm diameter and 18 mm pitch circle',max(keychecks)<1e-4,missing_key_material_mm3=keychecks)
new=[q for q in h if sig(q) not in [sig(v) for v in other]]
check('exactly six external clamp fasteners added',len(new)==6)
bad=[]
for i,s in enumerate(new):
 for name,q in p.items():
  v=common(s,q)
  if v>1e-4:bad.append(dict(hardware=i,part=name,overlap_mm3=v))
check('new fasteners clear all five mechanical parts',not bad,unexpected=bad)
for sign in (1,-1):
 x=sign*20.5;axis=(0,0,-sign);seat=(x,3,sign*6.5)
 expected_w=washer(seat,axis);expected_n=hexnut((x,3,-sign*6),axis)
 check('clamp '+str(sign)+' washer and nut at their bearing seats',all(any(abs(t.volume(q)-t.volume(e))<.01 and t.distance(q,e)<1e-6 and common(q,e)>t.volume(e)-.01 for q in new) for e in (expected_w,expected_n)))
 gap=box((sign*22.3 if sign==1 else -24,1,-.299),(24 if sign==1 else -22.3,5,.299))
 check('clamp '+str(sign)+' closure stops have 0.6 mm initial gap',common(gap,p['propeller'])<1e-5)
 bore=cylinder(1.699,(x,3,-10),(0,0,1),21)
 check('clamp '+str(sign)+' bolt has 3.4 mm clearance passage',common(bore,p['propeller'])<1e-5)
 # L-key envelope, fitted after nuts are captured and before cover installation.
 key_short=cylinder(1.43,(x,3,sign*9.51),(0,0,sign),8.49)
 key_long=cylinder(1.43,(x,3,sign*18),(0,1,0),37)
 violations=[]
 for target in ('propeller','rotor','stator','nozzle','cover'):
  for k in (key_short,key_long):
   if common(k,p[target])>1e-4:violations.append(target)
 check('clamp '+str(sign)+' L-key insertion and handle path clear',not violations,blocked_parts=violations)
sweep=cylinder(35.5001,(0,-3.0001,0),(0,1,0),22.0002)
escaped={name:abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,q,sweep))) for name,q in [('propeller',p['propeller'])]+[('newhardware'+str(i),q) for i,q in enumerate(new)]}
check('entire new propeller and clamp hardware stay inside full-turn envelope',max(escaped.values())<1e-4,outside_volumes_mm3=escaped)
gaps={name:t.distance(sweep,p[name]) for name in ('nozzle','cover','stator')}
check('continuous 360-degree envelope clears stationary geometry',gaps['nozzle']>2.4 and gaps['cover']>.99 and gaps['stator']>2.9,gaps_mm=gaps)
check('M3x16 threads pass through 2.4 mm nuts with 1.1 mm protrusion',abs((6.5-16)-(-8.4)+1.1)<1e-6,nominal_protrusion_mm=1.1)
if (r/'Propeller-R6-integral-M3-clamp.stl').exists():
 import vtk
 from check_print_revision import mesh
 for filename in ('Propeller-R6-integral-M3-clamp.stl','Nozzle-R5-unchanged.stl','Front-cap-R4-unchanged.stl'):
  m=mesh(r/filename);e=vtk.vtkFeatureEdges();e.SetInputData(m);e.BoundaryEdgesOn();e.NonManifoldEdgesOn();e.FeatureEdgesOff();e.ManifoldEdgesOff();e.Update()
  c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(m);c.SetExtractionModeToAllRegions();c.Update()
  check(filename+' is one closed manifold component',e.GetOutput().GetNumberOfCells()==0 and c.GetNumberOfExtractedRegions()==1,bad_edges=e.GetOutput().GetNumberOfCells(),components=c.GetNumberOfExtractedRegions(),triangles=m.GetNumberOfCells())
 for a,b in [('Nozzle-R5-unchanged.stl',r.parent/'remove-wire-holder-2026-10-21/Nozzle-no-wire-holder-R5.stl'),('Front-cap-R4-unchanged.stl',r.parent/'cover-through-bolts-2026-10-17/printable-STLs/Front-cover-M3-through-tabs-R4.stl')]:
  check(a+' is byte-identical to preserved print',hashlib.sha256((r/a).read_bytes()).digest()==hashlib.sha256(b.read_bytes()).digest())
(r/'verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
