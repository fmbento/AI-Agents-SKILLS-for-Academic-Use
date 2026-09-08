# Research Skills

**Language / Idioma:** [en](README.md) · [pt](README_PT.md)

The `Research` collection contains agent skills for structured, reproducible academic research. It currently includes one complete workflow and its example artefacts.

## Skills

### [scopus-research](scopus-research/SKILL.md)

**End-to-end Scopus literature research.** Takes a research topic in any language and guides the agent through an institutional Scopus session using browser control.

The workflow:

1. creates a timestamped output directory;
2. enriches the topic, including Portuguese-to-English translation, synonyms, variants and concept blocks;
3. shows the proposed advanced-search equation and lets the user adjust it before searching;
4. runs the query in Scopus and sorts the results by relevance;
5. exports up to 2,000 records as CSV with abstracts, author keywords, indexed keywords and references;
6. analyses relevance-ranked and most-cited papers, journals, years, keywords, document types and open-access status;
7. ranks the most-mentioned references with resolution links and stated parsing caveats;
8. filters a focused title/abstract subset and reports its statistics.

Expected deliverables are `scopus_export_full.csv`, a focused subset CSV, `query.txt` and an analysis summary in the conversation, stored below `./pesquisas/scopus/<date-time> - <topic>/`.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `TOPIC` | Yes | The research question or subject, in any language. |
| `FOCUS_TERMS` | No | Terms used to filter the focused title/abstract subset; otherwise derived and confirmed. |
| `MAX_EXPORT` | No | Export ceiling, default 2,000. |
| `OUT_ROOT` | No | Output root, default `./pesquisas/scopus/`. |

## Requirements and boundaries

- A Chrome session with remote debugging enabled and the user's authenticated Scopus/institutional session.
- `browser-harness` for browser control and Python 3 standard library for CSV analysis.
- The agent must show the equation before searching and report the 2,000-record export ceiling honestly.
- The workflow does not use a fresh browser profile unless the user accepts losing the existing session.
- The research query is performed in Scopus, not through a general web search.

The skill's own [README](scopus-research/README.md) contains a concise usage guide, requirements, syntax notes, limitations and the example file map. The full [SKILL.md](scopus-research/SKILL.md) contains the browser procedure, export details, analysis rules and known UI pitfalls.

## Nested examples

The [examples](scopus-research/examples/README.md) folder documents a validated Scopus run about artificial intelligence for eldercare. It contains a query, representative CSV exports and the full/subset analysis reports. These files are examples of output format and provenance, not a replacement for running a fresh search.

## Folder structure

```text
Research/
├── README.md
├── README_PT.md
└── scopus-research/
    ├── SKILL.md
    ├── README.md
    └── examples/
        ├── README.md
        ├── query.txt
        ├── scopus_export_full_HEADER_ONLY.csv
        ├── scopus_eldercare_subset_SAMPLE.csv
        ├── analysis_full_export.md
        └── analysis_subset.md
```

## Choosing this skill

Use `scopus-research` when the task needs a documented Scopus search, a relevance-sorted export, bibliometric summaries, reference-frequency analysis or a focused subset. It is not intended to fabricate literature findings, bypass institutional access, or treat a relevance slice of 2,000 records as the complete Scopus corpus.
