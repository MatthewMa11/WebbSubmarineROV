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

    // R5: both the old side collar and rear wire-holder ring are omitted.

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
        var seat=c+vector(0,52.5,0)*millimeter;
        var axis=vector(0,-1,0);
        kitCapScrew(context,id+("coverScrew"~i),seat,axis,3*millimeter,40*millimeter,5.68*millimeter,2.5*millimeter,"M3x40 cover-extension through-bolt "~(i+1));
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
    // R5: no rear wire-holder ring or added ring posts.
    if(size(evaluateQuery(context,nozzle))!=1) throw regenError("Nozzle must remain one connected body.");
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
    setProperty(context,{"entities":nozzle,"propertyType":PropertyType.NAME,"value":"Nozzle - permanent motor centering cup, no wire holder"});
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
    setProperty(context,{"entities":nozzle,"propertyType":PropertyType.NAME,"value":"Nozzle - M3 captive nut joints and motor cup, no wire holder (R5)"});
}



// Finish the three pads generated by the native 4-instance circular pattern.
// Source pattern: Extrude 1 + 4.5 mm clearance Hole, Reapply features=true.
// R6: external motor-bell retention. No printed insert inside the rotor.
// Four original drive keys carry torque; opposed clamp screws retain axially.
// R8: two-jaw external axle retention. Four existing keys carry drive torque.
// Reference shaft is 3.175 mm. Physical shaft fit and retention require testing.
function r8Boolean(context is Context,id is Id,definition is map)
{
    try { opBoolean(context,id,definition); }
    catch(error) { throw regenError("R8 Boolean failed: "~id[size(id)-1]); }
}

function r8Box(context is Context,id is Id,a is Vector,b is Vector)
{
    fCuboid(context,id+"box",{"corner1":a*millimeter,"corner2":b*millimeter});
    var body=qCreatedBy(id+"box",EntityType.BODY);
    checkedFillet(context,id+"rounds",{"entities":qOwnedByBody(body,EntityType.EDGE),"radius":0.4*millimeter});
    return body;
}

