FeatureScript 3095;
import(path : "onshape/std/geometry.fs", version : "3095.0");

function checkedFillet(context is Context, id is Id, definition is map)
{
    try { opFillet(context, id, definition); }
    catch (error) { throw regenError("Cannot round " ~ id[size(id)-1]); }
}

// Approved revision from the user's two-page print-fit report.
// Intended for the six aligned bodies in "A2212 corrected parts".
function applyPrintFit(context is Context, id is Id, definition is map)
{
    if (size(evaluateQuery(context, definition.nozzle)) != 1 ||
        size(evaluateQuery(context, definition.propeller)) != 1)
        throw regenError("Select the nozzle and propeller bodies.");

    var nozzleBounds = evBox3d(context, { "topology" : definition.nozzle, "tight" : true });
    var propBounds = evBox3d(context, { "topology" : definition.propeller, "tight" : true });
    if (nozzleBounds.minCorner[1] > -30 * millimeter ||
        propBounds.minCorner[1] < -4 * millimeter || propBounds.minCorner[1] > 0 * millimeter)
        throw regenError("Use the aligned nozzle and propeller in A2212 corrected parts.");

    // The single side collar is superseded by the continuous rear ring.

    // Reinforce the existing hole locations without moving the cover or its feet.
    var directions = [vector(1, 0, 0), vector(-1, 0, 0),
                      vector(0, 0, 1), vector(0, 0, -1)];
    var bossBodies = [];
    var boreBodies = [];
    for (var i = 0; i < size(directions); i += 1)
    {
        var direction = directions[i];
        var holeCenter = vector(0, 17.5, 0) * millimeter;
        var bossId = id + ("boss" ~ i);
        fCylinder(context, bossId, {
                    "bottomCenter" : holeCenter + direction * 45 * millimeter,
                    "topCenter" : holeCenter + direction * 50.25 * millimeter,
                    "radius" : definition.bossDiameter / 2
                });
        bossBodies = append(bossBodies, qCreatedBy(bossId, EntityType.BODY));
    }
    // First tool retains the imported nozzle identity and assembly references.
    opBoolean(context, id + "reinforce", {
                "tools" : qUnion([definition.nozzle, qUnion(bossBodies)]),
                "operationType" : BooleanOperationType.UNION
            });
    // R4 uses axial clamping joints instead of radial retention pins.

    // Adjust only the sixteen flat seating ribs, keeping the ventilation grooves.
    var seatingFaces = [];
    for (var face in evaluateQuery(context,
            qGeometry(qOwnedByBody(definition.propeller, EntityType.FACE), GeometryType.PLANE)))
    {
        var facePlane = evPlane(context, { "face" : face });
        if (abs(facePlane.normal[1]) < 1e-6 &&
            abs(abs(dot(facePlane.origin, facePlane.normal)) - 14.4 * millimeter) < 1e-5 * millimeter)
            seatingFaces = append(seatingFaces, face);
    }
    if (size(seatingFaces) != 16)
        throw regenError("Expected the sixteen original motor seating ribs.");
    opOffsetFace(context, id + "snugSeat", {
                "moveFaces" : qUnion(seatingFaces),
                "offsetDistance" : definition.guideTightening
            });
}

annotation { "Feature Type Name" : "PDF fit corrections" }
export const thrusterPrintFit = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Nozzle body", "Filter" : EntityType.BODY && BodyType.SOLID,
                     "MaxNumberOfPicks" : 1 }
        definition.nozzle is Query;
        annotation { "Name" : "Propeller body", "Filter" : EntityType.BODY && BodyType.SOLID,
                     "MaxNumberOfPicks" : 1 }
        definition.propeller is Query;
        annotation { "Name" : "Enclosed wire hole diameter" }
        isLength(definition.wireDiameter, { (millimeter) : [6, 10, 12] } as LengthBoundSpec);
        annotation { "Name" : "Reinforcing boss diameter" }
        isLength(definition.bossDiameter, { (millimeter) : [8, 12, 14] } as LengthBoundSpec);
        annotation { "Name" : "Screw hole diameter" }
        isLength(definition.screwDiameter, { (millimeter) : [3, 3.3, 4] } as LengthBoundSpec);
        annotation { "Name" : "Motor guide tightening" }
        isLength(definition.guideTightening, { (millimeter) : [0.01, 0.35, 0.4] } as LengthBoundSpec);
    }
    {
        applyPrintFit(context, id, definition);
    }, {
        "nozzle" : qNothing(), "propeller" : qNothing(),
        "wireDiameter" : 10 * millimeter, "bossDiameter" : 12 * millimeter,
        "screwDiameter" : 3.3 * millimeter, "guideTightening" : 0.35 * millimeter
    });

// Keep the gray cover's shape. Extend only the nozzle's front mounting region
// and rigidly place the cover forward to clear the rotating propeller.
function applySpinClearance(context is Context, id is Id, definition is map)
{
    if (size(evaluateQuery(context, definition.nozzle)) != 1 ||
        size(evaluateQuery(context, definition.cover)) != 1 ||
        size(evaluateQuery(context, definition.rotor)) != 1)
        throw regenError("Select the aligned nozzle, gray cover, and A2212 rotor.");

    var sectionPlane = plane(vector(0, 10, 0) * millimeter, vector(0, 1, 0));
    opSplitPart(context, id + "splitFront", {
                "targets" : definition.nozzle, "tool" : sectionPlane
            });
    var rear = qSplitBy(id + "splitFront", EntityType.BODY, true);
    var front = qSplitBy(id + "splitFront", EntityType.BODY, false);
    if (size(evaluateQuery(context, rear)) != 1 || size(evaluateQuery(context, front)) != 1)
        throw regenError("Expected the nozzle tube to cross the front section plane.");
    var sectionFace = qCoincidesWithPlane(qOwnedByBody(rear, EntityType.FACE), sectionPlane);
    opTransform(context, id + "moveFrontMounts", {
                "bodies" : front,
                "transform" : transform(vector(0, 1, 0) * definition.extension)
            });
    // Extrude the actual tube section, preserving its wall and inner contour.
    opExtrude(context, id + "extendTube", {
                "entities" : sectionFace, "direction" : vector(0, 1, 0),
                "endBound" : BoundingType.BLIND, "endDepth" : definition.extension
            });
    opBoolean(context, id + "rejoinTube", {
                "tools" : qUnion([rear, front, qCreatedBy(id + "extendTube", EntityType.BODY)]),
                "operationType" : BooleanOperationType.UNION
            });
    opTransform(context, id + "placeUnchangedCover", {
                "bodies" : definition.cover,
                "transform" : transform(vector(0, 1, 0) * definition.extension)
            });

    var motorAxis = coordSystem(vector(0, 0, 0) * millimeter, vector(1, 0, 0), vector(0, 1, 0));
    opMateConnector(context, id + "fixedAxis", {
                "coordSystem" : motorAxis, "owner" : rear, "attachTo" : rear
            });
    setProperty(context, { "entities" : qCreatedBy(id + "fixedAxis", EntityType.BODY),
                "propertyType" : PropertyType.NAME, "value" : "Fixed motor axis" });
    opMateConnector(context, id + "rotatingAxis", {
                "coordSystem" : motorAxis, "owner" : definition.rotor, "attachTo" : definition.rotor
            });
    setProperty(context, { "entities" : qCreatedBy(id + "rotatingAxis", EntityType.BODY),
                "propertyType" : PropertyType.NAME, "value" : "Rotating motor axis" });
}

