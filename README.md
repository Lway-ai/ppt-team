# PPT Team

PPT Team is an open-source Codex/ZCode plugin for building and reviewing editable RFIC, ISSCC, and technical PowerPoint presentations.

It packages a multi-agent workflow with four roles:

1. `ppt-architect` — creates evidence-backed outline variants.
2. `ppt-builder` — builds or edits PPTX files through safe PowerPoint/Office XML paths.
3. `ppt-consolidator` — reviews composition, density, and reusable layouts.
4. `ppt-judge` — performs page-level visual acceptance checks on rendered slides.

The package includes the role definitions, Codex skill adapter, `/make-ppt` command, editable OMML helpers, rendering helpers, style profiles, templates, and deterministic PPTX verification tests.

## Repository layout

| Path | Purpose |
|---|---|
| `.codex-plugin/` | Codex plugin manifest |
| `.zcode-plugin/` | ZCode plugin manifest |
| `agents/` | Architect, builder, consolidator, judge, and conductor role definitions |
| `commands/` | User-facing `/make-ppt` command |
| `scripts/` | PowerPoint COM helpers, OMML injection, rendering, style profiles, and QA tests |
| `skills/` | Codex skill adapter and conference-style guidance |
| `templates/` | Content and technical-data provenance templates |

Examples, rendered decks, learned corpus snapshots, backup files, and third-party logos are intentionally not distributed in this repository. Generate a plain gradient footer locally with `scripts/make_footer_band.py`, and provide any legally reusable branding assets yourself.

## Safety rules

- Do not save PPTX files with `python-pptx`.
- Keep PPTX writes serialized: only one builder may hold a file-write handle at a time.
- Treat OMML equations as XML and do not overwrite them through ordinary text APIs.
- Run deterministic verification after every deck-editing round.
- Technical claims, topology, measurements, and source-model values still require human/source review; the verifier cannot prove them.

## Validation

The repository has no runtime dependency for its core regression tests:

```powershell
python scripts/test_verify_deck.py
python scripts/test_omml_tex.py
```

The plugin manifest can be checked with Codex's `validate_plugin.py` helper when the Codex skill tooling is installed.

## Installation

Install the repository as a local Codex plugin or copy it into your personal plugin directory. The exact installation command depends on the Codex release and local marketplace configuration; the manifests in `.codex-plugin/` and `.zcode-plugin/` are the source of truth.

## License

MIT. See [LICENSE](LICENSE).
