"""Extract reported completion evidence, separately from the immutable V1 bundle.

This is a reviewed-layout research adapter, not a training-label approval. It
preserves June's absent actual-date column and never equates expenditure to cost.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re

import pdfplumber
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
MISSING = {'', '-', 'NA', 'N/A'}
# Reviewed V1 layout coverage; other reports require an explicit adapter review.
EXPECTED = {
    '2026-04': ([35], 9, True), '2026-05': ([35], 16, True),
    '2026-06': (list(range(36, 43)), 130, False),
    '2026-07': ([36, 37], 25, True), '2026-08': ([37, 38, 39], 47, True),
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compact(value):
    return re.sub(r'\s+', '', value or '')


def month(raw):
    value = raw.strip()
    if value.startswith('(') and value.endswith(')'):
        value = value[1:-1].strip()
    if value in MISSING:
        return None
    match = re.fullmatch(r'(0[1-9]|1[0-2])/(20\d{2}|19\d{2})', value)
    if not match:
        raise ValueError(f'Unrecognized month: {raw!r}')
    return f'{match[2]}-{match[1]}'


def parse_dates(cell, has_actual):
    parts = [line.strip() for line in cell.splitlines() if line.strip()]
    expected = 3 if has_actual else 2
    if len(parts) != expected:
        raise ValueError('Unexpected completion cell layout')
    values = [month(part) for part in parts]
    if has_actual:
        return dict(actual_completion_month=values[0], original_target_month=values[1],
                    revised_target_month=values[2], actual_date_status='reported' if values[0] else 'source_missing')
    return dict(actual_completion_month=None, original_target_month=values[0],
                revised_target_month=values[1], actual_date_status='column_absent')


def parse_record(cells, has_actual):
    if len(cells) != 7 or any(cell is None for cell in cells):
        raise ValueError('Expected seven non-null physical cells')
    identity = cells[1].splitlines()
    code = identity[-1].strip()
    if not re.fullmatch(r'\d+', code):
        raise ValueError('Project code must be the final identity line')
    return dict(serial_no=int(cells[0]), project_code=code,
                identity_raw=cells[1], state_raw=cells[2],
                approval_start_raw=cells[3], completion_cell_raw=cells[4],
                cost_cell_raw=cells[5], cumulative_expenditure_raw=cells[6],
                final_outturn_cost=None, final_cost_status='not_established',
                source_cells=cells, **parse_dates(cells[4], has_actual))


def extract_report(pdf, report):
    expected_pages, expected_count, expected_actual = EXPECTED[report['report_month_iso']]
    source_hash = digest(pdf)
    if source_hash != report['source_sha256']:
        raise ValueError('Source PDF hash mismatch')
    records, pages, totals = [], [], []
    with pymupdf.open(pdf) as document, pdfplumber.open(pdf) as second:
        for index, page in enumerate(document):
            text = page.get_text()
            if 'Completed Projects During Month' not in text:
                continue
            # The title also appears in contents; require the actual column header.
            if 'Project Name (Agency) (Project Code)' not in text:
                continue
            primary = [row for table in page.find_tables().tables for row in table.extract()]
            secondary = [row for table in second.pages[index].extract_tables() for row in table]
            left = [r for r in primary if r and str(r[0]).isdigit()]
            right = [r for r in secondary if r and str(r[0]).isdigit()]
            if not left or len(left) != len(right):
                raise ValueError(f'Reader count disagreement on page {index + 1}')
            headers = [r for r in primary if r and compact(r[0]) == 'Sl.No']
            if len(headers) != 1 or len(headers[0]) != 7:
                raise ValueError('Unrecognized completed-table header')
            has_actual = 'ActualDateofCompletion' in compact(headers[0][4])
            if not all(term in compact(headers[0][4]) for term in ('TargetDoC', 'RevisedDoC')):
                raise ValueError('Unrecognized date semantics')
            if has_actual != expected_actual:
                raise ValueError('Actual-date header differs from reviewed layout')
            pages.append(index + 1)
            for row, other in zip(left, right):
                if list(map(compact, row)) != list(map(compact, other)):
                    raise ValueError(f'Independent reader disagreement on page {index + 1}, serial {row[0]}')
                record = parse_record(row, has_actual)
                record.update(report_month=report['report_month_iso'], source_sha256=source_hash,
                              source_filename=Path(pdf).name, pdf_page=index + 1,
                              date_precision='month', first_available_date=report.get('first_available_date'),
                              training_approved=False)
                records.append(record)
            for row in primary:
                if len(row) > 1 and re.fullmatch(r'Total\s*\(\d+\)', row[1] or ''):
                    totals.append(int(re.search(r'\d+', row[1])[0]))
    if pages != expected_pages or len(records) != expected_count:
        raise ValueError('Completed-table coverage differs from reviewed layout')
    if pages != list(range(pages[0], pages[-1] + 1)):
        raise ValueError('Noncontiguous table pages')
    if [r['serial_no'] for r in records] != list(range(1, len(records) + 1)):
        raise ValueError('Incomplete or duplicate serial coverage')
    if len({r['project_code'] for r in records}) != len(records):
        raise ValueError('Duplicate code in completed table')
    if not totals or sum(totals) != len(records):
        raise ValueError('Completed-table section counts do not reconcile')
    return records, dict(pdf_pages=pages, records=len(records), section_count_sum=sum(totals),
                         actual_date_status=dict(Counter(r['actual_date_status'] for r in records)),
                         independent_readers_agree=True)


def coverage(records, history):
    by_code = {}
    for row in history:
        by_code.setdefault(row['project_code'], []).append(row)
    result = Counter()
    for row in records:
        snapshots = by_code.get(row['project_code'], [])
        actual = row['actual_completion_month']
        result['records'] += 1
        result['with_any_ongoing_code_match'] += bool(snapshots)
        result['with_reported_actual_month'] += actual is not None
        if actual:
            result['with_earlier_report_month_match'] += any(s['report_month_iso'] < actual for s in snapshots)
            result['with_ongoing_report_at_or_after_completion_month'] += any(s['report_month_iso'] >= actual for s in snapshots)
            result['actual_month_later_than_report_month'] += actual > row['report_month']
    return dict(result)


def build(root=ROOT):
    root = Path(root)
    manifest = json.loads((root / 'docs/examples/dataset-manifest.json').read_bytes())
    catalog = root / 'config/monthly_reports.json'
    if digest(catalog) != manifest['catalog_sha256']:
        raise ValueError('Pinned catalog hash mismatch')
    records, reports = [], {}
    for report in json.loads(catalog.read_bytes())['reports']:
        extracted, summary = extract_report(root / report['pdf'], report)
        records.extend(extracted)
        reports[report['report_month_iso']] = summary
    fixture_path = root / 'tests/fixtures/completion_evidence_visual_samples.json'
    fixtures = json.loads(fixture_path.read_bytes())
    keyed = {(r['report_month'], r['project_code']): r for r in records}
    for expected in fixtures:
        actual = keyed[(expected['report_month'], expected['project_code'])]
        if any(actual.get(key) != value for key, value in expected.items()):
            raise ValueError(f'Visual reference mismatch: {expected["project_code"]}')
    history_path = root / 'data/processed/monthly_history/april_august_2026_history.csv'
    if digest(history_path) != manifest['outputs']['history_sha256']:
        raise ValueError('Pinned history hash mismatch')
    with history_path.open(encoding='utf-8', newline='') as stream:
        history = list(csv.DictReader(stream))
    for record in records:
        matches = [s for s in history if s['project_code'] == record['project_code']]
        record['code_match_report_months'] = [s['report_month_iso'] for s in matches]
        record['identity_review_status'] = 'pending'
        actual = record['actual_completion_month']
        record['review_flags'] = []
        if actual and actual > record['report_month']:
            record['review_flags'].append('completion_later_than_report_label')
        if actual and any(s['report_month_iso'] >= actual for s in matches):
            record['review_flags'].append('ongoing_snapshot_at_or_after_reported_completion')
    return dict(schema='completion-evidence-v1', status='extracted_for_review',
                training_approved=False, dataset_version=digest(root / 'docs/examples/dataset-manifest.json'),
                extractor_sha256=digest(Path(__file__)), fixture_sha256=digest(fixture_path),
                fixture_count=len(fixtures), reports=reports, coverage=coverage(records, history),
                limitations=['Code matches are not reviewed identity links',
                             'Earlier report month is not proof of pre-event availability',
                             'Completed-table costs are not verified final outturn costs',
                             'No target, forecast horizon or evaluation split approved',
                             'Agreement of readers is not independent verification of reported outcomes'],
                records=records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/validation/completion-evidence.json')
    args = parser.parse_args()
    # Invalidate stale success evidence before work; partial runs cannot look passed.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'status': 'running', 'training_approved': False}) + '\n')
    try:
        result = build()
    except Exception:
        args.output.write_text(json.dumps({'status': 'failed', 'training_approved': False}) + '\n')
        raise
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}, indent=2))


if __name__ == '__main__':
    main()
