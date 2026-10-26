exec(open(__file__.replace('probe_threads.py','diagnose_threads.py')).read().split('for i,q in enumerate(rings):')[0])
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN
classifiers=[BRepClass3d_SolidClassifier(s) for s in [prop]+rings]
for y in (-4,-3.5,-3,-2.5,-2,-1.5,-1,-.5,0,.5,1,1.5,2):
 row=[]
 for cl in classifiers:
  xx=[]
  for j in range(160,224):
   x=j/10;cl.Perform(gp_Pnt(x,y,0),1e-6)
   if cl.State()==TopAbs_IN:xx.append(x)
  row.append(xx)
 print('Y',y,'prop/main/jam',row,flush=True)
