# ROV chassis implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan in this session. Steps use checkbox syntax for tracking.

**Goal:** Build the approved eight-thruster chassis in the user's existing Chassis Onshape document.

**Architecture:** A self-contained FeatureScript reuses the existing holder, builds a connected cage and eight split-clamp bases, and places eight removable caps. All solids remain named and editable through one chassis feature.

**Tech Stack:** FeatureScript 3083, Onshape MCP kernel tests and persistence, browser UI for final feature insertion.

**Spec:** `docs/superpowers/specs/2026-09-30-rov-chassis-design.md`

## Global constraints

- Default size 360 × 300 × 120 mm; 60 mm propeller, 64 mm bore and 70 mm OD.
- Four diagonal horizontal thrusters, four vertical thrusters, two facing each vertical direction.
- M3 clearance 3.3 mm; clamp bore 70.4 mm and 1 mm split gap.
- Use the empty Chassis Part Studio, preserve Motor + Fan.
- Write final FeatureScript once, after kernel checks pass.

## Review focus

- Frame/holder/cap solids must not overlap after placement.
- Clamp supports must connect to the cage and stay outside the duct bore.
- Both ends of every vertical duct need an unobstructed path through the cage.
- Size and propeller edits must either rebuild correctly or explain the required minimum size.
- Clamp screws and motor mounting holes must remain accessible and aligned.

### Task 1: Geometry and kernel checks

**Files:** Create `rov_chassis.fs`, `rov_chassis_tests.fs`.

**Interfaces:** `rovChassis(context is Context, id is Id, definition is map)` has defaults `length:360 mm`, `width:300 mm`, `height:120 mm`, `propDiameter:60 mm`, `clampClearance:0.4 mm`. It creates 17 named solids. Existing `rovThrusterHolder` is private in this source, unchanged geometrically.

- [x] Write a real kernel test expecting 17 solids and bounds (-180,-150,-60)..(180,150,60) mm; run against a no-op chassis and observe count failure.
- [x] Implement cage, vented tray, split collars and transformed holder instances using cuboids/cylinders, Boolean operations and coordinate systems.
- [x] Add and run checks of the eight actual cylinder axes and bore sizes, M3 mounting holes, clamp screw holes, vertical flow windows, body interference and a larger-frame rebuild.
- [x] Add an invalid large-prop/small-frame fixture; prove a clear regeneration error is returned without partial geometry.
- [x] Save passed kernel output alongside the source.

### Task 2: Review, persistence and actual document verification

**Files:** Create `rov_chassis_onshape.jpg`, update execution ledger.

**Interfaces:** Consume tested source and target document IDs from the spec; produce a saved custom feature and a rendered Part Studio with 17 parts.

- [x] Review source and kernel evidence for geometry, screw access and untested parameter combinations.
- [x] Create the new Feature Studio; read its version and write the final tested source once.
- [x] Insert the custom feature through the Chassis browser UI and accept default dimensions.
- [x] Rename Part Studio for clarity, hide reference planes, fit and show the chassis.
- [x] Reload and confirm feature, 17 parts and no regeneration errors remain; save and embed a screenshot.

Git commits are not part of this CAD deliverable; the Onshape document history and local source preserve the work.

