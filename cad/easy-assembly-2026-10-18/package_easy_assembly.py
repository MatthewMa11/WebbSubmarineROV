from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,csv
R=Path(__file__).resolve().parent
m=json.loads((R/'frame-pod-verification.json').read_text())
assert m['native_step_solids']==368 and m['native_root_components']==9
assert len(m['laser_cut_parts'])==5 and m['unique_laser_profiles']==3
assert m['frame_joint_bolts']==8 and m['added_solids']==56
assert all(c['passed'] for c in m['checks']) and all(c['passed'] for c in m['added_checks'])
assert m['continuous_pod_lift_check']['passed']
paths=sorted((R/'laser-cut-unique').glob('*.dxf'));assert len(paths)==3
with (R/'cutting-and-hardware-list.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Item','Quantity','Specification','Notes'])
    w.writerows([
        ['A base',1,'3 mm aluminum; 520 x 500 mm','A-base-QTY1.dxf'],
        ['B side plate',2,'3 mm aluminum; about 240 x 84 mm','Identical pair; B-side-plate-QTY2.dxf'],
        ['C open saddle',2,'3 mm aluminum; about 190 x 79 mm','Identical pair; C-open-saddle-QTY2.dxf'],
        ['Frame bolt',8,'M4x16 socket head','Replaces the 24 M3 frame-joint bolts'],
        ['Frame washer',8,'M4; 9 OD x 4.3 ID x 0.8 thick mm','Under bolt heads'],
        ['Frame hex nut',8,'M4; AF7 x 3.2 thick mm','Accessible cross pockets'],
        ['Release strap',2,'25 mm adjustable webbing; side-release buckle','Purchased layout reference; select suitable retention rating'],
        ['Complete electronics pod',1,'Existing 160 OD x 148 ID x 200 mm tube, two caps, four tie rods','Retained; not pressure-qualified'],
        ['Complete A2212 thruster',8,'Existing 39-body R3 subassemblies','Positions and internals retained']])
names=['ROV-easy-assembly.step','READ-ME.txt','ASSEMBLY-4-STEPS.txt','cutting-and-hardware-list.csv',
       'frame-pod-verification.json','easy-assembly-preview.png','laser-cut-profile-preview.png']
if (R/'onshape-easy-assembly.png').exists():names.append('onshape-easy-assembly.png')
paths += [R/n for n in names]
dest=R/'ROV-easy-assembly-CAD-DXF-and-guide.zip'
with ZipFile(dest,'w',ZIP_DEFLATED) as z:
    for p in paths:z.write(p,str(p.relative_to(R)))
with ZipFile(dest) as z:assert z.testzip() is None
print(json.dumps(dict(package=str(dest),bytes=dest.stat().st_size,panels=5,unique_cut_profiles=3,
                     frame_joint_bolts=8,pod_release_straps=2,total_solids=368,checks='All recorded CAD and export checks passed'),indent=2))
