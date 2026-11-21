# UniXNU on GREE G0345D

[中文说明](README.zh.md) | [Porting record](porting.toml) | [Current status](docs/status.md)

Experimental GREE G0345D (G3), Qualcomm MSM8996, targeting iPhone iOS 16.5
build 20F66 / Darwin 22.5.0. Current diagnostic sources use XNU 8796.121.2
and 46 ordered patches: native-only, prelink skipped, no 20F66 donor kexts.
This is an experimental source prerelease, not an installable iOS distribution
or a complete iOS boot.

## Current checkpoint — 2026-11-21

Official Stage 5 (kernel entry through platform expert) remains in progress,
after early PE return and within WFE/clock initialization. Earlier evidence
supports firmware, menu, payload and DarwinBoot handoff. Stage 6 storage/root
and Stage 7 userland have not been reached.

The latest v9 white WFE entry band and red classifier slot, together with
audited machine code, support real timebase=0, quotient=0 and index=0xffffffff
at pixel stores before the original shift. They do not identify a trap PC,
establish the precise zero-clock cause, prove the final DSB or subsequent
shift/UBSAN path, or establish function return or stability.

v10 reuses the exact v9 kernel and changes only nine ADT u64 fields (ten bytes)
for an isolated MSM8996 64 KiB SoC window adaptation. All seven register ranges
retain their physical addresses and lengths; real 19.2MHz, WFE and UBSAN remain.
Independent FAT/ADT and Windows checks passed. Finalization is
ready-for-temporary-device-test; **v10 has not been device-tested**. See the
[derived v9/v10 summary](docs/bringup/stage5-wfe-v10-20261121.md).

## Sources and readiness

- [diagnostics/ios16-20F66](diagnostics/ios16-20F66/README.md) contains the exact
  46-patch source series, public tools, pins, manifests and sanitized summaries.
- [The root iOS profile](docs/os-profile-proposal/ios-16.5-20F66/) remains a
  separate XNU 8796.101.5 proposal. It did not build v9/v10. Board and profile
  patch lists remain empty; that does not prevent an unpatched CLI build.
- Root patches/xnu/series is empty. The 51 iPadOS 17 patches were retired after
  hash verification; [immutable history remains](docs/ipados17-abandoned.md).
- iPhone10,3 is an OS donor identity, not the target board. Full 20F66
  kernelcache/prelink inputs and component ABI compatibility remain unresolved.
  UFS/BLSP/Adreno selections are probe scaffolds.
- Clean end-to-end reproduction still requires the complete companion firmware
  delta and lawful Apple/OEM inputs. Historical scripts are not a qualified
  standard iOS release recipe.

## Offline validation

~~~sh
python3 scripts/check-repository.py
python3 diagnostics/ios16-20F66/check_export.py
git diff --check
~~~

These source and record checks do not compile a kernel, test a device, qualify
drivers or demonstrate iOS userland. See [publication limits](docs/publication.md).

## Official guides

- [Device format](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/device-repository.md)
- [Porting records](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/records.md)
- [Packaging](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/packaging.md)
- [UEFI separation](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/uefi-firmware.md)

No binaries, raw ADT, original photos, identifiers/seeds, credentials, private
reports or local absolute paths are distributed. Hardware tests require
separate authorization and may use temporary fastboot boot only.
