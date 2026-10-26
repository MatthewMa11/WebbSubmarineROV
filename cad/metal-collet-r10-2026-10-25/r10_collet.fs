// R10: bought metal CPA-317-N prop adapter. Published outer dimensions only;
// this is a clearance envelope, not a machining model of its collet taper.
function r10ColletFan(context is Context,id is Id,prop is Query)
{
    r9ForwardFan(context,id+"bladeLayout",prop);
    // Discard the obsolete four rotor-vent keys, leaving the flat R9 disk.
    fCylinder(context,id+"oldKeys",{"bottomCenter":vector(0,-5,0)*millimeter,"topCenter":vector(0,12.8,0)*millimeter,"radius":36*millimeter});
    r8Boolean(context,id+"removeKeys",{"tools":qCreatedBy(id+"oldKeys",EntityType.BODY),"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
    fCylinder(context,id+"M6clearance",{"bottomCenter":vector(0,12.7,0)*millimeter,"topCenter":vector(0,19.4,0)*millimeter,"radius":3.1*millimeter});
    r8Boolean(context,id+"clearanceBore",{"tools":qCreatedBy(id+"M6clearance",EntityType.BODY),"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
    var mouths=[];
    for(var e in evaluateQuery(context,qGeometry(qCreatedBy(id+"clearanceBore",EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(abs(b.maxCorner[0]-b.minCorner[0]-6.2*millimeter)<1e-5*millimeter && abs(b.maxCorner[1]-b.minCorner[1])<1e-5*millimeter) mouths=append(mouths,e);
    }
    if(size(mouths)!=2) throw regenError("R10 needs two 6.2 mm bore mouths.");
    checkedFillet(context,id+"boreLeadIns",{"entities":qUnion(mouths),"radius":0.25*millimeter,"tangentPropagation":false});
    opTransform(context,id+"adapterPlane",{"bodies":prop,"transform":transform(vector(0,11.5,0)*millimeter)});
    setProperty(context,{"entities":prop,"propertyType":PropertyType.NAME,"value":"R10 fan - 6.2 bore, 6.5 flat hub, metal collet"});
    if(size(evaluateQuery(context,prop))!=1) throw regenError("R10 fan must remain a single body.");

    fCylinder(context,id+"adapterBackEnvelope",{"bottomCenter":vector(0,16.3,0)*millimeter,"topCenter":vector(0,24.3,0)*millimeter,"radius":7.75*millimeter});
    var adapter=qCreatedBy(id+"adapterBackEnvelope",EntityType.BODY);
    fCylinder(context,id+"adapterStudEnvelope",{"bottomCenter":vector(0,24.3,0)*millimeter,"topCenter":vector(0,41.3,0)*millimeter,"radius":3*millimeter});
    r8Boolean(context,id+"adapterJoin",{"tools":qUnion([adapter,qCreatedBy(id+"adapterStudEnvelope",EntityType.BODY)]),"operationType":BooleanOperationType.UNION});
    fCylinder(context,id+"shaftInput",{"bottomCenter":vector(0,16.29,0)*millimeter,"topCenter":vector(0,25.6,0)*millimeter,"radius":1.5875*millimeter});
    r8Boolean(context,id+"shaftInputCut",{"tools":qCreatedBy(id+"shaftInput",EntityType.BODY),"targets":adapter,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":adapter,"propertyType":PropertyType.NAME,"value":"BOUGHT CPA-317-N metal collet and backplate - clearance envelope"});
    setProperty(context,{"entities":adapter,"propertyType":PropertyType.APPEARANCE,"value":color(0.68,0.71,0.74)});
    var washer=annularTool(context,id+"propWasher",3.1*millimeter,7.75*millimeter,30.8*millimeter,32.3*millimeter);
    setProperty(context,{"entities":washer,"propertyType":PropertyType.NAME,"value":"BOUGHT CPA-317-N washer - 1.5 mm reference"});
    setProperty(context,{"entities":washer,"propertyType":PropertyType.APPEARANCE,"value":color(0.68,0.71,0.74)});
    var nut=hexPrism(context,id+"propNut",vector(0,32.3,0)*millimeter,vector(0,1,0),10*millimeter,5*millimeter);
    fCylinder(context,id+"nutThreadEnvelope",{"bottomCenter":vector(0,32.29,0)*millimeter,"topCenter":vector(0,37.31,0)*millimeter,"radius":3*millimeter});
    r8Boolean(context,id+"nutClearance",{"tools":qCreatedBy(id+"nutThreadEnvelope",EntityType.BODY),"targets":nut,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":nut,"propertyType":PropertyType.NAME,"value":"BOUGHT M6 prop nut - AF10 reference"});
    setProperty(context,{"entities":nut,"propertyType":PropertyType.APPEARANCE,"value":color(0.45,0.47,0.5)});
}

function r10DuctExtension(context is Context,id is Id,nozzle is Query)
{
    var covers=[];
    for(var b in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var r10Bounds=evBox3d(context,{"topology":b,"tight":true});
        if(r10Bounds.maxCorner[0]-r10Bounds.minCorner[0]>80*millimeter && r10Bounds.minCorner[1]>18*millimeter) covers=append(covers,b);
    }
    if(size(covers)!=1) throw regenError("R10 expects the unchanged cap before translation.");
    opTransform(context,id+"moveUnchangedCap",{"bodies":qUnion(covers),"transform":transform(vector(0,28,0)*millimeter)});
    var extension=annularTool(context,id+"duct",38.8*millimeter,43*millimeter,19*millimeter,42*millimeter);
    var ears=[];
    var ds=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1),vector(1,0,0)];
    for(var i=0;i<4;i+=1)
    {
        var c=ds[i]*44.5*millimeter;
        fCylinder(context,id+("ear"~i),{"bottomCenter":c+vector(0,19,0)*millimeter,"topCenter":c+vector(0,47,0)*millimeter,"radius":5*millimeter});
        ears=append(ears,qCreatedBy(id+("ear"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"joinEars",{"tools":qUnion([extension,qUnion(ears)]),"operationType":BooleanOperationType.UNION});
    var endRims=[];
    for(var e in evaluateQuery(context,qOwnedByBody(extension,EntityType.EDGE)))
    {
        var eb=evBox3d(context,{"topology":e,"tight":true});
        if(abs(eb.maxCorner[1]-eb.minCorner[1])<1e-5*millimeter &&
            (abs(eb.minCorner[1]-19*millimeter)<1e-5*millimeter || abs(eb.minCorner[1]-47*millimeter)<1e-5*millimeter)) endRims=append(endRims,e);
    }
    if(size(endRims)<4) throw regenError("R10 expects both extension end perimeters.");
    checkedFillet(context,id+"extensionRounds",{"entities":qUnion(endRims),"radius":0.4*millimeter,"tangentPropagation":false});
    // Match existing front protrusions, with positive print-fit side relief.
    // Enlarge the copied front mating pocket on a 0.4 mm grid spanning
    // +/-0.4 mm in X/Z. The Y19 plane and planar bearing seats stay intact.
    // Discrete-copy relief avoids offsetting fragile imported fillet faces.
    // The original frame and the four planar bearing seats stay untouched.
    opPattern(context,id+"frameCopy",{"entities":nozzle,"transforms":[identityTransform()],"instanceNames":["clearance"],"copyPropertiesAndAttributes":false});
    fCylinder(context,id+"frontMask",{"bottomCenter":vector(0,19,0)*millimeter,"topCenter":vector(0,26,0)*millimeter,"radius":60*millimeter});
    r8Boolean(context,id+"frontClip",{"tools":qUnion([qCreatedBy(id+"frameCopy",EntityType.BODY),qCreatedBy(id+"frontMask",EntityType.BODY)]),"operationType":BooleanOperationType.INTERSECTION});
    var frontCopy=qCreatedBy(id+"frontClip",EntityType.BODY);
    var offsets=[];var copyNames=[];
    for(var ix=-1;ix<=1;ix+=1)
        for(var iz=-1;iz<=1;iz+=1)
        {
            offsets=append(offsets,transform(vector(ix*0.4,0,iz*0.4)*millimeter));
            copyNames=append(copyNames,"clear"~(ix+1)~"_"~(iz+1));
        }
    opPattern(context,id+"relievedCopies",{"entities":frontCopy,"transforms":offsets,"instanceNames":copyNames,"copyPropertiesAndAttributes":false});
    opDeleteBodies(context,id+"removeClipSource",{"entities":frontCopy});
    r8Boolean(context,id+"frameSeat",{"tools":qCreatedBy(id+"relievedCopies",EntityType.BODY),"targets":extension,"operationType":BooleanOperationType.SUBTRACTION});
    // The inherited front lip has thin features at approximately R39,Y19..23.
    // Give the new rear mouth an explicit R40 counterbore and a gentle lead-in
    // to the R38.8 duct bore; preserve all four full R5 bolt-bearing columns.
    fCylinder(context,id+"rearLipRelief",{"bottomCenter":vector(0,18.99,0)*millimeter,"topCenter":vector(0,23.5,0)*millimeter,"radius":40*millimeter});
    var rearRelief=qCreatedBy(id+"rearLipRelief",EntityType.BODY);
    fCone(context,id+"rearLipTaper",{"bottomCenter":vector(0,23.5,0)*millimeter,"topCenter":vector(0,26.5,0)*millimeter,"bottomRadius":40*millimeter,"topRadius":38.8*millimeter});
    r8Boolean(context,id+"lipToolJoin",{"tools":qUnion([rearRelief,qCreatedBy(id+"rearLipTaper",EntityType.BODY)]),"operationType":BooleanOperationType.UNION});
    var bearingKeeps=[];
    for(var i=0;i<4;i+=1)
    {
        var c=ds[i]*44.5*millimeter;
        fCylinder(context,id+("bearingKeep"~i),{"bottomCenter":c+vector(0,18.98,0)*millimeter,"topCenter":c+vector(0,26.51,0)*millimeter,"radius":5*millimeter});
        bearingKeeps=append(bearingKeeps,qCreatedBy(id+("bearingKeep"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"protectBearings",{"tools":qUnion(bearingKeeps),"targets":rearRelief,"operationType":BooleanOperationType.SUBTRACTION});
    r8Boolean(context,id+"rearMouthClearance",{"tools":rearRelief,"targets":extension,"operationType":BooleanOperationType.SUBTRACTION});
    var mouthRims=[];
    for(var e in evaluateQuery(context,qGeometry(qCreatedBy(id+"rearMouthClearance",EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var eb=evBox3d(context,{"topology":e,"tight":true});
        var mid=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
        var rr=sqrt(mid[0]*mid[0]+mid[2]*mid[2]);
        if(abs(eb.maxCorner[1]-eb.minCorner[1])<1e-5*millimeter &&
            (abs(rr-40*millimeter)<1e-4*millimeter || abs(rr-38.8*millimeter)<1e-4*millimeter) && evLength(context,{"entities":e})>1*millimeter) mouthRims=append(mouthRims,e);
    }
    if(size(mouthRims)==0) throw regenError("R10 expects the new duct lead-in rims.");
    checkedFillet(context,id+"leadInRounds",{"entities":qUnion(mouthRims),"radius":0.2*millimeter,"tangentPropagation":false});
    var holes=[];
    for(var i=0;i<4;i+=1)
    {
        var c=ds[i]*44.5*millimeter;
        fCylinder(context,id+("boltBore"~i),{"bottomCenter":c+vector(0,18.9,0)*millimeter,"topCenter":c+vector(0,47.1,0)*millimeter,"radius":1.7*millimeter});
        holes=append(holes,qCreatedBy(id+("boltBore"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"throughBoltBores",{"tools":qUnion(holes),"targets":extension,"operationType":BooleanOperationType.SUBTRACTION});
    if(size(evaluateQuery(context,extension))!=1) throw regenError("R10 duct extension must remain one body.");
    setProperty(context,{"entities":extension,"propertyType":PropertyType.NAME,"value":"R10 duct extension - 28 mm, four M3x40 through-bolts"});
    setProperty(context,{"entities":extension,"propertyType":PropertyType.APPEARANCE,"value":color(0.35,0.55,0.68)});
}
