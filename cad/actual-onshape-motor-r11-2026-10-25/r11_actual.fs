// R11 imports exact source solids from the user's Motor document.
// Metal geometry receives rigid transforms and display properties only.
function applyR11ActualMotor(context is Context,id is Id,nozzle is Query)
{
    var source=[];var old=[];var fans=[];var bolts=[];var washers=[];
    for(var b in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var bb=evBox3d(context,{"topology":b,"tight":true});
        var d=(bb.maxCorner-bb.minCorner)/millimeter;
        if(bb.minCorner[1]>150*millimeter) { source=append(source,b);continue; }
        if(d[2]>70 && d[0]<50 && bb.minCorner[1]>24*millimeter && bb.maxCorner[1]<31*millimeter) fans=append(fans,b);
        if((d[0]>27 && d[0]<29 && d[1]>25 && bb.minCorner[1]>-5.01*millimeter) ||
           (d[0]>27 && d[0]<29 && d[1]>3 && d[1]<6.1 && abs(bb.minCorner[1]+11*millimeter)<1e-4*millimeter) ||
           (abs(d[0]-15.5)<1e-4 && abs(d[1]-25)<1e-4 && abs(bb.minCorner[1]-16.3*millimeter)<1e-4*millimeter) ||
           (abs(d[0]-15.5)<1e-4 && abs(d[1]-1.5)<1e-4 && abs(bb.minCorner[1]-30.8*millimeter)<1e-4*millimeter) ||
           (abs(d[1]-5)<1e-4 && abs(bb.minCorner[1]-32.3*millimeter)<1e-4*millimeter)) old=append(old,b);
        if(abs(bb.minCorner[1]+19.5*millimeter)<1e-4*millimeter && abs(bb.maxCorner[1]+8.5*millimeter)<1e-4*millimeter && d[0]<6 && d[2]<6) bolts=append(bolts,b);
        if(abs(bb.minCorner[1]+16.5*millimeter)<1e-4*millimeter && abs(d[1]-0.5)<1e-4 && d[0]<8 && d[2]<8) washers=append(washers,b);
    }
    if(size(source)!=4 || size(old)!=5 || size(fans)!=1 || size(bolts)!=4 || size(washers)!=4)
        throw regenError("R11 expects source4, obsolete5, fan1, base bolts4/washers4; found "~size(source)~","~size(old)~","~size(fans)~","~size(bolts)~","~size(washers));
    var fan=qUnion(fans);
    opDeleteBodies(context,id+"removeGenericReferences",{"entities":qUnion(old)});

    // Match the exact source collar-to-nut gap without moving its thread phase.
    var front=31.4450595848951*millimeter;
    fCylinder(context,id+"solidHub",{"bottomCenter":vector(0,24.3,0)*millimeter,"topCenter":vector(0*millimeter,front,0*millimeter),"radius":20*millimeter});
    r8Boolean(context,id+"hubJoin",{"tools":qUnion([fan,qCreatedBy(id+"solidHub",EntityType.BODY)]),"operationType":BooleanOperationType.UNION});
    var rearRim=[];var frontRim=[];
    for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(fan,EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var bb=evBox3d(context,{"topology":e,"tight":true});
        var p=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
        var rr=sqrt(p[0]*p[0]+p[2]*p[2]);
        if(abs(rr-20*millimeter)<1e-4*millimeter && abs(bb.maxCorner[1]-bb.minCorner[1])<1e-5*millimeter)
        {
            if(abs(bb.minCorner[1]-24.3*millimeter)<1e-5*millimeter) rearRim=append(rearRim,e);
            if(abs(bb.minCorner[1]-front)<1e-5*millimeter) frontRim=append(frontRim,e);
        }
    }
    if(size(rearRim)==0 || size(frontRim)==0) throw regenError("R11 needs both flat hub perimeters.");
    checkedFillet(context,id+"rearRim",{"entities":qUnion(rearRim),"radius":0.07*millimeter,"tangentPropagation":false});
    checkedFillet(context,id+"frontRim",{"entities":qUnion(frontRim),"radius":0.35*millimeter,"tangentPropagation":false});
    fCylinder(context,id+"studBore",{"bottomCenter":vector(0,24.2,0)*millimeter,"topCenter":vector(0*millimeter,front+0.1*millimeter,0*millimeter),"radius":2.55*millimeter});
    r8Boolean(context,id+"studBoreCut",{"tools":qCreatedBy(id+"studBore",EntityType.BODY),"targets":fan,"operationType":BooleanOperationType.SUBTRACTION});
    fCylinder(context,id+"neckRelief",{"bottomCenter":vector(0,24.2,0)*millimeter,"topCenter":vector(0,24.65,0)*millimeter,"radius":3.1*millimeter});
    r8Boolean(context,id+"neckReliefCut",{"tools":qCreatedBy(id+"neckRelief",EntityType.BODY),"targets":fan,"operationType":BooleanOperationType.SUBTRACTION});
    var mouths=[];var steps=[];
    for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(fan,EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var bb=evBox3d(context,{"topology":e,"tight":true});
        if(abs(bb.maxCorner[1]-bb.minCorner[1])>1e-5*millimeter) continue;
        var p=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
        var rr=sqrt(p[0]*p[0]+p[2]*p[2]);
        if((abs(bb.minCorner[1]-front)<1e-5*millimeter && abs(rr-2.55*millimeter)<1e-4*millimeter) ||
            (abs(bb.minCorner[1]-24.3*millimeter)<1e-5*millimeter && abs(rr-3.1*millimeter)<1e-4*millimeter)) mouths=append(mouths,e);
        if(abs(bb.minCorner[1]-24.65*millimeter)<1e-5*millimeter && (abs(rr-3.1*millimeter)<1e-4*millimeter || abs(rr-2.55*millimeter)<1e-4*millimeter)) steps=append(steps,e);
    }
    if(size(mouths)!=2 || size(steps)!=2) throw regenError("R11 needs two bore mouths and two shoulder-step rims.");
    checkedFillet(context,id+"boreMouths",{"entities":qUnion(mouths),"radius":0.2*millimeter,"tangentPropagation":false});
    checkedFillet(context,id+"neckStepRounds",{"entities":qUnion(steps),"radius":0.1*millimeter,"tangentPropagation":false});
    opTransform(context,id+"seatOnActualCollar",{"bodies":fan,"transform":transform(vector(0,0.2346,0)*millimeter)});
    setProperty(context,{"entities":fan,"propertyType":PropertyType.NAME,"value":"R11 fan - actual adapter, 5.1 bore, 7.145 hub"});

    var rotation=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),45*degree);
    var place=transform(rotation.linear,vector(0,-184.33,0)*millimeter);
    var motor=qNothing();
    for(var b in source)
    {
        var bb=evBox3d(context,{"topology":b,"tight":true});var d=(bb.maxCorner-bb.minCorner)/millimeter;
        var label="";var role="";
        if(d[0]>27 && d[1]>40) { label="ACTUAL A2212 motor - original fused CAD reference";role="motor";motor=b; }
        else if(d[0]>7 && d[0]<9 && d[1]>22) { label="ACTUAL motor collet thread - Motor source";role="collet"; }
        else if(d[0]>12 && d[1]<8) { label="ACTUAL motor prop collar - Motor source";role="collar"; }
        else if(d[0]>11 && d[1]>14) { label="ACTUAL motor bullet nut - Motor source";role="nut"; }
        else throw regenError("Unrecognized R11 source shape.");
        setAttribute(context,{"entities":b,"name":"r11SourceRole","attribute":{"role":role}});
        var sourceRotation=rotation;
        var sourceY=-184.33*millimeter;
        if(role=="collet") sourceY+=1.905*millimeter;
        if(role=="nut")
        {
            sourceRotation=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),(45-96.73356114112303)*degree);
            sourceY+=16.0096595848951*millimeter;
        }
        if(role=="collar")
        {
            sourceRotation=rotation*rotationAround(line(vector(0,0,0)*millimeter,vector(1,0,0)),180*degree);
            sourceY=224.5346*millimeter;
        }
        var sourcePlace=transform(sourceRotation.linear,vector(0*millimeter,sourceY,0*millimeter));
        opTransform(context,id+("place"~role),{"bodies":b,"transform":sourcePlace});
        setProperty(context,{"entities":b,"propertyType":PropertyType.NAME,"value":label});
    }
    if(size(evaluateQuery(context,motor))!=1) throw regenError("R11 motor source missing.");
    var oldAxes=[vector(9.5,0,0),vector(-9.5,0,0),vector(0,0,8),vector(0,0,-8)];
    var newAxes=[vector(9.4361,0,0),vector(-9.4361,0,0),vector(0,0,8.0137),vector(0,0,-8.0137)];
    for(var b in evaluateQuery(context,qUnion([qUnion(bolts),qUnion(washers)])))
    {
        var bb=evBox3d(context,{"topology":b,"tight":true});var mid=(bb.minCorner+bb.maxCorner)/(2*millimeter);
        var index=-1;
        for(var j=0;j<4;j+=1) if(norm(vector(mid[0],0,mid[2])-oldAxes[j])<1e-4) index=j;
        if(index<0) throw regenError("R11 cannot identify a motor-base fastener axis.");
        var shift=newAxes[index]-oldAxes[index];
        if(bb.maxCorner[1]-bb.minCorner[1]>1*millimeter) shift+=vector(0,-0.5,0);
        opTransform(context,id+("baseAlign"~index~(bb.maxCorner[1]-bb.minCorner[1]>1*millimeter ? "bolt" : "washer")),{"bodies":b,"transform":transform(shift*millimeter)});
    }
    for(var j=0;j<4;j+=1) finalM3Washer(context,id+("extraWasher"~j),(newAxes[j]+vector(0,-17,0))*millimeter,vector(0,1,0),"M3 second motor-base washer "~(j+1)~" (R11)");

    var axis=coordSystem(vector(0,0,0)*millimeter,vector(1,0,0),vector(0,1,0));
    opMateConnector(context,id+"fanAxis",{"coordSystem":axis,"owner":fan});
    opMateConnector(context,id+"frameAxis",{"coordSystem":axis,"owner":nozzle});
    setProperty(context,{"entities":qCreatedBy(id+"fanAxis",EntityType.BODY),"propertyType":PropertyType.NAME,"value":"R11 shaft axis - fan"});
    setProperty(context,{"entities":qCreatedBy(id+"frameAxis",EntityType.BODY),"propertyType":PropertyType.NAME,"value":"R11 shaft axis - frame"});
    if(size(evaluateQuery(context,qAllModifiableSolidBodies()))!=48) throw regenError("R11 expects 48 solids: actual motor,3 adapter pieces, fan/structure and40 fasteners.");
}
