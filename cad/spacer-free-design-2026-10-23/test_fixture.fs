annotation {"Feature Type Name":"R6 external bell clamp geometry test"}
export const testR6 = defineFeature(function(context is Context,id is Id,definition is map)
    precondition {}
    {
        var prop=annularTool(context,id+"cage",15.1*millimeter,18*millimeter,-3*millimeter,19*millimeter);
        var plate=annularTool(context,id+"plate",4.8*millimeter,18*millimeter,14.2*millimeter,19*millimeter);
        var keys=[];var holes=[];
        var centers=[vector(9,0,0),vector(-9,0,0),vector(0,0,9),vector(0,0,-9)];
        for(var i=0;i<4;i+=1)
        {
            fCylinder(context,id+("key"~i),{"bottomCenter":(centers[i]+vector(0,11.5,0))*millimeter,"topCenter":(centers[i]+vector(0,14.3,0))*millimeter,"radius":2.85*millimeter});
            keys=append(keys,qCreatedBy(id+("key"~i),EntityType.BODY));
            fCylinder(context,id+("pilot"~i),{"bottomCenter":(centers[i]+vector(0,11.4,0))*millimeter,"topCenter":(centers[i]+vector(0,19.1,0))*millimeter,"radius":1.65*millimeter});
            fCylinder(context,id+("head"~i),{"bottomCenter":(centers[i]+vector(0,15,0))*millimeter,"topCenter":(centers[i]+vector(0,19.1,0))*millimeter,"radius":3*millimeter});
            holes=append(holes,qCreatedBy(id+("pilot"~i),EntityType.BODY));
            holes=append(holes,qCreatedBy(id+("head"~i),EntityType.BODY));
        }
        opBoolean(context,id+"joinProp",{"tools":qUnion([prop,plate,qUnion(keys)]),"operationType":BooleanOperationType.UNION});
        opBoolean(context,id+"cutProp",{"tools":qUnion(holes),"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
        r6BuildBellClamp(context,id+"r6",prop);
        if(size(evaluateQuery(context,qAllModifiableSolidBodies()))!=7) throw regenError("Expected one propeller and six clamp hardware bodies.");
        var rotor=annularTool(context,id+"rotor",11.85*millimeter,13.85*millimeter,-5*millimeter,10*millimeter);
        var bell=annularTool(context,id+"bell",4.5*millimeter,13.85*millimeter,10*millimeter,14*millimeter);
        opBoolean(context,id+"joinRotor",{"tools":qUnion([rotor,bell]),"operationType":BooleanOperationType.UNION});
        var vents=[];
        for(var i=0;i<4;i+=1)
        {
            fCylinder(context,id+("vent"~i),{"bottomCenter":(centers[i]+vector(0,9.9,0))*millimeter,"topCenter":(centers[i]+vector(0,14.1,0))*millimeter,"radius":3*millimeter});
            vents=append(vents,qCreatedBy(id+("vent"~i),EntityType.BODY));
        }
        opBoolean(context,id+"cutVents",{"tools":qUnion(vents),"targets":rotor,"operationType":BooleanOperationType.SUBTRACTION});
        var cap=annularTool(context,id+"cap",1.75*millimeter,20*millimeter,20*millimeter,40*millimeter);
        fCylinder(context,id+"stator",{"bottomCenter":vector(0,-11,0)*millimeter,"topCenter":vector(0,-6,0)*millimeter,"radius":13.85*millimeter});
        var stator=qCreatedBy(id+"stator",EntityType.BODY);
        var duct=annularTool(context,id+"duct",37.95*millimeter,43*millimeter,-30*millimeter,26.5*millimeter);
        for(var target in [rotor,cap,stator,duct])
            if(evDistance(context,{"side0":prop,"side1":target}).distance < 0.14*millimeter) throw regenError("Insufficient R6 fixture clearance.");
        println("R6 fixture passed: one connected propeller, six hardware bodies, no fixed-envelope interference.");
        println("Bell radial clearance (mm): "~(evDistance(context,{"side0":prop,"side1":rotor}).distance/millimeter));
        println("Cap axial clearance (mm): "~(evDistance(context,{"side0":prop,"side1":cap}).distance/millimeter));
    },{});
