from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,re,struct
r=Path(__file__).resolve().parent
reports=[json.loads((r/name).read_text(encoding='utf-8')) for name in ('after-mesh-checks.json','native-geometry-checks.json')]
assert all(c['passed'] for report in reports for c in report)
source=(r/'native-after.fs').read_text(encoding='utf-8');local=(r/'thruster-physical-revision.fs').read_text(encoding='utf-8')
assert source==local and source.count('FeatureScript 3095;')==1
native=(r/'native-interference.txt').read_text(encoding='utf-8')
pairs=[line.strip() for line in native.splitlines() if 'text ' in line and '<1> and ' in line]
assert len(pairs)==4 and all('socket propeller screw' in line and 'Motor insert - 22.6' in line for line in pairs)
assert 'Thruster assembly - A2212 fit check ×' in native
assert '360 deg' in (r/'native-360.txt').read_text(encoding='utf-8')
files=sorted((r/'printable-STLs').glob('*.stl'));assert len(files)==4
items=[]
for f in files:
    data=f.read_bytes();n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*n
    items.append(dict(name=f.name,bytes=len(data),triangles=n,sha256=hashlib.sha256(data).hexdigest()))
manifest=dict(revision='R2 - physical print feedback, 2026-10-17',
    mesh_checks=len(reports[0]),native_geometry_checks=len(reports[1]),
    native_rotation_degrees=360,native_assembly_instances=39,
    native_interferences='Only the four intentional M3-to-insert pilot contacts',
    physical_revision_tested=False,files=items)
(r/'R2-manifest.json').write_text(json.dumps(manifest,indent=2))
replacement=r/'A2212-R2-three-replacement-STLs.zip'
with ZipFile(replacement,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for f in files:
        if 'cover' not in f.name.lower():z.write(f,f.name)
    for name in ('READ-ME-BEFORE-PRINTING.txt','physical-test-status.csv','R2-printable-parts.png','R2-manifest.json'):
        z.write(r/name,name)
complete=r/'A2212-R2-complete-CAD-and-verification.zip'
with ZipFile(complete,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for f in files:z.write(f,'printable-STLs/'+f.name)
    for name in ('Thruster-physical-fit-R2.step','native-after.fs','READ-ME-BEFORE-PRINTING.txt',
                 'physical-test-status.csv','R2-printable-parts.png','R2-manifest.json',
                 'after-mesh-checks.json','native-geometry-checks.json',
                 'native-final-assembly.jpg','native-360.jpg','native-360.txt',
                 'native-interference.jpg','native-interference.txt'):
        z.write(r/name,name)
for archive in (replacement,complete):
    with ZipFile(archive) as z:
        assert z.testzip() is None
        for f in files:
            n=f.name if archive==replacement else 'printable-STLs/'+f.name
            if archive==replacement and 'cover' in f.name.lower():continue
            assert hashlib.sha256(z.read(n)).hexdigest()==next(x['sha256'] for x in items if x['name']==f.name)
print(json.dumps(dict(checks=sum(len(report) for report in reports),all_passed=True,
    archives=[dict(name=p.name,bytes=p.stat().st_size) for p in (replacement,complete)],
    physical_fit='R2 awaits a new print and motor hand-spin check'),indent=2))
