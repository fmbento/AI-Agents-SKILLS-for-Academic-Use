---
name: scopus-research
description: >
  Full Scopus literature-research workflow: build an enriched advanced-search
  equation from a research topic (any language, PT→EN enrichment), run the
  search relevance-sorted in Scopus via browser control, export up to 2000
  records as CSV with abstracts, keywords and references, analyze the CSV
  (top-cited papers, journals, years, keywords, most-mentioned references),
  and save a focused-keyword subset CSV. Outputs go to
  ./pesquisas/scopus/<day-time> - <topic>/.
---

# Scopus Research Skill

End-to-end literature research on Scopus driven through browser control, from a
research topic (pergunta de investigação) to analyzed CSV deliverables.

## Inputs

| Input | Required | Meaning |
|-------|----------|---------|
| `TOPIC` | yes | The research question subject. May be in Portuguese or any language; enrich to English. |
| `FOCUS_TERMS` | optional | Key terms that define the specific sub-field (e.g. a technique). Used only in Step 6 filtering. If not given, derive 3-6 terms from the TOPIC and confirm with the user. |
| `MAX_EXPORT` | optional | Export ceiling, default **2000** (Scopus CSV export maximum per run). |
| `OUT_ROOT` | optional | Output root, default `./pesquisas/scopus/`. |

## Tools Required

- **browser-harness** (the `browser-use` agent skill): install with
  `uv tool install --python 3.12 --upgrade --force browser-harness`.
  Invoke as `browser-harness <<'PY' ... PY` heredocs. Helpers used:
  `new_tab`, `goto_url`, `wait_for_load`, `page_info`, `js`, `click_at_xy`,
  `scroll`, `cdp` (for `Page.captureScreenshot`).
- **python** (standard library only: `csv`, `re`, `collections`, `pathlib`,
  `datetime`) for CSV analysis, subset filtering, and reference ranking.
- **web_search / read_url** (backend search tools) — only to confirm Scopus
  operator syntax if unsure; do not use for the literature search itself
  (Scopus requires the institutional session).

## Prerequisites (validated on this machine)

