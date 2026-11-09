# Remote verification — 9 November 2026

Environment: Linux remote workspace, Python 3.12 and Node 24. This is not a new Windows laptop run. No dependency versions or lockfiles were changed.

- `npm ci`: passed.
- `npm test`: 11 passed, zero skipped.
- `npm run build`: passed.
- Pinned Python backend/extraction dependency installation and `pip check`: passed.
- Original five-source acquisition: all PDF hashes verified.
- Full `rebuild_dataset.py`: passed, with original source/code/reference hashes intact.
- `backend.import_dataset.validate_bundle`: passed; revision `756d0304736b2f6a61a5fee7363a07e23c583611319fd4f17699ac6f4942d24a`, 9,321 snapshots and 7,202 comparisons. This was validation, not database activation.
- Full Python discovery: 120 run, 90 passed, 30 PostgreSQL tests skipped. This includes 13 completion-evidence and six candidate-acquisition tests.
- Completion evidence: 227 records; both PDF readers agree on physical cells; seven visual fixtures passed. No training approval.
- March source: acquired and hash-pinned; V1 extraction rejected its layout. Candidate remains isolated.
- Native PostgreSQL: not available in this workspace. Installing the server failed because system package operations could not change user/group IDs. No SQLite substitute was used.
- Browser smoke: blocked during Chromium package extraction by filesystem `chown` EINVAL. Frontend contract tests/build passed; this is not a browser-pass claim.

The GitHub workflow now targets `main` and supports manual dispatch, includes scripts/config/dependency changes, and runs full backend discovery with a dedicated PostgreSQL 17 service database (`sentinel_tests`). It also runs frontend browser smoke on the standard Ubuntu runner. Workflow configuration is not itself evidence of a completed CI run; consult the actual run results.

No predictive model, accuracy result, new dataset promotion or deployment is claimed. Existing observed-risk behavior remains unchanged. Deployment stays the final phase.

## Completed GitHub verification

[Run 42550104581](https://github.com/Kaushik-web-arch/sih103/actions/runs/42550104581) passed for implementation commit `27ab2272230296323a7c6c6f270cebe1dc75c2a9`:

- Python: **120 tests passed in 25.759 seconds, zero skipped**, against native PostgreSQL 17 in the isolated CI service database `sentinel_tests` (not SQLite and not a live/shared database).
- Full five-report acquisition/rebuild, completion-evidence extraction and dependency consistency: passed.
- Frontend: **11 tests passed**, production build passed, and browser smoke passed (public connection flow, source evidence, exact filters, history drilldown). Browser smoke uses the existing mock API fixture; it does not establish a deployed service or live-data browser integration.
- Python syntax job: passed.

The local limitations above are retained as an accurate record of the workspace attempt; the separate standard GitHub runner completed those database/browser checks successfully. PostgreSQL error messages for attempted illegal mutations and invalid foreign keys in teardown logs are expected negative-test evidence; the test suite itself reports OK.
