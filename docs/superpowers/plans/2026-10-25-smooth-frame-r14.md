# Smooth Frame R14 Implementation Plan

> Execute inline with superpowers:executing-plans; one fresh final review.

**Goal:** Smooth the frame surface and remove obsolete crescent mounts.
**Architecture:** Append local shell/rounded-root cleanup after R13. New native
branch preserves R13; retain all other46 solids and functional front joints.
**Tech:** Onshape FeatureScript; independent OCP geometry and STL checks.
**Spec:** cad/smooth-frame-r14-2026-10-25/DESIGN.txt

## Review Focus
- Old C-shaped mounts must be removed rather than hidden.
- Smooth transition must not intrude into rotating/insertion envelopes.
- Keep current nut loading, pilot fit, bolt roof and tool access.
- Native assembly must retain actual motor/hardware and47 solid poses.
- Print must be closed and single-body; only frame needs a new full print.

## Task1: Native geometry
- [x] Branch savedR13; implement smooth skin and obsolete-mount removal.
- [x] Inspect/export; verify other46 bodies, profile and current joint geometry.
- [x] Check rotation, nut loading and motor insertion.

## Task2: Delivery
- [x] Fine housing STL and local fit coupon; verify closed connected meshes.
- [x] Native assembly evidence, saved version and screenshot.
- [x] One fresh review and verified ZIP with unchanged cone/fan.
