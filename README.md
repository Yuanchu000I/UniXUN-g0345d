# UniXNU on GREE G0345D

[中文说明](README.zh.md) | [Porting record](porting.toml) | [Current status](docs/status.md)

Experimental GREE G0345D (G3), Qualcomm MSM8996, targeting iPhone iOS 16.5
build 20F66 (Darwin 22.5.0), with XNU 8796.101.5 as the open-source baseline.
The iPhone10,3 restore identity is an OS donor only; the target board remains
G0345D/MSM8996. This is not an installable iOS distribution or an officially
supported UniXNU device.

No iOS 16.5 kernel has been built or booted. The XNU 8796.101.5 source and exact
restore manifest are not present, and the existing device patches target a
different XNU generation. The latest recorded M71/v213 result belongs to the
previous iPadOS 17.7.11 / XNU 10063.141.1 experiment: it reached bsd_init after
mounting a small md0 MockFS root. That does not qualify iOS 16.5, physical UFS,
APFS, or iOS userland. See [current status](docs/status.md).

## Repository and Prerequisites

The board uses device repository format 2 and a structured format 1 porting
record. G0345D hardware, firmware, DTS, storage geometry and peripheral inputs
remain board-specific. The iOS profile is a proposal because UnixNu resolves
OS profiles from the central UniXNU profiles/os directory, not from a device
repository. See [the proposal](docs/os-profile-proposal/ios-16.5-20F66/).

The published main branch preserves the earlier M42/v185 iPadOS source snapshot.
This branch changes the selected OS target but does not include the incomplete
and untracked M71 probe patch set. Historical M71 observations are labeled as
such and are not evidence for iOS 16.5.

## Build Readiness

Do not build or boot iOS 16.5 from this branch yet. First the proposed profile
must be accepted into the central UniXNU profiles tree. Then obtain and verify
the exact restore manifest and XNU source, inspect the resolved ARM64 and
MSM8996 inputs, and rebase and validate the required ARM64/MSM8996/G0345D patch
order against XNU 8796.101.5. The empty patch list is not a build guard: the CLI
can still build an unpatched kernel. The historical package and fastboot scripts
are not a tested iOS 16.5 recipe.

## Validate

After the OS profile is available in the central UniXNU checkout, inspect the
resolved configuration and source layers before any build:

```sh
./unixnu status --json -D ../UniXNU-g0345d
./unixnu tree -D ../UniXNU-g0345d
python3 scripts/check-repository.py
```

These commands have not been run for this proposal. A successful configuration
or record check would not establish an iOS kernel build or device boot.

## Official Guides

- [Device repository format](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/device-repository.md)
- [Structured porting records](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/records.md)
- [Packaging](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/packaging.md)
- [UEFI separation](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/uefi-firmware.md)

Apple/OEM images, firmware, device seeds and local overrides are external
inputs. No binary or original device photograph is distributed here.