annotation { "Feature Type Name" : "Free rotation clearance" }
export const thrusterSpinClearance = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Nozzle body", "Filter" : EntityType.BODY && BodyType.SOLID,
                     "MaxNumberOfPicks" : 1 }
        definition.nozzle is Query;
        annotation { "Name" : "Unchanged gray cover", "Filter" : EntityType.BODY && BodyType.SOLID,
                     "MaxNumberOfPicks" : 1 }
        definition.cover is Query;
        annotation { "Name" : "A2212 rotor", "Filter" : EntityType.BODY && BodyType.SOLID,
                     "MaxNumberOfPicks" : 1 }
        definition.rotor is Query;
        annotation { "Name" : "Front mounting extension" }
        isLength(definition.extension, { (millimeter) : [3, 3, 5] } as LengthBoundSpec);
    }
    {
        applySpinClearance(context, id, definition);
    }, { "nozzle" : qNothing(), "cover" : qNothing(), "rotor" : qNothing(),
         "extension" : 3 * millimeter });
// User-confirmed M3 fasteners and 9.6 mm center opening.
// Four motor vent openings are 6 mm diameter on an 18 mm pitch circle.
function applyStrengthDrive(context is Context, id is Id, definition is map)
{
    var axes = [vector(9, 0, 0), vector(-9, 0, 0), vector(0, 0, 9), vector(0, 0, -9)];
    var oldAxes = [vector(8.25, 0, 0), vector(-8.25, 0, 0), vector(0, 0, 8.25), vector(0, 0, -8.25)];
    var propTools = [];
    var insertTools = [];
    for (var i = 0; i < 4; i += 1)
    {
        var fillProp = id + ("fillProp" ~ i);
        fCylinder(context, fillProp, { "bottomCenter" : (oldAxes[i] + vector(0,16,0)) * millimeter,
                    "topCenter" : (oldAxes[i] + vector(0,19,0)) * millimeter, "radius" : 1.65 * millimeter });
        propTools = append(propTools, qCreatedBy(fillProp, EntityType.BODY));
        var fillInsert = id + ("fillInsert" ~ i);
        fCylinder(context, fillInsert, { "bottomCenter" : (oldAxes[i] + vector(0,5.6,0)) * millimeter,
                    "topCenter" : (oldAxes[i] + vector(0,10,0)) * millimeter, "radius" : 1.4 * millimeter });
        insertTools = append(insertTools, qCreatedBy(fillInsert, EntityType.BODY));
        var lug = id + ("driveLug" ~ i);
        fCylinder(context, lug, { "bottomCenter" : (axes[i] + vector(0,11.5,0)) * millimeter,
                    "topCenter" : (axes[i] + vector(0,14.25,0)) * millimeter, "radius" : 2.85 * millimeter });
        propTools = append(propTools, qCreatedBy(lug, EntityType.BODY));
        var ear = id + ("insertEar" ~ i);
        fCylinder(context, ear, { "bottomCenter" : (axes[i] + vector(0,5.6,0)) * millimeter,
                    "topCenter" : (axes[i] + vector(0,10,0)) * millimeter, "radius" : 2.6 * millimeter });
        insertTools = append(insertTools, qCreatedBy(ear, EntityType.BODY));
    }
    fCylinder(context, id + "backplate", { "bottomCenter" : vector(0,14.2,0) * millimeter,
                "topCenter" : vector(0,16.05,0) * millimeter, "radius" : 18 * millimeter });
    propTools = append(propTools, qCreatedBy(id + "backplate", EntityType.BODY));
    opBoolean(context, id + "propJoin", { "tools" : qUnion([definition.propeller,qUnion(propTools)]),
                "operationType" : BooleanOperationType.UNION });
    opBoolean(context, id + "insertJoin", { "tools" : qUnion([definition.insert,qUnion(insertTools)]),
                "operationType" : BooleanOperationType.UNION });
    var roots = [];
    for (var e in evaluateQuery(context,qGeometry(qOwnedByBody(definition.propeller,EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if (abs(b.minCorner[1]-14.2*millimeter)<1e-5*millimeter &&
            abs(b.maxCorner[1]-14.2*millimeter)<1e-5*millimeter &&
            abs(b.maxCorner[0]-b.minCorner[0]-5.7*millimeter)<1e-5*millimeter)
            roots=append(roots,e);
    }
    if (size(roots)!=4) throw regenError("Expected four matched drive-lug roots.");
    checkedFillet(context,id+"driveRootRounds",{"entities":qUnion(roots),"radius":0.4*millimeter});
    var propCuts=[];
    var insertCuts=[];
    fCylinder(context,id+"centerBore",{"bottomCenter":vector(0,14.1,0)*millimeter,
                "topCenter":vector(0,19.1,0)*millimeter,"radius":4.8*millimeter});
    propCuts=append(propCuts,qCreatedBy(id+"centerBore",EntityType.BODY));
    for (var i=0;i<4;i+=1)
    {
        var shaft=id+("shaft"~i);
        fCylinder(context,shaft,{"bottomCenter":(axes[i]+vector(0,11.4,0))*millimeter,
                    "topCenter":(axes[i]+vector(0,19.1,0))*millimeter,"radius":1.65*millimeter});
        propCuts=append(propCuts,qCreatedBy(shaft,EntityType.BODY));
        var head=id+("head"~i);
        fCylinder(context,head,{"bottomCenter":(axes[i]+vector(0,16.1,0))*millimeter,
                    "topCenter":(axes[i]+vector(0,19.1,0))*millimeter,"radius":3*millimeter});
        propCuts=append(propCuts,qCreatedBy(head,EntityType.BODY));
        var pilot=id+("pilot"~i);
        fCylinder(context,pilot,{"bottomCenter":(axes[i]+vector(0,5.599,0))*millimeter,
                    "topCenter":(axes[i]+vector(0,10.001,0))*millimeter,"radius":1.3*millimeter});
        insertCuts=append(insertCuts,qCreatedBy(pilot,EntityType.BODY));
    }
    opBoolean(context,id+"propBores",{"tools":qUnion(propCuts),"targets":definition.propeller,"operationType":BooleanOperationType.SUBTRACTION});
    opBoolean(context,id+"insertPilots",{"tools":qUnion(insertCuts),"targets":definition.insert,"operationType":BooleanOperationType.SUBTRACTION});
    var propRims=[];
    var tips=[];
    var mouths=[];
    for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(definition.propeller,EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        var w=b.maxCorner[0]-b.minCorner[0];
        var y=b.minCorner[1];
        if(abs(w-36*millimeter)<1e-5*millimeter &&
            (abs(y-19*millimeter)<1e-5*millimeter || abs(y+3*millimeter)<1e-5*millimeter)) propRims=append(propRims,e);
        if(abs(w-5.7*millimeter)<1e-5*millimeter && abs(y-11.5*millimeter)<1e-5*millimeter) tips=append(tips,e);
        if(abs(y-19*millimeter)<1e-5*millimeter && w<10*millimeter) mouths=append(mouths,e);
    }
    checkedFillet(context,id+"hubRims",{"entities":qUnion(propRims),"radius":0.6*millimeter});
    checkedFillet(context,id+"keyLeadIns",{"entities":qUnion(tips),"radius":0.2*millimeter});
    checkedFillet(context,id+"fastenerMouths",{"entities":qUnion(mouths),"radius":0.2*millimeter});
    // Retain the original imported blade-root surfaces.
    var bossRims=[];
    var frameRoots=[];
    var nozzleLips=[];
    for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(definition.nozzle,EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        var r=max([abs(b.minCorner[0]),abs(b.maxCorner[0]),abs(b.minCorner[2]),abs(b.maxCorner[2])]);
        if(r>50.2*millimeter && b.maxCorner[1]-b.minCorner[1]>11*millimeter) bossRims=append(bossRims,e);
        if(abs(b.minCorner[1]-23*millimeter)<1e-5*millimeter && abs(b.maxCorner[1]-23*millimeter)<1e-5*millimeter && r>44.5*millimeter && r<48*millimeter) nozzleLips=append(nozzleLips,e);
    }
    if(size(bossRims)!=4) throw regenError("Set the reinforcing bosses to 12 mm before adding the fillets.");
    checkedFillet(context,id+"bossRimRounds",{"entities":qUnion(bossRims),"radius":0.75*millimeter});
    if(size(nozzleLips)>0) checkedFillet(context,id+"nozzleLipRounds",{"entities":qUnion(nozzleLips),"radius":0.6*millimeter,"tangentPropagation":true});
    for(var e in evaluateQuery(context,qEdgeConvexityTypeFilter(qOwnedByBody(definition.nozzle,EntityType.EDGE),EdgeConvexityType.CONCAVE)))
    {
        var p=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
        var r=norm(vector(p[0],0*millimeter,p[2]));
        if(evLength(context,{"entities":e})>12*millimeter && ((r>46*millimeter && p[1]>10*millimeter) ||
           (r>18*millimeter && r<35*millimeter && p[1]<-12*millimeter && p[1]>-38*millimeter))) frameRoots=append(frameRoots,e);
    }
    if(size(frameRoots)>0) checkedFillet(context,id+"frameRootStrength",{"entities":qUnion(frameRoots),"radius":0.8*millimeter,"tangentPropagation":false,"allowEdgeOverflow":true,"smoothCorners":true});
    setProperty(context,{"entities":definition.nozzle,"propertyType":PropertyType.NAME,"value":"Nozzle - enclosed 10 mm wire hole, rounded 12 mm mounts"});
    setProperty(context,{"entities":definition.propeller,"propertyType":PropertyType.NAME,"value":"Propeller - A2212 drive keys, 18 mm M3 pattern"});
    setProperty(context,{"entities":definition.insert,"propertyType":PropertyType.NAME,"value":"Motor insert - 23.2 mm envelope, matching M3 pilots"});

}

annotation { "Feature Type Name" : "Rounded strength and motor drive" }
export const thrusterStrengthDrive=defineFeature(function(context is Context,id is Id,definition is map)
    precondition
    {
        annotation {"Name":"Nozzle","Filter":EntityType.BODY && BodyType.SOLID,"MaxNumberOfPicks":1}
        definition.nozzle is Query;
        annotation {"Name":"Propeller","Filter":EntityType.BODY && BodyType.SOLID,"MaxNumberOfPicks":1}
        definition.propeller is Query;
        annotation {"Name":"Motor inner adapter","Filter":EntityType.BODY && BodyType.SOLID,"MaxNumberOfPicks":1}
        definition.insert is Query;
    }
    { applyStrengthDrive(context,id,definition); },
    {"nozzle":qNothing(),"propeller":qNothing(),"insert":qNothing()});


// M4 through-bolt conversion uses the native hole feature; this adds nut seats.
function applyBoltSeats(context is Context, id is Id, definition is map)
{
    var centers=[vector(-10,-5),vector(-10,5),vector(10,-5),vector(10,5)];
    var seatPlane=plane(vector(0,0,-46.8)*millimeter,vector(0,0,1),vector(1,0,0));
    var profile=newSketchOnPlane(context,id+"nutProfiles",{"sketchPlane":seatPlane});
    var radius=7.4/sqrt(3);
    for(var i=0;i<4;i+=1)
        for(var j=0;j<6;j+=1)
        {
            var a=(30+j*60)*degree;
            var b=(30+((j+1)%6)*60)*degree;
            skLineSegment(profile,"edge"~i~"_"~j,{
                "start":(centers[i]+radius*vector(cos(a),sin(a)))*millimeter,
                "end":(centers[i]+radius*vector(cos(b),sin(b)))*millimeter});
        }
    skSolve(profile);
    opExtrude(context,id+"nutTools",{"entities":qSketchRegion(id+"nutProfiles"),
                "direction":vector(0,0,1),"endBound":BoundingType.BLIND,"endDepth":12*millimeter});
    opBoolean(context,id+"nutSeats",{"tools":qCreatedBy(id+"nutTools",EntityType.BODY),
                "targets":definition.nozzle,"operationType":BooleanOperationType.SUBTRACTION});
    var corners=[];
    for(var e in evaluateQuery(context,qGeometry(qCreatedBy(id+"nutSeats",EntityType.EDGE),GeometryType.LINE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(b.maxCorner[0]-b.minCorner[0]<1e-5*millimeter &&
           b.maxCorner[1]-b.minCorner[1]<1e-5*millimeter &&
           b.maxCorner[2]-b.minCorner[2]>1*millimeter) corners=append(corners,e);
    }
    if(size(corners)>0) checkedFillet(context,id+"nutCornerRounds",{"entities":qUnion(corners),"radius":0.15*millimeter});
    var mouths=[];
    var rim=[];
    for(var e in evaluateQuery(context,qOwnedByBody(definition.nozzle,EntityType.EDGE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(abs(b.minCorner[2]+50.795543309729*millimeter)<1e-5*millimeter &&
           abs(b.maxCorner[2]+50.795543309729*millimeter)<1e-5*millimeter)
        {
            var length=evLength(context,{"entities":e});
            if(abs(b.maxCorner[0]-b.minCorner[0]-4.5*millimeter)<1e-5*millimeter &&
               abs(b.maxCorner[1]-b.minCorner[1]-4.5*millimeter)<1e-5*millimeter) mouths=append(mouths,e);
            if(length>15*millimeter) rim=append(rim,e);
        }
    }
    if(size(mouths)!=8) throw regenError("Set the eight native mounting holes to 4.5 mm clearance, up to next.");
    checkedFillet(context,id+"boltMouthRounds",{"entities":qUnion(mouths),"radius":0.2*millimeter});
    if(size(rim)>0) checkedFillet(context,id+"padPerimeterRounds",{"entities":qUnion(rim),"radius":0.6*millimeter,"tangentPropagation":true});
    opDeleteBodies(context,id+"hideNutProfiles",{"entities":qCreatedBy(id+"nutProfiles",EntityType.BODY)});
}

annotation {"Feature Type Name":"M4 bolt nut seats"}
export const m4BoltSeats=defineFeature(function(context is Context,id is Id,definition is map)
    precondition
    {
        annotation {"Name":"Nozzle with mounting pad","Filter":EntityType.BODY && BodyType.SOLID,"MaxNumberOfPicks":1}
        definition.nozzle is Query;
    }
    {applyBoltSeats(context,id,definition);},{"nozzle":qNothing()});

// Approved repair removes only the ten imported sliver faces inside blade roots.
function applyBladeFinish(context is Context,id is Id,definition is map)
{
    var originalBounds=evBox3d(context,{"topology":definition.propeller,"tight":true});
    var originalVolume=evVolume(context,{"entities":definition.propeller});
    var rootSlivers=[];
    for(var f in evaluateQuery(context,qOwnedByBody(definition.propeller,EntityType.FACE)))
    {
        var b=evBox3d(context,{"topology":f,"tight":true});
        var zmax=max([abs(b.minCorner[2]),abs(b.maxCorner[2])]);
        var xmax=max([abs(b.minCorner[0]),abs(b.maxCorner[0])]);
        if(zmax>15*millimeter && zmax<18.01*millimeter && xmax<10*millimeter &&
           b.minCorner[1]>4*millimeter && b.maxCorner[1]<13*millimeter && evArea(context,{"entities":f})<20*millimeter^2)
            rootSlivers=append(rootSlivers,f);
    }
    if(size(rootSlivers)!=10) throw regenError("Expected the ten original imported blade-root sliver faces.");
    opDeleteFace(context,id+"healBladeRoots",{"deleteFaces":qUnion(rootSlivers),"includeFillet":false,"capVoid":false,"leaveOpen":false});
    var roots=[];
    for(var e in evaluateQuery(context,qEdgeConvexityTypeFilter(qOwnedByBody(definition.propeller,EntityType.EDGE),EdgeConvexityType.CONCAVE)))
    {
        var p=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
        if(abs(norm(vector(p[0],0*millimeter,p[2]))-18*millimeter)<0.05*millimeter &&
           p[1]>3*millimeter && p[1]<14*millimeter) roots=append(roots,e);
    }
    if(size(roots)>0) checkedFillet(context,id+"bladeRootRounds",{"entities":qUnion(roots),
        "radius":definition.rootRadius,"tangentPropagation":true,"smoothCorners":true});
    var edges=[];
    for(var e in evaluateQuery(context,qEdgeConvexityTypeFilter(qOwnedByBody(definition.propeller,EntityType.EDGE),EdgeConvexityType.CONVEX)))
    {
        var p=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(norm(vector(p[0],0*millimeter,p[2]))>18.2*millimeter &&
           b.maxCorner[2]-b.minCorner[2]>10*millimeter) edges=append(edges,e);
    }
    if(size(edges)>0) opFillet(context,id+"bladeEdgeRounds",{"entities":qUnion(edges),
        "radius":definition.edgeRadius,"tangentPropagation":false,"smoothCorners":true});
    var tips=[];
    for(var e in evaluateQuery(context,qEdgeConvexityTypeFilter(qOwnedByBody(definition.propeller,EntityType.EDGE),EdgeConvexityType.CONVEX)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(b.maxCorner[2]-b.minCorner[2]<1e-5*millimeter &&
           abs(abs(b.minCorner[2])-36*millimeter)<1e-5*millimeter &&
           evLength(context,{"entities":e})>0.5*millimeter) tips=append(tips,e);
    }
    if(size(tips)>0) checkedFillet(context,id+"bladeTipRounds",{"entities":qUnion(tips),
        "radius":definition.edgeRadius,"tangentPropagation":true,"smoothCorners":true});
    var finalBounds=evBox3d(context,{"topology":definition.propeller,"tight":true});
    if(norm(finalBounds.minCorner-originalBounds.minCorner)>0.1*millimeter ||
       norm(finalBounds.maxCorner-originalBounds.maxCorner)>0.1*millimeter ||
       abs(evVolume(context,{"entities":definition.propeller})-originalVolume)>0.05*originalVolume)
        throw regenError("Blade repair exceeded its protected envelope or material limit.");
}

annotation {"Feature Type Name":"Repaired blade rounds"}
export const repairedBladeRounds=defineFeature(function(context is Context,id is Id,definition is map)
    precondition
    {
        annotation {"Name":"Propeller","Filter":EntityType.BODY && BodyType.SOLID,"MaxNumberOfPicks":1}
        definition.propeller is Query;
        annotation {"Name":"Blade root radius"}
        isLength(definition.rootRadius,{(millimeter):[0.1,0.4,0.8]} as LengthBoundSpec);
        annotation {"Name":"Blade edge radius"}
        isLength(definition.edgeRadius,{(millimeter):[0.03,0.1,0.25]} as LengthBoundSpec);
    }
    {applyBladeFinish(context,id,definition);},
    {"propeller":qNothing(),"rootRadius":0.4*millimeter,"edgeRadius":0.1*millimeter});

// Kit-matched nominal hardware; thread helices are omitted for assembly speed.
// Solid shafts use major diameter, so contact with insert pilots is intentional.
function hexPrism(context is Context,id is Id,origin is Vector,axis is Vector,af is ValueWithUnits,height is ValueWithUnits)
{
    var xdir=vector(1,0,0);
    if(abs(axis[0])>0.9) xdir=vector(0,1,0);
    var sketch=newSketchOnPlane(context,id+"profile",{"sketchPlane":plane(origin,axis,xdir)});
    for(var j=0;j<6;j+=1)
    {
        var a=(30+j*60)*degree;
        var b=(30+((j+1)%6)*60)*degree;
        skLineSegment(sketch,"side"~j,{"start":af/sqrt(3)*vector(cos(a),sin(a)),"end":af/sqrt(3)*vector(cos(b),sin(b))});
    }
    skSolve(sketch);
    opExtrude(context,id+"solid",{"entities":qSketchRegion(id+"profile"),"direction":axis,"endBound":BoundingType.BLIND,"endDepth":height});
    opDeleteBodies(context,id+"cleanup",{"entities":qCreatedBy(id+"profile",EntityType.BODY)});
    return qCreatedBy(id+"solid",EntityType.BODY);
}

function kitCapScrew(context is Context,id is Id,seat is Vector,axis is Vector,d is ValueWithUnits,length is ValueWithUnits,headDiameter is ValueWithUnits,key is ValueWithUnits,label is string)
{
    fCylinder(context,id+"head",{"bottomCenter":seat-axis*d,"topCenter":seat,"radius":headDiameter/2});
    fCylinder(context,id+"shaft",{"bottomCenter":seat,"topCenter":seat+axis*length,"radius":d/2});
    opBoolean(context,id+"join",{"tools":qUnion([qCreatedBy(id+"head",EntityType.BODY),qCreatedBy(id+"shaft",EntityType.BODY)]),"operationType":BooleanOperationType.UNION});
    var screw=qCreatedBy(id+"head",EntityType.BODY);
    var rim=[];
    for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(screw,EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        var mid=(b.minCorner+b.maxCorner)/2;
        if(norm(mid-(seat-axis*d))<0.01*millimeter) rim=append(rim,e);
    }
    if(size(rim)>0) checkedFillet(context,id+"headRound",{"entities":qUnion(rim),"radius":0.15*millimeter});
    var socket=hexPrism(context,id+"socket",seat-axis*(d+0.01*millimeter),axis,key,d*0.5+0.01*millimeter);
    opBoolean(context,id+"drive",{"tools":socket,"targets":screw,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":screw,"propertyType":PropertyType.NAME,"value":label});
    setProperty(context,{"entities":screw,"propertyType":PropertyType.APPEARANCE,"value":color(0.18,0.19,0.20)});
}

annotation {"Feature Type Name":"Kit M3x8 screw seats"}
export const kitM3Seats=defineFeature(function(context is Context,id is Id,definition is map)
    precondition
    {
        annotation {"Name":"Propeller","Filter":EntityType.BODY && BodyType.SOLID,"MaxNumberOfPicks":1}
        definition.propeller is Query;
    }
    {
        var axes=[vector(9,0,0),vector(0,0,9),vector(-9,0,0),vector(0,0,-9)];
        var cuts=[];
        for(var i=0;i<4;i+=1)
        {
            fCylinder(context,id+("head"~i),{"bottomCenter":(axes[i]+vector(0,15,0))*millimeter,"topCenter":(axes[i]+vector(0,16.11,0))*millimeter,"radius":3*millimeter});
            cuts=append(cuts,qCreatedBy(id+("head"~i),EntityType.BODY));
        }
        opBoolean(context,id+"deeperSeats",{"tools":qUnion(cuts),"targets":definition.propeller,"operationType":BooleanOperationType.SUBTRACTION});
        var bearingRims=[];
        for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(definition.propeller,EntityType.EDGE),GeometryType.CIRCLE)))
        {
            var b=evBox3d(context,{"topology":e,"tight":true});
            if(abs(b.minCorner[1]-15*millimeter)<1e-5*millimeter && abs(b.maxCorner[1]-15*millimeter)<1e-5*millimeter)
                bearingRims=append(bearingRims,e);
        }
        if(size(bearingRims)!=8) throw regenError("Expected four head seats and four shaft openings at Y=15 mm.");
        checkedFillet(context,id+"seatRelief",{"entities":qUnion(bearingRims),"radius":0.1*millimeter});
    },{"propeller":qNothing()});

annotation {"Feature Type Name":"Fgruh kit hardware"}
export const fgruhKitHardware=defineFeature(function(context is Context,id is Id,definition is map)
    precondition {}
    {
        var axes=[vector(9,0,0),vector(0,0,9),vector(-9,0,0),vector(0,0,-9)];
        for(var i=0;i<4;i+=1)
            kitCapScrew(context,id+("prop"~i),(axes[i]+vector(0,15,0))*millimeter,vector(0,-1,0),3*millimeter,8*millimeter,5.68*millimeter,2.5*millimeter,"M3x8 socket propeller screw "~(i+1));
        var corners=[vector(-10,-5,0),vector(-10,5,0),vector(10,-5,0),vector(10,5,0)];
        for(var i=0;i<4;i+=1)
        {
            var center=corners[i]*millimeter;
            var z=-50.795543309729*millimeter;
            kitCapScrew(context,id+("mount"~i),center+vector(0*millimeter,0*millimeter,z-0.8*millimeter),vector(0,0,1),4*millimeter,12*millimeter,7.22*millimeter,3*millimeter,"M4x12 socket mounting bolt "~(i+1));
            fCylinder(context,id+("washer"~i),{"bottomCenter":center+vector(0*millimeter,0*millimeter,z-0.8*millimeter),"topCenter":center+vector(0*millimeter,0*millimeter,z),"radius":4.5*millimeter});
            var washer=qCreatedBy(id+("washer"~i),EntityType.BODY);
            fCylinder(context,id+("washerBore"~i),{"bottomCenter":center+vector(0*millimeter,0*millimeter,z-0.81*millimeter),"topCenter":center+vector(0*millimeter,0*millimeter,z+0.01*millimeter),"radius":2.15*millimeter});
            opBoolean(context,id+("washerCut"~i),{"tools":qCreatedBy(id+("washerBore"~i),EntityType.BODY),"targets":washer,"operationType":BooleanOperationType.SUBTRACTION});
            setProperty(context,{"entities":washer,"propertyType":PropertyType.NAME,"value":"M4 flat washer 9x4.3x0.8 - "~(i+1)});
            var nut=hexPrism(context,id+("nut"~i),center+vector(0,0,-46.8)*millimeter,vector(0,0,1),7*millimeter,3.2*millimeter);
            fCylinder(context,id+("nutBore"~i),{"bottomCenter":center+vector(0,0,-46.81)*millimeter,"topCenter":center+vector(0,0,-43.59)*millimeter,"radius":2*millimeter});
            opBoolean(context,id+("nutCut"~i),{"tools":qCreatedBy(id+("nutBore"~i),EntityType.BODY),"targets":nut,"operationType":BooleanOperationType.SUBTRACTION});
            setProperty(context,{"entities":nut,"propertyType":PropertyType.NAME,"value":"M4 hex nut AF7x3.2 - "~(i+1)});
            setProperty(context,{"entities":qUnion([washer,nut]),"propertyType":PropertyType.APPEARANCE,"value":color(0.25,0.26,0.27)});
        }
    },{});

// Approved P1S / PLA Basic assembly completion, 15 October 2026.
// Cover, propeller, insert and motor geometry/placement are protected.
function finalM3Washer(context is Context,id is Id,seat is Vector,axis is Vector,label is string)
{
    fCylinder(context,id+"body",{"bottomCenter":seat,"topCenter":seat+axis*0.5*millimeter,"radius":3.5*millimeter});
    var body=qCreatedBy(id+"body",EntityType.BODY);
    fCylinder(context,id+"bore",{"bottomCenter":seat-axis*0.01*millimeter,"topCenter":seat+axis*0.51*millimeter,"radius":1.6*millimeter});
    opBoolean(context,id+"clear",{"tools":qCreatedBy(id+"bore",EntityType.BODY),"targets":body,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":body,"propertyType":PropertyType.NAME,"value":label});
    setProperty(context,{"entities":body,"propertyType":PropertyType.APPEARANCE,"value":color(0.25,0.26,0.27)});
}

function applyFinalPlaAssembly(context is Context,id is Id,nozzle is Query)
{
    var motorAxes=[vector(9.5,0,0),vector(-9.5,0,0),vector(0,0,8),vector(0,0,-8)];
    var tools=[];
    for(var i=0;i<4;i+=1)
    {
        var sid=id+("motorAccess"~i);
        fCylinder(context,sid,{"bottomCenter":(motorAxes[i]+vector(0,-45,0))*millimeter,
            "topCenter":(motorAxes[i]+vector(0,-16,0))*millimeter,"radius":3.8*millimeter});
        tools=append(tools,qCreatedBy(sid,EntityType.BODY));
    }
    opBoolean(context,id+"motorAccessCut",{"tools":qUnion(tools),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
    var floors=[];
    var mouths=[];
    for(var e in evaluateQuery(context,qCreatedBy(id+"motorAccessCut",EntityType.EDGE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(abs(b.minCorner[1]+16*millimeter)<1e-5*millimeter && abs(b.maxCorner[1]+16*millimeter)<1e-5*millimeter &&
            abs(b.maxCorner[0]-b.minCorner[0]-7.6*millimeter)<1e-5*millimeter)
            floors=append(floors,e);
        if(b.maxCorner[1]<-18*millimeter) mouths=append(mouths,e);
    }
    if(size(floors)!=4) throw regenError("Expected the four motor-base washer seats at Y=-16 mm.");
    checkedFillet(context,id+"motorSeatRounds",{"entities":qUnion(floors),"radius":0.15*millimeter});
    if(size(mouths)>0) checkedFillet(context,id+"motorAccessMouthRounds",{"entities":qUnion(mouths),"radius":0.25*millimeter,"tangentPropagation":true});

    for(var i=0;i<4;i+=1)
    {
        var seat=(motorAxes[i]+vector(0,-16.5,0))*millimeter;
        kitCapScrew(context,id+("motorScrew"~i),seat,vector(0,1,0),3*millimeter,8*millimeter,5.68*millimeter,2.5*millimeter,"M3x8 motor-base screw "~(i+1));
        finalM3Washer(context,id+("motorWasher"~i),seat,vector(0,1,0),"M3 flat washer motor base "~(i+1));
    }
    var directions=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1),vector(1,0,0)];
    for(var i=0;i<4;i+=1)
    {
        var d=directions[i];
        var c=d*44.5*millimeter;
        var seat=c+vector(0,24.5,0)*millimeter;
        var axis=vector(0,-1,0);
        kitCapScrew(context,id+("coverScrew"~i),seat,axis,3*millimeter,12*millimeter,5.68*millimeter,2.5*millimeter,"M3x12 cover through-bolt "~(i+1));
        finalM3Washer(context,id+("coverWasher"~i),seat,axis,"M3 front washer cover "~(i+1));
        finalM3Washer(context,id+("coverRearWasher"~i),c+vector(0,15.5,0)*millimeter,vector(0,1,0),"M3 rear washer cover "~(i+1));
        var nut=hexPrism(context,id+("coverNut"~i),c+vector(0,15.5,0)*millimeter,axis,5.5*millimeter,2.4*millimeter);
        if(abs(d[0])>0.9) opTransform(context,id+("coverNutOrient"~i),{"bodies":nut,"transform":rotationAround(line(c,vector(0,1,0)),90*degree)});
        fCylinder(context,id+("coverNutBore"~i),{"bottomCenter":c+vector(0,15.51,0)*millimeter,
            "topCenter":c+vector(0,13.09,0)*millimeter,"radius":1.5*millimeter});
        opBoolean(context,id+("coverNutClear"~i),{"tools":qCreatedBy(id+("coverNutBore"~i),EntityType.BODY),"targets":nut,"operationType":BooleanOperationType.SUBTRACTION});
        setProperty(context,{"entities":nut,"propertyType":PropertyType.NAME,"value":"M3 captured cover nut "~(i+1)});
        setProperty(context,{"entities":nut,"propertyType":PropertyType.APPEARANCE,"value":color(0.25,0.26,0.27)});
    }
}


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


// R4: four actual axial clamping joints. Approved cover-tab changes only.
function applyCoverThroughJoints(context is Context,id is Id,nozzle is Query)
{
    var covers=[];
    for(var b in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var bounds=evBox3d(context,{"topology":b,"tight":true});
        if(bounds.maxCorner[0]-bounds.minCorner[0]>80*millimeter && bounds.minCorner[1]>10*millimeter) covers=append(covers,b);
    }
    if(size(covers)!=1) throw regenError("Expected one original front cover.");
    var cover=qUnion(covers);
    var directions=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1),vector(1,0,0)];
    for(var i=0;i<4;i+=1)
    {
        var sid=id+("joint"~i);
        var d=directions[i];
        var c=d*44.5*millimeter;
        fCylinder(context,sid+"ear",{"bottomCenter":c+vector(0,19,0)*millimeter,"topCenter":c+vector(0,24,0)*millimeter,"radius":5*millimeter});
        var ear=qCreatedBy(sid+"ear",EntityType.BODY);
        checkedFillet(context,sid+"earRounds",{"entities":qGeometry(qOwnedByBody(ear,EntityType.EDGE),GeometryType.CIRCLE),"radius":0.6*millimeter});
        opBoolean(context,sid+"earJoin",{"tools":qUnion([cover,ear]),"operationType":BooleanOperationType.UNION});
        // Original imported feet extend about 1 mm behind the new datum.
        // Trim only the local feet to the same flat clamping plane.
        fCylinder(context,sid+"backSpotFace",{"bottomCenter":c+vector(0,16,0)*millimeter,"topCenter":c+vector(0,19,0)*millimeter,"radius":6.8*millimeter});
        opBoolean(context,sid+"backFaceCut",{"tools":qCreatedBy(sid+"backSpotFace",EntityType.BODY),"targets":cover,"operationType":BooleanOperationType.SUBTRACTION});
        fCylinder(context,sid+"flange",{"bottomCenter":c+vector(0,12.5,0)*millimeter,"topCenter":c+vector(0,19,0)*millimeter,"radius":5*millimeter});
        var flange=qCreatedBy(sid+"flange",EntityType.BODY);
        checkedFillet(context,sid+"flangeRounds",{"entities":qGeometry(qOwnedByBody(flange,EntityType.EDGE),GeometryType.CIRCLE),"radius":0.5*millimeter});
        opBoolean(context,sid+"flangeJoin",{"tools":qUnion([nozzle,flange]),"operationType":BooleanOperationType.UNION});
        fCylinder(context,sid+"earSocket",{"bottomCenter":c+vector(0,19,0)*millimeter,"topCenter":c+vector(0,31,0)*millimeter,"radius":6.8*millimeter});
        opBoolean(context,sid+"socketCut",{"tools":qCreatedBy(sid+"earSocket",EntityType.BODY),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
        // Nut T-slot: loading from the duct interior, hex flats stop rotation.
        var hex=hexPrism(context,sid+"nutSlot",c+vector(0,12.8,0)*millimeter,vector(0,1,0),5.9*millimeter,2.8*millimeter);
        if(abs(d[0])>0.9) opTransform(context,sid+"nutSlotOrient",{"bodies":hex,"transform":rotationAround(line(c,vector(0,1,0)),90*degree)});
        var turn=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),i*90*degree);
        // d follows +Z,-X,-Z,+X; positive rotation maps +Z to +X.
        turn=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),-i*90*degree);
        fCuboid(context,sid+"nutEntry",{"corner1":vector(-2.95,12.8,34)*millimeter,"corner2":vector(2.95,15.6,44.5)*millimeter});
        var entry=qCreatedBy(sid+"nutEntry",EntityType.BODY);
        opTransform(context,sid+"entryOrient",{"bodies":entry,"transform":turn});
        fCylinder(context,sid+"rearWasherSeat",{"bottomCenter":c+vector(0,15.3,0)*millimeter,"topCenter":c+vector(0,16,0)*millimeter,"radius":3.7*millimeter});
        fCuboid(context,sid+"washerEntry",{"corner1":vector(-3.7,15.3,34)*millimeter,"corner2":vector(3.7,16,44.5)*millimeter});
        var we=qCreatedBy(sid+"washerEntry",EntityType.BODY);
        opTransform(context,sid+"washerEntryOrient",{"bodies":we,"transform":turn});
        opBoolean(context,sid+"pocketCuts",{"tools":qUnion([hex,entry,qCreatedBy(sid+"rearWasherSeat",EntityType.BODY),we]),"targets":nozzle,"operationType":BooleanOperationType.SUBTRACTION});
        // A front spot-face guarantees a flat washer seat on the curved arm.
        fCylinder(context,sid+"frontSpotFace",{"bottomCenter":c+vector(0,24,0)*millimeter,"topCenter":c+vector(0,65,0)*millimeter,"radius":3.7*millimeter});
        opBoolean(context,sid+"frontFaceCut",{"tools":qCreatedBy(sid+"frontSpotFace",EntityType.BODY),"targets":cover,"operationType":BooleanOperationType.SUBTRACTION});
        fCylinder(context,sid+"clearBore",{"bottomCenter":c+vector(0,12,0)*millimeter,"topCenter":c+vector(0,25,0)*millimeter,"radius":1.7*millimeter});
        opBoolean(context,sid+"throughCut",{"tools":qCreatedBy(sid+"clearBore",EntityType.BODY),"targets":qUnion([cover,nozzle]),"operationType":BooleanOperationType.SUBTRACTION});
        var mouths=[];
        for(var e in evaluateQuery(context,qGeometry(qOwnedByBody(qUnion([cover,nozzle]),EntityType.EDGE),GeometryType.CIRCLE)))
        {
            var bounds=evBox3d(context,{"topology":e,"tight":true});
            var mid=(bounds.minCorner+bounds.maxCorner)/2;
            if(norm(vector(mid[0],0*millimeter,mid[2])-c)<1e-5*millimeter && abs(bounds.maxCorner[0]-bounds.minCorner[0]-3.4*millimeter)<1e-5*millimeter && abs(bounds.maxCorner[1]-bounds.minCorner[1])<1e-5*millimeter &&
                (abs(bounds.minCorner[1]-24*millimeter)<1e-5*millimeter || abs(bounds.minCorner[1]-19*millimeter)<1e-5*millimeter || abs(bounds.minCorner[1]-16*millimeter)<1e-5*millimeter)) mouths=append(mouths,e);
        }
        // Coincident cover/nozzle circles at the clamping plane may share one
        // query identity. The exported bearing and bore gauges check both parts.
        if(size(mouths)<3 || size(mouths)>4) throw regenError("Expected M3 mouths at three axial planes at joint "~i~", found "~size(mouths));
        checkedFillet(context,sid+"boreRounds",{"entities":qUnion(mouths),"radius":0.2*millimeter,"tangentPropagation":false});
    }
    if(size(evaluateQuery(context,cover))!=1 || size(evaluateQuery(context,nozzle))!=1) throw regenError("Cover and nozzle must remain separate connected parts.");
    setProperty(context,{"entities":cover,"propertyType":PropertyType.NAME,"value":"Front cover - four M3 through-bolt tabs (R4)"});
    setProperty(context,{"entities":nozzle,"propertyType":PropertyType.NAME,"value":"Nozzle - M3 captive nut joints and motor cup (R4)"});
}



// Finish the three pads generated by the native 4-instance circular pattern.
// Source pattern: Extrude 1 + 4.5 mm clearance Hole, Reapply features=true.
annotation {"Feature Type Name":"Four side mount finishing"}
export const fourSideMountFinish=defineFeature(function(context is Context,id is Id,definition is map)
    precondition
    {
        annotation {"Name":"Nozzle with four mounting pads","Filter":EntityType.BODY && BodyType.SOLID,"MaxNumberOfPicks":1}
        definition.nozzle is Query;
    }
    {
        var centers=[vector(-10,-5),vector(-10,5),vector(10,-5),vector(10,5)];
        for(var k=1;k<4;k+=1)
        {
            var sid=id+("side"~k);
            var turn=rotationAround(line(vector(0,0,0)*millimeter,vector(0,1,0)),k*90*degree);
            var normal=turn.linear*vector(0,0,1);
            var xdir=turn.linear*vector(1,0,0);
            var profile=newSketchOnPlane(context,sid+"nutProfiles",{"sketchPlane":plane(turn*(vector(0,0,-46.8)*millimeter),normal,xdir)});
            for(var i=0;i<4;i+=1)
                for(var j=0;j<6;j+=1)
                {
                    var a=(30+j*60)*degree;
                    var b=(30+((j+1)%6)*60)*degree;
                    skLineSegment(profile,"edge"~i~"_"~j,{
                        "start":(centers[i]+7.4/sqrt(3)*vector(cos(a),sin(a)))*millimeter,
                        "end":(centers[i]+7.4/sqrt(3)*vector(cos(b),sin(b)))*millimeter});
                }
            skSolve(profile);
            opExtrude(context,sid+"nutTools",{"entities":qSketchRegion(sid+"nutProfiles"),"direction":normal,"endBound":BoundingType.BLIND,"endDepth":12*millimeter});
            opBoolean(context,sid+"nutSeats",{"tools":qCreatedBy(sid+"nutTools",EntityType.BODY),"targets":definition.nozzle,"operationType":BooleanOperationType.SUBTRACTION});
            var corners=[];
            for(var e in evaluateQuery(context,qGeometry(qCreatedBy(sid+"nutSeats",EntityType.EDGE),GeometryType.LINE)))
            {
                var tangent=evEdgeTangentLine(context,{"edge":e,"parameter":0.5});
                if(abs(dot(tangent.direction,normal))>0.99999 && evLength(context,{"entities":e})>1*millimeter) corners=append(corners,e);
            }
            if(size(corners)==0) throw regenError("No new nut pocket corners found on side "~k);
            checkedFillet(context,sid+"nutCornerRounds",{"entities":qUnion(corners),"radius":0.15*millimeter});
            var mouths=[];
            var rim=[];
            var undo=inverse(turn);
            for(var e in evaluateQuery(context,qOwnedByBody(definition.nozzle,EntityType.EDGE)))
            {
                var bounds=evBox3d(context,{"topology":e,"tight":true});
                var a=undo*bounds.minCorner;
                var b=undo*bounds.maxCorner;
                if(abs(a[2]+50.795543309729*millimeter)<1e-5*millimeter && abs(b[2]+50.795543309729*millimeter)<1e-5*millimeter)
                {
                    var span=bounds.maxCorner-bounds.minCorner;
                    if(abs(max([span[0],span[1],span[2]])-4.5*millimeter)<1e-5*millimeter) mouths=append(mouths,e);
                    if(evLength(context,{"entities":e})>15*millimeter) rim=append(rim,e);
                }
            }
            if(size(mouths)!=8 || size(rim)!=4) throw regenError("Expected eight clearance holes and a capsule rim on side "~k);
            checkedFillet(context,sid+"boltMouthRounds",{"entities":qUnion(mouths),"radius":0.2*millimeter});
            checkedFillet(context,sid+"padPerimeterRounds",{"entities":qUnion(rim),"radius":0.6*millimeter,"tangentPropagation":true});
            opDeleteBodies(context,sid+"hideNutProfiles",{"entities":qCreatedBy(sid+"nutProfiles",EntityType.BODY)});
        }
        applyFinalPlaAssembly(context,id+"finalPla",definition.nozzle);
        applyPhysicalPrintRevision(context,id+"physicalPrint",definition.nozzle);
        applyMotorCenteringCup(context,id+"centeringCup",definition.nozzle);
        applyCoverThroughJoints(context,id+"throughJoints",definition.nozzle);
    },{"nozzle":qNothing()});


