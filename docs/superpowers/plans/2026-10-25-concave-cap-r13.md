# Concave Cone and Bolt Joint R13 Implementation Plan

> Execute inline with superpowers:executing-plans and one final fresh review.

**Goal:** Recess the cone for adapter clearance; simplify cone-to-frame bolting.
**Architecture:** Branch saved R12, append bowl/pilot/pocket features and update
only four cover screws, nuts and rear washers. Preserve actual motor/fan/adapter.
**Tech:** Native Onshape/FeatureScript, independent geometry and mesh checks.
**Spec:** cad/concave-cap-r13-2026-10-25/DESIGN.txt

## Review Focus
- Concavity must face the metal adapter, preserve outer cone and adequate walls.
- Nuts must load from outside, stay rotationally captured, and bear on real washers.
- M3x12 stack needs full nut engagement, roof thickness and clear key approach.
- Locating pilots need print relief and must not hold cap above its bearing seats.
- Fan/adapter rotation and motor insertion remain clear; no spacer returns.

## Task1: Native design and fit
- [x] Observe RED against R12 for bowl, short screws and front nut seats.
- [x] Branch R13, implement features and export; verify shapes and joint geometry.
- [x] Check full-turn, insertion, nut/washer loading and screw-key paths.
- [x] Verify native47-part poses, groups, motion and interference.

## Task2: Printable delivery
- [x] Export housing/cap and joint fit coupons; validate closed connected meshes.
- [x] Update assembly/print directions and save native version.
- [x] One fresh review, package gate and delivery links/screenshot.
