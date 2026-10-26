"""CAD tool/insertion checks for bench-first fan/motor assembly; cap is removed."""
from pathlib import Path
import json,sys
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py';ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];cylinder=ns['cylinder'];p,_,extra=ns['read'](r/'Thruster-R9-forward-fan.step');_,_,oldhw=ns['read'](v.parent/'Thruster-R7-bolt-free.step')
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Vec
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
def sig(s):return tuple(round(v,4) for q in t.limits(s) for v in q)+(round(t.volume(s),3),round(t.area(s),3))
jaw=next(s for s in extra if 40<span(s)[0]<43 and 6<span(s)[1]<8 and 5<span(s)[2]<7)
stationary=[s for s in extra if sig(s) in {sig(q) for q in oldhw}]
newhw=[s for s in extra if sig(s) not in {sig(q) for q in oldhw} and s is not jaw]
assembly=[p['propeller'],jaw,p['rotor'],p['stator']]+newhw
checks=[]
def common(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
def check(name,ok,**d):
 checks.append(dict(check=name,passed=bool(ok),detail=d));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
in_frame='--in-frame' in sys.argv
for x in (-16.8,16.8):
 for side in (-1,1):
  start=(x,15.8,side*6.201);axis=(0,0,side)
  tool=t.boolean(t.BRepAlgoAPI_Cut,cylinder(4.2,start,axis,70),cylinder(3.3,start,axis,70.01))
  targets=[p['propeller'],jaw,p['rotor'],p['stator']]+([p['nozzle']] if in_frame else [])
  vol=sum(common(tool,q) for q in targets)
  check(('in-frame' if in_frame else 'bench')+f' 70 mm driver path X{x}, side{side}',vol<1e-4,overlap_mm3=vol)
if not in_frame:
 # Radius never decreases toward the open front, so this covers every axial
 # insertion position between the final seat and80 mm forward of it.
 corridor=cylinder(13.9,(0,-11,0),(0,1,0),131)
 corridor=t.boolean(BRepAlgoAPI_Fuse,corridor,cylinder(22.27,(0,11.49,0),(0,1,0),108.51))
 ring=t.boolean(t.BRepAlgoAPI_Cut,cylinder(35.57,(0,13,0),(0,1,0),107),cylinder(21.93,(0,12.99,0),(0,1,0),107.02))
 corridor=t.boolean(BRepAlgoAPI_Fuse,corridor,ring)
 motorbase=[s for s in stationary if t.limits(s)[1][1]<-5]
 fixed=[p['nozzle']]+[s for s in stationary if s not in motorbase]
 check('preassembly has eight components and eight motor-base fasteners are withdrawn',len(assembly)==8 and len(motorbase)==8,assembly_parts=len(assembly),withdrawn_fasteners=len(motorbase))
 overlap=sum(common(corridor,q) for q in fixed)
 check('continuous insertion corridor clears frame and remaining stationary fasteners',overlap<1e-4,overlap_mm3=overlap,fixed_parts=len(fixed))
 escaped={}
 for offset in (0,80):
  tr=gp_Trsf();tr.SetTranslation(gp_Vec(0,offset,0))
  escaped[str(offset)]=sum(abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,BRepBuilderAPI_Transform(q,tr,True).Shape(),corridor))) for q in assembly)
 check('eight-piece preassembly stays inside the monotone insertion corridor',max(escaped.values())<1e-4,escaped_mm3=escaped)
(r/('preassembly-red-in-frame.json' if in_frame else 'preassembly-verification.json')).write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(q['passed'] for q in checks) else 1)
