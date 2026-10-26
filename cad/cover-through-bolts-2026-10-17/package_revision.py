from pathlib import Path
import json,hashlib,zipfile,re
r=Path(__file__).resolve().parent
reports=[json.loads((r/n).read_text()) for n in ('joint-checks.json','mesh-checks.json')]
assert all(q['passed'] for report in reports for q in report)
assert sum(map(len,reports))==30
group=(r/'stationary-group.txt').read_text(encoding='utf-8')
members=[s for s in group.splitlines() if re.search(r'text .+<1> ×$',s)]
assert len(members)==39,len(members)
motion=(r/'native-360.txt').read_text(encoding='utf-8')
assert 'text field (disabled) 360 deg' in motion
interf=(r/'native-interference.txt').read_text(encoding='utf-8')
contacts=[s.strip() for s in interf.splitlines() if 'text ' in s and ' and ' in s and 'Motor insert - ' in s]
assert len(contacts)==4 and all('M3x8 socket propeller screw' in s for s in contacts)
source=(r/'native-after.fs').read_text(encoding='utf-8')
assert source.count('FeatureScript 3095;')==1
assert source==(r/'thruster-through-bolts.fs').read_text(encoding='utf-8')
files=list((r/'printable-STLs').glob('*.stl'))
assert len(files)==4
files += [r/'READ-ME-THROUGH-BOLTS.txt',r/'Thruster-cover-through-bolts-R4-verified.step',r/'native-after.fs',r/'joint-checks.json',r/'mesh-checks.json',r/'native-bolted-cover.png',r/'native-360.jpg',r/'native-interference.jpg']
manifest={'revision':'R4 four cover through-bolt joints','date':'2026-10-17','units':'mm','scale_percent':100,'passed_checks':30,'native_solids':46,'stationary_group':39,'rotating_group':7,'full_rotation_degrees':360,'native_interference':'Four intentional propeller-screw / printed-spacer pilot contacts only','reprint':['Nozzle-M3-through-bolts-R4.stl','Front-cover-M3-through-tabs-R4.stl'],'cover_hardware':{'M3x12_socket_cap':4,'M3_flat_washer_OD7_ID3p2_t0p5':8,'M3_hex_nut_AF5p5_h2p4':4},'physical_validation':'Pending print and fit on actual motor','files':{str(f.relative_to(r)):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files}}
(r/'R4-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');files.append(r/'R4-manifest.json')
out=r/'A2212-R4-through-bolts-print-files.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files:z.write(f,f.relative_to(r))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len([n for n in z.namelist() if n.endswith('.stl')])==4
print(json.dumps({'archive':str(out.resolve()),'bytes':out.stat().st_size,'passed_checks':30,'stationary_members':len(members),'files':len(files)}))
