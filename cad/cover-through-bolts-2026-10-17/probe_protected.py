from verify_through_joints import *
p,h=read(r/'Thruster-cover-through-bolts-R4-verified.step');o,oh=read(r.parent/'motor-centering-cover-2026-10-17/Thruster-centering-cup-R3.step')
a=p['nozzle'];b=o['nozzle']
for i in range(4):
 region=turn(cylinder(8.6,(0,12.3,44.5),(0,1,0),53),i)
 a=t.boolean(t.BRepAlgoAPI_Cut,a,region);b=t.boolean(t.BRepAlgoAPI_Cut,b,region)
print('volume',t.volume(a),t.volume(b),'area',t.area(a),t.area(b),flush=True)
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
for label,aa,bb in [('added',a,b),('removed',b,a)]:
 s=t.boolean(t.BRepAlgoAPI_Cut,aa,bb);print(label,t.volume(s),flush=True)
 e=TopExp_Explorer(s,TopAbs_SOLID)
 while e.More():
  q=e.Current();print('patch',t.volume(q),'bounds',t.limits(q),flush=True);e.Next()
