# Phase 1 — full local audit results

Evidence: user-supplied Windows PowerShell output from the audit at code commit `0644d9d4898faafcacb0d0b65481e3911a364dca`. This records the local run; it is not a new remote execution or an approval to train.

- Nine readiness tests passed in 0.283 seconds.
- Dataset revision: `756d0304736b2f6a61a5fee7363a07e23c583611319fd4f17699ac6f4942d24a`.
- History status: `profiled_pinned_bytes`.
- Snapshot count: 9,321; distinct project codes: 2,111.
- Validation scope: pinned manifest/catalog/history hashes, snapshot identities, source hashes and counts. Full bundle validation remains the importer’s responsibility.
- `training_approved` remains false.

## Numeric coverage

The four audited numeric columns have zero missing and negative values across all five months. Physical progress has no values above 100. This is a coverage/range result, not proof of semantic accuracy or forecasting suitability. Date-field completeness is not measured by this numeric audit.

| Month | Snapshots | Zero expenditure | Zero physical progress | Zero original cost | Zero revised cost |
| --- | ---: | ---: | ---: | ---: | ---: |
| April 2026 | 1,981 | 302 | 95 | 0 | 0 |
| May 2026 | 1,987 | 303 | 108 | 0 | 0 |
| June 2026 | 1,847 | 260 | 91 | 0 | 0 |
| July 2026 | 1,775 | 135 | 81 | 0 | 0 |
| August 2026 | 1,731 | 51 | 68 | 0 | 1,731 |

Every August revised cost is a reported zero. Preserve these source values; do not treat them as final outturn costs, free projects, or automatic negative examples of cost overrun. Modelling use requires an explicit field-specific comparability policy.

## Longitudinal coverage

| Observed months per code | Project codes |
| --- | ---: |
| 1 | 69 |
| 2 | 192 |
| 3 | 141 |
| 4 | 100 |
| 5 | 1,609 |

The distribution reconciles to 2,111 codes and 9,321 snapshots. Codes appearing in all five months do not thereby establish stable identity/scope, final outcomes, or independence between observations. Five months provide only four adjacent report transitions; 9,321 rows are not 9,321 independent temporal outcomes.

## Remaining Phase 1 gates

- [x] Run readiness tests on Windows.
- [x] Profile full pinned history and reconcile counts.
- [ ] Locate and review additional official reports and implement a versioned candidate-ingestion workflow.
- [ ] Establish actual completion/final-cost labels with provenance, or document restricted proxy targets explicitly.
- [ ] Recover report first-availability evidence; all five values are currently unknown. Reporting cutoffs cannot substitute.
- [ ] Review identity splits, baseline changes and field-specific quality eligibility.
- [ ] Approve forecast horizon and temporal/project-separated evaluation design based on available evidence.

The next work is additional-source and label acquisition, not model fitting. Refer to [data feasibility](data-feasibility.md) for target contracts and official source links. Deployment remains Phase 7; updates go only to sih103.
