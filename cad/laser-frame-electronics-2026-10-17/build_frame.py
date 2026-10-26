"""Flat-sheet ROV frame, mounting hardware and central electronics pod.

All new cut parts are straight 3 mm extrusions; DXF paths are taken from
their actual bottom faces. Existing thruster geometry is never regenerated.
"""
from pathlib import Path
import sys,math,json,itertools,re,csv
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parents[2]/'robotic FTC 2026-2027/cad/.vendor'))
from OCP.gp import gp_Pnt,gp_Vec,gp_Dir,gp_Ax2,gp_Trsf
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism,BRepPrimAPI_MakeCylinder,BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut,BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Line,GeomAbs_Circle
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE,TopAbs_EDGE
from OCP.TopoDS import TopoDS,TopoDS_Compound
from OCP.TopLoc import TopLoc_Location
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label
from OCP.XCAFDoc import XCAFDoc_DocumentTool,XCAFDoc_ColorGen
from OCP.Quantity import Quantity_Color,Quantity_TOC_RGB
from OCP.collections import Sequence_TDF_Label
from OCP.STEPControl import STEPControl_AsIs,STEPControl_Reader
from OCP.STEPCAFControl import STEPCAFControl_Reader,STEPCAFControl_Writer
from OCP.BRepTools import BRepTools

T=3.0; BASE=-50.795543309729; TOP=160.0; ZC=55.0
POD_OD=160.0; POD_ID=148.0; POD_L=200.0; CAP_R=98.0; CAP_T=8.0
old=R.parent/'eight-thruster-assembly-2026-10-17'
layout=json.loads((old/'assembly-verification.json').read_text())
parts=[];flat=[];checks=[]
BLUE=(.16,.34,.49);METAL=(.46,.49,.52);TUBE=(.48,.73,.83)
def check(name,ok,**data):
    checks.append(dict(check=name,passed=bool(ok),**data));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
    if not ok:raise AssertionError((name,data))
def bounds(s):
    b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b,False,False)
    return [[p.X(),p.Y(),p.Z()] for p in (b.CornerMin(),b.CornerMax())]
def vol(s):
    p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return abs(p.Mass())
def area(s):
    p=GProp_GProps();BRepGProp.SurfaceProperties_s(s,p);return abs(p.Mass())
def count(s,kind=TopAbs_SOLID):
    ex=TopExp_Explorer(s,kind);n=0
    while ex.More():n+=1;ex.Next()
    return n
def compound(shapes):
    c=TopoDS_Compound();b=BRep_Builder();b.MakeCompound(c)
    for s in shapes:b.Add(c,s)
    return c
def cut(a,b):
    op=BRepAlgoAPI_Cut(a,b);op.Build();assert op.IsDone();return op.Shape()
def common(a,b):
    op=BRepAlgoAPI_Common(a,b);op.Build();assert op.IsDone();return op.Shape()
def cyl(rad,start,axis,height):return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*start),gp_Dir(*axis)),rad,height).Shape()
def polygon(points,z=0,h=T):
    p=BRepBuilderAPI_MakePolygon()
    for x,y in points:p.Add(gp_Pnt(x,y,z))
    p.Close();return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Vec(0,0,h)).Shape()
def rect(cx,cy,w,h,z=-.1,depth=T+.2):return polygon([(cx-w/2,cy-h/2),(cx+w/2,cy-h/2),(cx+w/2,cy+h/2),(cx-w/2,cy+h/2)],z,depth)
def chamfer_rect(w,h,c,cx=0,cy=0):
    return [(cx+x,cy+y) for x,y in [(-w/2+c,-h/2),(w/2-c,-h/2),(w/2,-h/2+c),(w/2,h/2-c),(w/2-c,h/2),(-w/2+c,h/2),(-w/2,h/2-c),(-w/2,-h/2+c)]]
def hole(s,x,y,d):return cut(s,cyl(d/2,(x,y,-.1),(0,0,1),T+.2))
def matrix(cols,origin):
    tr=gp_Trsf();tr.SetValues(cols[0][0],cols[1][0],cols[2][0],origin[0],cols[0][1],cols[1][1],cols[2][1],origin[1],cols[0][2],cols[1][2],cols[2][2],origin[2]);return tr
