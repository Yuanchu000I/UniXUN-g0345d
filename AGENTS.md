# G0345D device repository

Read README.md, porting.toml, docs/status.md, docs/firmware-dependency.md and
source-pins.toml before changing this port. Follow the official device, records,
packaging and UEFI guides linked from README.md.

- Target: GREE G0345D / msm8996 / ipados-17.7.11-21H461.
- Hardware experimentation is paused. Repository organization does not authorize
  builds, image generation, device reboot or tests. Resume only on user request.
- Future authorized tests use fastboot boot only. Never flash partitions.
- Preserve FD base 0x91700000 and size 0x600000, kernel_size 54773873 and the
  fixed kernel/container layout. Do not bypass allocator initialization.
- Preserve active patch order and inherited g0245d names/symbols. Do not include
  inactive experimental patches or apply the same patch twice.
- Record changed code paths and findings/evidence in porting.toml. Do not label
  linked scaffolds as working hardware drivers or claim M42 fully boots XNU.
- scripts/package.sh is the unchanged official template; board-specific package
  settings belong in board.toml. Legacy firmware work belongs in its companion
  repository. See docs/publication.md for explicit unresolved requirements.
- Never commit proprietary images, device seeds, serials, private keys, original
  photographs, local absolute paths, caches or generated outputs.
- Run python3 scripts/check-repository.py and git diff --check after edits;
  use --base with a real committed base for changed-area validation.
- Do not reset/clean original worktrees or invent a hardware-tested commit for
  this curated snapshot. Historical logs predate this repository.
