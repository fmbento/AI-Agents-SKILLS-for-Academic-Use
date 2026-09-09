# Cross-Skill Integration Notes

**Language / Idioma:** [en](README.md) · [pt](../README_PT.md)

Notes for reusing the new scripts and skills under `Utils/` inside the existing `Learning`, `Research`, and `Production` skill workflows.

## Scripts

### `Utils/scripts/generate_pdf.py`

Markdown → professionally formatted PDF via pandoc/xelatex.

Best-fit insertion point: any workflow whose **final deliverable is a markdown file you also want as a PDF**.

Natural homes:
- `Research/scopus-research` — after writing `analysis_full_export.md` / `analysis_subset.md`, optionally render them to PDF.
- `Research/scopus-research/K-Dense-AI_scientific-agent-skills_literature-review/literature-review` — this skill already documents PDF generation as the final step; the existing `literature-review/scripts/generate_pdf.py` is essentially the same kind of tool. If you want one shared PDF helper across research workflows, `Utils/scripts/generate_pdf.py` can be the common one, but it is **not a drop-in replacement** for the `literature-review/scripts/generate_pdf.py` that the literature-review skill already calls. Keep whichever PDF path the active research skill already documents.
- `Learning/eli14` — the `eli14` skill already produces a standalone HTML visual. If you also want a PDF companion, export that markdown/text to PDF here. Do **not** convert the interactive HTML to PDF through this script; it converts markdown.

Usage concept:
- run from the markdown file's directory;
- it expects `pandoc` and `xelatex` on PATH;
- pass the `.md` file and optional output path / citation style / `--no-toc` / `--no-numbers`.

### Other `Utils/Skills/*` scripts

These are skill-local helpers, not generic repo scripts, so they should normally be invoked **through their owning skill**, not copied into `Learning`, `Research`, or `Production` workflows.

Quick orientation:
- `Utils/Skills/docx/scripts/office/soffice.py` — LibreOffice runner used by the `docx` skill for `.docx` → PDF and related conversions.
- `Utils/Skills/xlsx/scripts/recalc.py` — LibreOffice formula recalculation for `.xlsx`.
- `Utils/Skills/scientific-slides/scripts/generate_slide_image.py` — Nano Banana Pro slide/figure generation for the `scientific-slides` skill.
- `Utils/Skills/scientific-visualization/scripts/export_plan.py`, `image_metadata.py` — export planning and figure metadata inspection for the `scientific-visualization` skill.
- `Utils/Skills/pptx-posters/scripts/generate_poster.py` — exact-pinned poster generation for the `pptx-posters` skill.
- `Utils/Skills/scientific-schematics/scripts/generate_schematic.py` — AI schematic generation for the `scientific-schematics` skill.
- `Utils/Skills/exploratory-data-analysis/scripts/eda_analyzer.py` and related CLIs — bounded EDA for the `exploratory-data-analysis` skill.
- `Utils/Skills/markitdown` — MarkItDown conversion skill, with its own batch/literature helpers.

Do not wire these into other skills' pipelines unless the owning skill already describes that integration. The risk is not just "extra dependency"; several of them carry exact-package pins, API-key handling, or narrow local-file contracts that other skills would need to respect explicitly.

## Skills

### `Utils/Skills/pdf`

Use when a workflow needs to read, extract, merge, split, watermark, create, or otherwise process PDFs.

Most useful bridge into existing skills:
- Any skill that ends with a document deliverable and wants a PDF next step.
- PDF-side verification for exported artefacts (for example, checking an exported report PDF exists and has the expected page count before handing it back to the user).

### `Utils/Skills/xlsx`

Use when a workflow needs to produce or verify an Excel deliverable.

Most useful bridge into existing skills:
- Exporting a structured analysis table from a markdown/CSV-heavy workflow into a polished `.xlsx`.
- Recalculating formulas after programmatic edits.

### `Utils/Skills/docx`

Use when a workflow needs Word output or Word-level editing that markdown/PDF tooling cannot express.

Most useful bridge into existing skills:
- Turning a research or learning markdown deliverable into an editable `.docx` for a user who wants trackable edits, comments, or a template-driven layout.

### `Utils/Skills/markdown-mermaid-writing`

Use when a workflow produces documentation and wants consistent markdown + Mermaid conventions.

Most useful bridge into existing skills:
- `Learning/arquiteto-mermaid` is already Mermaid-focused; `markdown-mermaid-writing` is more about the surrounding documentation standard (style guide, templates, 24 diagram types) than about generating one diagram from structured text.
- Research or production documentation that should render cleanly on GitHub and also stay diff-friendly.

### `Utils/Skills/scientific-visualization`, `matplotlib`, `scientific-schematics`

Use when a workflow needs figures.

Most useful bridge into existing skills:
- `Research/scopus-research` does not currently require figures, but any bibliometric or conceptual summary that benefits from a chart or schematic could use them.
- `Production/webinar-to-video` already produces video + overlays; if a companion slide/figure set is needed, these are the skills to reach for, not the video pipeline.

### `Utils/Skills/scientific-slides`, `pptx-posters`

Use when a workflow needs presentation output.

Most useful bridge into existing skills:
- `Production/webinar-to-video` already produces video for YouTube/LinkedIn. If an accompanying slide deck or poster is also wanted, these skills are the better home.
- Research results that should become a talk or poster rather than (or in addition to) a CSV/markdown analysis.

### `Utils/Skills/optimize-for-gpu`

Use when a workflow has a CPU-bound numeric/data bottleneck on NVIDIA hardware.

Most useful bridge into existing skills:
- Not a default addition to any current skill; only relevant if a specific workflow is already doing heavy numerical work and profiling shows a plausible GPU path.

### `Utils/Skills/pi-agent`

Use when the agent-orchestration layer itself is Pi.

Most useful bridge into existing skills:
- This is about running and extending the harness, not about a specific content skill. It matters if/when some of these skills are deployed through Pi rather than another harness.

### `Utils/Skills/experimental-data-analysis`

Use when a workflow inspects authorized local scientific data files before modeling.

Most useful bridge into existing skills:
- Not a natural default for the current `Learning`, `Research`, or `Production` skills as written, because those workflows are document/record/export-oriented rather than raw-data analysis-oriented. If a future research workflow starts from local CSV/TSV/JSON/FASTA/etc. files, this is the skill for the inspection step.

## Integration priorities

If you want the highest-value, lowest-friction bridges first:

1. **PDF from markdown deliverables** — `Utils/scripts/generate_pdf.py` (where a workflow already ends in `.md` and the user wants a PDF too).
2. **PDF as a general downstream format** — `Utils/Skills/pdf` when the deliverable itself is or becomes a PDF.
3. **Document-output skills** — `Utils/Skills/docx`, `Utils/Skills/xlsx` when the user asks for an editable office file instead of, or after, markdown/CSV/PDF.
4. **Documentation standard** — `Utils/Skills/markdown-mermaid-writing` when any skill's output should follow a stricter markdown + Mermaid style.
5. **Figures/presentations** — the scientific-visualization/scientific-schematics/scientific-slides/pptx-posters skills when a deliverable needs visuals or slides rather than only text/tables.

## Compatibility warning

`Utils/Skills/*` skills frequently declare their own exact dependencies and runtime expectations. Before reusing one inside `Learning`, `Research`, or `Production`, check:
- package pins;
- network/API-key requirements;
- local-file and root-boundary rules;
- whether the skill is meant to be a self-contained assistant skill rather than a library of scripts.

That check is especially important for skills that invoke external generation services or that are designed to run only inside a specific harness.
