# Companion firmware and reproducibility gap

The historical G0345D boot chain uses a legacy `edk2-porting/edk2-msm8998`
derived firmware tree with local MSM8996/G0345D adaptations. It is not the
current official Mu-Silicium implementation. This device repository contains
board selection, DTS, kernel patches and text evidence. The adapted firmware
belongs in a separately published companion firmware repository under the
official separation of device and UEFI sources.

## Recorded source baselines

| Source | Baseline commit |
| --- | --- |
| Legacy edk2-msm8998 firmware tree | `ace27110b9b9b6c591387d50cf748ec646402b4a` |
| `Common/edk2` | `e7aac7fc137e247edad22f7ee53b9a1fba227397` |
| `Common/edk2-platforms` | `35a84b1838baacf0d470e76fb68a6ade30413450` |
| `GPLDrivers/Library/simple-init` | `29e062805776db5ab7a61d07ef040d43aed71161` |
| Nested DarwinBoot source | `5243c68ec332a227fe3680cd5da6d5a0e127035c` |

These commits identify starting points, not a complete reproducible M42
firmware source state. The development tree additionally has uncommitted
changes/additions in `build.sh`, `Config/default.conf`, `Config/g0345d.conf`,
`Platforms/Msm8996FamilyPkg`, `Platforms/Msm8996Pkg`, `Silicon/QC/Msm8996`,
`UniXNUPkg`, the edk2/FdtLib integration, and DarwinBoot's source, INF and entry
assembly. SimpleInit also has local changes and Windows-checkout symlink
problems. Those changes have not been exported as a complete licensed,
build-verified companion repository in this snapshot.

The board metadata records the legacy DSC and FD location:

```text
Platforms/Msm8996Pkg/Device/gree/g0345d/g0345d.dsc
Build/g0345d/{target}_GCC5/FV/MSM8996PKG_UEFI.fd
FD base 0x91700000, size 0x600000
```

The current FDF still contains early RAW fixtures (an 8192-byte kernel and a
56-byte ADT). Running the ordinary firmware `build.sh` is not a recipe for the
frozen M42 FD/container: its ordinary image header/offset choices also differ
from the retained Android v0 container. Do not replace the proven FD or claim
these baseline commits alone reproduce M42.

## External image input

The historical strict repacker requires a privately retained M34-v177split
template image with SHA-256
`56a2c1dca6900c3d4fdfef504608836f5fb3661160f26db1174f69d141317315`.
That image is not included or downloadable from this repository. It contains
the frozen kernel container/firmware and a 46,208,636-byte appended OEM DTB
bundle. A verified lawful source and extraction process for all such inputs
must be documented before independent reproduction can be claimed.

The repacker validates template identity, Android header geometry, FAT contents,
the native kernel, configuration and ADT. It replaces the 24 MiB ramdisk and
boot ID while preserving the remaining container. ADT equality permits only
the `/chosen/random-seed` difference. An actual ADT hash must come from the
matching production manifest, because fresh random seeds change that hash.
This is a historical container-preservation tool, not a substitute for the
official `scripts/package.sh` release path.

No Apple kernelcache, IPSW, OEM image, FD binary, personal platform seed,
device serial or original photograph is distributed. See
`proprietary-files.txt` for the external-input inventory.

## Required work before standard packaging

1. Export and review the full companion firmware source delta, submodule pins,
   licenses, symlinks and G0345D-specific build inputs.
2. Replace or explicitly integrate the RAW fixtures and reconcile the legacy
   DSC/FDF, BootShim, FD placement, loader protocol and image geometry.
3. Document lawful firmware/OEM input URLs, extraction recipes and hashes;
   generate or otherwise account for the exact required DTB bundle.
4. Integrate the firmware checkout with UniXNU's standard release pipeline and
   verify that a clean checkout creates the intended payload and boot image.
5. Resume hardware testing only when separately authorized, using temporary
   `fastboot boot`, with the fixed-container checks retained.

The standard package interface is present for migration, but its end-to-end
macOS release is pending. Repository record checks and a manual packaging
preflight must not be described as successful artifact production.
