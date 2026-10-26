"""Geometry requirements for the R8 axle-clamp revision, including RED R7 baseline."""
from pathlib import Path
import sys,json
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)}
exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];solids=ns['solids'];cylinder=ns['cylinder']
path=Path(sys.argv[1]) if len(sys.argv)>1 else r/'Thruster-R8-M3-axle-clamp.step'
ss=solids(path); checks=[]
def check(name,ok,**d):
 checks.append(dict(check=name,passed=bool(ok),detail=d));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
def overlap(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
rings=[s for s in ss if 39<span(s)[0]<47 and 39<span(s)[2]<47 and 2<span(s)[1]<8 and -8<t.limits(s)[0][1]<0]
jaws=[s for s in ss if 40<span(s)[0]<43 and 6<span(s)[1]<8 and 5<span(s)[2]<7]
check('collar and jam ring removed',not rings,count=len(rings))
check('one removable upper axle jaw',len(jaws)==1,count=len(jaws))
check('46 assembly bodies',len(ss)==46,count=len(ss))
# A shaft-sized cylinder must pass through both printed jaws without interference.
fan=[s for s in ss if span(s)[2]>70 and span(s)[0]<60][0]
probe=cylinder(1.5875,(0,16.25,0),(0,1,0),3.05)
check('nominal shaft passes through fan and jaw',overlap(fan,probe)<1e-5 and all(overlap(j,probe)<1e-5 for j in jaws))
# A thin annular sector near the shaft proves the hub actually grips at the axle.
outer=cylinder(1.8,(0,16.3,0),(0,1,0),2.9)
inner=cylinder(1.7,(0,16.29,0),(0,1,0),2.92)
grip=t.boolean(t.BRepAlgoAPI_Cut,outer,inner)
check('fan lower jaw surrounds the axle',overlap(fan,grip)>.5,material_mm3=overlap(fan,grip))
check('upper jaw surrounds the axle',sum(overlap(j,grip) for j in jaws)>.5,material_mm3=sum(overlap(j,grip) for j in jaws))
(r/('baseline-red.json' if 'R7' in path.name else 'audit-r8.json')).write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
