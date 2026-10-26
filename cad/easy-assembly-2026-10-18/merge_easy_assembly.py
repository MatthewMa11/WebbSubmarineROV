"""Keep original thruster STEP surfaces and add the flat frame/pod assembly."""
from pathlib import Path
import sys,re,json,math
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parents[2]/'robotic FTC 2026-2027/cad/.vendor'))
from OCP.STEPControl import STEPControl_Reader
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.collections import Sequence_TDF_Label
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

old=R.parent/'eight-thruster-assembly-2026-10-17/ROV8-native.step'
text=old.read_text();frame=(R/'frame-pod-parts.step').read_text()
def parse(s):return {int(n):b.strip() for n,b in re.findall(r'#(\d+)\s*=(.*?);',s,re.S)}
entities=parse(text);fentities=parse(frame);next_id=max(entities)+10;extra=[];changed={}
def refs(body):return [int(n) for n in re.findall(r'#(\d+)',body)]
def add(body):
    global next_id
    next_id+=1;extra.append(f'#{next_id}={body};');return next_id
def link_for_product(es,product_name):
    prod=next(n for n,b in es.items() if b.startswith('PRODUCT(') and "'"+product_name+"'" in b)
    formation=next(n for n,b in es.items() if b.startswith('PRODUCT_DEFINITION_FORMATION(') and prod in refs(b))
    pd=next(n for n,b in es.items() if b.startswith('PRODUCT_DEFINITION(') and formation in refs(b))
    pds=next(n for n,b in es.items() if b.startswith('PRODUCT_DEFINITION_SHAPE(') and refs(b)==[pd])
    rep=next(refs(b)[1] for n,b in es.items() if b.startswith('SHAPE_DEFINITION_REPRESENTATION(') and refs(b)[0]==pds)
    origin=refs(es[rep])[0]
    return pd,rep,origin
parent_pd,parent_rep,parent_origin=link_for_product(entities,'ROV - 8 thrusters - 4 diagonal + 4 vertical')
frame_pd,frame_rep,frame_origin=link_for_product(fentities,'Easy frame and removable electronics pod')

# The source is in metres. Only the eight assembly-placement transforms change.
selected=[(n,b) for n,b in entities.items() if b.startswith('NEXT_ASSEMBLY_USAGE_OCCURRENCE(') and ('M4 flat washer' in b or 'M4x12 socket mounting bolt' in b)]
assert len(selected)==8,len(selected)
root_rep_body=entities[22337]
for occurrence,body in selected:
    pds=next(n for n,b in entities.items() if b.startswith('PRODUCT_DEFINITION_SHAPE(') and refs(b)[-1]==occurrence)
    cdsr=next(b for n,b in entities.items() if b.startswith('CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(') and refs(b)[1]==pds)
    relation=entities[refs(cdsr)[0]]
    transform_id=int(re.search(r'REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION\(#(\d+)\)',relation).group(1))
    first,target_axis=refs(entities[transform_id])
    ar=refs(entities[target_axis]);point=entities[ar[0]]
    vals=[float(v) for v in re.search(r'\(([-+\d.Ee,\s]+)\)\s*\)',point).group(1).split(',')]
    assert len(vals)==3;vals[2]-=.003
    new_point=add("CARTESIAN_POINT('',("+','.join(f'{v:.16g}' for v in vals)+'))')
    new_axis=add("AXIS2_PLACEMENT_3D('',"+','.join('#'+str(n) for n in [new_point,*ar[1:]])+')')
    changed[transform_id]=re.sub(r'#'+str(target_axis)+r'\b','#'+str(new_axis),entities[transform_id])
    root_rep_body=re.sub(r'#'+str(target_axis)+r'\b','#'+str(new_axis),root_rep_body)
changed[22337]=root_rep_body
newtitle='ROV - easy assembly - five panels'
for n,b in entities.items():
    if 'ROV - 8 thrusters - 4 diagonal + 4 vertical' in b:
        changed[n]=b.replace('ROV - 8 thrusters - 4 diagonal + 4 vertical',newtitle)
    elif b.startswith('PRODUCT(') and "'Thruster assembly - A2212 fit check'" in b:
        changed[n]=b.replace('Thruster assembly - A2212 fit check','A2212 R3 - 3 mm mounting plates')
for n,b in changed.items():
    text=re.sub(r'#'+str(n)+r'\s*=.*?;',lambda m:f'#{n}={b};',text,count=1,flags=re.S)

# Remap only entity IDs. New simple surfaces remain the writer's original data.
offset=next_id+100
payload=frame.split('DATA;',1)[1].rsplit('ENDSEC;',1)[0]
payload=re.sub(r'#(\d+)',lambda m:'#'+str(int(m.group(1))+offset),payload)
next_id=max(fentities)+offset+10
fpd,frep,forigin=[n+offset for n in (frame_pd,frame_rep,frame_origin)]
nauo=add(f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('FRAME','Easy frame and removable electronics pod','',#{parent_pd},#{fpd},'')")
pds=add(f"PRODUCT_DEFINITION_SHAPE('','',#{nauo})")
tr=add(f"ITEM_DEFINED_TRANSFORMATION('','',#{forigin},#{parent_origin})")
rel=add(f"(REPRESENTATION_RELATIONSHIP('','',#{frep},#{parent_rep}) REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(#{tr}) SHAPE_REPRESENTATION_RELATIONSHIP())")
add(f'CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#{rel},#{pds})')
idx=text.rfind('ENDSEC;');target=R/'ROV-easy-assembly.step'
target.write_text(text[:idx]+'\n'+payload+'\n'+'\n'.join(extra)+'\n'+text[idx:])

rd=STEPControl_Reader();assert int(rd.ReadFile(str(target)))==1;rd.TransferRoots();shape=rd.OneShape()
ex=TopExp_Explorer(shape,TopAbs_SOLID);solids=0
while ex.More():solids+=1;ex.Next()
assert solids==368,solids
b=Bnd_Box();BRepBndLib.AddOptimal_s(shape,b,False,False)
bounds=[[p.X(),p.Y(),p.Z()] for p in (b.CornerMin(),b.CornerMax())]
assert max(abs(v-w) for v,w in zip(bounds[0][:2],[-260,-250]))<1e-4,bounds
assert max(abs(v-w) for v,w in zip(bounds[1][:2],[260,250]))<1e-4,bounds
doc=TDocStd_Document(TCollection_ExtendedString('XCAF'));r=STEPCAFControl_Reader();r.ReadFile(str(target));assert r.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main());roots=Sequence_TDF_Label();st.GetFreeShapes(roots);assert roots.Length()==1
cs=Sequence_TDF_Label();st.GetComponents_s(roots.Value(1),cs);assert cs.Length()==9,cs.Length()
meta=json.loads((R/'frame-pod-verification.json').read_text())
meta.update(native_step_file=target.name,native_step_solids=solids,native_root_components=cs.Length(),assembled_bounds_mm=bounds,
            original_thruster_geometry_entities_reserialized=False,mounting_bolt_and_washer_transforms_changed_per_thruster=8)
(R/'frame-pod-verification.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(dict(solids=solids,root_components=cs.Length(),bounds_mm=bounds,file=str(target))))
