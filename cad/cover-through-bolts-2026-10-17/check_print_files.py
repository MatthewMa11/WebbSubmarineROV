from pathlib import Path
import sys,json,math
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from check_print_revision import mesh,occupied,points
import vtk,numpy as np
folder=Path(sys.argv[1]);checks=[]
def check(n,ok,**d):checks.append(dict(check=n,passed=bool(ok),detail=d));print(('PASS ' if ok else 'FAIL ')+n,flush=True)
parts={}
for k in ('nozzle','cover','propeller','insert'):
 files=[q for q in folder.glob('*.stl') if k in q.name.lower()];assert len(files)==1;parts[k]=mesh(files[0])
 forpart=parts[k]
 e=vtk.vtkFeatureEdges();e.SetInputData(forpart);e.BoundaryEdgesOn();e.NonManifoldEdgesOn();e.FeatureEdgesOff();e.ManifoldEdgesOff();e.Update()
 c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(forpart);c.SetExtractionModeToAllRegions();c.Update()
 check(k+' STL is one closed manifold body',e.GetOutput().GetNumberOfCells()==0 and c.GetNumberOfExtractedRegions()==1,triangles=forpart.GetNumberOfCells(),bad_edges=e.GetOutput().GetNumberOfCells(),components=c.GetNumberOfExtractedRegions())
bore=[];bearing=[];contacts=[]
for i in range(4):
 a=i*math.pi/2;d=(math.sin(-a),math.cos(-a));u=(d[1],-d[0])
 def pt(y,rad=44.5,tan=0):return (d[0]*rad+u[0]*tan,y,d[1]*rad+u[1]*tan)
 for y in np.linspace(12.4,24.6,123):
  for off in (0,1.4,-1.4):bore.append(pt(y,44.5,off))
 for j in range(32):
  b=j*math.pi/16;rad=44.5+2.8*math.cos(b);tan=2.8*math.sin(b)
  bearing.append((pt(16.02,rad,tan),pt(23.98,rad,tan)))
  rad=44.5+3.8*math.cos(b);tan=3.8*math.sin(b)
  contacts.append((pt(18.98,rad,tan),pt(19.02,rad,tan)))
free={k:sum(occupied(parts[k],bore)) for k in ('nozzle','cover')}
check('four M3 paths are open through both exported meshes',not any(free.values()),blocked_probes=free,probes_per_part=len(bore))
b1=occupied(parts['nozzle'],[a for a,b in bearing]);b2=occupied(parts['cover'],[b for a,b in bearing])
check('front and rear flat washer seats survive STL export',all(b1+b2),solid_probes=sum(b1+b2),expected=len(b1+b2))
c1=occupied(parts['nozzle'],[a for a,b in contacts]);c2=occupied(parts['cover'],[b for a,b in contacts])
check('four mating clamping lands survive STL export',all(c1+c2),solid_probes=sum(c1+c2),expected=len(c1+c2))
tip=np.linalg.norm(points(parts['propeller'])[:,[0,2]],axis=1).max();insert=np.linalg.norm(points(parts['insert'])[:,[0,2]],axis=1).max()
check('protected rotating print dimensions are retained',tip<=35.501 and insert<=11.301,blade_sweep_mm=float(tip*2),insert_envelope_mm=float(insert*2))
window=[]
for j in range(720):
 a=j*math.pi/360
 for rad in (16,20,24,27.4):window.append((rad*math.cos(a),-26,rad*math.sin(a)))
check('rear wire route remains open at every angle',not any(occupied(parts['nozzle'],window)))
Path(sys.argv[2]).write_text(json.dumps(checks,indent=2),encoding='utf-8')
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
