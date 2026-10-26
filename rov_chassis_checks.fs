
function requireClear(context is Context, a is Query, b is Query, label is string)
{
    const clashes=evCollision(context,{"tools":a,"targets":b});
    for(var clash in clashes)
    {
        if(clash["type"]!=ClashType.NONE)
            throw regenError(label~" ("~clash["type"]~")");
    }
}
function inspectChassis(context is Context, root is Id, bodies is Query, resized is boolean, propChoice is number) returns map
{
    const frame=qCreatedBy(root+"baseRing"+"solid",EntityType.BODY);
    if(size(evaluateQuery(context,frame))!=1) throw regenError("Main cage must be one connected solid.");
    const all=evaluateQuery(context,bodies);
    if(size(all)!=17) throw regenError("Expected frame + 8 holders + 8 clamp caps (17 solids), got "~size(all));
    const expected=propChoice==80?vector(220,180,70):(resized?vector(210,170,70):vector(180,150,60));
    const bounds=evBox3d(context,{"topology":bodies,"tight":true});
    if(norm(bounds.minCorner+expected*millimeter)>0.01*millimeter || norm(bounds.maxCorner-expected*millimeter)>0.01*millimeter)
        throw regenError("Chassis does not fit the selected overall dimensions.");
    const q=1/sqrt(2);
    const hx=propChoice==80?159.571428571429:(propChoice==72?154.942857142857:(resized?163:133));
    const hy=propChoice==80?57.857142857143:(propChoice==72?58.714285714285714:(resized?75:55));
    const vx=propChoice==80?65.714285714286:(propChoice==72?69.428571428571:(resized?90:60));
    const vy=propChoice==80?122.142857142857:(propChoice==72?117.285714285714:(resized?125:105));
    const wantedRadius=propChoice/2+5;
    const fixtures=[
        {"centre":vector(-hx,-hy,0),"axis":vector(-q,-q,0),"x":vector(q,-q,0),"y":vector(0,0,1)},
        {"centre":vector(-hx,hy,0),"axis":vector(-q,q,0),"x":vector(-q,-q,0),"y":vector(0,0,1)},
        {"centre":vector(hx,-hy,0),"axis":vector(q,-q,0),"x":vector(q,q,0),"y":vector(0,0,1)},
        {"centre":vector(hx,hy,0),"axis":vector(q,q,0),"x":vector(-q,q,0),"y":vector(0,0,1)},
        {"centre":vector(-vx,-vy,0),"axis":vector(0,0,1),"x":vector(-1,0,0),"y":vector(0,-1,0)},
        {"centre":vector(-vx,vy,0),"axis":vector(0,0,-1),"x":vector(-1,0,0),"y":vector(0,1,0)},
        {"centre":vector(vx,-vy,0),"axis":vector(0,0,-1),"x":vector(1,0,0),"y":vector(0,-1,0)},
        {"centre":vector(vx,vy,0),"axis":vector(0,0,1),"x":vector(1,0,0),"y":vector(0,1,0)}
    ];
    var checks=3;
    for(var i=0;i<8;i+=1)
    {
        const f=fixtures[i];
        const holder=qCreatedBy(root+("holder"~i)+"motorPlate",EntityType.BODY);
        const cap=qCreatedBy(root+("clamp"~i)+"cap",EntityType.BODY);
        if(size(evaluateQuery(context,holder))!=1 || size(evaluateQuery(context,cap))!=1)
            throw regenError("Missing or disconnected holder or cap "~i);
        checks+=1;
        const faces=evaluateQuery(context,qGeometry(qOwnedByBody(holder,EntityType.FACE),GeometryType.CYLINDER));
        var outerFace=undefined;
        var radius=0*millimeter;
        var hasBore=false;
        for(var face in faces)
        {
            const cylinder=evSurfaceDefinition(context,{"face":face});
            if(cylinder.radius>radius){radius=cylinder.radius;outerFace=face;}
            if(abs(cylinder.radius-(propChoice/2+2)*millimeter)<0.01*millimeter) hasBore=true;
        }
        if(abs(radius-wantedRadius*millimeter)>0.01*millimeter || !hasBore) throw regenError("Holder "~i~" has incorrect duct diameters.");
        checks+=1;
        const actualAxis=evAxis(context,{"axis":outerFace});
        if(abs(dot(actualAxis.direction,f.axis))<0.999999 ||
           norm(cross(actualAxis.origin-f.centre*millimeter,f.axis))>0.01*millimeter)
            throw regenError("Holder "~i~" axis or position is wrong.");
        checks+=1;
        const rear=(f.centre-f.axis*30)*millimeter;
        const motorHoles=[vector(8,0,2),vector(-8,0,2),vector(0,9.5,2),vector(0,-9.5,2)];
        for(var p in motorHoles)
        {
            const world=rear+(f.x*p[0]+f.y*p[1]+f.axis*p[2])*millimeter;
            const gap=evDistance(context,{"side0":world,"side1":holder}).distance;
            if(abs(gap-1.65*millimeter)>0.01*millimeter) throw regenError("Motor M3 hole or facing direction is wrong on holder "~i);
            checks+=1;
        }
        const boss=evDistance(context,{"side0":rear+f.axis*2*millimeter,"side1":holder}).distance;
        if(abs(boss-4.75*millimeter)>0.01*millimeter) throw regenError("Rear motor boss opening is wrong.");
        checks+=1;
        const blade=evDistance(context,{"side0":rear+(f.x*(propChoice/2)+f.axis*50)*millimeter,"side1":holder}).distance;
        if(abs(blade-2*millimeter)>0.01*millimeter) throw regenError("Propeller tip clearance was lost.");
        checks+=1;
        const clampGap=evDistance(context,{"side0":rear+f.axis*24*millimeter,"side1":cap}).distance;
        if(abs(clampGap-(wantedRadius+0.2)*millimeter)>0.01*millimeter) throw regenError("Clamp cap "~i~" fit radius "~(clampGap/millimeter)~" mm.");
        checks+=1;
        for(var sign in [-1,1])
        {
            const bolt=rear+(f.x*(sign*(wantedRadius+7))+f.y*4.5+f.axis*24)*millimeter;
            const boltGap=evDistance(context,{"side0":bolt,"side1":cap}).distance;
            if(abs(boltGap-1.65*millimeter)>0.01*millimeter) throw regenError("Clamp cap M3 bolt hole is wrong.");
            checks+=1;
            const baseBolt=rear+(f.x*(sign*(wantedRadius+7))-f.y*4.5+f.axis*24)*millimeter;
            if(abs(evDistance(context,{"side0":baseBolt,"side1":frame}).distance-1.65*millimeter)>0.01*millimeter)
                throw regenError("Clamp base bolt: prop "~propChoice~" holder "~i~" side "~sign~" radius "~(evDistance(context,{"side0":baseBolt,"side1":frame}).distance/millimeter));
            checks+=1;
        }
        const flow=chassisCylinder(context,root+("flowProbe"~i),f.centre-f.axis*(i<4?90:80),f.centre+f.axis*(i<4?90:80),propChoice/2+1);
        requireClear(context,flow,qUnion([frame,cap]),"Chassis obstructs flow for prop "~propChoice~" holder "~i);
        opDeleteBodies(context,root+("deleteFlowProbe"~i),{"entities":flow});
        checks+=1;
    }
    for(var i=0;i<size(all);i+=1)
    {
        for(var j=i+1;j<size(all);j+=1)
        {
            requireClear(context,all[i],all[j],"Placed chassis solids interfere");
            checks+=1;
        }
    }
    return {"checksPassed":checks,"solids":size(all),"boundsMM":[bounds.minCorner/millimeter,bounds.maxCorner/millimeter]};
}
annotation { "Feature Type Name":"ChassisGeometryChecks" }
export const chassisGeometryChecks = defineFeature(function(context is Context,id is Id,definition is map)
precondition {}
{
    const before=evaluateQuery(context,qBodyType(qEverything(EntityType.BODY),BodyType.SOLID));
    rovChassis(context,id+"design",{});
    const bodies=qSubtraction(qBodyType(qEverything(EntityType.BODY),BodyType.SOLID),qUnion(before));
    const defaultResult=inspectChassis(context,id+"design",bodies,false,60);
    // Move the default fixture away before testing a second complete chassis.
    opTransform(context,id+"moveDefault",{"bodies":bodies,"transform":transform(vector(0,0,500)*millimeter)});
    const beforeLarger=evaluateQuery(context,qBodyType(qEverything(EntityType.BODY),BodyType.SOLID));
    rovChassis(context,id+"larger",{"length":420*millimeter,"width":340*millimeter,"height":140*millimeter});
    const larger=qSubtraction(qBodyType(qEverything(EntityType.BODY),BodyType.SOLID),qUnion(beforeLarger));
    const largerResult=inspectChassis(context,id+"larger",larger,true,60);
    opDeleteBodies(context,id+"removeLarger",{"entities":larger});
    opTransform(context,id+"restoreDefault",{"bodies":bodies,"transform":transform(vector(0,0,-500)*millimeter)});
    const beforeBare=evaluateQuery(context,qBodyType(qEverything(EntityType.BODY),BodyType.SOLID));
    rovChassis(context,id+"bare",{"showHolders":false});
    const bare=qSubtraction(qBodyType(qEverything(EntityType.BODY),BodyType.SOLID),qUnion(beforeBare));
    if(size(evaluateQuery(context,bare))!=9) throw regenError("Hide-reference mode must retain frame and eight caps.");
    opDeleteBodies(context,id+"removeBare",{"entities":bare});
    
    var parameterResults=[];
    for(var diameter in [72,80])
    {
        const snapshot=evaluateQuery(context,qBodyType(qEverything(EntityType.BODY),BodyType.SOLID));
        const pId=id+("parameter"~diameter);
        const parameters={"length":(diameter==80?440:420)*millimeter,"width":(diameter==80?360:340)*millimeter,"height":140*millimeter,"propDiameter":diameter*millimeter};
        rovChassis(context,pId,parameters);
        const parameterBodies=qSubtraction(qBodyType(qEverything(EntityType.BODY),BodyType.SOLID),qUnion(snapshot));
        const results=inspectChassis(context,pId,parameterBodies,true,diameter);
        parameterResults=append(parameterResults,results);
        opDeleteBodies(context,id+("removeParameter"~diameter),{"entities":parameterBodies});
    }

    const edgeSnapshot=evaluateQuery(context,qBodyType(qEverything(EntityType.BODY),BodyType.SOLID));
    rovChassis(context,id+"edge",{"length":361*millimeter,"width":304*millimeter,"height":120*millimeter,"propDiameter":65*millimeter});
    const edgeBodies=qSubtraction(qBodyType(qEverything(EntityType.BODY),BodyType.SOLID),qUnion(edgeSnapshot));
    const edgeFrame=qCreatedBy(id+"edge"+"baseRing"+"solid",EntityType.BODY);
    if(size(evaluateQuery(context,edgeBodies))!=17) throw regenError("Edge case must produce 17 solids.");
    for(var sx in [-1,1])
        for(var sy in [-1,1])
        {
            if(size(evaluateQuery(context,qContainsPoint(edgeFrame,vector(sx*74.95,sy*30,-45)*millimeter)))!=1)
                throw regenError("Tray has insufficient material beyond equipment screw hole.");
            if(abs(evDistance(context,{"side0":vector(sx*70,sy*30,-45)*millimeter,"side1":edgeFrame}).distance-1.65*millimeter)>0.01*millimeter)
                throw regenError("Edge case equipment screw hole missing.");
        }
    const edgeAll=evaluateQuery(context,edgeBodies);
    for(var i=0;i<size(edgeAll);i+=1)
        for(var j=i+1;j<size(edgeAll);j+=1)
            requireClear(context,edgeAll[i],edgeAll[j],"Edge case solids interfere");
    opDeleteBodies(context,id+"removeEdge",{"entities":edgeBodies});
    println({"trayMargin":"passed","default":defaultResult,"resized":largerResult,"propellerVariants":parameterResults,"hideReferenceMode":"passed"});
},{});

