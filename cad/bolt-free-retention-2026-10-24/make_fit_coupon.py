from pathlib import Path
f=Path(__file__).resolve().parent/'verify_r7.py'
exec(f.read_text().split("p,rings,h=read(")[0])
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Ax1,gp_Dir,gp_Pnt,gp_Vec
p,rr,h=read(r/'Thruster-R7-bolt-free.step')
crop=cylinder(21.05,(0,-5.41,0),(0,1,0),9.72)
s=t.boolean(t.BRepAlgoAPI_Common,p['propeller'],crop)
print('cropped native sleeve valid',BRepCheck_Analyzer(s).IsValid(),flush=True)
top=t.boolean(t.BRepAlgoAPI_Cut,cylinder(20.1,(0,4.1,0),(0,1,0),1.5),cylinder(14,(0,4.09,0),(0,1,0),1.52))
s=t.boolean(BRepAlgoAPI_Fuse,s,top)
if not BRepCheck_Analyzer(s).IsValid():
 e=TopExp_Explorer(s,TopAbs_FACE);aa=BRepCheck_Analyzer(s)
 while e.More():
  if not aa.IsValid(e.Current()):print('invalid coupon face',t.limits(e.Current()),flush=True)
  e.Next()
assert BRepCheck_Analyzer(s).IsValid(),'Coupon B-rep invalid'
tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(1,0,0)),-math.pi/2)
s=BRepBuilderAPI_Transform(s,tr,True).Shape()
zmin=t.limits(s)[0][2];tr=gp_Trsf();tr.SetTranslation(gp_Vec(0,0,-zmin));s=BRepBuilderAPI_Transform(s,tr,True).Shape()
m=BRepMesh_IncrementalMesh(s,.02,False,.12,True);m.Perform()
w=StlAPI_Writer();w.ASCIIMode=False;assert w.Write(s,str(r/'TEST-FIRST-external-sleeve-R7.stl'))
print('Coupon valid; exact native thread, no blades or internal spacer; Z-up, base Z=0',flush=True)
