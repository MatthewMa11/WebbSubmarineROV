"""Check the native R5 assembly and exported mesh against the R4 baseline."""
from pathlib import Path
import sys,json,math
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t,cylinder
from check_print_revision import mesh,occupied
import vtk
p,h=read(r/'Thruster-no-wire-holder-R5.step')
old,oh=read(r.parent/'cover-through-bolts-2026-10-17/Thruster-cover-through-bolts-R4-verified.step')
checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
check('native assembly keeps six mechanical bodies and forty fasteners',len(h)==40)
for n in ('cover','propeller','insert','rotor','stator'):
 dv=abs(t.volume(p[n])-t.volume(old[n]));da=abs(t.area(p[n])-t.area(old[n]));db=max(abs(a-b) for aa,bb in zip(t.limits(p[n]),t.limits(old[n])) for a,b in zip(aa,bb))
 check(n+' geometry and position unchanged',dv<.01 and da<.01 and db<.001,volume_delta_mm3=dv,area_delta_mm2=da,bounds_delta_mm=db)
def signature(hh):return sorted(tuple(round(v,5) for pair in t.limits(q) for v in pair)+(round(t.volume(q),4),round(t.area(q),4)) for q in hh)
check('all forty hardware geometries and positions unchanged',signature(h)==signature(oh))
reduction=t.volume(old['nozzle'])-t.volume(p['nozzle'])
check('wire holder material removed from the nozzle',reduction>1000,removed_material_mm3=reduction)
ring=t.boolean(t.BRepAlgoAPI_Cut,cylinder(33.01,(0,-29.01,0),(0,1,0),6.02),cylinder(27.99,(0,-29.02,0),(0,1,0),6.04))
regions=[ring]
for x,z in ((30.5,0),(-30.5,0),(0,30.5),(0,-30.5)):
 regions.append(cylinder(2.51,(x,-26.01,z),(0,1,0),12.02))
a=p['nozzle'];b=old['nozzle']
for region in regions:
 a=t.boolean(t.BRepAlgoAPI_Cut,a,region);b=t.boolean(t.BRepAlgoAPI_Cut,b,region)
dv=abs(t.volume(a)-t.volume(b));da=abs(t.area(a)-t.area(b))
check('nozzle outside the holder ring and added posts is unchanged',dv<.01 and da<.02,volume_delta_mm3=dv,area_delta_mm2=da)
sweep=cylinder(35.5001,(0,-3.0001,0),(0,1,0),22.0002)
gaps={n:t.distance(sweep,p[n]) for n in ('nozzle','cover','stator')}
check('continuous propeller rotation envelope retains clearance',gaps['nozzle']>2.4 and gaps['cover']>.99 and gaps['stator']>2.9,gaps_mm=gaps)
nozzle=mesh(r/'Nozzle-no-wire-holder-R5.stl')
edges=vtk.vtkFeatureEdges();edges.SetInputData(nozzle);edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
connect=vtk.vtkPolyDataConnectivityFilter();connect.SetInputData(nozzle);connect.SetExtractionModeToAllRegions();connect.Update()
check('nozzle STL is one closed manifold body',edges.GetOutput().GetNumberOfCells()==0 and connect.GetNumberOfExtractedRegions()==1,bad_edges=edges.GetOutput().GetNumberOfCells(),components=connect.GetNumberOfExtractedRegions(),triangles=nozzle.GetNumberOfCells())
probes=[]
for i in range(720):
 angle=2*math.pi*i/720
 for radius in (28.5,30.5,32.5):
  for y in (-28,-26,-24):probes.append((radius*math.cos(angle),y,radius*math.sin(angle)))
blocked=sum(occupied(nozzle,probes))
check('rear wire-holder ring is absent through every angle',blocked==0,obstructed_probes=blocked,probe_count=len(probes))
(r/'verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
