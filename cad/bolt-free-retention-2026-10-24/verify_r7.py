"""Independent geometry checks on the original native R7 STEP export."""
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
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
def exact_limits(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b,False,False)
 return [[p.X(),p.Y(),p.Z()] for p in (b.CornerMin(),b.CornerMax())]
t.limits=exact_limits
def read(path):
 p={};rings=[];h=[]
 for s in solids(path):
  lo,hi=t.limits(s);dx,dy,dz=[b-a for a,b in zip(lo,hi)]
  if lo[1]<-30 and dx>90:n='nozzle'
  elif dz>70 and dx<60:n='propeller'
  elif dx>80 and lo[1]>10:n='cover'
  elif 27<dx<29 and dy>25:n='rotor'
  elif 27<dx<29 and dy<6:n='stator'
  elif 39<dx<47 and 39<dz<47 and 2<dy<8 and -8<lo[1]<0 and hi[1]<5:rings.append(s);continue
  else:h.append(s);continue
  assert n not in p;p[n]=s
 return p,sorted(rings,key=lambda q:t.limits(q)[0][1]),h
p,rings,h=read(r/'Thruster-R7-bolt-free.step')
old,_,oh=read(r.parent/'flatter-motor-boss-2026-10-24/Thruster-R6p1-flat-motor-boss.step')
checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def common(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
def sig(q):return tuple(round(v,4) for pair in t.limits(q) for v in pair)+(round(t.volume(q),3),round(t.area(q),3))
check('seven mechanical parts and thirty-six metal fasteners',len(p)==5 and len(rings)==2 and len(h)==36)
assert len(p)==5 and len(rings)==2,'Missing R7 parts'
def invalid_face_bounds(q):
 a=BRepCheck_Analyzer(q);e=TopExp_Explorer(q,TopAbs_FACE);out=[]
 while e.More():
  f=e.Current()
  if not a.IsValid(f):out.append(tuple(round(v,5) for pair in t.limits(f) for v in pair))
  e.Next()
 return sorted(out)
new_invalid_faces=[b for b in invalid_face_bounds(p['propeller']) if b[1]<8.6]
check('all edited sleeve faces and both complete rings pass B-rep validity checks',not new_invalid_faces and all(BRepCheck_Analyzer(q).IsValid() for q in rings),invalid_edited_faces=new_invalid_faces)
check('no new invalid exported faces; two inherited blade-tip STEP slivers match baseline',invalid_face_bounds(p['propeller'])==invalid_face_bounds(old['propeller']) and len(invalid_face_bounds(p['propeller']))==2,inherited_faces=invalid_face_bounds(p['propeller']))
for name in ('nozzle','cover','rotor','stator'):
 dv=abs(t.volume(p[name])-t.volume(old[name]));da=abs(t.area(p[name])-t.area(old[name]));db=max(abs(a-b) for aa,bb in zip(t.limits(p[name]),t.limits(old[name])) for a,b in zip(aa,bb))
 check(name+' geometry and placement unchanged from flat-boss R6.1',dv<.01 and da<.01 and db<.001,volume_delta_mm3=dv,area_delta_mm2=da,bounds_delta_mm=db)
check('all thirty-six stationary fasteners retain their original geometry and poses',all(sig(q) in [sig(v) for v in oh] for q in h) and len(set(sig(q) for q in h))==36)
keys=[];ex=TopExp_Explorer(p['propeller'],TopAbs_FACE)
while ex.More():
 f=TopoDS.Face(ex.Current());sf=BRepAdaptor_Surface(f)
 if sf.GetType()==GeomAbs_Cylinder:
  c=sf.Cylinder();a=c.Axis();o=a.Location()
  if abs(c.Radius()-2.75)<1e-5 and abs(a.Direction().Y())>.9999:keys.append((round(o.X(),5),round(o.Z(),5)))
 ex.Next()
check('four 5.5 mm drive keys retain the exact 18 mm motor pattern',sorted(set(keys))==[(-9.,0.),(0.,-9.),(0.,9.),(9.,0.)],key_axes_mm=sorted(set(keys)))
empty=cylinder(11.31,(0,5.59,0),(0,1,0),4.42)
block=sum(common(q,empty) for q in [p['propeller']]+rings)
check('no printed part enters the former internal motor-spacer region',block<1e-5,obstruction_mm3=block)
check('no propeller ears remain beyond the 43 mm central sleeve envelope',t.limits(p['propeller'])[1][0]-t.limits(p['propeller'])[0][0]<43)
for i,q in enumerate(rings):
 v=common(q,p['propeller']);gap=t.distance(q,p['propeller'])
 check('ring '+str(i)+' thread clears the unloaded sleeve',v<1e-4,overlap_mm3=v,minimum_gap_mm=gap)
 for target in ('rotor','stator','nozzle','cover'):
  v=common(q,p[target]);gap=t.distance(q,p[target])
  check('ring '+str(i)+' clears '+target,v<1e-4 and gap>.35,overlap_mm3=v,gap_mm=gap)
v=common(rings[0],rings[1]);check('collar and jam ring meet without penetrating',v<1e-4 and t.distance(*rings)<1e-4,overlap_mm3=v)
check('rotating propeller does not penetrate the motor or stationary frame',max(common(p['propeller'],p[n]) for n in ('rotor','stator','nozzle','cover'))<1e-4)
sweep=cylinder(35.5001,(0,-5.5001,0),(0,1,0),24.5002)
escaped={n:abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,q,sweep))) for n,q in [('propeller',p['propeller']),('jam',rings[0]),('collar',rings[1])]}
check('full-turn envelope contains fan and both printed rings',max(escaped.values())<1e-4,escaped_volumes_mm3=escaped)
gaps={n:t.distance(sweep,p[n]) for n in ('nozzle','cover','stator')}
check('continuous 360-degree envelope clears all stationary mechanical parts',gaps['nozzle']>.70 and gaps['cover']>.99 and gaps['stator']>.45,gaps_mm=gaps)
region=cylinder(27.01,(0,-6.2,0),(0,1,0),16.9)
a=t.boolean(t.BRepAlgoAPI_Cut,p['propeller'],region);b=t.boolean(t.BRepAlgoAPI_Cut,old['propeller'],region)
dv=abs(t.volume(a)-t.volume(b));da=abs(t.area(a)-t.area(b))
check('blade tips and front motor-coupling geometry outside the sleeve revision are unchanged',dv<.01 and da<.02,volume_delta_mm3=dv,area_delta_mm2=da)
if (r/'Propeller-R7-bolt-free.stl').exists():
 import vtk
 from check_print_revision import mesh
 for name in ('Propeller-R7-bolt-free.stl','Compression-collar-R7.stl','Jam-ring-R7.stl'):
  m=mesh(r/name);e=vtk.vtkFeatureEdges();e.SetInputData(m);e.BoundaryEdgesOn();e.NonManifoldEdgesOn();e.FeatureEdgesOff();e.ManifoldEdgesOff();e.Update();c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(m);c.SetExtractionModeToAllRegions();c.Update()
  check(name+' is one closed manifold body',e.GetOutput().GetNumberOfCells()==0 and c.GetNumberOfExtractedRegions()==1,bad_edges=e.GetOutput().GetNumberOfCells(),components=c.GetNumberOfExtractedRegions(),triangles=m.GetNumberOfCells())
(r/'verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