def moved(s,tr):return s.Moved(TopLoc_Location(tr))
def translate(s,x=0,y=0,z=0):
    tr=gp_Trsf();tr.SetTranslation(gp_Vec(x,y,z));return moved(s,tr)
def add(name,s,color=METAL,kind='hardware'):
    assert count(s)==1,(name,count(s))
    assert BRepCheck_Analyzer(s).IsValid(),name
    entry=dict(name=name,shape=s,color=color,kind=kind);parts.append(entry);return entry
def dxf(name,shape):
    """Export the single planar lower face, in mm at 1:1 scale."""
    faces=[];ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face(ex.Current());ex.Next();lo,hi=bounds(f)
        if abs(lo[2])<1e-6 and abs(hi[2])<1e-6:faces.append(f)
    assert len(faces)==1,(name,len(faces))
    lo,hi=bounds(shape);dx,dy=-lo[0],-lo[1]
    out=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1015','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
    def ent(kind,values):
        out.extend(['0',kind,'8','CUT'])
        for code,val in values:out.extend([str(code),str(val)])
    edges=[];ex=TopExp_Explorer(faces[0],TopAbs_EDGE)
    while ex.More():
        e=TopoDS.Edge(ex.Current());ex.Next();c=BRepAdaptor_Curve(e);typ=c.GetType()
        if typ==GeomAbs_Line:
            a=c.Value(c.FirstParameter());b=c.Value(c.LastParameter())
            ent('LINE',[(10,a.X()+dx),(20,a.Y()+dy),(30,0),(11,b.X()+dx),(21,b.Y()+dy),(31,0)])
            edges.append(dict(type='line',p1=[a.X()+dx,a.Y()+dy],p2=[b.X()+dx,b.Y()+dy]))
        elif typ==GeomAbs_Circle:
            cc=c.Circle();p=cc.Location();rad=cc.Radius();a=c.Value(c.FirstParameter());b=c.Value(c.LastParameter())
            vals=[(10,p.X()+dx),(20,p.Y()+dy),(30,0),(40,rad)]
            if abs(c.LastParameter()-c.FirstParameter())>2*math.pi-1e-6:
                ent('CIRCLE',vals);edges.append(dict(type='circle',center=[p.X()+dx,p.Y()+dy],radius=rad))
            else:
                aa=math.degrees(math.atan2(a.Y()-p.Y(),a.X()-p.X()))%360;bb=math.degrees(math.atan2(b.Y()-p.Y(),b.X()-p.X()))%360
                if cc.Axis().Direction().Z()<0:aa,bb=bb,aa
                ent('ARC',vals+[(50,aa),(51,bb)]);edges.append(dict(type='arc',center=[p.X()+dx,p.Y()+dy],radius=rad,start_deg=aa,end_deg=bb))
        else:raise RuntimeError('Non laser-cut curve type: '+str(typ))
    out+=['0','ENDSEC','0','EOF']
    folder=R/'laser-cut-DXF';folder.mkdir(exist_ok=True)
    (folder/(name+'.dxf')).write_text('\n'.join(out)+'\n')
    return dict(name=name,stock_thickness_mm=T,flat_size_mm=[hi[0]-lo[0],hi[1]-lo[1]],area_mm2=area(faces[0]),dxf_entities=len(edges),paths=edges)
def add_flat(name,s,tr):
    item=dxf(name,s);flat.append(item);return add(name,moved(s,tr),BLUE,'laser-cut sheet')

# Two decks, with local fastener holes on the actual thruster pad pattern.
vertical_positions=[e['origin_mm'][:2] for e in layout['placements'][4:]]
bolt_stations=[]
for x in (-98.5,98.5):
    for y in (-100,100):bolt_stations.append((x,y,'bulkhead'))
for sx,sy in itertools.product((-1,1),repeat=2):
    for off in (-20,20):bolt_stations.append((sx*75+off,sy*(170+BASE-T/2),'vertical mount'))
