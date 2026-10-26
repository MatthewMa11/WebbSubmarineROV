from pathlib import Path
import sys, json
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t,cylinder
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
p,h=read(r.parent/'motor-centering-cover-2026-10-17/Thruster-centering-cup-R3.step')
def volcommon(a,b):return t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b))
for x,z in ((0,44.5),(-44.5,0),(0,-44.5),(44.5,0)):
 ear=cylinder(5,(x,19,z),(0,1,0),5)
 flange=cylinder(5,(x,12.5,z),(0,1,0),6.5)
 print((x,z),'ear attachment overlap',volcommon(p['cover'],ear),'flange attachment',volcommon(p['nozzle'],flange),flush=True)
 through=cylinder(1.69,(x,12.4,z),(0,1,0),12)
 print('old design blocks through path:',volcommon(p['nozzle'],through)+volcommon(p['cover'],through),flush=True)
