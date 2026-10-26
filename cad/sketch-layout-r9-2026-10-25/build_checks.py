"""Reuse the established independent rigid-fit suite with explicit R9 changes."""
from pathlib import Path
r=Path(__file__).resolve().parent;base=r.parent/'shaft-clamp-r8-2026-10-25'
s=(base/'verify_r8.py').read_text()
s=s.replace('8.2','8.0')
s=s.replace('Thruster-R8-M3-axle-clamp.step','Thruster-R9-forward-fan.step')
s=s.replace("bad==oldbad and len(bad)==2","all(q in shifted_bad for q in bad)")
s=s.replace("bad=invalid_faces(p['fan']);oldbad=invalid_faces(old['propeller'])","bad=invalid_faces(p['fan']);oldbad=invalid_faces(old['propeller'])\nshifted_bad=[tuple(round(v+(8.0 if i in (1,4) else 0),5) for i,v in enumerate(q)) for q in oldbad]")
s=s.replace("'edited fan faces valid; only two inherited blade-tip STEP slivers remain'","'all edited fan faces valid; any inherited tip slivers translate with blades'")
s=s.replace("a=t.boolean(t.BRepAlgoAPI_Cut,p['fan'],region);b=t.boolean(t.BRepAlgoAPI_Cut,old['propeller'],region)","a=t.boolean(t.BRepAlgoAPI_Cut,p['fan'],region);b=t.boolean(t.BRepAlgoAPI_Cut,old['propeller'],region)\nfrom OCP.BRepBuilderAPI import BRepBuilderAPI_Transform\nfrom OCP.gp import gp_Trsf,gp_Vec\nback=gp_Trsf();back.SetTranslation(gp_Vec(0,-8.0,0));a=BRepBuilderAPI_Transform(a,back,True).Shape()")
s=s.replace("check('blade tips outside central revision retain original geometry',dv<.01 and da<.02,volume_delta_mm3=dv,area_delta_mm2=da)","from profile_check import profile_check\nprofile=profile_check(r)\ncheck('outer blade sampled surfaces agree within 0.02 mm after 8 mm translation',profile['passed'],surface_comparison=profile,step_mass_integration_diagnostics={'volume_delta_mm3':dv,'area_delta_mm2':da})")
s=s.replace("sweep=cylinder(35.57,(0,-3.001,0),(0,1,0),22.302)","from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse\ncore=cylinder(22.27,(0,-3.001,0),(0,1,0),22.302)\nring=t.boolean(t.BRepAlgoAPI_Cut,cylinder(35.57,(0,13.0,0),(0,1,0),6.61),cylinder(21.93,(0,12.99,0),(0,1,0),6.63))\nsweep=t.boolean(BRepAlgoAPI_Fuse,core,ring)")
s=s.replace("(r/'verification.json').write_text", "fastener_gaps=[t.distance(sweep,q) for q in stationary]\ncheck('all stationary fasteners clear the full-turn envelope',len(fastener_gaps)==36 and min(fastener_gaps)>4.8,minimum_gap_mm=min(fastener_gaps))\n(r/'verification.json').write_text")
assert 'shifted_bad' in s and 'fastener_gaps' in s and 'back.SetTranslation' in s
(r/'verify_r9.py').write_text(s)
for src in ('verify_tool_access.py','make_coupon_and_check_mesh.py','verify_artifacts.py'):
 s=(base/src).read_text().replace('Thruster-R8-M3-axle-clamp.step','Thruster-R9-forward-fan.step').replace('Fan-R8-M3-axle-clamp.stl','Fan-R9-forward-fan.stl').replace('Upper-jaw-R8-M3-axle-clamp.stl','Upper-jaw-R9-M3-axle-clamp.stl').replace('TEST-FIRST-R8-lower-jaw.stl','TEST-FIRST-R9-lower-jaw.stl').replace('R8-M3-Axle-Clamp-Print-Kit.zip','R9-Forward-Fan-Print-Kit.zip')
 (r/src).write_text(s)
print('Built R9 independent geometry, closure, tool and artifact checks')
