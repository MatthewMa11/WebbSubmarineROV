from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,struct
r=Path(__file__).resolve().parent
names=['cup-mesh-checks.json','cup-native-checks.json','inherited-mesh-checks.json','inherited-native-checks.json']
reports=[json.loads((r/n).read_text(encoding='utf-8')) for n in names]
assert all(q['passed'] for report in reports for q in report)
source=(r/'native-after.fs').read_text(encoding='utf-8')
assert source==(r/'thruster-centering-cup.fs').read_text(encoding='utf-8') and source.count('FeatureScript 3095;')==1
interference=(r/'native-interference.txt').read_text(encoding='utf-8')
pairs=[line for line in interference.splitlines() if 'text ' in line and '<1> and ' in line]
assert len(pairs)==4 and all('socket propeller screw' in q and 'Motor insert' in q for q in pairs)
motion=(r/'native-360.txt').read_text(encoding='utf-8')
assert 'text field (disabled) 360 deg' in motion and 'Instances (39)' in motion
files=sorted((r/'printable-STLs').glob('*.stl'));assert len(files)==4
manifest=[]
for f in files:
    data=f.read_bytes();triangles=struct.unpack_from('<I',data,80)[0];assert len(data)==84+triangles*50
    if 'Nozzle' not in f.name:
        assert data==(r.parent/'print-revision-2026-10-17/printable-STLs'/f.name).read_bytes()
    manifest.append(dict(file=f.name,bytes=len(data),triangles=triangles,sha256=hashlib.sha256(data).hexdigest()))
info=dict(revision='R3 permanent stationary motor centering cup',checks=sum(map(len,reports)),all_passed=True,
    assembly_instances=39,native_rotation_degrees=360,physical_revision_tested=False,files=manifest)
(r/'R3-manifest.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
archive=r/'A2212-R3-centering-cover-print-files.zip'
with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for f in files:z.write(f,'printable-STLs/'+f.name)
    for n in names+['READ-ME-CENTERING-CUP.txt','R3-manifest.json','Thruster-centering-cup-R3.step',
                    'native-after.fs','native-360.txt','native-interference.txt','native-cup-closeup.jpg']:
        z.write(r/n,n)
with ZipFile(archive) as z:
    assert z.testzip() is None
    for f in files:assert z.read('printable-STLs/'+f.name)==f.read_bytes()
print(json.dumps(dict(checks=info['checks'],all_passed=True,archive=archive.name,bytes=archive.stat().st_size,
                     nozzle_stl=(r/'Nozzle-centering-cup-R3.stl').name,physical_fit='Awaiting print and motor fit check'),indent=2))
