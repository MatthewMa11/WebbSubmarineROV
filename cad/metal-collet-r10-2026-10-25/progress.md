# SDD ledger — plan: docs/superpowers/plans/2026-10-25-metal-collet-r10.md

Approved: documented adapter and duct extension preserving frame/cap shapes.
Ruling: isolate with a native Onshape workspace branch, not a Git worktree —
the deliverable is a native CAD revision; prior R8/R9 workspace files preserved.
Ruling: use CPA-317-N own-product dimensional documentation; simplified metal
reference envelope only. Actual grip depth/taper is not claimed verified.
Pre-flight: Task 2 consumes Task 1 part identities and verified export.
Packaging study: current cap intersects the proposed M6 stud by 377.718 mm3.
Choose 23 mm cap translation so M3x35 maintains original 12.5 mm bolt tip datum.

Native R10 workspace: 19f580305ee8d4219aed16cb, same assembly/PS EIDs as R9.
RED: R9 fails body count, moved cap, separate extension checks as expected.
Native source regenerated after renaming reserved FeatureScript identifier box.
Export: 45 solids; hub/extension valid; nominal intersections zero; full-turn
envelope gaps frame 3.573, cap 1.630, extension 3.230 mm with 0.07 mm allowance.
Ruling: coincident Boolean difference is unsuitable for inherited imported
frame/rotor (identical mass/area/bounds but subtracting rotor returned itself).
Use face type/area/bounds fingerprints plus independent mass/bounds and a
negative control translating each part 0.1 mm. Preserve failed diagnostics in
this ledger: frame Cut residual .195 mm3; rotor Cut residual 7424.326 mm3.

Fresh review Important: actual collet bore depth unpublished; an 8 mm depth
would shift stack forward about 1.2 mm, reducing original 1.7 mm cap gap to .5.
Ruling: increase extension/cap movement to28 mm, use M3x40 retaining original
tip plane, and prove clearance continuously for stack offset0..3 mm. Nominal
backplateY24.3, acceptable installed datum24.3..27.3 subject to full actual
metal collet engagement. Explicitly measure bore/installed datum before print.
Fresh review Important: exact frame-copy subtraction had zero lateral print
relief; 0.1 mm offset caused~20 mm3 interference. Fix: clip copied frame above
Y19, subtract its center plus eight radial0.3mm translations, preserving all
bearing planes. New verification probes extension lateral offsets0.2mm in
eight directions and requires zero frame penetration.
First discrete-copy relief passed cardinal probes but left .050..052 mm3
overlap on diagonal0.2mm probes. Do not accept. Replaced discrete offsets
with native opOffsetFace(+0.30 mm) on the clipped front-copy solids, then
reclipped aboveY19 to preserve bearing planes. Re-export and rerun required.
Native opOffsetFace cannot offset inherited front fillets. Replace with denser
25-copy grid (+/-0.4mm, step0.2) and validate24 independent lateral directions
at0.2mm offsets, including directions not represented by the grid. Keep entire
Y19 bearing plane and frame/cap unchanged; no global tolerance relaxation.
25-copy cut failed nativeBoolean; final native operation uses nine copies on
square grid +/-0.4mm (step0.4), which regenerates successfully. Validation uses
24 lateral0.2mm directions, independent of the grid points, and crops only the
mathematically possible Y-overlap zone19..24.714mm for efficient Booleans.
Current final exports:45 solids; fan+extension+coupon each one closed manifold;
mesh/STEP volume error fan0.0423%, extension0.0254%, coupon0.0414%.
Square-grid relief left valid thin contact strips, .006..169mm3, nearR39 and
Y19.095..23 (diagnose_relief.py). Fix actual geometry: explicit rear-mouth
counterboreR40 throughY23.5, taper toR38.8 atY26.5, protectedR5 bolt columns,
0.2mm edge blends. This removes the specific inherited lip contact, keeps
minimum main ring wall3mm at rear and4.2mm forward, preserving bearing areas.
Task1: complete — final native feature healthy;45 STEP solids; all26 geometric
checks pass including24 lateral0.2mm directions and envelope offset0..3mm.
Task2 checks: assembly/PS signature agreement, insertion/tool access all6pass;
nativeNoInterferences, groups40+5,360degree motion; three closed print meshes.
Outer profile107278 samples max0.01697mm; wrong1mmtranslation negative fails.
Final reviewer findings resolved as inFINAL-REVIEW.txt; physical adapter
grip/datum fit remains explicit user acceptance before print/operation.
Saved native version:cc9d5f72788640984612fdc3
R10 workspace19f580305ee8d4219aed16cb; original and R8/R9 preserved.
Task2: complete — immutable native version saved; screenshots refreshed;
print kit built with20 explicitly selected entries. CRC and every archived
byte checked against verified sources. No superseded23mm extension included.
