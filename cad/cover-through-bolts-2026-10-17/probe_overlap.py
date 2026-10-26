from pathlib import Path
import sys
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
p,h=read(r/'Thruster-cover-through-bolts-R4.step')
s=t.boolean(t.BRepAlgoAPI_Common,p['nozzle'],p['cover'])
print('overlap volume',t.volume(s),flush=True)
e=TopExp_Explorer(s,TopAbs_SOLID)
while e.More():
 q=e.Current();print('patch',t.volume(q),'bounds',t.limits(q),flush=True);e.Next()
for j,q in enumerate(h):
 lo,hi=t.limits(q)
 if lo[1]>12.4 and hi[1]>27:print('cover screw',j,lo,hi,flush=True)
