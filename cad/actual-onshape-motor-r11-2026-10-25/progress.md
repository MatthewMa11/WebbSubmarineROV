# SDD ledger — plan: docs/superpowers/plans/2026-10-25-actual-onshape-motor-r11.md

User specifically selected actual Onshape Motor models; proceed without another
mechanism/design approval. This refines the existing authorized R10 design.
Source DID0ff4892958a7b27bdfa13caa WID1f7c20273f2399a89a8462fd
AssemblyEID10199497d26cbfa5205bde9c.
ColletPartStudio41395be9c93b16fb0a259429
CollarPartStudio49b0f0b0739f8b8437009f02
NutPartStudio692582a588d627f766b2030c
MountPartStudio03ed89273c33f819beee0eb0 (not installed; frame replaces it).
Original linked motor source: DIDe9378d61974ba56cdbc5a682
V5c01672258b8dd37b174a197 AssemblyEIDb028319ba6be81980f63dc97.

Ruling: native Onshape API unavailable/no connected document sessions; use
existing IAB2 via CUA. Motor source tab3, original linked motor tab4, target
R10 tab2 (shaftDocTab). Do not mutate source geometry.
Ruling: source motor is one fused solid plus3 unrouted straight lead solids.
Keep motor shape intact as fixed CAD reference; fan+3 actual adapter parts
rotate together. Omit unrouted flexible lead solids from installed model.
Ruling: use exact exported source B-reps, not reconstructed geometry. A local
source snapshot imported into R11 preserves actual threads; record provenance.
Ruling: thicken fan to source collar/nut gap7.1450594848951mm so all metal
relative positions and thread phase remain unchanged. No speculative nut move.
Source fit study: motor/frame zero overlap; collet/frame zero; nut/cap gap2.15mm;
source clamp overlaps9.29286 and2.47698mm3, preserved and explicitly reported.
Pre-flight: Task2 consumes Task1 native parts/axis connectors and verified STEP.
Source saved version:5118b626e64f625b172818f8 (no geometry modifications).
R11 workspace:91c3cde4d7a276d485262d0d; target EIDs inherited fromR10.
RED: R10 fails44-solid/actualmotor/new5.1mm interface checks as expected.
Exact four-solid source snapshot built atY+200 with no reconstructed surfaces.
Actual base blind holes end atY=-8.6124 after pose. OldM3x8 tipY=-8.5 would
bottom0.1124mm. Add four0.5mm M3 washers under heads, shift bolts -0.5mmY:
tipsY=-9, 2mm nominal engagement, .3876mm blind-bottom margin. Recenter all
eight existing bolt/washer bodies on measured axes; frame holes stay unchanged.
Final body count48: fixed44, rotating4 (revises earlier44/fixed40 count).

Native source fidelity correction: superseded STEP staging with four native Derived
references in source PS a1aec6c523ece1f6e49fbec2. Motor original PS
44bd5137a633a0393f072e66 / V5c01672258b8dd37b174a197; three adapter
PSs from Motor source V5118b626e64f625b172818f8. Native staging Transform
Y+200 only. Finisher restores source assembly poses: collet Y1.905; collar
flip X180 then Y8.8646; nut Y16.0096595848951 and Y rotation
-96.73356114112303 degrees; whole group Y+15.67 / rotationY45. No
source shape or appearance overrides. Hub front corrected1e-7mm to source
plane (31.6796595848951).
Ruling: outer blade surface preservation uses the existing dense bidirectional
STL comparison (vertices, edges and triangle centers, radius>27.05) rather than
CSG subtraction of coincident STEP lofts. Native BReps and cut bodies are valid,
but OCP returns ~747.69mm3 differences both ways even with1e-5 fuzzy matching.
Independent53,202 samples each way match within1.906e-6mm. Keep diagnostic
CSG failure and require a wrong-placement negative control. This is a verifier
classification issue; delivered blade geometry is not changed to satisfy it.

Task1 complete: native source geometry preservation, measured hub interface,
unchanged structure, contacts and full-turn enclosure: verify_r11.py29/29.
Task2 complete: native48-part constrained assembly placements, groups44/4,
zero printed-structure interference, native360 animation, outerblade samples
and negative control: assembly_checks.py7/7. Print meshes pass.
Final review: fresh r11_final_review complete, no defects. Physical performance
remains hardware-qualified, saved native version independently opened by parent,
ZIP gate remains required before final delivery.
Final package gate PASS: 24 entries, CRC valid, source bytes and all five
print-file hashes verified. ZIP15,300,223 bytes SHA256
d566b41307f678ef2ef1be573be56248b3e352887ef244dad05e1e9641558bd0.
All requested CAD/print delivery complete; physical fit/retention remains a
hardware check as stated in the kit.
