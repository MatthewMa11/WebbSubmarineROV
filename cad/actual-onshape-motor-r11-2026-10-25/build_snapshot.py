"""Exact rigid-copy snapshot; no metal surfaces are reconstructed or edited."""
from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];ss=ns['solids'](r/'SOURCE-Motor-assembly.step')
from OCP.gp import gp_Trsf,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
stage=gp_Trsf();stage.SetTranslation(gp_Vec(0,200,0))
compound=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(compound)
items=[]
for name,index in [('Actual motor fused body',4),('Actual collet thread',1),('Actual prop collar',7),('Actual bullet nut',2)]:
 source=ss[index];copied=BRepBuilderAPI_Transform(source,stage,True).Shape();builder.Add(compound,copied)
 assert abs(t.volume(source)-t.volume(copied))<1e-6
 items.append({'name':name,'source_solid_index':index,'source_bounds_mm':t.limits(source),'source_volume_mm3':t.volume(source),'source_area_mm2':t.area(source),'staging_translation_mm':[0,200,0]})
Interface_Static.SetCVal_s('write.step.schema','AP214IS')
Interface_Static.SetCVal_s('write.step.unit','MM')
writer=STEPControl_Writer();assert writer.Transfer(compound,STEPControl_AsIs)==IFSelect_RetDone
target=r/'R11-actual-Motor-source-stage.step';assert writer.Write(str(target))==IFSelect_RetDone
assert len(ns['solids'](target))==4
report={'source_document':'0ff4892958a7b27bdfa13caa','source_assembly_element':'10199497d26cbfa5205bde9c','source_file_sha256':hashlib.sha256((r/'SOURCE-Motor-assembly.step').read_bytes()).hexdigest(),'snapshot_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'items':items,'omitted':['optional cross mounting plate; existing frame supplies mount','three flexible straight leads; routing is not represented by their source straight geometry']}
(r/'source-provenance.json').write_text(json.dumps(report,indent=2))
print('Four actual source solids copied without geometry edits:',target.name)
