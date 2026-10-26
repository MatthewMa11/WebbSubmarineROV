from pathlib import Path
import json,zipfile,hashlib
r=Path(__file__).resolve().parent
for name in ['verification.json','assembly-verification.json']:
 report=json.loads((r/name).read_text(encoding="utf-8"));assert report and all(c['passed'] for c in report),name
assert json.loads((r/'profile-verification.json').read_text(encoding="utf-8"))['passed']
assert not json.loads((r/'profile-negative-control.json').read_text(encoding="utf-8"))['passed']
for p in json.loads((r/'print-verification.json').read_text(encoding="utf-8")):
 if 'closed_manifold' in p:assert p['closed_manifold'] and p['components']==1 and p['stl_step_volume_relative_error']<.001
assert 'No interferences' in (r/'native-interference.txt').read_text(encoding="utf-8")
assert '360 deg' in (r/'native-motion.txt').read_text(encoding="utf-8")
groups=(r/'native-groups.txt').read_text(encoding="utf-8").split('\n\n')
assert len(groups)==2 and [s.count('×') for s in groups]==[40,5]
assert 'Status: complete' in (r/'FINAL-REVIEW.txt').read_text(encoding="utf-8")
files=[r/n for n in ['ASSEMBLY-AND-PRINT.txt','FINAL-REVIEW.txt','DESIGN.txt','Assembly-R10-metal-collet.step','R10-complete-assembly.png','R10-collet-layout.png','verification.json','assembly-verification.json','profile-verification.json','profile-negative-control.json','print-verification.json','native-interference.txt','native-groups.txt','native-motion.txt','native-version.txt']]
files += [r/'PRINT'/n for n in ['Fan-R10-metal-collet.stl','Duct-extension-R10-28mm.stl','TEST-FIRST-R10-6p2-bore.stl','OPTIONAL-unchanged-frame-cap/Frame-R6p1-UNCHANGED.stl','OPTIONAL-unchanged-frame-cap/Cap-R4-UNCHANGED.stl']]
target=r/'R10-Metal-Collet-Print-Kit.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(r).as_posix())
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(files)
 for f in files:assert z.read(f.relative_to(r).as_posix())==f.read_bytes(),f
assert not any('23mm' in f.name for f in files)
report={'zip':target.name,'bytes':target.stat().st_size,'entries':len(files),'crc_valid':True,'all_entries_match_verified_sources':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(r/'package-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
