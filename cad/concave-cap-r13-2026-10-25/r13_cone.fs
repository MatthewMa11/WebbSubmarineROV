// R13: concave inner cone, front-loaded M3 nuts, short screws and locating pilots.
function r13ConeAndJoints(context is Context,id is Id,nozzle is Query)
{
    var caps=[];var bolts=[];var nuts=[];var rearWashers=[];
    for(var b in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var bb=evBox3d(context,{"topology":b,"tight":true});var d=(bb.maxCorner-bb.minCorner)/millimeter;
        var mid=(bb.maxCorner+bb.minCorner)/(2*millimeter);
        if(d[0]>90 && bb.minCorner[1]>46.9*millimeter) caps=append(caps,b);
        if(abs(max([abs(mid[0]),abs(mid[2])])-44.5)>1e-4) continue;
        if(abs(bb.minCorner[1]-12.5*millimeter)<1e-4*millimeter && abs(bb.maxCorner[1]-55.5*millimeter)<1e-4*millimeter) bolts=append(bolts,b);
        if(abs(bb.minCorner[1]-13.1*millimeter)<1e-4*millimeter && abs(d[1]-2.4)<1e-4) nuts=append(nuts,b);
        if(abs(bb.minCorner[1]-15.5*millimeter)<1e-4*millimeter && abs(d[1]-0.5)<1e-4) rearWashers=append(rearWashers,b);
    }
    if(size(caps)!=1 || size(bolts)!=4 || size(nuts)!=4 || size(rearWashers)!=4) throw regenError("R13 expects cone1 and cover bolts/nuts/rear washers4 each.");
    var cap=qUnion(caps);
    // Close the obsolete blind shaft passage before forming a continuous bowl.
    fCylinder(context,id+"oldPassageFill",{"bottomCenter":vector(0,47.9,0)*millimeter,"topCenter":vector(0,63.1,0)*millimeter,"radius":1.9*millimeter});
    r8Boolean(context,id+"closePassage",{"tools":qUnion([cap,qCreatedBy(id+"oldPassageFill",EntityType.BODY)]),"operationType":BooleanOperationType.UNION});
    opSphere(context,id+"bowlTool",{"center":vector(0,43,0)*millimeter,"radius":13*millimeter});
    r8Boolean(context,id+"bowlCut",{"tools":qCreatedBy(id+"bowlTool",EntityType.BODY),"targets":cap,"operationType":BooleanOperationType.SUBTRACTION});
    var rim=[];
    for(var e in evaluateQuery(context,qGeometry(qCreatedBy(id+"bowlCut",EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var bb=evBox3d(context,{"topology":e,"tight":true});var p=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
        if(abs(bb.minCorner[1]-48*millimeter)<1e-4*millimeter && abs(bb.maxCorner[1]-48*millimeter)<1e-4*millimeter && abs(sqrt(p[0]*p[0]+p[2]*p[2])-12*millimeter)<1e-4*millimeter) rim=append(rim,e);
    }
    if(size(rim)<1) throw regenError("R13 bowl opening rim missing.");
    checkedFillet(context,id+"bowlRimRound",{"entities":qUnion(rim),"radius":0.6*millimeter,"tangentPropagation":false});
    var ds=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1),vector(1,0,0)];
    for(var i=0;i<4;i+=1)
    {
        var sid=id+("joint"~i);var radial=ds[i];var c=radial*44.5*millimeter;
        var turn=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),-i*90*degree);
        var pilot=annularTool(context,sid+"pilot",1.8*millimeter,3.2*millimeter,46.6*millimeter,47.8*millimeter);
        opTransform(context,sid+"pilotPosition",{"bodies":pilot,"transform":transform(c)});
        var top=[];
        for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(pilot,EntityType.EDGE),GeometryType.CIRCLE)))
        {
            var bb=evBox3d(context,{"topology":e,"tight":true});var p=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
            if(abs(bb.minCorner[1]-47.8*millimeter)<1e-4*millimeter && abs(sqrt((p[0]-c[0])^2+(p[2]-c[2])^2)-3.2*millimeter)<1e-4*millimeter) top=append(top,e);
        }
        if(size(top)<1) throw regenError("R13 pilot lead-in missing.");
        checkedFillet(context,sid+"pilotLeadIn",{"entities":qUnion(top),"radius":0.2*millimeter,"tangentPropagation":false});
        r8Boolean(context,sid+"pilotJoin",{"tools":qUnion([nozzle,pilot]),"operationType":BooleanOperationType.UNION});
        fCylinder(context,sid+"pilotSocket",{"bottomCenter":c+vector(0,46.9,0)*millimeter,"topCenter":c+vector(0,48,0)*millimeter,"radius":3.4*millimeter});
        r8Boolean(context,sid+"socketCut",{"tools":qCreatedBy(sid+"pilotSocket",EntityType.BODY),"targets":cap,"operationType":BooleanOperationType.SUBTRACTION});
        var hex=hexPrism(context,sid+"nutPocket",c+vector(0,40.9,0)*millimeter,vector(0,1,0),5.9*millimeter,3.1*millimeter);
        if(abs(radial[0])>0.9) opTransform(context,sid+"hexOrient",{"bodies":hex,"transform":rotationAround(line(c,vector(0,1,0)),90*degree)});
        fCuboid(context,sid+"nutEntry",{"corner1":vector(-2.95,40.9,44.5)*millimeter,"corner2":vector(2.95,44.0,51)*millimeter});
        var entry=qCreatedBy(sid+"nutEntry",EntityType.BODY);opTransform(context,sid+"entryOrient",{"bodies":entry,"transform":turn});
        fCylinder(context,sid+"washerSeat",{"bottomCenter":c+vector(0,43.3,0)*millimeter,"topCenter":c+vector(0,44.3,0)*millimeter,"radius":3.7*millimeter});
        fCuboid(context,sid+"washerEntry",{"corner1":vector(-3.7,43.3,44.5)*millimeter,"corner2":vector(3.7,44.3,51)*millimeter});
        var we=qCreatedBy(sid+"washerEntry",EntityType.BODY);opTransform(context,sid+"washerOrient",{"bodies":we,"transform":turn});
        r8Boolean(context,sid+"pocketCut",{"tools":qUnion([hex,entry,qCreatedBy(sid+"washerSeat",EntityType.BODY),we]),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
        fCylinder(context,sid+"boltClearance",{"bottomCenter":c+vector(0,39.9,0)*millimeter,"topCenter":c+vector(0,52.1,0)*millimeter,"radius":1.8*millimeter});
        r8Boolean(context,sid+"boreCut",{"tools":qCreatedBy(sid+"boltClearance",EntityType.BODY),"targets":qUnion([nozzle,cap]),"operationType":BooleanOperationType.SUBTRACTION});
    }
    for(var i=0;i<4;i+=1)
    {
        var b=bolts[i];var bb=evBox3d(context,{"topology":b,"tight":true});var c=(bb.maxCorner+bb.minCorner)/2;c[1]=0*millimeter;
        fCylinder(context,id+("oldBoltTail"~i),{"bottomCenter":c+vector(0,12.4,0)*millimeter,"topCenter":c+vector(0,40.5,0)*millimeter,"radius":3*millimeter});
        r8Boolean(context,id+("shortenBolt"~i),{"tools":qCreatedBy(id+("oldBoltTail"~i),EntityType.BODY),"targets":b,"operationType":BooleanOperationType.SUBTRACTION});
        setProperty(context,{"entities":b,"propertyType":PropertyType.NAME,"value":"R13 M3x12 cone bolt "~(i+1)});
    }
    opTransform(context,id+"frontNutSeats",{"bodies":qUnion([qUnion(nuts),qUnion(rearWashers)]),"transform":transform(vector(0,28.3,0)*millimeter)});
    setProperty(context,{"entities":cap,"propertyType":PropertyType.NAME,"value":"R13 concave cone -24mm bowl - M3x12 joints"});
    setProperty(context,{"entities":nozzle,"propertyType":PropertyType.NAME,"value":"R13 one-piece housing - front captive nuts and pilots"});
    if(size(evaluateQuery(context,cap))!=1 || size(evaluateQuery(context,nozzle))!=1 || size(evaluateQuery(context,qAllModifiableSolidBodies()))!=47) throw regenError("R13 expects separate cone/housing and47 solids.");
}
