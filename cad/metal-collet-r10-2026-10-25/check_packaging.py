"""Read-only packaging study; no source CAD or print files are modified."""
from pathlib import Path
import json

root=Path(__file__).resolve().parent
v=root.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)}
exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t']; cylinder=ns['cylinder']
parts=ns['solids'](root.parent/'sketch-layout-r9-2026-10-25/Thruster-R9-forward-fan.step')
cover=next(s for s in parts if t.limits(s)[1][0]-t.limits(s)[0][0]>80 and t.limits(s)[0][1]>10)
# CPA-317-N: manufacturer/supplier's own product documentation states
# 3.17 mm input, M6x1 stud, 25 mm overall and 17 mm usable stud.
# Rear datum 16.3 is a STUDY choice, 0.3 mm ahead of the reference pilot.
stud=cylinder(3,(0,24.3,0),(0,1,0),17)
collision=t.boolean(t.BRepAlgoAPI_Common,cover,stud)
report={
 'status':'layout conflict; not a print-ready revision',
 'adapter':'Innov8tive Designs CPA-317-N',
 'source':'https://innov8tivedesigns.com/collet-style-prop-adapter-with-hex-nut-for-3-17mm-motor-shafts.html',
 'published':{'motor_shaft_mm':3.17,'prop_stud_mm':6,'thread':'M6x1.0','overall_length_mm':25,'usable_stud_mm':17,'backplate_and_washer_diameter_mm':15.5,'maximum_hub_thickness_mm':10.5,'nut_wrench_mm':10},
 'study_assumptions':{'adapter_rear_y_mm':16.3,'stud_start_y_mm':24.3,'stud_end_y_mm':41.3,'hub_thickness_mm':6.5},
 'stud_intersection_with_unchanged_cap_mm3':abs(t.volume(collision)),
 'intersection_bounds_mm':t.limits(collision),
 'current_cap_bounds_mm':t.limits(cover),
 'limitations':['Product page is dimensional documentation, not manufacturer CAD.','Actual collet engagement depth and taper must be checked on purchased adapter.','Moving the cap requires additional duct/joint design; not authorized by this study.']
}
root.mkdir(parents=True,exist_ok=True)
(root/'packaging-study.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
