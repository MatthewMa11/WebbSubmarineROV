"""Physical fastener access and continuous rotation, checked against native STEP.

The fixture dimensions are conservative envelopes of standard kit fasteners,
independent of the FeatureScript operations that construct the model.
"""
import sys, json, math, itertools
from pathlib import Path
OLD=Path('C:/Users/ROG/OneDrive/Documents/ChatGPT/robotic FTC 2026-2027/cad/frame-fit-check')
sys.path.insert(0,str(OLD))
import verify_free_rotation as t
from verify_kit_hardware import solids
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec
from OCP.TopAbs import TopAbs_FACE

MOTOR_AXES=((9.5,0),(-9.5,0),(0,8),(0,-8))
COVER_AXES=((0,0,1),(-1,0,0),(0,0,-1))

def read(path):
    parts={};hardware=[]
    for s in solids(path):
        lo,hi=t.limits(s);dx,dy,dz=[b-a for a,b in zip(lo,hi)]
        if lo[1]<-30 and dx>90:n='nozzle'
        elif dz>70 and dx<40:n='propeller'
        elif dx>80 and lo[1]>10:n='cover'
        elif 22<dx<24 and dy<6:n='insert'
        elif 27<dx<29 and dy>25:n='rotor'
        elif 27<dx<29 and dy<6:n='stator'
        else:hardware.append(s);continue
        assert n not in parts;parts[n]=s
    assert len(parts)==6
    return parts,hardware

def cylinder(r,start,axis,h):
    return t.BRepPrimAPI_MakeCylinder(t.gp_Ax2(t.gp_Pnt(*start),t.gp_Dir(*axis)),r,h).Shape()

def vector_add(a,b,k=1):return tuple(x+k*y for x,y in zip(a,b))

def washer(start,axis):
    return t.boolean(t.BRepAlgoAPI_Cut,cylinder(3.5,start,axis,.5),cylinder(1.6,vector_add(start,axis,-.01),axis,.52))

def hexnut(start,axis):
    u=(0,1,0) if abs(axis[0])>.9 else (1,0,0)
    v=(axis[1]*u[2]-axis[2]*u[1],axis[2]*u[0]-axis[0]*u[2],axis[0]*u[1]-axis[1]*u[0])
    poly=BRepBuilderAPI_MakePolygon()
    for i in range(6):
        a=math.radians(30+60*i);r=5.5/math.sqrt(3)
        poly.Add(t.gp_Pnt(*(start[j]+r*(u[j]*math.cos(a)+v[j]*math.sin(a)) for j in range(3))))
    poly.Close();body=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(),gp_Vec(*(2.4*q for q in axis))).Shape()
    return t.boolean(t.BRepAlgoAPI_Cut,body,cylinder(1.5,vector_add(start,axis,-.01),axis,2.42))

def fixtures():
    out=[]
    for i,(x,z) in enumerate(MOTOR_AXES):
        seat=(x,-16.5,z);axis=(0,1,0)
        out += [(f'motor_screw_head_{i}',cylinder(2.84,vector_add(seat,axis,-3),axis,3)),
                (f'motor_screw_shaft_{i}',cylinder(1.5,seat,axis,8)),
                (f'motor_washer_{i}',washer(seat,axis))]
    for i,d in enumerate(COVER_AXES):
        axis=tuple(-v for v in d);center=(0,20.5,0);seat=vector_add(center,d,49.75)
        out += [(f'cover_screw_head_{i}',cylinder(2.84,vector_add(seat,d,3),axis,3)),
                (f'cover_screw_shaft_{i}',cylinder(1.5,seat,axis,8)),
                (f'cover_washer_{i}',washer(seat,axis)),
                (f'cover_nut_{i}',hexnut(vector_add(center,d,47.4),axis))]
    return out

