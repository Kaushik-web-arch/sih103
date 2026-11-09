import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.extract_completion_evidence import ROOT, build, coverage, extract_report, month, parse_dates, parse_record


class CompletionEvidenceTests(unittest.TestCase):
    def test_absent_actual_column_never_uses_revised_date(self):
        value = parse_dates('(12/2021)\n(04/2026)', False)
        self.assertIsNone(value['actual_completion_month'])
        self.assertEqual(value['actual_date_status'], 'column_absent')
        self.assertEqual(value['revised_target_month'], '2026-04')

    def test_na_actual_is_not_completed_report_month(self):
        value = parse_dates('NA\n(02/2025)\n(08/2025)', True)
        self.assertIsNone(value['actual_completion_month'])
        self.assertEqual(value['actual_date_status'], 'source_missing')

    def test_month_precision_preserved(self):
        self.assertEqual(month('06/2026'), '2026-06')
        self.assertEqual(month('(06/2026)'), '2026-06')
        self.assertIsNone(month('(-)'))

    def test_invalid_month_rejected(self):
        for raw in ('13/2026', '06/26', '2026-06-01', '0', 'unknown'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                month(raw)

    def test_ambiguous_date_cell_rejected(self):
        for cell in ('06/2026', '06/2026\n(07/2026)', '06/2026\n(07/2026)\n(08/2026)\n(09/2026)'):
            with self.subTest(cell=cell), self.assertRaises(ValueError):
                parse_dates(cell, True)

    def test_raw_zero_and_expenditure_never_become_final_cost(self):
        row = ['1', 'Name\n(Agency)\n0012', 'State', '01/2020\n(02/2020)',
               '06/2026\n(07/2025)\n(06/2026)', '200.00\n(0.00)', '123.40']
        value = parse_record(row, True)
        self.assertEqual(value['project_code'], '0012')
        self.assertEqual(value['cost_cell_raw'], '200.00\n(0.00)')
        self.assertEqual(value['cumulative_expenditure_raw'], '123.40')
        self.assertIsNone(value['final_outturn_cost'])

    def test_incomplete_physical_row_rejected(self):
        with self.assertRaises(ValueError):
            parse_record(['1', 'Name'], True)

    def test_code_requires_final_identity_line(self):
        with self.assertRaises(ValueError):
            parse_record(['1', 'Name\n(Agency)', 'State', '', '', '', ''], True)

    def test_absence_is_not_an_outcome(self):
        result = coverage([], [{'project_code': '1', 'report_month_iso': '2026-04'}])
        self.assertEqual(result.get('records', 0), 0)

    def test_at_or_after_event_is_flagged_not_pre_event(self):
        records = [{'project_code':'1', 'report_month':'2026-08', 'actual_completion_month':'2026-05'}]
        history = [{'project_code':'1', 'report_month_iso':'2026-05'},
                   {'project_code':'1', 'report_month_iso':'2026-06'}]
        result = coverage(records, history)
        self.assertEqual(result['with_earlier_report_month_match'], 0)
        self.assertEqual(result['with_ongoing_report_at_or_after_completion_month'], 1)

    def test_changed_pdf_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.pdf'
            path.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                extract_report(path, {'report_month_iso':'2026-08', 'source_sha256':'0'*64})

    def test_changed_catalog_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'config').mkdir()
            (root / 'docs/examples').mkdir(parents=True)
            (root / 'config/monthly_reports.json').write_text('{}')
            (root / 'docs/examples/dataset-manifest.json').write_text('{"catalog_sha256":"wrong"}')
            with self.assertRaisesRegex(ValueError, 'catalog hash'):
                build(root)


@unittest.skipUnless((ROOT / 'data/raw/FlashReport_August_2026.pdf').exists()
                     and (ROOT / 'data/processed/monthly_history/april_august_2026_history.csv').exists(),
                     'Requires acquired reports and rebuilt pinned history')
class CompletionSourceTests(unittest.TestCase):
    def test_full_pinned_source_evidence_and_visual_references(self):
        result = build()
        self.assertEqual(result['coverage']['records'], 227)
        self.assertEqual(result['coverage']['with_reported_actual_month'], 92)
        self.assertEqual(result['coverage']['with_earlier_report_month_match'], 31)
        self.assertEqual(result['reports']['2026-06']['actual_date_status'], {'column_absent':130})
        self.assertEqual(result['fixture_count'], 7)
        self.assertFalse(result['training_approved'])
        self.assertTrue(all(r['final_outturn_cost'] is None for r in result['records']))


if __name__ == '__main__':
    unittest.main()
