from pathlib import Path
f=Path(__file__).resolve().parent/'verify_r7.py'
exec(f.read_text().split("p,rings,h=read(")[0])
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Ax1,gp_Dir,gp_Pnt,gp_Vec
p,rr,h=read(r/'Thruster-R7-bolt-free.step');results=[]
def moved(s,advance):
 tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,1,0)),advance*math.pi)
 tr.SetTranslationPart(gp_Vec(0,advance,0))
 return BRepBuilderAPI_Transform(s,tr,True).Shape()
for n,q in enumerate(rr):
 qt=moved(q,.15);v=t.volume(t.boolean(t.BRepAlgoAPI_Common,qt,p['propeller']))
 results.append(dict(check='ring '+str(n)+' follows 2 mm pitch for further 0.15 mm free travel',passed=v<1e-4,overlap_mm3=v))
 print(results[-1],flush=True)
outer=t.boolean(t.BRepAlgoAPI_Cut,cylinder(23,(0,-5.5,0),(0,1,0),8.85),cylinder(21.05,(0,-5.6,0),(0,1,0),9.05))
gap=t.distance(outer,p['propeller']);v=t.volume(t.boolean(t.BRepAlgoAPI_Common,outer,p['propeller']))
results.append(dict(check='ring outer envelope clears blade roots through estimated clamp travel',passed=v<1e-4 and gap>.35,overlap_mm3=v,gap_mm=gap,maximum_front_y_mm=3.35))
main=rr[1];front=t.limits(main)[1][1];estimated_advance=(.25-.3*.5+.15)/.3
results.append(dict(check='estimated bell contact occurs before the travel stop',passed=front+estimated_advance<3.6,estimated_additional_advance_mm=estimated_advance,estimated_front_y_mm=front+estimated_advance,stop_y_mm=3.6,warning='Geometric estimate; elastic grip and actual motor diameter need physical testing'))
print(results[-2:],flush=True)
(r/'thread-travel.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if all(q['passed'] for q in results) else 1)