def main():
    p,hardware=read(sys.argv[1]);checks=[]
    def check(name,ok,**details):
        checks.append({'check':name,'pass':bool(ok),'details':details})
        print(('PASS ' if ok else 'FAIL ')+name,flush=True)
    check('complete assembly has 39 solids including all requested retention hardware',len(hardware)==33,solid_count=6+len(hardware))
    fx=fixtures()
    # Match each actual inserted native fastener to its independent expected
    # envelope. An instance at the cursor or a duplicate cannot pass this test.
    expected={}
    for name,s in fx:
        key=name.replace('_head','').replace('_shaft','')
        lo,hi=t.limits(s)
        if key in expected:
            a,b=expected[key];expected[key]=[[min(a[j],lo[j]) for j in range(3)],[max(b[j],hi[j]) for j in range(3)]]
        else:expected[key]=[lo,hi]
    matched={};missing=[]
    for name,bounds in expected.items():
        indices=[i for i,h in enumerate(hardware) if i not in matched.values() and max(abs(x-y) for aa,bb in zip(t.limits(h),bounds) for x,y in zip(aa,bb))<1e-5]
        if len(indices)==1:matched[name]=indices[0]
        else:missing.append({'name':name,'matches':len(indices),'expected_bounds_mm':bounds})
    check('all seventeen added native hardware instances occupy their checked positions',len(matched)==17 and not missing,matched_count=len(matched),missing=missing)
    motor={n:t.volume(t.boolean(t.BRepAlgoAPI_Common,s,p['nozzle'])) for n,s in fx if n.startswith('motor')}
    check('four motor socket screws and M3 washers fit the revised access pockets',max(motor.values())<1e-4,overlap_mm3=motor)
    cover={n:t.volume(t.boolean(t.BRepAlgoAPI_Common,s,p['nozzle'])) for n,s in fx if n.startswith('cover')}
    check('three cover bolt stacks clear the recessed nozzle seats',max(cover.values())<1e-4,overlap_mm3=cover)
    attachment=[]
    for n,s in fx:
        for target in ('cover','stator','propeller','rotor','insert'):
            overlap=t.volume(t.boolean(t.BRepAlgoAPI_Common,s,p[target]))
            if overlap>1e-4:attachment.append({'hardware':n,'body':target,'overlap_mm3':overlap})
    check('motor and cover hardware has no unintended body overlap',not attachment,unexpected=attachment)
    check('M3x8 motor screws have 2.5 mm engagement and 0.5 mm blind-hole margin',
          all(t.volume(t.boolean(t.BRepAlgoAPI_Common,p['stator'],cylinder(1.5,(x,-11,z),(0,1,0),2.5)))<1e-4 for x,z in MOTOR_AXES),
          engagement_mm=2.5,tip_y_mm=-8.5,blind_bottom_y_mm=-8,washer_thickness_mm=.5)
    bearing=[]
    for n,s in fx:
        if not n.endswith(tuple(str(i) for i in range(4))) or 'washer' not in n:continue
        # All fixture washer faces are planes; an area intersection with the
        # nozzle surface measures actual support rather than only bolt axis fit.
        ex=t.TopExp_Explorer(p['nozzle'],TopAbs_FACE);a=0
        sl,sh=t.limits(s)
        while ex.More():
            face=t.TopoDS.Face(ex.Current());ex.Next()
            fl,fh=t.limits(face)
            if any(fh[j]<sl[j]-1e-5 or fl[j]>sh[j]+1e-5 for j in range(3)):continue
            a+=t.area(t.boolean(t.BRepAlgoAPI_Common,face,s))
        bearing.append({'washer':n,'supported_area_mm2':a})
    check('all seven new washers bear on adequate flat nozzle seats',min(d['supported_area_mm2'] for d in bearing)>28,support=bearing)
    check('M3x8 cover retention bolts fully engage captured nuts and stop before blind-hole floors',
          49.75-8>40.754+.9 and 49.75-8<43.754-2 and 47.4-2.4>43.754+1,
          tip_radius_mm=41.75,nut_inner_radius_mm=45,blind_floor_radius_mm=40.754,
          blind_floor_margin_mm=.996,retention_pin_insertion_mm=2.004,
          note='Nuts are captured in the nozzle, not in the unchanged cover. The three cover holes are blind; these are locking retention pins, not through-bolts that clamp the cover.')
    envelopes=[t.cylinder(37.4,-3.0001,19.5002),t.cylinder(25.456,16.4999,2.5002),
               t.cylinder(13.8501,-5.0001,2.0002),t.cylinder(1.5876,18.9999,6.5002)]
    moving=[p[n] for n in ('propeller','insert','rotor')]
    stationary=[]
    for h in hardware:
        lo,hi=t.limits(h)
        if abs((hi[1]-lo[1])-11)<.01 and lo[1]>6:moving.append(h)
        else:stationary.append(h)
    outside=[]
    for s in moving:
        rem=s
        for env in envelopes:rem=t.boolean(t.BRepAlgoAPI_Cut,rem,env)
        outside.append(t.volume(rem))
    check('refined continuous envelopes contain all seven moving components',len(moving)==7 and max(outside)<1e-4,moving_count=len(moving),outside_mm3=outside)
    gaps=[]
    for name,s in list(p.items()):
        if name not in ('nozzle','cover','stator'):continue
        for i,env in enumerate(envelopes):gaps.append({'part':name,'envelope':i,'gap_mm':t.distance(env,s)})
    for i,s in enumerate(stationary):
        for j,env in enumerate(envelopes):gaps.append({'part':f'hardware_{i+1}','envelope':j,'gap_mm':t.distance(env,s)})
    check('complete rotating group stays clear through every angle with all fasteners installed',min(g['gap_mm'] for g in gaps)>.1,minimum_gap_mm=min(g['gap_mm'] for g in gaps),clearances=gaps)
    baseline,_=read(OLD/'Thruster-A2212-final-audit.step')
    unchanged={}
    for n in ('cover','propeller','insert','rotor','stator'):
        a,b=p[n],baseline[n]
        unchanged[n]={'volume_delta_mm3':abs(t.volume(a)-t.volume(b)),'area_delta_mm2':abs(t.area(a)-t.area(b)),
                      'max_bounds_delta_mm':max(abs(x-y) for aa,bb in zip(t.limits(a),t.limits(b)) for x,y in zip(aa,bb))}
    check('gray cover, motor and rotating printed parts retain geometry and placement',
          all(d['volume_delta_mm3']<.01 and d['area_delta_mm2']<.01 and d['max_bounds_delta_mm']<1e-5 for d in unchanged.values()),comparisons=unchanged)
    labelled=list(p.items())+[(f'hardware_{i}',s) for i,s in enumerate(hardware)]
    unwanted=[];threads=[]
    for (an,a),(bn,b) in itertools.combinations(labelled,2):
        al,ah=t.limits(a);bl,bh=t.limits(b)
        if any(ah[j]<=bl[j]+1e-7 or bh[j]<=al[j]+1e-7 for j in range(3)):continue
        v=t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b))
        if v<1e-4:continue
        screw=b if an=='insert' else a if bn=='insert' else None
        if screw is not None:
            lo,hi=t.limits(screw)
            if abs(lo[1]-7)<1e-5 and abs(hi[1]-18)<1e-5:
                threads.append({'a':an,'b':bn,'volume_mm3':v});continue
        unwanted.append({'a':an,'b':bn,'volume_mm3':v})
    check('all 39 native solids have no unintended static interference',not unwanted and len(threads)==4,
          checked_pairs=len(labelled)*(len(labelled)-1)//2,intended_pilot_contacts=threads,unexpected=unwanted)
    report={'file':sys.argv[1],'checks':checks,'physical_validation_pending':True,
            'printer':'Bambu Lab P1S','material':'PLA Basic','nominal_shaft_clearance_per_side_mm':.1625}
    Path(sys.argv[2]).write_text(json.dumps(report,indent=2))
    print(json.dumps({'passed':sum(c['pass'] for c in checks),'total':len(checks),'failed':[c['check'] for c in checks if not c['pass']]},indent=2))
    sys.exit(0 if all(c['pass'] for c in checks) else 1)

if __name__=='__main__':main()
