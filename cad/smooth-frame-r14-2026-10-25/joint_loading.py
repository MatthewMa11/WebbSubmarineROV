from pathlib import Path
import math,json
r=Path(__file__).resolve().parent;v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py';n={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],n)
t=n['t'];cyl=n['cylinder'];ss=n['solids'](r/'Thruster-R14-smooth-frame.step')
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism,BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse

def bounds(q):return t.limits(q)
def mid(q):
 a,b=bounds(q);return [(x+y)/2 for x,y in zip(a,b)]
def span(q):
 a,b=bounds(q);return [y-x for x,y in zip(a,b)]
def hull(points):
 pts=sorted(set(points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 lo=[]
 for p in pts:
  while len(lo)>1 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 hi=[]
 for p in pts[::-1]:
  while len(hi)>1 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
rows=[]
for i,(rx,rz) in enumerate([(0,1),(-1,0),(0,-1),(1,0)]):
 x,z=44.5*rx,44.5*rz;theta=-i*math.pi/2;points=[]
 for k in range(6):
  a=(30+k*60)*math.pi/180;lx=5.7/math.sqrt(3)*math.cos(a);lz=5.7/math.sqrt(3)*math.sin(a)
  px=lx*math.cos(theta)+lz*math.sin(theta);pz=-lx*math.sin(theta)+lz*math.cos(theta)
  for shift in [0,20]:points.append((x+px+rx*shift,z+pz+rz*shift))
 poly=BRepBuilderAPI_MakePolygon()
 for px,pz in hull(points):poly.Add(gp_Pnt(px,41.15,pz))
 poly.Close();face=BRepBuilderAPI_MakeFace(poly.Wire()).Face();nut=BRepPrimAPI_MakePrism(face,gp_Vec(0,2.4,0)).Shape()
 washer=cyl(3.6,(x,43.55,z),(0,1,0),.5);end=cyl(3.6,(x+20*rx,43.55,z+20*rz),(0,1,0),.5)
 if rx:lo=(min(x,x+20*rx),43.55,z-3.6);hi=(max(x,x+20*rx),44.05,z+3.6)
 else:lo=(x-3.6,43.55,min(z,z+20*rz));hi=(x+3.6,44.05,max(z,z+20*rz))
 rect=BRepPrimAPI_MakeBox(gp_Pnt(*lo),gp_Pnt(*hi)).Shape();washer=t.boolean(BRepAlgoAPI_Fuse,t.boolean(BRepAlgoAPI_Fuse,washer,end),rect)
 conflicts=[]
 for j,q in enumerate(ss):
  a,b=bounds(q);d=span(q);c=mid(q)
  cap=d[0]>90 and a[1]>46.9;bolt=abs(a[1]-40.5)<.001 and abs(b[1]-55.5)<.001
  fw=abs(a[1]-52)<.001 and abs(b[1]-52.5)<.001
  own=math.hypot(c[0]-x,c[2]-z)<.001 and ((abs(a[1]-41.4)<.001 and abs(b[1]-43.8)<.001) or (abs(a[1]-43.8)<.001 and abs(b[1]-44.3)<.001))
  if cap or bolt or fw or own:continue
  for name,g in [('nut',nut),('washer',washer)]:
   ga,gb=bounds(g)
   if any(b[k]<ga[k]-1e-5 or a[k]>gb[k]+1e-5 for k in range(3)):continue
   vol=abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,g,q)))
   if vol>1e-4:conflicts.append(dict(part=j,gauge=name,overlap_mm3=vol))
 rows.append(dict(joint=i+1,passed=not conflicts,conflicts=conflicts,nut_gauge_AF_mm=5.7,washer_gauge_OD_mm=7.2,loading_stack_offset_y_mm=-.25))
report=dict(check='continuous outward swept nut and washer loading paths',passed=all(x['passed'] for x in rows),cap_and_cover_bolts_removed=True,radial_stroke_mm=20,joints=rows)
(r/'joint-loading-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True);raise SystemExit(0 if report['passed'] else 1)

