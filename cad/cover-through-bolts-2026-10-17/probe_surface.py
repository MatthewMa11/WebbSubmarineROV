from pathlib import Path
import sys
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from check_print_revision import mesh,points
import vtk,numpy as np
new=mesh(r/'printable-STLs/Nozzle-M3-through-bolts-R4.stl');old=mesh(r.parent/'motor-centering-cover-2026-10-17/Nozzle-centering-cup-R3.stl')
for name,a,b in [('new',new,old),('old',old,new)]:
 p=points(a)[::7];protected=np.ones(len(p),dtype=bool)
 for x,z in ((0,44.5),(-44.5,0),(0,-44.5),(44.5,0)):
  protected &= ~((np.linalg.norm(p[:,[0,2]]-[x,z],axis=1)<8.61)&(p[:,1]>12.29))
 p=p[protected];f=vtk.vtkImplicitPolyDataDistance();f.SetInput(b)
 d=np.array([abs(f.EvaluateFunction(q)) for q in p]);idx=np.argsort(d)[-15:]
 print(name,'max',d.max(),'over .02',sum(d>.02),'probes',len(d),flush=True)
 for j in idx:print(d[j],p[j].tolist(),flush=True)
