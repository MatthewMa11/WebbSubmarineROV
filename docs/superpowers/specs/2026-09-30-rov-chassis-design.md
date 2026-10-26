# Eight-thruster ROV chassis

The user approved an editable 360 × 300 × 120 mm chassis and directed implementation in the existing Onshape **Chassis** document, in Submarine ROV. Use the existing 60 mm A2212 holder geometry and M3 screws. The requested layout has four diagonal horizontal axes and four vertical axes; the proposed two-up/two-down vertical orientation was followed by the instruction to design it in Chassis.

## Geometry and interfaces

- Document: `d2d1146b52127ad44971fea6`, workspace `129565adc2b6b396a0e4ce06`, Part Studio `71f6fbd269f35af936273442`. It is empty. Save a new `ROV Chassis` Feature Studio and insert its custom feature into Part Studio 1.
- Origin at chassis centre. X is fore/aft, Y port/starboard, Z vertical. Bounds are ±180, ±150, ±60 mm.
- Open perimeter cage, 8 mm upper/lower rails, four edge-centre uprights, central 160 × 90 mm vented equipment tray. Tray dimensions follow the mount positions when the cage is resized. Leave vertical flow paths open through both cage planes. Equipment mounts are generic M3 holes and strap slots; no unspecified electronics enclosure is invented.
- Four 70 mm OD / 64 mm ID / 60 mm long holders, centred at (±133, ±55, 0) mm, with outward diagonal axes (±1, ±1, 0)/sqrt(2). The non-radial axis placement produces a yaw moment arm of 55.15 mm about the geometric centre.
- Four vertical holders centred at (±60, ±105, 0) mm. Diagonally opposed holders face +Z; the other diagonal faces −Z.
- Holders retain 32 mm motor plates, four 3.3 mm holes on the nominal 16/19 mm cross pattern, 9.5 mm boss clearance and rear cable notch. They are reference instances of the existing printable holder, not imported motor solids or propeller blades.
- Each holder sits in a 12 mm wide split collar at local Z=18..30 mm, away from the rear cable notch. Nominal collar bore 70.4 mm, radial wall 4 mm, split gap 1 mm. Two 3.3 mm cross-bolt holes per clamp. Lower clamp halves join the chassis; eight upper caps remain separate solids. Cap screws are accessible from above for horizontal holders and outside the sides for vertical holders.
- Main frame, eight holders and eight caps are separately named: 17 solids total. Frame is dark blue, holders ivory, caps contrasting blue. No interfering solids; the 0.2 mm radial collar clearance is intentional.
- Editable overall length, width, height, propeller diameter (60–80 mm) and clamp fit. Scale placement offsets with holder radius. Reject combinations that cannot maintain holder separation, fit inside bounds, or keep vertical bores clear of the tray. Larger propellers can require a larger frame.

## Verification and scope

Run Onshape kernel tests for connected frame, 17 solids, exact bounds, eight shrouds and axes, M3 hole geometry, open vertical flow, clamp clearance and pairwise solid interference. Rebuild at 420 × 340 × 140 mm; verify eight holders and clearances persist. Test invalid size combinations before persisting code once. Reload the actual document after feature insertion and save a screenshot.

This is chassis CAD. It does not establish structural load capacity, buoyancy, waterproofing, hydrodynamic thrust or motor/ESC reversibility. Fabrication splitting and a rounded cosmetic shell can be added after the equipment and printer constraints are known.
