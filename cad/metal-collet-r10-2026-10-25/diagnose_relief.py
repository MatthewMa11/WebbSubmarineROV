from pathlib import Path
import math
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];ss=ns['solids'](r/'Thruster-R10-metal-collet.step')
frame=next(s for s in ss if t.limits(s)[0][1]<-29 and t.limits(s)[1][0]-t.limits(s)[0][0]>90)
ext=next(s for s in ss if 18.9<t.limits(s)[0][1]<19.1 and 46.9<t.limits(s)[1][1]<47.1)
from OCP.gp import gp_Trsf,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
tr=gp_Trsf();tr.SetTranslation(gp_Vec(-.17320508075688773,0,.1))
shift=BRepBuilderAPI_Transform(ext,tr,True).Shape()
q=t.boolean(t.BRepAlgoAPI_Common,shift,frame)
print('common',t.volume(q),t.limits(q),'valid',BRepCheck_Analyzer(q).IsValid(),flush=True)
ex=TopExp_Explorer(q,TopAbs_SOLID)
while ex.More():
 s=ex.Current();print('piece',t.volume(s),t.limits(s),'valid',BRepCheck_Analyzer(s).IsValid(),flush=True);ex.Next()
