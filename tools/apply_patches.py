#!/usr/bin/env python3
"""Verify and apply this patch series to a disposable pinned-upstream checkout.

By default only verify: stage the affected source files in a temporary directory,
apply both patches there, and verify every resulting hash. Pass --apply to copy
those validated files into the checkout. Never target a running installation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    manifest = json.loads((ROOT / 'source-manifest.json').read_text())
    for entry in manifest['files']:
        path = checkout / entry['path']
        expected = entry['upstream_sha256']
        if path.is_symlink():
            raise ValueError('Refusing a symlink: ' + entry['path'])
        if expected is None:
            if path.exists():
                raise ValueError('New-file destination already exists: ' + entry['path'])
        elif not path.is_file() or digest(path) != expected:
            raise ValueError('Upstream source mismatch: ' + entry['path'])
    with tempfile.TemporaryDirectory(prefix='openab-patch-verify-') as directory:
        staged = Path(directory)
        for entry in manifest['files']:
            if entry['upstream_sha256'] is not None:
                path = staged / entry['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(checkout / entry['path'], path)
        for name in ('0001-slack-prerequisites.patch', '0002-thread-session-queue.patch'):
            subprocess.run(['git', 'apply', '--check', str(ROOT / 'patches' / name)], cwd=staged, check=True)
            subprocess.run(['git', 'apply', str(ROOT / 'patches' / name)], cwd=staged, check=True)
        for entry in manifest['files']:
            if digest(staged / entry['path']) != entry['patched_sha256']:
                raise ValueError('Patched source mismatch: ' + entry['path'])
        if args.apply:
            # Recheck before writes. Target must be a disposable, idle checkout.
            for entry in manifest['files']:
                path = checkout / entry['path']
                expected = entry['upstream_sha256']
                if (expected is None and path.exists()) or (expected is not None and digest(path) != expected):
                    raise ValueError('Checkout changed during verification: ' + entry['path'])
            for entry in manifest['files']:
                path = checkout / entry['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(staged / entry['path'], path)
    print('11 source files verified' + (' and applied.' if args.apply else '; checkout unchanged.'))


if __name__ == '__main__':
    main()