for name,z,upper in [('LC01-lower-deck',BASE-T,False),('LC02-upper-deck',TOP,True)]:
    s=polygon(chamfer_rect(520,500,15))
    for x,y in vertical_positions:s=hole(s,x,y,96)
    s=cut(s,polygon(chamfer_rect(280 if upper else 220,170 if upper else 110,10),-.1,T+.2))
    if upper:
        for sx,sy in itertools.product((-1,1),repeat=2):
            s=cut(s,polygon(chamfer_rect(120,120,8,sx*185,sy*75),-.1,T+.2))
    for sx in (-1,1):s=cut(s,polygon(chamfer_rect(100 if upper else 80,44,6,sx*188,0),-.1,T+.2))
    for sy in (-1,1):s=cut(s,polygon(chamfer_rect(20,96,4,0,sy*180),-.1,T+.2))
    for x,y,kind in bolt_stations:s=cut(s,rect(x,y,3.2 if kind=='bulkhead' else 12,12 if kind=='bulkhead' else 3.2))
    if not upper:
        for e in layout['placements'][:4]:
            m=e['transform_3x4']
            for x,y in itertools.product((-10,10),(-5,5)):
                xx=m[0][0]*x+m[0][1]*y+m[0][3];yy=m[1][0]*x+m[1][1]*y+m[1][3];s=hole(s,xx,yy,4.3)
            xx=m[0][1]*20.5+m[0][3];yy=m[1][1]*20.5+m[1][3];s=hole(s,xx,yy,10)
    add_flat(name,s,matrix([(1,0,0),(0,1,0),(0,0,1)],(0,0,z)))

def upright(width,tabs,bulkhead):
    p=[(-width/2,BASE)]
    for u in sorted(tabs):p.extend([(u-6,BASE),(u-6,BASE-T),(u+6,BASE-T),(u+6,BASE)])
    p.extend([(width/2,BASE),(width/2,TOP)])
    for u in sorted(tabs,reverse=True):p.extend([(u+6,TOP),(u+6,TOP+T),(u-6,TOP+T),(u-6,TOP)])
    p.append((-width/2,TOP));s=polygon(p)
    for u in tabs:
        for edge,sgn in ((BASE,1),(TOP,-1)):
            s=cut(s,rect(u,edge+sgn*5.4,3.3,17.4))
            s=cut(s,rect(u,edge+sgn*8.5,5.7,2.6))
    if bulkhead:
        s=hole(s,0,ZC,160.6)
        for y,z in itertools.product((-89/math.sqrt(2),89/math.sqrt(2)),repeat=2):s=hole(s,y,ZC+z,4.3)
    else:
        for x,z in itertools.product((-10,10),(-5,5)):s=hole(s,x,z,4.3)
        for z in (-20.5,20.5):s=hole(s,0,z,10)
        s=cut(s,polygon(chamfer_rect(32,80,5,0,95),-.1,T+.2))
    return s
for n,x in enumerate((-98.5,98.5),3):
    add_flat(f'LC{n:02d}-pod-bulkhead',upright(230,[-100,100],True),matrix([(0,1,0),(0,0,1),(1,0,0)],(x-T/2,0,0)))
for n,(sx,sy) in enumerate(itertools.product((-1,1),repeat=2),5):
    add_flat(f'LC{n:02d}-vertical-thruster-support',upright(60,[-20,20],False),matrix([(sy,0,0),(0,0,1),(0,-sy,0)],(sx*75,sy*(170+BASE),0)))
check('eight frame pieces are valid single solids and constant-thickness sheet extrusions',len(flat)==8 and len(parts)==8)

# Hollow centre tube, removable end plates and four external M4 tie rods.
tube=cut(cyl(80,(-100,0,ZC),(1,0,0),200),cyl(74,(-100.1,0,ZC),(1,0,0),200.2))
add('POD01-electronics-tube-OD160-ID148-L200',tube,TUBE,'pod')
rod_axes=list(itertools.product((-89/math.sqrt(2),89/math.sqrt(2)),repeat=2))
for sign in (-1,1):
    cap=cyl(CAP_R,(sign*100,0,ZC),(sign,0,0),CAP_T)
    for y,z in rod_axes:cap=cut(cap,cyl(2.15,(sign*99.9,y,ZC+z),(sign,0,0),8.2))
    add('POD02-end-cap-left' if sign<0 else 'POD03-end-cap-right',cap,(.30,.34,.38),'pod')
