from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'bolt-free-retention-2026-10-24/native-before.fs').read_text(encoding='utf-8')
start=s.index('function r6BuildBellClamp(');end=s.index('\nfunction applyR6SimpleDrive(',start)
old=s[start:end];prefix=old[:old.index('    var band=annularTool')]
new=prefix+'    opBoolean(context,id+"solidDriveKeys",{"tools":qUnion([prop,qUnion(fills)]),"operationType":BooleanOperationType.UNION});\n    r8BuildAxleClamp(context,id+"axleClamp",prop);\n}\n'
s=s[:start]+(r/'r8_axle.fs').read_text()+'\n'+new+s[end:]
s=s.replace('!=47) throw regenError("Expected 47 R6 assembly solids after replacing the insert and fasteners.");','!=46) throw regenError("Expected 46 R8 assembly solids with the two-piece axle clamp.");')
assert 'Expected 46 R8' in s and 'r7BuildRetention' not in s
(r/'native-r8.fs').write_text(s,encoding='utf-8')
print('R8 source characters',len(s))
