# Publication scope and present limits

This iOS 16.5 update is an experimental **source prerelease** for G0345D. It
publishes the 46-patch XNU 8796.121.2 diagnostic export and sanitized derived
evidence, not binaries or an installable system. Current execution remains
Stage 5 after early PE return in WFE/clock initialization; v10 passed host
checks and awaits temporary device testing.

| Requirement | State in this export |
| --- | --- |
| Board/record | Format 2 / format 1, G0345D/MSM8996/ios-16.5-20F66 |
| Diagnostic sources | Exact 46-patch series, pins, checks and summaries in diagnostics/ios16-20F66 |
| Root profile | Separate XNU 8796.101.5 proposal; empty board/profile lists; did not build v9/v10 |
| iPadOS 17 | Abandoned; 51 root patches retired after hash checks; history retained |
| Host checks | Source/export integrity, record-schema check with pinned fork catalog and publication hygiene |
| Hardware | Stage 5 incomplete; v10 untested; storage/root/userland unreached |
| Standard clean release | Pending complete companion firmware delta and lawful external inputs |
| Package workflow | Prerequisite gate; no successful standard package release claimed |
| Active publication branch | device/g0345d-ios16.5; earlier main history retained |
| Website/upstream acceptance | Unverified; local validation is not catalog acceptance |

## Checker compatibility

The unmodified pinned official record checker uses the hash-checked fork
catalog. The strict upstream catalog lacks selected MSM8996 IDs; local success
is not success of its stock reusable workflow. Records include the full
selected dependency closure, including VerifiedRoot and ArmSmmu4K. Bundled
NativeUfs8996, Blsp8996, Adreno530 and Msm8996Platform are probe scaffolds.

The root checker retains the historical source-snapshot manifest, skips its
retired patch paths, verifies remaining applicable inputs, requires an empty
root series and invokes the exact diagnostic checker. The manifest's old
51-patch count is historical. Source checks neither build nor test a device.

## History and licensing

Earlier iPadOS main source remains at
[53ce24cd0e727914f4e25f32b44815cd00885774](https://github.com/Yuanchu000I/UniXUN-g0345d/tree/53ce24cd0e727914f4e25f32b44815cd00885774).
See [retirement details](ipados17-abandoned.md). Original GitHub commit
3058d69bb630776104fc78731f1d87c6db374210 and both histories remain retained.
Its original license is archived at
[github-initial-LICENSE.txt](provenance/github-initial-LICENSE.txt); see the
[license provenance note](provenance/github-initial-license.md). Existing root
and component licenses remain in effect.

## Update checks and limits

~~~sh
git status --short
python3 scripts/check-repository.py
python3 diagnostics/ios16-20F66/check_export.py
git diff --check
~~~

After committing, use scripts/check-repository.py --base with a real previous
committed revision for the official changed-area check. Ownership patterns
retain retired deletion paths. Check the exact published commit's Actions
result; a gated package job is not successful artifact production.

Complete companion firmware sources, lawful OEM/Apple input reconstruction,
20F66 kernelcache/prelink integration, ABI qualification and a clean standard
release remain outstanding. The isolated diagnostic checker retained its actual
device.soc naming failure; source publication does not rewrite old receipts.
v10 host success does not establish a hardware clock fix or complete iOS boot.

No proprietary binary/image, original photograph, raw ADT, serial/seed,
credential, local absolute path or private raw report is included. Evidence is
published as sanitized derived summaries. Publication performs no device
operation; future authorized tests use temporary fastboot boot only.
