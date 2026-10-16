# Botulism-hazard food recall chronology

Reproducible exploratory research on FDA food-enforcement records, by Shivam Gupta.

## Research question

Among already reported recalls whose current reason names a botulism hazard,
do recorded initiation-to-report intervals differ between Class I and II?
How do product-entry multiplicity and administrative chronology affect interpretation?

## Main results

The 14 October 2026 export, downloaded 16 October, contains 29,485 records.
Selection by initiation during 2012–2025 and `botul` in the reason yields
327 product records, 81 firm-events, and 79 normalized firm names.
The overall median recorded interval is 47 days (IQR 32–68).
The Class II minus I median difference is −1.5 days (firm-cluster bootstrap
95% CI −16 to 19.5). This does not establish a severity difference or equivalence.
One event accounts for 77 of 113 Class I product entries.

**Important:** these are administrative date intervals in a current snapshot.
They are not delays to public warning, intervals to diagnosis or treatment,
confirmed toxin prevalence, or patient outcomes. Historical database contents
cannot be reconstructed from these fields. Shared incidents can span firms.

## Reproduce

Python 3.12 was used. From this directory:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/analyze.py
.venv/bin/python -m unittest discover -s tests -v
```

The frozen original data are included; no API key or live download is needed.
Running the analysis regenerates `results/summary.json`, the event table, and
three figures in PNG and vector PDF. The bootstrap performs 20,000 draws with
seed 1720406. Dependency versions are pinned in `requirements.txt`.

## Files

- `data/raw/food-enforcement.json.zip`: unchanged FDA bulk export.
- `data/raw/download_manifest.json`: download catalog retrieved with the export.
- `data/derived/events.csv`: one row per firm-event, including membership text.
- `data/derived/matching_records.json`: the 327 matching records.
- `results/summary.json`: full estimates, uncertainty and sensitivity results.
- `src/analyze.py`: cohort extraction, analysis, plots and diagnostics.
- `tests/test_analysis.py`: duplicate rejection, row-order invariance, unit-of-analysis,
  date arithmetic, threshold and reproducibility checks.
- `docs/analysis-plan.md`: plan recorded before interval calculations, after inspecting
  candidate text and severity counts; this is not a preregistration.
- `docs/literature-review.md`: closest prior work and limits of the contribution.
- `docs/literature-search.json`: query metadata; broad query retrieves only the first
  100 records and is not a systematic review.

## Provenance

Source: https://open.fda.gov/apis/food/enforcement/download/

Archive SHA-256:
`7f8e2b5bd6e05e0cbf15e43860c74538ad09e1f8b07928e9c92de3ead3dac9c6`

Code is MIT licensed. FDA data retain their source terms:
https://open.fda.gov/license/ and https://open.fda.gov/terms/ .
Inclusion is not regulatory endorsement; retain FDA's source disclaimer.

The full manuscript is kept separate from this public code repository while
ACMT 2027 abstract review is pending. The abstract was submitted on 16 October
2026 as submission 7; no acceptance is claimed. This study has not undergone clinical validation.
