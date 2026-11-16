# Source and evidence provenance

The source started from the midopix G0245D device repository at
`24508221a8ce11129257f4f6d1225d220f3ffefa`, then accumulated G0345D local changes
through M42/v185. The device worktree was dirty; the base commit does not claim
to identify the complete tested state. This repository is an independent curated
snapshot with no remote inherited from the G0245D worktree.

`source-snapshot.json` contains SHA256 hashes of the exact exported defconfig,
DTS, feeds, lock and 51 active XNU patches. Their bytes were preserved. The active
series was rewritten only to drop old comments while preserving ordered names.
Git whitespace diagnostics are disabled for .patch text because unified-diff
context records contain structural spaces; original patch bytes are hash-checked
and all 54 exported patch files passed Git parser validation.
`board.toml` retains runtime values; publication comments and the official
`[package]` mapping were added separately. Nine inactive historical patches were
not included. Historical `g0245d_*` filenames and symbols are intentional.

The unchanged official record checker and packaging script, and the two catalog
snapshots under `ci/`, have full source commits and hashes in source-pins.toml.
The compatibility checker copies the official script to a temporary directory
and pairs it with the fork catalog explicitly. It does not edit upstream source
or suppress unknown-component validation. The stock upstream catalog gap is
reported separately.

`docs/evidence/` and `docs/bringup/` are selected historical artifacts. Paths,
serial and seed were redacted; JSON absolute input paths became basenames.
Logs/disassembly record the old environment, not a run of the curated repository.
Original photographs and binaries are withheld; hashes remain for correlation.
Photo-analysis JSON alone cannot reproduce a visual decode without the original.
The source-only evidence entries in porting.toml do not assert a new device test
or assign an invented full commit to the historical dirty worktree.

The root license and original notices were retained. XNU patches apply to Apple
source under its respective license (including APSL-covered files); EDK2 and
other upstream components retain their own licenses. Assembly excerpts are
selected diagnostic output, not full source or binary distributions. See NOTICE.
