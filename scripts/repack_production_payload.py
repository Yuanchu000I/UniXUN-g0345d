#!/usr/bin/env python3
"""Validate a production UniXNU FAT and replace only M34's ramdisk bytes.

This does not invoke adb/fastboot or modify a device. Run with --check-only
to inspect inputs without creating an image. Python 3.11+ is required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import tomllib
import zlib
from pathlib import Path

PAGE = 4096
KERNEL_SIZE = 54_773_873
RAMDISK_SIZE = 25_165_824
RAMDISK_OFFSET = 0x343E000
IMAGE_SIZE = 79_945_728
GZIP_SIZE = 8_565_237
DTB_SIZE = 46_208_636
TEMPLATE_SHA256 = "56a2c1dca6900c3d4fdfef504608836f5fb3661160f26db1174f69d141317315"
CONFIG_PATH = "/EFI/UniXNU/unixnu.toml"
KERNEL_PATH = "/EFI/UniXNU/Payloads/kernel.macho"
ADT_PATH = KERNEL_PATH + ".adt"
KERNEL_ARGS = "-v serial=3 console=ttyHSL0,115200,n8"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(blob: bytes | bytearray) -> str:
    return hashlib.sha256(blob).hexdigest()


def boot_id(image: bytes | bytearray) -> bytes:
    digest = hashlib.sha1()
    for blob in (image[PAGE:PAGE + KERNEL_SIZE], image[RAMDISK_OFFSET:]):
        digest.update(struct.pack("<I", len(blob)))
        digest.update(blob)
    return digest.digest() + b"\0" * 12


def adt_properties(blob: bytes) -> dict[str, dict[str, bytes]]:
    """Read Apple flattened device-tree properties, preserving every value."""
    nodes = {}

    def node(offset: int, parent: str, depth: int) -> int:
        require(depth < 32 and offset + 8 <= len(blob), "invalid ADT node")
        properties, children = struct.unpack_from("<II", blob, offset)
        require(properties < 1024 and children < 1024, "invalid ADT node counts")
        offset += 8
        values = {}
        for _ in range(properties):
            require(offset + 36 <= len(blob), "truncated ADT property")
            key = blob[offset:offset + 32].split(b"\0", 1)[0].decode("ascii")
            size = struct.unpack_from("<I", blob, offset + 32)[0]
            offset += 36
            require(key not in values and size < len(blob) and offset + size <= len(blob),
                    "invalid ADT property")
            values[key] = blob[offset:offset + size]
            offset += (size + 3) & ~3
        name = values.get("name", b"").split(b"\0", 1)[0].decode("ascii")
        require("/" not in name, "invalid ADT node name")
        path = parent + "/" + name if name else parent
        require(path not in nodes, "duplicate ADT node path")
        nodes[path] = values
        for _ in range(children):
            offset = node(offset, path, depth + 1)
        return offset

    require(node(0, "", 0) == len(blob), "unparsed ADT tail")
    return nodes


def compare_adt(reference: bytes, candidate: bytes) -> bool:
    """Only the production builder's /chosen/random-seed may change."""
    old = adt_properties(reference)
    new = adt_properties(candidate)
    require(old.keys() == new.keys(), "ADT node paths differ from M34")
    seed_changed = False
    for path, properties in old.items():
        require(properties.keys() == new[path].keys(), f"ADT properties differ: {path}")
        for key, value in properties.items():
            other = new[path][key]
            if path.endswith("/chosen") and key == "random-seed":
                require(len(value) == len(other) == 256, "unexpected ADT random-seed length")
                seed_changed = value != other
            else:
                require(value == other, f"ADT property differs from M34: {path}/{key}")
    return seed_changed


