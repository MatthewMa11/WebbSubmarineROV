from pathlib import Path
import json,collections
r=Path(__file__).resolve().parent;v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
n={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],n)
t=n['t'];ss=n['solids'](r/'Assembly-R14-smooth-frame.step');ps=n['solids'](r/'Thruster-R14-smooth-frame.step')
def sig(s):return tuple(round(x,3) for pp in t.limits(s) for x in pp)+(round(t.volume(s),2),round(t.area(s),2))
checks=[]
def check(name,ok):checks.append(dict(check=name,passed=bool(ok)));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
check('native assembly retains47 solids with matching checked shape signatures and poses',len(ss)==len(ps)==47 and collections.Counter(map(sig,ss))==collections.Counter(map(sig,ps)))
check('native cone frame and fan interference check is clear','No interferences' in (r/'native-interference.txt').read_text(encoding='utf-8'))
(r/'assembly-verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
