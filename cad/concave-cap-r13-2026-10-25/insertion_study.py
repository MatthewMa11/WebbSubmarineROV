from pathlib import Path
import json
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py';n={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],n)
t=n['t'];cyl=n['cylinder'];ss=n['solids'](r/'Thruster-R13-concave-cap.step')
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
house=None;moving=[];hw=[]
for s in ss:
 lo,hi=t.limits(s);dx,dy,dz=[b-a for a,b in zip(lo,hi)]
 if dx>100 and lo[1]<-29:house=s
 elif dx>90 and lo[1]>40:continue
 elif (dz>70 and dx<50) or (27<dx<29 and 40<dy<41) or (7.8<dx<8.1 and 22<dy<23) or (12<dx<12.2 and 6<dy<8) or (11<dx<12 and 14<dy<15 and lo[1]>30):moving.append(s)
 else:hw.append(s)
assert house and len(moving)==5 and len(hw)==40
# These cylinders enclose every axial position from installation to forward
# withdrawal: exact full-length radial envelopes plus small print allowance.
core=cyl(13.92,(0,-11,0),(0,1,0),141)
rear_pilot=cyl(3.84,(0,-11.28,0),(0,1,0),141.28)
rear_axle=cyl(1.58,(0,-13.32,0),(0,1,0),143.32)
blade=cyl(35.57,(0,24.4646,0),(0,1,0),105.5354)
corridor=core
for s in [rear_pilot,rear_axle,blade]:corridor=t.boolean(BRepAlgoAPI_Fuse,corridor,s)
escaped=[abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,s,corridor))) for s in moving]
remaining=[]
for s in hw:
 lo,hi=t.limits(s);dy=hi[1]-lo[1];center=max(abs((hi[k]+lo[k])/2) for k in [0,2])
 remove=(abs(dy-15)<.01 and abs(lo[1]-40.5)<.001) or (lo[1]>51 and dy<1) or (center<13 and lo[1]<-16.49 and hi[1]<-8)
 if not remove:remaining.append(s)
assert len(remaining)==20,len(remaining)
contacts=[abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,corridor,s))) for s in [house]+remaining]
report=dict(check='continuous axial motor-fan insertion with cap and installation fasteners removed',passed=max(escaped)<1e-4 and max(contacts)<1e-4,moving_parts=5,retained_fasteners=len(remaining),escaped_mm3=escaped,housing_overlap_mm3=contacts[0],largest_retained_fastener_overlap_mm3=max(contacts[1:]),envelope_radii_mm=dict(motor=13.92,rear_pilot=3.84,rear_axle=1.58,fan=35.57))
(r/'insertion-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
raise SystemExit(0 if report['passed'] else 1)
