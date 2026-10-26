from pathlib import Path
import sys,json,zipfile,shutil,hashlib
r=Path(__file__).resolve().parent
sys.path.insert(0,'C:/Users/ROG/OneDrive/Documents/ChatGPT/robotic FTC 2026-2027/cad/.vendor')
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
import vtk
from check_print_revision import mesh
out=r/'PRINT';out.mkdir(exist_ok=True)
for report in ('verification.json','print-and-closure-verification.json','tool-access-verification.json'):
 assert all(q['passed'] for q in json.loads((r/report).read_text())),report
reports=[]
for name,angle in [('Fan-R8-M3-axle-clamp.stl',90),('Upper-jaw-R8-M3-axle-clamp.stl',-90),('TEST-FIRST-R8-lower-jaw.stl',0)]:
 m=mesh(r/name);tr=vtk.vtkTransform();tr.RotateX(angle)
 f=vtk.vtkTransformPolyDataFilter();f.SetInputData(m);f.SetTransform(tr);f.Update()
 b=f.GetOutput().GetBounds();tr2=vtk.vtkTransform();tr2.Translate(-(b[0]+b[1])/2,-(b[2]+b[3])/2,-b[4])
 g=vtk.vtkTransformPolyDataFilter();g.SetInputConnection(f.GetOutputPort());g.SetTransform(tr2);g.Update()
 w=vtk.vtkSTLWriter();w.SetFileName(str(out/name));w.SetFileTypeToBinary();w.SetInputConnection(g.GetOutputPort());assert w.Write()
 m2=mesh(out/name);e=vtk.vtkFeatureEdges();e.SetInputData(m2);e.BoundaryEdgesOn();e.NonManifoldEdgesOn();e.FeatureEdgesOff();e.ManifoldEdgesOff();e.Update()
 c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(m2);c.SetExtractionModeToAllRegions();c.Update()
 assert e.GetOutput().GetNumberOfCells()==0 and c.GetNumberOfExtractedRegions()==1
 assert abs(m2.GetBounds()[4])<1e-4
 reports.append(dict(file=name,angle_x_deg=angle,print_bounds_mm=m2.GetBounds(),bad_edges=0,components=1))
for src,dst in [('Nozzle-R6p1-flat-motor-boss.stl','Frame-R6p1-UNCHANGED.stl'),('Front-cap-R4-unchanged.stl','Cap-R4-UNCHANGED.stl')]:
 source=r.parent/'flatter-motor-boss-2026-10-24'/src;shutil.copyfile(source,out/dst)
 reports.append(dict(file=dst,unchanged_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
(r/'print-orientation-verification.json').write_text(json.dumps(reports,indent=2))
target=r/'R8-M3-Axle-Clamp-Print-Kit.zip'
files=[r/'ASSEMBLY-AND-PRINT.txt',r/'Thruster-R8-M3-axle-clamp.step',r/'R8-clamp-detail.png',r/'R8-complete-assembly.png',r/'FINAL-REVIEW.txt',r/'verification.json',r/'print-and-closure-verification.json',r/'tool-access-verification.json',r/'print-orientation-verification.json']+list(out.glob('*.stl'))
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(r))
print('Packaged',target.name,'bytes',target.stat().st_size,'files',len(files),flush=True)
print(json.dumps(reports,indent=2))
