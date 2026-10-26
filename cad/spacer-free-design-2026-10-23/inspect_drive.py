from pathlib import Path
import sys,json
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Plane
p,h=read(r.parent/'remove-wire-holder-2026-10-21/Thruster-no-wire-holder-R5.step')
for n in ('rotor','stator','cover','propeller','insert'):
 print(n,'bounds',t.limits(p[n]),'volume',t.volume(p[n]),flush=True)
 e=TopExp_Explorer(p[n],TopAbs_FACE)
 while e.More():
  face=TopoDS.Face(e.Current());surf=BRepAdaptor_Surface(face)
  if surf.GetType()==GeomAbs_Cylinder:
   c=surf.Cylinder();ax=c.Axis();o=ax.Location();d=ax.Direction()
   if abs(d.Y())>.999 and abs(o.X())<.01 and abs(o.Z())<.01:
    print('central cylinder',c.Radius(),'bounds',t.limits(face),flush=True)
  e.Next()
