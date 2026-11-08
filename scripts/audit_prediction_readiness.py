"""Read-only profiling of pinned V1 history; never creates labels or trains models."""
import argparse
from collections import Counter
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path

NUMERIC = (
    'original_cost_rs_crore_normalized', 'revised_cost_rs_crore_normalized',
    'cumulative_expenditure_rs_crore_normalized', 'physical_progress_pct_normalized',
)
IDENTITY = ('project_code', 'report_month_iso', 'source_sha256')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root):
    root = Path(root).resolve()
    manifest_path = root / 'docs/examples/dataset-manifest.json'
    manifest = json.loads(manifest_path.read_bytes())
    catalog_path = root / 'config/monthly_reports.json'
    if sha256(catalog_path) != manifest['catalog_sha256']:
        raise ValueError('Catalog hash mismatch; restore reviewed bytes, do not edit manifest')
    reports = json.loads(catalog_path.read_bytes())['reports']
    by_month = {r['report_month_iso']: r for r in reports}
    if len(by_month) != len(reports):
        raise ValueError('Duplicate catalog month')
    history = root / 'data/processed/monthly_history/april_august_2026_history.csv'
    missing_dates = [r['report_month_iso'] for r in reports
                     if not r.get('first_available_date')]
    result = {
        'audit_schema': 'prediction-readiness-v1',
        'dataset_version': sha256(manifest_path),
        'scope': 'Pinned V1 ongoing-project snapshots; not a training dataset approval',
        'reports': [{'month': r['report_month_iso'],
                     'expected_snapshots': r['expected_project_count'],
                     'publication_date': r.get('publication_date'),
                     'first_available_date': r.get('first_available_date'),
                     'reporting_cutoff_is_availability': False} for r in reports],
        'months_without_first_available_date': missing_dates,
        'history': {'status': 'not_available', 'counts': None},
        'training_approved': False,
        'outcome_labels': {
            'actual_completion_delay': 'No verified actual-completion label table supplied',
            'final_cost_overrun': 'No verified final-cost label table supplied',
            'future_reported_revision': 'Candidate proxy only; not an actual outcome',
        },
        'blockers': [
            'Actual outcome labels and their evidence have not been supplied',
            'Identity/splits, changing baselines and source quality need eligibility review',
            'Forecast horizon and temporal/project evaluation splits are not approved',
        ],
    }
    if missing_dates:
        result['blockers'].append('Report first-availability evidence is missing')
    if not history.exists():
        result['blockers'].append('Full generated history is absent; row coverage was not measured')
        return result
    if sha256(history) != manifest['outputs']['history_sha256']:
        raise ValueError('History hash mismatch; run the existing validated rebuild')
    monthly = {m: {'snapshots': 0, 'fields': {
        f: {'missing': 0, 'zero': 0, 'nonzero': 0, 'negative': 0, 'over_100': 0}
        for f in NUMERIC}} for m in by_month}
    keys, codes = set(), set()
    headers = []
    with history.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        absent = set((*IDENTITY, *NUMERIC)) - set(headers)
        if absent:
            raise ValueError('Missing history columns: ' + ', '.join(sorted(absent)))
        for row in reader:
            code, month = row['project_code'], row['report_month_iso']
            if not code or month not in by_month:
                raise ValueError('Empty identity or unsupported report month')
            if row['source_sha256'] != by_month[month]['source_sha256']:
                raise ValueError('Snapshot source hash differs from catalog')
            if (code, month) in keys:
                raise ValueError('Duplicate snapshot identity')
            keys.add((code, month))
            codes.add(code)
            monthly[month]['snapshots'] += 1
            for field in NUMERIC:
                stats = monthly[month]['fields'][field]
                raw = row[field]
                if raw is None:
                    raise ValueError('Truncated history row')
                if raw == '':
                    stats['missing'] += 1
                    continue
                try:
                    value = Decimal(raw)
                except InvalidOperation as exc:
                    raise ValueError('Invalid normalized number in ' + field) from exc
                if not value.is_finite():
                    raise ValueError('Nonfinite normalized number in ' + field)
                stats['zero' if value == 0 else 'nonzero'] += 1
                stats['negative'] += int(value < 0)
                if field == 'physical_progress_pct_normalized':
                    stats['over_100'] += int(value > 100)
    for month, report in by_month.items():
        if monthly[month]['snapshots'] != report['expected_project_count']:
            raise ValueError('Snapshot count differs from catalog for ' + month)
    observed_months = Counter(code for code, month in keys)
    result['history'] = {
        'status': 'profiled_pinned_bytes',
        'validation_scope': 'Manifest/catalog/history hashes, identities and counts only; use existing importer for full bundle validation',
        'counts': {'snapshots': len(keys), 'distinct_project_codes': len(codes)},
        'observed_months_per_code': dict(sorted(Counter(observed_months.values()).items())),
        'monthly': monthly,
        'columns': headers,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = audit(args.root)
    except (ValueError, KeyError, OSError, csv.Error) as exc:
        parser.exit(2, 'Audit failed: ' + str(exc) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
