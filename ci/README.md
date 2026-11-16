# Record validation inputs

`upstream/scripts/porting-record.py` and `upstream/components.toml` are unchanged
files from UniXNU/UniXNU at the official schema commit in source-pins.toml.
`fork/components.toml` is unchanged from the tested midopix tools commit.
Their byte hashes are checked before validation; ci/LICENSE retains the upstream
license. No full tool checkout is required for the local metadata check.

scripts/check-repository.py runs the official script from a temporary tools root
with the fork catalog. Its component validation remains strict. This explicit
compatibility mode checks all selected components and transitive dependencies;
it does not imply stock official main accepts the MSM8996 extensions. Changes
must be integrated upstream before replacing this job with the official reusable
workflow. Repository CI cannot prove kernel or firmware reproducibility.
