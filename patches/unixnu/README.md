# Tools patches

These are not members of `patches/xnu/series`.

- `0002-portrait-menu-shows-all-entries.patch` and
  `0003-linux-host-without-root.patch` are inherited device-source material.
  They predate the pinned tools fork and may already be present there. They are
  retained for provenance, not automatically reapplied.
- `9001-local-network-retries-and-header-cache.patch` is the exact uncommitted
  diff of `scripts/prepare-xnu-source.py` and `scripts/linux/setup-toolchain.py`
  against tools commit `1e0d72a34b952eacdec1f90941c617bf45860b76`.
  It was part of the historical local environment. It is optional for a new host;
  the clean baseline alone does not include it.

Inspect each patch and use `git apply --check` in the intended tools checkout
before deciding whether it is needed. This export did not apply tools patches,
fetch dependencies or build anything. Patch target licenses remain applicable.
