import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from scripts.acquire_report_candidate import acquire


class CandidateAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.content = b'%PDF-1.7 synthetic test only'
        self.metadata = {'report_month':'2026-03', 'source_url':'https://example.gov.in/report.pdf',
                         'expected_sha256':hashlib.sha256(self.content).hexdigest()}
        self.response = MagicMock()
        self.response.__enter__.return_value = self.response
        self.response.geturl.return_value = self.metadata['source_url']
        self.response.read.return_value = self.content

    def test_download_pins_bytes_and_reuses_verified_candidate(self):
        with patch('urllib.request.urlopen', return_value=self.response) as fetch:
            target = acquire(self.metadata, self.root)
            self.assertEqual((target / 'source.pdf').read_bytes(), self.content)
            self.assertEqual(acquire(self.metadata, self.root), target)
            fetch.assert_called_once()

    def test_changed_download_leaves_no_candidate(self):
        self.response.read.return_value = b'%PDF-1.7 changed'
        with patch('urllib.request.urlopen', return_value=self.response), self.assertRaisesRegex(ValueError, 'hash mismatch'):
            acquire(self.metadata, self.root)
        self.assertFalse((self.root / 'data').exists())

    def test_changed_local_candidate_not_silently_replaced(self):
        with patch('urllib.request.urlopen', return_value=self.response):
            target = acquire(self.metadata, self.root)
        (target / 'source.pdf').write_bytes(b'changed')
        with patch('urllib.request.urlopen') as fetch, self.assertRaisesRegex(ValueError, 'Existing candidate differs'):
            acquire(self.metadata, self.root)
        fetch.assert_not_called()

    def test_http_redirect_rejected(self):
        self.response.geturl.return_value = 'http://example.gov.in/report.pdf'
        with patch('urllib.request.urlopen', return_value=self.response), self.assertRaisesRegex(ValueError, 'HTTPS'):
            acquire(self.metadata, self.root)

    def test_oversized_source_rejected(self):
        with patch('scripts.acquire_report_candidate.MAX_BYTES', 4), patch('urllib.request.urlopen', return_value=self.response), self.assertRaisesRegex(ValueError, 'limit'):
            acquire(self.metadata, self.root)

    def test_network_failure_leaves_no_candidate(self):
        with patch('urllib.request.urlopen', side_effect=TimeoutError), self.assertRaises(TimeoutError):
            acquire(self.metadata, self.root)
        self.assertFalse((self.root / 'data').exists())


if __name__ == '__main__':
    unittest.main()
