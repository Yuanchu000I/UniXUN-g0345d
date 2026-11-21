#!/usr/bin/env python3
"""Stage the bundled iPhone iOS profile into an explicit UniXNU checkout.

Only the three runtime profile files are copied. Existing files must be byte
identical; this command never replaces them or starts a build, fetch or boot.
Python 3.11 or newer is required.

The native_kernel and kernel.linux settings also require the separately reviewed
profile-driven tools compatibility patch; staging does not apply tools patches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import stat
import sys
import tomllib


PROFILE = 'ios-16.5-20F66'
FILES = ('configs/ios.config', 'patches/xnu/series', 'profile.toml')
ROOT = Path(__file__).resolve().parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def linked(path):
    if path.is_symlink():
        return True
    # Path.is_junction() is only available in Python 3.12+. On Windows 3.11,
    # lstat() still exposes the reparse-point attribute, which covers junctions.
    is_junction = getattr(path, 'is_junction', None)
    if is_junction is not None and is_junction():
        return True
    try:
        attributes = path.lstat().st_file_attributes
    except (AttributeError, OSError):
        return False
    reparse_point = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
    return bool(attributes & reparse_point)


def checked_path(root, relative, *, directory=False, optional=False):
    """Reject linked ancestors and unexpected file types before using a path."""
    current = root
    parts = Path(relative).parts
    for index, part in enumerate(parts):
        current = current / part
        need(not linked(current), f'refusing linked path: {current}')
        if not current.exists():
            need(optional, f'missing path: {current}')
            continue
        is_directory = index < len(parts) - 1 or directory
        need(current.is_dir() if is_directory else current.is_file(),
             f'expected {"directory" if is_directory else "file"}: {current}')
    return current


def source_files(source):
    need(not linked(source) and source.is_dir(), f'invalid profile source: {source}')
    blobs = {name: checked_path(source, name).read_bytes() for name in FILES}
    profile = tomllib.loads(blobs['profile.toml'].decode('utf-8'))
    for section in ('os', 'ipsw', 'kernel'):
        need(isinstance(profile.get(section), dict), f'bundled {section} must be a table')
    os_profile = profile.get('os', {})
    for key, expected in {
        'name': PROFILE, 'arch': 'arm64', 'target': 'ios',
        'ios_version': '16.5', 'darwin': '22.5.0',
        'xnu_version': '8796.101.5',
        'xnu_revision': 'aca3beaa3dfbd42498b42c5e5ce20a938e6554e5',
    }.items():
        need(os_profile.get(key) == expected, f'wrong bundled os.{key}')
    ipsw = profile.get('ipsw', {})
    for key, expected in {
        'product': 'iPhone10,3', 'version': '16.5', 'build': '20F66',
        'device_class': 'd22ap', 'chip_id': 0x8015, 'board_id': 0x06,
    }.items():
        need(ipsw.get(key) == expected, f'wrong bundled ipsw.{key}')
    url = ipsw.get('url', '')
    need(isinstance(url, str) and url.startswith('https://updates.cdn-apple.com/')
         and url.endswith('/iPhone10,3,iPhone10,6_16.5_20F66_Restore.ipsw'),
         'wrong bundled iPhone restore URL')
    kernel = profile.get('kernel', {})
    need(kernel.get('patch_series') == [],
         'bundled patch_series must remain empty until the full stack is reviewed')
    need(not kernel.get('prelink'), 'bundled prelink inputs are not qualified')
    need(kernel.get('native_kernel') ==
         'build/xnu/ios-obj/DEVELOPMENT_ARM64_MSM8996/mach.development.msm8996.unstripped',
         'native kernel path must identify the G0345D/MSM8996 staging input')
    linux = kernel.get('linux', {})
    need(isinstance(linux, dict) and linux.get('sdk_version') == '16.5'
         and linux.get('triple') == 'arm64-apple-ios16.5',
         'wrong bundled Linux SDK or target triple')
    entries = [line.split('#', 1)[0].strip()
               for line in blobs['patches/xnu/series'].decode('utf-8').splitlines()]
    need(not any(entries), 'bundled OS series contains unreviewed active patches')
    config = blobs['configs/ios.config'].decode('utf-8')
    need('CONFIG_XNU_SOURCE_MOCKFS=y' in config.splitlines()
         and 'CONFIG_XNU_NATIVE_CS_HASH_CACHE=y' in config.splitlines(),
         'bundled iOS configuration is incomplete')
    return blobs


def stage_profile(tools, *, source=None, check=False):
    """Validate all destinations first, then create only missing runtime files."""
    source = Path(source) if source is not None else ROOT / 'profiles/os' / PROFILE
    blobs = source_files(source)
    tools = Path(tools).expanduser().absolute()
    need(not linked(tools) and tools.is_dir(), f'invalid tools checkout: {tools}')
    tools = tools.resolve()
    for marker in ('unixnu', 'scripts/unixnu/profiles.py',
                   'profiles/arch/arm64/profile.toml'):
        checked_path(tools, marker)
    checked_path(tools, 'profiles/os', directory=True)
    destination = checked_path(tools, f'profiles/os/{PROFILE}',
                               directory=True, optional=True)
    planned = []
    for name, blob in blobs.items():
        target = checked_path(tools, f'profiles/os/{PROFILE}/{name}', optional=True)
        exists = target.exists()
        need(not exists or target.read_bytes() == blob,
             f'existing profile file differs; leaving all files untouched: {target}')
        planned.append((name, target, blob, exists))
    # No destination is changed until the complete source and conflict checks pass.
    files = []
    for name, target, blob, exists in planned:
        if not exists and not check:
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation also refuses a file that appeared after preflight.
            with target.open('xb') as stream:
                stream.write(blob)
        files.append({
            'path': f'profiles/os/{PROFILE}/{name}',
            'sha256': hashlib.sha256(blob).hexdigest(),
            'action': 'unchanged' if exists else ('would-install' if check else 'installed'),
        })
    return {'profile': PROFILE, 'tools': str(tools),
            'destination': str(destination), 'mode': 'check' if check else 'stage',
            'files': files}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools', required=True, type=Path,
                        help='existing UniXNU checkout to receive the OS profile')
    parser.add_argument('--check', action='store_true',
                        help='validate and report planned files without writing them')
    args = parser.parse_args(argv)
    try:
        result = stage_profile(args.tools, check=args.check)
    except (ValueError, OSError, UnicodeError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
