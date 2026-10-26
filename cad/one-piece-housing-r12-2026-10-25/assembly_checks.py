from pathlib import Path
import json,collections
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py';ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];ss=ns['solids'](r/'Assembly-R12-one-piece.step');ps=ns['solids'](r/'Thruster-R12-one-piece.step')
def sig(s):return tuple(round(x,3) for pp in t.limits(s) for x in pp)+(round(t.volume(s),2),round(t.area(s),2))
checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
check('native assembly has all47 checked solids in checked poses',len(ss)==len(ps)==47 and collections.Counter(map(sig,ss))==collections.Counter(map(sig,ps)))
for name,count in [('fixed',43),('rotating',4)]:
 text=(r/('native-'+name+'-group.txt')).read_text(encoding='utf-8')
 check('native '+name+' group contains '+str(count)+' instances',text.count('\u00d7')==count,count=text.count('\u00d7'))
check('native fan cap and merged housing have no interference','No interferences' in (r/'native-interference.txt').read_text(encoding='utf-8'))
text=(r/'native-motion.txt').read_text(encoding='utf-8')
check('native0..360 degree motion remains available','360 deg' in text and 'Current value' in text and 'Revolute 1' in text)
(r/'assembly-verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
