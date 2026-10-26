from pathlib import Path
import json,hashlib,zipfile
r=Path(__file__).resolve().parent
for name in ['verification.json','assembly-verification.json']:
 report=json.loads((r/name).read_text());assert report and all(c['passed'] for c in report),name
j=json.loads((r/'print-verification.json').read_text());h=j['housing'];assert h['closed_manifold'] and h['components']==1 and h['removed_volume_mm3']<1e-6
assert all(c['passed'] for c in j['retained_source_surfaces'])
expected={'Housing-R12-one-piece.stl':h['sha256']};expected.update({c['file']:c['sha256'] for c in j['unchanged_prints']})
assert set(p.name for p in (r/'PRINT').glob('*.stl'))==set(expected)
assert len(expected)==4
for name,sha in expected.items():assert hashlib.sha256((r/'PRINT'/name).read_bytes()).hexdigest()==sha,name
assert json.loads((r/'insertion-verification.json').read_text())['passed']
assert '46cfeee110ebcedd02908155' in (r/'native-saved-version.txt').read_text(encoding='utf-8')
assert 'Status: complete' in (r/'FINAL-REVIEW.txt').read_text(encoding='utf-8')
assert 'Instances (47)' in (r/'native-saved-version.txt').read_text(encoding='utf-8')
assert 'No interferences' in (r/'native-interference.txt').read_text(encoding='utf-8')
files=[r/'PRINT'/n for n in expected]
files += [r/n for n in ['ASSEMBLY-AND-PRINT.txt','DESIGN.txt','FINAL-REVIEW.txt','native-version.txt','source-provenance.json','verification.json','assembly-verification.json','print-verification.json','legacy-step-reader-status.json','insertion-verification.json','native-fixed-group.txt','native-rotating-group.txt','native-interference.txt','native-motion.txt','native-saved-version.txt','R12-complete-assembly.png','R12-one-housing-selected.png']]
assert not any(f.suffix.lower() in ['.step','.stp'] for f in files)
target=r/'R12-One-Piece-Housing-Print-Kit.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(r).as_posix())
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None and len(z.namelist())==len(files)
 for f in files:assert z.read(f.relative_to(r).as_posix())==f.read_bytes()
report=dict(file=target.name,bytes=target.stat().st_size,entries=len(files),crc_valid=True,all_entries_match_verified_sources=True,print_files=list(expected),sha256=hashlib.sha256(target.read_bytes()).hexdigest())
(r/'package-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
