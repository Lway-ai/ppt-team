# PPT Team contributor and agent rules

These rules apply when the plugin is used to create, modify, or review technical PowerPoint files.

## Editing constraints

1. Do not save PPTX files with `python-pptx`; use PowerPoint COM, raw ZIP/XML edits, or an approved Office XML editing path.
2. Never assign ordinary text to an OMML equation shape. Edit equation XML instead.
3. Keep one writer for a PPTX at a time. Read-only extraction, rendering, and validation may run in parallel.
4. Preserve the source deck before intrusive edits.
5. Pass non-ASCII PowerShell text through UTF-8 files when scripting.

## Verification discipline

After each editing round:

1. Render the changed pages.
2. Run `scripts/verify_deck.py` and require zero `FAIL` findings.
3. Visually review only the changed pages, then perform a final full-deck review before delivery.
4. Record the change in the project's changelog.

The verifier checks package/layout/font/overlap/formula-presence signals. It cannot prove technical truth, circuit topology, equation correctness, or measurement provenance; those require source-grounded human review.

## Public-repository boundary

This repository intentionally contains source code, scripts, templates, and documentation only. Do not add private decks, proprietary model files, rendered slides, third-party logos, extracted conference corpus files, credentials, or machine-specific absolute paths.
