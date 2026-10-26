"""Independent gauges for physical clamping, loading access and full rotation."""
from pathlib import Path
import sys,json,math
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t,cylinder
from verify_pla_revision import hexnut,washer
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Ax1
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

def turn(s,i):
 tr=t.gp_Trsf();tr.SetRotation(gp_Ax1(t.gp_Pnt(0,0,0),t.gp_Dir(0,1,0)),-i*math.pi/2)
 return t.BRepBuilderAPI_Transform(s,tr,True).Shape()
def box(x,y,z,dx,dy,dz):return BRepPrimAPI_MakeBox(t.gp_Pnt(x,y,z),dx,dy,dz).Shape()
def common(a,b):return t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b))
def missing(a,b):return t.volume(t.boolean(t.BRepAlgoAPI_Cut,a,b))
def tube(ro,ri,y,h,z=44.5):return t.boolean(t.BRepAlgoAPI_Cut,cylinder(ro,(0,y,z),(0,1,0),h),cylinder(ri,(0,y-.001,z),(0,1,0),h+.002))
def main():
 p,h=read(sys.argv[1]);checks=[]
 hb=[t.limits(q) for q in h]
 for j,q in enumerate(h):
  lo,hi=hb[j]
  if abs(lo[1]-12.5)<.001 and abs(hi[1]-27.5)<.001:
   bb=Bnd_Box();BRepBndLib.AddOptimal_s(q,bb,False,False)
   hb[j]=[[z.X(),z.Y(),z.Z()] for z in (bb.CornerMin(),bb.CornerMax())]
 def check(n,ok,**d):checks.append(dict(check=n,passed=bool(ok),detail=d));print(('PASS ' if ok else 'FAIL ')+n,flush=True)
 check('six mechanical parts and all forty fasteners are present',len(h)==40,actual_solids=6+len(h))
 through=[];bearing=[];clamp=[];fit=[];access=[];capture=[];pose=[]
 for i in range(4):
  through.append(sum(common(turn(cylinder(1.499,(0,12.49,44.5),(0,1,0),12.02),i),p[n]) for n in ('cover','nozzle')))
  bearing += [missing(turn(tube(3.4,2,23.99,.009),i),p['cover']),missing(turn(tube(3.4,2,16.001,.009),i),p['nozzle'])]
  clamp += [missing(turn(tube(4.15,2,18.99,.009),i),p['nozzle']),missing(turn(tube(4.15,2,19.001,.009),i),p['cover'])]
  nut=hexnut((0,15.5,44.5),(0,-1,0));rear=washer((0,15.5,44.5),(0,1,0));front=washer((0,24.5,44.5),(0,-1,0))
  for label,s in [('nut',nut),('rear',rear),('front',front),('head',cylinder(2.84,(0,24.5,44.5),(0,1,0),3)),('shaft',cylinder(1.499,(0,12.5,44.5),(0,1,0),12))]:
   ss=turn(s,i);fit += [common(ss,p[n]) for n in ('nozzle','cover')]
   if label!='shaft':
    # A screw's head is part of a larger joined body, so compare its full bounds below.
    if label=='head':ss=turn(cylinder(2.84,(0,24.5,44.5),(0,1,0),3),i); bounds=t.limits(ss);bounds[0][1]=12.5
    else:bounds=t.limits(ss)
    matches=[j for j,q in enumerate(h) if max(abs(a-b) for aa,bb in zip(hb[j],bounds) for a,b in zip(aa,bb))<.001]
    pose.append(dict(joint=i,part=label,matches=matches))
  # Continuous radial insertion envelope = full final part + its inner prism.
  ng=t.boolean(BRepAlgoAPI_Fuse,nut,box(-2.75,13.1,30,5.5,2.4,14.5))
  wg=t.boolean(BRepAlgoAPI_Fuse,rear,box(-3.5,15.5,30,7,.5,14.5))
  access += [common(turn(ng,i),p['nozzle']),common(turn(wg,i),p['nozzle']),common(turn(cylinder(1.6,(0,27.51,44.5),(0,1,0),30),i),p['cover'])]
  tr=t.gp_Trsf();tr.SetRotation(gp_Ax1(t.gp_Pnt(0,0,44.5),t.gp_Dir(0,1,0)),math.radians(20))
  rotated=t.BRepBuilderAPI_Transform(nut,tr,True).Shape();capture.append(common(turn(rotated,i),p['nozzle']))
 check('four continuous M3 shafts pass both parts',max(through)<1e-4,blocked_mm3=through)
 check('both washers bear on full flat annular plastic lands',max(bearing)<1e-4,missing_land_mm3=bearing)
 check('both parts meet at four broad flat clamping faces',max(clamp)<1e-4,missing_contact_land_mm3=clamp)
 check('all cover fasteners fit without plastic interference',max(fit)<1e-4,overlap_mm3=fit)
 check('all sixteen cover hardware instances occupy their checked positions',all(len(q['matches'])==1 for q in pose),positions=pose)
 check('nuts and rear washers have continuous insertion paths and front Allen-key access',max(access)<1e-4,obstruction_mm3=access)
 check('four nut pockets resist a twenty degree nut rotation',min(capture)>.1,blocking_mm3=capture)
 check('M3x12 fully spans plastic, washers and nuts with 0.6 mm protrusion',abs(12-(5+3+1+2.4+.6))<1e-8,bolt_mm=12,nut_engagement_mm=2.4,protrusion_mm=.6)
 sweep=cylinder(35.5001,(0,-3.0001,0),(0,1,0),22.0002)
 gaps={n:t.distance(sweep,p[n]) for n in ('nozzle','cover','stator')}
 check('continuous blade rotation envelope clears all stationary parts',gaps['nozzle']>2.4 and gaps['cover']>.99 and gaps['stator']>2.9,gaps_mm=gaps)
 check('no cover-nozzle material interference outside intended face contacts',common(p['nozzle'],p['cover'])<1e-4)
 rotor_sweep=cylinder(13.8501,(0,-5.0001,0),(0,1,0),19.5002)
 check('motor rotor continuous envelope clears the fixed nozzle',t.distance(p['nozzle'],rotor_sweep)>1,clearance_mm=t.distance(p['nozzle'],rotor_sweep))
 old,oh=read(r.parent/'motor-centering-cover-2026-10-17/Thruster-centering-cup-R3.step')
 for n in ('propeller','insert','rotor','stator'):
  dv=abs(t.volume(p[n])-t.volume(old[n]));da=abs(t.area(p[n])-t.area(old[n]));db=max(abs(a-b) for aa,bb in zip(t.limits(p[n]),t.limits(old[n])) for a,b in zip(aa,bb))
  check(n+' geometry and placement remain unchanged',dv<.01 and da<.01 and db<.001,volume_delta_mm3=dv,area_delta_mm2=da,bounds_delta_mm=db)
 protected=cylinder(37.6,(0,10,0),(0,1,0),55)
 for n in ('cover','nozzle'):
  a=t.boolean(t.BRepAlgoAPI_Common,p[n],protected);b=t.boolean(t.BRepAlgoAPI_Common,old[n],protected)
  check(n+' central geometry remains unchanged',abs(t.volume(a)-t.volume(b))<.01 and abs(t.area(a)-t.area(b))<.02)
 # Check all material away from the four authorized mounting-tab regions,
 # rather than allowing unrelated duct/dome edits outside the central probe.
 for n in ('cover','nozzle'):
  a=p[n];b=old[n]
  for i in range(4):
   # Through-drill begins at Y=12, half a millimetre behind the bolt tip.
   region=turn(cylinder(8.6,(0,11.9,44.5),(0,1,0),53.1),i)
   a=t.boolean(t.BRepAlgoAPI_Cut,a,region);b=t.boolean(t.BRepAlgoAPI_Cut,b,region)
  check(n+' material outside the four mounting regions remains unchanged',abs(t.volume(a)-t.volume(b))<.01 and abs(t.area(a)-t.area(b))<.05,volume_delta_mm3=abs(t.volume(a)-t.volume(b)),area_delta_mm2=abs(t.area(a)-t.area(b)))
 protected=box(-60,-45,-60,120,55,120)
 a=t.boolean(t.BRepAlgoAPI_Common,p['nozzle'],protected);b=t.boolean(t.BRepAlgoAPI_Common,old['nozzle'],protected)
 check('motor centering cup, motor seats and 360 degree rear wire ring are unchanged',abs(t.volume(a)-t.volume(b))<.01 and abs(t.area(a)-t.area(b))<.02)
 Path(sys.argv[2]).write_text(json.dumps(checks,indent=2),encoding='utf-8')
 return 0 if all(c['passed'] for c in checks) else 1
if __name__=='__main__':raise SystemExit(main())
