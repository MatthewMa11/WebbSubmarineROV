"""Cap is removed for installation; reserve an 8.4 mm OD hollow nutdriver."""
from pathlib import Path
import json
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];cylinder=ns['cylinder'];ss=ns['solids'](r/'Thruster-R9-forward-fan.step')
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
fan=next(s for s in ss if span(s)[2]>70 and span(s)[0]<60)
jaw=next(s for s in ss if 40<span(s)[0]<43 and 6<span(s)[1]<8 and 5<span(s)[2]<7)
checks=[]
for x in (-16.8,16.8):
 for side in (-1,1):
  start=(x,15.8,side*6.201);axis=(0,0,side)
  outer=cylinder(4.2,start,axis,24);inner=cylinder(3.3,start,axis,24.01)
  tool=t.boolean(t.BRepAlgoAPI_Cut,outer,inner)
  overlap=sum(abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,tool,q))) for q in (fan,jaw))
  checks.append(dict(x=x,side=side,overlap_mm3=overlap,passed=overlap<1e-4))
  print(('PASS ' if overlap<1e-4 else 'FAIL ')+f'8.4 mm nutdriver access at X{x}, side {side}: overlap {overlap:.4f} mm3',flush=True)
(r/'tool-access-verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(q['passed'] for q in checks) else 1)
