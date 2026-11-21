# Official bring-up flow, 2026-11-20

Later continuation: the user requested the next diagnostic build.
An isolated XNU 8796.121.2 MSM8996 kernel adds a green `_start` marker and
reuses the logger firmware and remaining payload files. Its image has passed
host packaging. A subsequent user photograph shows its EBS-success red strip
and XNU-entry green strip; this supports entry-probe execution but not the
complete Stage 5 platform-expert goal. See
[the entry diagnostic record](stage4-entry-20261120.md). The following logger
capture is the earlier pre-handoff observation and remains unchanged.

This run resumes the authorized G0345D investigation in the order described by
the [pinned official bring-up guide](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/bring-up.md)
and [firmware log capture guide](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/log-capture.md).
The diagnostic image was accepted by temporary `fastboot boot` twice. The first
run displayed the Advanced Logger QR page; the second was accepted by fastboot
but did not record a menu or QR observation. The received OneSend log now
confirms Stage 1 and Stage 2. Host FAT readback supports the Stage 3 payload
files, with the device-log limitations recorded below. Those earlier logger
captures did not observe DarwinBoot or XNU entry. Historical M42/M71 iPadOS results do not
qualify this iOS 16.5 investigation.

An isolated ext4 snapshot of the legacy companion firmware completed a full
GCC5/AARCH64 DEBUG build; the retained local log is `build-full-03.log`. This
integrates `AdvLoggerPkg` and `MsGraphicsPkg` from
`microsoft/mu_plus@b8d46c71610318e36a661819e1e3c0b8bdda413a`: a DXE Core
Advanced Logger producer, DXE consumers and UniXNU's `AdvancedLogDxe` exporter.
The buffer uses 128 pages, the device model is `g0345d`, and INFO/ERROR output
is enabled. The inherited screen serial path remains available.

Replacing the old transitive DebugLib route exposed an existing
`PlatformScreenBar` dependency. The isolated
`PlatformBootManagerLib.inf` now explicitly lists `SerialPortLib`; this restores
its existing framebuffer dependency without changing the serial implementation.
The integration and this repair have separate local receipts and patches.
They have not yet been published as a complete companion source revision.

Independent final-FV verification passed in the local report
`firmware-verification-04.json` (SHA-256
`8421e2a5cf4abd441c553cee7686bff4c31829c6f13b0a95c21656a712cc9931`).
The inner and outer FV match the build outputs. Twelve extracted FFS PE
images match their built EFI files byte for byte and identify as AARCH64
PE32+. The producer constructor, consumer libraries, generated PCDs,
`g0345d` model and inherited serial dependency chain passed host checks.
These checks establish binary integration, not hardware protocol execution.

The host packer and byte-for-byte readback passed for these artifacts:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| DEBUG FD | 6,291,456 | `014989c02786b7fbfa0f5afb68dcf9d9422d0113a1fb2abee4243ae3d7d17771` |
| Temporary-boot image | 79,945,728 | `9db77d465331e8ad2d0186d7126ccd6ee0edf8970489e4fa953dbfb697dfc7f5` |
| FAT payload | 25,165,824 | `3a47517f6b94e01f86795763cd71b882534c5ca197f9ea13a68a1414f8807d86` |

The packer preserves the FD execution prefix, source-declared base
`0x91700000`, FD size `0x600000`, Android v0 page size 4096, header
`kernel_size` 54,773,873, stored-DEFLATE layout, appended DTB bundle and
ramdisk offset `0x343e000`. The base declaration is not independent proof of
the effective runtime address. The legacy transport remains separate from the
standard Mu-Silicium release pipeline. No binary or private input is included
in this repository.

The 24 MiB FAT retains attempt 27's kernel, adjacent ADT sidecar and small
RAM-root fixture byte for byte. Only the menu configuration changes: it adds
the Tools action and selects `default = "tools"`, `timeout = -1`, and
`fallback_timeout = 60`. The kernel is still the native-only XNU 8796.121.2
diagnostic with prelink skipped and no 20F66 donor kexts. It is not a qualified
iOS system image. FAT readback confirms:

- Kernel SHA-256: `eb0be0a26899abb1777fa0a8f4592d339af35f9a741afd180f725bfba7fc4874`.
- Adjacent ADT SHA-256: `4198fc29f87e8084f76438bcd1e6c8422559acf46dbc9eafebd0e0a76bb21f57`.
- Configuration SHA-256: `949124b5e52a885bdffcc948059fe001799c2a2bf732e2ad380729fa0f9d61fe`.

The received file `g0345d-20190100-000027.log` is 74,225 bytes and 739 lines;
SHA-256 is `4ee86e32440940dd9eb8538e8a000918f28ba289474139d1932c7be2f176a388`.
It is retained locally as
`probe/official-flow-20261120/captured/g0345d-firmware-stage23-20261120.log`;
the analysis is `probe/official-flow-20261120/captured/capture-analysis.json`.
The log shows `\EFI\UniXNU\unixnu.toml` opened successfully, 4 entries
loaded with 0 skipped, a 4-entry UniXNU menu, entry into Tools, and selection
of Advanced Logger. This confirms Stage 1 and Stage 2. It does not separately
print the `xnu` entry name or payload hashes. Host FAT readback confirms the
`xnu` entry, kernel/report hash match, and adjacent ADT/hash match, supporting
the file-side Stage 3 checks. The log ends as the logger snapshot opens, before
DarwinBoot; this is expected for a pre-handoff capture and does not indicate a
handoff failure.
The log itself has no embedded image digest tying it to one particular repeat
boot; retain that association limit when comparing it to the two boot records.

The log also contains `PartitionValidMbr: Bad MBR partition size
EndingLBA(C0EF) > LastLBA(BFFF)`. Preserve this as an untriaged storage-probe
diagnostic; the current evidence does not establish that it blocks the payload.
The `[ERR]`-tagged logger/RAM-disk/framebuffer diagnostics likewise include a
RAM-disk initialization line ending in `Success`; they are not by themselves
evidence of payload rejection.

At 2026-11-20 17:33:30+08:00, temporary `fastboot boot` of the image above
returned exit 0: Sending OKAY (1.898 s), Booting OKAY (0.121 s), total
2.062 s. The local records are `temporary-boot.log` and `temporary-boot.json`.
No partition-write command was issued. The command result establishes
transfer and boot-command acceptance only.
At 17:47:52+08:00, the same image hash was accepted again (Sending OKAY
1.902 s, Booting OKAY 0.114 s, total 2.055 s); that record has no menu/QR
observation. See `temporary-boot-02.log` and `temporary-boot-02.json`.

The official next step is to return from Advanced Logger to the UniXNU menu and
select the `xnu` entry with the already staged kernel and ADT. Capture any
returned-menu error log, then assess Stage 4 from DarwinBoot output (including
ExitBootServices and the kernel-entry path). Continue using temporary `fastboot
boot`; no partition-write procedure or validated persistent target is recorded.
The image is a native-only XNU 8796.121.2 diagnostic with prelink skipped and
without the 20F66 donor kexts; it is not a qualified iOS system image.
