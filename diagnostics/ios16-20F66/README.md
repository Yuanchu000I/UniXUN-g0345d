# iOS 16.5 / 20F66 diagnostic source export

This is the actual native-only XNU 8796.121.2 MSM8996 diagnostic source stack from 2026-11-21. It is separate from the root board/profile XNU 8796.101.5 proposal; this export does not enable that proposal or qualify iOS boot. iPadOS 17 is abandoned as the current target. Inherited patch names remain unchanged for byte identity.

patches/xnu/series is the exact ordered 46-patch v9 stack; manifest.json pins exported bytes. v10 reused the v9 kernel and changed nine ADT u64 fields, preserving seven translated physical register ranges. config/ is a diagnostic snapshot, not the active root proposal. resolved.config.in substitutes TOOLS_ROOT, DEVICE_ROOT and REFERENCE_ROOT placeholders for local roots; its original hash is in evidence-summary.json. Copied board comments and catalog metadata are historical bytes, not present qualification claims.

tooling/ contains five v9-receipt tool files; four are exact and prepare-xnu.py has one historical developer LLVM checkout path replaced with {LLVM_PROJECT_ROOT}. source-pins.json retains all five original hashes. patches/tools/ retains device tool deltas. components/ contains platform, CPU and probe source snapshots. source-pins.json maps dependencies, observed local revisions, catalog pins and inferred public project locators. Additional dirty tool/dependency deltas, compiler availability, lawful private inputs, firmware closure and clean-checkout reproduction remain to be reviewed. Prelink was skipped; no 20F66 donor kexts were added. No source rebuild was performed for this export.

Run with Python 3 from this directory (or use the script's full path):

    python3 check_export.py
    python3 audit_native_kernel.py PRIVATE_KERNEL
    python3 check_export.py --adt-pair PRIVATE_BEFORE_ADT PRIVATE_AFTER_ADT
    python3 adapt_adt_window.py PRIVATE_INPUT_ADT PRIVATE_NEW_OUTPUT

The portable adapter checks the old bus window, register inventory and CPU timebase. It changes only nine existing u64 fields, creates the explicit output exclusively and verifies readback. Parent base 0x60000 and span 0x09fa0000 are 64 KiB aligned; top 0x0a000000 stays fixed. Child offsets subtract 0x60000; sizes and translated physical addresses remain fixed. This host-audited mapping hypothesis does not establish corrected runtime clocks.

The independent checker verifies export bytes, ordered patch inventory and nine-field/seven-range semantics using an in-memory synthetic ADT plus rejection controls. It audits private before/after inputs without printing properties. The kernel audit validates the known digest and Mach-O headers, without repeating every original instruction check. No private or binary fixture tree is included.

evidence-summary.json separates v9 photo-supported observations from v10 host-only work. Under the audited-v9 association, white WFE entry and the red classifier slot support ticks_per_sec=0, ticks_per_event=0 and bit_index=0xffffffff. Visual identity lacks an independent transfer digest. Later WFE return, full platform expert, BSD and iOS startup remain unverified. v10 had not been device-tested when exported. Private receipt hashes are anchors, not publicly inspectable receipt copies. Original photographs and private ADT are excluded.

Preserve licenses and notices. This source export performs no device operation or image packaging. Firmware/container closure and integration with the root proposal remain outside its established scope.
