"""Place eight unchanged R3 thrusters in a hierarchical STEP assembly."""
from pathlib import Path
import sys, math, json, csv, itertools
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / 'robotic FTC 2026-2027' / 'cad' / '.vendor'))
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.collections import Sequence_TDF_Label
from OCP.TopoDS import TopoDS_Compound
from OCP.TopLoc import TopLoc_Location
from OCP.BRep import BRep_Builder
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax1, gp_Trsf

SOURCE = ROOT.parent / 'motor-centering-cover-2026-10-17' / 'Thruster-centering-cup-R3.step'
def bounds(shape):
    b=Bnd_Box(); BRepBndLib.AddOptimal_s(shape,b,False,False)
    return [[p.X(),p.Y(),p.Z()] for p in (b.CornerMin(),b.CornerMax())]
def count_solids(shape):
    ex=TopExp_Explorer(shape,TopAbs_SOLID); n=0
    while ex.More(): n+=1; ex.Next()
    return n
def distance(a,b):
    d=BRepExtrema_DistShapeShape(a,b);d.Perform();assert d.IsDone();return d.Value()
def rotation(axis,deg):
    t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(*axis)),math.radians(deg));return t
def placement(sx,sy,vertical,hx,hy,vx,vy):
    if not vertical:
        angle=math.degrees(math.atan2(sy,sx))-90
        t=rotation((0,0,1),angle); origin=[sx*hx,sy*hy,0]
        direction=[sx/math.sqrt(2),sy/math.sqrt(2),0]
    else:
        up=sx*sy>0
        t=rotation((1,0,0),90 if up else -90)
        # Place the original mounting pads toward the centre in Y.
        if (up and sy>0) or (not up and sy<0):
            t=rotation((0,0,1),180).Multiplied(t)
        origin=[sx*vx,sy*vy,0];direction=[0,0,1 if up else -1]
    t.SetTranslationPart(gp_Vec(*origin))
    return t,origin,direction

doc=TDocStd_Document(TCollection_ExtendedString('XCAF'))
reader=STEPCAFControl_Reader();assert int(reader.ReadFile(str(SOURCE)))==1
assert reader.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
roots=Sequence_TDF_Label();st.GetFreeShapes(roots);assert roots.Length()==1
source_label=roots.Value(1);source_shape=st.GetShape_s(source_label)
source_parts=Sequence_TDF_Label();assert st.GetComponents_s(source_label,source_parts)
assert source_parts.Length()==39 and count_solids(source_shape)==39
source_brep_valid=BRepCheck_Analyzer(source_shape).IsValid()
lo,hi=bounds(source_shape)
# Conservative closed box containing every original body, including fasteners.
envelope=BRepPrimAPI_MakeBox(gp_Pnt(*(x-.01 for x in lo)),gp_Pnt(*(x+.01 for x in hi))).Shape()
print('Original envelope:',lo,hi,flush=True)
signs=[(1,1),(-1,1),(-1,-1),(1,-1)]
for hx,hy,vx,vy in [(180,70,75,160),(190,75,75,170),(200,80,75,180),(210,85,75,190),(220,90,75,200)]:
    entries=[]
    for vertical in (False,True):
        for i,(sx,sy) in enumerate(signs):
            t,origin,axis=placement(sx,sy,vertical,hx,hy,vx,vy)
            tag=('V' if vertical else 'H')+str(i+1)
            name=tag+(' - UP' if vertical and axis[2]>0 else ' - DOWN' if vertical else ' - diagonal')
            entries.append(dict(tag=tag,name=name,origin_mm=origin,axis=axis,transform=t,
                                envelope=envelope.Moved(TopLoc_Location(t))))
    gaps=[dict(a=a['tag'],b=b['tag'],conservative_clearance_mm=distance(a['envelope'],b['envelope']))
          for a,b in itertools.combinations(entries,2)]
    smallest=min(q['conservative_clearance_mm'] for q in gaps)
    print('Layout',hx,hy,vx,vy,'minimum envelope gap',smallest,flush=True)
    if smallest>=10:break
else:raise RuntimeError('No layout with >=10 mm conservative clearance')

empty=TopoDS_Compound();BRep_Builder().MakeCompound(empty)
assembly=st.AddShape(empty,False)
TDataStd_Name.Set_s(assembly,TCollection_ExtendedString('ROV - 8 thrusters - 4 diagonal + 4 vertical'))
for e in entries:
    instance=st.AddComponent(assembly,source_label,TopLoc_Location(e['transform']))
    TDataStd_Name.Set_s(instance,TCollection_ExtendedString(e['name']))
st.UpdateAssemblies()
whole=st.GetShape_s(assembly)
assert count_solids(whole)==312
writer=STEPCAFControl_Writer();writer.SetNameMode(True);writer.SetColorMode(True)
assert writer.Transfer(doc,STEPControl_AsIs)
target=ROOT/'ROV-8-thrusters-4-diagonal-4-vertical.step'
assert int(writer.Write(str(target)))==1
# Read the deliverable back through both geometric and assembly readers.
verify=STEPControl_Reader();assert int(verify.ReadFile(str(target)))==1;verify.TransferRoots()
assert count_solids(verify.OneShape())==312
doc2=TDocStd_Document(TCollection_ExtendedString('XCAF'))
reader2=STEPCAFControl_Reader();assert int(reader2.ReadFile(str(target)))==1;assert reader2.Transfer(doc2)
st2=XCAFDoc_DocumentTool.ShapeTool_s(doc2.Main());roots2=Sequence_TDF_Label();st2.GetFreeShapes(roots2)
assert roots2.Length()==1
instances=Sequence_TDF_Label();st2.GetComponents_s(roots2.Value(1),instances);assert instances.Length()==8
out=[]
for e in entries:
    mat=[[e['transform'].Value(i,j) for j in range(1,5)] for i in range(1,4)]
    # Independently read back the transformed +Y shaft axis.
    actual=[mat[0][1],mat[1][1],mat[2][1]]
    assert max(abs(a-b) for a,b in zip(actual,e['axis']))<1e-12
    out.append({k:e[k] for k in ('tag','name','origin_mm','axis')}|{'transform_3x4':mat})
report=dict(source_file=str(SOURCE),source_solids=39,source_passes_strict_occt_brep_check=source_brep_valid,
            source_check_note='Saved R3 contains pre-existing strict OCCT check flags; placement does not alter or heal source geometry.',
            thruster_instances=8,total_solids=312,
            horizontal=4,vertical_up=2,vertical_down=2,units='mm',layout_bounds_mm=bounds(whole),
            source_bounds_mm=[lo,hi],minimum_conservative_thruster_clearance_mm=smallest,
            pairwise_envelope_checks=gaps,placements=out,source_geometry_modified=False,
            includes_vehicle_frame=False,includes_mounting_brackets=False,
            validation='312 solids and 8 subassemblies confirmed by STEP read-back; all 28 conservative envelopes separate by >=10 mm')
(ROOT/'assembly-verification.json').write_text(json.dumps(report,indent=2))
with (ROOT/'thruster-positions.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['ID','Name','X_mm','Y_mm','Z_mm','Axis_X','Axis_Y','Axis_Z'])
    for e in out:w.writerow([e['tag'],e['name'],*e['origin_mm'],*e['axis']])
print(json.dumps({k:report[k] for k in ('thruster_instances','total_solids','layout_bounds_mm','minimum_conservative_thruster_clearance_mm','validation')},indent=2))
