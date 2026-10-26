"""Independent continuous-clearance and preserved-interface checks on native STEP."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'thruster-final-optimization'))
from verify_pla_revision import read,t,cylinder,fixtures
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

def quick_limits(s):
    box=Bnd_Box();BRepBndLib.Add_s(s,box,False)
    return [[p.X(),p.Y(),p.Z()] for p in (box.CornerMin(),box.CornerMax())]
t.limits=quick_limits

def main():
    r=Path(__file__).resolve().parent
    p,h=read(sys.argv[1]);old,oh=read(r.parent/'thruster-final-optimization/Thruster-A2212-PLA-complete.step')
    checks=[]
    def check(name,ok,**detail):
        checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
    def common(a,b):return t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b))
    check('native assembly retains six mechanical bodies and 33 fasteners',len(h)==33,solids=6+len(h))
    for name in ('cover','rotor','stator'):
        dv=abs(t.volume(p[name])-t.volume(old[name]));da=abs(t.area(p[name])-t.area(old[name]))
        delta=max(abs(x-y) for aa,bb in zip(t.limits(p[name]),t.limits(old[name])) for x,y in zip(aa,bb))
        check(name+' geometry and placement unchanged',dv<.01 and da<.01 and delta<.001,volume_difference_mm3=dv,area_difference_mm2=da,bounds_difference_mm=delta)
    # Neither the tip trim nor the ring should change any motor-coupling feature.
    hub=cylinder(18.01,(0,-3.01,0),(0,1,0),22.02)
    a=t.boolean(t.BRepAlgoAPI_Common,p['propeller'],hub);b=t.boolean(t.BRepAlgoAPI_Common,old['propeller'],hub)
    diff=abs(t.volume(a)-t.volume(b));area=abs(t.area(a)-t.area(b))
    check('propeller hub, drive keys and all four screw seats unchanged',diff<.01 and area<.01,hub_volume_difference_mm3=diff,hub_area_difference_mm2=area)
    axes=((9,0),(-9,0),(0,9),(0,-9));blocked=[]
    for x,z in axes:blocked.append(common(p['insert'],cylinder(1.299,(x,5.599,z),(0,1,0),4.402)))
    check('all four spacer pilot axes stay at the original 18 mm pitch circle',max(blocked)<1e-4,blocked_probe_volumes_mm3=blocked)
    sweep=cylinder(35.5001,(0,-3.0001,0),(0,1,0),22.0002)
    outside=t.volume(t.boolean(t.BRepAlgoAPI_Cut,p['propeller'],sweep))
    check('continuous rotation envelope encloses the complete native propeller',outside<1e-4,outside_volume_mm3=outside)
    gaps={n:t.distance(sweep,p[n]) for n in ('nozzle','cover','stator')}
    # The reference base's forward face is Y=-6, not Y=-8 (the blind-hole
    # bottom). The blade envelope starts at Y=-3, giving 3 mm base clearance.
    check('continuous full-turn blade envelope clears all fixed mechanical bodies',gaps['nozzle']>2.4 and gaps['cover']>.99 and gaps['stator']>2.9,gaps_mm=gaps)
    expanded=cylinder(36.724,(0,-3.6,0),(0,1,0),23.2)
    gap=t.distance(expanded,p['nozzle'])
    check('blade error envelope retains clearance after 0.3 mm inward duct error',gap-.3>.75,
          gap_before_duct_error_mm=gap,gap_after_duct_error_mm=gap-.3,
          assumptions='0.5 mm eccentricity + 0.2 mm blade growth + 1 degree tilt over 30 mm; not measured printer tolerances')
    window=t.boolean(t.BRepAlgoAPI_Cut,cylinder(27.9,(0,-27,0),(0,1,0),2),cylinder(15.6,(0,-27.1,0),(0,1,0),2.2))
    overlap=common(window,p['nozzle'])
    check('continuous 360 degree annular wire window is unobstructed',overlap<1e-4,obstruction_volume_mm3=overlap,radial_window_mm=[15.6,27.9],axial_window_mm=[-27,-25])
    rim=t.boolean(t.BRepAlgoAPI_Cut,cylinder(32,(0,-27,0),(0,1,0),2),cylinder(29,(0,-27.1,0),(0,1,0),2.2))
    missing=t.volume(t.boolean(t.BRepAlgoAPI_Cut,rim,p['nozzle']))
    check('continuous outer wire ring is solid through every angle',missing<1e-4,missing_material_mm3=missing)
    fit={name:common(s,p['nozzle']) for name,s in fixtures()}
    check('existing motor and cover hardware still clears the nozzle',max(fit.values())<1e-4,overlap_mm3=fit)
    native_geometry=[]
    for solids in (h,oh):
        native_geometry.append(sorted([tuple(round(q,5) for pair in t.limits(s) for q in pair)+(round(t.volume(s),4),round(t.area(s),4)) for s in solids]))
    check('all 33 hardware geometries and positions are retained',native_geometry[0]==native_geometry[1])
    (r/'inherited-native-checks.json').write_text(json.dumps(checks,indent=2))
    return 0 if all(x['passed'] for x in checks) else 1
if __name__=='__main__':raise SystemExit(main())
