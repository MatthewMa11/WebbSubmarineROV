from pathlib import Path
import sys,json,shutil,hashlib
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];cylinder=ns['cylinder']
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
coupon=t.boolean(t.BRepAlgoAPI_Cut,cylinder(11,(0,0,0),(0,0,1),6.5),cylinder(3.1,(0,0,-.01),(0,0,1),6.52))
mesher=BRepMesh_IncrementalMesh(coupon,.012,False,.1,True);mesher.Perform()
w=StlAPI_Writer();w.ASCIIMode=False;assert w.Write(coupon,str(r/'TEST-FIRST-R10-6p2-bore.stl'))
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
import vtk
from check_print_revision import mesh
ss=ns['solids'](r/'Thruster-R10-metal-collet.step')
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
fan=next(s for s in ss if span(s)[2]>70 and span(s)[0]<50)
extension=next(s for s in ss if span(s)[0]>90 and 18.9<t.limits(s)[0][1]<19.1 and 46.9<t.limits(s)[1][1]<47.1)
parts={'Fan-R10-metal-collet.stl':fan,'Duct-extension-R10-28mm.stl':extension,'TEST-FIRST-R10-6p2-bore.stl':coupon}
out=r/'PRINT';out.mkdir(exist_ok=True);reports=[]
for name,part in parts.items():
 m=mesh(r/name);angle=90 if name!='TEST-FIRST-R10-6p2-bore.stl' else 0
 tr=vtk.vtkTransform();tr.RotateX(angle)
 f=vtk.vtkTransformPolyDataFilter();f.SetInputData(m);f.SetTransform(tr);f.Update()
 b=f.GetOutput().GetBounds();tr2=vtk.vtkTransform();tr2.Translate(-(b[0]+b[1])/2,-(b[2]+b[3])/2,-b[4])
 g=vtk.vtkTransformPolyDataFilter();g.SetInputConnection(f.GetOutputPort());g.SetTransform(tr2);g.Update()
 writer=vtk.vtkSTLWriter();writer.SetFileTypeToBinary();writer.SetFileName(str(out/name));writer.SetInputConnection(g.GetOutputPort());assert writer.Write()
 pm=mesh(out/name);edges=vtk.vtkFeatureEdges();edges.SetInputData(pm);edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
 conn=vtk.vtkPolyDataConnectivityFilter();conn.SetInputData(pm);conn.SetExtractionModeToAllRegions();conn.Update()
 mass=vtk.vtkMassProperties();mass.SetInputData(pm);mass.Update();err=abs(mass.GetVolume()-abs(t.volume(part)))/abs(t.volume(part))
 assert edges.GetOutput().GetNumberOfCells()==0 and conn.GetNumberOfExtractedRegions()==1,(name,'mesh not closed or disconnected')
 assert err<.001,(name,err)
 bounds=pm.GetBounds();assert abs(bounds[4])<1e-4
 assert max(bounds[1]-bounds[0],bounds[3]-bounds[2],bounds[5]-bounds[4])<256
 reports.append(dict(file=name,closed_manifold=True,components=1,triangles=pm.GetNumberOfCells(),stl_step_volume_relative_error=err,print_bounds_mm=bounds,orientation_x_deg=angle,sha256=hashlib.sha256((out/name).read_bytes()).hexdigest()))
optional=out/'OPTIONAL-unchanged-frame-cap';optional.mkdir(exist_ok=True)
for src,dst in [('Nozzle-R6p1-flat-motor-boss.stl','Frame-R6p1-UNCHANGED.stl'),('Front-cap-R4-unchanged.stl','Cap-R4-UNCHANGED.stl')]:
 source=r.parent/'flatter-motor-boss-2026-10-24'/src;shutil.copyfile(source,optional/dst)
 assert source.read_bytes()==(optional/dst).read_bytes()
 reports.append(dict(file=str((optional/dst).relative_to(out)),unchanged_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
(r/'print-verification.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2))
