# R11 Actual Onshape Motor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Replace generic R10 motor/adapter references with the actual Onshape models and match the fan to them.
**Architecture:** Isolated native workspace; four native source Part Studio references derived before final finishing. Preserve source metal geometry and all frame/cap/duct geometry; adjust only fan interface and assembly references.
**Tech Stack:** Native Onshape FeatureScript/UI, STEP/OCP and mesh verification.
**Spec:** cad/actual-onshape-motor-r11-2026-10-25/DESIGN.txt

## Global Constraints

Frame/cap shapes and28mm extension unchanged. No internal motor spacer.
Actual motor and3 metal adapter models retain exact source shape.
Fan uses5.1mm bore,6.2x0.35mm rear relief,7.1450595848951mm hub thickness.
Source assembly pose maps with +45degY and +15.67mmY.
Do not hide pre-existing metal clamp overlaps in zero-interference claims.

## Review Focus

- Actual source models/threads must be preserved, not reconstructed envelopes.
- Source motor is fused; animation must not rotate the stationary body/wires.
- Shoulder relief must clear the source's protruding5.7912mm neck.
- Source metal clamp/thread contacts must be separated from unintended contact.
- Exported fan/coupon must match updated source hardware and supersede R10.

### Task1: Actual source and native fan interface

Files: source snapshot/provenance, r11_actual.fs, build_source.py, native-r11.fs, verify_r11.py.

- [x] Save source version and branch R11 from R10.
- [x] Write/run RED checks against R10 for actual-source geometry/new interface.
- [x] Link four actual source Part Studios natively; derive before final feature (supersedes snapshot).
- [x] Implement fan interface, actual-body pose, cleanup and axis connectors.
- [x] Export STEP and prove actual source preservation and fit (GREEN).

### Task2: Assembly and print delivery

- [x] Replace five obsolete reference instances with four actual model instances.
- [x] Constrain fixed44/rotating4, including4 added M3 washers, and rebuild axis mate; check motion/contacts.
- [x] Export fan and coupon; reuse unchanged extension/frame/cap files.
- [x] Update source-based instructions and model limitations.
- [x] One fresh final review, resolve Important findings, save native version.
- [x] Verify package contents and deliver updated Onshape/STL links with screenshot.
