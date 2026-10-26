FeatureScript 3083;
import(path : "onshape/std/geometry.fs", version : "3083.0");

// A2212 stationary-base holder. The motor's rotating bell stays free.
// Axis: +Z. Motor seats at Z = plate thickness. No propeller is manufactured here.
annotation { "Feature Type Name" : "ROVThrusterHolder" }
const rovThrusterHolder = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Propeller diameter" }
        isLength(definition.propDiameter, { (millimeter) : [40, 60, 200] } as LengthBoundSpec);
        annotation { "Name" : "Radial blade clearance" }
        isLength(definition.tipClearance, { (millimeter) : [1, 2, 6] } as LengthBoundSpec);
        annotation { "Name" : "Shroud wall thickness" }
        isLength(definition.wallThickness, { (millimeter) : [2, 3, 8] } as LengthBoundSpec);
        annotation { "Name" : "Shroud length" }
        isLength(definition.ductLength, { (millimeter) : [40, 60, 150] } as LengthBoundSpec);
        annotation { "Name" : "Motor plate thickness" }
        isLength(definition.plateThickness, { (millimeter) : [3, 4, 8] } as LengthBoundSpec);
        annotation { "Name" : "Motor plate diameter" }
        isLength(definition.plateDiameter, { (millimeter) : [28, 32, 45] } as LengthBoundSpec);
        annotation { "Name" : "M3 screw clearance diameter" }
        isLength(definition.screwDiameter, { (millimeter) : [3.1, 3.3, 3.8] } as LengthBoundSpec);
        annotation { "Name" : "Rear shaft / bearing-boss clearance" }
        isLength(definition.bossDiameter, { (millimeter) : [5, 9.5, 10] } as LengthBoundSpec);
        annotation { "Name" : "Motor mounting spacing X" }
        isLength(definition.spacingX, { (millimeter) : [14, 16, 24] } as LengthBoundSpec);
        annotation { "Name" : "Motor mounting spacing Y" }
        isLength(definition.spacingY, { (millimeter) : [14, 19, 24] } as LengthBoundSpec);
        annotation { "Name" : "Support rib width" }
        isLength(definition.ribWidth, { (millimeter) : [3, 4, 8] } as LengthBoundSpec);
    }
    {
        const boreRadius = definition.propDiameter / 2 + definition.tipClearance;
        const outerRadius = boreRadius + definition.wallThickness;
        const plateRadius = definition.plateDiameter / 2;
        const maxSpacing = max(definition.spacingX, definition.spacingY);
        const minSpacing = min(definition.spacingX, definition.spacingY);
        if (boreRadius <= plateRadius + 4 * millimeter)
            throw regenError("Increase propeller diameter or reduce motor plate diameter.", ["propDiameter", "plateDiameter"]);
        if (plateRadius - maxSpacing / 2 - definition.screwDiameter / 2 < 2 * millimeter)
            throw regenError("Motor plate needs at least 2 mm of material beyond the screw holes.", ["plateDiameter"]);
        if (minSpacing / 2 - definition.screwDiameter / 2 - definition.bossDiameter / 2 < 1.5 * millimeter)
            throw regenError("Rear shaft hole is too close to the M3 mounting holes.", ["bossDiameter", "spacingX", "spacingY"]);

        fCylinder(context, id + "ductOuter", {
            "bottomCenter" : vector(0, 0, 0) * millimeter,
            "topCenter" : vector(0, 0, 1) * definition.ductLength,
            "radius" : outerRadius
        });
        fCylinder(context, id + "ductBore", {
            "bottomCenter" : vector(0, 0, -1) * millimeter,
            "topCenter" : vector(0, 0, 1) * (definition.ductLength + millimeter),
            "radius" : boreRadius
        });
        const duct = qCreatedBy(id + "ductOuter", EntityType.BODY);
        opBoolean(context, id + "hollowShroud", {
            "targets" : duct,
            "tools" : qCreatedBy(id + "ductBore", EntityType.BODY),
            "operationType" : BooleanOperationType.SUBTRACTION
        });

        fCylinder(context, id + "motorPlate", {
            "bottomCenter" : vector(0, 0, 0) * millimeter,
            "topCenter" : vector(0, 0, 1) * definition.plateThickness,
            "radius" : plateRadius
        });
        const holder = qCreatedBy(id + "motorPlate", EntityType.BODY);
        var joinedBodies = [holder, duct];
        for (var i = 0; i < 3; i += 1)
        {
            const ribId = id + ("rib" ~ i);
            fCuboid(context, ribId, {
                "corner1" : vector(plateRadius - millimeter, -definition.ribWidth / 2, 0 * millimeter),
                "corner2" : vector(boreRadius + millimeter, definition.ribWidth / 2, definition.plateThickness)
            });
            const rib = qCreatedBy(ribId, EntityType.BODY);
            if (i > 0)
                opTransform(context, id + ("rotateRib" ~ i), {
                    "bodies" : rib,
                    "transform" : rotationAround(line(vector(0, 0, 0) * millimeter, vector(0, 0, 1)), i * 120 * degree)
                });
            joinedBodies = append(joinedBodies, rib);
        }
        opBoolean(context, id + "joinHolder", {
            "tools" : qUnion(joinedBodies),
            "operationType" : BooleanOperationType.UNION
        });

        // Cross pattern: (+/-8,0) and (0,+/-9.5), not a 16 x 19 rectangle.
        const holeCenters = [
            vector(definition.spacingX / 2, 0 * millimeter, 0 * millimeter),
            vector(-definition.spacingX / 2, 0 * millimeter, 0 * millimeter),
            vector(0 * millimeter, definition.spacingY / 2, 0 * millimeter),
            vector(0 * millimeter, -definition.spacingY / 2, 0 * millimeter),
            vector(0, 0, 0) * millimeter
        ];
        var holeTools = [];
        for (var j = 0; j < 5; j += 1)
        {
            const holeId = id + ("hole" ~ j);
            fCylinder(context, holeId, {
                "bottomCenter" : holeCenters[j] - vector(0, 0, 1) * millimeter,
                "topCenter" : holeCenters[j] + vector(0, 0, 1) * (definition.plateThickness + millimeter),
                "radius" : j == 4 ? definition.bossDiameter / 2 : definition.screwDiameter / 2
            });
            holeTools = append(holeTools, qCreatedBy(holeId, EntityType.BODY));
        }
        opBoolean(context, id + "mountingHoles", {
            "targets" : holder,
            "tools" : qUnion(holeTools),
            "operationType" : BooleanOperationType.SUBTRACTION
        });

        // Open rear cable notch in the gap between the support ribs.
        fCuboid(context, id + "cableNotchTool", {
            "corner1" : vector(-4 * millimeter, boreRadius - millimeter, -millimeter),
            "corner2" : vector(4 * millimeter, outerRadius + millimeter, 8 * millimeter)
        });
        opBoolean(context, id + "cableExit", {
            "targets" : holder,
            "tools" : qCreatedBy(id + "cableNotchTool", EntityType.BODY),
            "operationType" : BooleanOperationType.SUBTRACTION
        });
        const circularEdges = qGeometry(qOwnedByBody(holder, EntityType.EDGE), GeometryType.CIRCLE);
        const frontRim = qUnion([
            qClosestTo(circularEdges, vector(boreRadius, 0 * millimeter, definition.ductLength)),
            qClosestTo(circularEdges, vector(outerRadius, 0 * millimeter, definition.ductLength))
        ]);
        opFillet(context, id + "roundedInlet", { "entities" : frontRim, "radius" : millimeter });
        setProperty(context, { "entities" : holder, "propertyType" : PropertyType.NAME,
            "value" : "A2212 ROV motor + fan holder" });
        setProperty(context, { "entities" : holder, "propertyType" : PropertyType.APPEARANCE,
            "value" : color(0.92, 0.94, 0.96) });
    }, {
        "propDiameter" : 60 * millimeter,
        "tipClearance" : 2 * millimeter,
        "wallThickness" : 3 * millimeter,
        "ductLength" : 60 * millimeter,
        "plateThickness" : 4 * millimeter,
        "plateDiameter" : 32 * millimeter,
        "screwDiameter" : 3.3 * millimeter,
        "bossDiameter" : 9.5 * millimeter,
        "spacingX" : 16 * millimeter,
        "spacingY" : 19 * millimeter,
        "ribWidth" : 4 * millimeter
    });
