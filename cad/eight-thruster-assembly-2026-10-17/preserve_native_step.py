"""Add outer placements without rewriting any original Onshape B-rep entity."""
from pathlib import Path
import json,re,sys
from zipfile import ZipFile,ZIP_DEFLATED
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r.parents[2]/'robotic FTC 2026-2027/cad/.vendor'))
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
report=json.loads((r/'assembly-verification.json').read_text())
source=Path(report['source_file']).read_text()
entities={int(n):b for n,b in re.findall(r'#(\d+)\s*=(.*?);',source,re.S)}
highest=max(entities);counter=highest
added=[]
def add(body):
    global counter
    counter+=1;added.append(f'#{counter}={body};');return counter
def refs(n):return [int(x) for x in re.findall(r'#(\d+)',entities[n])]
def numbers(v):return ','.join('0.' if abs(x)<1e-13 else f'{x:.15g}' if abs(x)>=1e-3 else f'{x:.15e}' for x in v)
root_pd=49828;root_rep=22337;origin=22377;context=49666
assert 'Thruster assembly - A2212 fit check' in entities[root_rep]
formation,definition_context=refs(root_pd)
old_product=refs(formation)[0];product_context=refs(old_product)[0]
title='ROV - 8 thrusters - 4 diagonal + 4 vertical'
product=add(f"PRODUCT('{title}','{title}','',(#{product_context}))")
formation=add(f"PRODUCT_DEFINITION_FORMATION('','',#{product})")
pd=add(f"PRODUCT_DEFINITION('','',#{formation},#{definition_context})")
pds=add(f"PRODUCT_DEFINITION_SHAPE('','',#{pd})")
placements=[]
for e in report['placements']:
    m=e['transform_3x4'];pos=[m[i][3]/1000 for i in range(3)]
    p=add(f"CARTESIAN_POINT('',({numbers(pos)}))")
    z=add(f"DIRECTION('',({numbers([m[i][2] for i in range(3)])}))")
    x=add(f"DIRECTION('',({numbers([m[i][0] for i in range(3)])}))")
    placements.append(add(f"AXIS2_PLACEMENT_3D('',#{p},#{z},#{x})"))
rep=add(f"SHAPE_REPRESENTATION('{title}',(#{origin},"+','.join(f'#{n}' for n in placements)+f'),#{context})')
add(f'SHAPE_DEFINITION_REPRESENTATION(#{pds},#{rep})')
for e,place in zip(report['placements'],placements):
    name=e['name']
    nauo=add(f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('{e['tag']}','{name}','{name}',#{pd},#{root_pd},'')")
    shape=add(f"PRODUCT_DEFINITION_SHAPE('','',#{nauo})")
    tr=add(f"ITEM_DEFINED_TRANSFORMATION('','',#{origin},#{place})")
    rel=add(f"(REPRESENTATION_RELATIONSHIP('','',#{root_rep},#{rep}) REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(#{tr}) SHAPE_REPRESENTATION_RELATIONSHIP())")
    add(f'CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#{rel},#{shape})')
target=r/'ROV8-native.step'
idx=source.rfind('ENDSEC;')
target.write_text(source[:idx]+'\n/* Eight layout occurrences; original geometry entities preserved. */\n'+'\n'.join(added)+'\n'+source[idx:])
reader=STEPControl_Reader();assert int(reader.ReadFile(str(target)))==1;reader.TransferRoots();s=reader.OneShape()
ex=TopExp_Explorer(s,TopAbs_SOLID);count=0
while ex.More():count+=1;ex.Next()
assert count==312,count
b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b,False,False)
bounds=[[p.X(),p.Y(),p.Z()] for p in (b.CornerMin(),b.CornerMax())]
assert max(abs(a-b) for aa,bb in zip(bounds,report['layout_bounds_mm']) for a,b in zip(aa,bb))<1e-5,bounds
doc=TDocStd_Document(TCollection_ExtendedString('XCAF'));rd=STEPCAFControl_Reader();rd.ReadFile(str(target));assert rd.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main());roots=Sequence_TDF_Label();st.GetFreeShapes(roots);assert roots.Length()==1
cs=Sequence_TDF_Label();st.GetComponents_s(roots.Value(1),cs);assert cs.Length()==8
report['native_preserving_step']='ROV8-native.step';report['original_step_entities_preserved']=len(entities)
(r/'assembly-verification.json').write_text(json.dumps(report,indent=2))
with ZipFile(r/'ROV8-native.zip','w',ZIP_DEFLATED) as z:z.write(target,target.name)
print(json.dumps(dict(solids=count,thrusters=cs.Length(),bounds_mm=bounds,preserved_entities=len(entities))))
