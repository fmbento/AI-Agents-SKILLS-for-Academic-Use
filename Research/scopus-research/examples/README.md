# Example Outputs — validated run (2026-09-08)

Source session: topic **"artificial intelligence / eldercare"** (the query that
validated this skill). Files here are real outputs, trimmed for sharing.

| File | What it shows |
|------|---------------|
| `query.txt` | The exact advanced-search equation used |
| `scopus_export_full_HEADER_ONLY.csv` | First 10 rows of the raw CSV export (2000 rows in a real run). Note the 22 columns incl. `Abstract`, `Author Keywords`, `Index Keywords` |
| `scopus_eldercare_subset_SAMPLE.csv` | The complete focused-subset CSV (74 rows) — this one is NOT trimmed |
| `analysis_full_export.md` | Step-4 report written from the real run (date-sorted slice caveat visible) |
| `analysis_subset.md` | Step-6 report: filter terms, hit counts, subset stats |

## Column reference (Scopus CSV export, "Abstract & keywords" + citations)

```
Authors, Author full names, Author(s) ID, Title, Year, Source title, Volume,
Issue, Art. No., Page start, Page end, Cited by, DOI, Link, Abstract,
Author Keywords, Index Keywords, Document Type, Publication Stage,
Open Access, Source, EID
```

`References` appears as an extra trailing column when **Include references**
is ticked (Other information section) — it is the input for the
most-mentioned-references ranking.

## Rebuilding this run

```
TOPIC       = "use of AI for eldercare"
MAX_EXPORT  = 2000
FOCUS_TERMS = eldercare, assisted living, independent living, caregiv*, nursing home(s)
```
