"""Independent closure of exported cutting paths and vertical flow checks."""
from pathlib import Path
import sys,json,math,collections
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parents[2]/'robotic FTC 2026-2027/cad/.vendor'))
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
meta=json.loads((R/'frame-pod-verification.json').read_text());proof=[]
for path in sorted((R/'laser-cut-DXF').glob('*.dxf')):
    lines=path.read_text().splitlines();assert len(lines)%2==0
    pairs=[(int(lines[i]),lines[i+1]) for i in range(0,len(lines),2)]
    assert (9,'$INSUNITS') in pairs and pairs[pairs.index((9,'$INSUNITS'))+1]==(70,'4')
    start=pairs.index((2,'ENTITIES'))+1;entities=[];current=None
    for code,value in pairs[start:]:
        if code==0:
            if current:entities.append(current)
            if value=='ENDSEC':break
            current=[value,{}]
        elif current:current[1][code]=value
    graph=collections.Counter();circles=0
    for kind,values in entities:
        assert values.get(8)=='CUT' and kind in ('LINE','CIRCLE'),(path,kind)
        if kind=='LINE':
            a=tuple(round(float(values[n]),6) for n in (10,20));b=tuple(round(float(values[n]),6) for n in (11,21))
            assert a!=b;graph[a]+=1;graph[b]+=1
        else:assert float(values[40])>0;circles+=1
    assert graph and all(n==2 for n in graph.values()),(path,{k:v for k,v in graph.items() if v!=2})
    proof.append(dict(file=path.name,cut_entities=len(entities),circles=circles,line_endpoints_all_degree_two=True,units='mm'))
assert len(proof)==5
flow=[]
for x in (-75,75):
    for y in (-170,170):
        gauge=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,-100),gp_Dir(0,0,1)),38,300).Shape();blocked=0
        for item in meta['added_parts']:
            if item['kind']!='laser-cut sheet':continue
            s=TopoDS_Shape();assert BRepTools.Read_s(s,str(R/'native-breps'/(item['name']+'.brep')),BRep_Builder())
            op=BRepAlgoAPI_Common(gauge,s);op.Build();assert op.IsDone()
            props=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),props);blocked+=abs(props.Mass())
        assert blocked<1e-4,(x,y,blocked)
        flow.append(dict(axis_xy_mm=[x,y],clear_diameter_mm=76,obstruction_volume_mm3=blocked))
meta.update(sheet_material='3 mm aluminum - selected by user',exported_dxf_closure_checks=proof,vertical_flow_checks=flow)
(R/'frame-pod-verification.json').write_text(json.dumps(meta,indent=2))
print('PASS: all five DXFs contain closed CUT paths in millimetres.')
print('PASS: all four vertical thruster axes retain a clear 76 mm diameter passage through the new frame.')
