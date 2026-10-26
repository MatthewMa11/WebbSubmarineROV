# Webb Submarine ROV Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build an accessible static club website that explains the project and provides useful routes to its evidence and downloads.

**Architecture:** One semantic HTML document with one stylesheet and native anchor navigation. Existing images remain in their CAD folders. GitHub Pages serves the repository root.

**Tech Stack:** HTML5 and CSS; no build or external dependencies.

**Spec:** `docs/superpowers/specs/2026-10-26-club-website.md`

## Global Constraints

- The current configuration is R14 housing + R13 concave cone + R11 fan.
- Keep the museum unnamed and activities aspirational.
- No external dependencies, fonts, analytics, frameworks, or required JavaScript.
- Use existing CAD images through relative paths; no copied or generated assets.
- Parent agent owns GitHub publication and browser verification.

## Review Focus

- A narrow mobile viewport must keep navigation, text and downloads readable without horizontal scrolling.
- Keyboard users must have a visible focus indicator and a skip link.
- Root and project-path hosting must both resolve relative image/style URLs.
- The CAD picture must be labeled as a model and show the actual current configuration.
- Source links must point to the journals, correct assembly guide, current print kit and complete archive.

## Task 1: Create the complete static experience

**Files:** Create `index.html`, `site-assets/site.css`, `.nojekyll`.

**Interfaces:** Consumes the existing R14 image files, README, journals and archive index. Produces a buildless document with `#project`, `#journal`, `#mission` and `#downloads` anchors.

- [x] Read the README, journals, image assets and design constraints.
- [x] Implement semantic navigation, hero, project detail, journal links, museum vision, downloads and footer.
- [x] Style the document with responsive grids, readable typography, CSS image crops, focus states and reduced-motion support.
- [x] Validate HTML structure, fragment links and relative asset existence with a bounded local read-only check.
- [x] Hand off to parent for browser QA and publication.

## Execution notes

The user has authorized implementation and publication; no additional design approval is needed. This presentation change uses static validation and parent browser review rather than implementation-mirroring unit tests. The parent owns remote writes; this worker edits only the listed site and planning files.

HTML structure, heading hierarchy, fragment IDs, image descriptions and local stylesheet/image references passed a Python HTMLParser audit. The current print kit exists in the upload package and public repository, as confirmed by the parent; its absence from the loose source checkout does not affect its deployed path. Download size is 13,526,821 bytes, SHA-256 `f26497122d734f83af8dbbd34d58e356b7b87de6fcc95017674709b3de2eae7e`.

Independent read-only review found no material content, accessibility or responsive defects. Primary text contrast ranges from 5.80:1 to 12.74:1. The focus outline was darkened to provide at least 3.51:1 against cream and navy. Browser rendering and deployment verification remain owned by the parent.
