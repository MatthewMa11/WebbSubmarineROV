from pathlib import Path
import sys,json,hashlib,shutil
sys.path.insert(0,'C:/Users/ROG/OneDrive/Documents/ChatGPT/robotic FTC 2026-2027/cad/.vendor')
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'print-revision-2026-10-17'))
import vtk,numpy as np
from vtk.util.numpy_support import vtk_to_numpy
from check_print_revision import mesh
r=Path(__file__).resolve().parent;p=mesh(r/'Housing-R12-one-piece.stl')
conn=vtk.vtkPolyDataConnectivityFilter();conn.SetInputData(p);conn.SetExtractionModeToAllRegions();conn.Update();count=conn.GetNumberOfExtractedRegions()
regions=[];parts=[]
for i in range(count):
 c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(p);c.SetExtractionModeToSpecifiedRegions();c.AddSpecifiedRegion(i);c.Update()
 clean=vtk.vtkCleanPolyData();clean.SetInputConnection(c.GetOutputPort());clean.Update();q=vtk.vtkPolyData();q.DeepCopy(clean.GetOutput());parts.append(q)
 m=vtk.vtkMassProperties();m.SetInputData(q);m.Update();regions.append(dict(region=i,cells=q.GetNumberOfCells(),bounds_mm=q.GetBounds(),volume_mm3=m.GetVolume()))
big=max(range(count),key=lambda i:regions[i]['volume_mm3']);discard=[d for i,d in enumerate(regions) if i!=big]
assert all(d['cells']<=8 and d['volume_mm3']<1e-6 and max(d['bounds_mm'][k+1]-d['bounds_mm'][k] for k in [0,2,4])<.1 for d in discard),discard
house=parts[big]
# Keep the exact native surface triangles of the functional housing. Only two
# sub-nozzle export tetrahedra (total3.1e-8mm3) are excluded; no resampling.
w=vtk.vtkSTLWriter();w.SetFileTypeToBinary();w.SetFileName(str(r/'Housing-R12-one-piece-clean.stl'));w.SetInputData(house);assert w.Write()
# Rear face down. Rotation maps CAD's +Y axis to build +Z, translation rests on bed.
tr=vtk.vtkTransform();tr.RotateX(90);f=vtk.vtkTransformPolyDataFilter();f.SetInputData(house);f.SetTransform(tr);f.Update();b=f.GetOutput().GetBounds()
tr2=vtk.vtkTransform();tr2.Translate(-(b[0]+b[1])/2,-(b[2]+b[3])/2,-b[4]);g=vtk.vtkTransformPolyDataFilter();g.SetInputConnection(f.GetOutputPort());g.SetTransform(tr2);g.Update()
out=r/'PRINT';out.mkdir(exist_ok=True);w.SetFileName(str(out/'Housing-R12-one-piece.stl'));w.SetInputConnection(g.GetOutputPort());assert w.Write()
q=mesh(out/'Housing-R12-one-piece.stl');edge=vtk.vtkFeatureEdges();edge.SetInputData(q);edge.BoundaryEdgesOn();edge.NonManifoldEdgesOn();edge.FeatureEdgesOff();edge.ManifoldEdgesOff();edge.Update()
c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(q);c.SetExtractionModeToAllRegions();c.Update();bounds=q.GetBounds()
assert edge.GetOutput().GetNumberOfCells()==0 and c.GetNumberOfExtractedRegions()==1
assert abs(bounds[4])<1e-5 and max(bounds[k+1]-bounds[k] for k in [0,2,4])<256
checks=dict(closed_manifold=True,components=1,triangles=q.GetNumberOfCells(),print_bounds_mm=bounds,discarded_export_fragments=discard,removed_volume_mm3=sum(d['volume_mm3'] for d in discard),sha256=hashlib.sha256((out/'Housing-R12-one-piece.stl').read_bytes()).hexdigest())
# Reuse the exact already verified prints for the unaffected rotating hub and cap.
refs=r.parent/'actual-onshape-motor-r11-2026-10-25/PRINT';preserved=[]
for src,dst in [('Fan-R11-actual-adapter.stl','Fan-R11-actual-adapter.stl'),('TEST-FIRST-R11-5p1-bore.stl','TEST-FIRST-R11-5p1-bore.stl'),('OPTIONAL-unchanged-frame-cap/Cap-R4-UNCHANGED.stl','Cap-R4-UNCHANGED.stl')]:
 shutil.copyfile(refs/src,out/dst);assert (refs/src).read_bytes()==(out/dst).read_bytes();preserved.append(dict(file=dst,sha256=hashlib.sha256((out/dst).read_bytes()).hexdigest()))
# Source material must remain inside the union. This surface classifier avoids
# inherited STEP tolerance faults in the legacy imported frame/cap B-reps.
normal=vtk.vtkPolyDataNormals();normal.SetInputData(house);normal.ConsistencyOn();normal.AutoOrientNormalsOn();normal.SplittingOff();normal.Update()
locator=vtk.vtkImplicitPolyDataDistance();locator.SetInput(normal.GetOutput());retained=[]
for file in [r.parent/'flatter-motor-boss-2026-10-24/Nozzle-R6p1-flat-motor-boss.stl',r.parent/'metal-collet-r10-2026-10-25/Duct-extension-R10-28mm.stl']:
 old=mesh(file);pts=vtk_to_numpy(old.GetPoints().GetData()).astype(float)
 cells=vtk_to_numpy(old.GetPolys().GetConnectivityArray()).reshape(-1,3);centers=pts[cells].mean(axis=1);samples=np.vstack([pts,centers])
 d=np.fromiter((locator.EvaluateFunction(tuple(p)) for p in samples),float,count=len(samples))
 outside_joint=(samples[:,1]<17.9)|(samples[:,1]>28.1)
 retained.append(dict(source=file.name,samples=len(samples),checked_outside_joint_samples=int(outside_joint.sum()),modified_joint_y_mm=[17.9,28.1],whole_source_max_outside_mm=float(d.max()),max_outside_joint_mm=float(d[outside_joint].max()),percentile99_outside_joint_mm=float(np.percentile(d[outside_joint],99)),passed=bool(d[outside_joint].max()<.02)))
assert all(x['passed'] for x in retained),retained
report=dict(housing=checks,unchanged_prints=preserved,retained_source_surfaces=retained,source_surface_tolerance_mm=.02)
(r/'print-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
