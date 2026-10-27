# WebbSubmarineROV

The Webb Submarine ROV club is developing a remotely operated underwater vehicle while learning mechanical design, fabrication, electronics, programming, and testing. Our vision is to turn that work into useful science and engineering experiences for the museum and its community.

**Club website:** [WebbSubmarineROV](https://matthewma11.github.io/WebbSubmarineROV/)

## Project journals

- [Motor and fan CAD development journal](docs/journals/motor-and-fan-cad-development.md) — a detailed retrospective of the PLA baseline and R2–R14, including the reasons for changes, motor and adapter fit, retention mechanisms, housings, assembly access, and remaining physical checks.
- [Club mission and museum vision](docs/journals/club-mission-and-museum-vision.md) — what the club does, what we are learning, and how the project could serve museum education and future staff-directed work.

## Start with the current design

The latest recorded thruster configuration is **R14 housing + R13 concave cone + R11 fan**, fitted to the actual motor and metal adapter used in the R11 source model. It is a CAD and fabrication development configuration; the saved records do not establish successful powered-water operation.

- [R14 assembly and print instructions](cad/smooth-frame-r14-2026-10-25/ASSEMBLY-AND-PRINT.txt)
- [Download the R14 print kit](archives/R14-Smooth-Frame-Print-Kit.zip) — current housing, retained fan/cone, fit coupons, and instructions.
- [R14 design decisions](cad/smooth-frame-r14-2026-10-25/DESIGN.txt) and [verification limits](cad/smooth-frame-r14-2026-10-25/FINAL-REVIEW.txt)
- [Latest whole-vehicle assembly notes](cad/easy-assembly-2026-10-18/READ-ME.txt) — the October 18 chassis/electronics-tube assembly is a separate snapshot; it has not been represented as a complete R14 vehicle integration.

Earlier revision folders are historical snapshots. Their hardware stacks and print files are not automatically interchangeable with the current design.

## Files and downloads

FeatureScript, Python scripts, design notes, verification reports, bills of materials, cutting outlines, and selected CAD screenshots are browsable in their original project paths. The [CAD archive index](archives/README.md) provides every original CAD revision file, including STL, STEP, BREP, all original images, and original print ZIP packages, in ordinary ZIP downloads attached to the [CAD development release](https://github.com/MatthewMa11/WebbSubmarineROV/releases/tag/cad-archive-2026-10-26). Each archive preserves the original `cad/` paths; extract all archives for a revision into the same project root to restore that revision completely.

Large geometry is packaged into downloads rather than displayed as individual GitHub files. This preserves historical exports and duplicate print bundles while keeping the repository useful to browse. [The file inventory](archives/file-inventory.csv) maps each original CAD file to its archive and SHA-256 checksum. [The archive manifest](archives/archive-manifest.json) records download sizes and checksums.

The root `rov_*.fs` files and chassis progress notes preserve the earlier chassis and thruster-holder work. `docs/superpowers/` contains the existing design and implementation records. The journals connect those technical artifacts to the project's development story.

## Continuing the work

Start from the instructions associated with the chosen revision, record real measurements and print settings, and keep the small fit-test results with the parts they describe. When a design changes, save the reason, the affected interfaces, and the evidence supporting the change. CAD interference results, mesh checks, and assembly animations should remain distinct from physical fit, retention, thrust, durability, and underwater tests.

Project import and journal date: **October 26, 2026**. Historical dates in the journals come from the saved project records; this GitHub import does not recreate earlier Git commits.

## Updating the website

The public club website uses GitHub Pages, published from the root of the `main` branch. Edit `index.html` for content and `site-assets/site.css` for styling. The site uses the project’s existing CAD images and links to the journals and release downloads. Keep `.nojekyll` in place so GitHub serves the static files directly. Changes pushed to `main` are published automatically by GitHub Pages.

The homepage opens dedicated journal pages at `journals/`. The Markdown files in `docs/journals/` remain the editable source. After changing a journal, run `npm install` once and `npm run build:site`, then commit the generated HTML and diagram SVGs with the source. This preserves the illustrated journal content without requiring JavaScript in the reader’s browser. Reader styling lives in `site-assets/journals.css`.
