from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'shaft-clamp-r8-2026-10-25/native-r8.fs').read_text(encoding='utf-8')
pos=s.index('function r6BuildBellClamp(')
s=s[:pos]+(r/'r9_layout.fs').read_text()+'\n'+s[pos:]
s=s.replace('    r8BuildAxleClamp(context,id+"axleClamp",prop);','    r9ForwardFan(context,id+"forwardLayout",prop);\n    r8BuildAxleClamp(context,id+"axleClamp",prop);')
s=s.replace('R8 fan - M3 axle clamp lower jaw, four motor drive keys','R9 forward fan - flat hub, M3 axle clamp, four drive keys')
s=s.replace('Expected 46 R8 assembly solids with the two-piece axle clamp.','Expected 46 R9 assembly solids with forward fan and axle clamp.')
assert 'r9ForwardFan(context,id+"forwardLayout",prop)' in s and 'Expected 46 R9' in s
(r/'native-r9.fs').write_text(s,encoding='utf-8')
print('R9 native source characters',len(s))
