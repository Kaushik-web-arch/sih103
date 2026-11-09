# Phase 1 — prediction data feasibility

Status: **in progress; training is not approved**. This document supersedes earlier model suggestions as an implementation plan. Work is published only in `Kaushik-web-arch/sih103`. Deployment remains Phase 7.

## Update: completed-table evidence

The original ongoing-history audit remains unchanged. A separate reviewed-layout extractor now recovers 227 completed-table records, including 92 reported actual months. These are evidence candidates, not approved training labels. June has no actual-date column, and final outturn cost remains unverified. See [completion evidence](completion-evidence.md) for measured linkage coverage and exclusions.

## Evidence available now

The pinned catalog contains April–August 2026, with expected monthly counts 1,981 / 1,987 / 1,847 / 1,775 / 1,731 (9,321 snapshots). The established full dataset has 2,111 project codes and 7,202 adjacent comparisons. These totals are baseline evidence, not independent training examples or a new full-data audit run.

All five catalog publication dates and first-availability dates are null. Submission/reporting cutoffs are not release dates. The ongoing-project schema has no verified actual completion date or final outturn-cost label table. An ongoing row disappearing does not supply either outcome. The documented project split requires lineage review before any project-held-out split.

The 2026-08 literal revised-cost zeros are preserved; they are not substituted, forward-filled or treated as verified final costs. V1's conservative pair eligibility remains unchanged. A new forecasting eligibility policy needs its own review and version.

## Reproducible audit

From the project root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_prediction_readiness.py -v
.\.venv\Scripts\python.exe scripts\audit_prediction_readiness.py
```

The new standard-library script reads the manifest/catalog and, if present, the full generated history. It checks pinned catalog/history hashes, source identifiers and per-month counts; it reports missing/zero/nonzero numeric coverage and observed months per project code. It never changes raw data, creates labels, imputes numbers, trains models or activates a revision.

When full history is absent, counts are null and status is `not_available`, rather than claiming zero records or profiling the frontend samples. Full-bundle import validation remains the existing importer's responsibility. `training_approved` deliberately remains false: passing a profiling check cannot approve label semantics, availability evidence or evaluation design.

The nine synthetic boundary tests exercise zero/missing distinctions, unknown dates, missing files, changed hashes, duplicate identities, source mismatch, nonfinite numbers and count mismatches. Their synthetic data is testing material, never model evaluation evidence. The initial run passed all nine in the remote development environment. The full 80-test PostgreSQL suite has not been rerun for this addition; its prior laptop result remains recorded separately.

## Preliminary CUF correspondence

The official MoSPI concept note includes CUF definitions and milestone monitoring. Its form covers sanction/start/target dates, sanctioned cost, expenditure and scheduled/actual progress. This table is a preliminary semantic correspondence, not proof that every published PDF field is a complete CUF export.

| Existing extracted field | Potential use | Restriction |
| --- | --- | --- |
| Project code, legacy code, PMGID | Identity linkage | Preserve strings; review splits and collisions; avoid memorizing IDs as predictors |
| Ministry, sector, agency, state | Context at forecast time | Preserve reported labels and dated changes |
| Approval/start month | Project age | Month precision only; no invented day |
| Original target/revised target month | Schedule baseline and revisions | Planned/reported dates, not actual completion |
| Original/revised cost | Sanction/revision context | Review baseline changes and reported zeros |
| Cumulative expenditure | Spending history | Not final cost until independently established |
| Reported physical progress | Progress history | Reported decreases may reflect corrections; scheduled progress unavailable |
| Source hash/page and report month | Provenance and chronology | Report month does not establish availability |

Absent from the current extracted schema: verified actual completion/final cost, planned-progress trajectories, detailed milestones and bottleneck resolution events. They must be sourced, not synthesized. The official form is broader than the ongoing-table extract.

## Target contracts before modelling

| Proposed target | Evidence required | Current status |
| --- | --- | --- |
| Actual completion delay | Verified completion month/date; explicit baseline target; baseline frozen at forecast; label source | Blocked: actual outcome labels absent |
| Final cost overrun | Verified final outturn cost; explicit sanctioned baseline and scope; label source | Blocked: final-cost labels absent |
| Future reported target postponement | Later reported target; identity continuity; known feature availability; fixed horizon | Research proxy only; not actual delay |
| Future reported cost revision | Later comparable revised cost; scope/quality review; fixed horizon | Research proxy only; not final overrun |

Completion delay months and percentage final-cost overrun are candidate measures, not approved definitions. Distinguish signed deviations from positive overruns. Missing outcomes are censored/unknown, not negatives. Baseline costs <= 0 cannot support percentage labels. Do not derive a label from the same revised value supplied as an input at the same date. No prediction horizon or accuracy threshold has been selected arbitrarily.

## Additional report ingestion work remaining

1. Locate official older/newer PDF downloads and record retrieval URLs and hashes. Retrieval time is an observation bound, not a fabricated original publication date.
2. Stage candidates separately from the immutable V1 catalog. Inspect layout, table coverage, date precision, notes and reviewed cells before extraction.
3. Define a new versioned report-registration/validation path; retain regression checks for all original five reports. The new audit does not itself generalize ingestion.
4. Reconcile project identity and splits across sources; preserve original identifiers and evidence-backed linkage separately.
5. Locate completed/commissioned project records, sanctioned baselines and final-cost evidence. Reconcile these explicitly; headline completion counts alone are insufficient labels.
6. Record source availability evidence and identify any need for authorized OCMS/PAIMANA historical exports. No private portal access or government integration is claimed.
7. Produce a target coverage table and decide which tasks are feasible before Phase 2 begins.

## Official source register (checked 9 November 2026)

- Report listing: https://paimana-proj.mospi.gov.in/ReportPage
- Archive listing: https://paimana-proj.mospi.gov.in/ReportPage/ArchiveProjectMonitoring
- CUF concept note: https://ipm.mospi.gov.in/Content/pdf/Concept%20note%20to%20Line%20Ministries%20dated%204%20Sept%202024.pdf
- Existing pinned five-report release: https://github.com/PrithvirajKhokale/Sentinel/releases/tag/source-reports-2026-v1

The official report and archive pages were reachable, but their retrieved HTML exposed selector controls rather than direct additional PDF links. No additional report was downloaded or validated in this increment. The CUF concept-note contents were retrieved; it also distinguishes public reporting from some government-only summaries. Do not assume all historical outcomes are publicly accessible.

The official SIH problem-statement page previously returned HTTP 403. The seven-phase requirements mapping remains provisional against the reproduced statement until the official text can be verified; the CUF note is an independent primary source, not a substitute for the statement.

## Phase 1 exit gate

- Reviewed additional-source acquisition/registration workflow and regression-preserving ingestion implemented.
- Full local history profiled with this audit; results retained under ignored validation outputs.
- CUF correspondence reviewed and unavailable fields explicitly listed.
- At least one defensible future target with evidence-backed labels, or a documented data-access blocker and restricted claim.
- Availability and identity/lineage evidence adequate to design leakage-resistant experiments.

Phase 1 is not complete until these gates are met. More monthly reports alone do not establish outcome labels or enough independent evaluation periods.
