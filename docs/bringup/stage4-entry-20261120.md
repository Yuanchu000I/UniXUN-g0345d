# Stage 4 / XNU entry diagnostic, 2026-11-20

The user authorized another diagnostic build after the
[official-flow logger capture](official-flow-20261120.md). Host build and
packaging completed first. A subsequent user-provided device photograph now
supports successful ExitBootServices and execution of the XNU entry-probe
stores. This reaches the earliest Stage 5 entry checkpoint; the complete
platform-expert goal remains unverified. The agent issued no device command,
reboot or partition write during build or photo analysis.

## Subsequent device photograph

The private photograph is 906,151 bytes, SHA-256
`d41aff43142b2337a22c3fd9b15251902fd7810c93ea2c9a1349f4f99097e046`.
It visibly contains the thin red strip and thick green strip at their expected
relative positions. The displayed physical kernel base `0xD0604000` plus the
linked entry offset `0x409488` equals displayed entry PA `0xD0A0D488`. The
displayed entry words `5800F949 D290E00A 5280000B 52801FEC` match the first
four instructions in the final entry-green kernel. This binds the observation
to its entry signature and test context; the photo contains neither a full
image digest nor an independently captured fastboot transport log.

VideoBase, row bytes and bpp are displayed as zero. The final DarwinEnter PE
has `cbz x4` at RVA `0x6a98`, skipping its generic green writer to `0x6ac0`
when VideoBase is zero. The PE/ELF region `0x6a94..0x6b28` matches, SHA-256
`2ce57cfcc58acdf9ff7ebc8071cd1c3a873bb9b8f2fdbfb0de922ed9b4217463`.
The separate board-specific firmware marker writes only the red rows 0–7.
Thus the old on-screen message about a loader green bar does not explain this
green entry strip. The menu and countdown remain from pre-handoff drawing.

Supported result: EBS returned successfully, then control reached this XNU
`_start` and executed its green framebuffer stores. A still photo does not
prove loop exit, completion of the following barrier or branch, entry into
`start_first_cpu`, bootstrap page-table construction, MMU enable, `arm_init`,
or platform-expert initialization. It also does not establish a hang duration,
fault instruction or repeatability. The private photo and `photo-result.json`
remain outside this repository; existing host receipts stay immutable.

## Change and build

An isolated copy of the attempt 27 device/output trees preserves all 40 prior
patches and adds only the RGB888 `_start` entry patch, SHA-256
`aa046760cf1032c3bff90a8707d4a9f43bf9cca3260411d29748b31bcac71b0e`.
The source reference remains `c54f35ca767986246321eb901baf8f5ff7923f6a`,
XNU 8796.121.2, selecting `DEVELOPMENT_ARM64_MSM8996`. The patch preserves x0
BootArgs, writes 1080 x 32 green pixels at physical `0x8341A500` (rows 32–63),
executes `dsb sy`, then branches to `start_first_cpu`. It does not alter Video
boot arguments, allocator behavior or driver functionality.

The first attempt exposed a generator mismatch when inherited generated files
were rebuilt: the default IIG emitted a `kernelContent` member absent from the
8796 IORPC definition. That failed receipt/log is preserved. The recovery
selected the existing XNU8796 IORPC4 generator, SHA-256
`55063fa04af1b6a275340adcf52c3f2fe33d1807962fc11c94eeff97c0842278`,
archived only the isolated XNU generated-build directory, and regenerated it.
The native-only build then returned exit 0. No source API was changed for this
recovery. The old kernel and configuration retain their original hashes.

Local evidence consists of `build-receipt.json` / `kernel-build.log` for the
failure, `build-receipt-02.json` / `kernel-build-02.log` for the successful
recovery, and `kernel-verification.json` / `entry.disasm.txt` for final binary
checks, all under the private `probe/stage4-entry-20261120` evidence directory.
These files and generated binaries are not published in this repository.

## Artifact identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Native ARM64 MH_EXECUTE | 17,956,280 | `dbd399718670124e2a52600f31f4a0b92cba878a42a6658c4ee87a607789403b` |
| FAT payload | 25,165,824 | `cc509a43192b22e8dfcf6a251efce1bb7d23f9a2275e4f6b632c6d69ce706cfe` |
| Temporary-boot image | 79,945,728 | `cdd7901533e68d6d455bb6ba11391a96a614309c09ccb9c0b4fc4d05fd1b3c1d` |

FAT readback verifies the complete file set and every non-kernel file byte
against the previous logger payload. The menu/default, ADT sidecar, boot
arguments and small RAM-root fixture are unchanged. The existing FD, SHA-256
`014989c02786b7fbfa0f5afb68dcf9d9422d0113a1fb2abee4243ae3d7d17771`,
already contains a red RGB888 marker after successful ExitBootServices.
Final-FV extraction matches the built DarwinBoot PE, SHA-256
`8167e44f7273da0fb4051ac8a8b7a1fe39d39a30e88e0ffe596cac84379658aa`;
the EBS/marker/entry instruction region matches the DEBUG ELF. Firmware was
reused without rebuilding.

The strict packer preserves Android v0 geometry, FD reservation, header
`kernel_size` 54,773,873, OEM DTB bundle and ramdisk offset `0x343e000`. The
image readback and a separate Windows SHA-256 check agree. This remains the
legacy diagnostic transport, not a standard clean-source release.

## Initial test procedure and next measurement

The initial test procedure uses only temporary `fastboot boot` of the exact
image hash above. Return from
Tools to the UniXNU menu, select `xnu`, and record the screen transition. A
visible red strip (rows 0–7) supports execution after EBS success; a visible
green strip (rows 32–63) supports execution of the XNU entry marker. Absence
of a strip alone is inconclusive because display visibility and later writes
can hide it. If control returns to the menu, capture a fresh Advanced Logger
snapshot. Do not infer runtime execution from host binary checks. The user
photo above now supplies the entry-probe observation. The next diagnostic
should add bounded checkpoints after the green loop, in `start_first_cpu`,
and around bootstrap mapping/MMU handoff without bypassing initialization.

Prelink remains skipped; no 20F66 donor kexts were added. Platform expert,
POST, BSD, real UFS/APFS root mounting and iOS userspace remain unverified.
Historical iPadOS M42/M71 milestones do not qualify this artifact.
