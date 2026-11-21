# Stage 5 mapped post-MMU diagnostic, 2026-11-20

The preceding [CPU/bootstrap photograph](stage5-cpu-mmu-20261120.md) shows
red, green, blue, cyan, yellow and magenta strips. That confirms arrival at
the checkpoint before the SCTLR write; it does not confirm MMU enable. Under
the user's standing authorization to build after each review, this next
diagnostic adds a bounded framebuffer mapping and two later checkpoints.
Host build, final-binary verification and packaging passed first. A subsequent
user photograph now shows both white and gray checkpoints. The agent issued
no device command during the build or photograph review.

This remains native-only XNU 8796.121.2 / MSM8996 for the iOS 16.5 / 20F66
investigation, with prelink skipped and no 20F66 donor kexts. The independent
diagnostic does not replace the repository's XNU 8796.101.5 proposal baseline.
The complete Stage 5 platform-expert goal, BSD, real UFS/APFS root mounting
and iOS userland remain unverified. Historical iPadOS results do not qualify
this image.

## Subsequent device photograph

The private photograph is 811,911 bytes, SHA-256
`ad792210fa0a61f1ee3e125e64b193893adce042b08df659ec593d2126b0bd6e`.
Red, green, blue, cyan, yellow, magenta, white and gray strips are visible;
no orange strip is observed. The displayed kernel PA `0xD0604000` plus
entry offset `0x409488` equals entry PA `0xD0A0D488`. Entry words
`58010609 D290E00A 5280000B 52801FEC` match this final kernel, including
its changed literal-load displacement. The photograph contains neither a
whole-image digest nor an independent fastboot transcript; image association
rests on the test context, matching entry signature and checkpoint pattern.

In the final binary, the original SCTLR write at `0xfffffff00740f478` and
ISB at `0xfffffff00740f47c` precede the white loop. The gray loop starts
at `0xfffffff00740f4e8`, its final barrier is at `0xfffffff00740f514`,
and the retained `ret` is at `0xfffffff00740f518`. Together with the ordered cold-start path, the gray
observation supports passage through the SCTLR/ISB boundary, mapped
framebuffer stores, completion of the white loop and its `dsb sy`, the
existing prepared-SCTLR-value comparison, CPACR/TPIDR setup and BootArgs
KVA argument calculation. The comparison checks preserved x0 against the
expected constant; it is not a hardware SCTLR readback.

The new device checkpoint is arrival at the pre-return gray stores. The
photograph does not prove completion of the gray loop's final `dsb sy`,
execution of `ret`, correctness of its target, C `arm_init` entry, stack
memory access, platform expert, BSD, root mounting or userland. The visible
post-ISB stores do not qualify every live translation, later memory
management, DMA or a native display driver. A single still photograph does
not identify a fault instruction, elapsed hang time or repeatability. The
menu and countdown are retained pre-handoff framebuffer contents.

The private photograph and separate `photo-result.json` remain outside this
repository. Original host receipts retain their false device-execution
fields. The next measurement should distinguish the retained return from
actual C entry and stack-memory access.

## Change and host verification

The isolated build retains the previous 42 patches in order and appends one
`osfmk/arm64/start.s` patch, SHA-256
`431657fa5969ab89004aeae9ea9d83fcb96fd5db8c63f714807cc19596965277`.
The clean XNU reference remains
`c54f35ca767986246321eb901baf8f5ff7923f6a`. A comparison of 4,999 source
entries in each tree found only the intended `start.s` change. Existing
red/green and pre-MMU probes, initialization and allocation guards are retained.

The build uses independent device/output copies, checks relocated links and
regenerates the copied XNU build directory with the pinned IORPC4 IIG. It
returned exit 0 for `DEVELOPMENT_ARM64_MSM8996`. The staged kernel is
byte-identical to the native link output. Final Mach-O checks validate the
mapping instructions, descriptor attributes, actual linked TCR/MAIR values,
probe bounds, cold-path guards and retained SCTLR-write/ISB sequence. Probe
instructions preserve x0, SP and LR; neither new probe calls a function or
accesses the stack. Old stable artifacts retain their hashes.

