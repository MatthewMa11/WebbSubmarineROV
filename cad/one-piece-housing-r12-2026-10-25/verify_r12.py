from pathlib import Path
import sys,json,collections
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py';ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];cylinder=ns['cylinder'];solids=ns['solids']
ss=solids(Path(sys.argv[1]) if len(sys.argv)>1 else r/'Thruster-R12-one-piece.step')
checks=[]
def check(name,ok,**detail):
 checks.append(dict(check=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
def sig(s):return tuple(round(x,4) for pp in t.limits(s) for x in pp)+(round(t.volume(s),4),round(t.area(s),4))
check('47 solids after merging two housing parts into one',len(ss)==47,count=len(ss))
houses=[s for s in ss if span(s)[0]>100 and t.limits(s)[0][1]<-29 and t.limits(s)[1][1]>46.9]
check('one continuous housing spans original frame and extension',len(houses)==1,count=len(houses))
if len(ss)==47 and len(houses)==1:
 from OCP.BRepCheck import BRepCheck_Analyzer
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
 house=houses[0];other=[s for s in ss if not s.IsSame(house)]
 old=solids(r.parent/'actual-onshape-motor-r11-2026-10-25/Thruster-R11-actual-models.step')
 oldshell=[];oldother=[]
 for s in old:
  lo,hi=t.limits(s)
  (oldshell if span(s)[0]>90 and lo[1]<40 else oldother).append(s)
 check('all other46 solids retain geometry and placement',len(other)==len(oldother)==46 and collections.Counter(map(sig,other))==collections.Counter(map(sig,oldother)))
 # The pre-existing imported frame/cap STEP representations fail this reader's
 # topology check as well. Record that limitation without claiming it is green;
 # native connected-body and closed print-mesh evidence are the delivery gates.
 status=dict(new_housing_step_reader_valid=BRepCheck_Analyzer(house).IsValid(),legacy_shell_step_reader_valid=[BRepCheck_Analyzer(s).IsValid() for s in oldshell])
 (r/'legacy-step-reader-status.json').write_text(json.dumps(status,indent=2))
 print('INFO legacy STEP reader topology: '+str(status),flush=True)
 mesh_report=json.loads((r/'print-verification.json').read_text())
 check('one closed connected printable housing',mesh_report['housing']['closed_manifold'] and mesh_report['housing']['components']==1)
 lo,hi=t.limits(house);expectedlo=[min(t.limits(s)[0][i] for s in oldshell) for i in range(3)];expectedhi=[max(t.limits(s)[1][i] for s in oldshell) for i in range(3)]
 check('installed outside dimensions unchanged',max(abs(x-y) for aa,bb in zip([lo,hi],[expectedlo,expectedhi]) for x,y in zip(aa,bb))<.001,bounds_mm=[lo,hi])
 # Finite-volume seam web must connect the housing, rather than a contact group.
 check('finite seam reinforcement was added',t.volume(house)>sum(t.volume(s) for s in oldshell)+100,added_volume_mm3=t.volume(house)-sum(t.volume(s) for s in oldshell))
 fan_sweep=cylinder(35.57,(0,24.4646,0),(0,1,0),7.2850595848951)
 metal_sweep=cylinder(6.11,(0,17.505,0),(0,1,0),28.7226595848951)
 sweep=t.boolean(BRepAlgoAPI_Fuse,fan_sweep,metal_sweep)
 overlap=abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,house,sweep)));gap=t.distance(house,sweep)
 check('complete360 degree rotating envelope clears merged housing',overlap<1e-5 and gap>1.5,overlap_mm3=overlap,clearance_mm=gap)
 # Mating faces in Y18..28 are intentionally replaced by the reinforced seam.
 # The independent dense native-STL comparison checks retained surfaces away
 # from that joint; it avoids unreliable CSG of legacy STEP lofts.
 retained=mesh_report['retained_source_surfaces']
 check('old housing surfaces retained outside the modified mating joint',all(c['passed'] for c in retained),samples=retained)
 # Check every other body, including all hardware and real source motor pieces.
 contacts=[]
 for i,s in enumerate(other):
  a,b=t.limits(s)
  if any(b[k]<lo[k]-1e-5 or a[k]>hi[k]+1e-5 for k in range(3)):continue
  vol=abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,house,s)))
  if vol>1e-4:contacts.append(dict(index=i,overlap_mm3=vol,bounds=[a,b]))
 check('no housing interference with fan cap motor or40 fasteners',not contacts,contacts=contacts)
(r/'verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
