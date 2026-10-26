from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,re,csv

r=Path(__file__).resolve().parent
reports=['pla-after.json','pla-mount-regression.json','pla-wire-regression.json']
checks=[c for f in reports for c in json.loads((r/f).read_text())['checks']]
assert len(checks)==35 and all(c['pass'] for c in checks)
meshes=json.loads((r/'pla-mesh-check.json').read_text())
assert len(meshes)==10 and all(m['watertight_and_consistently_oriented'] and m['components']==1 and not m['degenerate_triangles'] and m['volume_mm3']>0 for m in meshes)
meta=json.loads((r/'pla-native-verification.json').read_text())
assert meta['interference_selected_instance_count']==39 and meta['observed_animation_end_degrees']==360
native=(r/'pla-native-interference.txt').read_text()
pairs=[line.strip() for line in native.splitlines() if re.search(r' text .*<1> and .*<1>',line)]
assert len(pairs)==4,pairs
assert all('Motor insert' in line and 'M3x8 socket propeller screw' in line for line in pairs)
assert (r/'thruster_print_fit_pla.fs').read_text().strip()==(r/'thruster-pla-native-verified.fs').read_text().strip()
assert (r/'thruster-pla-native-verified.fs').read_text().count('FeatureScript 3095;')==1
with (r/'physical-fit-record.csv').open(newline='') as f:assert all(row['Status']=='NOT TESTED' for row in csv.DictReader(f))

manifest={'date':'2026-10-15','printer':'Bambu Lab P1S','material':'PLA Basic',
          'cad_checks_passed':35,'cad_checks_total':35,'native_assembly_solids':39,
          'modeled_screws':15,'added_hardware_solids':17,'native_rotation_degrees':360,
          'native_interference_pairs':pairs,'unintended_interference_pairs':0,
          'closed_print_meshes':10,'full_part_meshes':4,'fit_test_meshes':6,
          'gray_cover_geometry_changed':False,'physical_validation':'NOT TESTED',
          'files':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for folder in ('full-print-parts','fit-check-first') for p in sorted((r/folder).glob('*.stl'))}}
(r/'PLA-revision-manifest.json').write_text(json.dumps(manifest,indent=2))
shared=['START-HERE-P1S-PLA.txt','PLA-hardware-BOM.csv','physical-fit-record.csv','fit-check-preview.png','fit-piece-manifest.json']
proof=['CAD-verification-notes.txt','PLA-revision-manifest.json','Thruster-A2212-PLA-complete.step',
       'pla-after.json','pla-mount-regression.json','pla-wire-regression.json','pla-mesh-check.json',
       'pla-native-verification.json','pla-native-interference.txt','pla-native-interference.jpg',
       'pla-animation-360.jpg','pla-final-assembly.jpg','thruster-pla-native-verified.fs']
full=r/'A2212-P1S-PLA-CAD-and-fit-tests.zip';fit=r/'P1S-PLA-fit-check-first.zip'
with ZipFile(full,'w',ZIP_DEFLATED) as z:
    for folder in ('full-print-parts','fit-check-first'):
        for p in sorted((r/folder).glob('*.stl')):z.write(p,str(p.relative_to(r)))
    for name in shared+proof:z.write(r/name,name)
with ZipFile(fit,'w',ZIP_DEFLATED) as z:
    for p in sorted((r/'fit-check-first').glob('*.stl')):z.write(p,p.name)
    for name in shared:z.write(r/name,name)
for p in (full,fit):
    with ZipFile(p) as z:assert z.testzip() is None
print(json.dumps({'cad_checks':'35/35','meshes':'10 closed, single-component meshes','physical_tests':'NOT TESTED',
                  'archives':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (full,fit)]},indent=2))
