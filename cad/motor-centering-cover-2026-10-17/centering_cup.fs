// Permanent stationary motor-base centering cover, 17 October 2026.
// The original M3 motor seats, rotating group and rear wire ring are retained.
function applyMotorCenteringCup(context is Context,id is Id,nozzle is Query)
{
    fCylinder(context,id+"cupOuter",{"bottomCenter":vector(0,-13,0)*millimeter,
        "topCenter":vector(0,-6.25,0)*millimeter,"radius":18.5*millimeter});
    var cup=qCreatedBy(id+"cupOuter",EntityType.BODY);
    fCylinder(context,id+"pilotBore",{"bottomCenter":vector(0,-13.1,0)*millimeter,
        "topCenter":vector(0,-6.1,0)*millimeter,"radius":14.25*millimeter});
    opBoolean(context,id+"pilotClear",{"tools":qCreatedBy(id+"pilotBore",EntityType.BODY),"targets":cup,"operationType":BooleanOperationType.SUBTRACTION});
    fCone(context,id+"leadInCone",{"bottomCenter":vector(0,-10,0)*millimeter,
        "topCenter":vector(0,-6.15,0)*millimeter,"bottomRadius":14.25*millimeter,
        "topRadius":16.816666666667*millimeter});
    opBoolean(context,id+"taperClear",{"tools":qCreatedBy(id+"leadInCone",EntityType.BODY),"targets":cup,"operationType":BooleanOperationType.SUBTRACTION});
    var lips=[];
    for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(cup,EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(abs(b.minCorner[1]+6.25*millimeter)<1e-5*millimeter && abs(b.maxCorner[1]+6.25*millimeter)<1e-5*millimeter)
            lips=append(lips,e);
    }
    if(size(lips)!=2) throw regenError("Expected two centering-cup entrance rims.");
    checkedFillet(context,id+"entranceRounds",{"entities":qUnion(lips),"radius":0.35*millimeter});

    // Rounded, open-top cable ports between the four original support ribs.
    // Cut the new cup before joining, preserving all original nozzle material.
    var ports=[];
    for(var i=0;i<4;i+=1)
    {
        var a=(45+90*i)*degree;
        var d=vector(cos(a),0,sin(a));
        fCylinder(context,id+("wirePort"~i),{"bottomCenter":d*12*millimeter+vector(0,-6.5,0)*millimeter,
            "topCenter":d*23*millimeter+vector(0,-6.5,0)*millimeter,"radius":6*millimeter});
        ports=append(ports,qCreatedBy(id+("wirePort"~i),EntityType.BODY));
    }
    opBoolean(context,id+"wirePortCuts",{"tools":qUnion(ports),"targets":cup,"operationType":BooleanOperationType.SUBTRACTION});
    var portEdges=qCreatedBy(id+"wirePortCuts",EntityType.EDGE);
    if(size(evaluateQuery(context,portEdges))==0) throw regenError("No new centering-cup wire openings found.");
    checkedFillet(context,id+"wirePortRounds",{"entities":portEdges,"radius":0.25*millimeter,"tangentPropagation":false,"allowEdgeOverflow":true});
    opBoolean(context,id+"cupJoin",{"tools":qUnion([nozzle,cup]),"operationType":BooleanOperationType.UNION});
    if(size(evaluateQuery(context,nozzle))!=1) throw regenError("Centering cup must join the original nozzle.");
    setProperty(context,{"entities":nozzle,"propertyType":PropertyType.NAME,"value":"Nozzle - permanent motor centering cup and rear wire ring"});
}
