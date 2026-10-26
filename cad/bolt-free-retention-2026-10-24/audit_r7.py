"""Audit actual native STEP rather than relying on FeatureScript body names."""
from pathlib import Path
import sys,json
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import t,cylinder
from verify_kit_hardware import solids
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
def exact_limits(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b,False,False)
 return [[p.X(),p.Y(),p.Z()] for p in (b.CornerMin(),b.CornerMax())]
t.limits=exact_limits
filename=Path(sys.argv[1])
parts={};rings=[];hardware=[]
for s in solids(filename):
 lo,hi=t.limits(s);dx,dy,dz=[b-a for a,b in zip(lo,hi)]
 if lo[1]<-30 and dx>90:n='nozzle'
 elif dz>70 and dx<60:n='propeller'
 elif dx>80 and lo[1]>10:n='cover'
 elif 27<dx<29 and dy>25:n='rotor'
 elif 27<dx<29 and dy<6:n='stator'
 elif 39<dx<47 and 39<dz<47 and 2<dy<8 and -8<lo[1]<0 and hi[1]<5:
  rings.append(s);continue
 else:hardware.append(s);continue
 assert n not in parts,n
 parts[n]=s
checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
check('five original mechanical components retained',len(parts)==5)
check('two external printed locking rings exist',len(rings)==2,ring_count=len(rings))
check('six external clamp fasteners removed, thirty-six stationary fasteners retained',len(hardware)==36,metal_hardware_count=len(hardware))
check('complete bolt-free assembly has forty-three solids',len(parts)+len(rings)+len(hardware)==43,solid_count=len(parts)+len(rings)+len(hardware))
if len(rings)==2 and len(parts)==5:
 insert_region=cylinder(11.31,(0,5.59,0),(0,1,0),4.42)
 blocked=sum(abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,q,insert_region))) for q in [parts['propeller']]+rings)
 check('no printed material in former internal spacer region',blocked<1e-5,obstruction_mm3=blocked)
 check('integral propeller stays within the original envelope of old clamp ears',t.limits(parts['propeller'])[1][0]-t.limits(parts['propeller'])[0][0]<43)
out=r/('baseline-audit.json' if 'R6p1' in filename.name else 'structure-audit.json')
out.write_text(json.dumps(checks,indent=2),encoding='utf-8')
raise SystemExit(0 if all(x['passed'] for x in checks) else 1)
