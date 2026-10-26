# R9 Forward Fan Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Implement the user's cap--fan--motor--rear-support sketch in the separate Onshape design.
**Architecture:** Flatten the rotating hub, relocate the existing outer blade geometry8.0 mm forward, and retain the M3 axle clamp and four drive keys. All stationary reference geometry/poses stay unchanged.
**Tech Stack:** Native Onshape FeatureScript/UI, local OCP/VTK geometry checks, native STEP/STL exports.
**Spec:** DESIGN.txt, based on the user's attached sketch and previously authorized hardware.

## Global Constraints

- Preserve original R7 and R8; use new R9 workspace in the separate document.
- Frame, cap, rotor, stator and36stationaryfasteners unchanged.
- No motor spacer, threaded collar or jam ring. Keep four5.5 mm keys on18 mm pattern.
- TwoM3x16+twoM3nuts retain the axle;3.175 mm reference shaft,3.3 mm bore and3.05 mm grip.
-46assemblysolids,47PSparts including unusedmesh; rotatinggroup7.

## Review Focus

- New blade root connectivity and round validity.
- Blade/cap/duct collision throughout360degrees, including stationaryfasteners.
- Removing old motor cup while preserving keys and clamp ears.
- Nutdriver access and screw/nut engagement after moving blades.
- Explicit prototype limits: physical retention, PLA creep, balance and strength.

### Task 1: Forward blades and flat hub

**Files:** create layout_test.py, r9_layout.fs, build_source.py, native-r9.fs.
**Interfaces:** consume R8 native FeatureScript plus R6 filled-key prefix; produce r9ForwardFan(context,id,prop) before r8BuildAxleClamp.

- [x] Run layout_test.py on R8 STEP; expect failures for rear cup material and aft blade location.
- [x] Copy the original fan and remove its R19 center, producing exactly two complete blades. Mask all front/rear root tools insideR26.9; preserve outerprofile beyondR27.01 and translate8.0 mm alongY. Remove old rear geometry belowY14.2 except four keys. Add flatR20diskY12.8..19.3, motor-clear its back belowY14.2, round only R20 root junctions. Enforce one fan body and native46body guard.
- [x] Commit only R9 workspace Feature Studio, verify47parts and no regeneration error.

### Task 2: Native assembly and verification

**Files:** create verify_r9.py; export Thruster-R9-forward-fan.step and Fan-R9-forward-fan.stl.
**Interfaces:** consume Task1 nativebody identities; produce46body constrained assembly and final meshes.

- [x] Rename R9 fan/PS/assembly; retain all existing group members and original stationary poses.
- [x] Run layouttest and independent geometric suite. Compare blade tips to original after reversing8.0 mm translation. Verify keys, pilot/shaft fit, closing travel, stepped fullturnclearance, hardware, toolaccess and no internalspacer.
- [x] NativeNoInterferences and360degreeanimation; one-body and manifold STLs, track or heal inherited tip slivers.

### Task 3: Review and deliver

**Files:** native screenshots, assembly instructions, PRINT folder, ZIP, progress.md.
**Interfaces:** final STEP/STL from Task2; deliver saved nativeR9version and matching prints.

- [x] One fresh-context read-only final review; fix Important/Critical issues with failing checks before source changes.
- [x] Regenerate small lowerjawcoupon; provide unchanged upperjaw/frame/cap meshes and source-provenance checks.
- [x] Save native R9 version, present side/section and complete views matching sketch, mark tabdeliverable.
- [x] Verify ZIP CRC and STL/native volume agreement, provide links and physical test limits.
