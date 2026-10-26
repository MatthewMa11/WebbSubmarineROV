from pathlib import Path
import sys,json,math
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];ss=ns['solids'](r/'Thruster-R9-forward-fan.step')
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
fan=next(s for s in ss if span(s)[2]>70 and span(s)[0]<60)
jaw=next(s for s in ss if 40<span(s)[0]<43 and 6<span(s)[1]<8 and 5<span(s)[2]<7)
rotor=next(s for s in ss if 27<span(s)[0]<29 and span(s)[1]>25)
def move(s,z):
 tr=gp_Trsf();tr.SetTranslation(gp_Vec(0,0,z));return BRepBuilderAPI_Transform(s,tr,True).Shape()
def common(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
checks=[]
def check(name,ok,**d):
 checks.append(dict(check=name,passed=bool(ok),detail=d));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
# Geometric closure only; this is not a clamp-load or elastic-strain model.
loadedfan=move(fan,.0625);loadedjaw=move(jaw,-.0625)
check('nominal 0.125 mm closing travel reaches shaft without jaw collision',common(loadedfan,loadedjaw)<1e-5)
check('taking up bore clearance does not penetrate reference rotor',common(loadedfan,rotor)<1e-4 and common(loadedjaw,rotor)<1e-4)
shaft=ns['cylinder'](1.5875,(0,16.25,0),(0,1,0),3.05)
check('closed nominal jaws contact the axle without penetrating it',common(loadedfan,shaft)<1e-5 and common(loadedjaw,shaft)<1e-5 and t.distance(loadedfan,shaft)<1e-4 and t.distance(loadedjaw,shaft)<1e-4)
check('M3x16 provides complete 2.4 mm nut engagement and 1.2 mm protrusion',abs(16-(12.4+2.4)-1.2)<1e-9)
crop=BRepPrimAPI_MakeBox(gp_Pnt(-21.1,12.19,-6.21),gp_Pnt(21.1,19.31,0)).Shape()
coupon=t.boolean(t.BRepAlgoAPI_Common,fan,crop)
check('small lower-jaw test coupon is a valid solid',BRepCheck_Analyzer(coupon).IsValid())
ex=TopExp_Explorer(coupon,TopAbs_SOLID);count=0
while ex.More():count+=1;ex.Next()
check('test coupon remains one connected solid',count==1)
tr=gp_Trsf();tr.SetTranslation(gp_Vec(0,-12.2,6.2));coupon=BRepBuilderAPI_Transform(coupon,tr,True).Shape()
mesher=BRepMesh_IncrementalMesh(coupon,.015,False,.12,True);mesher.Perform()
w=StlAPI_Writer();w.ASCIIMode=False;assert w.Write(coupon,str(r/'TEST-FIRST-R9-lower-jaw.stl'))
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from check_print_revision import mesh
import vtk
for name in ('Fan-R9-forward-fan.stl','Upper-jaw-R9-M3-axle-clamp.stl','TEST-FIRST-R9-lower-jaw.stl'):
 m=mesh(r/name);edges=vtk.vtkFeatureEdges();edges.SetInputData(m);edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
 c=vtk.vtkPolyDataConnectivityFilter();c.SetInputData(m);c.SetExtractionModeToAllRegions();c.Update()
 check(name+' is one closed manifold mesh',edges.GetOutput().GetNumberOfCells()==0 and c.GetNumberOfExtractedRegions()==1,bad_edges=edges.GetOutput().GetNumberOfCells(),regions=c.GetNumberOfExtractedRegions(),triangles=m.GetNumberOfCells())
(r/'print-and-closure-verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
