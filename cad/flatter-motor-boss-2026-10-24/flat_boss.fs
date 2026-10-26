// R6.1: flatten only the redundant rear dome, keeping all motor seats in place.
function applyFlatRearMotorBoss(context is Context,id is Id,nozzle is Query)
{
    if(size(evaluateQuery(context,nozzle))!=1) throw regenError("Select the existing nozzle body.");
    fCylinder(context,id+"rearTrimTool",{"bottomCenter":vector(0,-60,0)*millimeter,"topCenter":vector(0,-30,0)*millimeter,"radius":21*millimeter});
    opBoolean(context,id+"flattenRear",{"tools":qCreatedBy(id+"rearTrimTool",EntityType.BODY),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
    var rims=[];
    var mouths=[];
    for(var edge in evaluateQuery(context,qGeometry(qCreatedBy(id+"flattenRear",EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var bounds=evBox3d(context,{"topology":edge,"tight":true});
        if(abs(bounds.minCorner[1]+30*millimeter)<1e-5*millimeter && abs(bounds.maxCorner[1]+30*millimeter)<1e-5*millimeter)
        {
            var diameter=bounds.maxCorner[0]-bounds.minCorner[0];
            if(abs(diameter-31*millimeter)<1e-5*millimeter) rims=append(rims,edge);
            if(abs(diameter-7.6*millimeter)<1e-5*millimeter) mouths=append(mouths,edge);
        }
    }
    if(size(rims)!=1 || size(mouths)!=4) throw regenError("Expected one rear boss perimeter and four original access holes.");
    checkedFillet(context,id+"flatOuterRound",{"entities":qUnion(rims),"radius":1*millimeter,"tangentPropagation":false});
    checkedFillet(context,id+"flatAccessRounds",{"entities":qUnion(mouths),"radius":0.3*millimeter,"tangentPropagation":false});
    if(size(evaluateQuery(context,nozzle))!=1) throw regenError("Flattened nozzle must remain one connected body.");
    setProperty(context,{"entities":nozzle,"propertyType":PropertyType.NAME,"value":"R6.1 nozzle - flatter rear motor boss, R6 drive retained"});
}
