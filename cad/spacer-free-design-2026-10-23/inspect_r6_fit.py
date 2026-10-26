from pathlib import Path
import sys
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t,cylinder
from verify_kit_hardware import solids
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
ss=solids(r/'Thruster-R6-spacer-free-assembly.step')
prop=next(s for s in ss if t.limits(s)[1][2]-t.limits(s)[0][2]>70 and t.limits(s)[1][0]-t.limits(s)[0][0]<60)
rotor=next(s for s in ss if 27<t.limits(s)[1][0]-t.limits(s)[0][0]<29 and t.limits(s)[1][1]-t.limits(s)[0][1]>25)
d=BRepExtrema_DistShapeShape(prop,rotor);d.Perform()
for i in range(1,d.NbSolution()+1):
 a=d.PointOnShape1(i);b=d.PointOnShape2(i);print('nearest',d.Value(),(a.X(),a.Y(),a.Z()),(b.X(),b.Y(),b.Z()))
for y in (11.51,11.7,11.9):
 q=cylinder(2.849,(9,y,0),(0,1,0),14.19-y)
 print('key gauge',y,'missing',t.volume(t.boolean(t.BRepAlgoAPI_Cut,q,prop)))
