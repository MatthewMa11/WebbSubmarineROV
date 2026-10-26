# Reinforced chassis revision — 2026-09-30

Authorization: user requested making the existing Onshape chassis far more sturdy and aerodynamic. Preserve approved360 × 300 × 120 mm default envelope, eight holder axes,60 mm default propeller and M3 mounting interfaces. Geometry work is authorized; no additional publication or permission changes.

Intent: visibly reinforced load paths and smoother water-facing geometry. Existing open-cage architecture is retained. No FEA/CFD or material/load specification is available, so strength and drag improvements are design intent rather than measured claims.

Changes: perimeter rails16 × 12 mm,24 mm plan corner radii,4 mm rail-edge radius;20 × 20 mm uprights with6 mm rounding;16 triangular40 × 32 × 12 mm gussets;28 mm vertical support width,24 mm horizontal support width;8 mm tray,22 mm spine;6 mm clamp wall,16 mm axial bands,1.5 mm clamp/support edge rounding. Vertical bands are centred at worldZ=-12 mm (local18/up,42/down), preserving all motor axes and avoiding horizontal-cap/vertical-base contact. M3 hole centres stayaligned within each clamp.

Parameter validity: early vx>=r+18 guard clears opposing vertical ears; final actual-body collision validation rejects overlapping edits.370 × 304 × 120 /65 mm is rejected;370 × 316 × 120 /65 mm passes. Default and enlarged60/72/80 mm cases pass.

Verification: reinforcedChassisSuite evaluated successfully with no notices.259 checks each for default60, enlarged60,72,80 mm layouts; hide-reference mode9parts; additional65 mm hole/material and pair-interference checks; actual reinforcement/cylindrical fillet checks; .2/.8 mm clamp-clearance endpoints. Negative compact-layout probe returns the intended error.

Review complete: no Critical, Important or Minor issues requiring action. Fastener access, rear cable notch clearance, support footprints and connected load paths checked. Quantitative strength/fatigue/impact and drag claims are excluded until material/load/FEA/CFD evidence exists; pressure containment, buoyancy, sealing and fabrication splitting remain outside this revision.

Source persisted once for this revision in existing ROV Chassis Feature Studio (d851987a47dbfa3bc92ebb5f), with exact readback match. Browser reload visibly confirms17 parts,5 features, the new reinforced-frame name, thicker rounded rails, uprights/gussets and unchanged eight-holder layout; no regeneration error displayed. Proof: rov_chassis_reinforced_onshape.jpg. Onshape tab marked deliverable. Source: rov_chassis_reinforced.fs. Verification module: rov_chassis_reinforced_tests.fs. Kernel evidence: rov_chassis_reinforced_kernel_result.txt.
