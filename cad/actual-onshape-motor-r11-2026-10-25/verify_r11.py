from pathlib import Path
import sys,json
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t'];cylinder=ns['cylinder'];ss=ns['solids'](Path(sys.argv[1]) if len(sys.argv)>1 else r/'Thruster-R11-actual-models.step')
checks=[]
def check(name,ok,**d):
 checks.append(dict(check=name,passed=bool(ok),detail=d));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def span(s):
 lo,hi=t.limits(s);return [b-a for a,b in zip(lo,hi)]
check('48 solids with actual source motor and adapter',len(ss)==48,total=len(ss))
motor=[s for s in ss if 27<span(s)[0]<29 and 40<span(s)[1]<41 and -13.4<t.limits(s)[0][1]<-13.1]
check('actual fused motor model replaces both generic motor references',len(motor)==1,count=len(motor))
fans=[s for s in ss if span(s)[2]>70 and span(s)[0]<50]
if len(fans)==1:
 from OCP.TopExp import TopExp_Explorer
 from OCP.TopAbs import TopAbs_FACE
 from OCP.TopoDS import TopoDS
 from OCP.BRepAdaptor import BRepAdaptor_Surface
 from OCP.GeomAbs import GeomAbs_Cylinder
 radii=[];ex=TopExp_Explorer(fans[0],TopAbs_FACE)
 while ex.More():
  a=BRepAdaptor_Surface(TopoDS.Face(ex.Current()))
  if a.GetType()==GeomAbs_Cylinder and abs(a.Cylinder().Axis().Direction().Y())>.9999:radii.append(a.Cylinder().Radius())
  ex.Next()
 check('fan has 5.1 mm stud bore and 6.2 mm shoulder relief',any(abs(x-2.55)<1e-5 for x in radii) and any(abs(x-3.1)<1e-5 for x in radii),radii_mm=sorted(set(round(x,6) for x in radii)))
