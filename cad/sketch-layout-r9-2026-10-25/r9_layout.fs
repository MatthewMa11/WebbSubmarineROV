// R9: user's side sketch -- fixed cap, forward fan, motor, rear support.
// Pattern copy uses native opPattern; source remains the assembly's fan body.
function r9ForwardFan(context is Context,id is Id,prop is Query)
{
    opPattern(context,id+"bladeCopy",{"entities":prop,"transforms":[identityTransform()],"instanceNames":["outerBlades"],"copyPropertiesAndAttributes":false});
    var blades=qCreatedBy(id+"bladeCopy",EntityType.BODY);
    setAttribute(context,{"entities":blades,"name":"r9Stage","attribute":{"role":"blades"}});
    blades=qHasAttributeWithValueMatching(qAllModifiableSolidBodies(),"r9Stage",{"role":"blades"});
    // Keep the complete outer profiles; every following root cut is bounded
    // inside R26.9 so the blade surfaces beyond R27.01 remain untouched.
    if(size(evaluateQuery(context,blades))!=1) throw regenError("R9 blade copy must be one body before removing its old root.");
    fCylinder(context,id+"oldRootTool",{"bottomCenter":vector(0,-4,0)*millimeter,"topCenter":vector(0,19.4,0)*millimeter,"radius":19*millimeter});
    r8Boolean(context,id+"bladeRootCut",{"tools":qCreatedBy(id+"oldRootTool",EntityType.BODY),"targets":blades,"operationType":BooleanOperationType.SUBTRACTION});
    if(size(evaluateQuery(context,blades))!=2) throw regenError("R9 expects exactly two outer blade bodies.");
    // Taper only the inner root's forward edge, retaining the complete outer
    // blade surfaces beyond R27.01. The cap's center remains clear.
    fCone(context,id+"rootFrontTool",{"bottomCenter":vector(0,10,0)*millimeter,"topCenter":vector(0,11.41,0)*millimeter,"bottomRadius":19*millimeter,"topRadius":27.1*millimeter});
    fCylinder(context,id+"rootFrontMask",{"bottomCenter":vector(0,9.99,0)*millimeter,"topCenter":vector(0,11.42,0)*millimeter,"radius":26.9*millimeter});
    r8Boolean(context,id+"rootFrontLimit",{"tools":qUnion([qCreatedBy(id+"rootFrontTool",EntityType.BODY),qCreatedBy(id+"rootFrontMask",EntityType.BODY)]),"operationType":BooleanOperationType.INTERSECTION});
    fCylinder(context,id+"rootFrontBeyond",{"bottomCenter":vector(0,11.4,0)*millimeter,"topCenter":vector(0,19.4,0)*millimeter,"radius":26.9*millimeter});
    fCylinder(context,id+"rootRearTool",{"bottomCenter":vector(0,-4,0)*millimeter,"topCenter":vector(0,5.3,0)*millimeter,"radius":26.9*millimeter});
    r8Boolean(context,id+"taperRootFront",{"tools":qUnion([qCreatedBy(id+"rootFrontLimit",EntityType.BODY),qCreatedBy(id+"rootFrontBeyond",EntityType.BODY),qCreatedBy(id+"rootRearTool",EntityType.BODY)]),"targets":blades,"operationType":BooleanOperationType.SUBTRACTION});
    if(size(evaluateQuery(context,blades))!=2) throw regenError("R9 tapered roots must retain two blade bodies.");
    opTransform(context,id+"forwardBlades",{"bodies":blades,"transform":transform(vector(0,8,0)*millimeter)});

    // Remove the motor-bell cup and old blades; retain all four solid keys.
    fCylinder(context,id+"rearTrimTool",{"bottomCenter":vector(0,-4,0)*millimeter,"topCenter":vector(0,14.2,0)*millimeter,"radius":36*millimeter});
    var trim=qCreatedBy(id+"rearTrimTool",EntityType.BODY);var keeps=[];
    var axes=[vector(9,0,0),vector(-9,0,0),vector(0,0,9),vector(0,0,-9)];
    for(var i=0;i<4;i+=1)
    {
        fCylinder(context,id+("keyKeep"~i),{"bottomCenter":(axes[i]+vector(0,11.49,0))*millimeter,"topCenter":(axes[i]+vector(0,14.3,0))*millimeter,"radius":2.75*millimeter});
        keeps=append(keeps,qCreatedBy(id+("keyKeep"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"preserveDriveKeys",{"tools":qUnion(keeps),"targets":trim,"operationType":BooleanOperationType.SUBTRACTION});
    r8Boolean(context,id+"removeRearCup",{"tools":trim,"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
    if(size(evaluateQuery(context,prop))!=1) throw regenError("R9 flat disk and original drive keys must remain one body.");
    // The old cup is only R18. A flat R20 disk overlaps the R19 blade roots.
    // A 1.4 mm rear rim supplies room for the new root blend. R8's following
    // bell-envelope relief removes its center behind Y14.2, clearing the motor.
    fCylinder(context,id+"flatDisk",{"bottomCenter":vector(0,12.8,0)*millimeter,"topCenter":vector(0,19.3,0)*millimeter,"radius":20*millimeter});
    var disk=qCreatedBy(id+"flatDisk",EntityType.BODY);
    r8Boolean(context,id+"flatDiskJoin",{"tools":qUnion([prop,disk]),"operationType":BooleanOperationType.UNION});
    r8Boolean(context,id+"bladeJoin",{"tools":qUnion([prop,blades]),"operationType":BooleanOperationType.UNION});
    if(size(evaluateQuery(context,qUnion([prop,blades])))!=1) throw regenError("R9 forward blades must join the flat hub.");
    var rootEdges=[];var positiveRoot=false;var negativeRoot=false;
    for(var edge in evaluateQuery(context,qCreatedBy(id+"bladeJoin",EntityType.EDGE)))
    {
        var mid=evEdgeTangentLine(context,{"edge":edge,"parameter":0.5}).origin;
        var radius=sqrt(mid[0]*mid[0]+mid[2]*mid[2]);
        if(abs(radius-20*millimeter)<1e-4*millimeter && mid[1]>13.1*millimeter && mid[1]<19.1*millimeter)
        {
            rootEdges=append(rootEdges,edge);
            if(mid[2]>0*millimeter) positiveRoot=true;
            if(mid[2]<0*millimeter) negativeRoot=true;
        }
    }
    if(!positiveRoot || !negativeRoot) throw regenError("R9 needs intersection edges at both R20 blade roots.");
    var roots=qUnion(rootEdges);
    try { checkedFillet(context,id+"newRootRounds",{"entities":roots,"radius":0.35*millimeter,"tangentPropagation":false}); }
    catch(error)
    {
        var lengths=[];
        for(var edge in evaluateQuery(context,roots)) lengths=append(lengths,evLength(context,{"entities":edge})/millimeter);
        throw regenError("R9 root blend failed; seam lengths mm="~lengths);
    }
    var rims=[];var frontRim=false;var backRim=false;
    for(var edge in evaluateQuery(context,qGeometry(qOwnedByBody(prop,EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var b=evBox3d(context,{"topology":edge,"tight":true});
        var mid=evEdgeTangentLine(context,{"edge":edge,"parameter":0.5}).origin;
        var radius=sqrt(mid[0]*mid[0]+mid[2]*mid[2]);
        if(abs(radius-20*millimeter)<1e-4*millimeter && abs(b.maxCorner[1]-b.minCorner[1])<1e-5*millimeter)
        {
            if(abs(b.minCorner[1]-12.8*millimeter)<1e-5*millimeter) { backRim=true;rims=append(rims,edge); }
            if(abs(b.minCorner[1]-19.3*millimeter)<1e-5*millimeter) { frontRim=true;rims=append(rims,edge); }
        }
    }
    if(!frontRim || !backRim) throw regenError("R9 expects both circular flat-disk perimeter rims.");
    checkedFillet(context,id+"diskRimRounds",{"entities":qUnion(rims),"radius":0.07*millimeter,"tangentPropagation":false});
}
