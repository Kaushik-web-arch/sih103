# Sentinel — SIH26103

Infrastructure project monitoring from monthly government reports. Sentinel turns reported project records into searchable snapshots, monthly history, portfolio comparisons, and evidence-backed change signals.

This repository continues the team's integrated V1 implementation. **It contains the integrated V1 dashboard, setup documentation, and initial Phase 1 prediction-readiness tooling. Predictive models and general additional-report ingestion are not implemented.**

## Origin and attribution

- Original team repository: https://github.com/PrithvirajKhokale/Sentinel
- Contributor fork: https://github.com/Kaushik-web-arch/Sentinel
- Integrated branch: `feat/frontend-backend-integration`
- Starting commit: `4f7941dbb1b7adf641e5d5cd7f1363e4a190ce64`
- Original integration PR: https://github.com/PrithvirajKhokale/Sentinel/pull/8

Original commits and authorship are retained. The previous root README is preserved at [docs/upstream-readme-v1.md](docs/upstream-readme-v1.md); its relative links refer to the original repository-root location. Some older documents describe superseded authentication or deployment stages. Check the current code and [frontend integration notes](docs/frontend-integration.md).

## What works today

- Project name search, exact-label filters, pagination, and project details.
- Monthly history with explicit report gaps and source evidence.
- Portfolio totals and adjacent-month comparisons that distinguish filter-scope changes from report absence.
- Observed signals: postponed revised targets, decreasing reported progress, and increased expenditure with unchanged reported progress.
- Explicit reference-example mode and live API mode.
- SHA-256 source verification, extraction audits, dataset revision pinning, immutable database records, and atomic revision activation.
- Responsive React interface with light/dark themes.

Signals are observations, not predictions or explanations of causes. A project missing from a report is not proven complete. Reported zeros remain zeros; missing values remain distinct. August's published revised-cost zeros intentionally generate a source warning.

## Stack and data

React/Vite frontend; FastAPI, SQLAlchemy, Alembic and psycopg backend; PostgreSQL 17. CI uses Node 22 and Python 3.12. The laptop verification used Node 26.13.0, npm 11.20.0 and Python 3.13.15.

The validated April–August 2026 dataset has **9,321 snapshots, 2,111 project codes and 7,202 adjacent comparisons**. Source PDFs, regenerated outputs, database contents, revision archives and credentials are separate from the source repository. The small tracked reference fixtures are examples, not the full portfolio.

## Windows setup — PowerShell

Install Git, Node.js 22+, Python with the pinned dependencies, and Docker Desktop using Linux containers. Enable WSL and Virtual Machine Platform when required, restart Windows, and wait for Docker's engine to run. Confirm both Client and Server appear:

```powershell
docker --context desktop-linux version
```

Clone with Git to retain the required `.gitattributes` line endings:

```powershell
git clone https://github.com/Kaushik-web-arch/sih103.git
Set-Location sih103
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-backend.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\acquire_reports.py
.\.venv\Scripts\python.exe scripts\rebuild_dataset.py
```

Run commands separately and stop on errors. Acquisition verifies the pinned release archive and individual PDF hashes. Rebuilding must pass before importing. Do not edit manifest hashes to bypass validation. See [Windows verification notes](docs/windows-local-verification.md) for the ZIP line-ending issue encountered during setup.

### PostgreSQL, migrations and import

From the repository root, in the terminal that will run the backend:

```powershell
$localPassword = Read-Host 'Local PostgreSQL password' -AsSecureString
$env:SENTINEL_DB_PASSWORD = [System.Net.NetworkCredential]::new('', $localPassword).Password
$encodedPassword = [uri]::EscapeDataString($env:SENTINEL_DB_PASSWORD)
$env:DATABASE_URL = "postgresql+psycopg://sentinel:$encodedPassword@127.0.0.1:5433/sentinel"
$env:APP_ENV = 'development'
$env:API_HOST = '127.0.0.1'
$env:API_PORT = '8000'

docker --context desktop-linux compose -f compose.backend.yaml -p sentinel-backend up -d --wait
```

