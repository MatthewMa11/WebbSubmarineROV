from pathlib import Path
import runpy,sys
ns=runpy.run_path(str(Path(__file__).with_name('check_packaging.py')))
t=ns['t'];parts=ns['parts'];r=ns['root']
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln,gp_Pnt,gp_Dir
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(12,6))
for name,s,col in [('frame',next(s for s in parts if t.limits(s)[0][1]<-30 and t.limits(s)[1][0]-t.limits(s)[0][0]>90),'#333333'),('cap',ns['cover'],'#888888')]:
 print(name,t.limits(s))
 a=BRepAlgoAPI_Section(s,gp_Pln(gp_Pnt(0,0,0),gp_Dir(0,0,1)),False);a.Build()
 ex=TopExp_Explorer(a.Shape(),TopAbs_EDGE)
 while ex.More():
  c=BRepAdaptor_Curve(TopoDS.Edge(ex.Current()))
  pts=[c.Value(float(u)) for u in np.linspace(c.FirstParameter(),c.LastParameter(),80)]
  ax.plot([p.Y() for p in pts],[p.X() for p in pts],color=col,lw=1)
  ex.Next()
ax.set(xlabel='Axial Y (mm)',ylabel='Radial X at Z=0 (mm)',xlim=(-35,80),ylim=(-55,55),title='Existing frame and cap section: unchanged source geometry')
ax.set_aspect('equal');ax.grid(alpha=.25);fig.tight_layout();fig.savefig(r/'existing-section.png',dpi=150)
