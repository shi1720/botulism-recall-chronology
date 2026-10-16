# Analysis plan: botulism-hazard recall reporting intervals

Recorded 16 October 2026 before calculating reporting-interval outcomes.
This is an exploratory retrospective registry cohort, not a preregistered study.
The full source, candidate reason text, counts and severity distributions were
inspected before this plan; interval outcomes had not been computed.

## Question and estimand
Among FDA food-enforcement recall events initiated during 2012–2025 whose stated
reason includes the case-insensitive string `botul`, do Class I events have
different recorded initiation-to-report intervals from Class II events?
The primary contrast is the unadjusted difference in medians (Class II minus I).
An adjusted log-interval ratio controls for centered calendar year and whether
the event product descriptions mention seafood. This is an association, not a
causal effect of classification. We do not interpret dates as warning dates,
clinical notification dates, or FDA detection/response delays.

## Cohort
Deduplicate by recall_number, reject inconsistent duplicates. Select records by
initiation date 20120101–20251231 and reason string `botul`; aggregate by event_id.
Require a valid event ID; report missing or inconsistent dates and classifications.
Use earliest matching record initiation and report dates for an event; repeat
using all records in the event and latest matching report date. Report Class III
descriptively; do not pool it with II for the primary contrast.

## Analyses
1. Event and product counts; medians and IQRs; severity-specific proportions
   with report intervals <=30, <=60 and <=90 days (Wilson intervals).
2. Class II minus I median difference, firm-cluster bootstrap percentile 95% CI
   (20,000 draws, seed 1720406); two-sided Mann–Whitney comparison (exploratory).
3. OLS of log(1+days) on Class II, year-2018, and a seafood indicator, firm-cluster
   robust SE; exponentiated Class II coefficient interpreted on (days+1) scale.
4. Compare class composition with event vs. product weighting; for events
   present in the current snapshot, calculate composition when retaining only
   intervals <=30/60/90. This is a retrospective interval-threshold analysis,
   not reconstruction of historical database contents or validated nowcasting.
5. Sensitivity: exclude 2012 (left boundary); exclude mixed-hazard events naming
   Cronobacter; restrict to >=2017; leave-one-event-out; exclude negative intervals;
   repeat date aggregation; unique normalized firm clusters; influence diagnostics.

## Interpretation boundaries
Registry completeness, free-text selection, evolving reporting procedures,
current rather than initial classifications, cross-firm shared contamination
incidents and absence of archived snapshots limit inference. No clinical
incidence, antitoxin benefit, confirmed toxin prevalence, or patient outcome can
be estimated. All analyses and sensitivity results will be reported, including
null or imprecise estimates. No hypothesis switching based on significance.
