function r7Boolean(context is Context,id is Id,definition is map)
{
    try { opBoolean(context,id,definition); }
    catch(error) { throw regenError("R7 Boolean failed: "~id[size(id)-1]); }
}

// Custom printed 2 mm-pitch tapered thread. Not a standard metal fastener.
function r7RootRadius(y is ValueWithUnits)
{
    return 18.9*millimeter+0.3*y;
}

function r7ThreadRidge(context is Context,id is Id,radialClearance is ValueWithUnits,axialClearance is ValueWithUnits)
{
    // Explicit radial sections prevent the profile twist of a free sweep.
    // Each 15-degree station advances 1/12 mm along the 2 mm-pitch thread.
    var profiles=[];var sketches=[];
    for(var n=0;n<=144;n+=1)
    {
        var y=(-7+n/12)*millimeter;
        var angle=n*15*degree;
        var turn=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),angle);
        var radius=r7RootRadius(y)+radialClearance;
        var sid=id+("section"~n);
        var sk=newSketchOnPlane(context,sid,{"sketchPlane":plane(turn*vector(radius,y,0*millimeter),turn.linear*vector(0,0,1),turn.linear*vector(1,0,0))});
        var points=[vector(-0.15*millimeter,-0.8*millimeter-axialClearance),
            vector(0.65*millimeter,-0.15*millimeter-axialClearance),
            vector(0.65*millimeter,0.15*millimeter+axialClearance),
            vector(-0.15*millimeter,0.8*millimeter+axialClearance)];
        for(var k=0;k<4;k+=1) points[k]=vector(points[k][0]+0.3*points[k][1],points[k][1]);
        for(var k=0;k<4;k+=1) skLineSegment(sk,"side"~k,{"start":points[k],"end":points[(k+1)%4]});
        skSolve(sk);
        profiles=append(profiles,qSketchRegion(sid));
        sketches=append(sketches,qCreatedBy(sid,EntityType.BODY));
    }
    opLoft(context,id+"ridge",{"profileSubqueries":profiles,"bodyType":ToolBodyType.SOLID});
    var ridge=qCreatedBy(id+"ridge",EntityType.BODY);
    if(size(evaluateQuery(context,ridge))!=1) throw regenError("R7 loft must create one thread ridge.");
    opDeleteBodies(context,id+"cleanup",{"entities":qUnion(sketches)});
    return {"body":ridge,"rotationSign":1};
}

function r7RingBlank(context is Context,id is Id,y0 is ValueWithUnits,y1 is ValueWithUnits,label is string)
{
    fCylinder(context,id+"outer",{"bottomCenter":vector(0*millimeter,y0,0*millimeter),"topCenter":vector(0*millimeter,y1,0*millimeter),"radius":23*millimeter});
    setAttribute(context,{"entities":qCreatedBy(id+"outer",EntityType.BODY),"name":"r7RetentionRole","attribute":{"role":label}});
    var ring=qHasAttributeWithValueMatching(qAllModifiableSolidBodies(),"r7RetentionRole",{"role":label});
    checkedFillet(context,id+"rimRounds",{"entities":qGeometry(qOwnedByBody(ring,EntityType.EDGE),GeometryType.CIRCLE),"radius":0.35*millimeter});
    var grips=[];
    for(var k=0;k<12;k+=1)
    {
        var angle=k*30*degree;
        var offset=vector(cos(angle),0,sin(angle))*23.2*millimeter;
        fCylinder(context,id+("grip"~k),{"bottomCenter":offset+vector(0*millimeter,y0-0.1*millimeter,0*millimeter),
            "topCenter":offset+vector(0*millimeter,y1+0.1*millimeter,0*millimeter),"radius":0.7*millimeter});
        grips=append(grips,qCreatedBy(id+("grip"~k),EntityType.BODY));
    }
    r7Boolean(context,id+"gripCuts",{"tools":qUnion(grips),"targets":ring,"operationType":BooleanOperationType.SUBTRACTION});
    checkedFillet(context,id+"gripSoftEdges",{"entities":qCreatedBy(id+"gripCuts",EntityType.EDGE),"radius":0.12*millimeter,"tangentPropagation":false});
    setProperty(context,{"entities":ring,"propertyType":PropertyType.NAME,"value":label});
    setProperty(context,{"entities":ring,"propertyType":PropertyType.APPEARANCE,"value":color(0.56,0.72,0.81)});
    return ring;
}

