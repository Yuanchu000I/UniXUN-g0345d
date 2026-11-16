#!/usr/bin/env python3
"""Offline metadata/source-export checks; no compilation or device operations.

The unchanged official record checker is paired explicitly with the pinned
fork component catalog. Use --base REV for committed change ownership checks.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {'.git', '.cache', '__pycache__', '.venv', 'venv', 'out', 'build', 'Build', 'dist', 'artifacts'}
BINARY_SUFFIXES = {'.img', '.bin', '.fd', '.efi', '.dtb', '.dtbo', '.macho', '.ipsw', '.dmg', '.aea', '.zip', '.7z', '.gz', '.a', '.o', '.obj', '.dll', '.exe', '.jpg', '.jpeg', '.png', '.mp4'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def load(name):
    return tomllib.loads((ROOT / name).read_text(encoding='utf-8'))


def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not set(p.relative_to(ROOT).parts) & IGNORED_DIRS and p.name != 'local.toml')


def verify():
    board, record, pins = load('board.toml'), load('porting.toml'), load('source-pins.toml')
    required = ['AGENTS.md', 'README.md', 'README.zh.md', '.gitignore', '.gitattributes',
                'board.toml', 'porting.toml', 'feeds.toml', 'unixnu.lock', 'LICENSE', 'NOTICE',
                'configs/g0345d_defconfig', 'dts/g0345d.dts', 'patches/xnu/series',
                'scripts/package.sh', 'proprietary-files.txt', 'package/README.md',
                'local.toml.example', '.github/workflows/porting-record.yml',
                '.github/workflows/package.yml', 'docs/status.md', 'docs/publication.md',
                'docs/firmware-dependency.md', 'docs/provenance/source-snapshot.json']
    for name in required:
        need((ROOT / name).is_file(), f'missing required publication file: {name}')
    need(board.get('schema_version') == 2 and not board['board'].get('example'), 'board must be real format 2')
    for key, value in [('name', 'g0345d'), ('soc', 'msm8996'), ('os_profile', 'ipados-17.7.11-21H461')]:
        need(board['board'][key] == record['device'][key] == value, f'wrong identity: {key}')
    need(board['package']['unixnu'] == '../UniXNU', 'package tools path must stay portable')
    need(board['package']['defconfig'][board['board']['os_profile']] == board['kernel']['defconfig'] == 'g0345d_defconfig', 'defconfig mismatch')
    need(board['device_tree']['source'] == 'device:dts/g0345d.dts', 'wrong board DTS')
    need('device:patches/xnu/series' in board['kernel']['patch_series'], 'missing device patch series')
    snapshot = json.loads((ROOT / 'docs/provenance/source-snapshot.json').read_text(encoding='utf-8'))
    for name, digest in snapshot['files'].items():
        need(sha((ROOT / name).read_bytes()) == digest, f'exported functional input changed: {name}')
    runtime = {key: value for key, value in board.items() if key != 'package'}
    digest = sha(json.dumps(runtime, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())
    need(digest == snapshot['board_runtime_semantic_sha256'], 'runtime board settings differ from M42 source')
    series = [line.split('#', 1)[0].strip() for line in (ROOT / 'patches/xnu/series').read_text().splitlines()]
    series = [name for name in series if name]
    expected = [name.removeprefix('patches/xnu/') for name in snapshot['files'] if name.startswith('patches/xnu/')]
    need(series == expected and len(series) == len(set(series)) == snapshot['ordered_device_patch_count'] == 51, 'active patch order/count changed')
    need({p.name for p in (ROOT / 'patches/xnu').glob('*.patch')} == set(series), 'inactive or missing XNU patch')
    for name, digest in pins['validation']['sha256'].items():
        need(sha((ROOT / name).read_bytes()) == digest, f'pinned checker/catalog/template changed: {name}')
    need(pins['official']['commit'] == '21d683dff61c66f219f03ab9d8b9249026514788', 'unexpected official schema pin')
    need(pins['tools']['commit'] == snapshot['tool_commit'], 'tested tools pin differs')
    feed = load('feeds.toml')['source']
    soc = next(item for item in feed if item['name'] == 'msm8996')
    need(soc['commit'] == pins['soc']['commit'] == load('unixnu.lock')['source']['msm8996']['commit'], 'SoC pin mismatch')
    for name, item in load('unixnu.lock')['source'].items():
        need(re.fullmatch(r'[0-9a-f]{40}', item['commit']), f'invalid source commit: {name}')
    fork_catalog = {item['id']: item for item in load('ci/fork/components.toml')['component']}
    upstream_ids = {item['id'] for item in load('ci/upstream/components.toml')['component']}
    selected = set(board['components']['include'])
    pending = list(selected)
    while pending:
        current = pending.pop()
        need(current in fork_catalog, f'unknown fork component: {current}')
        for dep in fork_catalog[current].get('dependencies', []):
            if dep not in selected:
                selected.add(dep)
                pending.append(dep)
    need(selected <= {c for area in record['area'] for c in area['components']}, 'selected dependency lacks area')
    need('cellular' in {area['id'] for area in record['area']}, 'missing cellular area from official prose guide')
    print(f'PASS: 55 exact functional inputs; 51 ordered patches; unchanged runtime board settings')
    print(f'PASS: {len(record["area"])} areas cover {len(selected)} components including dependencies')
    print('COMPATIBILITY: official strict catalog lacks ' + ', '.join(sorted(selected - upstream_ids)))
    print('MODE: unchanged official record checker + explicitly pinned fork catalog')
    all_files = files()
    sensitive = [re.compile(r'[A-Za-z]:[\\/]Users[\\/][^\s]+', re.I),
                 re.compile(r'/(?:home|mnt/[a-z])/[^\s]+'),
                 re.compile(r'\b(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b'),
                 re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
                 re.compile(r'(?im)^\s*unique_chip_id\s*=\s*["\'](?!required)[0-9a-f]{8,}["\']')]
    markdown_links = 0
    for path in all_files:
        name = path.relative_to(ROOT).as_posix()
        need(path.suffix.lower() not in BINARY_SUFFIXES, f'binary/private artifact in publication: {name}')
        need(not path.is_symlink(), f'review symlink before publishing: {name}')
        need(path.stat().st_size < 2 * 1024 * 1024, f'unexpected large file: {name}')
        blob = path.read_bytes()
        need(b'\0' not in blob, f'binary/NUL file: {name}')
        text = blob.decode('utf-8-sig')
        need(not any(pattern.search(text) for pattern in sensitive), f'private path/credential pattern: {name}')
        if name.endswith('.toml') or name in ('unixnu.lock', 'local.toml.example'):
            tomllib.loads(text)
        if name.endswith('.json'):
            json.loads(text)
        if name.endswith('.py'):
            compile(text, name, 'exec')
        if name.endswith('.sh'):
            need(b'\r' not in blob, f'shell script must use LF: {name}')
        if name not in ('porting.toml',) and not name.lower().endswith(('.md', '.rst')):
            need(any(fnmatch.fnmatchcase(name, pattern) for area in record['area'] for pattern in area['paths']), f'file needs owning area: {name}')
        if name.endswith('.md'):
            for target in re.findall(r'\]\(([^\s)]+)\)', text):
                if target.startswith(('https://', 'http://', '#', 'mailto:')):
                    continue
                target = target.split('#', 1)[0]
                if not target:
                    continue
                resolved = (path.parent / target).resolve()
                need(resolved.is_relative_to(ROOT) and resolved.exists(), f'broken local Markdown link in {name}: {target}')
                markdown_links += 1
    print(f'PASS: {len(all_files)} UTF-8 files; TOML/JSON/Python syntax; size/type/privacy/ownership scan; {markdown_links} local Markdown links')
    return all_files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='existing committed base for the official changed-area check')
    args = parser.parse_args()
    try:
        verify()
        with tempfile.TemporaryDirectory(prefix='g0345d-record-') as temp:
            root = Path(temp)
            (root / 'scripts').mkdir()
            shutil.copyfile(ROOT / 'ci/upstream/scripts/porting-record.py', root / 'scripts/porting-record.py')
            shutil.copyfile(ROOT / 'ci/fork/components.toml', root / 'components.toml')
            command = [sys.executable, '-X', 'utf8', str(root / 'scripts/porting-record.py'), 'check', '--device', str(ROOT)]
            if args.base:
                command += ['--base', args.base]
            subprocess.run(command, check=True)
        print('PASS: official record-schema check with pinned fork catalog')
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
