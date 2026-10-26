# CAD ledger — plan: docs/superpowers/plans/2026-09-30-rov-chassis.md

Authorization: user approved editable dimensions and explicitly directed design in Chassis. Continue implementation in this session without another permission request.

Isolation: existing Chassis document has zero parts and zero Feature Studios; edits are confined to that document and new local CAD sources. Motor + Fan is the preserved reference.

Pre-flight: the source holder's axis +Z and motor-plate identity are used by every clamp transformation. Clamp bases join the frame; holder/cap bodies remain independent. Tests evaluate actual kernel solids rather than source text.

Task 1: geometry checks passed: 259 checks each for default 360 × 300 × 120 / 60 mm prop, resized 420 × 340 × 140 / 60 mm prop, and resized / 72 mm prop; hide-reference mode creates nine solids. Kernel reported no notices.

Ruling: Put uprights at edge centres — corner uprights obstructed diagonal thruster streams — cost is a change in the cage's post positions.

Ruling: Limit chassis propeller editing to 60–80 mm — the approved layout uses 60 mm and smaller props require a different mount spacing — sizes below 60 mm need a layout revision.

Ruling: Tray dimensions follow the mount positions when the frame is resized — it keeps all vertical supports connected — generic equipment tray dimensions grow or shrink with the chosen frame/propeller combination.

Task 2: complete. Feature Studio ROV Chassis persisted once (d851987a47dbfa3bc92ebb5f), exact source readback verified. Custom feature placed in Chassis — 8 thrusters Part Studio (71f6fbd269f35af936273442), with holder references enabled. Reload visibly retains Features (5), Parts (17), all eight holders/caps and one cage/tray body; no feature regeneration error displayed. Proof image: rov_chassis_onshape.jpg. Onshape tab marked deliverable.

Review closed: enlarged-propeller spacing guard now rejects 440 × 340 × 140 / 80 mm before creating geometry; regression first reproduced actual interfering solids. Tray width is at least 150 mm, retaining 3.35 mm beyond equipment-hole edges; regression first reproduced missing material in the 361 × 304 × 120 / 65 mm fixture.

Final kernel verification: no notices; 259 checks each for default 60 mm, enlarged-frame 60 mm, 72 mm, and accepted 440 × 360 × 140 / 80 mm. The tray-edge fixture passes all four hole/material checks and all body-pair interference checks. Hide-reference mode retains nine solids. Review's optional clearance-endpoint sweep deferred; default clearance is verified in every fixture.
