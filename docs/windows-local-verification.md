# Windows local verification and handover

Recorded 9 November 2026 from the user's terminal outputs and the integrated V1 code review. This is a development handover, not a deployment or predictive-accuracy claim.

## Baseline and ownership

The extracted ZIP was compared against all 124 tracked files at team commit `4f7941dbb1b7adf641e5d5cd7f1363e4a190ce64`. Both the team and contributor fork's `main` branches were still at the earlier backend baseline when checked. Integrated V1 was on `feat/frontend-backend-integration` in draft PR #8.

The user's existing Windows folder was connected to that history on `feat/v1-local-upgrades`. Its tracked working tree was clean. `.env`, `frontend/.env.local`, and `.venv/` were confirmed ignored. Only `data/repair-backups/` was untracked; a local exclusion was subsequently recommended. This repository retains the integrated history and adds documentation of the setup completed so far.

## Resolved setup blockers

- Node and npm initially unavailable; frontend subsequently started successfully.
- CMD syntax was being pasted into PowerShell; setup commands now use PowerShell.
- Docker CLI installed before its engine was available. WSL was installed, Virtual Machine Platform was enabled in administrator PowerShell, and Windows restarted. Docker client/server and the hello-world container then passed.
- All five source PDFs were recovered and hash-verified using the existing acquisition script.
- `Catalog hash mismatch`: the ZIP contained LF bytes while the pinned revision expected CRLF for selected source inputs. `.gitattributes` specifies CRLF. Each affected catalog/computation/reference file was backed up and converted only if the result matched its expected SHA-256 exactly. The original manifest was preserved and outputs rebuilt. Prefer a Git clone for subsequent setup.
- Database connection timeout: Compose listed no database container and port 5433 was unreachable. Starting the existing `sentinel-backend` Compose project was the corrective step.
- The native backend does not load `.env` automatically. Backend configuration was supplied through process environment variables; the frontend proxy target was set separately.

## Verified checks and limits

- Frontend: 11 tests passed, zero skipped; Vite production build succeeded.
- Python: full discovery ran 80 tests in 48.173 seconds, all passed, zero skipped.
- PostgreSQL: real version 17 in Docker, dedicated `sentinel_tests` database; no native Windows PostgreSQL testing.
- Tests covered rollback, immutable records, full dataset import counts/idempotence, exact values and provenance, filtering, pagination, histories without fabricated gaps, portfolio reconciliation, pinned/scoped risk signals and source hash verification.
- User reported the running dashboard and its expected August revised-cost-zero warning. The entire manual browser acceptance checklist has not been recorded as completed.
- A successful application database import summary was not included in retained terminal logs; full import behavior and counts were independently exercised by the passing integration tests.
- GitHub CI for the source commit passed, but its backend test command selected only risk and backend modules. Expanding it to full discovery is planned.
- Test logs contained non-failing Starlette/httpx and Alembic deprecation warnings. No dependency upgrade was performed to suppress them.

## Local configuration and data

Keep `.env`, passwords, connection URLs, `.venv`, `node_modules`, build outputs, full PDFs, generated datasets, database files, revision archives and repair backups out of commits. Recover the pinned source reports via the existing acquisition script and rebuild using the existing validator. Never relax hashes to make an import pass.

The PostgreSQL database is exposed at loopback port 5433; FastAPI defaults to loopback port 8000; Vite prints its selected local port. Empty `SENTINEL_FRONTEND_DIR` is correct for a separate Vite development server. Test database configuration must remain separate from the application database.

## Proposed first changes

1. Repeatable Windows startup and consistent environment loading, respecting process-variable precedence and keeping secrets out of browser bundles.
2. Recoverable invalid history ranges: the current early error return hides the controls needed to correct the range.
3. Surface risk-response top-level source warnings.
4. Align CI coverage and stale documentation with the current public read-only API.
5. Plan additional report ingestion and dynamic month discovery as versioned V2 work.

Predictive ML remains unimplemented. Report-derived observations must stay separate from any future predictions, and project absence must not be equated with completion.
