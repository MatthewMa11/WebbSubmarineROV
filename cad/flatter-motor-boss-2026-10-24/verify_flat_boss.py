"""Verify the flatter nozzle against the exact preceding R6 assembly export."""
from pathlib import Path
import sys,json,math
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import t,cylinder
from verify_kit_hardware import solids
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane,GeomAbs_Torus
def read(path):
 p={};h=[]
 for s in solids(path):
  lo,hi=t.limits(s);dx,dy,dz=[b-a for a,b in zip(lo,hi)]
  if lo[1]<-30 and dx>90:n='nozzle'
  elif dz>70 and dx<60:n='propeller'
  elif dx>80 and lo[1]>10:n='cover'
  elif 27<dx<29 and dy>25:n='rotor'
  elif 27<dx<29 and dy<6:n='stator'
  else:h.append(s);continue
  assert n not in p;p[n]=s
 return p,h
p,h=read(r/'Thruster-R6p1-flat-motor-boss.step')
old,oh=read(r.parent/'spacer-free-design-2026-10-23/Thruster-R6-spacer-free-assembly.step')
checks=[]
def check(name,passed,**detail):
 checks.append(dict(check=name,passed=bool(passed),detail=detail));print(('PASS ' if passed else 'FAIL ')+name,flush=True)
def common(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
check('five mechanical bodies and all forty-two fasteners retained',len(p)==5 and len(h)==42)
for name in ('propeller','rotor','stator','cover'):
 dv=abs(t.volume(p[name])-t.volume(old[name]));da=abs(t.area(p[name])-t.area(old[name]));db=max(abs(a-b) for aa,bb in zip(t.limits(p[name]),t.limits(old[name])) for a,b in zip(aa,bb))
 check(name+' geometry and placement unchanged',dv<.01 and da<.01 and db<.001,volume_delta_mm3=dv,area_delta_mm2=da,bounds_delta_mm=db)
def signature(ss):return sorted(tuple(round(v,4) for pair in t.limits(s) for v in pair)+(round(t.volume(s),3),round(t.area(s),3)) for s in ss)
check('all forty-two fastener shapes and locations unchanged',signature(h)==signature(oh))
region=cylinder(21.01,(0,-60.01,0),(0,1,0),31.12)
a=t.boolean(t.BRepAlgoAPI_Cut,p['nozzle'],region);b=t.boolean(t.BRepAlgoAPI_Cut,old['nozzle'],region)
dv=abs(t.volume(a)-t.volume(b));da=abs(t.area(a)-t.area(b))
check('nozzle outside the local rear-tip relief is unchanged',dv<.01 and da<.02,volume_delta_mm3=dv,area_delta_mm2=da)
central=cylinder(15.51,(0,-60,0),(0,1,0),38)
newtip=t.boolean(t.BRepAlgoAPI_Common,p['nozzle'],central);oldtip=t.boolean(t.BRepAlgoAPI_Common,old['nozzle'],central)
lo,hi=t.limits(newtip);oldlo,_=t.limits(oldtip)
check('rear projection shortened by approximately twelve millimetres',abs(lo[1]+30)<.01 and 11.9<lo[1]-oldlo[1]<12.2,old_tip_Y_mm=oldlo[1],new_tip_Y_mm=lo[1],reduction_mm=lo[1]-oldlo[1])
planes=[];rounds=[];e=TopExp_Explorer(p['nozzle'],TopAbs_FACE)
while e.More():
 f=TopoDS.Face(e.Current());sf=BRepAdaptor_Surface(f);aa,bb=t.limits(f)
 if sf.GetType()==GeomAbs_Plane and abs(aa[1]+30)<.01 and abs(bb[1]+30)<.01:planes.append(t.area(f))
 if sf.GetType()==GeomAbs_Torus:
  tor=sf.Torus()
  # Add_s bounds include the torus control net. Use its exact analytic center.
  if abs(tor.MinorRadius()-1)<1e-5 and abs(tor.MajorRadius()-14.5)<1e-5 and abs(tor.Location().Y()+29)<1e-5:rounds.append(t.area(f))
 e.Next()
check('broad flat rear face replaces the rounded dome',len(planes)==1 and planes[0]>400,flat_face_area_mm2=planes)
check('one millimetre external rim fillet is present',len(rounds)>0,round_face_count=len(rounds))
axes=((9.5,0),(-9.5,0),(0,8),(0,-8))
blocks=[]
for x,z in axes:blocks.append(common(p['nozzle'],cylinder(3.79,(x,-30.01,z),(0,1,0),13.8)))
check('all four 7.6 mm motor screw access passages remain open',max(blocks)<1e-4,blocked_gauge_volumes_mm3=blocks)
retained=cylinder(20.01,(0,-20.01,0),(0,1,0),14)
a=t.boolean(t.BRepAlgoAPI_Common,p['nozzle'],retained);b=t.boolean(t.BRepAlgoAPI_Common,old['nozzle'],retained)
dv=abs(t.volume(a)-t.volume(b));da=abs(t.area(a)-t.area(b))
check('motor seats, structural floor and centering cup remain unchanged',dv<.01 and da<.02,volume_delta_mm3=dv,area_delta_mm2=da)
behind=cylinder(1,(0,-29.99,0),(0,1,0),6.9)
check('at least seven millimetres of central rear cap thickness retained',common(p['nozzle'],behind)>t.volume(behind)-1e-4)
bad=[]
for i,s in enumerate(h):
 v=common(s,p['nozzle'])
 if v>1e-4:bad.append(dict(fastener=i,overlap_mm3=v))
check('existing fasteners do not penetrate the revised nozzle',not bad,unexpected=bad)
sweep=cylinder(35.5001,(0,-3.0001,0),(0,1,0),22.0002)
gaps={n:t.distance(sweep,p[n]) for n in ('nozzle','cover','stator')}
check('continuous propeller rotation envelope retains its clearance',gaps['nozzle']>2.4 and gaps['cover']>.99 and gaps['stator']>2.9,gaps_mm=gaps)
check('stationary nozzle clears motor rotor and propeller',max(common(p['nozzle'],p[n]) for n in ('rotor','propeller'))<1e-4)
if (r/'Nozzle-R6p1-flat-motor-boss.stl').exists():
 import vtk
 from check_print_revision import mesh
 m=mesh(r/'Nozzle-R6p1-flat-motor-boss.stl');edges=vtk.vtkFeatureEdges();edges.SetInputData(m);edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
 c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(m);c.SetExtractionModeToAllRegions();c.Update()
 check('revised nozzle STL is one closed manifold body',edges.GetOutput().GetNumberOfCells()==0 and c.GetNumberOfExtractedRegions()==1,bad_edges=edges.GetOutput().GetNumberOfCells(),components=c.GetNumberOfExtractedRegions(),triangles=m.GetNumberOfCells())
(r/'verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
