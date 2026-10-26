exec(open(__file__.replace('inspect_faces.py','diagnose_threads.py')).read().split('for i,q in enumerate(rings):')[0])
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cone
from OCP.BRepCheck import BRepCheck_Analyzer
print('validity', [BRepCheck_Analyzer(s).IsValid() for s in [prop]+rings],flush=True)
for i,s in enumerate([prop]+rings):
 e=TopExp_Explorer(s,TopAbs_FACE)
 while e.More():
  a=BRepAdaptor_Surface(TopoDS.Face(e.Current()));e.Next()
  if a.GetType()==GeomAbs_Cone:
   c=a.Cone();o=c.Location();di=c.Axis().Direction()
   print('cone',i,'loc',[o.X(),o.Y(),o.Z()],'axis',[di.X(),di.Y(),di.Z()],'R',c.RefRadius(),'ang',c.SemiAngle(),flush=True)