The private `probe/stage5-postmmu-20261120` evidence includes the build
receipt/log, `kernel-verification.json`, `cpu-mmu.disasm.txt`, source and
container comparisons, payload report and `validation.json`. The kernel
verification SHA-256 is
`e849afa471a9317eab751217dec668f7ff78708fb406bb156be8cf786e3433c3`.
The validation state is `host-build-binary-package-chain-passed`, SHA-256
`a6ec4b5906adc3914ab6fd08be545a531a46dc61b8813c4fc46707f80f538e4d`.
An independent Windows verification matches the artifact hashes and all
14 evidence hashes. Device-execution and boot-verification fields remain
false in the original host receipts. Generated files and binaries are not
published here.

## Bounded framebuffer mapping

After the existing yellow checkpoint, the cold-start path adds one 2 MiB
identity-mapped block: VA and PA `0x83400000` through `0x835FFFFF`. It covers
the diagnostic strips without mapping the entire framebuffer reservation.
With the linked 4 KiB granules and 39-bit TTBR0 VA space, it uses L1 index 2
and L2 index 26. The leaf descriptor is `0x006000008340060d`, selecting
MAIR AttrIdx3, Device-nGnRnE, EL1 read/write and both privileged and
unprivileged execute-never. Linked TCR is `0x22a5192519`; MAIR is
`0x0c08044f00bb44ff`, with AttrIdx3 equal to zero. These are host-verified
linked values, not a device register capture.

The code refuses an occupied parent slot by entering a distinct self-loop.
It allocates the L2 page from the previously cleared bootstrap pool with the
existing exhaustion boundary check, writes the leaf before publishing the
parent, and retains a `dsb ish`. It does not overwrite an existing kernel
mapping or bypass exhaustion. The old orange strip still marks pool
exhaustion; the separate occupied-parent refusal has no dedicated color.
Visible probes do not qualify general memory, DMA or display-driver behavior.

## New checkpoints and interpretation

Both strips are cold-path-only, use the mapped identity address, and write
1080 x 16 RGB888 pixels each. Rows are inclusive. The previous strips retain
their positions and meanings.

| Strip | Rows | Address | Instruction boundary |
| --- | --- | --- | --- |
| White | 240–255 | `0x834BED80` | After the original SCTLR write and ISB |
| Gray | 272–287 | `0x834D8280` | Immediately before the retained return to `arm_init` |

In the final binary the SCTLR write is at `0xfffffff00740f478`, ISB at
`0xfffffff00740f47c`, white loop at `0xfffffff00740f484`, gray loop at
`0xfffffff00740f4e8`, and the retained `ret` at `0xfffffff00740f518`.
A visible white strip would support execution after the SCTLR/ISB boundary
with the diagnostic framebuffer mapping usable for those stores. It would
not validate every live translation or later memory management. A visible
gray strip would support arrival at the pre-return stores, not execution of
`ret`, entry into the C `arm_init` routine, or return from it. Neither strip
proves completion of its final barrier. Absence of a strip alone does not
locate a fault because visibility and later writes may obscure it.

## Artifact identities and packaging

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Native ARM64 MH_EXECUTE | 17,959,088 | `b0dc5bfcc3ad9c2331e0331dbc0b438dfe985405529dc8b69ff2a47964d38bfa` |
| FAT payload | 25,165,824 | `7c14734f6010bc28670eac4458e56541edfd723bbfc64b78bccfbf62a94199b5` |
| Temporary-boot image | 79,945,728 | `f9f76d36ebcf560e548d60bda88b847c61b1dcac67f48150d55e196b9b4c3ac6` |

FAT readback retains the same four-file set; all three non-kernel files are
unchanged. The menu/default, boot arguments, RAM-root fixture and ADT remain
unchanged. The reused FD SHA-256 is
`014989c02786b7fbfa0f5afb68dcf9d9422d0113a1fb2abee4243ae3d7d17771`.
The fixed Android v0/4096-byte geometry, FD declaration
`0x91700000`/`0x600000`, header `kernel_size` 54,773,873, ramdisk offset
`0x343e000` and OEM DTB bundle are preserved. This remains the legacy
diagnostic transport, not a clean-source standard release.

## Initial test procedure, before the photograph

Temporarily boot the exact image above using `fastboot boot`, return from
Tools to the UniXNU menu and select `xnu`. Capture the full screen including
the old strips and the new white/gray positions, or preserve a returned-menu
log. The current device checkpoint remains the preceding image's pre-SCTLR
magenta observation until new evidence establishes a later boundary. Review
that evidence before interpreting the next bounded build.
