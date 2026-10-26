FeatureScript 3083;
import(path : "onshape/std/geometry.fs", version : "3083.0");

// A2212 stationary-base holder. The motor's rotating bell stays free.
// Axis: +Z. Motor seats at Z = plate thickness. No propeller is manufactured here.
annotation { "Feature Type Name" : "ROVThrusterHolder" }
export const rovThrusterHolder = defineFeature(function(context is Context, id is Id, definition is map)
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
