from pathlib import Path
import sys,json
r=Path(__file__).resolve().parent
v=r.parent/'bolt-free-retention-2026-10-24/verify_r7.py'
ns={'__file__':str(v)};exec(v.read_text().split('p,rings,h=read(')[0],ns)
t=ns['t']; solids=ns['solids']; cylinder=ns['cylinder']
source=Path(sys.argv[1]) if len(sys.argv)>1 else r/'Thruster-R10-metal-collet.step'
ss=solids(source)
checks=[]
def check(n,ok,**detail):
 checks.append(dict(check=n,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+n,flush=True)
check('45 assembly solids, printed clamp removed',len(ss)==45,total=len(ss))
caps=[s for s in ss if t.limits(s)[1][0]-t.limits(s)[0][0]>80 and t.limits(s)[0][1]>30]
check('unchanged cap translated forward by 28 mm',len(caps)==1,cap_candidates=len(caps))
extensions=[s for s in ss if t.limits(s)[1][0]-t.limits(s)[0][0]>90 and 18.9<t.limits(s)[0][1]<19.1 and 46.9<t.limits(s)[1][1]<47.1]
check('separate 28 mm duct extension',len(extensions)==1,extension_candidates=len(extensions))
if len(caps)==1 and len(extensions)==1:
 from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
 from OCP.gp import gp_Trsf,gp_Vec
 from OCP.BRepCheck import BRepCheck_Analyzer
 from OCP.TopExp import TopExp_Explorer
 from OCP.TopAbs import TopAbs_FACE
 from OCP.TopoDS import TopoDS
 from OCP.BRepAdaptor import BRepAdaptor_Surface
 old,_,_=ns['read'](r.parent/'bolt-free-retention-2026-10-24/Thruster-R7-bolt-free.step')
 def moved(q,y):
  x=gp_Trsf();x.SetTranslation(gp_Vec(0,y,0));return BRepBuilderAPI_Transform(q,x,True).Shape()
 def span(q):
  lo,hi=t.limits(q);return [b-a for a,b in zip(lo,hi)]
 def common(a,b):return abs(t.volume(t.boolean(t.BRepAlgoAPI_Common,a,b)))
 def sig(q):return tuple(round(v,4) for pp in t.limits(q) for v in pp)+(round(t.volume(q),3),round(t.area(q),3))
 def face_fingerprints(q):
  out=[];ex=TopExp_Explorer(q,TopAbs_FACE)
  while ex.More():
   f=TopoDS.Face(ex.Current());sf=BRepAdaptor_Surface(f)
   out.append((int(sf.GetType()),round(t.area(f),5))+tuple(round(v,5) for pp in t.limits(f) for v in pp))
   ex.Next()
  return sorted(out)
 p={'cap':caps[0],'extension':extensions[0]};extra=[]
 for s in ss:
  if s.IsSame(caps[0]) or s.IsSame(extensions[0]):continue
  lo,hi=t.limits(s);dx,dy,dz=span(s)
  if lo[1]<-29 and dx>90:n='frame'
  elif dz>70 and dx<50:n='fan'
  elif 27<dx<29 and dy>25:n='rotor'
  elif 27<dx<29 and dy<6:n='stator'
  elif abs(dx-15.5)<.01 and dy>24.9:n='adapter'
  elif abs(dx-15.5)<.01 and 1.49<dy<1.51:n='washer'
  elif 4.99<dy<5.01 and 9<dx<12 and lo[1]>32:n='nut'
  else:extra.append(s);continue
  assert n not in p,n;p[n]=s
 check('nine modeled bodies and thirty-six stationary fasteners',len(p)==9 and len(extra)==36,parts=list(p),hardware=len(extra))
 assert len(p)==9
 for n,ref in [('frame',old['nozzle']),('rotor',old['rotor']),('stator',old['stator']),('cap',moved(old['cover'],28))]:
  dv=abs(t.volume(p[n])-t.volume(ref));da=abs(t.area(p[n])-t.area(ref));db=max(abs(a-b) for aa,bb in zip(t.limits(p[n]),t.limits(ref)) for a,b in zip(aa,bb))
  # Coincident Booleans on inherited imported faces are not robust (the rotor
  # can return itself after subtracting its identical STEP copy). Use a face-
  # by-face type/area/bounds fingerprint and independent mass/bounds instead.
  fp=face_fingerprints(p[n]);rfp=face_fingerprints(ref)
  check(n+' preserves all face fingerprints at required placement',dv<.01 and da<.01 and db<.001 and fp==rfp,volume_delta_mm3=dv,area_delta_mm2=da,bounds_delta_mm=db,face_count=len(fp),face_fingerprints_match=fp==rfp)
  check(n+' preservation check detects a 0.1 mm placement error',face_fingerprints(moved(p[n],.1))!=rfp)
 check('fan and extension B-rep valid',all(BRepCheck_Analyzer(p[n]).IsValid() for n in ('fan','extension')))
 from OCP.TopExp import TopExp_Explorer
 from OCP.TopAbs import TopAbs_FACE
 from OCP.TopoDS import TopoDS
 from OCP.BRepAdaptor import BRepAdaptor_Surface
 from OCP.GeomAbs import GeomAbs_Cylinder
 bore=[];ex=TopExp_Explorer(p['fan'],TopAbs_FACE)
 while ex.More():
  f=TopoDS.Face(ex.Current());a=BRepAdaptor_Surface(f)
  if a.GetType()==GeomAbs_Cylinder and abs(a.Cylinder().Radius()-3.1)<1e-5 and abs(a.Cylinder().Axis().Direction().Y())>.999:bore.append(t.limits(f))
  ex.Next()
 check('6.2 mm axial prop bore and 6.5 mm flat hub',len(bore)==1 and abs(bore[0][0][1]-24.55)<.001 and abs(bore[0][1][1]-30.55)<.001,bore_surface_bounds=bore)
 check('fan clears M6 stud with 0.1 mm radial nominal allowance',common(p['fan'],cylinder(3,(0,24.3,0),(0,1,0),6.5))<1e-5)
 check('hub thickness below published 10.5 mm maximum',6.5<10.5)
 empty=cylinder(11.31,(0,5.59,0),(0,1,0),4.42)
 check('no printed spacer in motor interior',sum(common(p[n],empty) for n in ('fan','extension'))<1e-5)
 oldkeyregion=cylinder(13.95,(0,11.49,0),(0,1,0),4.8)
 check('no old rotor vent drive keys or printed shaft clamp',common(p['fan'],oldkeyregion)<1e-5 and len(ss)==45)
 rotating=[('fan',p['fan']),('adapter',p['adapter']),('washer',p['washer']),('nut',p['nut'])]
 static=[('frame',p['frame']),('cap',p['cap']),('stator',p['stator']),('extension',p['extension'])]+[(f'fastener {i}',s) for i,s in enumerate(extra)]
 clashes=[]
 for i,(an,a) in enumerate(rotating):
  for bn,b in rotating[i+1:]+static+[('rotor',p['rotor'])]:
   vol=common(a,b)
   if vol>1e-4:clashes.append([an,bn,vol])
 for an,a in static[:4]:
  for bn,b in static[:4]:
   if an<bn:
    vol=common(a,b)
    if vol>1e-4:clashes.append([an,bn,vol])
 check('all new parts have zero nominal assembly penetration',not clashes,clashes_mm3=clashes)
 # Conservative continuous envelopes include .07 mm radial/axial allowance
 # and the entire installed adapter/fan forward offset range 0..3 mm.
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
 sweep=t.boolean(BRepAlgoAPI_Fuse,cylinder(35.57,(0,24.23,0),(0,1,0),9.88),cylinder(7.82,(0,16.23,0),(0,1,0),28.14))
 escaped={n:abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,s,sweep))) for n,s in rotating}
 escaped.update({n+' at +3mm':abs(t.volume(t.boolean(t.BRepAlgoAPI_Cut,moved(s,3),sweep))) for n,s in rotating})
 check('continuous full-turn envelope contains all new rotating geometry',max(escaped.values())<1e-4,escaped_mm3=escaped)
 gaps={n:t.distance(sweep,s) for n,s in static[:4]}
 check('full-turn envelope clears fixed structure',min(gaps.values())>1.0,clearance_mm=gaps)
 hardware_gaps=[t.distance(sweep,s) for s in extra]
 check('full-turn envelope clears all stationary fasteners',min(hardware_gaps)>1.0,minimum_mm=min(hardware_gaps))
 bolts=[s for s in extra if 42.99<span(s)[1]<43.01 and t.limits(s)[0][1]>12.49]
 check('four M3x40 cover bolts retain original tip plane',len(bolts)==4 and all(abs(t.limits(s)[0][1]-12.5)<.001 for s in bolts),count=len(bolts),bounds=[t.limits(s) for s in bolts])
 bore_probes=[]
 for x,z in [(0,44.5),(-44.5,0),(0,-44.5),(44.5,0)]:
  probe=cylinder(1.69,(x,18.99,z),(0,1,0),28.02)
  bore_probes.append(common(p['extension'],probe))
 check('all extension M3 through-bores are clear',max(bore_probes)<1e-5,overlap_mm3=bore_probes)
 relief=[]
 overlap_zone=cylinder(65,(0,18.99,0),(0,1,0),6.51)
 front_frame=t.boolean(t.BRepAlgoAPI_Common,p['frame'],overlap_zone)
 front_extension=t.boolean(t.BRepAlgoAPI_Common,p['extension'],overlap_zone)
 assert t.limits(p['frame'])[1][1]<25.5 and t.limits(p['extension'])[0][1]>18.99
 import math
 for x,z in [(.2*math.cos(math.radians(a)),.2*math.sin(math.radians(a))) for a in range(0,360,15)]:
  tr=gp_Trsf();tr.SetTranslation(gp_Vec(x,0,z))
  relieved=BRepBuilderAPI_Transform(front_extension,tr,True).Shape()
  relief.append(common(relieved,front_frame))
 check('new extension has print relief for 0.2 mm lateral variation',max(relief)<1e-4,overlap_mm3=relief)
 nut_probes=[cylinder(1.5,(x,13.1,z),(0,1,0),2.4) for x,z in [(0,44.5),(-44.5,0),(0,-44.5),(44.5,0)]]
 check('cover bolt shafts span full 2.4 mm captive-nut thread',all(sum(common(s,q) for s in bolts)>16.9 for q in nut_probes))
(r/'verification.json').write_text(json.dumps(checks,indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
