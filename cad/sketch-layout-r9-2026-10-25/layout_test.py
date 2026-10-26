"""Layout assertions independent of the native FeatureScript implementation."""
from pathlib import Path
import sys,json
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];cyl=ns['cylinder']
path=Path(sys.argv[1]) if len(sys.argv)>1 else r/'Thruster-R9-forward-fan.step'
ss=ns['solids'](path)
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
fan=next(s for s in ss if span(s)[2]>70 and span(s)[0]<60)
checks=[]
def check(name,ok,**d):
 checks.append(dict(check=name,passed=bool(ok),detail=d));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
rear=cyl(18.1,(0,-3.1,0),(0,1,0),14.59)
rear=t.boolean(t.BRepAlgoAPI_Cut,rear,cyl(13.9,(0,-3.11,0),(0,1,0),14.61))
vol=abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,fan,rear)))
check('old motor-bell cup removed',vol<1e-4,rear_cup_material_mm3=vol)
outside=t.boolean(t.BRepAlgoAPI_Cut,fan,cyl(27.01,(0,-6.2,0),(0,1,0),30))
lo,hi=t.limits(outside)
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
mass=GProp_GProps();BRepGProp.VolumeProperties_s(outside,mass);blade_plane=mass.CentreOfMass().Y()
check('outer blade plane lies ahead of motor face',blade_plane>15 and lo[1]>12.9 and hi[1]<19.61,blade_tip_y_bounds_mm=[lo[1],hi[1]],blade_volume_centroid_y_mm=blade_plane)
check('46 assembly bodies retained',len(ss)==46,bodies=len(ss))
(r/('baseline-red.json' if 'R8' in path.name else 'layout-verification.json')).write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
