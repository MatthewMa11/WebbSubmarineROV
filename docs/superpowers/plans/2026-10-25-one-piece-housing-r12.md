# One-piece Housing R12 Implementation Plan

> Execute with superpowers:executing-plans. One final fresh review.

**Goal:** Merge blue outer extension and gray housing into one printable part.
**Architecture:** Branch native R11 version; append one housing merge operation
with finite overlap web and relieved fastener paths. Preserve fan, actual motor/
adapter, cap and installed poses. Update assembly, print mesh and saved version.
**Tech:** Native Onshape/FeatureScript, independent STEP/OCP and mesh checks.
**Spec:** cad/one-piece-housing-r12-2026-10-25/DESIGN.txt

## Review Focus
- Union must be one connected printable solid, not a grouped pair.
- Added seam material must clear all hardware and rotating envelope.
- Motor/fan installation path and detachable cap remain usable.
- Actual metal models, fan, cap and fasteners retain geometry/poses.
- New PRINT folder must exclude superseded separate housing/extension files.

## Task1: Housing and assembly
- [x] Run RED against R11: expects47 solids and one combined outer shell.
- [x] Branch R12, append housing web/merge, regenerate and export.
- [x] Prove single solid, unchanged other46 bodies and rotation/fastener clearance.
- [x] Remove obsolete extension assembly instance; fixed43/rotating4; motion.

## Task2: Print and delivery
- [x] Export one manifold housing STL, verify dimensions/geometry; reuse fan/cap.
- [x] Update instructions, save native version, one final review.
- [x] Package verified outputs; deliver Onshape and STL links with screenshot.
