#!/usr/bin/env python3
"""Map the runtime-sorted XNU STARTUP table from its exact Mach-O.

Uses the Bentley/McIlroy ordering in this tree's bsd/kern/qsort.c, including
equal-key swaps. Python's stable sorted() is deliberately not used for entries.
"""
import argparse
import bisect
import hashlib
import json
from pathlib import Path
import struct


def qsort_entries(entries):
    """Element-index translation of bsd/kern/qsort.c (24-byte records)."""
    a = list(entries)

    def cmp(i, j):
        ki = a[i]['subsystem'], a[i]['rank']
        kj = a[j]['subsystem'], a[j]['rank']
        return (ki > kj) - (ki < kj)

    def swap(i, j):
        a[i], a[j] = a[j], a[i]

    def vecswap(i, j, n):
        for k in range(n):
            swap(i + k, j + k)

    def med3(i, j, k):
        if cmp(i, j) < 0:
            return j if cmp(j, k) < 0 else (k if cmp(i, k) < 0 else i)
        return j if cmp(j, k) > 0 else (i if cmp(i, k) < 0 else k)

    def sort(base, n):
        while True:
            swap_cnt = 0
            if n < 7:
                for pm in range(base + 1, base + n):
                    pl = pm
                    while pl > base and cmp(pl - 1, pl) > 0:
                        swap(pl, pl - 1)
                        pl -= 1
                return
            pm = base + n // 2
            if n > 7:
                pl, pn = base, base + n - 1
                if n > 40:
                    d = n // 8
                    pl = med3(pl, pl + d, pl + 2 * d)
                    pm = med3(pm - d, pm, pm + d)
                    pn = med3(pn - 2 * d, pn - d, pn)
                pm = med3(pl, pm, pn)
            swap(base, pm)
            pa = pb = base + 1
            pc = pd = base + n - 1
            while True:
                while pb <= pc:
                    r = cmp(pb, base)
                    if r > 0:
                        break
                    if r == 0:
                        swap_cnt = 1
                        swap(pa, pb)
                        pa += 1
                    pb += 1
                while pb <= pc:
                    r = cmp(pc, base)
                    if r < 0:
                        break
                    if r == 0:
                        swap_cnt = 1
                        swap(pc, pd)
                        pd -= 1
                    pc -= 1
                if pb > pc:
                    break
                swap(pb, pc)
                swap_cnt = 1
                pb += 1
                pc -= 1
            if swap_cnt == 0:
                for pm in range(base + 1, base + n):
                    pl = pm
                    while pl > base and cmp(pl - 1, pl) > 0:
                        swap(pl, pl - 1)
                        pl -= 1
                return
            pn = base + n
            r = min(pa - base, pb - pa)
            if r > 0:
                vecswap(base, pb - r, r)
            r = min(pd - pc, pn - pd - 1)
            if r > 0:
                vecswap(pb, pn - r, r)
            r = pb - pa
            if r > 1:
                sort(base, r)
            r = pd - pc
            if r > 1:
                base, n = pn - r, r
            else:
                return

    sort(0, len(a))
    assert all((a[i]['subsystem'], a[i]['rank']) <=
               (a[i + 1]['subsystem'], a[i + 1]['rank'])
               for i in range(len(a) - 1))
    return a


