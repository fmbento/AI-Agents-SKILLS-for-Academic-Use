# scopus-research

A reusable agent skill that runs a complete **Scopus literature research**
from one input — your research topic — through browser-controlled Scopus,
ending with analyzed CSV deliverables on disk.

Validated end-to-end on 2026-09-08 (topic: *AI for eldercare*, 138,573-doc
result set, 2,000-record export, 74-paper focused subset). Example outputs
from that run live in [`examples/`](examples/README.md).

## What it does

```
TOPIC ("aplicação de IA no cuidado de idosos")
  │
  ├─ 1. Builds an enriched Scopus advanced-search equation
  │      PT→EN + synonyms + wildcards + TITLE-ABS-KEY blocks; shows you first
  ├─ 2. Runs it in Scopus (your Chrome, your institutional session)
  │      and sorts results by RELEVANCE
  ├─ 3. Exports up to 2000 records as CSV:
  │      Abstract + Author keywords + Indexed keywords + Include references
  ├─ 4. Analyzes: top-20 most-cited, top journals, years, keywords
  │      + top-10 most-mentioned references, with permanent Scopus links
  └─ 5. Filters a focused subset (your key terms in title/abstract)
         → second CSV + stats
```

Deliverables land in `./pesquisas/scopus/<YYYY-MM-DD_HH-MM> - <topic>/`:
`scopus_export_full.csv`, `scopus_<focus>_subset.csv`, `query.txt`, plus the
analysis summary in chat.

## Requirements

| Need | Details |
|------|---------|
| **Chrome + remote debugging** | `chrome://inspect/#remote-debugging` → tick "Allow remote debugging for this browser instance" → **fully restart Chrome**. The skill uses your real profile so your Scopus/institutional login survives. |
| **browser-harness** | `uv tool install --python 3.12 --upgrade --force browser-harness`. Invoked as `browser-harness <<'PY' ... PY` heredocs. |
| **Scopus access** | Institutional (IP) or personal sign-in, visible in the user menu. |
| **Python 3** | Stdlib only — no extra packages. |

## Usage

Tell your agent, e.g.:

> Use the scopus-research skill on "digital twins for rehabilitation medicine"
> with focus terms: digital twin, rehabilitation, physiotherapy.

The skill accepts: `TOPIC` (any language — Portuguese is enriched to English),
optional `FOCUS_TERMS` (defaults to 3–6 terms derived from the topic, shown to
you first), `MAX_EXPORT` (default 2000, Scopus's per-run CSV cap), and
`OUT_ROOT` (default `./pesquisas/scopus/`).

The agent shows you the built equation **before searching**, so you can tune
synonyms and blocks.

## Scopus syntax it uses

- Field codes: `TITLE-ABS-KEY(...)`, `PUBYEAR`, `DOCTYPE`, `LANGUAGE`
- Boolean `AND` / `OR` / `AND NOT`; proximity `W/n` and `PRE/n`
- Wildcards `*` (any chars) and `?` (single char)
- `"exact phrases"` (stemmed) vs `{brace exact form}` (unstemmed)

## Honest limitations

- **2000-record cap per export.** For result sets larger than that, the export
  is a slice (of the current sort — relevance by default). Different sorts
  select different slices; the skill reports this caveat every time.
- The **most-mentioned-references** ranking parses Scopus's textual `References`
  column (semicolon-separated); fingerprints use first-author + year + DOI and
  can slightly over-segment odd reference formats.
- Scopus's UI changes: DOM ids validated on 2026-09-08 (`#searchfield`
  contenteditable, `#advSearch`, export dialog flow) are re-checkable against
  the "Search tips" panel if a step stops matching.

## Files

```
scopus-research/
├── SKILL.md            ← the skill (read this first as the agent)
├── README.md           ← this file
└── examples/
    ├── README.md                       ← example provenance + column reference
    ├── query.txt                       ← the validated equation
    ├── scopus_export_full_HEADER_ONLY.csv   ← first 10 rows of a real export
    ├── scopus_eldercare_subset_SAMPLE.csv   ← complete 74-row focused subset
    ├── analysis_full_export.md         ← Step-4 report from the real run
    └── analysis_subset.md              ← Step-6 report from the real run
```

## Sharing / installing

Copy the whole `scopus-research/` folder into any `.agents/skills/` directory
that your agent harness scans (e.g. `~/.agents/skills/`), then invoke it by
name. No dependencies beyond the requirements table.
