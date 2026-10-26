annotation {"Feature Type Name":"Flat rear motor boss fixture"}
export const flatBossFixture=defineFeature(function(context is Context,id is Id,definition is map)
    precondition {}
    {
        fCylinder(context,id+"base",{"bottomCenter":vector(0,-42,0)*millimeter,"topCenter":vector(0,-11,0)*millimeter,"radius":15.5*millimeter});
        var body=qCreatedBy(id+"base",EntityType.BODY);
        var tools=[];
        var axes=[vector(9.5,0,0),vector(-9.5,0,0),vector(0,0,8),vector(0,0,-8)];
        for(var i=0;i<4;i+=1)
        {
            fCylinder(context,id+("access"~i),{"bottomCenter":(axes[i]+vector(0,-45,0))*millimeter,"topCenter":(axes[i]+vector(0,-16,0))*millimeter,"radius":3.8*millimeter});
            fCylinder(context,id+("shaft"~i),{"bottomCenter":(axes[i]+vector(0,-16.1,0))*millimeter,"topCenter":(axes[i]+vector(0,-10,0))*millimeter,"radius":1.65*millimeter});
            tools=append(tools,qCreatedBy(id+("access"~i),EntityType.BODY));
            tools=append(tools,qCreatedBy(id+("shaft"~i),EntityType.BODY));
        }
        fCylinder(context,id+"centralPocket",{"bottomCenter":vector(0,-21,0)*millimeter,"topCenter":vector(0,-10,0)*millimeter,"radius":4.8*millimeter});
        tools=append(tools,qCreatedBy(id+"centralPocket",EntityType.BODY));
        opBoolean(context,id+"boreFixture",{"tools":qUnion(tools),"targets":body,"operationType":BooleanOperationType.SUBTRACTION});
        applyFlatRearMotorBoss(context,id+"flat",body);
        var bounds=evBox3d(context,{"topology":body,"tight":true});
        if(abs(bounds.minCorner[1]+30*millimeter)>1e-5*millimeter) throw regenError("Rear face was not flattened at Y=-30 mm.");
        if(size(evaluateQuery(context,qAllModifiableSolidBodies()))!=1) throw regenError("Fixture must remain one body.");
        var floor=qCoincidesWithPlane(qOwnedByBody(body,EntityType.FACE),plane(vector(0,-30,0)*millimeter,vector(0,1,0)));
        if(size(evaluateQuery(context,floor))!=1) throw regenError("Expected one flat rear face with four open access holes.");
    },{});
