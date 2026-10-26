// R14: remove unused old cap lugs; fair outer duct and round current post roots.
function r14Fairing(context is Context,id is Id,outside is boolean)
{
    var a=46.2977716548645;
    var sk=newSketchOnPlane(context,id+"profile",{"sketchPlane":plane(vector(0,0,0)*millimeter,vector(0,0,1),vector(1,0,0))});
    skBezier(sk,"fair",{"points":[vector(a,12)*millimeter,vector(a,15.6)*millimeter,vector(a,19.2)*millimeter,vector(43,22.8)*millimeter,vector(43,26.4)*millimeter,vector(43,30)*millimeter]});
    skLineSegment(sk,"cylinder",{"start":vector(43,30)*millimeter,"end":vector(43,35.5)*millimeter});
    var closeRadius=outside ? 60 : 38.8;
    skLineSegment(sk,"top",{"start":vector(43,35.5)*millimeter,"end":vector(closeRadius,35.5)*millimeter});
    skLineSegment(sk,"back",{"start":vector(closeRadius,35.5)*millimeter,"end":vector(closeRadius,12)*millimeter});
    skLineSegment(sk,"bottom",{"start":vector(closeRadius,12)*millimeter,"end":vector(a,12)*millimeter});
    skSolve(sk);
    opRevolve(context,id+"solid",{"entities":qSketchRegion(id+"profile"),"axis":line(vector(0,0,0)*millimeter,vector(0,1,0)),"angleForward":360*degree});
    opDeleteBodies(context,id+"removeSketch",{"entities":qCreatedBy(id+"profile",EntityType.BODY)});
    return qCreatedBy(id+"solid",EntityType.BODY);
}

function r14SmoothFrame(context is Context,id is Id,nozzle is Query)
{
    var skin=r14Fairing(context,id+"skin",false);
    r8Boolean(context,id+"fillObsoleteRecesses",{"tools":qUnion([nozzle,skin]),"operationType":BooleanOperationType.UNION});
    var ds=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1),vector(1,0,0)];
    var roots=[];
    for(var i=0;i<4;i+=1)
    {
        opSphere(context,id+("root"~i),{"center":ds[i]*44.5*millimeter+vector(0,35.5,0)*millimeter,"radius":5*millimeter});
        roots=append(roots,qCreatedBy(id+("root"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"roundedRoots",{"tools":qUnion([nozzle,qUnion(roots)]),"operationType":BooleanOperationType.UNION});
    var trim=r14Fairing(context,id+"trim",true);
    var keeps=[];
    for(var i=0;i<4;i+=1)
    {
        opSphere(context,id+("rootKeep"~i),{"center":ds[i]*44.5*millimeter+vector(0,35.5,0)*millimeter,"radius":5*millimeter});
        keeps=append(keeps,qCreatedBy(id+("rootKeep"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"protectRoots",{"tools":qUnion(keeps),"targets":trim,"operationType":BooleanOperationType.SUBTRACTION});
    r8Boolean(context,id+"removeOldLugs",{"tools":trim,"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
    var blends=[];
    for(var e in evaluateQuery(context,qEdgeConvexityTypeFilter(qOwnedByBody(nozzle,EntityType.EDGE),EdgeConvexityType.CONCAVE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(b.minCorner[1]>30*millimeter && b.maxCorner[1]<36*millimeter && evLength(context,{"entities":e})>1*millimeter) blends=append(blends,e);
    }
    if(size(blends)<4) throw regenError("R14 expects four rounded root junctions.");
    checkedFillet(context,id+"rootBlends",{"entities":qUnion(blends),"radius":0.6*millimeter,"tangentPropagation":false});
    var bores=[];
    for(var i=0;i<4;i+=1)
    {
        var c=ds[i]*44.5*millimeter;
        fCylinder(context,id+("bore"~i),{"bottomCenter":c+vector(0,39.9,0)*millimeter,"topCenter":c+vector(0,47.9,0)*millimeter,"radius":1.8*millimeter});
        bores=append(bores,qCreatedBy(id+("bore"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"restoreJointBores",{"tools":qUnion(bores),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":nozzle,"propertyType":PropertyType.NAME,"value":"R14 smooth one-piece frame - obsolete lugs removed"});
    if(size(evaluateQuery(context,nozzle))!=1 || size(evaluateQuery(context,qAllModifiableSolidBodies()))!=47) throw regenError("R14 expects one connected frame and47 solids.");
}

