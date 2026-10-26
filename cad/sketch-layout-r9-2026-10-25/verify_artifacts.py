from pathlib import Path
import json,zipfile,hashlib
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];ss=ns['solids'](r/'Thruster-R9-forward-fan.step')
from check_print_revision import mesh
import vtk
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
parts={
 'Fan-R9-forward-fan.stl':next(s for s in ss if span(s)[2]>70 and span(s)[0]<60),
 'Upper-jaw-R9-M3-axle-clamp.stl':next(s for s in ss if 40<span(s)[0]<43 and 6<span(s)[1]<8 and 5<span(s)[2]<7)}
checks=[]
for name,s in parts.items():
 p=vtk.vtkMassProperties();p.SetInputData(mesh(r/name));p.Update()
 native=abs(t.volume(s));delta=abs(p.GetVolume()-native)/native
 ok=delta<.002
 checks.append(dict(file=name,native_volume_mm3=native,mesh_volume_mm3=p.GetVolume(),relative_delta=delta,passed=ok))
 print(('PASS ' if ok else 'FAIL ')+name+' matches final native assembly volume: '+str(delta),flush=True)
target=r/'R9-Forward-Fan-Print-Kit.zip'
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for info in z.infolist():
  local=r/info.filename
  assert local.read_bytes()==z.read(info.filename),info.filename
 checks.append(dict(check='all ZIP entries match final local deliverables, CRC valid',passed=True,files=len(z.infolist())))
print('PASS ZIP contents and CRC match final deliverables',flush=True)
(r/'artifact-verification.json').write_text(json.dumps(checks,indent=2))
assert all(q['passed'] for q in checks)
with zipfile.ZipFile(target,'a',zipfile.ZIP_DEFLATED) as z:z.write(r/'artifact-verification.json','artifact-verification.json')