function r8Nut(context is Context,id is Id,x is number,axis is Vector,z is number,label is string)
{
    // Flat sides face fore/aft: 5.5 mm Y width leaves clearance to the cap.
    var seat=vector(x,15.8,z)*millimeter;
    var sketch=newSketchOnPlane(context,id+"profile",{"sketchPlane":plane(seat,axis,vector(1,0,0))});
    for(var j=0;j<6;j+=1)
    {
        var a=j*60*degree;var b=((j+1)%6)*60*degree;
        skLineSegment(sketch,"side"~j,{"start":5.5/sqrt(3)*vector(cos(a),sin(a))*millimeter,"end":5.5/sqrt(3)*vector(cos(b),sin(b))*millimeter});
    }
    skSolve(sketch);
    opExtrude(context,id+"solid",{"entities":qSketchRegion(id+"profile"),"direction":axis,"endBound":BoundingType.BLIND,"endDepth":2.4*millimeter});
    var nut=qCreatedBy(id+"solid",EntityType.BODY);
    opDeleteBodies(context,id+"cleanup",{"entities":qCreatedBy(id+"profile",EntityType.BODY)});
    fCylinder(context,id+"bore",{"bottomCenter":seat-axis*0.01*millimeter,"topCenter":seat+axis*2.41*millimeter,"radius":1.5*millimeter});
    r8Boolean(context,id+"boreCut",{"tools":qCreatedBy(id+"bore",EntityType.BODY),"targets":nut,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":nut,"propertyType":PropertyType.NAME,"value":label});
    setProperty(context,{"entities":nut,"propertyType":PropertyType.APPEARANCE,"value":color(0.25,0.26,0.27)});
}

function r8BuildAxleClamp(context is Context,id is Id,originalProp is Query)
{
    setAttribute(context,{"entities":originalProp,"name":"r8Role","attribute":{"role":"fan"}});
    var fan=qHasAttributeWithValueMatching(qAllModifiableSolidBodies(),"r8Role",{"role":"fan"});
    var lower=[r8Box(context,id+"lowerBridge",vector(-20.8,14.2,-6.2),vector(20.8,19.3,6.2))];
    for(var i=0;i<2;i+=1)
    {
        var x=(i==0 ? -20.8 : 13.2);
        lower=append(lower,r8Box(context,id+("lowerEar"~i),vector(x,12.2,-6.2),vector(x+7.6,19.3,6.2)));
    }
    r8Boolean(context,id+"lowerJoin",{"tools":qUnion([fan,qUnion(lower)]),"operationType":BooleanOperationType.UNION});
    // Leave the original key roots supported by a 0.95 mm backing plate.
    var seats=[];
    fCuboid(context,id+"bridgeSeat",{"corner1":vector(-13.8,15.15,0)*millimeter,"corner2":vector(13.8,19.7,6.45)*millimeter});
    seats=append(seats,qCreatedBy(id+"bridgeSeat",EntityType.BODY));
    for(var i=0;i<2;i+=1)
    {
        var x=(i==0 ? -21.05 : 13.0);
        fCuboid(context,id+("earSeat"~i),{"corner1":vector(x,12.0,0)*millimeter,"corner2":vector(x+8.05,19.7,6.45)*millimeter});
        seats=append(seats,qCreatedBy(id+("earSeat"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"seatCut",{"tools":qUnion(seats),"targets":fan,"operationType":BooleanOperationType.SUBTRACTION});

    var upper=r8Box(context,id+"upperBridge",vector(-13.5,15.4,0.3),vector(13.5,19.3,6.2));
    setAttribute(context,{"entities":upper,"name":"r8Role","attribute":{"role":"jaw"}});
    var jaw=qHasAttributeWithValueMatching(qAllModifiableSolidBodies(),"r8Role",{"role":"jaw"});
    var ears=[];
    for(var i=0;i<2;i+=1)
    {
        var x=(i==0 ? -20.8 : 13.2);
        ears=append(ears,r8Box(context,id+("upperEar"~i),vector(x,12.2,0.3),vector(x+7.6,19.3,6.2)));
    }
    r8Boolean(context,id+"upperJoin",{"tools":qUnion([jaw,qUnion(ears)]),"operationType":BooleanOperationType.UNION});
    // Every new feature behind the original motor face clears the rotor bell.
    fCylinder(context,id+"bellEnvelope",{"bottomCenter":vector(0,11.9,0)*millimeter,"topCenter":vector(0,14.2,0)*millimeter,"radius":14.25*millimeter});
    var keyKeeps=[];var keyAxes=[vector(9,0,0),vector(-9,0,0),vector(0,0,9),vector(0,0,-9)];
    for(var i=0;i<4;i+=1)
    {
        fCylinder(context,id+("keyKeep"~i),{"bottomCenter":(keyAxes[i]+vector(0,11.8,0))*millimeter,"topCenter":(keyAxes[i]+vector(0,14.3,0))*millimeter,"radius":2.75*millimeter});
        keyKeeps=append(keyKeeps,qCreatedBy(id+("keyKeep"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"preserveKeys",{"tools":qUnion(keyKeeps),"targets":qCreatedBy(id+"bellEnvelope",EntityType.BODY),"operationType":BooleanOperationType.SUBTRACTION});
    r8Boolean(context,id+"bellClear",{"tools":qCreatedBy(id+"bellEnvelope",EntityType.BODY),"targets":qUnion([fan,jaw]),"operationType":BooleanOperationType.SUBTRACTION});
    fCylinder(context,id+"pilotClearance",{"bottomCenter":vector(0,11.8,0)*millimeter,"topCenter":vector(0,16.25,0)*millimeter,"radius":4.8*millimeter});
    fCylinder(context,id+"axleBore",{"bottomCenter":vector(0,16.24,0)*millimeter,"topCenter":vector(0,19.7,0)*millimeter,"radius":1.65*millimeter});
    r8Boolean(context,id+"centerBores",{"tools":qUnion([qCreatedBy(id+"pilotClearance",EntityType.BODY),qCreatedBy(id+"axleBore",EntityType.BODY)]),"targets":qUnion([fan,jaw]),"operationType":BooleanOperationType.SUBTRACTION});

    for(var i=0;i<2;i+=1)
    {
        var sid=id+("hardware"~i);var x=(i==0 ? 16.8 : -16.8);
        fCylinder(context,sid+"through",{"bottomCenter":vector(x,15.8,-12)*millimeter,"topCenter":vector(x,15.8,12)*millimeter,"radius":1.7*millimeter});
        r8Boolean(context,sid+"boltClear",{"tools":qCreatedBy(sid+"through",EntityType.BODY),"targets":qUnion([fan,jaw]),"operationType":BooleanOperationType.SUBTRACTION});
        // Open clearance above and below each bearing face for head, nut and tool.
        var outside=[];
        for(var k=0;k<2;k+=1)
        {
            var za=(k==0 ? 6.2 : -30);var zb=(k==0 ? 30 : -6.2);
            fCylinder(context,sid+("outside"~k),{"bottomCenter":vector(x,15.8,za)*millimeter,"topCenter":vector(x,15.8,zb)*millimeter,"radius":4.3*millimeter});
            outside=append(outside,qCreatedBy(sid+("outside"~k),EntityType.BODY));
        }
        r8Boolean(context,sid+"toolAccess",{"tools":qUnion(outside),"targets":fan,"operationType":BooleanOperationType.SUBTRACTION});
        var dir=(i==0 ? -1 : 1);var axis=vector(0,0,dir);
        kitCapScrew(context,sid+"bolt",vector(x,15.8,-dir*6.2)*millimeter,axis,3*millimeter,16*millimeter,5.68*millimeter,2.5*millimeter,"R8 M3x16 axle clamp bolt "~(i+1));
        r8Nut(context,sid+"nut",x,axis,dir*6.2,"R8 M3 axle clamp nut AF5.5x2.4 - "~(i+1));
    }
    if(size(evaluateQuery(context,fan))!=1 || size(evaluateQuery(context,jaw))!=1) throw regenError("R8 fan and removable jaw must each be one connected body.");
    setProperty(context,{"entities":fan,"propertyType":PropertyType.NAME,"value":"R9 forward fan - flat hub, M3 axle clamp, four drive keys"});
    setProperty(context,{"entities":jaw,"propertyType":PropertyType.NAME,"value":"R8 removable axle clamp upper jaw - 3.175 mm shaft"});
    setProperty(context,{"entities":jaw,"propertyType":PropertyType.APPEARANCE,"value":color(0.56,0.72,0.81)});
}

// R9: user's side sketch -- fixed cap, forward fan, motor, rear support.
// Pattern copy uses native opPattern; source remains the assembly's fan body.
function r9ForwardFan(context is Context,id is Id,prop is Query)
{
    opPattern(context,id+"bladeCopy",{"entities":prop,"transforms":[identityTransform()],"instanceNames":["outerBlades"],"copyPropertiesAndAttributes":false});
    var blades=qCreatedBy(id+"bladeCopy",EntityType.BODY);
    setAttribute(context,{"entities":blades,"name":"r9Stage","attribute":{"role":"blades"}});
    blades=qHasAttributeWithValueMatching(qAllModifiableSolidBodies(),"r9Stage",{"role":"blades"});
    // Keep the complete outer profiles; every following root cut is bounded
    // inside R26.9 so the blade surfaces beyond R27.01 remain untouched.
    if(size(evaluateQuery(context,blades))!=1) throw regenError("R9 blade copy must be one body before removing its old root.");
    fCylinder(context,id+"oldRootTool",{"bottomCenter":vector(0,-4,0)*millimeter,"topCenter":vector(0,19.4,0)*millimeter,"radius":19*millimeter});
    r8Boolean(context,id+"bladeRootCut",{"tools":qCreatedBy(id+"oldRootTool",EntityType.BODY),"targets":blades,"operationType":BooleanOperationType.SUBTRACTION});
    if(size(evaluateQuery(context,blades))!=2) throw regenError("R9 expects exactly two outer blade bodies.");
    // Taper only the inner root's forward edge, retaining the complete outer
    // blade surfaces beyond R27.01. The cap's center remains clear.
    fCone(context,id+"rootFrontTool",{"bottomCenter":vector(0,10,0)*millimeter,"topCenter":vector(0,11.41,0)*millimeter,"bottomRadius":19*millimeter,"topRadius":27.1*millimeter});
    fCylinder(context,id+"rootFrontMask",{"bottomCenter":vector(0,9.99,0)*millimeter,"topCenter":vector(0,11.42,0)*millimeter,"radius":26.9*millimeter});
    r8Boolean(context,id+"rootFrontLimit",{"tools":qUnion([qCreatedBy(id+"rootFrontTool",EntityType.BODY),qCreatedBy(id+"rootFrontMask",EntityType.BODY)]),"operationType":BooleanOperationType.INTERSECTION});
    fCylinder(context,id+"rootFrontBeyond",{"bottomCenter":vector(0,11.4,0)*millimeter,"topCenter":vector(0,19.4,0)*millimeter,"radius":26.9*millimeter});
    fCylinder(context,id+"rootRearTool",{"bottomCenter":vector(0,-4,0)*millimeter,"topCenter":vector(0,5.3,0)*millimeter,"radius":26.9*millimeter});
    r8Boolean(context,id+"taperRootFront",{"tools":qUnion([qCreatedBy(id+"rootFrontLimit",EntityType.BODY),qCreatedBy(id+"rootFrontBeyond",EntityType.BODY),qCreatedBy(id+"rootRearTool",EntityType.BODY)]),"targets":blades,"operationType":BooleanOperationType.SUBTRACTION});
    if(size(evaluateQuery(context,blades))!=2) throw regenError("R9 tapered roots must retain two blade bodies.");
    opTransform(context,id+"forwardBlades",{"bodies":blades,"transform":transform(vector(0,8,0)*millimeter)});

    // Remove the motor-bell cup and old blades; retain all four solid keys.
    fCylinder(context,id+"rearTrimTool",{"bottomCenter":vector(0,-4,0)*millimeter,"topCenter":vector(0,14.2,0)*millimeter,"radius":36*millimeter});
    var trim=qCreatedBy(id+"rearTrimTool",EntityType.BODY);var keeps=[];
    var axes=[vector(9,0,0),vector(-9,0,0),vector(0,0,9),vector(0,0,-9)];
    for(var i=0;i<4;i+=1)
    {
        fCylinder(context,id+("keyKeep"~i),{"bottomCenter":(axes[i]+vector(0,11.49,0))*millimeter,"topCenter":(axes[i]+vector(0,14.3,0))*millimeter,"radius":2.75*millimeter});
        keeps=append(keeps,qCreatedBy(id+("keyKeep"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"preserveDriveKeys",{"tools":qUnion(keeps),"targets":trim,"operationType":BooleanOperationType.SUBTRACTION});
    r8Boolean(context,id+"removeRearCup",{"tools":trim,"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
    if(size(evaluateQuery(context,prop))!=1) throw regenError("R9 flat disk and original drive keys must remain one body.");
    // The old cup is only R18. A flat R20 disk overlaps the R19 blade roots.
    // A 1.4 mm rear rim supplies room for the new root blend. R8's following
    // bell-envelope relief removes its center behind Y14.2, clearing the motor.
    fCylinder(context,id+"flatDisk",{"bottomCenter":vector(0,12.8,0)*millimeter,"topCenter":vector(0,19.3,0)*millimeter,"radius":20*millimeter});
    var disk=qCreatedBy(id+"flatDisk",EntityType.BODY);
    r8Boolean(context,id+"flatDiskJoin",{"tools":qUnion([prop,disk]),"operationType":BooleanOperationType.UNION});
    r8Boolean(context,id+"bladeJoin",{"tools":qUnion([prop,blades]),"operationType":BooleanOperationType.UNION});
    if(size(evaluateQuery(context,qUnion([prop,blades])))!=1) throw regenError("R9 forward blades must join the flat hub.");
    var rootEdges=[];var positiveRoot=false;var negativeRoot=false;
    for(var edge in evaluateQuery(context,qCreatedBy(id+"bladeJoin",EntityType.EDGE)))
    {
        var mid=evEdgeTangentLine(context,{"edge":edge,"parameter":0.5}).origin;
        var radius=sqrt(mid[0]*mid[0]+mid[2]*mid[2]);
        if(abs(radius-20*millimeter)<1e-4*millimeter && mid[1]>13.1*millimeter && mid[1]<19.1*millimeter)
        {
            rootEdges=append(rootEdges,edge);
            if(mid[2]>0*millimeter) positiveRoot=true;
            if(mid[2]<0*millimeter) negativeRoot=true;
        }
    }
    if(!positiveRoot || !negativeRoot) throw regenError("R9 needs intersection edges at both R20 blade roots.");
    var roots=qUnion(rootEdges);
    try { checkedFillet(context,id+"newRootRounds",{"entities":roots,"radius":0.35*millimeter,"tangentPropagation":false}); }
    catch(error)
    {
        var lengths=[];
        for(var edge in evaluateQuery(context,roots)) lengths=append(lengths,evLength(context,{"entities":edge})/millimeter);
        throw regenError("R9 root blend failed; seam lengths mm="~lengths);
    }
    var rims=[];var frontRim=false;var backRim=false;
    for(var edge in evaluateQuery(context,qGeometry(qOwnedByBody(prop,EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var b=evBox3d(context,{"topology":edge,"tight":true});
        var mid=evEdgeTangentLine(context,{"edge":edge,"parameter":0.5}).origin;
        var radius=sqrt(mid[0]*mid[0]+mid[2]*mid[2]);
        if(abs(radius-20*millimeter)<1e-4*millimeter && abs(b.maxCorner[1]-b.minCorner[1])<1e-5*millimeter)
        {
            if(abs(b.minCorner[1]-12.8*millimeter)<1e-5*millimeter) { backRim=true;rims=append(rims,edge); }
            if(abs(b.minCorner[1]-19.3*millimeter)<1e-5*millimeter) { frontRim=true;rims=append(rims,edge); }
        }
    }
    if(!frontRim || !backRim) throw regenError("R9 expects both circular flat-disk perimeter rims.");
    checkedFillet(context,id+"diskRimRounds",{"entities":qUnion(rims),"radius":0.07*millimeter,"tangentPropagation":false});
}

// R10: bought metal CPA-317-N prop adapter. Published outer dimensions only;
// this is a clearance envelope, not a machining model of its collet taper.
function r10ColletFan(context is Context,id is Id,prop is Query)
{
    r9ForwardFan(context,id+"bladeLayout",prop);
    // Discard the obsolete four rotor-vent keys, leaving the flat R9 disk.
    fCylinder(context,id+"oldKeys",{"bottomCenter":vector(0,-5,0)*millimeter,"topCenter":vector(0,12.8,0)*millimeter,"radius":36*millimeter});
    r8Boolean(context,id+"removeKeys",{"tools":qCreatedBy(id+"oldKeys",EntityType.BODY),"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
    fCylinder(context,id+"M6clearance",{"bottomCenter":vector(0,12.7,0)*millimeter,"topCenter":vector(0,19.4,0)*millimeter,"radius":3.1*millimeter});
    r8Boolean(context,id+"clearanceBore",{"tools":qCreatedBy(id+"M6clearance",EntityType.BODY),"targets":prop,"operationType":BooleanOperationType.SUBTRACTION});
    var mouths=[];
    for(var e in evaluateQuery(context,qGeometry(qCreatedBy(id+"clearanceBore",EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var b=evBox3d(context,{"topology":e,"tight":true});
        if(abs(b.maxCorner[0]-b.minCorner[0]-6.2*millimeter)<1e-5*millimeter && abs(b.maxCorner[1]-b.minCorner[1])<1e-5*millimeter) mouths=append(mouths,e);
    }
    if(size(mouths)!=2) throw regenError("R10 needs two 6.2 mm bore mouths.");
    checkedFillet(context,id+"boreLeadIns",{"entities":qUnion(mouths),"radius":0.25*millimeter,"tangentPropagation":false});
    opTransform(context,id+"adapterPlane",{"bodies":prop,"transform":transform(vector(0,11.5,0)*millimeter)});
    setProperty(context,{"entities":prop,"propertyType":PropertyType.NAME,"value":"R10 fan - 6.2 bore, 6.5 flat hub, metal collet"});
    if(size(evaluateQuery(context,prop))!=1) throw regenError("R10 fan must remain a single body.");

    fCylinder(context,id+"adapterBackEnvelope",{"bottomCenter":vector(0,16.3,0)*millimeter,"topCenter":vector(0,24.3,0)*millimeter,"radius":7.75*millimeter});
    var adapter=qCreatedBy(id+"adapterBackEnvelope",EntityType.BODY);
    fCylinder(context,id+"adapterStudEnvelope",{"bottomCenter":vector(0,24.3,0)*millimeter,"topCenter":vector(0,41.3,0)*millimeter,"radius":3*millimeter});
    r8Boolean(context,id+"adapterJoin",{"tools":qUnion([adapter,qCreatedBy(id+"adapterStudEnvelope",EntityType.BODY)]),"operationType":BooleanOperationType.UNION});
    fCylinder(context,id+"shaftInput",{"bottomCenter":vector(0,16.29,0)*millimeter,"topCenter":vector(0,25.6,0)*millimeter,"radius":1.5875*millimeter});
    r8Boolean(context,id+"shaftInputCut",{"tools":qCreatedBy(id+"shaftInput",EntityType.BODY),"targets":adapter,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":adapter,"propertyType":PropertyType.NAME,"value":"BOUGHT CPA-317-N metal collet and backplate - clearance envelope"});
    setProperty(context,{"entities":adapter,"propertyType":PropertyType.APPEARANCE,"value":color(0.68,0.71,0.74)});
    var washer=annularTool(context,id+"propWasher",3.1*millimeter,7.75*millimeter,30.8*millimeter,32.3*millimeter);
    setProperty(context,{"entities":washer,"propertyType":PropertyType.NAME,"value":"BOUGHT CPA-317-N washer - 1.5 mm reference"});
    setProperty(context,{"entities":washer,"propertyType":PropertyType.APPEARANCE,"value":color(0.68,0.71,0.74)});
    var nut=hexPrism(context,id+"propNut",vector(0,32.3,0)*millimeter,vector(0,1,0),10*millimeter,5*millimeter);
    fCylinder(context,id+"nutThreadEnvelope",{"bottomCenter":vector(0,32.29,0)*millimeter,"topCenter":vector(0,37.31,0)*millimeter,"radius":3*millimeter});
    r8Boolean(context,id+"nutClearance",{"tools":qCreatedBy(id+"nutThreadEnvelope",EntityType.BODY),"targets":nut,"operationType":BooleanOperationType.SUBTRACTION});
    setProperty(context,{"entities":nut,"propertyType":PropertyType.NAME,"value":"BOUGHT M6 prop nut - AF10 reference"});
    setProperty(context,{"entities":nut,"propertyType":PropertyType.APPEARANCE,"value":color(0.45,0.47,0.5)});
}

function r10DuctExtension(context is Context,id is Id,nozzle is Query)
{
    var covers=[];
    for(var b in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var r10Bounds=evBox3d(context,{"topology":b,"tight":true});
        if(r10Bounds.maxCorner[0]-r10Bounds.minCorner[0]>80*millimeter && r10Bounds.minCorner[1]>18*millimeter) covers=append(covers,b);
    }
    if(size(covers)!=1) throw regenError("R10 expects the unchanged cap before translation.");
    opTransform(context,id+"moveUnchangedCap",{"bodies":qUnion(covers),"transform":transform(vector(0,28,0)*millimeter)});
    var extension=annularTool(context,id+"duct",38.8*millimeter,43*millimeter,19*millimeter,42*millimeter);
    var ears=[];
    var ds=[vector(0,0,1),vector(-1,0,0),vector(0,0,-1),vector(1,0,0)];
    for(var i=0;i<4;i+=1)
    {
        var c=ds[i]*44.5*millimeter;
        fCylinder(context,id+("ear"~i),{"bottomCenter":c+vector(0,19,0)*millimeter,"topCenter":c+vector(0,47,0)*millimeter,"radius":5*millimeter});
        ears=append(ears,qCreatedBy(id+("ear"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"joinEars",{"tools":qUnion([extension,qUnion(ears)]),"operationType":BooleanOperationType.UNION});
    var endRims=[];
    for(var e in evaluateQuery(context,qOwnedByBody(extension,EntityType.EDGE)))
    {
        var eb=evBox3d(context,{"topology":e,"tight":true});
        if(abs(eb.maxCorner[1]-eb.minCorner[1])<1e-5*millimeter &&
            (abs(eb.minCorner[1]-19*millimeter)<1e-5*millimeter || abs(eb.minCorner[1]-47*millimeter)<1e-5*millimeter)) endRims=append(endRims,e);
    }
    if(size(endRims)<4) throw regenError("R10 expects both extension end perimeters.");
    checkedFillet(context,id+"extensionRounds",{"entities":qUnion(endRims),"radius":0.4*millimeter,"tangentPropagation":false});
    // Match existing front protrusions, with positive print-fit side relief.
    // Enlarge the copied front mating pocket on a 0.4 mm grid spanning
    // +/-0.4 mm in X/Z. The Y19 plane and planar bearing seats stay intact.
    // Discrete-copy relief avoids offsetting fragile imported fillet faces.
    // The original frame and the four planar bearing seats stay untouched.
    opPattern(context,id+"frameCopy",{"entities":nozzle,"transforms":[identityTransform()],"instanceNames":["clearance"],"copyPropertiesAndAttributes":false});
    fCylinder(context,id+"frontMask",{"bottomCenter":vector(0,19,0)*millimeter,"topCenter":vector(0,26,0)*millimeter,"radius":60*millimeter});
    r8Boolean(context,id+"frontClip",{"tools":qUnion([qCreatedBy(id+"frameCopy",EntityType.BODY),qCreatedBy(id+"frontMask",EntityType.BODY)]),"operationType":BooleanOperationType.INTERSECTION});
    var frontCopy=qCreatedBy(id+"frontClip",EntityType.BODY);
    var offsets=[];var copyNames=[];
    for(var ix=-1;ix<=1;ix+=1)
        for(var iz=-1;iz<=1;iz+=1)
        {
            offsets=append(offsets,transform(vector(ix*0.4,0,iz*0.4)*millimeter));
            copyNames=append(copyNames,"clear"~(ix+1)~"_"~(iz+1));
        }
    opPattern(context,id+"relievedCopies",{"entities":frontCopy,"transforms":offsets,"instanceNames":copyNames,"copyPropertiesAndAttributes":false});
    opDeleteBodies(context,id+"removeClipSource",{"entities":frontCopy});
    r8Boolean(context,id+"frameSeat",{"tools":qCreatedBy(id+"relievedCopies",EntityType.BODY),"targets":extension,"operationType":BooleanOperationType.SUBTRACTION});
    // The inherited front lip has thin features at approximately R39,Y19..23.
    // Give the new rear mouth an explicit R40 counterbore and a gentle lead-in
    // to the R38.8 duct bore; preserve all four full R5 bolt-bearing columns.
    fCylinder(context,id+"rearLipRelief",{"bottomCenter":vector(0,18.99,0)*millimeter,"topCenter":vector(0,23.5,0)*millimeter,"radius":40*millimeter});
    var rearRelief=qCreatedBy(id+"rearLipRelief",EntityType.BODY);
    fCone(context,id+"rearLipTaper",{"bottomCenter":vector(0,23.5,0)*millimeter,"topCenter":vector(0,26.5,0)*millimeter,"bottomRadius":40*millimeter,"topRadius":38.8*millimeter});
    r8Boolean(context,id+"lipToolJoin",{"tools":qUnion([rearRelief,qCreatedBy(id+"rearLipTaper",EntityType.BODY)]),"operationType":BooleanOperationType.UNION});
    var bearingKeeps=[];
    for(var i=0;i<4;i+=1)
    {
        var c=ds[i]*44.5*millimeter;
        fCylinder(context,id+("bearingKeep"~i),{"bottomCenter":c+vector(0,18.98,0)*millimeter,"topCenter":c+vector(0,26.51,0)*millimeter,"radius":5*millimeter});
        bearingKeeps=append(bearingKeeps,qCreatedBy(id+("bearingKeep"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"protectBearings",{"tools":qUnion(bearingKeeps),"targets":rearRelief,"operationType":BooleanOperationType.SUBTRACTION});
    r8Boolean(context,id+"rearMouthClearance",{"tools":rearRelief,"targets":extension,"operationType":BooleanOperationType.SUBTRACTION});
    var mouthRims=[];
    for(var e in evaluateQuery(context,qGeometry(qCreatedBy(id+"rearMouthClearance",EntityType.EDGE),GeometryType.CIRCLE)))
    {
        var eb=evBox3d(context,{"topology":e,"tight":true});
        var mid=evEdgeTangentLine(context,{"edge":e,"parameter":0.5}).origin;
        var rr=sqrt(mid[0]*mid[0]+mid[2]*mid[2]);
        if(abs(eb.maxCorner[1]-eb.minCorner[1])<1e-5*millimeter &&
            (abs(rr-40*millimeter)<1e-4*millimeter || abs(rr-38.8*millimeter)<1e-4*millimeter) && evLength(context,{"entities":e})>1*millimeter) mouthRims=append(mouthRims,e);
    }
    if(size(mouthRims)==0) throw regenError("R10 expects the new duct lead-in rims.");
    checkedFillet(context,id+"leadInRounds",{"entities":qUnion(mouthRims),"radius":0.2*millimeter,"tangentPropagation":false});
    var holes=[];
    for(var i=0;i<4;i+=1)
    {
        var c=ds[i]*44.5*millimeter;
        fCylinder(context,id+("boltBore"~i),{"bottomCenter":c+vector(0,18.9,0)*millimeter,"topCenter":c+vector(0,47.1,0)*millimeter,"radius":1.7*millimeter});
        holes=append(holes,qCreatedBy(id+("boltBore"~i),EntityType.BODY));
    }
    r8Boolean(context,id+"throughBoltBores",{"tools":qUnion(holes),"targets":extension,"operationType":BooleanOperationType.SUBTRACTION});
    if(size(evaluateQuery(context,extension))!=1) throw regenError("R10 duct extension must remain one body.");
    setProperty(context,{"entities":extension,"propertyType":PropertyType.NAME,"value":"R10 duct extension - 28 mm, four M3x40 through-bolts"});
    setProperty(context,{"entities":extension,"propertyType":PropertyType.APPEARANCE,"value":color(0.35,0.55,0.68)});
}

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
    opBoolean(context,id+"solidDriveKeys",{"tools":qUnion([prop,qUnion(fills)]),"operationType":BooleanOperationType.UNION});
    r10ColletFan(context,id+"metalCollet",prop);
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
    var nozzles=[];
    for(var b in evaluateQuery(context,qAllModifiableSolidBodies()))
    {
        var r10Bounds=evBox3d(context,{"topology":b,"tight":true});
        if(r10Bounds.minCorner[1]<-29*millimeter && r10Bounds.maxCorner[0]-r10Bounds.minCorner[0]>90*millimeter) nozzles=append(nozzles,b);
    }
    if(size(nozzles)!=1) throw regenError("R10 expects one original frame.");
    r10DuctExtension(context,id+"extension",qUnion(nozzles));
    if(size(evaluateQuery(context,qAllModifiableSolidBodies()))!=45) throw regenError("Expected 45 R10 solids: metal collet reference stack and duct extension.");
}
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
        applyR6SimpleDrive(context,id+"r6SimpleDrive");
        applyFlatRearMotorBoss(context,id+"flatRearBoss",definition.nozzle);
    },{"nozzle":qNothing()});

