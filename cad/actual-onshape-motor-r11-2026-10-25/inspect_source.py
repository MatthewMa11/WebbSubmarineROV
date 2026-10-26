from pathlib import Path
import json,collections,sys
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];solids=ns['solids']
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Cone
from OCP.BRepCheck import BRepCheck_Analyzer
report=[]
for i,s in enumerate(solids(r/(sys.argv[1] if len(sys.argv)>1 else 'SOURCE-Motor-assembly.step'))):
 lo,hi=t.limits(s);cyl=[];cones=[];counts=collections.Counter();ex=TopExp_Explorer(s,TopAbs_FACE)
 while ex.More():
  f=TopoDS.Face(ex.Current());a=BRepAdaptor_Surface(f);counts[str(a.GetType())]+=1
  if a.GetType()==GeomAbs_Cylinder:
   c=a.Cylinder();ax=c.Axis();p=ax.Location();d=ax.Direction()
   cyl.append({'r':c.Radius(),'p':[p.X(),p.Y(),p.Z()],'d':[d.X(),d.Y(),d.Z()],'bounds':t.limits(f)})
  if a.GetType()==GeomAbs_Cone:
   c=a.Cone();ax=c.Axis();p=ax.Location();d=ax.Direction()
   cones.append({'r':c.RefRadius(),'angle':c.SemiAngle(),'p':[p.X(),p.Y(),p.Z()],'d':[d.X(),d.Y(),d.Z()],'bounds':t.limits(f)})
  ex.Next()
 item=dict(index=i,bounds_mm=[lo,hi],span_mm=[b-a for a,b in zip(lo,hi)],volume_mm3=t.volume(s),area_mm2=t.area(s),valid=BRepCheck_Analyzer(s).IsValid(),types=counts,cylinders=cyl,cones=cones)
 report.append(item)
 print(i,dict(bounds_mm=[lo,hi],volume_mm3=item['volume_mm3'],valid=item['valid'],cylinders=len(cyl),cones=len(cones)),flush=True)
(r/'source-measurements.json').write_text(json.dumps(report,indent=2))
