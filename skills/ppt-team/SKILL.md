---
name: ppt-team
description: Use the local PPT Team workflow for editable RFIC, ISSCC, RFIC2024, and technical PowerPoint decks. Apply the architect, builder, consolidator, and judge roles in Codex or ZCode while using PowerPoint COM, raw-zip OMML injection, rendering, and verify_deck QA. Trigger when the user asks to create, modify, review, or validate a technical PPT/PPTX in any working directory.
---

# PPT Team for Codex

This skill is the entry point for the local multi-agent PPT Team in both Codex and
ZCode. In Codex it acts as the adapter: the original `.zcode-plugin` remains the
ZCode source package, and Codex loads this skill plus the project's
`ppt-conference-style` skill through `.codex-plugin/plugin.json`. In ZCode the native
conductor is `agents/ppt-team.md` (driven by the `/make-ppt` command in
`commands/make-ppt.md`); the workflow below states the Gate A/B/C human gates
explicitly so every host shares one rule set.

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
4. **Gate A (human gate, do not skip)**: have `ppt-architect` produce 2–3 competing outlines from the manifest and stop for the user to pick or hybridize — never choose a narrative line or silently drop a variant.
5. Select one style profile and declare it in the project record (never mix profiles within a deck): `scripts/style.json` = RFIC2024 majority variant (default); `scripts/style.zou.json` = Tenghao Zou RFIC2022 variant; `scripts/style.techshare.json` = FM/DDC tech-share variant (white background, deep-blue left title, three-segment footer without color band — see style skill §三).
6. **Gate B (human gate, do not skip)**: build a 3-page mini-deck through one full loop (build → render → verify → judge) and freeze the style only after the user confirms it.
7. Preserve the source before any write. Use `scripts/build_helpers.ps1` for PowerPoint COM construction and `scripts/inject_omml.py` for native editable formulas.
8. Render with `scripts/export_slides.ps1`, then run:

   ```powershell
   C:/Python314/python.exe scripts/verify_deck.py <deck.pptx> --style <selected-style.json>
   ```

9. Do not call visual review until `verify_deck.py` has zero FAIL findings. Review only the pages changed in the current round, then run a full final review before delivery. Repair rounds are capped at 5 — beyond that, escalate to the user (AGENTS.md rule 8).
10. Record each round in `CHANGELOG.md`. Keep backups under `_backups/` and keep the original ZCode package intact.
11. **Gate C (human gate, do not skip)**: before delivery, re-verify the whole deck, run a full-deck judge review with a fresh instance, and check every technical value against `templates/data_provenance.md` (verify cannot prove value truth — see safety boundaries below). Deliver renders + verify/judge reports + the changelog entry.
12. After the final save, zero-FAIL verification, and full visual review, close any resident editor state and reopen the exact final `.pptx` from disk in Microsoft PowerPoint (or the available desktop UI). Leave the deck visible for human inspection and report the handoff path. Do not claim human acceptance from automated gates; the final state is `ready for human review` until the user confirms or returns findings. If the deck cannot be opened, report that blocker explicitly.

## Safety and quality boundaries

- Never save a PPTX with `python-pptx`.
- Never revert versions on your own initiative: `git reset`/`git checkout`/`git revert`, restoring `.bak-*` backups, or wholesale rebuild from an old version all require explicit user approval first. Forward-fix on the current version (edit → render → verify → judge); escalate to the user before any rollback. Never use rollback to "clean up" a parallel session's changes.
- Never assign `.Text` to an OMML formula shape.
- Pass Chinese or other non-ASCII PowerShell text through UTF-8 files.
- Use the shape naming contract: `FooterBand`, `PageNo`, `SessionId`, `KeyBox*`, `Equation*`, and related names are consumed by the verifier.
- `verify_deck.py` checks package/layout/font/overlap/formula-presence signals. It cannot prove circuit topology, equation correctness, or measurement-value truth. Gate C must compare the deck against live models, source plots, and `data_provenance.md`.
- officecli MCP is configured in Codex (`config.toml` → `mcp_servers.officecli`) and is an approved editing/audit channel: `view stats|issues`, `validate`, `query equation`, `set/add` text and `--type equation --prop formula="LaTeX"` (native OMML, round-trip verified: math survives, COM can reopen, verify_deck 0 FAIL). officecli keeps a resident in memory — always `save`/`close` before verify_deck, export_slides, or COM touches the file.
- The official IEEE/MTT-S/RFIC footer logos are not bundled by default. Use only supplied or legally reusable assets.
- OfficeCLI's strict schema validator may report the known `a14:m` OMML leaf-node compatibility error; treat that specific error as documented and require PowerPoint reopen/render plus `verify_deck` for the release gate.

## Review-only requests

When the user asks for a review, preserve the current PPTX and project files.
Inspect the current disk state, render or read the named artifact, and report
verified facts separately from inferred or unverified claims. Do not silently
repair the deck during a review-only request.
