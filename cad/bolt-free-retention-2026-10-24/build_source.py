from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'native-before.fs').read_text(encoding='utf-8')
start=s.index('function r6BuildBellClamp(');end=s.index('\nfunction applyR6SimpleDrive(',start)
old=s[start:end];prefix=old[:old.index('    var band=annularTool')]
new=prefix+'    opBoolean(context,id+"solidDriveKeys",{"tools":qUnion([prop,qUnion(fills)]),"operationType":BooleanOperationType.UNION});\n    r7BuildRetention(context,id+"boltFree",prop);\n}\n'
s=s[:start]+(r/'r7_collar.fs').read_text()+'\n'+new+s[end:]
s=s.replace('!=47) throw regenError("Expected 47 R6 assembly solids after replacing the insert and fasteners.");','!=43) throw regenError("Expected 43 R7 assembly solids after replacing the insert and fasteners.");')
assert 'Expected 43 R7' in s
(r/'native-after.fs').write_text(s,encoding='utf-8')
print('Source characters',len(s))
