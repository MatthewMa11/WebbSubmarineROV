# R12 ledger
Ruling: interpret blue + gray as outer blue duct + gray main housing, based on
current visible assembly. Asked optional identity clarification, then stated
this interpretation after allowing time for reply. Do not merge moving fan
with stationary structure. R11 saved75c1dcfd63b352df99b31e2f remains intact.
Native assembly and source Part Studio retain real motor/adapter geometry.
NativeR12 workspace ce5746ad029eef06ab8599f6 from R11 version.
RED observed: R11 has48 solids and no single full-length combined housing.
Baseline OCP STEP validation rejects legacy frame/cap but native duct is valid;
this predates R12. Must prove native topology and exported print mesh, rather
than asserting source legacy STEP validity.
User confirmed outer blue duct + gray housing. Native one-body union succeeds.
Native STL has577,950 functional triangles plus two tiny4-triangle export
fragments, each1.547e-8mm3 / max dimension0.062mm. Remove only those sub-nozzle
fragments, no resampling; require closed connected main print mesh. Legacy
STEP reader rejects original frame/cap before R12 as well. Preserve that
failure diagnostically, use native connected-body and print mesh gates.
Ruling: retention comparison excludes intentionally modified seamY17.9..28.1;
all other original surfaces must remain within0.02mm. Full-source maximum
0.0637mm occurs at old mating-pocket fillets Y19.19; outside joint max0.0102mm.
All other46 bodies preserve exact signatures; all housing/hardware overlaps0.
Geometry GREEN:47 solids, one merged housing, all other46 signatures unchanged,
3.23mm full-turn envelope gap, no overlap against any of46 other bodies.
Print GREEN:577,950 triangles, closed manifold, connected1;101.591sq x77mm.
Outside-joint surface maxima0.00379mm(frame)/0.01012mm(duct). Fan/cap/coupon
print files remain byte-identical to R11. Native groups43/4 and motion recorded.
Final fresh review complete: no critical/important/minor findings. Parent
resolved insertion-evidence boundary: continuous corridor contains all5 moving
bench-assembled bodies and clears merged housing +20 retained fasteners,
zero escape/overlap. Saved nativeR12 version46cfeee110ebcedd02908155 opened
and visibly confirmed47 instances. Legacy STEP interchange validity remains
unqualified; no STEP supplied in kit. Physical qualification remains required.
Final package gate PASS:21 entries, CRC verified, current source bytes/hash
identities verified. ZIP14,230,428 bytes SHA256
b791aacf2ed5d855f395b3083a863b88ef2d9c87f99bf8f07d55121b9ab06221.
Task complete: native saved R12,47-part assembly, one printable housing,
rotation/insertion clearances, unchanged fan/cap/actual hardware and print kit.
