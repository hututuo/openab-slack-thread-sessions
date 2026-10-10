#!/usr/bin/env python3
"""Prepare reviewed migration candidates; NEVER overwrite a live mapping.

Bindings JSON: [{"team":"T...","channel":"C...","thread":"123.456"}].
Use verified receiving workspace + channel + exact root timestamp. No floats.
"""
import argparse
import hashlib
import json
from pathlib import Path


def migrate(mapping, metadata, bindings):
    if not isinstance(mapping, dict) or not isinstance(metadata, dict):
        raise ValueError('State must contain JSON objects')
    if any(not isinstance(k, str) or not isinstance(v, str)
           for state in (mapping, metadata) for k, v in state.items()):
        raise ValueError('State keys and values must be strings')
    mapping, metadata = dict(mapping), dict(metadata)
    claimed = set()
    for binding in bindings:
        team, channel, root = (binding[k] for k in ('team', 'channel', 'thread'))
        if any(not isinstance(v, str) or not v or ':' in v for v in (team, channel, root)):
            raise ValueError('Bindings require nonempty string IDs without colons')
        if not team.startswith('T') or channel[0] not in 'CDG':
            raise ValueError('Use verified Slack workspace and channel IDs')
        if root in claimed:
            raise ValueError('A legacy timestamp cannot be assigned to multiple destinations')
        claimed.add(root)
        old, new = f'slack:{root}', f'slack:{team}:{channel}:{root}'
        if old not in mapping and old not in metadata:
            raise ValueError(f'No legacy entry for {root}; confirm the source state')
        for state in (mapping, metadata):
            if old not in state:
                continue
            if new in state and state[new] != state[old]:
                raise ValueError(f'Destination conflict for {new}; refusing to merge conversations')
            state[new] = state.pop(old)
    return mapping, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state_directory', type=Path)
    parser.add_argument('bindings', type=Path)
    parser.add_argument('output_directory', type=Path)
    args = parser.parse_args()
    if args.output_directory.exists():
        raise ValueError('Output must be a NEW directory, separate from live state')
    originals = {}
    state = []
    for name in ('thread_map.json', 'session_meta.json'):
        path = args.state_directory / name
        raw = path.read_bytes() if path.exists() else b'{}'
        originals[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'existed': path.exists()}
        state.append(json.loads(raw))
    bindings = json.loads(args.bindings.read_text())
    result = migrate(*state, bindings)
    args.output_directory.mkdir(mode=0o700, parents=True)
    for name, value in zip(('thread_map.json', 'session_meta.json'), result):
        path = args.output_directory / name
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        path.chmod(0o600)
    (args.output_directory / 'source-hashes.json').write_text(json.dumps(originals, indent=2) + '\n')
    print('Prepared candidates only. Live state unchanged. Stop service and verify source hashes before a separately authorized installation.')

if __name__ == '__main__':
    main()
