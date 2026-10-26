// Revision driven by the user's first physical print, 17 October 2026.
// Keep body identities, the gray cover, all motor seats and fastener centers.
function annularTool(context is Context,id is Id,r1 is ValueWithUnits,r2 is ValueWithUnits,y1 is ValueWithUnits,y2 is ValueWithUnits)
{
    fCylinder(context,id+"outer",{"bottomCenter":vector(0*millimeter,y1,0*millimeter),"topCenter":vector(0*millimeter,y2,0*millimeter),"radius":r2});
    var tool=qCreatedBy(id+"outer",EntityType.BODY);
    fCylinder(context,id+"inner",{"bottomCenter":vector(0*millimeter,y1-0.1*millimeter,0*millimeter),"topCenter":vector(0*millimeter,y2+0.1*millimeter,0*millimeter),"radius":r1});
    opBoolean(context,id+"hollow",{"tools":qCreatedBy(id+"inner",EntityType.BODY),"targets":tool,"operationType":BooleanOperationType.SUBTRACTION});
    return tool;
}

function applyPhysicalPrintRevision(context is Context,id is Id,nozzle is Query)
{
    var props=[];
    var inserts=[];
    for(var body in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var b=evBox3d(context,{"topology":body,"tight":true});
        var span=b.maxCorner-b.minCorner;
        if(span[2]>70*millimeter && span[0]<40*millimeter && b.minCorner[1]>-4*millimeter && b.maxCorner[1]<20*millimeter)
            props=append(props,body);
        if(span[0]>22*millimeter && span[0]<24*millimeter && b.minCorner[1]>5.5*millimeter && b.maxCorner[1]<10.1*millimeter)
            inserts=append(inserts,body);
    }
    if(size(props)!=1 || size(inserts)!=1) throw regenError("Expected the original propeller and four-hole motor insert.");
    var prop=qUnion(props);
    var insert=qUnion(inserts);

    // Trim only blade material beyond R35.5; do not scale the hub or drive keys.
    var tipTool=annularTool(context,id+"tipTool",35.5*millimeter,55*millimeter,-4*millimeter,20*millimeter);
    opBoolean(context,id+"bladeTipCut",{"tools":tipTool,"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
    var tipEdges=qCreatedBy(id+"bladeTipCut",EntityType.EDGE);
    if(size(evaluateQuery(context,tipEdges))==0) throw regenError("No blade tips were trimmed.");
    checkedFillet(context,id+"tipRounds",{"entities":tipEdges,"radius":0.15*millimeter,"tangentPropagation":false,"allowEdgeOverflow":true});

    // 0.3 mm radial relief of the outer lobes. Every M3 pilot is untouched.
    var insertTool=annularTool(context,id+"insertTool",11.3*millimeter,16*millimeter,5.4*millimeter,10.2*millimeter);
    opBoolean(context,id+"spacerOutsideCut",{"tools":insertTool,"targets":insert,"operationType":BooleanOperationType.SUBTRACTION});
    var leadIns=[];
    for(var e in evaluateQuery(context,qOwnedByBody(insert,EntityType.EDGE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        var mid=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
        if(abs(b.maxCorner[1]-b.minCorner[1])<1e-5*millimeter &&
            abs(sqrt(mid[0]*mid[0]+mid[2]*mid[2])-11.3*millimeter)<0.005*millimeter) leadIns=append(leadIns,e);
    }
    if(size(leadIns)==0) throw regenError("No outer spacer lead-in edges found.");
    checkedFillet(context,id+"spacerLeadIns",{"entities":qUnion(leadIns),"radius":0.2*millimeter,"tangentPropagation":false});

    // A continuous rear cable window, R15.5..28, behind all four motor seats.
    // Retain the central support and original forward radial ribs.
    var rearRelief=annularTool(context,id+"rearRelief",15.5*millimeter,35*millimeter,-46*millimeter,-22*millimeter);
    opBoolean(context,id+"rearCableClear",{"tools":rearRelief,"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
    var ring=annularTool(context,id+"wireRing",28*millimeter,33*millimeter,-29*millimeter,-23*millimeter);
    checkedFillet(context,id+"ringLipRounds",{"entities":qGeometry(qOwnedByBody(ring,EntityType.EDGE),GeometryType.CIRCLE),"radius":0.8*millimeter});
    var supports=[];
    for(var i=0;i<4;i+=1)
    {
        var d=vector(cos(i*90*degree),0,sin(i*90*degree));
        fCylinder(context,id+("ringPost"~i),{"bottomCenter":d*30.5*millimeter+vector(0,-26,0)*millimeter,
            "topCenter":d*30.5*millimeter+vector(0,-14,0)*millimeter,"radius":2.5*millimeter});
        supports=append(supports,qCreatedBy(id+("ringPost"~i),EntityType.BODY));
    }
    opBoolean(context,id+"ringSupportJoin",{"tools":qUnion([nozzle,ring,qUnion(supports)]),"operationType":BooleanOperationType.UNION});
    if(size(evaluateQuery(context,nozzle))!=1) throw regenError("The wire ring must remain one connected nozzle body.");
    setProperty(context,{"entities":nozzle,"propertyType":PropertyType.NAME,"value":"Nozzle - 360 degree rear wire ring, PLA revision"});
    setProperty(context,{"entities":prop,"propertyType":PropertyType.NAME,"value":"Propeller - 71 mm sweep, original motor interface"});
    setProperty(context,{"entities":insert,"propertyType":PropertyType.NAME,"value":"Motor insert - 22.6 mm slip-fit envelope, M3 pilots"});
}