class Fat16:
    """Independent, read-only FAT16 BPB/FAT/LFN/directory reader."""

    def __init__(self, image: bytes):
        self.image = image
        require(len(image) == RAMDISK_SIZE, "payload must be exactly 24 MiB")
        require(image[510:512] == b"\x55\xaa", "missing FAT boot signature")
        self.sector = struct.unpack_from("<H", image, 11)[0]
        self.spc = image[13]
        self.reserved = struct.unpack_from("<H", image, 14)[0]
        copies = image[16]
        root_count = struct.unpack_from("<H", image, 17)[0]
        total = struct.unpack_from("<H", image, 19)[0] or struct.unpack_from("<I", image, 32)[0]
        fat_sectors = struct.unpack_from("<H", image, 22)[0]
        require(self.sector == 512 and self.spc > 0 and not (self.spc & (self.spc - 1)),
                "unexpected FAT sector/cluster geometry")
        require(self.reserved > 0 and copies == 2 and root_count > 0 and fat_sectors > 0,
                "unexpected FAT16 BPB")
        require(total * self.sector == len(image), "FAT volume length mismatch")
        self.cluster_bytes = self.sector * self.spc
        fat_start = self.reserved * self.sector
        fat_bytes = fat_sectors * self.sector
        self.fat = image[fat_start:fat_start + fat_bytes]
        require(self.fat == image[fat_start + fat_bytes:fat_start + fat_bytes * 2],
                "FAT copies differ")
        self.root_offset = fat_start + copies * fat_bytes
        root_sectors = (root_count * 32 + self.sector - 1) // self.sector
        self.root_bytes = root_count * 32
        self.data_offset = self.root_offset + root_sectors * self.sector
        self.cluster_count = (len(image) - self.data_offset) // self.cluster_bytes
        require(4085 <= self.cluster_count < 65525, "payload is not FAT16")
        require(len(self.fat) >= 2 * (self.cluster_count + 2), "undersized FAT")
        require(self.fat[:4] == b"\xf8\xff\xff\xff", "unexpected FAT reserved entries")
        self.files: dict[str, bytes] = {}
        self.visited_directories: set[int] = set()
        self.owners: dict[int, str] = {}
        self.walk(image[self.root_offset:self.root_offset + self.root_bytes], "", 0)

    def chain(self, first: int, owner: str) -> bytes:
        chunks = []
        seen = set()
        cluster = first
        while True:
            require(2 <= cluster < self.cluster_count + 2 and cluster not in seen,
                    f"invalid or cyclic FAT chain: {owner}")
            require(cluster not in self.owners, f"cross-linked FAT chain: {owner}")
            seen.add(cluster)
            self.owners[cluster] = owner
            offset = self.data_offset + (cluster - 2) * self.cluster_bytes
            chunks.append(self.image[offset:offset + self.cluster_bytes])
            cluster = struct.unpack_from("<H", self.fat, cluster * 2)[0]
            if cluster >= 0xFFF8:
                return b"".join(chunks)

    @staticmethod
    def checksum(short: bytes) -> int:
        value = 0
        for char in short:
            value = (((value & 1) << 7) + (value >> 1) + char) & 0xFF
        return value

    def entries(self, blob: bytes):
        pending = []
        for offset in range(0, len(blob), 32):
            entry = blob[offset:offset + 32]
            require(len(entry) == 32, "truncated directory entry")
            if entry[0] == 0:
                require(not pending, "unterminated LFN")
                return
            if entry[0] == 0xE5:
                pending = []
                continue
            if entry[11] == 0x0F:
                pending.append(entry)
                continue
            name = entry[:8].decode("ascii").rstrip()
            extension = entry[8:11].decode("ascii").rstrip()
            name += "." + extension if extension else ""
            if pending:
                count = len(pending)
                require(pending[0][0] == 0x40 | count, "invalid LFN sequence start")
                for index, part in enumerate(pending):
                    expected = count - index | (0x40 if index == 0 else 0)
                    require(part[0] == expected and part[13] == self.checksum(entry[:11])
                            and part[12] == 0 and part[26:28] == b"\0\0", "invalid LFN metadata")
                chars = b"".join(p[1:11] + p[14:26] + p[28:32] for p in reversed(pending))
                name = chars.decode("utf-16-le").split("\0", 1)[0].rstrip("\uffff")
                pending = []
            if name in (".", "..") or entry[11] & 0x08:
                continue
            require(name and "/" not in name and "\\" not in name, "invalid FAT name")
            require(entry[20:22] == b"\0\0", "unexpected FAT16 high cluster")
            yield name, entry[11], struct.unpack_from("<H", entry, 26)[0], struct.unpack_from("<I", entry, 28)[0]
        require(not pending, "unterminated LFN at directory end")

    def walk(self, blob: bytes, prefix: str, depth: int) -> None:
        require(depth < 32, "excessive FAT directory nesting")
        names = set()
        for name, attributes, cluster, size in self.entries(blob):
            require(name.casefold() not in names, f"duplicate FAT entry under {prefix}")
            names.add(name.casefold())
            path = prefix + "/" + name
            if attributes & 0x10:
                require(cluster not in self.visited_directories, "cyclic FAT directory")
                self.visited_directories.add(cluster)
                self.walk(self.chain(cluster, path), path, depth + 1)
            else:
                content = self.chain(cluster, path) if cluster else b""
                require(size <= len(content) and (not content or size > len(content) - self.cluster_bytes),
                        f"file size does not match FAT chain: {path}")
                self.files[path.casefold()] = content[:size]

    def read(self, path: str) -> bytes:
        require(path.casefold() in self.files, f"missing production file: {path}")
        return self.files[path.casefold()]


