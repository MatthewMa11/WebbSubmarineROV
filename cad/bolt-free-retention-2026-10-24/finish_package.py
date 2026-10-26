from pathlib import Path
import json,hashlib,zipfile,shutil
r=Path(__file__).resolve().parent
version='9eea26e83ee0486d05561043'
url=f'https://cad.onshape.com/documents/80535e3f457f805ec76c4df1/v/{version}/e/51ff5b1cdf93eadbe7b0e553'
reports={name:json.loads((r/name).read_text()) for name in ('verification.json','thread-travel.json','print-mesh-checks.json','structure-audit.json')}
assert all(c['passed'] for report in reports.values() for c in report)
notes='''R7 ENGINEERING NOTES - 25 October 2026

Approved change: replace the two external bolt ears and their six metal parts
with a compression collar and counter-tightened jam ring. Keep the four solid
motor keys and leave the internal spacer region empty. Frame and cap preserved.

Verified on exported final native geometry:
29 geometry/interface/mesh checks, 4 thread/travel checks, 4 printable mesh
checks and 6 structural checks pass. Native Onshape: 43 assembly instances,
no interferences, and a 360-degree revolute animation with rotor, fan and both
rings in one rotating group. The 36 stationary fasteners retain their poses.

Design rulings and their consequences:
1. Preserve existing blade-root material inside the conical sleeve. A smaller
   cone would cut blade connections. Cost: a larger central hub.
2. A solid rounded runout shoulder supports the last partial thread and stops
   excessive nut travel. Cost: limited tightening travel; do not force it shut.
3. Use explicit radial thread sections every 15 degrees after free and locked
   sweeps failed the geometry checks. Cost: custom printed thread geometry,
   rather than a standard fastener thread. Matching and further advance pass.
4. Use a 43 mm central-sleeve envelope check for the 41.7 mm shoulder, replacing
   the abandoned 40 mm target. This remains below the old 50.4 mm bolt-ear span.
5. Ring OD46 retains approximately 2 mm minimum wall near forward flutes and
   thread, rather than approximately 1 mm at OD44. Cost: 1 mm extra radius.
   Its outside annular envelope clears blade roots by 0.3815 mm through the
   estimated clamp travel. Nominal rotating clearances are checked separately.
6. Preserve the two tiny inherited blade-tip STEP sliver faces instead of
   changing blade geometry. Their invalid-face bounds match R6.1 exactly.
   Edited sleeve faces and both complete rings pass B-rep checks; native STL
   and print-oriented STL meshes are closed, manifold, and single-component.
   The whole legacy STEP retains import validity limitations.
7. Correct loading order: main collar FIRST from the smaller rear sleeve end,
   then jam ring. Assemble and lock the coupling outside the frame for access,
   then fit the motor/fan unit and tighten the existing motor-base screws.

Fresh read-only review found no new concrete geometry defect. Its incorrect
ring-loading instruction finding was corrected in both README copies. The
planning-status metadata is updated, and STEP limitations are included in the
print README. No remaining editorial review findings are deferred.

What remains physically unverified:
Actual bell diameter, printed thread feel, grip/pull-off force, elastic finger
deflection and bell distortion, PLA creep/heating/fatigue, balance and operating
speed. Practical tightening depends on the user's hand access and print. The
coupling is tightened outside the frame to improve access. A 0.15 mm additional
rigid screw advance is verified; the further 0.833 mm contact estimate is not an
elastic simulation or a measured clamping force. These are prototype files,
not a guarantee of secure powered operation. Test the coupon and actual motor.

The coupon preserves the thread and bell-bore dimensions, but uses a shorter
connecting ring. It tests diameters/thread fit only, not full-fan flexibility
or retention strength. It is not installed in the final thruster.
'''
(r/'ENGINEERING-NOTES.txt').write_text(notes,encoding='utf-8')
status=dict(status='CAD_checked_prototype_physical_validation_required',geometry_changed=True,workspace='a7e338b31063b1177578abb2',saved_version=version,saved_assembly_url=url,baseline_workspace='33449ef7e87a1027c0d498b3',baseline_version='da7c2535cd1e6a3484508358',native_instances=43,mechanical_bodies=7,stationary_fasteners=36,rotating_group=['rotor','fan','compression collar','jam ring'],internal_spacer=False,clamp_bolts=False,printed_rings=2,checks={k:dict(passed=sum(c['passed'] for c in v),total=len(v)) for k,v in reports.items()},physical_strength_verified=False,legacy_STEP_limitation='Inherited blade-tip slivers and cap/nozzle import flags; edited faces and ring B-reps checked separately.')
(r/'design-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
ref=r/'print'/'reference';ref.mkdir(exist_ok=True)
for name in ('Thruster-R7-bolt-free.step','ENGINEERING-NOTES.txt','verification.json','thread-travel.json','print-mesh-checks.json','structure-audit.json','design-status.json'):
 shutil.copy2(r/name,ref/name)
(r/'print'/'Onshape-R7.txt').write_text(url+'\n',encoding='utf-8')
manifest={str(p.relative_to(r/'print')).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((r/'print').rglob('*')) if p.is_file() and p.name!='SHA256.json'}
(r/'print'/'SHA256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=r/'A2212-R7-bolt-free-print-files.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted((r/'print').rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(r/'print')))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print('PACKAGED',archive,'bytes',archive.stat().st_size,'verified files',len(manifest),flush=True)
print('SAVED VERSION',version,flush=True)
