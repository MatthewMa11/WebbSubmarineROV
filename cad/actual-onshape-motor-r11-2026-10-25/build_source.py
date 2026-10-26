from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'metal-collet-r10-2026-10-25/native-r10.fs').read_text(encoding='utf-8')
pos=s.index('annotation {"Feature Type Name":"Four side mount finishing"}')
s=s[:pos]+(r/'r11_actual.fs').read_text(encoding='utf-8')+'\n'+s[pos:]
s=s.replace('!=45) throw regenError("Expected 45 R10 solids: metal collet reference stack and duct extension.")','!=49) throw regenError("R11 expects 49 solids before replacing references; derive the four actual source solids before this feature.")')
s=s.replace('        applyFlatRearMotorBoss(context,id+"flatRearBoss",definition.nozzle);','        applyFlatRearMotorBoss(context,id+"flatRearBoss",definition.nozzle);\n        applyR11ActualMotor(context,id+"actualMotor",definition.nozzle);')
assert '!=49)' in s and 'applyR11ActualMotor(context,id+"actualMotor",definition.nozzle)' in s
(r/'native-r11.fs').write_text(s,encoding='utf-8')
print('R11 source characters',len(s))
