# R13 ledger
Interpretation: cone=gold removable front cap; flat inner faceY48 faces the
actual metal bullet nut. User's current zoom and model geometry corroborate it.
Ruling: use short M3x12 screws with front-loaded captured nuts and locating pilots
as the implementation of requested attachment optimization. Prior preference for
real bolts/nuts remains; no printed threads or internal motor spacer.
Native workspace9692a2577c76c0b80fbde875 branched from savedR12.
RED observed on R12: no bowl, clearance gauge interferes, no4short bolts or
front nut seats. Plan refined for printing: nut pocket40.9..44.0, washer
slot43.3..44.3 (1mm high) and local3.6mm bolt clearances.
Diagnostic: native monitor reported fSphere center precondition Query, not Vector.
Official standard-library docs confirm opSphere takes Vector. Replace feature
constructor with opSphere only; no design change.
Print volume diagnosis: cone STEP mass integrals disagree0.337% with native
STL, inherited legacy source representation. Native Onshape Mass Properties
measured housing128520.263mm3 and combined158800.661mm3, cone30280.398mm3.
STL cone30265.9063 differs0.0479%, within0.1% fine mesh gate. Compare main
prints to native kernel volume, retain STEP mass as diagnostic; no interchange
STEP certification/packaging. Joint coupons use local valid clipped geometry.
Geometry21/21 GREEN. Full-turn cone gap6.08987mm vsold1.77234mm; housing3.23mm.
Continuous4nut/washer loading paths pass; continuous motor/fan insertion passes.
Six print files verified; newhousing607518triangles andcone111536 are closed,
connected1. Main volumes match native Onshape<0.1%; coupons clipped from actual
local joint geometry. Outer cone retained surfaces matchwithin7.5e-6mm.
Task1 complete: native assembly export poses match47checked solids; fixed43,
rotating4, motion0..360, scoped cone/housing/fan native interference clear.
Assembly5/5 GREEN. Saved versionb026d3e43969875b68fe1d72 confirmed view-only.
Fresh final review found no Critical/Important findings. Deferred minor:
stronger axial endpoint/per-seat regression assertions; current dimensions
support0.2mm relief and each seat. Native interference scope clarified as
cone/housing/fan; independent geometry covers modified parts versus hardware.
Physical qualification remains bench work, as detailed in FINAL-REVIEW.txt.
Task2 complete: six print files and27-entry ZIP gate passed, CRC and content
hashes match. Package R13-Concave-Cone-Print-Kit.zip,15265239bytes. Retain this
artifact ledger with design evidence rather than deleting the user deliverable.
