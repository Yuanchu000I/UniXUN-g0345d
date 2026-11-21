# Retired iPadOS 17 experiment

As of 2026-11-21 the active target is iPhone iOS 16.5 / 20F66 on G0345D.
The iPadOS 17.7.11 / XNU 10063.141.1 experiment is abandoned. M42/v185 and
M71/v213 observations are historical, not evidence for iOS 16.5, physical UFS,
APFS or iOS userland.

The previous main source remains in
[commit 53ce24cd0e727914f4e25f32b44815cd00885774](https://github.com/Yuanchu000I/UniXUN-g0345d/tree/53ce24cd0e727914f4e25f32b44815cd00885774).
Its [51-patch series](https://github.com/Yuanchu000I/UniXUN-g0345d/blob/53ce24cd0e727914f4e25f32b44815cd00885774/patches/xnu/series)
remains available through Git history. Before retirement all 51 patch files
matched the SHA-256 values in the historical
[source-snapshot manifest](provenance/source-snapshot.json), and the patch
directory had no uncommitted modifications. The manifest stays unchanged as a
historical record; those patch paths are deliberately absent on the iOS branch.

Root patches/xnu/series now contains comments only. Root XNU 8796.101.5 remains
a separate proposal with an empty board patch list. Current 46-patch XNU
8796.121.2 sources live under
[diagnostics/ios16-20F66](../diagnostics/ios16-20F66/README.md).
Historical patch paths in porting.toml remain changed-area ownership patterns
for deletions; historical patch evidence uses immutable commit URLs.

Retained M42 evidence pages document their original context. They are neither
the active patch stack nor a request to resume allocator experiments. See
[current status](status.md) for the Stage 5 WFE/clock checkpoint.
