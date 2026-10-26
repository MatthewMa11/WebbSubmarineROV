from pathlib import Path
import sys,json,shutil,hashlib
r=Path(__file__).resolve().parent;v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py';n={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],n)
t=n['t'];cyl=n['cylinder'];ss=n['solids'](r/'Thruster-R13-concave-cap.step')
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
import vtk,numpy as np
from vtk.util.numpy_support import vtk_to_numpy
from check_print_revision import mesh

def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
cap=next(s for s in ss if span(s)[0]>90 and t.limits(s)[0][1]>46.9);house=next(s for s in ss if span(s)[0]>100 and t.limits(s)[0][1]<-29)
male=t.boolean(t.BRepAlgoAPI_Common,house,cyl(6,(0,39.5,44.5),(0,1,0),8.6))
female=t.boolean(t.BRepAlgoAPI_Common,cap,cyl(6,(0,46.9,44.5),(0,1,0),5.1))
for name,part in [('Joint-Housing-R13.stl',male),('Joint-Cone-R13.stl',female)]:
 BRepMesh_IncrementalMesh(part,.012,False,.1,True).Perform();w=StlAPI_Writer();w.ASCIIMode=False;assert w.Write(part,str(r/name))
native_volumes=json.loads((r/'native-volumes.json').read_text())
parts=[('Housing-R13-short-bolt.stl',house,''),('Cone-R13-concave.stl',cap,''),('Joint-Housing-R13.stl',male,'TEST-FIRST'),('Joint-Cone-R13.stl',female,'TEST-FIRST')]
out=r/'PRINT';out.mkdir(exist_ok=True);reports=[];cleaned={}
for name,part,folder in parts:
 p=mesh(r/name);con=vtk.vtkPolyDataConnectivityFilter();con.SetInputData(p);con.SetExtractionModeToAllRegions();con.Update();regions=[];blocks=[]
 for i in range(con.GetNumberOfExtractedRegions()):
  c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(p);c.SetExtractionModeToSpecifiedRegions();c.AddSpecifiedRegion(i);c.Update();f=vtk.vtkCleanPolyData();f.SetInputConnection(c.GetOutputPort());f.Update();q=vtk.vtkPolyData();q.DeepCopy(f.GetOutput());blocks.append(q);m=vtk.vtkMassProperties();m.SetInputData(q);m.Update();regions.append(dict(region=i,triangles=q.GetNumberOfCells(),volume_mm3=m.GetVolume(),bounds_mm=q.GetBounds()))
 big=max(range(len(regions)),key=lambda i:regions[i]['volume_mm3']);discard=[x for i,x in enumerate(regions) if i!=big]
 assert all(x['triangles']<=8 and x['volume_mm3']<1e-6 and max(x['bounds_mm'][k+1]-x['bounds_mm'][k] for k in [0,2,4])<.1 for x in discard),(name,discard)
 p=blocks[big];cleaned[name]=p
 tr=vtk.vtkTransform();tr.RotateX(90);f=vtk.vtkTransformPolyDataFilter();f.SetInputData(p);f.SetTransform(tr);f.Update();b=f.GetOutput().GetBounds();tr2=vtk.vtkTransform();tr2.Translate(-(b[0]+b[1])/2,-(b[2]+b[3])/2,-b[4]);g=vtk.vtkTransformPolyDataFilter();g.SetInputConnection(f.GetOutputPort());g.SetTransform(tr2);g.Update()
 dest=out/folder/name;dest.parent.mkdir(exist_ok=True);w=vtk.vtkSTLWriter();w.SetFileTypeToBinary();w.SetFileName(str(dest));w.SetInputConnection(g.GetOutputPort());assert w.Write()
 pm=mesh(dest);edge=vtk.vtkFeatureEdges();edge.SetInputData(pm);edge.BoundaryEdgesOn();edge.NonManifoldEdgesOn();edge.FeatureEdgesOff();edge.ManifoldEdgesOff();edge.Update();con=vtk.vtkPolyDataConnectivityFilter();con.SetInputData(pm);con.SetExtractionModeToAllRegions();con.Update();mass=vtk.vtkMassProperties();mass.SetInputData(pm);mass.Update();step_volume=abs(t.volume(part));basis=native_volumes['housing'] if name=='Housing-R13-short-bolt.stl' else (native_volumes['cone'] if name=='Cone-R13-concave.stl' else step_volume);err=abs(mass.GetVolume()-basis)/basis;bounds=pm.GetBounds()
 assert edge.GetOutput().GetNumberOfCells()==0 and con.GetNumberOfExtractedRegions()==1,(name,'mesh topology')
 assert err<.001 and abs(bounds[4])<1e-5 and max(bounds[k+1]-bounds[k] for k in [0,2,4])<256,(name,err,bounds)
 reports.append(dict(file=dest.relative_to(out).as_posix(),closed_manifold=True,components=1,triangles=pm.GetNumberOfCells(),print_bounds_mm=bounds,relative_volume_error=err,volume_comparison_basis=('native Onshape' if name in ['Housing-R13-short-bolt.stl','Cone-R13-concave.stl'] else 'local clipped CAD'),reference_volume_mm3=basis,step_reader_volume_mm3=step_volume,discarded_export_fragments=discard,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
for name in ['Fan-R11-actual-adapter.stl','TEST-FIRST-R11-5p1-bore.stl']:
 src=r.parent/'actual-onshape-motor-r11-2026-10-25/PRINT'/name;shutil.copyfile(src,out/name);assert src.read_bytes()==(out/name).read_bytes();reports.append(dict(file=name,unchanged=True,sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
# Independent retained-surface comparisons. The new bowl/bolt holes and front
# joint windows are excluded; external cone and remaining housing stay fixed.
def samples(p):
 pts=vtk_to_numpy(p.GetPoints().GetData()).astype(float);cells=vtk_to_numpy(p.GetPolys().GetConnectivityArray()).reshape(-1,3);return np.vstack([pts,pts[cells].mean(axis=1)])
def keep(pts,role):
 ds=np.min(np.stack([(pts[:,0]-x)**2+(pts[:,2]-z)**2 for x,z in [(0,44.5),(-44.5,0),(0,-44.5),(44.5,0)]]),axis=0)
 if role=='house':return ~((pts[:,1]>39.8)&(ds<6.2**2))
 rr=pts[:,0]**2+pts[:,2]**2
 return ~(((rr<13.8**2)&(pts[:,1]<56.2))|(rr<2.1**2)|((ds<3.8**2)&(pts[:,1]<48.2))|(ds<2.1**2))
oldhouse=mesh(r.parent/'one-piece-housing-r12-2026-10-25/Housing-R12-one-piece-clean.stl');oldcap=mesh(r.parent/'actual-onshape-motor-r11-2026-10-25/PRINT/OPTIONAL-unchanged-frame-cap/Cap-R4-UNCHANGED.stl');tr=vtk.vtkTransform();tr.Translate(0,28,0);f=vtk.vtkTransformPolyDataFilter();f.SetInputData(oldcap);f.SetTransform(tr);f.Update();oldcap=vtk.vtkPolyData();oldcap.DeepCopy(f.GetOutput())
fidelity=[]
for role,old,new in [('house',oldhouse,cleaned['Housing-R13-short-bolt.stl']),('cone',oldcap,cleaned['Cone-R13-concave.stl'])]:
 for label,a,b in [('old-to-new',old,new),('new-to-old',new,old)]:
  pts=samples(a);pts=pts[keep(pts,role)];loc=vtk.vtkImplicitPolyDataDistance();loc.SetInput(b);d=np.fromiter((abs(loc.EvaluateFunction(tuple(p))) for p in pts),float,count=len(pts));fidelity.append(dict(part=role,direction=label,samples=len(pts),max_distance_mm=float(d.max()),passed=bool(d.max()<.02)))
assert all(x['passed'] for x in fidelity),fidelity
report=dict(prints=reports,retained_surface_checks=fidelity,retained_surface_tolerance_mm=.02)
(r/'print-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
