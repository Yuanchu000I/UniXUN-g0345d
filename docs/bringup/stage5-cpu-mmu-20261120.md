# Stage 5 CPU/bootstrap/MMU diagnostic, 2026-11-20

The user authorized the next diagnostic build after each completed review.
This host build follows the photo-confirmed
[XNU entry checkpoint](stage4-entry-20261120.md) and adds five bounded
framebuffer checkpoints before MMU enable. Build, final-binary verification
and packaging passed first. A subsequent user photograph now shows the
red/green/blue/cyan/yellow/magenta strips and supports arrival at the
pre-SCTLR checkpoint. The agent issued no adb, fastboot, reboot or
partition-write command during this build or photograph review.

This is an isolated native-only XNU 8796.121.2 / MSM8996 diagnostic for iOS
16.5 / 20F66, with prelink skipped and no 20F66 donor kexts. It does not replace
the repository's XNU 8796.101.5 proposal baseline or qualify a complete iOS
system. The official Stage 5 goal of reaching the platform expert remains
unverified. Historical iPadOS M42/M71 milestones do not qualify this image.

## Subsequent device photograph

The private photograph is 796,422 bytes, SHA-256
`3b6bcbf3b24c3886ec1bf6d16a707c2bc9aef1b54103aa92fcd6865d524e42c4`.
Red, green, blue, cyan, yellow and magenta strips are visible in their
expected order; no orange strip is observed. The displayed kernel PA
`0xD0604000` plus entry offset `0x409488` equals entry PA `0xD0A0D488`.
The displayed entry words `580100C9 D290E00A 5280000B 52801FEC` match
this final kernel. The first word also differs from the earlier entry-green
kernel's `5800F949`. Association with the image below rests on the test
context, checkpoint pattern and entry signature; the photograph contains
neither a whole-image hash nor an independent fastboot transcript.

Together with the final instruction ordering, the visible magenta strip
supports entry into `start_first_cpu`, passage through the BootArgs reads,
stack-register assignments and `arm_init` link-address conversion, completion
of both bootstrap mapping-construction loops and the original `dsb ish`,
and passage through the common-start TCR/TTBR/MAIR/VBAR setup path to the
pre-SCTLR pixel loop. The magenta probe starts at
`0xfffffff00740f408`; its final `dsb sy` is at `0xfffffff00740f434`,
followed by the original SCTLR write at `0xfffffff00740f438` and ISB at
`0xfffffff00740f43c`.

The photograph does not prove completion of that final probe barrier, the
following SCTLR write or ISB, successful MMU enable, correctness of the live
translations, stack-memory access, `arm_init`, platform expert, BSD, root
mounting or userland. No orange strip is consistent with this successful
pre-SCTLR path; it is not general memory-map validation. A single still
photograph does not locate a fault instruction or establish a hang duration
or repeatability. The menu and countdown are retained framebuffer contents.

The private photograph and separate `photo-result.json` record remain outside
this repository. Earlier host receipts retain their original false device
execution fields. The next measurement requires a bounded, legal bootstrap
framebuffer mapping before adding a post-MMU probe, then distinguishes
post-ISB execution from the `arm_init` handoff.

## Source and host build

The clean XNU reference remains
`c54f35ca767986246321eb901baf8f5ff7923f6a`. The isolated device preserves
the previous 41 patches in order and appends one diagnostic patch, SHA-256
`33ecf429ee82a9ce0da514ec2fda40bffc630b72797df49dbd2f4affaa45ddc8`.
A comparison of 4,999 source entries found only the intended
`osfmk/arm64/start.s` change. Existing initialization, page-table allocation
guards and the original SCTLR write/ISB sequence remain present.

The build uses independent copies of the previous output/device trees.
Absolute links into those previous trees were relocated and checked. The
copied generated XNU build was archived inside the new output, then regenerated
with the pinned IORPC4 IIG, SHA-256
`55063fa04af1b6a275340adcf52c3f2fe33d1807962fc11c94eeff97c0842278`.
The kernel build returned exit 0, selecting `DEVELOPMENT_ARM64_MSM8996`.
The old stable kernel and image retain their hashes.

