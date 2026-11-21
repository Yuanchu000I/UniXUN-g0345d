# G0345D device repository

Read README.md, porting.toml, docs/status.md, docs/firmware-dependency.md and
source-pins.toml before changing this port. Follow the official device, records,
packaging and UEFI guides linked from README.md.

- Target: GREE G0345D / msm8996 / iPhone iOS 16.5-20F66, experimental.
- Current diagnostics: diagnostics/ios16-20F66, 46 ordered patches against XNU
  8796.121.2. Root XNU 8796.101.5 is a separate proposal; board patch_series
  and root patches/xnu/series must remain empty.
- iPadOS 17 work is abandoned. Its 51 retired root patches and M42/M71 evidence
  belong to historical commit 53ce24cd0e727914f4e25f32b44815cd00885774.
  Keep the historical source-snapshot hash manifest unchanged.
- Current evidence reaches Stage 5 after early PE return, within WFE/clock
  initialization. v10 passed host checks and awaits temporary device testing.
  Do not claim a trap PC, confirmed zero-clock cause, full Stage 5 or iOS boot.
- Source publication does not authorize builds, image generation, device reboot
  or tests. Future authorized tests use fastboot boot only; never flash.
- Preserve FD base 0x91700000 and size 0x600000, kernel_size 54773873 and fixed
  container layout. Preserve initialization, the WFE algorithm and UBSAN.
- Preserve exact diagnostic patch order and inherited names/symbols. Do not
  apply this stack through the unrelated root profile or apply a patch twice.
- Record changed code paths and findings/evidence in porting.toml. Never label
  linked scaffolds as functional drivers or claim a complete iOS boot.
- scripts/package.sh is the unchanged official template. Legacy firmware work
  belongs in a companion repository; clean end-to-end reproduction is pending.
- Never publish proprietary images, binaries, raw ADT, device seeds, serials,
  private keys, original photographs, local absolute paths, caches or outputs.
  Publish sanitized derived summaries rather than copying private reports.
- Run python3 scripts/check-repository.py and git diff --check after edits;
  use --base with a real committed base for changed-area validation.
- Do not reset/clean original worktrees or invent hardware-tested commits.
  Historical logs predate this curated repository revision.
