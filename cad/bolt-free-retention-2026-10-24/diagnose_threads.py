from pathlib import Path
import sys, math, json
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import t
from verify_kit_hardware import solids
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
def exact_limits(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b,False,False)
 return [[p.X(),p.Y(),p.Z()] for p in (b.CornerMin(),b.CornerMax())]
t.limits=exact_limits
ss=solids(r/'DRAFT-R7-thread-diagnostic.step');rings=[]
for s in ss:
 lo,hi=t.limits(s);d=[b-a for a,b in zip(lo,hi)]
 if d[0]>30:print('large body',lo,hi,d,flush=True)
 if d[2]>70 and d[0]<60:prop=s
 if 39<d[0]<49 and 39<d[2]<49 and 2<d[1]<10 and -10<lo[1]<0 and hi[1]<6:rings.append(s)
print('body count',len(ss),'prop',t.limits(prop),'rings',[t.limits(q) for q in rings],flush=True)
for i,q in enumerate(rings):
 for angle in (0,90,180,-90):
  tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,1,0)),math.radians(angle))
  qt=BRepBuilderAPI_Transform(q,tr,True).Shape()
  v=t.volume(t.boolean(t.BRepAlgoAPI_Common,qt,prop))
  print('ring',i,'extra angle',angle,'overlap',v,flush=True)
