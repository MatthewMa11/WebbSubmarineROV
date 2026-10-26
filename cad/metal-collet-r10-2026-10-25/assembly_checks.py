from pathlib import Path
import json,collections
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];cylinder=ns['cylinder'];ss=ns['solids'](r/'Assembly-R10-metal-collet.step');ps=ns['solids'](r/'Thruster-R10-metal-collet.step')
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
def sig(s):return tuple(round(v,3) for pp in t.limits(s) for v in pp)+(round(t.volume(s),2),round(t.area(s),2))
def common(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
checks=[]
def check(n,ok,**detail):
 checks.append(dict(check=n,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+n,flush=True)
check('constrained assembly exactly matches all 45 Part Studio placements',len(ss)==len(ps)==45 and collections.Counter(map(sig,ss))==collections.Counter(map(sig,ps)))
frame=next(s for s in ss if span(s)[0]>90 and t.limits(s)[0][1]<-29)
cap=next(s for s in ss if span(s)[0]>90 and t.limits(s)[0][1]>40)
extension=next(s for s in ss if span(s)[0]>90 and 18.9<t.limits(s)[0][1]<19.1)
fan=next(s for s in ss if span(s)[2]>70 and span(s)[0]<50)
adapter=next(s for s in ss if abs(span(s)[0]-15.5)<.01 and span(s)[1]>24)
washer=next(s for s in ss if abs(span(s)[0]-15.5)<.01 and 1.49<span(s)[1]<1.51)
nut=next(s for s in ss if 4.99<span(s)[1]<5.01 and 32.29<t.limits(s)[0][1]<32.31)
rotor=next(s for s in ss if 27<span(s)[0]<29 and span(s)[1]>25)
stator=next(s for s in ss if 27<span(s)[0]<29 and span(s)[1]<6)
mechanical=[frame,cap,extension,fan,adapter,washer,nut,rotor,stator]
hw=[s for s in ss if not any(s.IsSame(q) for q in mechanical)]
moving=[fan,adapter,washer,nut,rotor,stator]
# Full forward withdrawal/insertion corridor, with cap and extension off.
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
core=cylinder(13.92,(0,-11,0),(0,1,0),131)
outer=cylinder(35.57,(0,24.23,0),(0,1,0),95.77)
corridor=t.boolean(BRepAlgoAPI_Fuse,core,outer)
escaped=[abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,s,corridor))) for s in moving]
check('bench-built motor/fan/collet fit through continuous insertion corridor',max(escaped)<1e-4,escaped_mm3=escaped)
remaining=[]
for s in hw:
 lo,hi=t.limits(s);dx,dy,dz=span(s)
 # Removed for insertion: 4 M3x40 cover screws, 4 front cover washers,
 # and 4 motor-base screws plus their 4 washers.
 remove=(42.99<dy<43.01 or (lo[1]>51 and dy<1) or (-20<lo[1]<-16.49 and hi[1]<-8))
 if not remove:remaining.append(s)
check('only twenty stationary fasteners remain during motor insertion',len(remaining)==20,remaining=len(remaining))
intrusions=[common(corridor,s) for s in [frame]+remaining]
check('continuous insertion corridor clears frame and retained fasteners',max(intrusions)<1e-4,largest_overlap_mm3=max(intrusions))
# Socket clearance study, not an exact tool model: 18 mm OD, 12 mm open
# depth clears the exposed M6 stud. Cap must be removed to use this tool.
socket=t.boolean(t.BRepAlgoAPI_Cut,cylinder(9,(0,32.3,0),(0,1,0),70),cylinder(6,(0,32.29,0),(0,1,0),12.01))
obstacles=[frame,extension,fan,adapter,washer]+hw
socket_intrusions=[common(socket,s) for s in obstacles]
check('18 mm OD nut socket has a straight path with cap off',max(socket_intrusions)<1e-4,largest_overlap_mm3=max(socket_intrusions))
cover_access=[]
for x,z in [(0,44.5),(-44.5,0),(0,-44.5),(44.5,0)]:
 probe=cylinder(1.45,(x,55.51,z),(0,1,0),60)
 cover_access.append(sum(common(probe,s) for s in mechanical))
check('straight key access exists above all four M3x40 heads',max(cover_access)<1e-4,overlaps_mm3=cover_access)
(r/'assembly-verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