function r7BuildRetention(context is Context,id is Id,originalProp is Query)
{
    setAttribute(context,{"entities":originalProp,"name":"r7RetentionRole","attribute":{"role":"propeller"}});
    var prop=qHasAttributeWithValueMatching(qAllModifiableSolidBodies(),"r7RetentionRole",{"role":"propeller"});
    // Existing filled 5.5 mm motor drive keys and their relief are retained.
    // The cone contains the original hub from Y=-3 forward. Keep its blade roots.

    fCone(context,id+"taperRoot",{"bottomCenter":vector(0,-5.4,0)*millimeter,"topCenter":vector(0,4.2,0)*millimeter,
        "bottomRadius":r7RootRadius(-5.4*millimeter),"topRadius":r7RootRadius(4.2*millimeter)});
    var root=qCreatedBy(id+"taperRoot",EntityType.BODY);
    fCone(context,id+"rootBlend",{"bottomCenter":vector(0,4.1,0)*millimeter,"topCenter":vector(0,8.5,0)*millimeter,
        "bottomRadius":r7RootRadius(4.1*millimeter),"topRadius":18*millimeter});
    // Solid runout shoulder supports the final partial thread and limits travel.
    fCylinder(context,id+"runoutStop",{"bottomCenter":vector(0,3.6,0)*millimeter,"topCenter":vector(0,4.2,0)*millimeter,"radius":20.85*millimeter});
    var stop=qCreatedBy(id+"runoutStop",EntityType.BODY);
    checkedFillet(context,id+"stopSoftEdges",{"entities":qGeometry(qOwnedByBody(stop,EntityType.EDGE),GeometryType.CIRCLE),"radius":0.15*millimeter});
    r7Boolean(context,id+"rootJoin",{"tools":qUnion([root,qCreatedBy(id+"rootBlend",EntityType.BODY),stop]),"operationType":BooleanOperationType.UNION});
    fCylinder(context,id+"bellBore",{"bottomCenter":vector(0,-5.5,0)*millimeter,"topCenter":vector(0,8.6,0)*millimeter,"radius":14*millimeter});
    r7Boolean(context,id+"boreRoot",{"tools":qCreatedBy(id+"bellBore",EntityType.BODY),"targets":root,"operationType":BooleanOperationType.SUBTRACTION});
    var male=r7ThreadRidge(context,id+"male",0*millimeter,0*millimeter);
    fCylinder(context,id+"threadLength",{"bottomCenter":vector(0,-5.2,0)*millimeter,"topCenter":vector(0,4,0)*millimeter,"radius":23*millimeter});
    r7Boolean(context,id+"trimMaleThread",{"tools":qUnion([male.body,qCreatedBy(id+"threadLength",EntityType.BODY)]),"operationType":BooleanOperationType.INTERSECTION});
    var trimmedRidge=qUnion([male.body,qCreatedBy(id+"trimMaleThread",EntityType.BODY),qOwnerBody(qCreatedBy(id+"trimMaleThread",EntityType.FACE))]);
    if(size(evaluateQuery(context,trimmedRidge))!=1) throw regenError("R7 clipped ridge count "~size(evaluateQuery(context,trimmedRidge))~", root count "~size(evaluateQuery(context,root)));
    r7Boolean(context,id+"maleToRoot",{"tools":qUnion([root,trimmedRidge]),"operationType":BooleanOperationType.UNION});
    r7Boolean(context,id+"collarToProp",{"tools":qUnion([prop,root]),"operationType":BooleanOperationType.UNION});
    if(size(evaluateQuery(context,prop))!=1) throw regenError("R7 propeller count after sleeve join: "~size(evaluateQuery(context,prop)));

    // Four rounded-end flex slots, between the two blade roots.
    var slots=[];
    for(var k=0;k<4;k+=1)
    {
        var sid=id+("slot"~k);
        fCuboid(context,sid+"box",{"corner1":vector(13.7,-5.6,-0.45)*millimeter,"corner2":vector(22.5,7.5,0.45)*millimeter});
        fCylinder(context,sid+"round",{"bottomCenter":vector(13.7,7.5,0)*millimeter,"topCenter":vector(22.5,7.5,0)*millimeter,"radius":0.45*millimeter});
        var cuts=qUnion([qCreatedBy(sid+"box",EntityType.BODY),qCreatedBy(sid+"round",EntityType.BODY)]);
        opTransform(context,sid+"rotate",{"bodies":cuts,"transform":rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),(45+90*k)*degree)});
        slots=append(slots,cuts);
    }
    r7Boolean(context,id+"flexSlots",{"tools":qUnion(slots),"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
    if(size(evaluateQuery(context,prop))!=1)
    {
        var details="";
        for(var piece in evaluateQuery(context,prop))
        {
            var b=evBox3d(context,{"topology":piece,"tight":true});
            details=details~" ["~((b.maxCorner-b.minCorner)/millimeter)~" at "~(b.minCorner/millimeter)~"]";
        }
        throw regenError("R7 split pieces: "~details);
    }

    var collar=r7RingBlank(context,id+"collar",-3*millimeter,2*millimeter,"R7 compression collar - external printed thread");
    var jam=r7RingBlank(context,id+"jam",-6*millimeter,-3*millimeter,"R7 jam ring - counter tighten against collar");
    fCone(context,id+"femaleCore",{"bottomCenter":vector(0,-7.2,0)*millimeter,"topCenter":vector(0,5.2,0)*millimeter,
        "bottomRadius":r7RootRadius(-7.2*millimeter)+0.25*millimeter,"topRadius":r7RootRadius(5.2*millimeter)+0.25*millimeter});
    var female=r7ThreadRidge(context,id+"female",0.25*millimeter,0.1*millimeter);
    r7Boolean(context,id+"ringThreads",{"tools":qUnion([qCreatedBy(id+"femaleCore",EntityType.BODY),female.body]),"targets":qUnion([collar,jam]),"operationType":BooleanOperationType.SUBTRACTION});
    // Remove the sharp first thread at both ends with short conical lead-ins.
    var leads=[];
    var ends=[[-3*millimeter,2*millimeter],[-6*millimeter,-3*millimeter]];
    for(var k=0;k<2;k+=1)
    {
        var ya=ends[k][0];var yb=ends[k][1];
        fCone(context,id+("entry"~k),{"bottomCenter":vector(0*millimeter,ya-0.01*millimeter,0*millimeter),"topCenter":vector(0*millimeter,ya+0.45*millimeter,0*millimeter),
            "bottomRadius":r7RootRadius(ya)+0.85*millimeter,"topRadius":r7RootRadius(ya+0.45*millimeter)+0.25*millimeter});
        fCone(context,id+("exit"~k),{"bottomCenter":vector(0*millimeter,yb-0.45*millimeter,0*millimeter),"topCenter":vector(0*millimeter,yb+0.01*millimeter,0*millimeter),
            "bottomRadius":r7RootRadius(yb-0.45*millimeter)+0.25*millimeter,"topRadius":r7RootRadius(yb)+0.85*millimeter});
        leads=append(leads,qCreatedBy(id+("entry"~k),EntityType.BODY));leads=append(leads,qCreatedBy(id+("exit"~k),EntityType.BODY));
    }
    r7Boolean(context,id+"ringLeadIns",{"tools":qUnion(leads),"targets":qUnion([collar,jam]),"operationType":BooleanOperationType.SUBTRACTION});
    var seated=transform(vector(0,0.5,0)*millimeter)*rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),male.rotationSign*90*degree);
    opTransform(context,id+"preseatRings",{"bodies":qUnion([collar,jam]),"transform":seated});
    if(size(evaluateQuery(context,collar))!=1 || size(evaluateQuery(context,jam))!=1) throw regenError("Both R7 locking rings must remain connected parts.");
    setProperty(context,{"entities":prop,"propertyType":PropertyType.NAME,"value":"R7 propeller - bolt-free external collet, original drive keys"});
}