def nut_z(x,y,z,af,thick,theta=0,bore=1.5):
    radius=af/math.sqrt(3)
    p=[(x+radius*math.cos(math.radians(theta+60*i)),y+radius*math.sin(math.radians(theta+60*i))) for i in range(6)]
    return cut(polygon(p,z,thick),cyl(bore,(x,y,z-.01),(0,0,1),thick+.02))
for i,(y,zz) in enumerate(rod_axes,1):
    z=ZC+zz;add(f'M4-pod-tie-rod-{i}-230mm',cyl(2,(-115,y,z),(1,0,0),230))
    for sign in (-1,1):
        washer=cut(cyl(4.5,(sign*108,y,z),(sign,0,0),.8),cyl(2.15,(sign*107.99,y,z),(sign,0,0),.82))
        add(f'M4-pod-washer-{i}-{sign}',washer)
        local=nut_z(0,0,0,7,3.2,30,2)
        tr=matrix([(0,1,0),(0,0,sign),(sign,0,0)],(sign*108.8,y,z))
        add(f'M4-pod-nut-{i}-{sign}',moved(local,tr))

# M3 bolts and nuts clamp the sheet tab joints; no glue-only or friction-only joints.
for i,(x,y,kind) in enumerate(bolt_stations,1):
    for top in (False,True):
        edge=TOP if top else BASE;axis=(0,0,-1 if top else 1);sgn=axis[2]
        washer_start=edge+(-sgn)*(T+.5)
        washer=cut(cyl(3.5,(x,y,washer_start),axis,.5),cyl(1.6,(x,y,washer_start-sgn*.01),axis,.52))
        tag=f'{i}-'+('top' if top else 'bottom')
        add('M3-frame-washer-'+tag,washer)
        # Shaft starts at the head bearing face and runs 16 mm into the T slot.
        seat=washer_start
        shaft=cyl(1.5,(x,y,seat),axis,16)
        head=cyl(2.84,(x,y,seat-sgn*3),axis,3)
        # Join touching cylinders using a single revolved step cylinder boolean union.
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
        op=BRepAlgoAPI_Fuse(shaft,head);op.Build();assert op.IsDone();add('M3x16-frame-bolt-'+tag,op.Shape())
        z=edge+sgn*8.5-1.2
        add('M3-frame-nut-'+tag,nut_z(x,y,z,5.5,2.4,0 if kind=='bulkhead' else 30))
check('frame and pod include all 103 added physical components',len(parts)==103,count=len(parts))
check('the electronics tube is hollow and provides 3.44 litres before electronics',abs(vol(tube)-math.pi*(80**2-74**2)*200)<.01,interior_volume_litres=math.pi*74**2*200/1e6)

# Validate new-solid intersections, excluding mere contact and thread-free shafts.
bb=[bounds(e['shape']) for e in parts]
def overlap_boxes(a,b,tol=1e-5):return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>tol for i in range(3))
bad=[];tested=0
for i,j in itertools.combinations(range(len(parts)),2):
    if not overlap_boxes(bb[i],bb[j]):continue
    tested+=1;v=vol(common(parts[i]['shape'],parts[j]['shape']))
    if v>1e-4:bad.append(dict(a=parts[i]['name'],b=parts[j]['name'],overlap_mm3=v))
check('new frame, tube and hardware have no unintended solid overlap',not bad,boolean_pairs=tested,interferences=bad)

# Load the original 39 parts with their names. Move each M4 mounting bolt and
# washer outward by the sheet thickness; motor/nozzle/propeller geometry stays put.
doc0=TDocStd_Document(TCollection_ExtendedString('XCAF'));rd=STEPCAFControl_Reader();rd.ReadFile(layout['source_file']);assert rd.Transfer(doc0)
st0=XCAFDoc_DocumentTool.ShapeTool_s(doc0.Main());rs=Sequence_TDF_Label();st0.GetFreeShapes(rs);cs=Sequence_TDF_Label();st0.GetComponents_s(rs.Value(1),cs)
source=[];shifted=[]
for i in range(1,cs.Length()+1):
    label=cs.Value(i);ref=TDF_Label();st0.GetReferredShape_s(label,ref)
    nm=TDataStd_Name();label.FindAttribute(TDataStd_Name.GetID_s(),nm);name=nm.Get().ToExtString()
    if not name:
        ref.FindAttribute(TDataStd_Name.GetID_s(),nm);name=nm.Get().ToExtString()
    shape=st0.GetShape_s(label)
    shift=name.startswith('M4 flat washer') or name.startswith('M4x12 socket mounting bolt')
    if shift:shape=translate(shape,z=-T);shifted.append(name)
    source.append((name,shape))
