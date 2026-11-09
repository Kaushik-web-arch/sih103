# Completed-project evidence extraction

Verified remotely on 9 November 2026 against the five exact V1 PDF hashes. This corrects the earlier assumption that the available PDFs offered no actual-completion evidence: Table 3 has useful reported dates in four months. The original ongoing-table schema still has no actual-completion field.

## Implemented and measured

`scripts/extract_completion_evidence.py` extracts Table 3 separately from V1's ongoing-project data. It checks the pinned catalog/PDF/history hashes, compares every physical record cell using PyMuPDF and pdfplumber (ignoring whitespace only), checks serial continuity, duplicate codes, reviewed page/count coverage and section count totals, and checks seven visually transcribed reference records spanning all five reports. This establishes extraction reproducibility, not independent certification of the ministry-reported outcomes.

| Report | PDF pages (1-based) | Completed-table records | Reported actual months | Missing actual value | Actual column absent |
| --- | --- | ---: | ---: | ---: | ---: |
| April | 35 | 9 | 7 | 2 | 0 |
| May | 35 | 16 | 13 | 3 | 0 |
| June | 36–42 | 130 | 0 | 0 | 130 |
| July | 36–37 | 25 | 25 | 0 | 0 |
| August | 37–39 | 47 | 47 | 0 | 0 |
| Total | | 227 | 92 | 5 | 130 |

All 227 records retain seven source cells, project code, PDF page, source hash and month precision. June lists only original/revised targets: the extractor explicitly returns `actual_completion_month: null`, `actual_date_status: column_absent`. It never substitutes the revised target or the report label.

Raw original/revised cost and expenditure are retained. The reports warn that cumulative expenditure may not be actual completion cost. Consequently `final_outturn_cost` remains null for every record, including rows whose revised cost equals expenditure or is literally zero.

## Linkage feasibility, not model accuracy

218 completed-table records have a code appearing somewhere in the V1 ongoing history. Among the 92 records with reported actual months:

- 31 have at least one matching ongoing snapshot with an earlier **report label month**.
- 66 have a matching ongoing snapshot at or after the reported completion month.
- Six give an actual month later than their report label. Reporting/submission lag must be reviewed; this is not automatically a fabricated date.

These counts overlap. A code match is not reviewed scope/identity continuity. An earlier report month does not establish that its inputs were available before completion. The output includes code-match months and row-level review flags, rather than silently treating these as eligible training samples. No forecast model or accuracy claim is produced.

## Run on Windows

After the existing PDF acquisition and dataset rebuild, from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\extract_completion_evidence.py
.\.venv\Scripts\python.exe -m unittest tests.test_completion_evidence -v
```

Output: ignored `data/validation/completion-evidence.json`. A run first marks its output `running`, then `failed` on error or `extracted_for_review` on success. The status is never `training_approved`. This script does not migrate/import data, alter API responses, modify the manifest, or overwrite the original dataset. It supports these reviewed layouts only; additional reports remain candidate inputs requiring review.

The seven fixtures were transcribed from rendered PDF pages: April 35 (705503), May 35 (612188), June 36 (701105), July 36 (701406), August 37 (612851, 702637, 618062). They cover actual-date absence, source NA, literal zero revised cost, and a completion event predating its report label. They are a subset, not visual inspection of all 227 records.

## Next evidence needed before Phase 2

1. Review the 31 potential pre-event code matches, including actual source availability, identity/scope, baseline changes and contradictory later ongoing records. Preserve exclusions with reasons.
2. Obtain more historical ongoing snapshots with evidence of when they were available. A five-report window and 31 preliminary matches are not a validated evaluation population.
3. Obtain project-matched verified final outturn costs and comparable sanctioned baselines. The current expense/revised-cost fields cannot supply this target honestly.
4. Freeze target definitions, forecast horizons, censoring policy, project-family groups and time-held-out evaluation before training. Report both outcome coverage and exclusions.

The current evidence supports further schedule-label research. It does not close Phase 1 or establish that actual delay and cost-overrun prediction have been solved.
