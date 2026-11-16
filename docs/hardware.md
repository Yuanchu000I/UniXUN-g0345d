# GREE G0345D hardware inputs

These values describe G0345D, not the inherited G0245D reference board.
The source is the board DTS/configuration, stock QFIL/DTS observations recorded
during bring-up, and historical framebuffer experiments. A configured value is
not evidence that its complete driver works. The source inputs themselves are
not a redistributed OEM firmware package.

## Board identity and memory

| Input | Value / scope |
| --- | --- |
| Device / compatible | GREE G0345D / `gree,g0345d`, `qcom,msm8996` |
| SoC | Snapdragon 820, MSM8996 v3.1, four Kryo CPUs |
| `qcom,msm-id` | `<0xf6 0x30001>` |
| `qcom,board-id` | `<0x08 0x00>` |
| `qcom,pmic-id` | `<0x20009 0x10013 0x00 0x00>` |
| DRAM | 4 GiB beginning at `0x80000000` |
| Active cores | Boot CPU only; CPU1–CPU3 disabled in the device DTS |
| PAN | Disabled; this target is ARMv8.0 and must not inherit ARMv8.1 PAN instructions |
| Panic memory | `CONFIG_XNU_DT_PANIC_REGION=y`; no BCM2837 fixed panic-RAM assumption |
| Shared interrupt/timer resources | Supplied by the pinned `msm8996.dtsi`; GIC/IPI and secondary-core operation remain unqualified |

The board DTS reserves firmware-owned ranges, including:

| Base | Size | Purpose |
| --- | --- | --- |
| `0x83400000` | `0x1000` | DFPS scratch |
| `0x83401000` | `0x23ff000` | Continuous splash / inherited framebuffer |
| `0x85800000` | `0x3000000` | Removed/TZ/SMEM region |
| `0x88800000` | `0x6200000` | Modem region |
| `0x8ea00000` | `0x2d00000` | Peripheral/TZ region |
| `0x91600000` | `0x110000` | Resident aboot reservation as currently expressed in DTS |
| `0x91700000` | `0x600000` | Fixed UniXNU UEFI FD destination |
| `0xb1c00000` | `0x23ff000` | HDMI splash reservation |
| `0x178c00000` | `0x7400000` | Stock dynamic DMA pools represented by the current DTS |

Keep the original reservations for this diagnostic snapshot. The current DTS
contains overlapping aboot/peripheral/FD reservations and a reusable DMA pool
also marked `no-map`; these have not been newly reconciled here. They need a
separate audited memory-map change before claims of general DMA correctness.

## Framebuffer

The inherited scanout is RGB888, `1080 × 2160`, stride `3240` bytes,
physical address `0x83401000`. Three bytes per pixel are required; a 32-bit
pixel assumption corrupts the diagnostic image. Historical probes write
directly through this framebuffer. The exact panel candidate, backlight,
native MDP/DSI modesetting and OS presentation are not qualified by those marks.
`GopFramebuffer` is not in this board's selected component list.

## Storage and other peripherals

Stock observations describe a 64 GB UFS 2.0 device with 4096-byte logical blocks
and six LUNs. The configured LUN0 userdata interval is LBA `74312..14530554`.
LUN4 boot is `39690..56073`, system `56074..842457`, and recovery
`842506..866825`. These geometry facts do not establish a working XNU block
device or permission to write any partition.

The DTS enables `ufshc`, `blsp2_i2c6` and `gpu`; the defconfig force-loads the
NativeUfs8996, Blsp8996 and Adreno530 archives. Those are register-probe
scaffolds. UFS PHY/SMMU, MDP/DSI, native touch, GPU queues, network, cellular,
audio and power management remain incomplete. The UART command line names
`ttyHSL0,115200,n8`; physical UART capture is unverified.

## Frozen temporary-boot container

| Field | Value |
| --- | --- |
| Android header | Version 0; page size 4096 |
| `kernel_size` | 54,773,873 bytes |
| Kernel gzip segment | 8,565,237 bytes |
| Appended OEM DTB bundle | 46,208,636 bytes |
| Ramdisk / FAT payload | 25,165,824 bytes (24 MiB) |
| Ramdisk file offset | `0x343e000` |
| Whole image | 79,945,728 bytes |
| Kernel load address | `0x80008000` |
| Ramdisk load address | `0x81000000` |
| Tags address | `0x80000100` |
| FD destination | `0x91700000`, size `0x600000` |

The OEM appended DTB bundle is an external historical input. It is not the
output of compiling `dts/g0345d.dts`. The latter feeds the UniXNU/Apple-tree
path. See [firmware dependencies](firmware-dependency.md) before treating
either input as replaceable.

No hardware action was performed to prepare this repository. Future device
checks require an explicit resumption of testing and must use temporary boot
only. Flashing is outside this repository's workflow.
