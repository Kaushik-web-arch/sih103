# Accepted delivery plan

All future updates go to **Kaushik-web-arch/sih103 only**. The existing Sentinel repository is a historical baseline. Follow these seven phases; deployment is the final phase. Scope additions must serve the problem statement or unblock a phase.

| Phase | Deliverable | Status |
| --- | --- | --- |
| 1. Prediction-ready data | Additional-report ingestion, CUF correspondence, source availability, identity review and verified label feasibility | In progress: full local audit confirmed 9,321 snapshots / 2,111 codes and nine readiness tests passed; candidate quarantine and 12 intake tests added; labels, availability, extraction review and promotion remain open |
| 2. Forecasts | Defined horizons/targets, statistical baselines and ML candidates for schedule and cost | Not started; requires Phase 1 evidence |
| 3. Predictive evaluation | Later-period and held-out-project evaluation; leakage checks, error/alert/lead-time metrics and uncertainty | Not started |
| 4. CUF value assessment | CUF-only evaluation and controlled comparison with legitimate additional data, or documented access limitations | Not started |
| 5. Early-warning decision support | Prioritized project review with forecasts, evidence, uncertainty and bounded suggested actions | Existing observed signals only; predictive integration not started |
| 6. End-to-end validation | Integration tests, representative-user walkthroughs, reproducible documentation and limitations | Baseline tests passed; predictive acceptance not started |
| 7. Deployment and handover | Hosting, database/model/data versions, security, backup/restore, monitoring, rollback and public verification | Not started; final delivery phase |

See [Phase 1 data feasibility](phase1/data-feasibility.md). A trained/deployed model is not sufficient evidence of useful forecasting. Actual outcomes must not be replaced silently with reported revisions, missing projects with completion labels, or missing availability with reporting cutoffs. LLM assistants and unrelated features are not automatically required.

Full local profiling evidence: [Phase 1 audit results](phase1/local-audit-results.md).

Additional-report work: [candidate intake](phase1/candidate-intake.md) and [official-source investigation](phase1/source-investigation.md).
