"""Verify serialized cut paths, vertical flow, and a continuous pod lift envelope."""
from pathlib import Path
import json,math,collections,shutil
_legacy=Path(__file__).resolve().parent.parent/'laser-frame-electronics-2026-10-17'
exec(compile((_legacy/'build_frame.py').read_text().split('# Two decks,')[0],str(__file__),'exec'),globals())
meta=json.loads((R/'frame-pod-verification.json').read_text());cutproof=[]
for path in sorted((R/'laser-cut-DXF').glob('*.dxf')):
    lines=path.read_text().splitlines();assert len(lines)%2==0
    pairs=[(int(lines[i]),lines[i+1]) for i in range(0,len(lines),2)]
    assert pairs[pairs.index((9,'$INSUNITS'))+1]==(70,'4')
    entities=[];current=None
    for code,value in pairs[pairs.index((2,'ENTITIES'))+1:]:
        if code==0:
            if current:entities.append(current)
            if value=='ENDSEC':break
            current=[value,{}]
        elif current:current[1][code]=value
    graph=collections.Counter()
    for kind,v in entities:
        assert kind in ('LINE','CIRCLE','ARC') and v.get(8)=='CUT'
        if kind=='LINE':ends=[(float(v[10]),float(v[20])),(float(v[11]),float(v[21]))]
        elif kind=='ARC':
            ends=[(float(v[10])+float(v[40])*math.cos(math.radians(float(v[a]))),float(v[20])+float(v[40])*math.sin(math.radians(float(v[a])))) for a in (50,51)]
        else:assert float(v[40])>0;continue
        for end in ends:graph[tuple(round(x,6) for x in end)]+=1
    assert graph and all(n==2 for n in graph.values()),(path,[(k,n) for k,n in graph.items() if n!=2])
    cutproof.append(dict(file=path.name,cut_entities=len(entities),all_paths_closed=True,units='mm'))
assert len(cutproof)==5
dxfs=R/'laser-cut-DXF'
assert (dxfs/'E02-side-rail-identical.dxf').read_bytes()==(dxfs/'E03-side-rail-identical.dxf').read_bytes()
assert (dxfs/'E04-open-saddle-identical.dxf').read_bytes()==(dxfs/'E05-open-saddle-identical.dxf').read_bytes()
unique=R/'laser-cut-unique';unique.mkdir(exist_ok=True)
for a,b in [('E01-base-plate.dxf','A-base-QTY1.dxf'),('E02-side-rail-identical.dxf','B-side-plate-QTY2.dxf'),('E04-open-saddle-identical.dxf','C-open-saddle-QTY2.dxf')]:shutil.copyfile(dxfs/a,unique/b)
check('five panels reduce to three unique, closed DXF cutting profiles',len(list(unique.glob('*.dxf')))==3)

loaded=[]
for item in meta['added_parts']:
    from OCP.TopoDS import TopoDS_Shape
    shape=TopoDS_Shape();assert BRepTools.Read_s(shape,str(R/'native-breps'/(item['name']+'.brep')),BRep_Builder())
    loaded.append((item,shape))
flow=[]
for x,y in itertools.product((-75,75),(-170,170)):
    gauge=cyl(38,(x,y,-100),(0,0,1),300)
    blocked=sum(vol(common(gauge,s)) for item,s in loaded if item['kind']=='laser-cut sheet')
    assert blocked<1e-4,(x,y,blocked)
    flow.append(dict(axis_xy_mm=[x,y],clear_diameter_mm=76,obstruction_volume_mm3=blocked))
check('all four vertical thruster passages stay open through the frame',len(flow)==4)

def lift_envelope(radius,y,zc,x0,length,travel=200):
    # Circumscribed polygon margin exceeds chord sagitta; this envelope encloses
    # the complete round feature throughout a continuous 200 mm vertical lift.
    r=radius+.05
    p=[(y+r*math.cos(math.pi+math.pi*i/96),zc+r*math.sin(math.pi+math.pi*i/96)) for i in range(97)]
    p += [(y+r*math.cos(math.pi*i/96),zc+travel+r*math.sin(math.pi*i/96)) for i in range(97)]
    return moved(polygon(p,0,length),matrix([(0,1,0),(0,0,1),(1,0,0)],(x0,0,0)))
sweeps=[('tube',lift_envelope(80,0,55,-100,200))]
for sign in (-1,1):sweeps.append(('end cap',lift_envelope(98,0,55,100 if sign>0 else -108,8)))
for y,z in itertools.product((-89/math.sqrt(2),89/math.sqrt(2)),repeat=2):
    sweeps.append(('tie rod',lift_envelope(2,y,55+z,-115,230)))
    for sign in (-1,1):sweeps.append(('cap nut and washer',lift_envelope(4.5,y,55+z,108 if sign>0 else -112,4)))
fixed=[(item['name'],s) for item,s in loaded if item['kind']=='laser-cut sheet' or '-frame-' in item['name']]
lo,hi=layout['source_bounds_mm'];lo=lo.copy();lo[2]-=3
protected=BRepPrimAPI_MakeBox(gp_Pnt(*lo),gp_Pnt(*hi)).Shape()
for e in layout['placements']:
    tr=gp_Trsf();tr.SetValues(*[v for row in e['transform_3x4'] for v in row])
    fixed.append((e['tag']+' conservative thruster envelope',moved(protected,tr)))
def boxes_intersect(a,b):return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>1e-5 for i in range(3))
bad=[];tested=0
for name,envelope in sweeps:
    for obstacle,shape in fixed:
        if not boxes_intersect(bounds(envelope),bounds(shape)):continue
        tested+=1;v=vol(common(envelope,shape))
        if v>1e-4:bad.append(dict(feature=name,obstacle=obstacle,volume_mm3=v))
check('released pod can lift continuously 200 mm without dismantling the frame',not bad,boolean_pairs=tested,interferences=bad)
meta.update(exported_dxf_closure_checks=cutproof,vertical_flow_checks=flow,
            unique_cut_files=['A-base-QTY1.dxf','B-side-plate-QTY2.dxf','C-open-saddle-QTY2.dxf'],
            continuous_pod_lift_check=dict(travel_mm=200,passed=True,straps_released=True,boolean_pairs=tested),
            added_checks=checks)
(R/'frame-pod-verification.json').write_text(json.dumps(meta,indent=2))
