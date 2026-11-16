# Script interfaces

`package.sh` is byte-for-byte the official template pinned in source-pins.toml.
It invokes `unixnu release`; current legacy firmware is not ready for this path.

`check-repository.py` validates metadata, exact exported functional inputs,
patch order, official-template hashes, component coverage, sanitized file scope
and syntax. It performs no kernel/firmware compilation or device operation.
It uses the official record checker with the documented fork catalog.
`--base REV` additionally checks committed changed paths and record updates.

`extract_startup_table.py --help` describes the read-only Mach-O startup-table
analysis tool. Use the exact kernel whose hash matches the evidence; addresses
and equal-key sort order vary between builds.

`repack_production_payload.py` preserves the fixed M34 template and accepts
explicit external inputs. Unlike the historical copy, the public interface
requires both `--template` and `--expected-adt-sha256`, because neither a private
input path nor a stale M34 ADT hash should be assumed. For read-only checking:

```sh
python3 scripts/repack_production_payload.py \
  --template private/M34-v177split.img \
  --payload private/payload.img --kernel private/kernel.macho \
  --expected-adt-sha256 ADT_HASH_FROM_MATCHING_PAYLOAD_MANIFEST --check-only
```

This command needs withheld matching inputs; it was not executed in this export.
Without `--check-only`, an explicit new `--output` is required; the tool refuses
to overwrite inputs or existing outputs. It writes no device, but generating a
new image still requires the user to resume experiments. M42's historical ADT
hash is recorded in its manifest, not hardcoded as a default for future payloads.
The repacker is separate from the official release interface and cannot produce
the missing firmware or make a clean M42 reproduction possible by itself.
