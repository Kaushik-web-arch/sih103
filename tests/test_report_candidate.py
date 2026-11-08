import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.stage_report_candidate import stage, validate_metadata


class ReportCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'input.pdf'
        self.pdf.write_bytes(b'%PDF-1.7\nsynthetic signature-only fixture\n')
        self.metadata = {'report_month': '2026-09',
                         'source_url': 'https://example.gov.in/report.pdf',
                         'expected_sha256': hashlib.sha256(self.pdf.read_bytes()).hexdigest()}

    def test_quarantine_is_not_training_approval(self):
        target = stage(self.pdf, self.metadata, self.root)
        result = json.loads((target / 'candidate.json').read_text())
        self.assertFalse(result['training_approved'])
        self.assertEqual(result['status'], 'quarantined')
        self.assertEqual(set(result['gates'].values()), {'pending'})
        self.assertEqual((target / 'source.pdf').read_bytes(), self.pdf.read_bytes())
        self.assertIsNone(result['metadata']['first_available_date'])

    def test_changed_source_rejected_without_staging(self):
        self.pdf.write_bytes(b'%PDF-1.7 changed')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            stage(self.pdf, self.metadata, self.root)
        self.assertFalse((self.root / 'data').exists())

    def test_html_response_rejected(self):
        self.pdf.write_bytes(b'<html>Access denied</html>')
        self.metadata['expected_sha256'] = hashlib.sha256(self.pdf.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'PDF header'):
            stage(self.pdf, self.metadata, self.root)

    def test_existing_candidate_never_overwritten(self):
        target = stage(self.pdf, self.metadata, self.root)
        original = (target / 'candidate.json').read_bytes()
        self.metadata['publication_date'] = '2026-10-01'
        with self.assertRaises(FileExistsError):
            stage(self.pdf, self.metadata, self.root)
        self.assertEqual((target / 'candidate.json').read_bytes(), original)

    def test_invalid_month_and_path_traversal_rejected(self):
        for month in ('2026-13', '../raw', '2026-9', '2026-09/../../raw'):
            with self.subTest(month=month), self.assertRaises(ValueError):
                validate_metadata(dict(self.metadata, report_month=month))

    def test_unpinned_digest_rejected(self):
        with self.assertRaises(ValueError):
            validate_metadata(dict(self.metadata, expected_sha256=''))

    def test_unsafe_url_rejected(self):
        for url in ('http://example.gov.in/a', 'file:///tmp/a', 'https://user:secret@example.com/a'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_metadata(dict(self.metadata, source_url=url))

    def test_availability_needs_evidence(self):
        with self.assertRaisesRegex(ValueError, 'requires availability'):
            validate_metadata(dict(self.metadata, first_available_date='2026-10-01'))
        result = validate_metadata(dict(self.metadata, publication_date='2026-10-01'))
        self.assertIsNone(result['first_available_date'])

    def test_invalid_date_rejected(self):
        for value in ('2026-02-30', '20261001', '', 2026):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_metadata(dict(self.metadata, publication_date=value))

    def test_evidence_does_not_grant_approval(self):
        target = stage(self.pdf, dict(self.metadata, first_available_date='2026-10-01',
                       availability_evidence_url='https://example.gov.in/archive'), self.root)
        result = json.loads((target / 'candidate.json').read_text())
        self.assertEqual(result['gates']['availability_evidence'], 'pending')
        self.assertFalse(result['training_approved'])

    def test_pinned_files_untouched(self):
        protected = self.root / 'config' / 'monthly_reports.json'
        protected.parent.mkdir()
        protected.write_bytes(b'pinned catalog sentinel')
        stage(self.pdf, self.metadata, self.root)
        self.assertEqual(protected.read_bytes(), b'pinned catalog sentinel')

    def test_unknown_fields_cannot_override_gates(self):
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            validate_metadata(dict(self.metadata, training_approved=True))


if __name__ == '__main__':
    unittest.main()
