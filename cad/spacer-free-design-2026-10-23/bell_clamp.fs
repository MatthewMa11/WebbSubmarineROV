// R6: external motor-bell retention. No printed insert inside the rotor.
// Four original drive keys carry torque; opposed clamp screws retain axially.
function r6BuildBellClamp(context is Context,id is Id,prop is Query)
{
    // Close the four obsolete screw/pilot passages, leaving solid drive keys.
    var fills=[];
    var axes=[vector(9,0,0),vector(-9,0,0),vector(0,0,9),vector(0,0,-9)];
    for(var i=0;i<4;i+=1)
    {
        fCylinder(context,id+("pilotFill"~i),{"bottomCenter":(axes[i]+vector(0,11.5,0))*millimeter,"topCenter":(axes[i]+vector(0,19,0))*millimeter,"radius":1.8*millimeter});
        fills=append(fills,qCreatedBy(id+("pilotFill"~i),EntityType.BODY));
        fCylinder(context,id+("headFill"~i),{"bottomCenter":(axes[i]+vector(0,14.9,0))*millimeter,"topCenter":(axes[i]+vector(0,19,0))*millimeter,"radius":3.2*millimeter});
        fills=append(fills,qCreatedBy(id+("headFill"~i),EntityType.BODY));
    }
    // Relieve the old root fillets and leave 5.5 mm solid drive keys.
    // The mating reference vents are 6 mm; front-face clearance is 0.2 mm.
    fCylinder(context,id+"rootRelief",{"bottomCenter":vector(0,11.49,0)*millimeter,"topCenter":vector(0,14.2,0)*millimeter,"radius":13.9*millimeter});
    var relief=qCreatedBy(id+"rootRelief",EntityType.BODY);
    var keeps=[];
    for(var i=0;i<4;i+=1)
    {
        fCylinder(context,id+("keyKeep"~i),{"bottomCenter":(axes[i]+vector(0,11.4,0))*millimeter,"topCenter":(axes[i]+vector(0,14.3,0))*millimeter,"radius":2.75*millimeter});
        keeps=append(keeps,qCreatedBy(id+("keyKeep"~i),EntityType.BODY));
    }
    opBoolean(context,id+"reliefVents",{"tools":qUnion(keeps),"targets":relief,"operationType":BooleanOperationType.SUBTRACTION});
    opBoolean(context,id+"relieveKeyRoots",{"tools":relief,"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
    var band=annularTool(context,id+"band",14*millimeter,18*millimeter,-2*millimeter,8.5*millimeter);
    checkedFillet(context,id+"bandLipRounds",{"entities":qGeometry(qOwnedByBody(band,EntityType.EDGE),GeometryType.CIRCLE),"radius":0.3*millimeter});
    opBoolean(context,id+"collarJoin",{"tools":qUnion([prop,band,qUnion(fills)]),"operationType":BooleanOperationType.UNION});

    for(var i=0;i<2;i+=1)
    {
        var sid=id+("clamp"~i);
        var turn=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),i*180*degree);
        var ears=[];
        for(var k=0;k<2;k+=1)
        {
            var za=(k==0 ? 1 : -8.7)*millimeter;
            var zb=(k==0 ? 6 : -1)*millimeter;
            fCylinder(context,sid+("earBody"~k),{"bottomCenter":vector(20.5*millimeter,3*millimeter,za),"topCenter":vector(20.5*millimeter,3*millimeter,zb),"radius":4.7*millimeter});
            var ear=qCreatedBy(sid+("earBody"~k),EntityType.BODY);
            checkedFillet(context,sid+("earRounds"~k),{"entities":qGeometry(qOwnedByBody(ear,EntityType.EDGE),GeometryType.CIRCLE),"radius":0.6*millimeter});
            opTransform(context,sid+("earTurn"~k),{"bodies":ear,"transform":turn});
            ears=append(ears,ear);
        }
        opBoolean(context,sid+"earJoin",{"tools":qUnion([prop,qUnion(ears)]),"operationType":BooleanOperationType.UNION});
        // A round-ended slit flexes the outer collar while the front hub stays joined.
        fCuboid(context,sid+"slitBox",{"corner1":vector(13.7,-3.1,-1)*millimeter,"corner2":vector(27,9.5,1)*millimeter});
        fCylinder(context,sid+"slitRound",{"bottomCenter":vector(13.7,9.5,0)*millimeter,"topCenter":vector(27,9.5,0)*millimeter,"radius":1*millimeter});
        var slit=qUnion([qCreatedBy(sid+"slitBox",EntityType.BODY),qCreatedBy(sid+"slitRound",EntityType.BODY)]);
        opTransform(context,sid+"slitTurn",{"bodies":slit,"transform":turn});
        opBoolean(context,sid+"slitCut",{"tools":slit,"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
        // Opposing broad stop pads limit each ear's closing travel to 0.6 mm.
        var stops=[];
        for(var k=0;k<2;k+=1)
        {
            var za=(k==0 ? 0.3 : -1.4)*millimeter;
            var zb=(k==0 ? 1.4 : -0.3)*millimeter;
            fCuboid(context,sid+("stopBody"~k),{"corner1":vector(22.3*millimeter,1*millimeter,za),"corner2":vector(24*millimeter,5*millimeter,zb)});
            var stop=qCreatedBy(sid+("stopBody"~k),EntityType.BODY);
            checkedFillet(context,sid+("stopRounds"~k),{"entities":qOwnedByBody(stop,EntityType.EDGE),"radius":0.15*millimeter});
            opTransform(context,sid+("stopTurn"~k),{"bodies":stop,"transform":turn});
            stops=append(stops,stop);
        }
        opBoolean(context,sid+"stopJoin",{"tools":qUnion([prop,qUnion(stops)]),"operationType":BooleanOperationType.UNION});
        fCylinder(context,sid+"boltBore",{"bottomCenter":vector(20.5,3,-10)*millimeter,"topCenter":vector(20.5,3,11)*millimeter,"radius":1.7*millimeter});
        var bore=qCreatedBy(sid+"boltBore",EntityType.BODY);
        var pocket=hexPrism(context,sid+"nutPocket",vector(20.5,3,-8.8)*millimeter,vector(0,0,1),5.9*millimeter,2.8*millimeter);
        opTransform(context,sid+"toolsTurn",{"bodies":qUnion([bore,pocket]),"transform":turn});
        opBoolean(context,sid+"hardwareClear",{"tools":qUnion([bore,pocket]),"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});

        var seat=turn*(vector(20.5,3,6.5)*millimeter);
        var axis=turn.linear*vector(0,0,-1);
        kitCapScrew(context,sid+"screw",seat,axis,3*millimeter,16*millimeter,5.68*millimeter,2.5*millimeter,"R6 M3x16 external clamp bolt "~(i+1));
        finalM3Washer(context,sid+"washer",seat,axis,"R6 M3 external clamp washer "~(i+1));
        var nutStart=turn*(vector(20.5,3,-6)*millimeter);
        var nut=hexPrism(context,sid+"nut",nutStart,axis,5.5*millimeter,2.4*millimeter);
        fCylinder(context,sid+"nutBore",{"bottomCenter":nutStart-axis*0.01*millimeter,"topCenter":nutStart+axis*2.41*millimeter,"radius":1.5*millimeter});
        opBoolean(context,sid+"nutClear",{"tools":qCreatedBy(sid+"nutBore",EntityType.BODY),"targets":nut,"operationType":BooleanOperationType.SUBTRACTION});
        setProperty(context,{"entities":nut,"propertyType":PropertyType.NAME,"value":"R6 M3 captured clamp nut "~(i+1)});
        setProperty(context,{"entities":nut,"propertyType":PropertyType.APPEARANCE,"value":color(0.25,0.26,0.27)});
    }
    if(size(evaluateQuery(context,prop))!=1) throw regenError("R6 propeller and clamp must be one connected part.");
    setProperty(context,{"entities":prop,"propertyType":PropertyType.NAME,"value":"R6 propeller - integral M3 bell clamp, no motor insert"});
}

function applyR6SimpleDrive(context is Context,id is Id)
{
    var props=[];var inserts=[];var oldScrews=[];
    for(var body in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var bounds=evBox3d(context,{"topology":body,"tight":true});
        var dims=(bounds.maxCorner-bounds.minCorner)/millimeter;
        var mid=(bounds.maxCorner+bounds.minCorner)/(2*millimeter);
        if(dims[2]>70 && dims[0]<40 && bounds.minCorner[1]>-4*millimeter && bounds.maxCorner[1]<20*millimeter) props=append(props,body);
        if(dims[0]>22 && dims[0]<24 && dims[1]<5 && bounds.minCorner[1]>5.5*millimeter && bounds.maxCorner[1]<10.1*millimeter) inserts=append(inserts,body);
        if(dims[1]>10.9 && dims[1]<11.1 && dims[0]<6 && dims[2]<6 && abs(mid[1]-12.5)<0.001 && abs(sqrt(mid[0]*mid[0]+mid[2]*mid[2])-9)<0.001) oldScrews=append(oldScrews,body);
    }
    if(size(props)!=1 || size(inserts)!=1 || size(oldScrews)!=4) throw regenError("R6 expects one R5 propeller, one motor insert and four M3x8 propeller screws.");
    opDeleteBodies(context,id+"removeInternalInsertAndOldScrews",{"entities":qUnion([qUnion(inserts),qUnion(oldScrews)])});
    r6BuildBellClamp(context,id+"bellClamp",qUnion(props));
    if(size(evaluateQuery(context,qAllModifiableSolidBodies()))!=47) throw regenError("Expected 47 R6 assembly solids after replacing the insert and fasteners.");
}