Local evidence under the private `probe/stage5-cpu-mmu-20261120` directory
includes `build-receipt.json`, `kernel-build.log`, `kernel-verification.json`,
`cpu-mmu.disasm.txt`, `source-comparison.json`, `container-comparison.json`
and `validation.json`. The final verification state is
`host-build-binary-package-chain-passed`; `device_executed` and
`boot_verified` remain false in those preserved host records. These generated
files and binaries are not published in this repository.

## Checkpoint interpretation

The existing firmware red rows 0–7 and XNU entry green rows 32–63 are
unchanged. Each new strip covers 1080 x 16 RGB888 pixels, or 51,840 bytes.
Rows in the table are inclusive. The failure strip is an alternate branch,
not an additional successful stage.

| Strip | Rows | Physical start | Location and supported observation |
| --- | --- | --- | --- |
| A, blue | 80–95 | `0x83440480` | First instructions in `start_first_cpu`, before the original OSLAR/DAIF setup |
| B, cyan | 112–127 | `0x83459980` | After BootArgs reads, stack-register assignments and conversion of the `arm_init` link address, before clearing bootstrap tables |
| C, yellow | 144–159 | `0x83472E80` | After both bootstrap mapping loops and the existing `dsb ish` |
| D, magenta | 176–191 | `0x8348C380` | After preparing `SCTLR_EL1_DEFAULT`, immediately before the original SCTLR write |
| E, orange | 208–223 | `0x834A5880` | Existing bootstrap-table exhaustion guard was taken |

Final Mach-O instruction checks confirm bounded inline loops, no probe call
or stack access, and preservation of x0, SP and LR by each probe. The orange
failure path also preserves the offending table cursor x2 and end x10, draws
once, then enters its own final self-loop. It does not bypass the exhaustion
guard. A–C are on the first-CPU cold path; D has an x21 guard that skips its
stores on the warm path.

All new stores occur before the original MMU-enable write. No framebuffer
mapping or post-MMU physical-framebuffer access was added: the framebuffer
physical address is outside the existing bootstrap kernel window. A visible
magenta strip proves only that the pre-write checkpoint was reached, not that
the SCTLR write, ISB, MMU transition or `arm_init` succeeded. Cyan does not
prove stack memory can be accessed. Absence of a strip alone is inconclusive;
display visibility and subsequent writes can obscure a checkpoint.

## Artifact identities and packaging

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Native ARM64 MH_EXECUTE | 17,958,776 | `e0620cd292399b8a6cb0654a6b0101816b3b578fec7b8f4386ff46447cd4eb78` |
| FAT payload | 25,165,824 | `bb97c9ccc8d5bae1805cd4b92409f8f2b5ddee8aec95f07b2b6b4ba702a88f3d` |
| Temporary-boot image | 79,945,728 | `8f2936c1eaa65d900aa73a2787c332716e9ce26c7b764e18c19e23326875e387` |

The staged kernel is byte-identical to the native link output. FAT readback
checks the same four-file set and all three non-kernel files byte for byte.
The menu/default, boot arguments, small RAM-root fixture and adjacent ADT
remain unchanged. The ADT SHA-256 is
`4198fc29f87e8084f76438bcd1e6c8422559acf46dbc9eafebd0e0a76bb21f57`.

The reused FD SHA-256 is
`014989c02786b7fbfa0f5afb68dcf9d9422d0113a1fb2abee4243ae3d7d17771`.
Final DarwinBoot binary checks retain the existing EBS-success red marker.
The packer preserves Android v0/4096-byte geometry, FD declaration
`0x91700000`/`0x600000`, header `kernel_size` 54,773,873, ramdisk offset
`0x343e000` and the OEM DTB bundle. Before the ramdisk, comparison with the
previous image differs only in the boot ID field. An independent Windows
SHA-256 calculation agrees with the image manifest. This remains the legacy
diagnostic transport, not a clean-source standard release.

## Initial test procedure, before the photograph

Use only temporary `fastboot boot` of the exact image hash above. Return from
Tools to the UniXNU menu, select `xnu`, then record the screen transition and
the last visible strip. Preserve any returned-menu error log. A–D distinguish
first-CPU entry, pre-table initialization, completion of mapping construction
and the point before MMU enable; E identifies the existing protected failure
branch. Do not infer these device milestones from successful host checks.

After reviewing new device evidence, continue the next bounded diagnostic
build under the user's standing authorization. Platform expert, POST, BSD,
real UFS/APFS root mounting and iOS userland remain unverified.
