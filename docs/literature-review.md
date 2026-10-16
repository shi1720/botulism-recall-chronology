# Targeted literature and overlap review

Search date: 16 October 2026. This is a targeted novelty assessment, not a
systematic review or proof of absolute priority. Public web searches and
Europe PMC were used. The broad Europe PMC query returned 980 hits and only
the first 100 were retrieved; narrow queries returned four and three hits.
Their exact queries and returned metadata are in `literature-search.json`.

## Closest work

1. Tang JS, Li P, Chen J. Scientific Reports 2026;16:27140.
   DOI: 10.1038/s41598-026-57837-z.
   Studies severity and firm/hazard structure across openFDA food records.
   Already reports about 65% Class II for C. botulinum product records.
   Therefore “botulism recalls are often Class II” is NOT a new contribution.
2. Zhang W, Wong CWY, Schaneberg B. Foods 2026;15:3115.
   DOI: 10.3390/foods15173115.
   Studies hazard counts, trends and classification lag; already identifies
   the risk of using report/classification dates for recall trends and models
   general classification lag. Therefore the existence of administrative lag,
   or recommending initiation-date anchoring in general, is NOT new.
3. Chen H, Xue Z, Yao M, et al. Journal of Food Protection 2026;89:100909.
   DOI: 10.1016/j.jfp.2026.100909. Online 8 September 2026.
   Studies pathogen–food combinations; already reports seafood concentration
   for C. botulinum. Therefore seafood concentration is NOT new.
4. Rao AK et al. MMWR 2021;70(2):1–30.
   DOI: 10.15585/mmwr.rr7002a1.
   Clinical guidelines; supports the clinical importance and distinct pathways
   of botulism, not the paper's original statistical results.

## Bounded contribution

A botulism-specific event cohort with severity-interval inference, exact
single-event product-count influence, threshold composition, and documented
counterexamples to treating an enforcement report date as a warning date.
The targeted search did not find this exact combined analysis. Its novelty is
incremental; it does not establish a new epidemiologic phenomenon, treatment,
LLM architecture, or patentable invention. The primary association is null and
imprecise. A poster/short observational report is a more defensible positioning
than a claim of a groundbreaking intervention or guaranteed platform selection.

## Prior-paper overlap

The user's Downloads/research folder was inventoried, including its index.
The first two pages of all top-level PDF papers were extracted and screened
for toxicology, botulism, poisoning, recalls, and relevant data sources.
The closest healthcare works are FHIR-Slice (partial clinical-data retrieval),
CARA-MIC (healthcare informatics) and polyp component cleanup (segmentation).
They do not examine FDA food-recall events or this empirical question.
This was a scoped overlap screen, not a full-text plagiarism audit.

## Documentary source checks

- True Taste, event 63914: original registry initiation 2012-12-14; report
  2018-05-23. A company notice dated 2012-12-18 is preserved by Indiana Health:
  https://www.in.gov/health/food-protection/files/Freshway_Foods_Recall_3.pdf
- Lyons Magnus, event 90667: registry initiation 2022-07-22; report 2022-09-07.
  FDA's original July announcement names Cronobacter, while the expansion
  dated 2022-08-10 names C. botulinum and says it had not been found in products.
  This is evidence against assuming current hazard text was available at initiation.
- ByHeart, event 97959: registry initiation 2025-11-08; report 2025-12-17.
  FDA's 2025-12-15 news release documents the initial November 8 action and
  November 11 expansion, before that enforcement-report date.

These are purposefully selected examples, not a representative validation sample.

## Practical and commercial context

Existing trackers already ingest FDA/FSIS recall feeds; RecallBench and other
public services expose botulism lists and event groupings. A generic recall
dashboard is not a defensible novelty claim. A possible implementation focus is
versioned event linkage, separate announcement/report/ingestion clocks and
deduplication for institutional workflows. Customer demand, time saved, willingness
to pay, safety improvement, intellectual property and market size have not been
measured. They should not appear as empirical findings of this study.
