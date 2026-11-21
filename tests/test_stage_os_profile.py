"""Offline staging safety checks; no external checkout or build is required."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('stage_os_profile',
                                            ROOT / 'scripts/stage-os-profile.py')
STAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STAGE)


class StagingSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='g0345d-profile-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tools = self.root / 'tools'
        for name in ('unixnu', 'scripts/unixnu/profiles.py',
                     'profiles/arch/arm64/profile.toml'):
            marker = self.tools / name
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text('# local test fixture\n', encoding='utf-8')
        (self.tools / 'profiles/os').mkdir()
        self.source = self.root / STAGE.PROFILE
        shutil.copytree(ROOT / 'profiles/os' / STAGE.PROFILE, self.source)
        self.destination = self.tools / 'profiles/os' / STAGE.PROFILE

    def stage(self, **kwargs):
        return STAGE.stage_profile(self.tools, source=self.source, **kwargs)

    def test_check_writes_nothing_then_stage_is_idempotent(self):
        result = self.stage(check=True)
        self.assertFalse(self.destination.exists())
        self.assertEqual([f['action'] for f in result['files']], ['would-install'] * 3)
        result = self.stage()
        self.assertEqual([f['action'] for f in result['files']], ['installed'] * 3)
        self.assertEqual([f['path'] for f in result['files']],
                         [f'profiles/os/{STAGE.PROFILE}/{name}' for name in STAGE.FILES])
        before = {name: (self.destination / name).stat().st_mtime_ns for name in STAGE.FILES}
        result = self.stage()
        self.assertEqual([f['action'] for f in result['files']], ['unchanged'] * 3)
        self.assertEqual(before, {name: (self.destination / name).stat().st_mtime_ns
                                  for name in STAGE.FILES})
        for name in STAGE.FILES:
            self.assertEqual((self.source / name).read_bytes(),
                             (self.destination / name).read_bytes())

    def test_conflicting_last_file_prevents_earlier_writes(self):
        self.destination.mkdir()
        existing = self.destination / 'profile.toml'
        existing.write_bytes(b'# local work must survive\n')
        with self.assertRaisesRegex(ValueError, 'differs'):
            self.stage()
        self.assertEqual(existing.read_bytes(), b'# local work must survive\n')
        self.assertEqual(list(self.destination.iterdir()), [existing])

    def test_unrelated_existing_files_are_preserved(self):
        self.destination.mkdir()
        extra = self.destination / 'provenance.md'
        extra.write_bytes(b'Existing documentation.\n')
        self.stage()
        self.assertEqual(extra.read_bytes(), b'Existing documentation.\n')

    def test_invalid_tools_are_rejected_without_output(self):
        (self.tools / 'scripts/unixnu/profiles.py').unlink()
        with self.assertRaisesRegex(ValueError, 'missing path'):
            self.stage()
        self.assertFalse(self.destination.exists())

    def test_wrong_donor_is_rejected_before_writing(self):
        profile = self.source / 'profile.toml'
        profile.write_text(profile.read_text(encoding='utf-8').replace(
            'product = "iPhone10,3"', 'product = "iPad7,5"'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'ipsw.product'):
            self.stage()
        self.assertFalse(self.destination.exists())

    def test_active_patch_is_rejected_before_writing(self):
        (self.source / 'patches/xnu/series').write_text('unreviewed.patch\n',
                                                       encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'unreviewed active patches'):
            self.stage()
        self.assertFalse(self.destination.exists())

    def test_active_kernel_series_is_rejected_before_writing(self):
        profile = self.source / 'profile.toml'
        profile.write_text(profile.read_text(encoding='utf-8').replace(
            'patch_series = []', 'patch_series = ["arch:patches/xnu/series"]'),
            encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'patch_series must remain empty'):
            self.stage()
        self.assertFalse(self.destination.exists())

    def test_malformed_profile_is_rejected_before_writing(self):
        (self.source / 'profile.toml').write_text('[os\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse(self.destination.exists())

    def test_old_linux_sdk_is_rejected_before_writing(self):
        profile = self.source / 'profile.toml'
        profile.write_text(profile.read_text(encoding='utf-8').replace(
            'sdk_version = "16.5"', 'sdk_version = "17.5"'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Linux SDK or target triple'):
            self.stage()
        self.assertFalse(self.destination.exists())

    def test_nonexistent_noctf_target_is_rejected_before_writing(self):
        profile = self.source / 'profile.toml'
        profile.write_text(profile.read_text(encoding='utf-8').replace(
            'msm8996.unstripped"', 'msm8996.unstripped.noctf"'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'native kernel path'):
            self.stage()
        self.assertFalse(self.destination.exists())

    def test_bcm2837_diagnostic_kernel_is_rejected_as_target(self):
        profile = self.source / 'profile.toml'
        profile.write_text(profile.read_text(encoding='utf-8').replace(
            'DEVELOPMENT_ARM64_MSM8996/mach.development.msm8996.unstripped',
            'DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped'),
            encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'native kernel path'):
            self.stage()
        self.assertFalse(self.destination.exists())

    def test_linked_destination_is_rejected(self):
        elsewhere = self.root / 'elsewhere'
        elsewhere.mkdir()
        try:
            self.destination.symlink_to(elsewhere, target_is_directory=True)
        except OSError as error:
            self.skipTest(f'symlink creation unavailable: {error}')
        with self.assertRaisesRegex(ValueError, 'linked path'):
            self.stage()
        self.assertEqual(list(elsewhere.iterdir()), [])
        # Simulate Python 3.11, which does not provide Path.is_junction().
        with patch.object(STAGE.Path, 'is_junction', None, create=True):
            self.assertTrue(STAGE.linked(self.destination))

    @unittest.skipUnless(os.name == 'nt', 'Windows directory junction test')
    def test_junction_destination_is_rejected(self):
        elsewhere = self.root / 'elsewhere-junction-target'
        elsewhere.mkdir()
        result = subprocess.run(
            ['cmd.exe', '/c', 'mklink', '/J', str(self.destination), str(elsewhere)],
            capture_output=True, text=True, check=False)
        if result.returncode != 0:
            self.skipTest(f'junction creation unavailable: {result.stderr or result.stdout}')
        with self.assertRaisesRegex(ValueError, 'linked path'):
            self.stage()
        self.assertEqual(list(elsewhere.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
