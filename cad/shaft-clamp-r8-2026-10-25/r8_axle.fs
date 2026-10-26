// R8: two-jaw external axle retention. Four existing keys carry drive torque.
// Reference shaft is 3.175 mm. Physical shaft fit and retention require testing.
function r8Boolean(context is Context,id is Id,definition is map)
{
    try { opBoolean(context,id,definition); }
    catch(error) { throw regenError("R8 Boolean failed: "~id[size(id)-1]); }
}

function r8Box(context is Context,id is Id,a is Vector,b is Vector)
{
    fCuboid(context,id+"box",{"corner1":a*millimeter,"corner2":b*millimeter});
    var body=qCreatedBy(id+"box",EntityType.BODY);
    checkedFillet(context,id+"rounds",{"entities":qOwnedByBody(body,EntityType.EDGE),"radius":0.4*millimeter});
    return body;
}

function r8Nut(context is Context,id is Id,x is number,axis is Vector,z is number,label is string)
{
    // Flat sides face fore/aft: 5.5 mm Y width leaves clearance to the cap.
    var seat=vector(x,15.8,z)*millimeter;
    var sketch=newSketchOnPlane(context,id+"profile",{"sketchPlane":plane(seat,axis,vector(1,0,0))});
    for(var j=0;j<6;j+=1)
    {
        var a=j*60*degree;var b=((j+1)%6)*60*degree;
        skLineSegment(sketch,"side"~j,{"start":5.5/sqrt(3)*vector(cos(a),sin(a))*millimeter,"end":5.5/sqrt(3)*vector(cos(b),sin(b))*millimeter});
    }
    skSolve(sketch);
    opExtrude(context,id+"solid",{"entities":qSketchRegion(id+"profile"),"direction":axis,"endBound":BoundingType.BLIND,"endDepth":2.4*millimeter});
    var nut=qCreatedBy(id+"solid",EntityType.BODY);
    opDeleteBodies(context,id+"cleanup",{"entities":qCreatedBy(id+"profile",EntityType.BODY)});
    fCylinder(context,id+"bore",{"bottomCenter":seat-axis*0.01*millimeter,"topCenter":seat+axis*2.41*millimeter,"radius":1.5*millimeter});
    r8Boolean(context,id+"boreCut",{"tools":qCreatedBy(id+"bore",EntityType.BODY),"targets":nut,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":nut,"propertyType":PropertyType.NAME,"value":label});
    setProperty(context,{"entities":nut,"propertyType":PropertyType.APPEARANCE,"value":color(0.25,0.26,0.27)});
}

function r8BuildAxleClamp(context is Context,id is Id,originalProp is Query)
{
    setAttribute(context,{"entities":originalProp,"name":"r8Role","attribute":{"role":"fan"}});
    var fan=qHasAttributeWithValueMatching(qAllModifiableSolidBodies(),"r8Role",{"role":"fan"});
    var lower=[r8Box(context,id+"lowerBridge",vector(-20.8,14.2,-6.2),vector(20.8,19.3,6.2))];
    for(var i=0;i<2;i+=1)
    {
        var x=(i==0 ? -20.8 : 13.2);
        lower=append(lower,r8Box(context,id+("lowerEar"~i),vector(x,12.2,-6.2),vector(x+7.6,19.3,6.2)));
    }
    r8Boolean(context,id+"lowerJoin",{"tools":qUnion([fan,qUnion(lower)]),"operationType":BooleanOperationType.UNION});
    // Leave the original key roots supported by a 0.95 mm backing plate.
    var seats=[];
    fCuboid(context,id+"bridgeSeat",{"corner1":vector(-13.8,15.15,0)*millimeter,"corner2":vector(13.8,19.7,6.45)*millimeter});
    seats=append(seats,qCreatedBy(id+"bridgeSeat",EntityType.BODY));
    for(var i=0;i<2;i+=1)
    {
        var x=(i==0 ? -21.05 : 13.0);
        fCuboid(context,id+("earSeat"~i),{"corner1":vector(x,12.0,0)*millimeter,"corner2":vector(x+8.05,19.7,6.45)*millimeter});
        seats=append(seats,qCreatedBy(id+("earSeat"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"seatCut",{"tools":qUnion(seats),"targets":fan,"operationType":BooleanOperationType.SUBTRACTION});

    var upper=r8Box(context,id+"upperBridge",vector(-13.5,15.4,0.3),vector(13.5,19.3,6.2));
    setAttribute(context,{"entities":upper,"name":"r8Role","attribute":{"role":"jaw"}});
    var jaw=qHasAttributeWithValueMatching(qAllModifiableSolidBodies(),"r8Role",{"role":"jaw"});
    var ears=[];
    for(var i=0;i<2;i+=1)
    {
        var x=(i==0 ? -20.8 : 13.2);
        ears=append(ears,r8Box(context,id+("upperEar"~i),vector(x,12.2,0.3),vector(x+7.6,19.3,6.2)));
    }
    r8Boolean(context,id+"upperJoin",{"tools":qUnion([jaw,qUnion(ears)]),"operationType":BooleanOperationType.UNION});
    // Every new feature behind the original motor face clears the rotor bell.
    fCylinder(context,id+"bellEnvelope",{"bottomCenter":vector(0,11.9,0)*millimeter,"topCenter":vector(0,14.2,0)*millimeter,"radius":14.25*millimeter});
    var keyKeeps=[];var keyAxes=[vector(9,0,0),vector(-9,0,0),vector(0,0,9),vector(0,0,-9)];
    for(var i=0;i<4;i+=1)
    {
        fCylinder(context,id+("keyKeep"~i),{"bottomCenter":(keyAxes[i]+vector(0,11.8,0))*millimeter,"topCenter":(keyAxes[i]+vector(0,14.3,0))*millimeter,"radius":2.75*millimeter});
        keyKeeps=append(keyKeeps,qCreatedBy(id+("keyKeep"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"preserveKeys",{"tools":qUnion(keyKeeps),"targets":qCreatedBy(id+"bellEnvelope",EntityType.BODY),"operationType":BooleanOperationType.SUBTRACTION});
    r8Boolean(context,id+"bellClear",{"tools":qCreatedBy(id+"bellEnvelope",EntityType.BODY),"targets":qUnion([fan,jaw]),"operationType":BooleanOperationType.SUBTRACTION});
    fCylinder(context,id+"pilotClearance",{"bottomCenter":vector(0,11.8,0)*millimeter,"topCenter":vector(0,16.25,0)*millimeter,"radius":4.8*millimeter});
    fCylinder(context,id+"axleBore",{"bottomCenter":vector(0,16.24,0)*millimeter,"topCenter":vector(0,19.7,0)*millimeter,"radius":1.65*millimeter});
    r8Boolean(context,id+"centerBores",{"tools":qUnion([qCreatedBy(id+"pilotClearance",EntityType.BODY),qCreatedBy(id+"axleBore",EntityType.BODY)]),"targets":qUnion([fan,jaw]),"operationType":BooleanOperationType.SUBTRACTION});

    for(var i=0;i<2;i+=1)
    {
        var sid=id+("hardware"~i);var x=(i==0 ? 16.8 : -16.8);
        fCylinder(context,sid+"through",{"bottomCenter":vector(x,15.8,-12)*millimeter,"topCenter":vector(x,15.8,12)*millimeter,"radius":1.7*millimeter});
        r8Boolean(context,sid+"boltClear",{"tools":qCreatedBy(sid+"through",EntityType.BODY),"targets":qUnion([fan,jaw]),"operationType":BooleanOperationType.SUBTRACTION});
        // Open clearance above and below each bearing face for head, nut and tool.
        var outside=[];
        for(var k=0;k<2;k+=1)
        {
            var za=(k==0 ? 6.2 : -30);var zb=(k==0 ? 30 : -6.2);
            fCylinder(context,sid+("outside"~k),{"bottomCenter":vector(x,15.8,za)*millimeter,"topCenter":vector(x,15.8,zb)*millimeter,"radius":4.3*millimeter});
            outside=append(outside,qCreatedBy(sid+("outside"~k),EntityType.BODY));
        }
        r8Boolean(context,sid+"toolAccess",{"tools":qUnion(outside),"targets":fan,"operationType":BooleanOperationType.SUBTRACTION});
        var dir=(i==0 ? -1 : 1);var axis=vector(0,0,dir);
        kitCapScrew(context,sid+"bolt",vector(x,15.8,-dir*6.2)*millimeter,axis,3*millimeter,16*millimeter,5.68*millimeter,2.5*millimeter,"R8 M3x16 axle clamp bolt "~(i+1));
        r8Nut(context,sid+"nut",x,axis,dir*6.2,"R8 M3 axle clamp nut AF5.5x2.4 - "~(i+1));
    }
    if(size(evaluateQuery(context,fan))!=1 || size(evaluateQuery(context,jaw))!=1) throw regenError("R8 fan and removable jaw must each be one connected body.");
    setProperty(context,{"entities":fan,"propertyType":PropertyType.NAME,"value":"R8 fan - M3 axle clamp lower jaw, four motor drive keys"});
    setProperty(context,{"entities":jaw,"propertyType":PropertyType.NAME,"value":"R8 removable axle clamp upper jaw - 3.175 mm shaft"});
    setProperty(context,{"entities":jaw,"propertyType":PropertyType.APPEARANCE,"value":color(0.56,0.72,0.81)});
}
