from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'sketch-layout-r9-2026-10-25/native-r9.fs').read_text(encoding='utf-8')
pos=s.index('function r6BuildBellClamp(')
s=s[:pos]+(r/'r10_collet.fs').read_text()+'\n'+s[pos:]
s=s.replace('    r9ForwardFan(context,id+"forwardLayout",prop);\n    r8BuildAxleClamp(context,id+"axleClamp",prop);','    r10ColletFan(context,id+"metalCollet",prop);')
s=s.replace('!=46) throw regenError("Expected 46 R9 assembly solids with forward fan and axle clamp.")','!=45) throw regenError("Expected 45 R10 solids: metal collet reference stack and duct extension.")')
# Extension must precede the total-body guard.
s=s.replace('    r6BuildBellClamp(context,id+"bellClamp",qUnion(props));','    r6BuildBellClamp(context,id+"bellClamp",qUnion(props));\n    var nozzles=[];\n    for(var b in evaluateQuery(context,qAllModifiableSolidBodies()))\n    {\n        var r10Bounds=evBox3d(context,{"topology":b,"tight":true});\n        if(r10Bounds.minCorner[1]<-29*millimeter && r10Bounds.maxCorner[0]-r10Bounds.minCorner[0]>90*millimeter) nozzles=append(nozzles,b);\n    }\n    if(size(nozzles)!=1) throw regenError("R10 expects one original frame.");\n    r10DuctExtension(context,id+"extension",qUnion(nozzles));')
s=s.replace('var seat=c+vector(0,24.5,0)*millimeter;','var seat=c+vector(0,52.5,0)*millimeter;')
s=s.replace('3*millimeter,12*millimeter,5.68*millimeter,2.5*millimeter,"M3x12 cover through-bolt "','3*millimeter,40*millimeter,5.68*millimeter,2.5*millimeter,"M3x40 cover-extension through-bolt "')
assert 'r10ColletFan(context,id+"metalCollet",prop)' in s and 'Expected 45 R10' in s
(r/'native-r10.fs').write_text(s,encoding='utf-8')
print('Native R10 characters',len(s))