def parse_macho(data):
    magic, _, _, _, ncmds, _, _, _ = struct.unpack_from('<8I', data)
    if magic != 0xfeedfacf:
        raise ValueError('Expected a little-endian 64-bit Mach-O')
    cursor = 32
    sections = []
    symtab = None
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from('<II', data, cursor)
        if cmdsize < 8 or cursor + cmdsize > len(data):
            raise ValueError('Invalid load command bounds')
        if cmd == 0x19:  # LC_SEGMENT_64
            nsects = struct.unpack_from('<I', data, cursor + 64)[0]
            for i in range(nsects):
                sec = cursor + 72 + i * 80
                name, segment, addr, size, offset = struct.unpack_from('<16s16sQQI', data, sec)
                sections.append({'name': name.rstrip(b'\0').decode(),
                                 'segment': segment.rstrip(b'\0').decode(),
                                 'address': addr, 'size': size, 'offset': offset})
        elif cmd == 2:  # LC_SYMTAB
            symtab = struct.unpack_from('<4I', data, cursor + 8)
        cursor += cmdsize
    if symtab is None:
        raise ValueError('LC_SYMTAB is required for symbol labels')
    symoff, nsyms, stroff, strsize = symtab
    strings = data[stroff:stroff + strsize]
    symbols = []
    for i in range(nsyms):
        strx, typ, sect, _, value = struct.unpack_from('<IBBHQ', data, symoff + 16 * i)
        if typ & 0xe0 or not strx or not value:  # STAB/debug, empty, undefined
            continue
        end = strings.find(b'\0', strx)
        if end < 0:
            raise ValueError('Unterminated symbol')
        name = strings[strx:end].decode('utf-8', errors='replace')
        symbols.append((value, name, typ, sect))
    symbols.sort(key=lambda x: (x[0], x[1]))
    return sections, symbols


def extract(path):
    data = path.read_bytes()
    sections, symbols = parse_macho(data)
    target = [s for s in sections if s['name'] == '__init_entry_set']
    if len(target) != 1:
        raise ValueError(f'Expected one startup section, got {len(target)}')
    sec = target[0]
    if sec['size'] % 24 or sec['offset'] + sec['size'] > len(data):
        raise ValueError('Invalid startup section layout')
    addresses = [x[0] for x in symbols]

    def describe(address):
        if address == 0:
            return 'NULL'
        i = bisect.bisect_right(addresses, address) - 1
        if i < 0:
            return '?'
        base, name, _, _ = symbols[i]
        return name if address == base else f'{name}+0x{address - base:x}'

    entries = []
    for i in range(sec['size'] // 24):
        sub, rank, func, arg = struct.unpack_from('<IIQQ', data, sec['offset'] + 24 * i)
        entries.append({'original_index': i, 'subsystem': sub, 'rank': rank,
                        'func': f'0x{func:016x}', 'arg': f'0x{arg:016x}',
                        'func_symbol': describe(func), 'arg_symbol': describe(arg)})
    ordered = qsort_entries(entries)
    zalloc_index = 0
    for i, entry in enumerate(ordered):
        entry['sorted_index'] = i
        if entry['subsystem'] == 7:
            entry['zalloc_index'] = zalloc_index
            zalloc_index += 1
    return {'kernel': str(path.resolve()), 'kernel_sha256': hashlib.sha256(data).hexdigest(),
            'section': sec, 'entry_size': 24, 'entry_count': len(ordered),
            'sort': 'bsd/kern/qsort.c Bentley/McIlroy exact equal-key swap order',
            'index_base': 0, 'zalloc_count': zalloc_index, 'entries': ordered}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kernel', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--tsv', type=Path)
    args = parser.parse_args()
    result = extract(args.kernel)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    if args.tsv:
        fields = ['sorted_index', 'zalloc_index', 'original_index', 'subsystem', 'rank',
                  'func', 'arg', 'func_symbol', 'arg_symbol']
        lines = ['\t'.join(fields)]
        lines += ['\t'.join(str(e.get(k, '')) for k in fields) for e in result['entries']]
        args.tsv.write_text('\n'.join(lines) + '\n')
    print(f"kernel SHA256 {result['kernel_sha256']}")
    print(f"entries={result['entry_count']} ZALLOC={result['zalloc_count']}; indices are 0-based")
    for entry in [e for e in result['entries'] if e['subsystem'] == 7][:12]:
        print(f"sorted={entry['sorted_index']} zalloc={entry['zalloc_index']} "
              f"rank=0x{entry['rank']:08x} {entry['func_symbol']} "
              f"({entry['arg_symbol']})")


if __name__ == '__main__':
    main()
