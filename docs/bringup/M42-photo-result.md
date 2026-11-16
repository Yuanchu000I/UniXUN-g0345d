# M42 photo result, 2026-11-16

Photo: `0f52ddf6cc0c6f1020db8b77c61112b7.jpg`, 1080 x 1920 pixels.
Photo SHA256: `2cf69ba5a8046faa2f72f5b41e69f53cb3b6baf59fbc7b0ed0c8c0aebb380c48`.

The row280 version band identifies M42. Calibration row240 is0xAAAA.
The following cells decode consistently, MSB first:

|Framebuffer row|Bits|Hex|
|---|---|---|
|240|1010101010101010|AAAA|
|320|0000001101101110|036E|
|480|1111111111111111|FFFF|
|560|1111111111110000|FFF0|
|640|0000011110011101|079D|
|720|0110111110010100|6F94|
|800|0100000100000111|4107|
|840|0000010001100111|0467|
|880|0000000000000000|0000|
|960|0000000000000000|0000|
|1040|0000000000000000|0000|
|1120|0000000000000000|0000|

The sorted startup-table index is878 (0x036E), ZALLOC index6, the seventh
callback. Function0xfffffff0079d6f94 and argumentNULL match `_kalloc_init`
in the final M42 startup mapping. Do not reuse the M41 function address.

**Current phase0x4107; value0x0467=1127 (`kt_count`).** Phase white cells
are1/7/13/14/15 and value white cells5/9/10/13/14/15. The count matches the
independent on-disk nondata/nonVM fixed-view count. It is not the raw1274
fixed-record count, which includes filtered data/VM types.

Bands1240/1280/1320/1360/1400 are present. Bands1440/1480/1520/1560 are
absent. Callback states1600/1660/1720 are present;1780 and1880 onward are
absent. The fixed-view function and the kalloc_init callback have no
completion marker.

Applied `osfmk/kern/kalloc.c` lines1890-1892 call the fixed iterators and
then write0x4107. Line1897 calls `kalloc_type_create_zones_fixed()`;
line1898 writes0x4108 after its return. The v185 object disassembly shows
the same order at offsets0x2668,0x2678 and0x2680 respectively. These are
object offsets, not the device's runtime fault PC.

Thus fixed parsing, both count/capacity assertions, the first fixed-view
qsort and `kalloc_type_create_iterators_fixed()` have returned. The next
narrowed interval is the fixed-zone creation call and its adjacent probe
boundaries, after0x4107 and before0x4108. The photo does not identify an
internal size class, prove that the first zone_create was reached, identify
an assertion/faulting instruction, or distinguish a hang from slow progress.
The last probe's tail and the call/return boundaries remain in the interval.

When work is explicitly resumed, the next diagnostic boundaries to consider
are policy entry/return (including its separate small qsort), size-class
index, create_zone_for_size entry/return, shuffle/signature equivalence and
type distribution. Preserve allocator behavior; do not skip initialization.

Reproduction: `analyze_M42_photo.py` uses PIL/numpy white-threshold median
sampling, full-width-band projective fits at x300/500/700, and cells calibrated
from rows480/560. Maximum per-column fit errors are2.54/2.19/2.37px.
Full samples: `M42-photo-analysis.json`; independent analysis:
`M42-photo-independent.md`. Both decoders agree on all displayed words.

The M42 build and temporary boot were completed before this photo. The
boot log records SendingOKAY2.002s, BootingOKAY0.115s, total2.163s.
This only confirms delivery and boot handoff; it is not full XNU startup.

The user explicitly requested analysis, handoff update, then stop. This
photo-analysis pass did not build, create a new image, reboot, boot or flash
the device. No allocator source, patch series, FD, boot-header kernel_size
or container layout was changed. Further build/device work awaits a later
explicit resume instruction.
