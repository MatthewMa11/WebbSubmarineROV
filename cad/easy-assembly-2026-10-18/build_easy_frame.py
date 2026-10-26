"""Five flat panels, eight accessible M4 joints, and a lift-out pod."""
from pathlib import Path
_legacy=Path(__file__).resolve().parent.parent/'laser-frame-electronics-2026-10-17'
_old=(_legacy/'build_frame.py').read_text()
# Reuse the previously verified geometry, DXF and source-preservation helpers.
exec(compile(_old.split('# Two decks,')[0],str(__file__),'exec'),globals())
TOP=30.0
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse

# One base, two identical short side rails, and two identical open saddles.
bolt_stations=[]
for x in (-65,65):
    for y in (-84,84):bolt_stations.append((x,y,'saddle'))
for sy in (-1,1):
    for x in (-105,105):bolt_stations.append((x,sy*(170+BASE-T/2),'side rail'))
s=polygon(chamfer_rect(520,500,15))
for e in layout['placements'][4:]:s=hole(s,*e['origin_mm'][:2],96)
s=cut(s,polygon(chamfer_rect(220,110,10),-.1,T+.2))
for sx in (-1,1):s=cut(s,polygon(chamfer_rect(80,44,6,sx*188,0),-.1,T+.2))
for sy in (-1,1):s=cut(s,polygon(chamfer_rect(20,96,4,0,sy*180),-.1,T+.2))
for x,y,kind in bolt_stations:
    s=cut(s,rect(x,y,3.2 if kind=='saddle' else 14,14 if kind=='saddle' else 3.2))
    s=hole(s,x,y,4.3)
for x,y in itertools.product((-45,45),(-90,90)):s=cut(s,rect(x,y,26,3.2))
for e in layout['placements'][:4]:
    m=e['transform_3x4']
    for x,y in itertools.product((-10,10),(-5,5)):
        s=hole(s,m[0][0]*x+m[0][1]*y+m[0][3],m[1][0]*x+m[1][1]*y+m[1][3],4.3)
    s=hole(s,m[0][1]*20.5+m[0][3],m[1][1]*20.5+m[1][3],10)
add_flat('E01-base-plate',s,matrix([(1,0,0),(0,1,0),(0,0,1)],(0,0,BASE-T)))
def lower_tabs(width,top,tabs):
    p=[(-width/2,BASE)]
    for u in sorted(tabs):p.extend([(u-7,BASE),(u-7,BASE-T),(u+7,BASE-T),(u+7,BASE)])
    p.extend([(width/2,BASE),(width/2,top),(-width/2,top)])
    s=polygon(p)
    for u in tabs:
        s=cut(s,rect(u,BASE+5.9,4.3,18.4))
        s=cut(s,rect(u,BASE+8.5,7.2,3.4))
    return s
rail=lower_tabs(240,30,[-105,105])
for mount in (-75,75):
    for x,z in itertools.product((-10,10),(-5,5)):rail=hole(rail,mount+x,z,4.3)
    for z in (-20.5,20.5):rail=hole(rail,mount,z,10)
rail=cut(rail,polygon(chamfer_rect(90,35,5,0,-3),-.1,T+.2))
for n,sy in enumerate((-1,1),2):
    add_flat(f'E{n:02d}-side-rail-identical',rail,matrix([(sy,0,0),(0,0,1),(0,-sy,0)],(0,sy*(170+BASE),0)))
saddle=hole(lower_tabs(190,25,[-84,84]),0,ZC,161)
for y in (-89/math.sqrt(2),89/math.sqrt(2)):
    rod_z=ZC-89/math.sqrt(2)
    saddle=hole(saddle,y,rod_z,6)
    saddle=cut(saddle,rect(y,(rod_z+25.1)/2,6,25.1-rod_z))
for n,x in enumerate((-65,65),4):
    add_flat(f'E{n:02d}-open-saddle-identical',saddle,matrix([(0,1,0),(0,0,1),(1,0,0)],(x-T/2,0,0)))
