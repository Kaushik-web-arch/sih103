# Source investigation — 8 November 2026

These are research leads, not a promoted dataset or training labels. No V1 catalog dates or source bytes were changed.

| Source | Evidence found | Remaining work |
| --- | --- | --- |
| [Official September release](https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2328472&lang=1&reg=1) | Posted 26 October 2026, 16:00; describes 1,853 ongoing projects and commissioning events | Acquire the full underlying report, bind its exact bytes and map event scope to project codes |
| [Official August release](https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2314852&lang=1&reg=3) | Posted 25 September 2026, 16:00; describes 1,731 projects | Establish whether the identical pinned PDF was available then; do not copy this date into the catalog automatically |
| [March report candidate](https://ipm.mospi.gov.in/Content/PDF/FlashReport_March_2026.pdf) | Official-host candidate URL | Direct acquisition returned HTTP 503 in this environment; no verified local PDF hash or extracted dataset was produced |

The September release reports commissioning dates for Buxar Thermal Power (12 September 2026), NMDC Slurry Pipeline Phase 1 (26 September 2026), and Delhi–Amritsar–Katra Phase I Package I (4 November 2025). These are **unlinked evidence candidates**, not labels: project codes, scope and prediction-time baselines still need verification. The last example also shows why report month cannot stand in for event date. Inauguration is a distinct event. None of these observations establishes final outturn cost.

The August release reports aggregate revised cost while the pinned ongoing-project rows contain literal zeros. Preserve both source observations and review comparability; do not distribute aggregate cost over projects or impute labels.

## Current gate

Readiness remains false. Additional sources offer a route to outcome evidence, but the verified five-month history alone does not supply actual completion and final-cost labels, evidence-backed availability dates, or an approved evaluation design. A model trained on future reported revisions would be a separately named proxy experiment, not proof of actual delay/overrun prediction accuracy.

See [candidate intake](candidate-intake.md) for implemented staging and the remaining extraction/review/promotion steps. Deployment stays Phase 7.

## Follow-up: 9 November 2026

The alternative official [PAIMANA archive URL](https://paimana-proj.mospi.gov.in/Content/ArchiveReport/flash/2025-26/FlashReport_March_2026.pdf) successfully supplied the March report. The older IPM URL still returned HTTP 503. Exact bytes and acquisition command are in [candidate intake](candidate-intake.md). March remains quarantined because the V1 extractor rejected its layout.

The existing five PDFs also yielded completed-table evidence directly, rather than relying only on press releases: see [completion extraction](completion-evidence.md). This supersedes the earlier status of no extracted actual-completion evidence, but it does not establish final cost or forecast-time availability.