check('only the eight M4 mounting washers and bolts shift for sheet thickness',len(shifted)==8,names=shifted)
thruster_conflicts=[];narrow=0;pod_clear=[]
for e in layout['placements']:
    m=e['transform_3x4'];tr=gp_Trsf();tr.SetValues(*[v for row in m for v in row])
    for name,s in source:
        world=moved(s,tr);sb=bounds(world)
        for k,p in enumerate(parts):
            if not overlap_boxes(sb,bb[k]):continue
            narrow+=1;v=vol(common(world,p['shape']))
            if v>1e-4:thruster_conflicts.append(dict(thruster=e['tag'],part=name,new_part=p['name'],overlap_mm3=v))
    # A simple bounding box is conservative for the complete 39-part thruster.
    sb=bounds(compound([moved(s,tr) for _,s in source]))
    box=BRepPrimAPI_MakeBox(gp_Pnt(*sb[0]),gp_Pnt(*sb[1])).Shape()
    d=BRepExtrema_DistShapeShape(box,compound([p['shape'] for p in parts if p['kind']=='pod']));d.Perform()
    pod_clear.append(dict(thruster=e['tag'],conservative_pod_clearance_mm=d.Value()))
check('all eight thrusters clear every added panel, cylinder and fastener',not thruster_conflicts,boolean_pairs=narrow,interferences=thruster_conflicts)

# Export the simple new parts as a named, coloured assembly; a separate script
# attaches this to the original native STEP without serializing its old surfaces.
doc=TDocStd_Document(TCollection_ExtendedString('XCAF'));st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main());ct=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
root=st.AddShape(compound([]),False);TDataStd_Name.Set_s(root,TCollection_ExtendedString('Laser-cut frame and electronics pod'))
for p in parts:
    lab=st.AddShape(p['shape'],False);TDataStd_Name.Set_s(lab,TCollection_ExtendedString(p['name']))
    ct.SetColor(lab,Quantity_Color(*p['color'],Quantity_TOC_RGB),XCAFDoc_ColorGen)
    occurrence=st.AddComponent(root,lab,TopLoc_Location());TDataStd_Name.Set_s(occurrence,TCollection_ExtendedString(p['name']))
st.UpdateAssemblies();w=STEPCAFControl_Writer();w.SetNameMode(True);w.SetColorMode(True);assert w.Transfer(doc,STEPControl_AsIs);assert int(w.Write(str(R/'frame-pod-parts.step')))==1
meshdir=R/'native-breps';meshdir.mkdir(exist_ok=True)
for p in parts:BRepTools.Write_s(p['shape'],str(meshdir/(p['name']+'.brep')))
manifest=dict(sheet_thickness_mm=T,sheet_material_assumption='3 mm aluminum; confirm actual stock before cutting',
              frame_outer_mm=[520,500],frame_deck_levels_mm=[BASE-T,BASE,TOP,TOP+T],
              tube=dict(outside_diameter_mm=POD_OD,inside_diameter_mm=POD_ID,body_length_mm=POD_L,end_cap_diameter_mm=196,end_cap_thickness_mm=8,center_mm=[0,0,ZC],axis='X',interior_litres=math.pi*74**2*200/1e6),
              laser_cut_parts=flat,added_parts=[{k:p[k] for k in ('name','color','kind')} for p in parts],
              added_solids=len(parts),total_expected_solids=312+len(parts),checks=checks,pod_clearances=pod_clear,
              source_mounting_hardware_shift_mm=-T,source_mounting_hardware_shifted=shifted,
              pressure_rating_validated=False,seal_and_cable_gland_hardware_selected=False,structural_loads_validated=False)
(R/'frame-pod-verification.json').write_text(json.dumps(manifest,indent=2))
print('Built',len(flat),'laser-cut parts and',len(parts),'new assembly solids.',flush=True)
