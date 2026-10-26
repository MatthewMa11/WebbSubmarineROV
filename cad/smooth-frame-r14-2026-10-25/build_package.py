from pathlib import Path
import json, hashlib, zipfile
r=Path(__file__).resolve().parent
for name,n in [('verification.json',21),('assembly-verification.json',2)]:
    report=json.loads((r/name).read_text())
    assert len(report)==n and all(c['passed'] for c in report),name
for name in ['insertion-verification.json','joint-loading-verification.json']:
    assert json.loads((r/name).read_text())['passed'],name
c=json.loads((r/'cleanup-verification.json').read_text());assert len(c)==5 and all(x['passed'] for x in c)
j=json.loads((r/'print-verification.json').read_text())
assert len(j['prints'])==6 and len(j['retained_surface_checks'])==4
assert all(c['passed'] for c in j['retained_surface_checks'])
expected={c['file']:c['sha256'] for c in j['prints']}
assert {p.relative_to(r/'PRINT').as_posix() for p in (r/'PRINT').rglob('*.stl')}==set(expected)
for c in j['prints']:
    f=r/'PRINT'/c['file']
    assert hashlib.sha256(f.read_bytes()).hexdigest()==c['sha256'],c['file']
    if not c.get('unchanged'):
        assert c['closed_manifold'] and c['components']==1
        assert c['relative_volume_error']<0.001
        b=c['print_bounds_mm'];assert abs(b[4])<0.001
        assert all(b[2*k+1]-b[2*k]<=256 for k in range(3))
        assert sum(v['volume_mm3'] for v in c['discarded_export_fragments'])<1e-6
for c in j['prints'][:2]:
    assert c['volume_comparison_basis']=='native Onshape'
saved=(r/'native-saved-version.txt').read_text(encoding='utf-8')
assert '8bf42d2b29fd6d1247b16a59' in saved and 'Instances (47)' in saved
assert 'Versions are view only' in saved
assert 'Status: complete' in (r/'FINAL-REVIEW.txt').read_text()
assert 'No interferences' in (r/'native-interference.txt').read_text(encoding='utf-8')
files=[r/'PRINT'/n for n in expected]
files += [r/n for n in ['ASSEMBLY-AND-PRINT.txt','DESIGN.txt','FINAL-REVIEW.txt',
    'native-version.txt','source-provenance.json','verification.json',
    'assembly-verification.json','print-verification.json','insertion-verification.json',
    'joint-loading-verification.json','cleanup-verification.json',
    'native-interference.txt','native-saved-version.txt',
    'native-volumes.json','native-cone-volume.txt','native-housing-volume.txt',
    'R14-cleaned-detail.png','R14-complete-assembly.png']]
assert not any(f.suffix.lower() in ['.step','.stp'] for f in files)
target=r/'R14-Smooth-Frame-Print-Kit.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(f,f.relative_to(r).as_posix())
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None and len(z.namelist())==len(files)
    for f in files:assert z.read(f.relative_to(r).as_posix())==f.read_bytes()
report=dict(file=target.name,bytes=target.stat().st_size,entries=len(files),
    crc_valid=True,all_entries_match_verified_sources=True,
    print_files=list(expected),sha256=hashlib.sha256(target.read_bytes()).hexdigest())
(r/'package-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

