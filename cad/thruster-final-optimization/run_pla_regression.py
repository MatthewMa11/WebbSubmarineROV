"""Retained mounting interfaces and enclosed wire route on the new assembly."""
import sys,runpy,json
from pathlib import Path
from verify_pla_revision import read,t,OLD

path=sys.argv[1];root=Path(__file__).resolve().parent
# The old reader only accepts 22 solids. The new reader preserves exactly the
# same six named mechanical bodies while allowing the 17 added hardware solids.
t.load=lambda p:read(p)[0]
sys.argv=[str(OLD/'verify_final_mounts.py'),path,str(root/'pla-mount-regression.json')]
runpy.run_path(str(OLD/'verify_final_mounts.py'),run_name='__main__')
p,_=read(path);checks=[]
def check(name,ok,**details):checks.append({'check':name,'pass':bool(ok),'details':details})
c=13.75;wire=t.cylinder(5,-45,37,c,-c)
block=t.volume(t.boolean(t.BRepAlgoAPI_Common,wire,p['nozzle']))
check('enclosed 10 mm wire passage remains unobstructed',block<1e-4,obstruction_mm3=block)
gap=t.distance(wire,p['stator']);check('wire route retains 0.5 mm minimum motor-base clearance',gap>.5,gap_mm=gap)
wall=t.boolean(t.BRepAlgoAPI_Cut,t.cylinder(8.999,-22,2,c,-c),t.cylinder(5.001,-22.001,2.002,c,-c))
missing=t.volume(t.boolean(t.BRepAlgoAPI_Cut,wall,p['nozzle']))
check('continuous nominal 4 mm wire sleeve remains intact',missing<1e-4,missing_material_mm3=missing)
headgaps=[]
for s in read(path)[1]:
    lo,hi=t.limits(s)
    if abs(lo[1]-7)<1e-5 and abs(hi[1]-18)<1e-5:headgaps.append(t.distance(s,p['cover']))
check('four propeller screw heads retain 2 mm cover clearance',len(headgaps)==4 and min(headgaps)>1.99,gaps_mm=headgaps)
(root/'pla-wire-regression.json').write_text(json.dumps({'file':path,'checks':checks},indent=2))
print(json.dumps({'passed':sum(c['pass'] for c in checks),'total':len(checks),'failed':[c for c in checks if not c['pass']]},indent=2))
assert all(c['pass'] for c in checks)
