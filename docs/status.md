# G0345D port status

Snapshot: 2026-11-16, M42 / v185. This is an experimental GREE G0345D
(Snapdragon 820 / MSM8996) port of the `ipados-17.7.11-21H461` profile.
It has not completed XNU startup or reached an interactive operating system.

## Latest historical hardware observation

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

## What the snapshot supports

| Area | Established scope | Still missing |
| --- | --- | --- |
| Configuration | G0345D DTS/defconfig and 51 ordered device patches are preserved | Clean-checkout end-to-end reproduction |
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

## Stopped experiment and next measurement

After M42 photo analysis the user requested a stop. Repository preparation
does not resume kernel or firmware builds, image production or device testing.
No M43 probe is part of this snapshot. If experiments are explicitly resumed,
the next measurement should distinguish policy calculation, its inner sort,
the 29 fixed size classes, `create_zone_for_size`, shuffle/signature equivalence
and type distribution before changing allocator behavior.

Any future hardware experiment must use temporary `fastboot boot` only.
Do not flash, change the fixed FD, alter header `kernel_size` or the frozen
kernel/container layout, or bypass allocator initialization to obtain a later
marker. See [hardware facts](hardware.md) and
[firmware dependencies](firmware-dependency.md).
