# Additional-report intake (quarantine only)

This additive path accepts any report month without changing `config/monthly_reports.json`, the five-report history builder, the active database, or the pinned dataset revision. It is **not yet general extraction or automated dataset promotion**.

`stage_report_candidate.py` uses only the Python standard library. It verifies the supplied SHA-256, a PDF signature, month syntax and metadata syntax. It does not prove authenticity, validate PDF structure, verify a publication claim, or approve training. A hash records bytes; it does not independently prove that the source is official.

## Windows PowerShell workflow

Run from `C:\Users\msc\Downloads\Sentinel-V1\Sentinel-V1`.

1. Obtain a PDF from an official source. Record its exact URL, retrieval circumstances and SHA-256 independently. Do not reuse a failed HTML download as a PDF.
2. Write a local metadata JSON (for example `data\validation\candidate-metadata.json`):

```json
{
  "report_month": "2026-09",
  "source_url": "https://OFFICIAL-HOST/EXACT-REPORT.pdf",
  "expected_sha256": "REPLACE_WITH_VERIFIED_64_CHARACTER_LOWERCASE_SHA256",
  "publication_date": null,
  "first_available_date": null,
  "availability_evidence_url": null
}
```

This template deliberately fails until real source information is supplied. `Get-FileHash -Algorithm SHA256 <PDF>` computes a local digest; independently compare it with the recorded acquisition digest when copying or transferring the file. Keep unknown dates null. A press release date is evidence about that release, not automatically about identical PDF bytes.

3. Stage the source (replace the PDF path):

```powershell
.\.venv\Scripts\python.exe scripts\stage_report_candidate.py --pdf "C:\path\report.pdf" --metadata "data\validation\candidate-metadata.json"
```

Success prints a directory under `data\candidates\YYYY-MM\<sha256>`, `status: quarantined` and `training_approved: false`. It contains `source.pdf` and `candidate.json`. Repeated runs refuse to overwrite existing candidates. A changed source needs a new digest and review. Candidates are ignored by Git.

4. Inspect layout before trying the existing extractor. For a compatible ongoing-project table, use the unchanged V1 extractor with outputs **inside the candidate directory**:

```powershell
# Set this to the exact directory printed by staging.
$candidate = "data\candidates\YYYY-MM\SHA256"
.\.venv\Scripts\python.exe scripts\extract_ongoing_projects.py "$candidate\source.pdf" --all --output "$candidate\ongoing.csv" --validation "$candidate\extraction-audit.json"
```

An extractor success without reviewed reference fixtures is insufficient for promotion. Add visually checked fixtures with `--reference`, review every unresolved issue, reconcile report totals and preserve source cells. Incompatible layouts need a reviewed adapter, not relaxed validation. Completed-project tables need a separate adapter; this command only extracts ongoing projects.

5. Before promoting any candidate, review identity/splits, scope changes, dates and source quality; establish source availability evidence; and validate any proposed outcomes. Create a new dataset revision through an explicitly reviewed migration. Never replace the V1 catalog hash or mark candidate gates passed just to run training.

## Outcome evidence still required

Schedule labels need an actual completion or agreed commissioning event, its exact project scope/identity, evidence and known-at date, plus the baseline target applicable at prediction time. Preserve month-only precision. Distinguish inauguration from commissioning and partial commissioning from entire-project completion. Projects still ongoing are censored, not negative completed outcomes.

Cost labels need verified final outturn and a comparable baseline/currency/unit/scope. Latest estimated cost and cumulative expenditure are not automatically final outturn. August literal revised-cost zeros remain unchanged and require eligibility review.

Forecast horizons and time/project splits must be fixed before model comparison. Source reporting cutoffs cannot substitute for availability dates.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_report_candidate tests.test_prediction_readiness -v
```

The remote run passed 21 tests (12 intake, 9 readiness), with no skips. These are filesystem/metadata tests using synthetic fixtures; they do not exercise PostgreSQL or establish that a new official PDF parses correctly. The full frontend/backend suite was not rerun for this additive change.
