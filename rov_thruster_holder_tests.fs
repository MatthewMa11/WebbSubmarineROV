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
annotation { "Feature Type Name" : "HolderGeometryChecks" }
export const holderGeometryChecks = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{
    const before = evaluateQuery(context, qBodyType(qEverything(EntityType.BODY), BodyType.SOLID));
    rovThrusterHolder(context, id + "holder", {});
    const solids = qSubtraction(qBodyType(qEverything(EntityType.BODY), BodyType.SOLID), qUnion(before));
    const count = size(evaluateQuery(context, solids));
    if (count != 1) throw regenError("Expected one connected holder solid, got " ~ count);
    const bounds = evBox3d(context, { "topology" : solids, "tight" : true });
    if (norm(bounds.minCorner - vector(-35, -35, 0) * millimeter) > 0.01 * millimeter ||
        norm(bounds.maxCorner - vector(35, 35, 60) * millimeter) > 0.01 * millimeter)
        throw regenError("Unexpected default holder bounds.");
    const centers = [vector(8,0,2), vector(-8,0,2), vector(0,9.5,2), vector(0,-9.5,2)];
    for (var center in centers)
    {
        const clearance = evDistance(context, { "side0" : center * millimeter, "side1" : solids }).distance;
        if (abs(clearance - 1.65 * millimeter) > 0.01 * millimeter)
            throw regenError("M3 mounting hole is missing or has incorrect size/position.");
    }
    const boss = evDistance(context, { "side0" : vector(0,0,2) * millimeter, "side1" : solids }).distance;
    if (boss < 4.695 * millimeter) throw regenError("Imported motor bearing boss needs at least 9.39 mm rear clearance.");
    const bladeTip = evDistance(context, { "side0" : vector(30,0,50) * millimeter, "side1" : solids }).distance;
    if (abs(bladeTip - 2 * millimeter) > 0.01 * millimeter) throw regenError("Blade tip clearance is incorrect.");
    const cable = evDistance(context, { "side0" : vector(0,33.5,4) * millimeter, "side1" : solids }).distance;
    if (cable < 3.5 * millimeter) throw regenError("Cable exit is obstructed.");
    const oldBodies = evaluateQuery(context, qBodyType(qEverything(EntityType.BODY), BodyType.SOLID));
    rovThrusterHolder(context, id + "largerHolder", { "propDiameter" : 72 * millimeter });
    const larger = qSubtraction(qBodyType(qEverything(EntityType.BODY), BodyType.SOLID), qUnion(oldBodies));
    if (size(evaluateQuery(context, larger)) != 1) throw regenError("Resized holder is disconnected.");
    const largerBounds = evBox3d(context, { "topology" : larger, "tight" : true });
    if (norm(largerBounds.maxCorner - vector(41,41,60) * millimeter) > 0.01 * millimeter)
        throw regenError("Propeller diameter edit did not resize the duct.");
    const largerGap = evDistance(context, { "side0" : vector(36,0,50) * millimeter, "side1" : larger }).distance;
    if (abs(largerGap - 2 * millimeter) > 0.01 * millimeter) throw regenError("Resizing lost the blade-tip clearance.");
    opDeleteBodies(context, id + "removeLargerTestFixture", { "entities" : larger });
    println({ "checksPassed" : 12, "rearClearanceMM" : boss / millimeter * 2, "connectedSolids" : count,
        "boundsMM" : [bounds.minCorner / millimeter, bounds.maxCorner / millimeter],
        "tipClearanceMM" : bladeTip / millimeter,
        "holderVolumeMM3" : evVolume(context, { "entities" : solids }) / (millimeter^3) });
}, {});

