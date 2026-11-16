M36 v179 hardware observation, 2026-11-16

Input: `48e98f7803c98ae4282b968d4124ba7e.jpg`.
Two independent source/photo reviews identify the same five white bands:

| Framebuffer rows | Meaning |
| --- | --- |
| 0-23, 40-63, 80-103 | Three existing painters, all using the explicit framebuffer slot |
| 300-315 | Full framebuffer black fill returned, inside arm_vm_init |
| 400-415 | arm_vm_init returned to arm_init |

The photo supports successful execution past the alternate TTBR setup,
the invalid TTBR0 switch, TLB flush, black fill and remaining arm_vm_init
body. It does not establish completion of later console initialization
or entry into userland. The top three bands no longer compare classic
address math and phystokv; those old source comments were inaccurate.

A later read-only ADB observation found Android Linux 3.18.31 with
sys.boot_completed=1. This is not XNU ADB. The reason for the Android
return is unknown; do not assert an automatic watchdog reset without
further evidence. Neither /sys/fs/pstore nor /proc/last_kmsg exists in
this Android environment.
