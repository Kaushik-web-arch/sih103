"""Quarantine an additional PDF without changing the pinned V1 dataset.

A successful run verifies bytes and metadata only, not PDF layout, outcomes,
identity, availability evidence, or training eligibility.
"""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def https_url(value, field):
    parsed = urlsplit(value) if isinstance(value, str) else None
    if not parsed or parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f'{field} must be an HTTPS URL without credentials')


def validate_metadata(metadata):
    if not isinstance(metadata, dict):
        raise ValueError('Metadata must be a JSON object')
    allowed = {'report_month', 'source_url', 'expected_sha256', 'publication_date',
               'first_available_date', 'availability_evidence_url'}
    if set(metadata) - allowed:
        raise ValueError('Unknown metadata fields')
    if not re.fullmatch(r'20\d{2}-(0[1-9]|1[0-2])', str(metadata.get('report_month', ''))):
        raise ValueError('report_month must be YYYY-MM')
    if not re.fullmatch(r'[0-9a-f]{64}', str(metadata.get('expected_sha256', ''))):
        raise ValueError('expected_sha256 must be a lowercase SHA-256 digest')
    https_url(metadata.get('source_url'), 'source_url')
    result = {key: metadata.get(key) for key in sorted(allowed)}
    for key in ('publication_date', 'first_available_date'):
        value = result[key]
        if value is not None:
            if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError(f'{key} must be YYYY-MM-DD or null')
            date.fromisoformat(value)
    evidence = result['availability_evidence_url']
    if evidence is not None:
        https_url(evidence, 'availability_evidence_url')
    if result['first_available_date'] is not None and evidence is None:
        raise ValueError('first_available_date requires availability_evidence_url')
    # Dates remain assertions needing review, even when an evidence URL is provided.
    return result


def stage(pdf, metadata, root=ROOT):
    metadata = validate_metadata(metadata)
    content = Path(pdf).read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if digest != metadata['expected_sha256']:
        raise ValueError('Source hash mismatch; candidate was not staged')
    if not content.startswith(b'%PDF-'):
        raise ValueError('Source has no PDF header; candidate was not staged')
    parent = Path(root) / 'data' / 'candidates' / metadata['report_month']
    target = parent / digest
    parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f'Candidate already exists; preserve it for review: {target}')
    manifest = dict(schema='sentinel-report-candidate-v1', metadata=metadata,
                    source_sha256=digest, source_bytes=len(content),
                    status='quarantined', training_approved=False,
                    validation_scope='SHA-256, PDF signature and metadata syntax only',
                    gates={'layout_and_extraction': 'pending', 'visual_reference_review': 'pending',
                           'identity_and_scope': 'pending', 'availability_evidence': 'pending',
                           'outcome_labels': 'pending', 'dataset_promotion': 'pending'})
    temporary = Path(tempfile.mkdtemp(prefix='.staging-', dir=parent))
    try:
        (temporary / 'source.pdf').write_bytes(content)
        (temporary / 'candidate.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        # Nonempty existing destinations are never replaced. Staged directories
        # always contain these two files; Windows also rejects any existing target.
        temporary.rename(target)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    args = parser.parse_args()
    metadata = json.loads(args.metadata.read_text(encoding='utf-8-sig'))
    target = stage(args.pdf, metadata)
    print(json.dumps({'candidate_directory': str(target), 'status': 'quarantined',
                      'training_approved': False}, indent=2))


if __name__ == '__main__':
    main()
