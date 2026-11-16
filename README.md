# UniXNU on GREE G0345D

[中文说明](README.zh.md) · [Porting record](porting.toml) · [Current status](docs/status.md)

Experimental GREE G0345D (G3), Qualcomm MSM8996, targeting
`ipados-17.7.11-21H461`. This is a curated device-source snapshot at M42/v185,
not an installable iOS distribution or an official UniXNU supported device.

The historical temporary boot reached `_kalloc_init`: phase `0x4107`, value
`1127`. Fixed-view parsing, the first sort and fixed iterator creation returned;
fixed-zone creation and its adjacent probe boundary have no observed return.
There is no complete XNU boot or userland, storage, input, GPU, network or audio
validation. Only CPU0 is enabled. Read [status](docs/status.md),
[hardware](docs/hardware.md) and [firmware dependencies](docs/firmware-dependency.md).

## Repository and prerequisites

The board uses format 2; the structured record uses format 1. Its 51 active XNU
patches retain their tested order, inherited names and `g0245d_*` symbols.
`feeds.toml` and `unixnu.lock` preserve the source pins from that worktree.
`source-pins.toml` distinguishes the tested tools fork, current official schema,
and companion firmware baselines. Exact input hashes are in
[the source snapshot](docs/provenance/source-snapshot.json).

Use Python 3.11+ and Git for repository checks. Kernel work historically used
Linux/WSL and the pinned tools fork; the official release interface targets a
supported macOS build host with its documented toolchain and Xcode prerequisites.
Apple/OEM images, firmware, device seeds and local overrides are external inputs.
No binary or original device photograph is distributed here.

## Validate the source snapshot

```sh
python3 scripts/check-repository.py
# After committing changes, also check area ownership against an existing base:
python3 scripts/check-repository.py --base origin/main
```

The checker uses the unchanged official record checker from
`21d683dff61c66f219f03ab9d8b9249026514788` with the explicitly pinned midopix fork
component catalog. Current official main lacks `NativeUfs8996`, `Blsp8996`,
`Adreno530` and `Msm8996Platform`; an upstream-only check does not pass yet.
The fork catalog marks these as `LOCAL-SCAFFOLD`, but their source is tracked
in the pinned tools fork; those markers are not missing local-only files.
A clean source-resolution and release audit is still required. See [publication requirements](docs/publication.md).

## Build entry points and their limits

Arrange sibling checkouts `UniXNU-g0345d/` and `UniXNU/`, using the tools revision
in `source-pins.toml`. The historical source-resolution commands from `UniXNU/`
are below. They are instructions for future work, not checks rerun for this export:

```sh
python3 unixnu defconfig g0345d_defconfig -D ../UniXNU-g0345d
python3 unixnu fetch -D ../UniXNU-g0345d
python3 unixnu status --json -D ../UniXNU-g0345d
python3 unixnu tree -D ../UniXNU-g0345d
```

The official `scripts/package.sh` template is copied unchanged. It delegates to
`unixnu release` using `[package]` in `board.toml`:

```sh
bash scripts/package.sh --os ipados-17.7.11-21H461 --check
# Future, after the documented firmware/release blockers are resolved:
# bash scripts/package.sh --os ipados-17.7.11-21H461 --uefi ../uefi-g0345d
```

These commands are not a currently reproducible M42 release recipe. The legacy
EDK2 firmware has unpublished local deltas, old RAW fixtures and a different
build interface; the fixed M34 container is not distributed. The manual package
workflow deliberately stops at its prerequisite gate. The strict historical
repacker is a separate laboratory tool, not a substitute for `unixnu release`.
See [its interface](scripts/README.md) and [firmware gaps](docs/firmware-dependency.md).

Future hardware validation must use `fastboot boot` only. Preserve the fixed FD,
header `kernel_size` and kernel/container layout. Hardware experiments are paused.

## Official guides

- [Device repository](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/device-repository.md)
- [Structured records](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/records.md)
- [Packaging](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/packaging.md)
- [UEFI separation](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/docs/porting/uefi-firmware.md)

The root [LICENSE](LICENSE) is retained from the device source. Patch targets and
external components retain their respective licenses; see [NOTICE](NOTICE) and
[provenance](docs/provenance/README.md).
