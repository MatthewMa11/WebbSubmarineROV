// R4: four actual axial clamping joints. Approved cover-tab changes only.
function applyCoverThroughJoints(context is Context,id is Id,nozzle is Query)
{
    var covers=[];
    for(var b in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var bounds=evBox3d(context,{"topology":b,"tight":true});
        if(bounds.maxCorner[0]-bounds.minCorner[0]>80*millimeter && bounds.minCorner[1]>10*millimeter) covers=append(covers,b);
    }
    if(size(covers)!=1) throw regenError("Expected one original front cover.");
    var cover=qUnion(covers);
    var directions=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1),vector(1,0,0)];
    for(var i=0;i<4;i+=1)
    {
        var sid=id+("joint"~i);
        var d=directions[i];
        var c=d*44.5*millimeter;
        fCylinder(context,sid+"ear",{"bottomCenter":c+vector(0,19,0)*millimeter,"topCenter":c+vector(0,24,0)*millimeter,"radius":5*millimeter});
        var ear=qCreatedBy(sid+"ear",EntityType.BODY);
        checkedFillet(context,sid+"earRounds",{"entities":qGeometry(qOwnedByBody(ear,EntityType.EDGE),GeometryType.CIRCLE),"radius":0.6*millimeter});
        opBoolean(context,sid+"earJoin",{"tools":qUnion([cover,ear]),"operationType":BooleanOperationType.UNION});
        // Original imported feet extend about 1 mm behind the new datum.
        // Trim only the local feet to the same flat clamping plane.
        fCylinder(context,sid+"backSpotFace",{"bottomCenter":c+vector(0,16,0)*millimeter,"topCenter":c+vector(0,19,0)*millimeter,"radius":6.8*millimeter});
        opBoolean(context,sid+"backFaceCut",{"tools":qCreatedBy(sid+"backSpotFace",EntityType.BODY),"targets":cover,"operationType":BooleanOperationType.SUBTRACTION});
        fCylinder(context,sid+"flange",{"bottomCenter":c+vector(0,12.5,0)*millimeter,"topCenter":c+vector(0,19,0)*millimeter,"radius":5*millimeter});
        var flange=qCreatedBy(sid+"flange",EntityType.BODY);
        checkedFillet(context,sid+"flangeRounds",{"entities":qGeometry(qOwnedByBody(flange,EntityType.EDGE),GeometryType.CIRCLE),"radius":0.5*millimeter});
        opBoolean(context,sid+"flangeJoin",{"tools":qUnion([nozzle,flange]),"operationType":BooleanOperationType.UNION});
        fCylinder(context,sid+"earSocket",{"bottomCenter":c+vector(0,19,0)*millimeter,"topCenter":c+vector(0,31,0)*millimeter,"radius":6.8*millimeter});
        opBoolean(context,sid+"socketCut",{"tools":qCreatedBy(sid+"earSocket",EntityType.BODY),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
        // Nut T-slot: loading from the duct interior, hex flats stop rotation.
        var hex=hexPrism(context,sid+"nutSlot",c+vector(0,12.8,0)*millimeter,vector(0,1,0),5.9*millimeter,2.8*millimeter);
        if(abs(d[0])>0.9) opTransform(context,sid+"nutSlotOrient",{"bodies":hex,"transform":rotationAround(line(c,vector(0,1,0)),90*degree)});
        var turn=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),i*90*degree);
        // d follows +Z,-X,-Z,+X; positive rotation maps +Z to +X.
        turn=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),-i*90*degree);
        fCuboid(context,sid+"nutEntry",{"corner1":vector(-2.95,12.8,34)*millimeter,"corner2":vector(2.95,15.6,44.5)*millimeter});
        var entry=qCreatedBy(sid+"nutEntry",EntityType.BODY);
        opTransform(context,sid+"entryOrient",{"bodies":entry,"transform":turn});
        fCylinder(context,sid+"rearWasherSeat",{"bottomCenter":c+vector(0,15.3,0)*millimeter,"topCenter":c+vector(0,16,0)*millimeter,"radius":3.7*millimeter});
        fCuboid(context,sid+"washerEntry",{"corner1":vector(-3.7,15.3,34)*millimeter,"corner2":vector(3.7,16,44.5)*millimeter});
        var we=qCreatedBy(sid+"washerEntry",EntityType.BODY);
        opTransform(context,sid+"washerEntryOrient",{"bodies":we,"transform":turn});
        opBoolean(context,sid+"pocketCuts",{"tools":qUnion([hex,entry,qCreatedBy(sid+"rearWasherSeat",EntityType.BODY),we]),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
        // A front spot-face guarantees a flat washer seat on the curved arm.
        fCylinder(context,sid+"frontSpotFace",{"bottomCenter":c+vector(0,24,0)*millimeter,"topCenter":c+vector(0,65,0)*millimeter,"radius":3.7*millimeter});
        opBoolean(context,sid+"frontFaceCut",{"tools":qCreatedBy(sid+"frontSpotFace",EntityType.BODY),"targets":cover,"operationType":BooleanOperationType.SUBTRACTION});
        fCylinder(context,sid+"clearBore",{"bottomCenter":c+vector(0,12,0)*millimeter,"topCenter":c+vector(0,25,0)*millimeter,"radius":1.7*millimeter});
        opBoolean(context,sid+"throughCut",{"tools":qCreatedBy(sid+"clearBore",EntityType.BODY),"targets":qUnion([cover,nozzle]),"operationType":BooleanOperationType.SUBTRACTION});
        var mouths=[];
        for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(qUnion([cover,nozzle]),EntityType.EDGE),GeometryType.CIRCLE)))
        {
            var bounds=evBox3d(context,{"topology":e,"tight":true});
            var mid=(bounds.minCorner+bounds.maxCorner)/2;
            if(norm(vector(mid[0],0*millimeter,mid[2])-c)<1e-5*millimeter && abs(bounds.maxCorner[0]-bounds.minCorner[0]-3.4*millimeter)<1e-5*millimeter && abs(bounds.maxCorner[1]-bounds.minCorner[1])<1e-5*millimeter &&
                (abs(bounds.minCorner[1]-24*millimeter)<1e-5*millimeter || abs(bounds.minCorner[1]-19*millimeter)<1e-5*millimeter || abs(bounds.minCorner[1]-16*millimeter)<1e-5*millimeter)) mouths=append(mouths,e);
        }
        // Coincident cover/nozzle circles at the clamping plane may share one
        // query identity. The exported bearing and bore gauges check both parts.
        if(size(mouths)<3 || size(mouths)>4) throw regenError("Expected M3 mouths at three axial planes at joint "~i~", found "~size(mouths));
        checkedFillet(context,sid+"boreRounds",{"entities":qUnion(mouths),"radius":0.2*millimeter,"tangentPropagation":false});
    }
    if(size(evaluateQuery(context,cover))!=1 || size(evaluateQuery(context,nozzle))!=1) throw regenError("Cover and nozzle must remain separate connected parts.");
    setProperty(context,{"entities":cover,"propertyType":PropertyType.NAME,"value":"Front cover - four M3 through-bolt tabs (R4)"});
    setProperty(context,{"entities":nozzle,"propertyType":PropertyType.NAME,"value":"Nozzle - M3 captive nut joints and motor cup (R4)"});
}