def validate_boot(image: bytes) -> None:
    require(len(image) == IMAGE_SIZE and image[:8] == b"ANDROID!", "unexpected boot image format/size")
    fields = struct.unpack_from("<10I", image, 8)
    require(fields[0] == KERNEL_SIZE and fields[2] == RAMDISK_SIZE and fields[7] == PAGE,
            "unexpected kernel/ramdisk/page size")
    require(fields[4] == 0 and fields[8] == 0, "unexpected second stage/header version")
    require(PAGE + ((KERNEL_SIZE + PAGE - 1) // PAGE) * PAGE == RAMDISK_OFFSET,
            "unexpected ramdisk offset")
    require(image[576:608] == boot_id(image), "boot id SHA1 mismatch")
    kernel = image[PAGE:PAGE + KERNEL_SIZE]
    stream = zlib.decompressobj(16 + zlib.MAX_WBITS)
    stream.decompress(kernel)
    require(stream.eof, "truncated kernel gzip")
    require(len(kernel) - len(stream.unused_data) == GZIP_SIZE and len(stream.unused_data) == DTB_SIZE,
            "gzip/DTB lengths changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--expected-adt-sha256", required=True,
                        help="expected ADT hash from production payload.json; seed changes on rebuild")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if not args.check_only and args.output is None:
        parser.error("--output is required unless --check-only is used")
    template = args.template.read_bytes()
    require(sha256(template) == TEMPLATE_SHA256, "template is not the known M34 image")
    validate_boot(template)
    payload = args.payload.read_bytes()
    native_kernel = args.kernel.read_bytes()
    fat = Fat16(payload)
    template_fat = Fat16(template[RAMDISK_OFFSET:])
    config = fat.read(CONFIG_PATH)
    kernel = fat.read(KERNEL_PATH)
    adt = fat.read(ADT_PATH)
    require(config == template_fat.read(CONFIG_PATH), "production config differs from M34")
    seed_changed = compare_adt(template_fat.read(ADT_PATH), adt)
    parsed = tomllib.loads(config.decode("utf-8"))
    require(parsed.get("version") == 1 and parsed.get("boot", {}).get("default") == "xnu",
            "config does not default to xnu")
    entries = [entry for entry in parsed.get("entry", []) if entry.get("id") == "xnu"]
    require(len(entries) == 1 and entries[0].get("type") == "xnu"
            and entries[0].get("path") == "Payloads/kernel.macho"
            and entries[0].get("args") == KERNEL_ARGS, "unexpected xnu config")
    require(kernel == native_kernel, "FAT kernel differs from --kernel")
    require(len(adt) == 12_984 and sha256(adt) == args.expected_adt_sha256, "incorrect production ADT")
    output = bytearray(template[:RAMDISK_OFFSET] + payload)
    output[576:608] = boot_id(output)
    validate_boot(output)
    require(output[PAGE:RAMDISK_OFFSET] == template[PAGE:RAMDISK_OFFSET], "kernel/container bytes changed")
    require(output[:576] == template[:576] and output[608:PAGE] == template[608:PAGE],
            "header changed outside boot id")
    require(output[RAMDISK_OFFSET:] == payload, "ramdisk differs from production FAT")
    manifest = {
        "validation": "passed", "template": str(args.template.resolve()),
        "template_sha256": TEMPLATE_SHA256, "payload": str(args.payload.resolve()),
        "payload_sha256": sha256(payload), "native_kernel": str(args.kernel.resolve()),
        "native_kernel_bytes": len(kernel), "native_kernel_sha256": sha256(kernel),
        "config_sha256": sha256(config), "adt_bytes": len(adt), "adt_sha256": sha256(adt),
        "config_equal_m34": True, "adt_equal_m34_except_random_seed": True,
        "adt_random_seed_changed": seed_changed, "kernel_container_equal_m34": True,
        "page_bytes": PAGE, "kernel_size": KERNEL_SIZE, "ramdisk_size": RAMDISK_SIZE,
        "ramdisk_offset": RAMDISK_OFFSET, "gzip_bytes": GZIP_SIZE, "dtb_bytes": DTB_SIZE,
        "image_bytes": len(output), "image_sha256": sha256(output),
        "boot_id_sha1": bytes(output[576:596]).hex(),
        "fat_files": {path: {"bytes": len(data), "sha256": sha256(data)}
                      for path, data in sorted(fat.files.items())},
    }
    if args.check_only:
        manifest["mode"] = "check_only_no_files_written"
    else:
        require(args.output.resolve() not in {args.template.resolve(), args.payload.resolve(), args.kernel.resolve()},
                "output would overwrite an input")
        require(not args.output.exists(), "output already exists")
        manifest_path = args.manifest or args.output.with_suffix(args.output.suffix + ".json")
        require(not manifest_path.exists() and manifest_path.resolve() not in
                {args.output.resolve(), args.template.resolve(), args.payload.resolve(), args.kernel.resolve()},
                "manifest would overwrite an existing file or input")
        args.output.write_bytes(output)
        require(args.output.read_bytes() == output, "output readback mismatch")
        manifest["output"] = str(args.output.resolve())
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
