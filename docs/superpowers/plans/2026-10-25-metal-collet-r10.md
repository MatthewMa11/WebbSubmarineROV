# R10 Metal Collet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Replace the printed shaft clamp with a normal bought metal collet adapter.
**Architecture:** Isolate R10 from saved R9 in Onshape. Preserve frame/cap shapes; add the approved duct extension and a flat propeller hub.
**Tech Stack:** Native Onshape FeatureScript/UI, Python OCP/mesh verification.
**Spec:** cad/metal-collet-r10-2026-10-25/DESIGN.txt

## Global Constraints

Frame unchanged in shape/placement. Cap unchanged in shape, translated +28 mm.
No internal motor spacer. CPA-317-N bought metal reference; M6x1 stud / 3.17 input.
Physical adapter grip depth remains a required fit check.

## Review Focus

- Full rotation, including fasteners, clears cap and extension.
- New extension supports the cap without modifying the old joint surfaces.
- M3x40 screws engage the existing captive nuts without entering blind material.
- Adapter model assumptions are explicit; no fictitious exact supplier CAD.
- Printable exports contain only printable bodies and match the verified model.

### Task 1: Native hub and stationary extension

Files: r10_collet.fs, build_source.py, native-r10.fs, verify_r10.py in the R10 folder.

- [x] Write/run checks against R9 to show required new layout absent (RED).
- [x] Branch saved R9; implement 6.2 mm hub bore and 28 mm duct extension.
- [x] Add metal adapter reference stack; extend four cover screws to M3x40.
- [x] Export STEP, verify preserved geometry and joint/rotation fit (GREEN).

### Task 2: Assembly and print delivery

Consumes verified native R10 parts; produces constrained assembly and print kit.

- [x] Remove obsolete jaw/clamp instances; add extension and metal reference stack.
- [x] Verify rotating/fixed groups, native interference and 360-degree motion.
- [x] Export fan/extension and small bore coupon; check STL closure and units.
- [x] Write installation/BOM with adapter purchase and physical fit limitations.
- [x] One fresh final review; resolve important findings and save native version.
- [x] Package files, capture native screenshot and deliver links.
