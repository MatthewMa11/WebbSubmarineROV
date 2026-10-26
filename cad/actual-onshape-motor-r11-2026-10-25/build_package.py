from pathlib import Path
import json,zipfile,hashlib
r=Path(__file__).resolve().parent
for name in ['verification.json','assembly-verification.json']:
 report=json.loads((r/name).read_text(encoding="utf-8"));assert report and all(c['passed'] for c in report),name
assert json.loads((r/'profile-verification.json').read_text(encoding="utf-8"))['passed']
assert not json.loads((r/'profile-negative-control.json').read_text(encoding="utf-8"))['passed']
for p in json.loads((r/'print-verification.json').read_text(encoding="utf-8")):
 if 'closed_manifold' in p:assert p['closed_manifold'] and p['components']==1 and p['stl_step_volume_relative_error']<.001
for p in json.loads((r/'print-verification.json').read_text(encoding='utf-8')):
 f=r/'PRINT'/p['file']
 expected=p.get('sha256',p.get('unchanged_sha256'))
 assert expected and hashlib.sha256(f.read_bytes()).hexdigest()==expected,f
assert '75c1dcfd63b352df99b31e2f' in (r/'native-saved-version.txt').read_text(encoding='utf-8')
assert 'Instances (48)' in (r/'native-saved-version.txt').read_text(encoding='utf-8')
assert 'No interferences' in (r/'native-interference.txt').read_text(encoding="utf-8")
assert '360 deg' in (r/'native-motion.txt').read_text(encoding="utf-8")
assert (r/'native-fixed-group.txt').read_text(encoding='utf-8').count('\u00d7')==44
assert (r/'native-rotating-group.txt').read_text(encoding='utf-8').count('\u00d7')==4
assert 'Status: complete' in (r/'FINAL-REVIEW.txt').read_text(encoding='utf-8')
files=[r/n for n in ['ASSEMBLY-AND-PRINT.txt','FINAL-REVIEW.txt','DESIGN.txt','Assembly-R11-actual-models.step','R11-complete-assembly.png','R11-actual-model-layout.png','verification.json','assembly-verification.json','profile-verification.json','profile-negative-control.json','print-verification.json','native-interference.txt','native-fixed-group.txt','native-rotating-group.txt','source-provenance.json','source-contact-report.json','native-motion.txt','native-version.txt','native-saved-version.txt']]
files += [r/'PRINT'/n for n in ['Fan-R11-actual-adapter.stl','Duct-extension-R10-28mm.stl','TEST-FIRST-R11-5p1-bore.stl','OPTIONAL-unchanged-frame-cap/Frame-R6p1-UNCHANGED.stl','OPTIONAL-unchanged-frame-cap/Cap-R4-UNCHANGED.stl']]
target=r/'R11-Actual-Onshape-Motor-Print-Kit.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(r).as_posix())
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(files)
 for f in files:assert z.read(f.relative_to(r).as_posix())==f.read_bytes(),f
assert not any(('23mm' in f.name or 'Fan-R10' in f.name or '6p2-bore' in f.name or 'source-stage.step' in f.name) for f in files)
report={'zip':target.name,'bytes':target.stat().st_size,'entries':len(files),'crc_valid':True,'all_entries_match_verified_sources':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(r/'package-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
