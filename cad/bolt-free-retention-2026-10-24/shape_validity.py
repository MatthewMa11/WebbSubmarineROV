from pathlib import Path
f=Path(__file__).resolve().parent/'verify_r7.py'
exec(f.read_text().split("p,rings,h=read(")[0])
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE,TopAbs_SHELL,TopAbs_SOLID
for name in ('Thruster-R7-bolt-free.step','../flatter-motor-boss-2026-10-24/Thruster-R6p1-flat-motor-boss.step'):
 p,rr,hh=read(r/name)
 for label,s in list(p.items())+list(enumerate(rr)):
  a=BRepCheck_Analyzer(s)
  bad=[]
  for typ in (TopAbs_FACE,TopAbs_EDGE,TopAbs_SHELL,TopAbs_SOLID):
   e=TopExp_Explorer(s,typ)
   while e.More():
    if not a.IsValid(e.Current()):bad.append([str(typ),t.limits(e.Current())])
    e.Next()
  print(name,label,'valid',a.IsValid(),'bad',bad[:12],flush=True)
