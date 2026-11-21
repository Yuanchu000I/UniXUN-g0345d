# G0345D/MSM8996 machine-layer gate

Reviewed on 2026-11-20 against the pinned XNU 8796.101.5 proposal source and
the isolated 8796.121.2 host experiment at
`c54f35ca767986246321eb901baf8f5ff7923f6a`. Both source trees register only
BCM2837, T6000, T8101, T8103, and VMAPPLE ARM64 machine configurations. The
device proposal still selects XNU 8796.101.5; the later host experiment does not
silently change that proposal baseline.

## Attempt 13 reconciliation

The 2026-11-19 host build completed successfully and produced a 17,704,784-byte
ARM64 MH_EXECUTE with SHA-256
`ccfec1f44b15ee428a2a405f9fcf6e3128ae7cd4ba60fabbd634e314f36cc758`. The
receipt and compile records select `DEVELOPMENT_ARM64_BCM2837`, so this is a
BCM2837 host diagnostic kernel, not a G0345D/MSM8996 kernel. A separate static
audit found no undefined symbols and recomputed the embedded source-crypto text
HMAC. That does not show runtime POST, boot, driver behavior, or iOS userspace.

## Missing XNU machine support

Neither reviewed source tree has an MSM8996 config. A complete addition
needs coordinated machine registration and flags, `config/MASTER.arm64.msm8996`,
an MSM8996 board-config branch and SoC header, and the corresponding ARM64
header export. A profile output string cannot provide these pieces or alter the
compiler's selected machine.

The generic ARM64 register layer also lacks a general cache-line fallback for
the Kryo CPUs in this target; its unmatched processor branch is a compile-time
error. CPU topology needs a generic MPIDR-affinity gate for
Aff1/Aff0 startup matching and cluster-offset construction. Reusing XNU's Apple
`HAS_CLUSTER` switch is unsafe because that switch also enables Apple cluster
power-control and fast-IPI assumptions. The board DTS currently disables
CPU1-3; secondary-core/IPI qualification remains a distinct step even after a
single-core machine config compiles.

## Attempt 27 qualification boundary

A later isolated attempt applied an MSM8996 machine patch to XNU 8796.121.2 and
completed a native-only kernel build. It skipped prelink and did not include the
20F66 KernelCache kext closure. The temporary image showed the UniXNU loader
menu, then returned to Android; successful ExitBootServices and XNU entry were
not confirmed. The attempt 27 patch stack is not integrated into this
8796.101.5 proposal. This result shows that a patched 8796.121.2 diagnostic can
compile; it does not qualify the selected baseline, a bootable target kernel,
or a complete iOS system.

## Build-pipeline requirements

The isolated tools checkout still hard-codes BCM2837 in the XNU build script,
object/stamp paths, bootstrap input checks and filelist, and archive builders
that replay XNU compiler records. The iOS profile's `native_kernel` is only a
staging input; it does not choose `MACHINE_CONFIGS`. Before a new target build,
one explicit machine identity must be threaded through XNU make variables,
object roots, archive recipes, bootstrap checks, artifact staging, and the
receipt. Preflight and output audits must reject BCM2837 config macros or
object paths for a requested MSM8996 build. Compile into a separate
machine-specific object root so old BCM2837 objects cannot satisfy checks.

## Exit criteria before a target build

1. Implement and review the MSM8996 machine layer, including Kryo cache-line
   handling and generic MPIDR topology without Apple power-control flags.
2. Thread the explicit machine identity through build and archive scripts, and
   add fail-fast checks for config selection, compiler flags, object roots, and
   final artifact identity.
3. Keep the first XNU build in a new MSM8996 object tree; preserve attempt 13
   unchanged as BCM2837 diagnostic evidence.
4. Separately resolve the selected 8796.101.5 proposal's source/profile/patch
   compatibility before treating a 8796.121.2 diagnostic experiment as target
   provenance.

No new target build or device operation was started during this audit.