1. Chrome must be running **with remote debugging enabled**
   (`chrome://inspect/#remote-debugging` → tick "Allow remote debugging for
   this browser instance" → **full restart of Chrome**). If the daemon fails
   with `DevToolsActivePort not found`, guide the user through this before
   proceeding. The Scopus session is usually authenticated by IP or existing
   login in the user's Chrome profile — do NOT use a fresh/isolated profile
   unless the user accepts losing the session.
2. User must have Scopus access (check for "Signed in" or institution branding
   on the page; the user menu shows their initials).

## Step 0 — Output directory

Create and remember the run directory (kebab-case topic slug):

```
python - <<'PY'
from pathlib import Path
from datetime import datetime
slug = "machine-learning-eldercare"           # kebab-case TOPIC slug
d = Path("./pesquisas/scopus") / f"{datetime.now():%Y-%m-%d_%H-%M} - {slug}"
d.mkdir(parents=True, exist_ok=True)
print(d)
PY
```

All deliverables go here. Report the path to the user at the end.

## Step 1 — Build the search equation (do NOT search yet)

Produce a Scopus **advanced search** equation. Rules (Scopus syntax,
<https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl> and the
"Search tips" panel on the advanced-search page):

- Field codes: `TITLE-ABS-KEY(...)` for topical blocks; `PUBYEAR`, `DOCTYPE`,
  `LANGUAGE` as optional limiters.
- Boolean: `AND`, `OR`, `AND NOT`; proximity: `W/n` (within n words, ordered),
  `PRE/n` (precede within n); wildcards `*` (any chars) and `?` (one char).
- **Exact phrases in double quotes**; multi-word expressions can also be
  braced (`{exact form}`) to disable stemming — prefer quotes for normal use.
- Enrichment (do this explicitly, then show the user before searching):
  1. Translate the TOPIC to English if given in Portuguese; keep PT synonyms
     only if the corpus may contain PT (Scopus is overwhelmingly English —
     add PT terms only on request).
  2. Add technical synonyms and variants: singular/plural, wildcarded stems,
     abbreviations and spellings (e.g. `artificial intelligence` OR `AI` —
     beware `AI` over-matching; test counts), British/American spellings,
     related techniques.
  3. Structure: 2-4 concept blocks of OR-groups joined by `AND` — e.g.
     `(concept-technology block) AND (population block) AND (context block)`.
  4. Show the equation + rationale to the user; let them adjust before
     running. Note the count from each block if useful.
- Example shape (from the validated session, topic "AI for elderly care"):

```
TITLE-ABS-KEY("artificial intelligence" OR "machine learning" OR "deep learning"
  OR robotics OR "assistive technology" OR "smart home")
AND TITLE-ABS-KEY(elderly OR "older adults" OR senior* OR geriatric*
  OR "aged population")
AND TITLE-ABS-KEY(eldercare OR "assisted living" OR healthcare
  OR "independent living" OR caregiving)
```

## Step 2 — Run the search, sorted by relevance (browser)

1. `new_tab("https://www.scopus.com/search/form.uri?display=advanced")`
2. The query box is a **contenteditable div** `#searchfield`, NOT a textarea.
   Insert text with `execCommand` (raw value assignment does not register):

```js
const f = document.getElementById('searchfield');
f.focus();
document.execCommand('selectAll', false, null);
document.execCommand('insertText', false, QUERY_STRING);
f.dispatchEvent(new Event('input', {bubbles: true}));
```

3. Verify `document.getElementById('searchfield').innerText` equals the
   equation before submitting.
4. Click the submit button `button#advSearch` (`.click()` via `js`).
5. `wait_for_load()`; confirm URL starts with
   `https://www.scopus.com/results/results.uri` and read the document count
   from `document.body.innerText` ("N documents found").
6. **Sort by relevance** (the skill default): open the "Sort by" dropdown and
   choose **Relevance**, or append `&sort=relevancy` style param — in the
   current UI the sort control is in the results toolbar; confirm the results
   header shows "Relevance" after selection. Relevance is the export order
   basis.
7. Screenshot evidence (optional, cheap):
   `cdp("Page.captureScreenshot", format="png")` → save into the run dir.

## Step 3 — Export CSV (max 2000) with Abstract & keywords + references

UI path (validated): results toolbar → **Export** → format tiles **CSV** /
RIS / Refworks / Zotero / EndNote → panel "What information do you want to
export?":

1. Click toolbar **Export** button (it may be below the fold: scroll it into
   view with `scrollIntoView({block:'center'})` before `click_at_xy`).
2. Click the **CSV** tile.
3. Scope radio: choose **"Documents"** (not "All documents on this page"),
   then fill the visible `input[type=number]` (aria-label **"To"**) with
   `MAX_EXPORT` (default 2000). Use `execCommand('insertText')` after focus,
   then dispatch `input` + `change`.
4. Tick **all** checkboxes under **"Abstract & keywords"**: Abstract, Author
   keywords, Indexed keywords.
5. Tick **"Include references"** under **"Other information"** — this adds
   the References field used in Step 5 for the most-mentioned-references
   ranking.
6. Click the dialog's **Export** button
   (`[role=dialog]` → button whose first text line is exactly "Export").
   Expect toast: "Preparing N documents for CSV export / Export will start
   shortly."
7. The dialog may briefly show "You need a valid selection to be able to
   export" inside the button while remaining enabled — that is a quirk; the
   export proceeds.
8. Poll the browser's download directory for `scopus_export_*.csv` until no
   `*.crdownload` remains (large exports take a minute or two).
9. Move the CSV into the run directory (Step 0) as `scopus_export_full.csv`
   and validate: 2001 rows (header + records), 22-23 columns, `Abstract`
   and `References` headers present.

Known export quirks (browser-harness/CDP):
- Dialog panels use `position:fixed` → `offsetParent` is null; detect
  visibility via `getBoundingClientRect().width > 0` instead.
- `js()` runs a persistent JS context: wrap snippets in IIFEs and never
  redeclare top-level `const`.
- Escape carefully: the heredoc body is Python + JS; avoid unescaped quotes
  breaking either layer.

## Step 4 — Analyze the full export (python, stdlib only)

Read with `encoding='utf-8-sig'` (Scopus emits BOM). Produce a written
summary for the user:

0. **Top 20 most relevant FIRST** — when the export is relevance-sorted,
   the first 20 rows of the CSV are Scopus's own relevance ranking. Report
   them as a table **before** the most-cited table, noting that relevance
   favors dense term matches (recent conference papers with 0 citations
   appear) — it is a matching-quality ranking, not an impact ranking.
1. **Top 20 most-cited** (sort by `Cited by` desc, tie-break `Year` desc).
   For each: title, year, journal, citations, and links (Step 4b).
2. **Most frequent journals** (`Source title` counter, top 15).
3. **Publication years** (`Year` counter sorted by year).
4. **Keywords**: split `Author Keywords` and `Index Keywords` on `;`,
   lowercase, trim, count separately (top 15 each).
5. **Document types** and **Open Access** split.
6. Note the sort caveat honestly: a relevance-sorted 2000-slice covers the
   most relevant records, not the full corpus; say so in the report.

### 4b — Permanent links (exact formats, validated)

- **Scopus record link:** `https://scopus.com/record/display.uri?eid=<EID>`
  (EID column, e.g. `2-s2.0-85064016092`). Note: plain `scopus.com`, no
  extra params needed — the earlier `partnerID=MN8TOARS` variant also works
  but is not required.
- **Full text / source link:** the DOI column → `https://doi.org/<DOI>`
  (strip anything after the first whitespace and trailing dots). Only emit
  a DOI link when a DOI actually exists in the row; conference/book rows
  often have none.

## Step 5 — Most-mentioned references (top 10)

Use the `References` column (only present if Step 3.5 was done). Scopus
reference strings look like:

```
Author, Year, Title, Journal, Volume(Issue), Pages, Publisher. DOI, [etc]
```

Strategy (heuristic but robust):
1. Split each row's `References` on `;` — Scopus separates individual
   references this way (careful: a few references contain internal `;`;
   accept minor over-segmentation).
2. Normalize each reference string: lowercase, strip numbers/punctuation,
   collapse whitespace; take a fingerprint = first 60 chars of author +
   year + first title words. Simplest reliable key: extract
   `(first-author surname, year)` or the DOI when present
   (`10.xxxx/...`).
3. Count across all rows; report the **top 10 most-mentioned references**
   with: reference string, count of citing papers in this corpus, and a
   **"Resolve via" column with TWO links** built from the reference's title
   fragment (drop the leading `Author, ` segment, cut at the last comma
   before the journal name):
   - Google exact-title search:
     `https://www.google.com/search?q=<url-encoded "title fragment">`
   - Scopus title search (relevance-sorted):
     `https://www.scopus.com/results/results.uri?sort=r-f&src=s&sot=a&sdt=a&s=TITLE-ABS-KEY%28%22<url-encoded fragment>%22%29`
   **Only emit `doi.org` links when a DOI is literally present in the
   reference string** — in the validated run (2026-09-08) Scopus reference
   strings carried **no DOIs**; never fabricate `doi.org` URLs.
4. State the method + caveats in the report (semicolon over-segmentation,
   fingerprint false-merges, missing DOIs → resolve links instead).

## Step 6 — Focused subset CSV

Filter rows whose **Title or Abstract** mentions the `FOCUS_TERMS`
(word-boundary regex, case-insensitive; include inflections: e.g. caregiv\*,
nursing home(s), elder-care/eldercare):

```python
import re
terms = {
  'eldercare': r'\belder[\s-]?care\b',
  'assisted living': r'\bassisted\s+living\b',
  # ... build from FOCUS_TERMS with \b word boundaries + inflections
}
blob = (r['Title'] + ' ' + r['Abstract']).lower()
matched = [r for r in rows if any(re.search(rx, blob) for rx in terms.values())]
```

Write `scopus_<focus>_subset.csv` in the run dir (same columns), and report:
- match counts per term,
- top 10 cited in subset,
- top journals / years / doc types / OA split / top author keywords,
- always `subset N of M papers` framing.

## Step 7 — Deliverables checklist (report to user)

In the run directory `./pesquisas/scopus/<day-time> - <topic>/`:
- [ ] `scopus_export_full.csv` (raw export, ≤2000 records)
- [ ] `scopus_<focus>_subset.csv` (focused filter)
- [ ] `query.txt` (final equation used)
- [ ] analysis summary in chat (top-20, journals, years, keywords,
      top-10 references with links, subset stats)

Report both CSV paths, the record counts, and the caveat about the
2000-record ceiling vs. the full result count.

## Analysis deliverables as markdown plus PDF

The analysis summary for the user is written in Markdown and stored in the run directory. Whenever the final written analysis is delivered as a `.md` file — for example `analysis_full_export.md`, `analysis_subset.md` or a comparable report — also generate the matching PDF with `Utils/scripts/generate_pdf.py` and place it in the same run directory. The skill does not replace the CSV deliverables with PDF; it keeps the CSVs as data artefacts and treats the Markdown report as the document artefact that gets a PDF companion.

Do not generate the PDF while the analysis is still in progress or while waiting for a substantive user decision about scope, focus terms or export size; the PDF step belongs after the written report is finalised. If `pandoc`/`xelatex` are not available, the Markdown report is still complete and the PDF is recorded as pending rather than silently skipped.

## Session-validated pitfalls

- **File-tool vs shell CWD divergence:** in some agent harnesses the file
  write tool resolves relative paths against the **project root**, while
  shell commands run in the session CWD (e.g. the user home). Write run
  artifacts with shell (`python`/`mv`) using absolute or CWD-relative
  paths, then verify with `ls` — a report landed in the wrong tree this
  way on 2026-09-08.
- Relevance sort control: a `<select>` whose options include
  `Relevance=r-f` — set `value='r-f'` + dispatch `change`; URL then shows
  `sort=r-f`. Options observed: `plf-f` (Date newest), `plf-t` (Date
  oldest), `cp-f` (Cited by highest), `r-f` (Relevance).
- Enrichment can over-match: `rehabilitat*` pulled bridge/infrastructure
  "rehabilitation" into a clinical corpus; `patient-specific model*`
  pulled pre-DT vascular modeling. Check the top-20 for off-domain papers
  and propose `AND NOT` blocks or subject-area limiters to the user.

- `#searchfield` is contenteditable — `execCommand('insertText')` only.
- Submit button is `button#advSearch`.
- Export dialog: CSV tile → radio "Documents" → number input aria-label
  "To" → checkboxes by exact label text → dialog "Export" button is the one
  whose first line is "Export" (the panel header button also contains the
  word Export — do not click that).
- `offsetParent` lies inside `position:fixed` dialogs; use bounding rect.
- Sort control: results toolbar "Sort by" → Relevance (re-export if you
  forget and the default was Date).
- Downloads land in the user's Downloads folder as
  `scopus_export_<Mon D-YYYY>_<uuid>.csv`; move them into the run dir.
- Always `encoding='utf-8-sig'` for Scopus CSVs.
- 138k+ result sets export at most 2000/run — do not try to loop exports to
  beat the cap without the user asking; different sorts select different
  slices (say this in the report).
