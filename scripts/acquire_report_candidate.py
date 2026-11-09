"""Download a registered candidate and stage only its pinned bytes.

Run from repository root: python -m scripts.acquire_report_candidate --metadata PATH
"""
import argparse
import json
from pathlib import Path
import tempfile
import urllib.request

from scripts.stage_report_candidate import ROOT, stage, validate_metadata

MAX_BYTES = 100 * 1024 * 1024


def acquire(metadata, root=ROOT):
    metadata = validate_metadata(metadata)
    target = Path(root) / 'data/candidates' / metadata['report_month'] / metadata['expected_sha256']
    if target.exists():
        import hashlib
        recorded = json.loads((target / 'candidate.json').read_text(encoding='utf-8'))
        if recorded['metadata'] != metadata or hashlib.sha256((target / 'source.pdf').read_bytes()).hexdigest() != metadata['expected_sha256']:
            raise ValueError('Existing candidate differs; refusing to replace it')
        return target
    request = urllib.request.Request(metadata['source_url'], headers={'User-Agent': 'Sentinel candidate acquisition/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        if not response.geturl().startswith('https://'):
            raise ValueError('Download redirected away from HTTPS')
        content = response.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise ValueError('Candidate exceeds 100 MiB limit')
    # stage() verifies SHA-256 and PDF signature before creating a candidate.
    with tempfile.TemporaryDirectory() as temporary:
        pdf = Path(temporary) / 'source.pdf'
        pdf.write_bytes(content)
        return stage(pdf, metadata, root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', type=Path, required=True)
    args = parser.parse_args()
    target = acquire(json.loads(args.metadata.read_text(encoding='utf-8-sig')))
    print(json.dumps({'candidate_directory': str(target), 'status': 'quarantined',
                      'training_approved': False}, indent=2))


if __name__ == '__main__':
    main()
