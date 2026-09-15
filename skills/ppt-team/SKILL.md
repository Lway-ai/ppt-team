---
name: ppt-team
description: Use the local PPT Team workflow for editable RFIC, ISSCC, RFIC2024, and technical PowerPoint decks. Apply the architect, builder, consolidator, and judge roles in Codex while using PowerPoint COM, raw-zip OMML injection, rendering, and verify_deck QA. Trigger when the user asks to create, modify, review, or validate a technical PPT/PPTX in this project.
---

# PPT Team for Codex

This skill is the Codex adapter for the local multi-agent PPT Team. The original
`.zcode-plugin` remains the ZCode source package. Codex loads this skill and the
project's `ppt-conference-style` skill through `.codex-plugin/plugin.json`.

## Role mapping

The ZCode roles remain the source of truth in `agents/`:

- `ppt-architect`: produce 2–3 competing outlines from an evidence-backed content manifest.
- `ppt-builder`: perform the only write operation on the PPTX through PowerPoint COM and raw-zip XML edits.
- `ppt-consolidator`: review rendered pages for density, composition, and reusable layout patterns.
- `ppt-judge`: review rendered PNGs only and return page-level pass/fail findings.

Codex does not treat the ZCode `agents/` and `commands/` manifest fields as
native plugin components. Therefore the main Codex agent coordinates these roles
sequentially, or uses available delegated workers only for read-only extraction,
review, rendering, and validation. Never allow two workers to write the same
PPTX at the same time.

## Required workflow

1. Read `AGENTS.md`, `skills/ppt-conference-style/SKILL.md`, and the relevant role files in `agents/`.
2. Inspect the exact source PDF/PPTX/model and create or update a content manifest using `templates/content_manifest.md`.
3. Register every technical number, equation, plot, photo, and comparison value in `templates/data_provenance.md`.
4. Select one style profile. Use `scripts/style.zou.json` for the Tenghao Zou RFIC2022 visual variant and `scripts/style.json` for the RFIC2024 majority variant.
5. Preserve the source before any write. Use `scripts/build_helpers.ps1` for PowerPoint COM construction and `scripts/inject_omml.py` for native editable formulas.
6. Render with `scripts/export_slides.ps1`, then run:

   ```powershell
   C:/Python314/python.exe scripts/verify_deck.py <deck.pptx> --style <selected-style.json>
   ```

7. Do not call visual review until `verify_deck.py` has zero FAIL findings. Review only the pages changed in the current round, then run a full final review before delivery.
8. Record the round in `CHANGELOG.md`. Keep backups under `_backups/` and keep the original ZCode package intact.

## Safety and quality boundaries

- Never save a PPTX with `python-pptx`.
- Never assign `.Text` to an OMML formula shape.
- Pass Chinese or other non-ASCII PowerShell text through UTF-8 files.
- Use the shape naming contract: `FooterBand`, `PageNo`, `SessionId`, `KeyBox*`, `Equation*`, and related names are consumed by the verifier.
- `verify_deck.py` checks package/layout/font/overlap/formula-presence signals. It cannot prove circuit topology, equation correctness, or measurement-value truth. Gate C must compare the deck against live models, source plots, and `data_provenance.md`.
- The official IEEE/MTT-S/RFIC footer logos are not bundled by default. Use only supplied or legally reusable assets.

## Review-only requests

When the user asks for a review, preserve the current PPTX and project files.
Inspect the current disk state, render or read the named artifact, and report
verified facts separately from inferred or unverified claims. Do not silently
repair the deck during a review-only request.