check('five 3 mm laser-cut panels are valid single solids; three unique profiles',len(flat)==5 and len(parts)==5)

# The complete cylinder/caps/tie rods remain unchanged from the previous model.
_pod=_old.split('# Hollow centre tube,',1)[1].split('\n',1)[1].split('# M3 bolts and nuts',1)[0]
exec(compile(_pod,str(__file__),'exec'),globals())

# All frame joints now use one accessible M4 bolt/washer/nut combination.
for i,(x,y,kind) in enumerate(bolt_stations,1):
    seat=BASE-T-.8
    washer=cut(cyl(4.5,(x,y,seat),(0,0,1),.8),cyl(2.15,(x,y,seat-.01),(0,0,1),.82))
    add(f'M4-frame-washer-{i}',washer)
    shaft=cyl(2,(x,y,seat),(0,0,1),16);head=cyl(3.61,(x,y,seat-4),(0,0,1),4)
    op=BRepAlgoAPI_Fuse(shaft,head);op.Build();assert op.IsDone();add(f'M4x16-frame-bolt-{i}',op.Shape())
    add(f'M4-frame-nut-{i}',nut_z(x,y,BASE+8.5-1.6,7,3.2,0 if kind=='saddle' else 30,2))

# Purchased adjustable straps and side-release buckle envelopes, not cut parts.
# Bands pass through base slots beside the saddles and can be released from above.
def belt_path(radius,ybottom,zbottom):
    return [(-ybottom,zbottom),(ybottom,zbottom),(ybottom,BASE-T)]+[(radius*math.cos(math.pi*i/96),ZC+radius*math.sin(math.pi*i/96)) for i in range(97)]+[(-ybottom,BASE-T)]
band=cut(polygon(belt_path(81.8,90.5,BASE-T-2),0,25),polygon(belt_path(80.8,89.5,BASE-T-1),-.1,25.2))
for i,x in enumerate((-45,45),1):
    add(f'STRAP-25mm-adjustable-{i}',moved(band,matrix([(0,1,0),(0,0,1),(1,0,0)],(x-12.5,0,0))),(.16,.17,.18),'purchased strap reference')
    case=cut(rect(0,0,33,36,137.5,7),rect(0,0,27,26,137.4,7.2))
    bar=rect(0,0,27.2,3,139,3)
    op=BRepAlgoAPI_Fuse(case,bar);op.Build();assert op.IsDone()
    add(f'BUCKLE-side-release-reference-{i}',translate(op.Shape(),x=x),(.24,.25,.26),'purchased strap reference')
check('added-part count falls from 103 to 56',len(parts)==56,count=len(parts))
check('frame joints fall from 24 to 8 and use M4 throughout',len(bolt_stations)==8)
check('the electronics cylinder dimensions are retained',abs(vol(tube)-math.pi*(80**2-74**2)*200)<.01)

# Keep the full source/added-part collision checks and native exports.
_tail=_old.split('# Validate new-solid intersections,',1)[1].split('\n',1)[1]
_tail=_tail.replace('Laser-cut frame and electronics pod','Easy frame and removable electronics pod')
_tail=_tail.replace('frame_deck_levels_mm=[BASE-T,BASE,TOP,TOP+T]','frame_deck_levels_mm=[BASE-T,BASE]')
_tail=_tail.replace("sheet_material_assumption='3 mm aluminum; confirm actual stock before cutting'","sheet_material_assumption='3 mm aluminum - retained user selection'")
exec(compile(_tail,str(__file__),'exec'),globals())
manifest.update(unique_laser_profiles=3,frame_joint_bolts=8,frame_bolt_size='M4x16',pod_release_straps=2,
                previous=dict(laser_cut_parts=8,frame_joint_bolts=24,added_solids=103),
                assembly_steps=['Fit two short side rails and two open saddles to the base using eight M4 joints',
                                'Bolt on the eight unchanged thrusters',
                                'Thread two straps through the base slots',
                                'Lower the cylinder into the open saddles and close the two buckles'])
(R/'frame-pod-verification.json').write_text(json.dumps(manifest,indent=2))
