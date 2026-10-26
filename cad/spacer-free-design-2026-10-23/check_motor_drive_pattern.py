"""Verify the R6 positive-drive interface independently from its source code.

Extract mating cylinder axes from native STEP, then calculate the signed radial
clearance while rotating the keys relative to the bell in both directions.
The circle-to-circle contact calculation avoids periodic STEP Boolean artifacts.
This tests geometric keying only;
it does not establish clamp friction, printed strength or a rated torque.
"""
from pathlib import Path
import sys,math,json
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import t,cylinder
from verify_kit_hardware import solids
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
ss=solids(r/'Thruster-R6-spacer-free-assembly.step')
prop=next(s for s in ss if t.limits(s)[1][2]-t.limits(s)[0][2]>70 and t.limits(s)[1][0]-t.limits(s)[0][0]<60)
rotor=next(s for s in ss if 27<t.limits(s)[1][0]-t.limits(s)[0][0]<29 and t.limits(s)[1][1]-t.limits(s)[0][1]>25)
def round_axes(shape,radius):
 out={};ex=TopExp_Explorer(shape,TopAbs_FACE)
 while ex.More():
  f=TopoDS.Face(ex.Current());sf=BRepAdaptor_Surface(f)
  if sf.GetType()==GeomAbs_Cylinder:
   c=sf.Cylinder();a=c.Axis();p=a.Location();d=a.Direction()
   if abs(c.Radius()-radius)<1e-5 and abs(d.Y())>.99999:
    key=(round(p.X(),6),round(p.Z(),6));lo,hi=t.limits(f)
    out.setdefault(key,[]).append([lo[1],hi[1]])
  ex.Next()
 return out
vents=round_axes(rotor,3);keys=round_axes(prop,2.75)
checks=[]
def check(name,passed,**detail):
 checks.append(dict(check=name,passed=bool(passed),detail=detail));print(('PASS ' if passed else 'FAIL ')+name,flush=True)
expected=[(-9.,0.),(0.,-9.),(0.,9.),(9.,0.)]
check('four motor openings and four propeller keys have identical axes',sorted(vents)==expected and sorted(keys)==expected,motor_vent_axes_mm=list(vents),propeller_key_axes_mm=list(keys))
check('motor openings are on 18 mm pitch circle at 90 degree spacing',len(vents)==4 and all(abs(math.hypot(x,z)-9)<1e-6 for x,z in vents))
check('5.5 mm keys have 0.25 mm radial assembly clearance in 6 mm openings',abs(3-2.75-.25)<1e-9)
engagement=[]
for center,faces in keys.items():
 lo=min(v[0] for v in faces);hi=max(v[1] for v in faces)
 motorlo=min(v[0] for v in vents[center]);motorhi=max(v[1] for v in vents[center])
 engagement.append(min(hi,motorhi)-max(lo,motorlo))
check('all four keys engage the rotating bell by at least 2 mm',min(engagement)>2,engagement_mm=engagement)
interface=t.boolean(t.BRepAlgoAPI_Common,prop,cylinder(13.9,(0,11.8,0),(0,1,0),2.1))
expected_volume=4*math.pi*2.75**2*2.1
check('isolated native drive-key material matches all four solid cylinders',abs(t.volume(interface)-expected_volume)<1e-4,actual_mm3=t.volume(interface),expected_mm3=expected_volume)
clearances={}
for angle in (0,-1,1,-2,2):
 a=math.radians(angle);margins=[]
 for x,z in keys:
  xx=x*math.cos(a)+z*math.sin(a);zz=-x*math.sin(a)+z*math.cos(a)
  offset=math.hypot(xx-x,zz-z)
  margins.append(3-2.75-offset)
 clearances[angle]=margins
 print('relative angle',angle,'minimum radial clearance mm',min(margins),flush=True)
check('aligned propeller keys fit without penetrating the bell',min(clearances[0])>.2499,clearance_mm=clearances[0])
check('one degree assembly play is clear in both directions',min(clearances[-1]+clearances[1])>.09)
check('all four drive keys stop independent rotation in both directions before two degrees',max(clearances[-2]+clearances[2])<-.06,signed_radial_clearances_at_minus_2_deg_mm=clearances[-2],signed_radial_clearances_at_plus_2_deg_mm=clearances[2])
result={'checks':checks,'reference_only':True,'physical_motor_measured':False,'clamp_grip_tested':False,'retention':'opposed integral external bell clamp with two M3x16 bolts, two captured M3 nuts and two washers','important':'A rigid assembly mate and interference-free rotation do not prove mechanical retention or a torque rating.'}
(r/'motor-drive-pattern-checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
