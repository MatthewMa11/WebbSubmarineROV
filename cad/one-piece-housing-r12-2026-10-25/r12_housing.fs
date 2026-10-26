// R12: one stationary printed shell replaces the former frame + extension.
function r12OnePieceHousing(context is Context,id is Id,nozzle is Query)
{
    var extensions=[];
    for(var b in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var bb=evBox3d(context,{"topology":b,"tight":true});
        if(bb.maxCorner[0]-bb.minCorner[0]>90*millimeter && abs(bb.minCorner[1]-19*millimeter)<1e-4*millimeter && abs(bb.maxCorner[1]-47*millimeter)<1e-4*millimeter)
            extensions=append(extensions,b);
    }
    if(size(extensions)!=1) throw regenError("R12 expects one28mm duct extension.");
    var web=annularTool(context,id+"seamWeb",38.8*millimeter,43*millimeter,18*millimeter,28*millimeter);
    var ds=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1),vector(1,0,0)];
    var keepClear=[];
    for(var i=0;i<4;i+=1)
    {
        var c=ds[i]*44.5*millimeter;
        fCylinder(context,id+("hardwareAccess"~i),{"bottomCenter":c+vector(0,17.9,0)*millimeter,"topCenter":c+vector(0,28.1,0)*millimeter,"radius":3.8*millimeter});
        keepClear=append(keepClear,qCreatedBy(id+("hardwareAccess"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"webHardwareRelief",{"tools":qUnion(keepClear),"targets":web,"operationType":BooleanOperationType.SUBTRACTION});
    var all=qUnion([nozzle,qUnion(extensions),web]);
    r8Boolean(context,id+"uniteHousing",{"tools":all,"operationType":BooleanOperationType.UNION});
    if(size(evaluateQuery(context,all))!=1) throw regenError("R12 housing must be one connected body.");
    setProperty(context,{"entities":all,"propertyType":PropertyType.NAME,"value":"R12 one-piece frame and duct - continuous shell"});
    setProperty(context,{"entities":all,"propertyType":PropertyType.APPEARANCE,"value":color(0.33,0.35,0.37)});
    if(size(evaluateQuery(context,qAllModifiableSolidBodies()))!=47) throw regenError("R12 expects47 solids after merging the outer shell.");
}
