from pathlib import Path
import json,collections
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];cylinder=ns['cylinder'];ss=ns['solids'](r/'Assembly-R11-actual-models.step');ps=ns['solids'](r/'Thruster-R11-actual-models.step')
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
def sig(s):return tuple(round(x,3) for pp in t.limits(s) for x in pp)+(round(t.volume(s),2),round(t.area(s),2))
checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
check('native assembly contains exactly the checked 48 solids in their checked poses',len(ss)==len(ps)==48 and collections.Counter(map(sig,ss))==collections.Counter(map(sig,ps)))
for name,count in [('fixed',44),('rotating',4)]:
 text=(r/('native-'+name+'-group.txt')).read_text(encoding='utf-8')
 check('native '+name+' group has '+str(count)+' instances',text.count('×')==count,count=text.count('×'))
check('native fan and housing interference result is clear','No interferences' in (r/'native-interference.txt').read_text(encoding='utf-8'))
text=(r/'native-motion.txt').read_text(encoding='utf-8')
check('native 0 to 360 degree revolute animation recorded','360 deg' in text and 'Current value' in text and 'Revolute 1' in text)
# Independent dense bidirectional mesh test, with a shifted negative control.
# Coincident exported loft B-reps have unreliable OCP CSG classification:
# both cuts returned almost their entire volume despite equal surface samples.
profile=json.loads((r/'profile-verification.json').read_text())
negative=json.loads((r/'profile-negative-control.json').read_text())
check('outer blade surfaces retained from R10',profile['passed'],tolerance_mm=profile['tolerance_mm'],directions=profile['directions'])
check('blade comparison detects an incorrect axial placement',not negative['passed'],wrong_shift_mm=negative['shift_mm'])
(r/'assembly-verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
