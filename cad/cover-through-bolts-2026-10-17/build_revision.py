from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'native-before.fs').read_text(encoding='utf-8')
# Retain the rounded reinforcing bosses, replace their old radial pin bores.
a=s.index('    for (var i = 0; i < size(directions); i += 1)',s.index('id + "reinforce"'))
b=s.index('    // Adjust only the sixteen',a)
s=s[:a]+'    // R4 uses axial clamping joints instead of radial retention pins.\n\n'+s[b:]
a=s.index('    // The three original cover holes are D4')
b=s.index('    for(var i=0;i<4;i+=1)\n    {\n        var seat=(motorAxes',a)
s=s[:a]+s[b:]
a=s.index('    for(var i=0;i<3;i+=1)',s.index('"M3 flat washer motor base'))
b=s.index('\n}\n',a)
s=s[:a]+'''    var directions=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1),vector(1,0,0)];
    for(var i=0;i<4;i+=1)
    {
        var d=directions[i];
        var c=d*44.5*millimeter;
        var seat=c+vector(0,24.5,0)*millimeter;
        var axis=vector(0,-1,0);
        kitCapScrew(context,id+("coverScrew"~i),seat,axis,3*millimeter,12*millimeter,5.68*millimeter,2.5*millimeter,"M3x12 cover through-bolt "~(i+1));
        finalM3Washer(context,id+("coverWasher"~i),seat,axis,"M3 front washer cover "~(i+1));
        finalM3Washer(context,id+("coverRearWasher"~i),c+vector(0,15.5,0)*millimeter,vector(0,1,0),"M3 rear washer cover "~(i+1));
        var nut=hexPrism(context,id+("coverNut"~i),c+vector(0,15.5,0)*millimeter,axis,5.5*millimeter,2.4*millimeter);
        if(abs(d[0])>0.9) opTransform(context,id+("coverNutOrient"~i),{"bodies":nut,"transform":rotationAround(line(c,vector(0,1,0)),90*degree)});
        fCylinder(context,id+("coverNutBore"~i),{"bottomCenter":c+vector(0,15.51,0)*millimeter,
            "topCenter":c+vector(0,13.09,0)*millimeter,"radius":1.5*millimeter});
        opBoolean(context,id+("coverNutClear"~i),{"tools":qCreatedBy(id+("coverNutBore"~i),EntityType.BODY),"targets":nut,"operationType":BooleanOperationType.SUBTRACTION});
        setProperty(context,{"entities":nut,"propertyType":PropertyType.NAME,"value":"M3 captured cover nut "~(i+1)});
        setProperty(context,{"entities":nut,"propertyType":PropertyType.APPEARANCE,"value":color(0.25,0.26,0.27)});
    }'''+s[b:]
helper=(r/'through_joint.fs').read_text(encoding='utf-8-sig')
pos=s.index('// Finish the three pads')
s=s[:pos]+helper+'\n\n'+s[pos:]
s=s.replace('        applyMotorCenteringCup(context,id+"centeringCup",definition.nozzle);','        applyMotorCenteringCup(context,id+"centeringCup",definition.nozzle);\n        applyCoverThroughJoints(context,id+"throughJoints",definition.nozzle);')
assert s.count('FeatureScript 3095;')==1
(r/'thruster-through-bolts.fs').write_text(s,encoding='utf-8')
print(len(s))