// Open eight-thruster cage. Local holder +Z is the thrust axis.
function chassisBrick(context is Context, id is Id, a is Vector, b is Vector) returns Query
{
    fCuboid(context,id,{
        "corner1":vector(min(a[0],b[0]),min(a[1],b[1]),min(a[2],b[2]))*millimeter,
        "corner2":vector(max(a[0],b[0]),max(a[1],b[1]),max(a[2],b[2]))*millimeter
    });
    return qCreatedBy(id,EntityType.BODY);
}
function chassisCylinder(context is Context, id is Id, a is Vector, b is Vector, r is number) returns Query
{
    fCylinder(context,id,{"bottomCenter":a*millimeter,"topCenter":b*millimeter,"radius":r*millimeter});
    return qCreatedBy(id,EntityType.BODY);
}
function chassisRing(context is Context, id is Id, l is number, w is number, z is number) returns Query
{
    const ring=chassisBrick(context,id+"solid",vector(-l/2,-w/2,z),vector(l/2,w/2,z+8));
    const tool=chassisBrick(context,id+"window",vector(-l/2+8,-w/2+8,z-1),vector(l/2-8,w/2-8,z+9));
    opBoolean(context,id+"open",{"targets":ring,"tools":tool,"operationType":BooleanOperationType.SUBTRACTION});
    return ring;
}
function chassisClamp(context is Context, id is Id, radius is number, clearance is number) returns map
{
    const inner=radius+clearance/2;
    const outer=inner+4;
    const base=chassisCylinder(context,id+"base",vector(0,0,18),vector(0,0,30),outer);
    const cap=chassisCylinder(context,id+"cap",vector(0,0,18),vector(0,0,30),outer);
    const bore=chassisCylinder(context,id+"bore",vector(0,0,17),vector(0,0,31),inner);
    opBoolean(context,id+"hollow",{"targets":qUnion([base,cap]),"tools":bore,"operationType":BooleanOperationType.SUBTRACTION});
    const upperCut=chassisBrick(context,id+"upperCut",vector(-outer-20,-0.5,17),vector(outer+20,outer+1,31));
    opBoolean(context,id+"lowerHalf",{"targets":base,"tools":upperCut,"operationType":BooleanOperationType.SUBTRACTION});
    const lowerCut=chassisBrick(context,id+"lowerCut",vector(-outer-20,-outer-1,17),vector(outer+20,0.5,31));
    opBoolean(context,id+"upperHalf",{"targets":cap,"tools":lowerCut,"operationType":BooleanOperationType.SUBTRACTION});
    var bases=[base];
    var caps=[cap];
    for(var s in [-1,1])
    {
        const label=s<0?"left":"right";
        bases=append(bases,chassisBrick(context,id+(label~"baseEar"),vector(s*inner,-8.5,18),vector(s*(radius+13),-0.5,30)));
        caps=append(caps,chassisBrick(context,id+(label~"capEar"),vector(s*inner,0.5,18),vector(s*(radius+13),8.5,30)));
    }
    opBoolean(context,id+"joinBase",{"tools":qUnion(bases),"operationType":BooleanOperationType.UNION});
    opBoolean(context,id+"joinCap",{"tools":qUnion(caps),"operationType":BooleanOperationType.UNION});
    var holes=[];
    for(var s in [-1,1])
    {
        holes=append(holes,chassisCylinder(context,id+("screw"~s),vector(s*(radius+7),-10,24),vector(s*(radius+7),10,24),1.65));
    }
    opBoolean(context,id+"bolts",{"targets":qUnion([base,cap]),"tools":qUnion(holes),"operationType":BooleanOperationType.SUBTRACTION});
    return {"base":base,"cap":cap};
}
annotation { "Feature Type Name":"ROVChassis" }
export const rovChassis = defineFeature(function(context is Context,id is Id,definition is map)
precondition
{
    annotation { "Name":"Overall length" }
    isLength(definition.length,{(millimeter):[360,360,600]} as LengthBoundSpec);
    annotation { "Name":"Overall width" }
    isLength(definition.width,{(millimeter):[300,300,500]} as LengthBoundSpec);
    annotation { "Name":"Overall height" }
    isLength(definition.height,{(millimeter):[120,120,220]} as LengthBoundSpec);
    annotation { "Name":"Propeller diameter" }
    isLength(definition.propDiameter,{(millimeter):[60,60,80]} as LengthBoundSpec);
    annotation { "Name":"Clamp diametral clearance" }
    isLength(definition.clampClearance,{(millimeter):[0.2,0.4,0.8]} as LengthBoundSpec);
    annotation { "Name":"Show thruster holder references" }
    definition.showHolders is boolean;
}
{
    const l=definition.length/millimeter;
    const w=definition.width/millimeter;
    const h=definition.height/millimeter;
    const r=definition.propDiameter/(2*millimeter)+5;
    const scale=r/35;
    const clearance=definition.clampClearance/millimeter;
    const outer=r+clearance/2+4;
    const hx=l/2-47*scale;
    const hy=w/2-95*scale;
    const vx=l/2-120*scale;
    const vy=w/2-45*scale;
    if(vx < r+14 || vy-r < 65 || hy < (30+r)/sqrt(2)+2 || h/2 < outer+12)
        throw regenError("Increase chassis length, width or height for this propeller size.",["length","width","height","propDiameter"]);
    if(l/2 < hx+(30+r)/sqrt(2) || w/2 < vy+outer)
        throw regenError("Thruster holders do not fit inside the chassis envelope.",["length","width","propDiameter"]);

    const frame=chassisRing(context,id+"baseRing",l,w,-h/2);
    var frameBodies=[frame,chassisRing(context,id+"topRing",l,w,h/2-8)];
    // Edge-centre uprights leave the four diagonal corner streams clear.
    const postRects=[
        [vector(-l/2,-7,-h/2+6),vector(-l/2+14,7,h/2-6)],
        [vector(l/2-14,-7,-h/2+6),vector(l/2,7,h/2-6)],
        [vector(-7,-w/2,-h/2+6),vector(7,-w/2+14,h/2-6)],
        [vector(-7,w/2-14,-h/2+6),vector(7,w/2,h/2-6)]
    ];
    for(var p=0;p<4;p+=1)
        frameBodies=append(frameBodies,chassisBrick(context,id+("post"~p),postRects[p][0],postRects[p][1]));
    frameBodies=append(frameBodies,chassisBrick(context,id+"traySpine",vector(-8,-w/2,-h/2),vector(8,w/2,-h/2+18)));
    frameBodies=append(frameBodies,chassisBrick(context,id+"tray",vector(-max(vx+20,75),-vy+r+25,-h/2+12),vector(max(vx+20,75),vy-r-25,-h/2+18)));
    var openings=[];
    for(var x in [-50,0,50])
        openings=append(openings,chassisBrick(context,id+("vent"~x),vector(x-17,-15,-h/2+11),vector(x+17,15,-h/2+19)));
    for(var sx in [-1,1])
    {
        for(var sy in [-1,1])
        {
            openings=append(openings,chassisBrick(context,id+("strap"~sx~"_"~sy),
                vector(sx*55-9,sy*33-1.75,-h/2+11),vector(sx*55+9,sy*33+1.75,-h/2+19)));
            openings=append(openings,chassisCylinder(context,id+("equipmentHole"~sx~"_"~sy),
                vector(sx*70,sy*30,-h/2+11),vector(sx*70,sy*30,-h/2+19),1.65));
        }
    }
    // Merge the cage before cutting the tray so every opening cuts its supports too.
    opBoolean(context,id+"joinCage",{"tools":qUnion(frameBodies),"operationType":BooleanOperationType.UNION});
    opBoolean(context,id+"trayOpenings",{"targets":frame,"tools":qUnion(openings),"operationType":BooleanOperationType.SUBTRACTION});
    frameBodies=[frame];

    var n=0;
    for(var sx in [-1,1])
    {
        for(var sy in [-1,1])
        {
            const axis=vector(sx,sy,0)/sqrt(2);
            const centre=vector(sx*hx,sy*hy,0);
            const rear=centre-axis*30;
            const cSys=coordSystem(rear*millimeter,vector(-sy,sx,0)/sqrt(2),axis);
            const clamp=chassisClamp(context,id+("clamp"~n),r,clearance);
            opTransform(context,id+("placeClamp"~n),{"bodies":qUnion([clamp.base,clamp.cap]),"transform":toWorld(cSys)});
            frameBodies=append(frameBodies,clamp.base);
            const foot=centre-axis*6;
            frameBodies=append(frameBodies,chassisBrick(context,id+("horizontalArm"~n),
                vector(foot[0]-sx*10,foot[1]-10,-h/2+12),vector(sx*(l/2-4),foot[1]+10,-outer+2)));
            frameBodies=append(frameBodies,chassisBrick(context,id+("horizontalLeg"~n),
                vector(sx*(l/2-10),foot[1]-10,-h/2),vector(sx*l/2,foot[1]+10,-outer+2)));
            if(definition.showHolders)
            {
                rovThrusterHolder(context,id+("holder"~n),{"propDiameter":definition.propDiameter});
                const holder=qCreatedBy(id+("holder"~n)+"motorPlate",EntityType.BODY);
                opTransform(context,id+("placeHolder"~n),{"bodies":holder,"transform":toWorld(cSys)});
                setProperty(context,{"entities":holder,"propertyType":PropertyType.NAME,"value":"H"~(n+1)~" - 45 deg horizontal holder"});
            }
            setProperty(context,{"entities":clamp.cap,"propertyType":PropertyType.NAME,"value":"H"~(n+1)~" - removable M3 clamp cap"});
            setProperty(context,{"entities":clamp.cap,"propertyType":PropertyType.APPEARANCE,"value":color(0.15,0.48,0.65)});
            n+=1;
        }
    }
    n=4;
    for(var sx in [-1,1])
    {
        for(var sy in [-1,1])
        {
            const sz=sx*sy;
            const axis=vector(0,0,sz);
            const centre=vector(sx*vx,sy*vy,0);
            const rear=centre-axis*30;
            const cSys=coordSystem(rear*millimeter,vector(sy*sz,0,0),axis);
            const clamp=chassisClamp(context,id+("clamp"~n),r,clearance);
            opTransform(context,id+("placeClamp"~n),{"bodies":qUnion([clamp.base,clamp.cap]),"transform":toWorld(cSys)});
            frameBodies=append(frameBodies,clamp.base);
            const z=-6*sz;
            frameBodies=append(frameBodies,chassisBrick(context,id+("verticalFoot"~n),
                vector(sx*vx-10,sy*(vy-r-26),-h/2+12),vector(sx*vx+10,sy*(vy-r-6),-h/2+18)));
            frameBodies=append(frameBodies,chassisBrick(context,id+("verticalColumn"~n),
                vector(sx*vx-10,sy*(vy-r-20),-h/2+12),vector(sx*vx+10,sy*(vy-r-6),z+6)));
            frameBodies=append(frameBodies,chassisBrick(context,id+("verticalArm"~n),
                vector(sx*vx-10,sy*(vy-r-16),z-6),vector(sx*vx+10,sy*(vy-r-1),z+6)));
            if(definition.showHolders)
            {
                rovThrusterHolder(context,id+("holder"~n),{"propDiameter":definition.propDiameter});
                const holder=qCreatedBy(id+("holder"~n)+"motorPlate",EntityType.BODY);
                opTransform(context,id+("placeHolder"~n),{"bodies":holder,"transform":toWorld(cSys)});
                setProperty(context,{"entities":holder,"propertyType":PropertyType.NAME,"value":"V"~(n-3)~(sz>0?" - upward holder":" - downward holder")});
            }
            setProperty(context,{"entities":clamp.cap,"propertyType":PropertyType.NAME,"value":"V"~(n-3)~" - removable M3 clamp cap"});
            setProperty(context,{"entities":clamp.cap,"propertyType":PropertyType.APPEARANCE,"value":color(0.15,0.48,0.65)});
            n+=1;
        }
    }
    opBoolean(context,id+"joinMountedFrame",{"tools":qUnion(frameBodies),"operationType":BooleanOperationType.UNION});
    if(size(evaluateQuery(context,frame))!=1)
        throw regenError("Chassis supports did not connect; increase the frame size.",["length","width","height"]);
    setProperty(context,{"entities":frame,"propertyType":PropertyType.NAME,"value":"ROV chassis - cage, tray and eight M3 clamp bases"});
    setProperty(context,{"entities":frame,"propertyType":PropertyType.APPEARANCE,"value":color(0.07,0.18,0.25)});
},{
    "length":360*millimeter,"width":300*millimeter,"height":120*millimeter,
    "propDiameter":60*millimeter,"clampClearance":0.4*millimeter,"showHolders":true
});