After PostgreSQL reports healthy, run each separately:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m backend.import_dataset
.\.venv\Scripts\python.exe -m backend.serve
```

Import should report 9,321 snapshots and 7,202 comparisons. Keep the API terminal open. An existing PostgreSQL volume retains its original password; changing an environment variable does not rotate it. Stop the database with `docker --context desktop-linux compose -f compose.backend.yaml -p sentinel-backend stop`. Preserve its volume.

**Environment behavior in V1:** the native Python backend reads process variables; it does not automatically load `.env`. Compose can read `.env`, but that does not configure the Python process. Keep real credentials in ignored local configuration or process variables. The Vite proxy likewise reads `SENTINEL_API_PROXY_TARGET` from its process environment. Reliable unified environment loading is planned.

`SENTINEL_FRONTEND_DIR=` can remain empty when running Vite separately. It is only needed when FastAPI serves a built frontend, in which case it points to `frontend/dist` and must be supplied to the backend process.

### Frontend

In another PowerShell terminal:

```powershell
Set-Location frontend
npm.cmd ci
$env:SENTINEL_API_PROXY_TARGET = 'http://127.0.0.1:8000'
npm.cmd run dev
```

Use the Local URL printed by Vite. Select **Data connection → Live Sentinel API**, with `/api/v1` as the base URL. Reference examples are explicitly sample data.

The API listens at `http://127.0.0.1:8000`; interactive documentation is at `/docs`. Check a data endpoint as well as health:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/healthz'
Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/projects?report_month=2026-08&page=1&page_size=1'
```

The earlier documented hosted API returned HTTP 503 during setup; the local stack does not depend on it. The current API is public read-only and needs no API token. Do not put database credentials in browser-visible `VITE_` variables.

## Verification

User-supplied Windows terminal logs on **9 November 2026** confirmed:

| Check | Result |
| --- | --- |
| Frontend unit/contract tests | 11 passed, 0 skipped |
| Frontend production build | Passed |
| Full Python test discovery | 80 passed, 0 skipped, 48.173 seconds |
| PostgreSQL integration | Real PostgreSQL 17 in Docker, separate `sentinel_tests` database |
| Docker smoke test | `hello-world` passed |

These are recorded baseline results, not a claim that every future commit passes. PostgreSQL was containerized, not installed as a native Windows server. The full manual browser checklist and local browser automation results were not supplied. The user reported the dashboard running and displaying its expected August source warning. Backend test logs cover full import counts and data contracts; a separate successful application-import summary was not retained in the handover.

Frontend checks, from `frontend`:

```powershell
npm.cmd test
npm.cmd run build
```

Backend checks, from the root, with the original local database password available:

```powershell
docker --context desktop-linux compose -f compose.backend.yaml -p sentinel-backend exec -T postgres createdb -U sentinel sentinel_tests
$env:BACKEND_TEST_DATABASE_URL = "postgresql+psycopg://sentinel:$encodedPassword@127.0.0.1:5433/sentinel_tests"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Create `sentinel_tests` once. If it already exists, verify it is the dedicated local test database before reusing it. The tests additionally use disposable schemas. Never point test configuration at a live/shared database. Without the test URL, database tests can be skipped, which is not equivalent to passing them.

Observed non-failing warnings concern Starlette's httpx TestClient integration and Alembic's legacy path-separator setting. Dependency changes require separate compatibility validation.

Manual acceptance: August should show 1,731 projects unfiltered; project `611752` should show its June report gap; July–August portfolio counts should show 1,694 shared, 81 before-only and 37 after-only projects. Check filters, detail, evidence and risk signals in live mode.

## Accepted seven-phase plan

Future changes are published to **this sih103 repository only**. Deployment is Phase 7.

1. Prediction-ready data: additional reports, CUF mapping, availability and label feasibility.
2. Forecasts: conventional statistical baselines and ML candidates for defined future outcomes.
3. Predictive evaluation on later periods and held-out projects.
4. CUF input-value assessment and evidence-based analysis of additional variables.
5. Early-warning decision support integrated into the dashboard.
6. End-to-end and representative-user validation.
7. Deployment, monitoring, recovery and handover.

**Phase 1 is in progress.** A read-only readiness audit and nine boundary tests have been added. No predictive model has been trained and additional-report ingestion is not yet implemented. See the [phase tracker](docs/implementation-phases.md) and [data-feasibility audit](docs/phase1/data-feasibility.md) for current blockers and exact commands. Preserve the existing API, dataset hashes and reported values throughout.

## Further documentation

- [API contract](docs/api_contract.md)
- [Frontend integration](docs/frontend-integration.md)
- [Backend local setup](docs/backend-local.md)
- [Risk intelligence](docs/risk-intelligence.md)
- [Monthly history](docs/monthly-project-history.md)
- [Windows verification and handover](docs/windows-local-verification.md)

### Completion-evidence research

A separate Table 3 extractor recovers reported completion evidence without changing the V1 API or dataset. See [coverage and Windows commands](docs/phase1/completion-evidence.md). Reported completion evidence is not yet an approved training dataset; final-cost labels and source availability remain open.
