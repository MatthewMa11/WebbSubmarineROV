from pathlib import Path
import math,json
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];cyl=ns['cylinder'];ss=ns['solids'](r/'SOURCE-Motor-assembly.step')
old=ns['solids'](r.parent/'metal-collet-r10-2026-10-25/Thruster-R10-metal-collet.step')
frame=next(s for s in old if t.limits(s)[0][1]<-29 and t.limits(s)[1][0]-t.limits(s)[0][0]>90)
cap=next(s for s in old if t.limits(s)[0][1]>40 and t.limits(s)[1][0]-t.limits(s)[0][0]>90)
from OCP.gp import gp_Trsf,gp_Vec,gp_Ax1,gp_Pnt,gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
def pose(s,dy=15.67):
 tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,1,0)),math.pi/4)
 tr.SetTranslationPart(gp_Vec(0,dy,0));return BRepBuilderAPI_Transform(s,tr,True).Shape()
def common(a,b):return t.boolean(t.BRepAlgoAPI_Common,a,b)
def info(q):
 vol=abs(t.volume(q))
 return {'volume_mm3':vol,'bounds_mm':t.limits(q) if vol>1e-7 else None}
stud=common(ss[1],cyl(20,(0,8.90,0),(0,1,0),14.4))
print('thread region',info(stud),flush=True)
report={'pose':{'rotate_y_deg':45,'translate_y_mm':15.67},'stud_region_source':info(stud),'contacts':{}}
aligned={n:pose(ss[i]) for n,i in [('mount',0),('collet',1),('nut',2),('motor',4),('collar',7)]}
for an,bn in [('motor','collet'),('collet','collar'),('collet','nut')]:
 a=common(aligned[an],aligned[bn]);report['contacts'][an+' / '+bn]=info(a);print(an,bn,info(a),flush=True)
for an in ['motor','mount','collet','collar','nut']:
 a=common(aligned[an],frame);report['contacts'][an+' / frame']=info(a);print(an,'frame',info(a),flush=True)
for an in ['nut','collet','collar']:
 report['contacts'][an+' / cap']=info(common(aligned[an],cap))
print('cap gaps',{n:t.distance(aligned[n],cap) for n in ['nut','collet','collar']},flush=True)
(r/'source-fit-study.json').write_text(json.dumps(report,indent=2))
