# iOS 16.5 profile provenance

This profile selects the iPhone OS release **iOS 16.5 (20F66)**, reported as
Darwin **22.5.0**. The selected source baseline is XNU **8796.101.5** at
aca3beaa3dfbd42498b42c5e5ce20a938e6554e5, following the pinned
UniXNU-NX769J reference profile. This is a UniXNU porting baseline; it is not
a claim that this commit is the exact source revision used in Apple's retail
20F66 kernel.

The reference restore product iPhone10,3 is only the iPhone OS software donor
identity. This profile does not adopt NX769J's hardware identity. The target
remains GREE G0345D with its real MSM8996 SoC, device tree, firmware, storage
layout, and board drivers.

## Deliberately unresolved inputs

The selected iPhone10,3/iPhone10,6 20F66 restore URL is recorded in
profile.toml. A lightweight BuildManifest read verified device_class = d22ap,
chip_id = 0x8015, and board_id = 0x06; these identify the iPhone OS donor and
do not describe G0345D. Component SHA-256 values, fetch member selection, and a
complete local IPSW verification are still pending. No unverified hash, UUID,
or prelink value is guessed.

The profile contains no ADT identity, DeviceTree, nonce, kernelcache hash,
prelink slide, root list, early-security initializer, or other NX769J prelink
values. Derive and qualify prelink inputs against the exact 20F66 kernelcache
and G0345D port. Keep G0345D/MSM8996 board values in the device and SoC layers.

The iOS config fragment enables only the existing mock-filesystem and native
code-signing hash-cache options. It does not enable runtime trust-cache
enforcement: the G0345D native-only bring-up has not qualified the Apple
Image4/AMFI provider closure. The OS-specific XNU patch series is intentionally
empty pending rebasing and applicability checks on the selected source.

## Integration requirements

1. Set the G0345D board's os_profile to ios-16.5-20F66 and use
   os:configs/ios.config; preserve name = g0345d, soc = msm8996, the G0345D
   DTS, and all board-level firmware, storage, and driver inputs.
2. Resolve the iPhone 20F66 restore metadata from its manifest, then set the
   required IPSW fields and verify the profile against that local restore.
3. Derive G0345D-compatible prelink inputs from that restore's kernelcache;
   do not import donor-board addresses or ADT properties.
4. Rebase and strictly apply each selected ARM64, SoC, and G0345D patch series
   against the pinned XNU baseline before invoking kernel build or device boot.
5. Record the resolved source SHA, IPSW member hashes, prelink report, build
   inputs, and hardware checkpoints before treating the profile as integrated.

## Host patch audit

On 2026-11-19, a clean isolated XNU 8796.101.5 worktree was used for
sequential apply-check and application. Twenty-one ARM64 candidates selected from the pinned
official series applied in their original relative order, and the MSM8996
0001-msm8996-smp.patch also passed git apply --check after them. The audit did
not apply G0345D's historical 51-patch series, did not compile XNU, and did
not change the active board or OS patch_series; its candidate list and
limitations are recorded in patch-audit.toml.

A separate host diagnostic experiment completed on 2026-11-19 against XNU
8796.121.2 (`c54f35ca767986246321eb901baf8f5ff7923f6a`) and selected
`DEVELOPMENT_ARM64_BCM2837`. Its ARM64 artifact passed a host-only static audit,
but it is not an MSM8996 build. This later experiment does not replace the
selected 8796.101.5 proposal baseline or change the scope/result of the
8796.101.5 candidate patch audit. The [machine-layer audit](machine-layer-audit.md)
records its qualification limits and the missing build support.

The portable runtime copy is now in profiles/os/ios-16.5-20F66. Run
`python3 scripts/stage-os-profile.py --tools /path/to/UniXNU` to install its
three files into an explicitly selected tools checkout. The script rejects
different existing files and never enables a patch stack. Its profile declares
the expected target native-kernel staging path and Linux SDK/triple 16.5; these require the
profile-driven tooling compatibility patch. Original kernelcache/prelink
qualification remains a separate unresolved input.

## Sources

- The local profile schema and layer merge rules: UniXNU scripts/unixnu/profiles.py
  and scripts/unixnu/feeds.py.
- The build's IPSW identity checks and optional hash pin behavior:
  UniXNU scripts/unixnu/ipsw.py.
- OS/version/source baseline: pinned UniXNU-NX769J reference profile at
  https://github.com/Asultop/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/os-profiles/ios-16.5-20F66/profile.toml.
- iOS 16.5 release/build identifier: Apple iOS 16.5 security release notes
  and the same pinned reference profile.
