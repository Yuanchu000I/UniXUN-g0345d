# G0345D port status

Target revision: 2026-11-19, iPhone iOS 16.5 build 20F66 / Darwin 22.5.0,
with XNU 8796.101.5 as the open-source baseline. This is an experimental GREE
G0345D (Snapdragon 820 / MSM8996) target; it has not been built or booted.

The published main branch retains the earlier M42/v185 iPadOS snapshot. A later
M71/v213 development run on the same iPadOS/XNU baseline was reported to return
from bsd_init after mounting a small md0 MockFS root. Its untracked patch set
and full receipts are not included in this revision. These observations are
historical and must not be reported as iOS 16.5 results.

## Historical hardware observation

The M42 framebuffer photograph decodes to phase `0x4107`, value
`0x0467` (`1127`). Two independent analyses agree. The current STARTUP
callback is table index `878` (ZALLOC entry 6, zero based), function
`0xfffffff0079d6f94` (`_kalloc_init`), with a null argument.

Fixed-view parsing, the count/capacity assertions, the first fixed-view qsort
and `kalloc_type_create_iterators_fixed()` returned. The next interval contains
`kalloc_type_create_zones_fixed()` and its adjacent probe boundaries; its return
marker `0x4108` was not observed. This does not identify a particular size class,
the first `zone_create` call, a fault instruction, or whether execution stopped
or progressed too slowly to observe. The M41 on-disk metadata audit found 1,274
fixed views, including 1,127 non-data/VM views, and 402 variable views; it did not
establish corrupt on-disk metadata as the cause.

See [M42 result](bringup/M42-photo-result.md),
[independent analysis](bringup/M42-photo-independent.md),
[probe map](bringup/M42-probe-map.md), and
[M41 metadata audit](bringup/M41-kalloc-metadata-audit.md).

## What the repository supports

| Area | Established scope | Still missing |
| --- | --- | --- |
| Configuration | G0345D DTS/defconfig and historical device inputs are preserved | iOS 16.5 source/profile resolution and a complete rebased patch order |
| Firmware/loader | Historical temporary boot reached XNU through the legacy UEFI chain | Published companion firmware delta and standard release integration |
| CPU/memory | Boot CPU executes through early VM and allocator checkpoints | Secondary cores, interrupt/IPI qualification, complete memory/DMA validation |
| Display | Direct RGB888 framebuffer probe marks are visible | Native display/presentation and brightness control |
| Storage | NativeUfs8996 probe archive is selected and linked | UFS transfer, LUN/GPT/root/Data validation |
| Input/GPU | BLSP/Adreno530 probe scaffolds are selected and linked | Touch input, GPU submission/fences and OS frontend |
| Network/cellular/audio/power | Required future work is recorded | Functional device validation |
| Packaging | Official script interface and historical container checks are recorded | Standard macOS release producing verified artifacts from a clean checkout |

The historical M42 fastboot log reports `Sending OKAY` (2.002 s),
`Booting OKAY` (0.115 s), total 2.163 s. These are transfer/boot-command results;
they do not establish full XNU or userland startup.

## Historical artifact identities

Only text manifests, logs and analysis are included. Images, Apple inputs,
OEM binaries, device identifiers/seeds and original photographs are excluded.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| M42 native kernel | 18,207,264 | `aac6aceb8f601ab312ea8598e4f658abf7ec83706c0cbc8a4e75c40088dd781a` |
| M42 FAT payload | 25,165,824 | `410f7e14b837932a10471ee3765f9c7c7f2ac494bda1fa07259b88ccfd1174ad` |
| M42 temporary-boot image | 79,945,728 | `498c23b58b71d64291bf921f7d4f95356fd0aba1fd8b872707df1e9f326ad726` |
| M42 ADT | 12,984 | `bd019ec8bc0c0266ed3cce366e2aec5b1be23f6f14473c8b596adca93ebe112e` |

The [historical manifest](evidence/g0345d-payload-M42-v185.img.json) identifies
the retained container geometry. A regenerated ADT can have a different random
seed and must be identified by its actual manifest hash.

## Verification language

`porting.toml` is the authoritative structured record. Its states are
`implemented` or `planned`: the historical experiments used dirty development
trees, and no complete published source commit identifies all firmware and
tool changes. The retained logs are historical observations, not new
`host-verified` or `device-verified` certification of this curated snapshot.

Record checking uses the official schema checker with a pinned fork component
catalog containing MSM8996 IDs. A passing local record check does not mean the
stock upstream workflow or catalog has accepted this device.

## iOS 16.5 readiness

The exact restore manifest and XNU 8796.101.5 source are missing. The proposed
OS profile is documented under docs/os-profile-proposal/ios-16.5-20F66/, but
UnixNu resolves profiles from the central UniXNU/profiles/os tree. The existing
M71 patch stack targets XNU 10063.141.1 and is not selected for 8796.101.5.
An empty patch list is not a CLI build guard. The next engineering step is to
land the profile centrally, verify the restore inputs, then rebase and validate
the ARM64/MSM8996/G0345D patch layers before any build or boot.

## Stopped experiment and next measurement

This publication update does not include a kernel or firmware build, image
production or device test. The M42/v185 files on main remain a separate
historical snapshot. A future allocator investigation should distinguish policy
calculation, its inner sort,
the 29 fixed size classes, `create_zone_for_size`, shuffle/signature equivalence
and type distribution before changing allocator behavior.

Any future hardware experiment must use temporary `fastboot boot` only.
Do not flash, change the fixed FD, alter header `kernel_size` or the frozen
kernel/container layout, or bypass allocator initialization to obtain a later
marker. See [hardware facts](hardware.md) and
[firmware dependencies](firmware-dependency.md).
