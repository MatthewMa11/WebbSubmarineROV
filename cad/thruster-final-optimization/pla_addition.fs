// Approved P1S / PLA Basic assembly completion, 15 October 2026.
// Cover, propeller, insert and motor geometry/placement are protected.
function finalM3Washer(context is Context,id is Id,seat is Vector,axis is Vector,label is string)
{
    fCylinder(context,id+"body",{"bottomCenter":seat,"topCenter":seat+axis*0.5*millimeter,"radius":3.5*millimeter});
    var body=qCreatedBy(id+"body",EntityType.BODY);
    fCylinder(context,id+"bore",{"bottomCenter":seat-axis*0.01*millimeter,"topCenter":seat+axis*0.51*millimeter,"radius":1.6*millimeter});
    opBoolean(context,id+"clear",{"tools":qCreatedBy(id+"bore",EntityType.BODY),"targets":body,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":body,"propertyType":PropertyType.NAME,"value":label});
    setProperty(context,{"entities":body,"propertyType":PropertyType.APPEARANCE,"value":color(0.25,0.26,0.27)});
}

function applyFinalPlaAssembly(context is Context,id is Id,nozzle is Query)
{
    var motorAxes=[vector(9.5,0,0),vector(-9.5,0,0),vector(0,0,8),vector(0,0,-8)];
    var tools=[];
    for(var i=0;i<4;i+=1)
    {
        var sid=id+("motorAccess"~i);
        fCylinder(context,sid,{"bottomCenter":(motorAxes[i]+vector(0,-45,0))*millimeter,
            "topCenter":(motorAxes[i]+vector(0,-16,0))*millimeter,"radius":3.8*millimeter});
        tools=append(tools,qCreatedBy(sid,EntityType.BODY));
    }
    opBoolean(context,id+"motorAccessCut",{"tools":qUnion(tools),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
    var floors=[];
    var mouths=[];
    for(var e in evaluateQuery(context,qCreatedBy(id+"motorAccessCut",EntityType.EDGE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(abs(b.minCorner[1]+16*millimeter)<1e-5*millimeter && abs(b.maxCorner[1]+16*millimeter)<1e-5*millimeter &&
            abs(b.maxCorner[0]-b.minCorner[0]-7.6*millimeter)<1e-5*millimeter)
            floors=append(floors,e);
        if(b.maxCorner[1]<-18*millimeter) mouths=append(mouths,e);
    }
    if(size(floors)!=4) throw regenError("Expected the four motor-base washer seats at Y=-16 mm.");
    checkedFillet(context,id+"motorSeatRounds",{"entities":qUnion(floors),"radius":0.15*millimeter});
    if(size(mouths)>0) checkedFillet(context,id+"motorAccessMouthRounds",{"entities":qUnion(mouths),"radius":0.25*millimeter,"tangentPropagation":true});

    // The three original cover holes are D4, 3 mm blind holes. Never put nuts
    // behind those floors or drive screws through the unchanged cover.
    // Captured nozzle nuts lock M3x8 retention pins; tips stop 0.996 mm short.
    var directions=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1)];
    for(var i=0;i<3;i+=1)
    {
        var d=directions[i];
        var center=vector(0,20.5,0)*millimeter;
        var sid=id+("cover"~i);
        fCylinder(context,sid+"headPocket",{"bottomCenter":center+d*49.25*millimeter,
            "topCenter":center+d*55*millimeter,"radius":3.8*millimeter});
        opBoolean(context,sid+"headCut",{"tools":qCreatedBy(sid+"headPocket",EntityType.BODY),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
        var rings=[];
        for(var e in evaluateQuery(context,qGeometry(qCreatedBy(sid+"headCut",EntityType.EDGE),GeometryType.CIRCLE)))
        {
            var b=evBox3d(context,{"topology":e,"tight":true});
            var span=b.maxCorner-b.minCorner;
            if(abs(max([span[0],span[1],span[2]])-7.6*millimeter)<1e-5*millimeter) rings=append(rings,e);
        }
        if(size(rings)!=2) throw regenError("Expected a flat recessed cover washer seat.");
        checkedFillet(context,sid+"headPocketRounds",{"entities":qUnion(rings),"radius":0.15*millimeter});
        var nutTool=hexPrism(context,sid+"nutPocket",center+d*47.4*millimeter,-d,5.8*millimeter,8*millimeter);
        opBoolean(context,sid+"nutCut",{"tools":nutTool,"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
        var corners=[];
        for(var e in evaluateQuery(context,qGeometry(qCreatedBy(sid+"nutCut",EntityType.EDGE),GeometryType.LINE)))
        {
            var tangent=evEdgeTangentLine(context,{"edge":e,"parameter":0.5});
            if(abs(dot(tangent.direction,d))>0.99999 && evLength(context,{"entities":e})>0.5*millimeter)
                corners=append(corners,e);
        }
        if(size(corners)>0) checkedFillet(context,sid+"nutPocketRounds",{"entities":qUnion(corners),"radius":0.15*millimeter});
    }
    for(var i=0;i<4;i+=1)
    {
        var seat=(motorAxes[i]+vector(0,-16.5,0))*millimeter;
        kitCapScrew(context,id+("motorScrew"~i),seat,vector(0,1,0),3*millimeter,8*millimeter,5.68*millimeter,2.5*millimeter,"M3x8 motor-base screw "~(i+1));
        finalM3Washer(context,id+("motorWasher"~i),seat,vector(0,1,0),"M3 flat washer motor base "~(i+1));
    }
    for(var i=0;i<3;i+=1)
    {
        var d=directions[i];
        var center=vector(0,20.5,0)*millimeter;
        var seat=center+d*49.75*millimeter;
        kitCapScrew(context,id+("coverScrew"~i),seat,-d,3*millimeter,8*millimeter,5.68*millimeter,2.5*millimeter,"M3x8 cover retention bolt "~(i+1));
        finalM3Washer(context,id+("coverWasher"~i),seat,-d,"M3 flat washer cover "~(i+1));
        var nut=hexPrism(context,id+("coverNut"~i),center+d*47.4*millimeter,-d,5.5*millimeter,2.4*millimeter);
        fCylinder(context,id+("coverNutBore"~i),{"bottomCenter":center+d*47.41*millimeter,
            "topCenter":center+d*44.99*millimeter,"radius":1.5*millimeter});
        opBoolean(context,id+("coverNutClear"~i),{"tools":qCreatedBy(id+("coverNutBore"~i),EntityType.BODY),"targets":nut,"operationType":BooleanOperationType.SUBTRACTION});
        setProperty(context,{"entities":nut,"propertyType":PropertyType.NAME,"value":"M3 captured cover nut "~(i+1)});
        setProperty(context,{"entities":nut,"propertyType":PropertyType.APPEARANCE,"value":color(0.25,0.26,0.27)});
    }
}

