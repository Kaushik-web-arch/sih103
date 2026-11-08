"""Synthetic boundary tests; these fixtures are never model-training evidence."""
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from scripts.audit_prediction_readiness import audit, NUMERIC


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.catalog = self.root / 'config/monthly_reports.json'
        self.manifest = self.root / 'docs/examples/dataset-manifest.json'
        self.history = self.root / 'data/processed/monthly_history/april_august_2026_history.csv'
        for p in (self.catalog, self.manifest, self.history):
            p.parent.mkdir(parents=True, exist_ok=True)
        self.catalog.write_text(json.dumps({'reports': [{
            'report_month_iso': '2026-08', 'expected_project_count': 1,
            'source_sha256': 'test-source', 'publication_date': None,
            'first_available_date': None, 'documented_reporting_cutoff_date': '2026-09-24',
        }]}))
        self.row = dict(project_code='001', report_month_iso='2026-08', source_sha256='test-source')
        self.row.update(dict(zip(NUMERIC, ['100', '0', '25', ''])))
        self.write([self.row])

    def write(self, rows):
        with self.history.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(self.row))
            writer.writeheader()
            writer.writerows(rows)
        self.manifest.write_text(json.dumps({
            'catalog_sha256': hashlib.sha256(self.catalog.read_bytes()).hexdigest(),
            'outputs': {'history_sha256': hashlib.sha256(self.history.read_bytes()).hexdigest()},
        }))

    def test_zero_missing_and_identifiers_remain_distinct(self):
        result = audit(self.root)
        fields = result['history']['monthly']['2026-08']['fields']
        self.assertEqual(fields[NUMERIC[1]]['zero'], 1)
        self.assertEqual(fields[NUMERIC[1]]['missing'], 0)
        self.assertEqual(fields[NUMERIC[3]]['missing'], 1)
        self.assertEqual(result['history']['counts']['distinct_project_codes'], 1)
        self.assertFalse(result['training_approved'])

    def test_cutoff_never_substitutes_for_availability(self):
        result = audit(self.root)
        self.assertEqual(result['months_without_first_available_date'], ['2026-08'])
        self.assertIsNone(result['reports'][0]['first_available_date'])

    def test_missing_history_is_not_zero_rows(self):
        self.history.unlink()
        self.assertIsNone(audit(self.root)['history']['counts'])

    def test_changed_history_rejected(self):
        with self.history.open('a') as f:
            f.write('\n')
        with self.assertRaisesRegex(ValueError, 'History hash mismatch'):
            audit(self.root)

    def test_changed_catalog_rejected(self):
        with self.catalog.open('a') as f:
            f.write('\n')
        with self.assertRaisesRegex(ValueError, 'Catalog hash mismatch'):
            audit(self.root)

    def test_duplicate_snapshot_rejected(self):
        self.write([self.row, self.row])
        with self.assertRaisesRegex(ValueError, 'Duplicate snapshot'):
            audit(self.root)

    def test_wrong_source_rejected(self):
        self.write([dict(self.row, source_sha256='changed')])
        with self.assertRaisesRegex(ValueError, 'source hash'):
            audit(self.root)

    def test_nonfinite_numeric_rejected(self):
        self.write([dict(self.row, **{NUMERIC[0]: 'NaN'})])
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            audit(self.root)

    def test_count_mismatch_rejected(self):
        self.write([])
        with self.assertRaisesRegex(ValueError, 'Snapshot count'):
            audit(self.root)