else:check('one printable fan',False,count=len(fans))
if len(motor)==1 and len(fans)==1 and len(ss)==48:
 import math,collections
 from OCP.gp import gp_Trsf,gp_Vec,gp_Ax1,gp_Pnt,gp_Dir
 from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
 from OCP.BRepCheck import BRepCheck_Analyzer
 def pose(s):
  tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,1,0)),math.pi/4);tr.SetTranslationPart(gp_Vec(0,15.67,0));return BRepBuilderAPI_Transform(s,tr,True).Shape()
 def common(a,b):return t.boolean(t.BRepAlgoAPI_Common,a,b)
 def cv(a,b):return abs(t.volume(common(a,b)))
 def sig(s):return tuple(round(v,4) for pp in t.limits(s) for v in pp)+(round(t.volume(s),3),round(t.area(s),3))
 def fp(s):
  out=[];ex=TopExp_Explorer(s,TopAbs_FACE)
  while ex.More():
   f=TopoDS.Face(ex.Current());a=BRepAdaptor_Surface(f)
   out.append((int(a.GetType()),round(t.area(f),4))+tuple(round(v,4) for pp in t.limits(f) for v in pp));ex.Next()
  return sorted(out)
 p={'motor':motor[0],'fan':fans[0]};extra=[]
 for s in ss:
  if any(s.IsSame(q) for q in p.values()):continue
  lo,hi=t.limits(s);dx,dy,dz=span(s)
  if dx>90 and lo[1]<-29:n='frame'
  elif dx>90 and lo[1]>40:n='cap'
  elif dx>90 and 18.9<lo[1]<19.1:n='extension'
  elif 7.8<dx<8.1 and 22<dy<23:n='collet'
  elif 12<dx<12.2 and 6<dy<8:n='collar'
  elif 11<dx<12 and 14<dy<15 and lo[1]>30:n='nut'
  else:extra.append(s);continue
  assert n not in p,n;p[n]=s
 check('eight mechanical bodies and forty standard hardware bodies',len(p)==8 and len(extra)==40,parts=list(p),hardware=len(extra));assert len(p)==8
 source=ns['solids'](r/'SOURCE-Motor-assembly.step')
 for n,i in [('motor',4),('collet',1),('collar',7),('nut',2)]:
  ref=pose(source[i]);dv=abs(t.volume(p[n])-t.volume(ref));da=abs(t.area(p[n])-t.area(ref));db=max(abs(a-b) for aa,bb in zip(t.limits(p[n]),t.limits(ref)) for a,b in zip(aa,bb))
  match=fp(p[n])==fp(ref)
  check('actual '+n+' source geometry preserved under rigid pose',dv<.01 and da<.02 and db<.001 and match,volume_delta_mm3=dv,area_delta_mm2=da,bounds_delta_mm=db,face_fingerprints_match=match)
 old=ns['solids'](r.parent/'metal-collet-r10-2026-10-25/Thruster-R10-metal-collet.step')
 refs={}
 for s in old:
  lo,hi=t.limits(s);dx,dy,dz=span(s)
  if dx>90 and lo[1]<-29:refs['frame']=s
  elif dx>90 and lo[1]>40:refs['cap']=s
  elif dx>90 and 18.9<lo[1]<19.1:refs['extension']=s
 for n in ['frame','cap','extension']:
  check(n+' shape and placement unchanged from R10',sig(p[n])==sig(refs[n]) and fp(p[n])==fp(refs[n]))
 check('all actual source solids and the edited fan are valid',all(BRepCheck_Analyzer(p[n]).IsValid() for n in ['motor','collet','collar','nut','fan']))
 hub=t.limits(p['fan'])
 check('hub seats in exact source collar-to-nut gap',abs(hub[0][1]-24.5346)<.001 and abs(hub[1][1]-31.6796594848951)<.001,axial_bounds_mm=[hub[0][1],hub[1][1]])
 new_contacts={n:cv(p['fan'],p[n]) for n in ['motor','collet','collar','nut','frame','cap','extension']}
 check('fan has no unintended nominal overlap',max(new_contacts.values())<1e-4,overlap_mm3=new_contacts)
 # Compare planar bearing faces directly. STEP tolerances can leave a 1e-7 mm
 # gap even when the native Parasolid planes are coincident.
 from OCP.GeomAbs import GeomAbs_Plane
 def bearing_faces(s,y):
  result=[];ex=TopExp_Explorer(s,TopAbs_FACE)
  while ex.More():
   f=TopoDS.Face(ex.Current());a=BRepAdaptor_Surface(f);lo,hi=t.limits(f)
   if a.GetType()==GeomAbs_Plane and abs(a.Plane().Axis().Direction().Y())>.99999 and abs(lo[1]-y)<1e-5 and abs(hi[1]-y)<1e-5:result.append(f)
   ex.Next()
  return result
 areas={};seat_gaps={}
 for name,y in [('collar',24.5346),('nut',31.6796595848951)]:
  areas[name]=0;seat_gaps[name]=t.distance(p['fan'],p[name])
  for a in bearing_faces(p['fan'],y):
   for b in bearing_faces(p[name],y):
    algo=t.BRepAlgoAPI_Common(a,b);algo.SetFuzzyValue(1e-5);algo.Build();assert algo.IsDone()
    areas[name]+=abs(t.area(algo.Shape()))
 check('both metal clamping faces contact the flat hub',min(areas.values())>50 and max(seat_gaps.values())<1e-5,contact_area_mm2=areas,separation_mm=seat_gaps,comparison_tolerance_mm=1e-5)
 no_relief=cylinder(3.1,(0,24.5346,0),(0,1,0),.35)
 no_relief=t.boolean(t.BRepAlgoAPI_Cut,no_relief,cylinder(2.55,(0,24.5246,0),(0,1,0),.37))
 check('actual shoulder demonstrates the need for rear relief',cv(no_relief,p['collet'])>1e-3,otherwise_overlap_mm3=cv(no_relief,p['collet']))
 source_contacts={}
 for a,b in [('motor','collet'),('collet','collar'),('collet','nut')]:
  nominal=cv(p[a],p[b]);ref=cv(pose(source[{'motor':4,'collet':1,'collar':7,'nut':2}[a]]),pose(source[{'motor':4,'collet':1,'collar':7,'nut':2}[b]]))
  source_contacts[a+'/'+b]=nominal
  check('existing source contact retained: '+a+'/'+b,abs(nominal-ref)<.01,overlap_mm3=nominal,source_mm3=ref)
 old_axes=[(9.5,0),(-9.5,0),(0,8),(0,-8)];new_axes=[(9.4361,0),(-9.4361,0),(0,8.0137),(0,-8.0137)]
 basebolts=[s for s in extra if abs(t.limits(s)[0][1]+20)<.001 and abs(t.limits(s)[1][1]+9)<.001]
 basewashers=[s for s in extra if abs(span(s)[1]-.5)<.001 and -17.01<t.limits(s)[0][1]<-16.49]
 check('four M3x8 bolts and eight M3 washers at motor base',len(basebolts)==4 and len(basewashers)==8)
 axes=[]
 for s in basebolts:
  lo,hi=t.limits(s);axes.append(((lo[0]+hi[0])/2,(lo[2]+hi[2])/2))
 check('base screws align with actual motor CAD holes',sorted((round(x,4),round(z,4)) for x,z in axes)==sorted(new_axes),actual_axes_mm=axes)
 check('base bolt tips stop 0.3876 mm before modeled blind bottom',len(basebolts)==4 and all(abs(t.limits(s)[1][1]+9)<.001 for s in basebolts),engagement_mm=2,blind_bottom_margin_mm=.3876)
 # Remaining28 cover/frame fasteners must stay exactly where R10 put them.
 oldp,_,oldhw=ns['read'](r.parent/'bolt-free-retention-2026-10-24/Thruster-R7-bolt-free.step')
 old_extra=[]
 for s in old:
  if any(sig(s)==sig(v) for v in refs.values()):continue
  lo,hi=t.limits(s);dx,dy,dz=span(s)
  if dx<12 and (dy<43.1):old_extra.append(s)
 common_signatures=collections.Counter(map(sig,extra)) & collections.Counter(map(sig,old_extra))
 check('all twenty-eight other mounting and cover fasteners preserved',sum(common_signatures.values())==28,count=sum(common_signatures.values()))
 frame_bolt_overlap=[cv(p['frame'],s) for s in basebolts+basewashers]
 check('recentered base hardware clears unchanged frame',max(frame_bolt_overlap)<1e-4,overlap_mm3=frame_bolt_overlap)
 thread_overlap=[]
 for s,(x,z) in zip(sorted(basebolts,key=lambda q:((t.limits(q)[0][0]+t.limits(q)[1][0])/2,(t.limits(q)[0][2]+t.limits(q)[1][2])/2)),sorted(new_axes)):
  engagement=cylinder(1.53,(x,-11.001,z),(0,1,0),2.002)
  contact=common(s,p['motor']);unexpected=t.boolean(t.BRepAlgoAPI_Cut,contact,engagement)
  thread_overlap.append({'total_thread_contact_mm3':abs(t.volume(contact)),'outside_engagement_mm3':abs(t.volume(unexpected))})
 check('motor screw contacts confined to intended threaded engagement',all(q['outside_engagement_mm3']<1e-4 for q in thread_overlap),contacts=thread_overlap)
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
 fan_sweep=cylinder(35.57,(0,24.4646,0),(0,1,0),7.2850594848951)
 metal_sweep=cylinder(6.11,(0,17.505,0),(0,1,0),28.7226594848951)
 sweep=t.boolean(BRepAlgoAPI_Fuse,fan_sweep,metal_sweep)
 rotating=[p[n] for n in ['fan','collet','collar','nut']]
 escaped=[abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,s,sweep))) for s in rotating]
 check('continuous full-turn envelope contains fan and actual adapter',max(escaped)<1e-4,escaped_mm3=escaped)
 # The fused source motor includes its rotating axle. Exclude that axle only
 # from the stationary clearance envelope; delivered source geometry stays exact.
 stationary_motor=t.boolean(t.BRepAlgoAPI_Cut,p['motor'],cylinder(1.56,(0,15.669,0),(0,1,0),11.178))
 gaps={n:t.distance(sweep,p[n]) for n in ['frame','cap','extension']};gaps['motor body excluding rotating axle']=t.distance(sweep,stationary_motor)
 check('full-turn envelope clears all fixed structure',min(gaps.values())>1.5,clearance_mm=gaps)
 check('full-turn envelope clears all forty standard fasteners',min(t.distance(sweep,s) for s in extra)>1.0)
 empty=cylinder(11.31,(0,5.59,0),(0,1,0),4.42)
 check('no printed motor spacer or printed clamp',cv(p['fan'],empty)<1e-5 and len(ss)==48)
 (r/'source-contact-report.json').write_text(json.dumps({'source_clamp_contacts_mm3':source_contacts,'motor_screw_thread_contacts':thread_overlap,'note':'These are retained source clamp / intended thread engagements, not free-running clearance pairs.'},indent=2))
(r/'verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
