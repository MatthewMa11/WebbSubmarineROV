from pathlib import Path
import sys,json,collections
r=Path(__file__).resolve().parent;v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py';n={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],n)
t=n['t'];cyl=n['cylinder'];ss=n['solids'](Path(sys.argv[1]) if len(sys.argv)>1 else r/'Thruster-R13-concave-cap.step')
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Sphere
checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def dims(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
def center(s):
 lo,hi=t.limits(s);return [(a+b)/2 for a,b in zip(lo,hi)]
def overlap(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
check('47 assembly solids retained',len(ss)==47)
cap=next(s for s in ss if dims(s)[0]>90 and t.limits(s)[0][1]>46.9)
house=next(s for s in ss if dims(s)[0]>100 and t.limits(s)[0][1]<-29)
bowl=[];ex=TopExp_Explorer(cap,TopAbs_FACE)
while ex.More():
 a=BRepAdaptor_Surface(TopoDS.Face(ex.Current()))
 if a.GetType()==GeomAbs_Sphere:
  q=a.Sphere();p=q.Location()
  if abs(q.Radius()-13)<1e-4 and abs(p.Y()-43)<1e-4:bowl.append(q.Radius())
 ex.Next()
check('cone has inward spherical bowlR13 atY43',len(bowl)>=1,count=len(bowl))
probe=cyl(9,(0,48,0),(0,1,0),4)
vol=overlap(cap,probe);check('inner recess accepts18mm-diameter by4mm clearance gauge',vol<1e-4,overlap_mm3=vol)
short=[];nuts=[];washers=[]
for s in ss:
 lo,hi=t.limits(s);dx,dy,dz=dims(s);c=center(s)
 if abs(max(abs(c[0]),abs(c[2]))-44.5)>.001:continue
 if abs(lo[1]-40.5)<.001 and abs(hi[1]-55.5)<.001:short.append(s)
 if abs(lo[1]-41.4)<.001 and abs(hi[1]-43.8)<.001:nuts.append(s)
 if abs(lo[1]-43.8)<.001 and abs(hi[1]-44.3)<.001:washers.append(s)
check('four M3x12 cover bolts replace40mm bolts',len(short)==4,count=len(short))
check('four nuts and four rear washers sit in front-access seats',len(nuts)==len(washers)==4,nuts=len(nuts),washers=len(washers))
check('housing has0.8mm locating pilots',abs(t.limits(house)[1][1]-47.8)<.001,maxY=t.limits(house)[1][1])
if bowl and len(short)==len(nuts)==len(washers)==4:
 import math
 from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
 from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
 from OCP.GeomAbs import GeomAbs_Plane,GeomAbs_Cylinder
 def sig(q):return tuple(round(x,4) for pp in t.limits(q) for x in pp)+(round(t.volume(q),4),round(t.area(q),4))
 old=n['solids'](r.parent/'one-piece-housing-r12-2026-10-25/Thruster-R12-one-piece.step')
 oldother=[]
 for q in old:
  lo,hi=t.limits(q);dx,dy,dz=dims(q);c=center(q)
  shell=dx>90 and (lo[1]<-29 or lo[1]>46.9)
  hw=abs(max(abs(c[0]),abs(c[2]))-44.5)<.001 and ((abs(lo[1]-12.5)<.001 and abs(hi[1]-55.5)<.001) or (abs(lo[1]-13.1)<.001 and abs(hi[1]-15.5)<.001) or (abs(lo[1]-15.5)<.001 and abs(hi[1]-16)<.001))
  if not shell and not hw:oldother.append(q)
 modified=[cap,house]+short+nuts+washers
 other=[q for q in ss if not any(q.IsSame(x) for x in modified)]
 check('other33 motor fan metal adapter and fastener bodies unchanged',len(other)==len(oldother)==33 and collections.Counter(map(sig,other))==collections.Counter(map(sig,oldother)))
 oldcap=next(q for q in old if dims(q)[0]>90 and t.limits(q)[0][1]>46.9)
 check('outside cone bounding dimensions retained',max(abs(x-y) for aa,bb in zip(t.limits(cap),t.limits(oldcap)) for x,y in zip(aa,bb))<.001)
 check('obsolete center passage closed below bowl',abs(t.volume(cyl(1.6,(0,56.2,0),(0,1,0),6.5))-overlap(cap,cyl(1.6,(0,56.2,0),(0,1,0),6.5)))<1e-4)
 fan_sweep=cyl(35.57,(0,24.4646,0),(0,1,0),7.2850595848951);metal_sweep=cyl(6.11,(0,17.505,0),(0,1,0),28.7226595848951)
 sweep=t.boolean(BRepAlgoAPI_Fuse,fan_sweep,metal_sweep)
 gaps={'cap':t.distance(cap,sweep),'housing':t.distance(house,sweep)}
 check('complete rotation clears cone by5mm and housing by3mm',gaps['cap']>5 and gaps['housing']>3,clearance_mm=gaps)
 oldgap=t.distance(oldcap,metal_sweep);newgap=t.distance(cap,metal_sweep)
 check('metal-adapter tolerance space increased',newgap>oldgap+3,old_clearance_mm=oldgap,new_clearance_mm=newgap)
 conflicts=[]
 for target,label in [(cap,'cap'),(house,'housing')]:
  a,b=t.limits(target)
  for j,q in enumerate(ss):
   if q.IsSame(cap) or q.IsSame(house):continue
   lo,hi=t.limits(q)
   if any(hi[k]<a[k]-1e-5 or lo[k]>b[k]+1e-5 for k in range(3)):continue
   vol=overlap(target,q)
   if vol>1e-4:conflicts.append(dict(target=label,part=j,overlap_mm3=vol))
 check('cone and housing clear all45 other installed bodies',not conflicts,conflicts=conflicts)
 check('cone pilots and bearing seats have no penetration',overlap(cap,house)<1e-4)
 axes=[(0,44.5),(-44.5,0),(0,-44.5),(44.5,0)]
 roof=[];caproof=[];key=[];spin=[]
 for x,z in axes:
  ann=t.boolean(t.BRepAlgoAPI_Cut,cyl(3.4,(x,44.31,z),(0,1,0),2.68),cyl(1.9,(x,44.30,z),(0,1,0),2.70))
  roof.append(abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,ann,house))))
  ann2=t.boolean(t.BRepAlgoAPI_Cut,cyl(3.3,(x,48.01,z),(0,1,0),3.98),cyl(1.9,(x,48,z),(0,1,0),4))
  caproof.append(abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,ann2,cap))))
  probe=cyl(1.45,(x,55.501,z),(0,1,0),50)
  key.append(overlap(probe,cap)+overlap(probe,house))
  q=min(nuts,key=lambda q:(center(q)[0]-x)**2+(center(q)[2]-z)**2)
  tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(x,0,z),gp_Dir(0,1,0)),math.pi/6)
  spin.append(overlap(BRepBuilderAPI_Transform(q,tr,True).Shape(),house))
 check('2.7mm housing roof is solid around every bolt',max(roof)<1e-4,escaped_mm3=roof)
 check('4mm cone material remains over locating sockets',max(caproof)<1e-4,escaped_mm3=caproof)
 check('all four screw heads have straight key access',max(key)<1e-4,overlap_mm3=key)
 check('captured nuts cannot rotate30 degrees',min(spin)>.01,rotation_overlap_mm3=spin)
 check('full nut engagement and two-thread tip projection',all(abs(t.limits(q)[0][1]-40.5)<.001 for q in short),nut_engagement_mm=2.4,tip_projection_mm=.9,housing_roof_mm=2.7)
 # Verify pilot OD / female socket ID and local printed clearance bore radii.
 pilots=[];sockets=[]
 for name,target in [('pilot',house),('socket',cap)]:
  ex=TopExp_Explorer(target,TopAbs_FACE)
  while ex.More():
   a=BRepAdaptor_Surface(TopoDS.Face(ex.Current()))
   if a.GetType()==GeomAbs_Cylinder:
    c=a.Cylinder();pt=c.Axis().Location();rad=c.Radius()
    if abs(c.Axis().Direction().Y())>.99999 and abs(max(abs(pt.X()),abs(pt.Z()))-44.5)<.001:
     if name=='pilot' and abs(rad-3.2)<.001:pilots.append((round(pt.X(),3),round(pt.Z(),3)))
     if name=='socket' and abs(rad-3.4)<.001:sockets.append((round(pt.X(),3),round(pt.Z(),3)))
   ex.Next()
 check('four pilots and sockets give0.2mm radial and axial relief',len(set(pilots))==len(set(sockets))==4,pilot_axes=sorted(set(pilots)),socket_axes=sorted(set(sockets)),radial_relief_mm=.2,axial_relief_mm=.2)
 def faces_at(q,y):
  faces=[];ex=TopExp_Explorer(q,TopAbs_FACE)
  while ex.More():
   f=TopoDS.Face(ex.Current());a=BRepAdaptor_Surface(f);lo,hi=t.limits(f)
   if a.GetType()==GeomAbs_Plane and abs(a.Plane().Axis().Direction().Y())>.99999 and abs(lo[1]-y)<1e-5 and abs(hi[1]-y)<1e-5:faces.append(f)
   ex.Next()
  return faces
 def contact_area(a,b,y):
  area=0
  for fa in faces_at(a,y):
   for fb in faces_at(b,y):
    op=t.BRepAlgoAPI_Common(fa,fb);op.SetFuzzyValue(1e-5);op.Build();assert op.IsDone();area+=abs(t.area(op.Shape()))
  return area
 areas=[contact_area(q,house,44.3) for q in washers]
 check('four rear washers bear flat on pocket roofs',min(areas)>25,contact_mm2=areas)
 area=contact_area(cap,house,47)
 check('cone rests on four bearing seats, not on pilots',area>60,contact_area_mm2=area)
(r/'verification.json').write_text(json.dumps(checks,indent=2));raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
