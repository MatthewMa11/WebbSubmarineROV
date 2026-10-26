"""Independent checks of the fixed motor centering cup in the native assembly."""
from pathlib import Path
import sys,json,math
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parent/'print-revision-2026-10-17'))
from verify_native_revision import read,t,cylinder
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Ax1

def main():
    p,h=read(sys.argv[1]);old,oh=read(r.parent/'print-revision-2026-10-17/Thruster-physical-fit-R2.step');checks=[]
    def check(name,ok,**detail):
        checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
    check('the centering cover is integrated into the existing 39-body assembly',len(h)==33)
    unchanged={}
    for n in ('propeller','insert','rotor','stator','cover'):
        unchanged[n]=dict(volume_difference_mm3=abs(t.volume(p[n])-t.volume(old[n])),area_difference_mm2=abs(t.area(p[n])-t.area(old[n])),
            bounds_difference_mm=max(abs(x-y) for aa,bb in zip(t.limits(p[n]),t.limits(old[n])) for x,y in zip(aa,bb)))
    check('all rotating components, motor and gray cover retain their R2 geometry and position',
          all(q['volume_difference_mm3']<.01 and q['area_difference_mm2']<.01 and q['bounds_difference_mm']<.001 for q in unchanged.values()),comparisons=unchanged)
    clip=cylinder(19,(0,-10.9,0),(0,1,0),4.7)
    cup=t.boolean(t.BRepAlgoAPI_Common,p['nozzle'],clip)
    before=t.volume(t.boolean(t.BRepAlgoAPI_Common,old['nozzle'],clip))
    check('a new fixed cup surrounds the motor base above the original seat',t.volume(cup)>100 and before<1e-4,new_material_mm3=t.volume(cup),old_material_mm3=before)
    gap=t.distance(cup,p['stator'])
    check('motor-base locator keeps at least 0.35 mm reference slip clearance',gap>.35,minimum_clearance_mm=gap,nominal_locator_diameter_mm=28.5)
    moving={n:t.distance(cup,p[n]) for n in ('propeller','rotor','insert')}
    check('the fixed cup is clear of all rotating mechanical parts',min(moving.values())>1,clearances_mm=moving)
    rotor_sweep=cylinder(13.8501,(0,-5.0001,0),(0,1,0),19.5002)
    rotor_gap=t.distance(p['nozzle'],rotor_sweep)
    check('the new stationary cup clears the motor bell continuous rotation envelope',rotor_gap>1,minimum_gap_mm=rotor_gap)
    wires=[]
    for i in range(4):
        box=BRepPrimAPI_MakeBox(t.gp_Pnt(14,-9.3,-4.5),7,2.6,9).Shape()
        turn=t.gp_Trsf();turn.SetRotation(gp_Ax1(t.gp_Pnt(0,0,0),t.gp_Dir(0,1,0)),-math.radians(45+90*i))
        gauge=t.BRepBuilderAPI_Transform(box,turn,True).Shape()
        wires.append(t.volume(t.boolean(t.BRepAlgoAPI_Common,p['nozzle'],gauge)))
    check('all four rounded wire slots clear a full 9 by 2.6 mm bundle gauge',max(wires)<1e-4,obstruction_volumes_mm3=wires)
    snapshots=[]
    for hardware in (h,oh):
        snapshots.append(sorted(tuple(round(v,5) for pair in t.limits(s) for v in pair)+(round(t.volume(s),4),round(t.area(s),4)) for s in hardware))
    check('no fastener size or position changed',snapshots[0]==snapshots[1],hardware_count=len(h))
    (r/'cup-native-checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    return 0 if all(q['passed'] for q in checks) else 1
if __name__=='__main__':raise SystemExit(main())
