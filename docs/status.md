# G0345D port status

Updated 2026-11-21. Target: GREE G0345D / MSM8996, iPhone iOS 16.5 build
20F66 / Darwin 22.5.0. Current diagnostics use native-only XNU 8796.121.2,
46 patches, skipped prelink and no 20F66 donor kexts. No complete iOS system
boot or qualified userland has been demonstrated.

## Current Stage 5 checkpoint

The official seven-stage process remains in Stage 5 (kernel entry through
platform expert), after early PE return and within WFE/clock initialization.
Earlier evidence supports firmware, menu, payload and DarwinBoot handoff.
Stage 5 is incomplete; Stage 6 storage/root and Stage 7 userland are unreached.
Local v9/v10 iteration numbers are not official stage numbers.

The latest v9 white entry band and red classifier slot support real timebase=0,
quotient=0 and index=0xffffffff at audited pixel stores before the original
shift. They do not prove final DSB, subsequent shift/UBSAN, trap PC, precise
zero-clock cause, function return or stability. Image association lacks an
independent full-image transfer digest. See the
[derived v9/v10 summary](bringup/stage5-wfe-v10-20261121.md).

v10 changes only nine ADT u64 fields (ten bytes), uses
arm-io/ranges=(0,0x60000,0x9fa0000), and preserves every physical address and
length of seven exported reg ranges. Real 19.2MHz, low-address hardware, WFE
and UBSAN remain. It reuses the exact v9 kernel; there was no XNU rebuild or
47th patch. Independent FAT/ADT and Windows fixed-envelope/FD/OEM DTB,
boot-ID and decompression checks passed. Finalization is
ready-for-temporary-device-test. **v10 has not been device-tested**.

| Artifact identity only; binaries excluded | Bytes | SHA-256 |
| --- | ---: | --- |
| v10 image | 79,945,728 | 409f9bf8517294aeca48c5e0401195c19dbf3c75eb36995cea24e81c7e0c173e |
| v9 kernel reused by v10 | 17,961,240 | af1550fdd5e219d54cb49e7a4806dcbfb8ef3778c03b381d4c88647355b94ab2 |

## Source qualification

The [diagnostic export](../diagnostics/ios16-20F66/README.md) publishes the exact
46-patch source series, tools and derived summaries. Private frozen receipts
retain original contents; the curated publication commit is not misrepresented
as the historical build commit. The isolated diagnostic record checker retained
exit 1 with only device.soc must match board.toml; not all official checks passed.

Root XNU 8796.101.5 remains an independent proposal, not the source of v9/v10.
Board and profile patch lists are empty. Component hashes, kernelcache/prelink
inputs and ABI compatibility remain unresolved. The root checker verifies
applicable historical inputs and delegates current integrity to check_export.py;
it does not build a kernel.

| Area | Established scope | Still missing |
| --- | --- | --- |
| Configuration | G0345D identity, separate profile proposal and exact diagnostic export | Complete clean iOS integration |
| Firmware/loader | Prior UEFI/menu/payload/DarwinBoot handoff evidence | Complete companion delta and standard release integration |
| CPU | WFE classifier stores after early PE return | Hardware clock result, timer/IRQ/IPI, secondary cores and sustained scheduling |
| Memory | Bounded framebuffer mapping; preserved seven MMIO physical ranges | Full VM, DMA and SMMU qualification |
| Display | Direct RGB888 diagnostic stores visible | Native presentation, brightness and GPU submission |
| Storage | NativeUfs8996 scaffold selected | Physical transfers, GPT/LUN, APFS/root/Data validation |
| Input/GPU | BLSP/Adreno530 scaffolds selected | Touch reports, GPU submission/fences and frontend |
| Network/cellular/audio/power | Future work recorded | Functional validation |
| Packaging | v10 host FAT/ADT and container audits | Clean standard release with lawful inputs |

## Retired history and verification language

iPadOS 17 work is abandoned. M42/v185 and M71/v213 observations belong to
iPadOS 17.7.11 / XNU 10063.141.1; they never qualify the iOS target. The 51 root
patches were hash-checked against the unchanged historical manifest and removed;
[history remains available](ipados17-abandoned.md).
Earlier [entry](bringup/stage4-entry-20261120.md),
[CPU/bootstrap](bringup/stage5-cpu-mmu-20261120.md) and
[post-MMU](bringup/stage5-postmmu-20261120.md) pages are dated checkpoints whose
then-current next steps are superseded by the v9/v10 summary.

porting.toml uses implemented/planned states. Passing the local record-schema
checker with the pinned fork catalog is not stock upstream catalog acceptance,
hardware certification or a clean release. Original photos, raw ADT, binaries,
seeds, serials, private reports and local absolute paths are excluded. Future
authorized tests use temporary fastboot boot only and never flash partitions.
