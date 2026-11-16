# M42 independent photo decode, 2026-11-16

Photo: `0f52ddf6cc0c6f1020db8b77c61112b7.jpg`, 1080 x 1920 pixels.
Analysis was read-only except for this report. No build or device operation was performed.

The six top bands at framebuffer rows0/40/80/120/160/200 and the additional
row280 band identify the M42 page. Calibration row240 is 0xAAAA.

| Framebuffer row | Bits, MSB first | Hex |
| --- | --- | --- |
|240|1010101010101010|AAAA|
|320|0000001101101110|036E|
|480|1111111111111111|FFFF|
|560|1111111111110000|FFF0|
|640|0000011110011101|079D|
|720|0110111110010100|6F94|
|800, phase|0100000100000111|4107|
|840, value|0000010001100111|0467|
|880/960/1040/1120|all zero|0000 each|

Index0x036E is878, function0xfffffff0079d6f94, argumentNULL. Entry878 in the
final M42-startup-table.json matches `_kalloc_init`, ZALLOC index6 (seventh
callback). The M41 function address must not be reused for this image.

The phase and value rows are clear, consistent whole values. The phase white
cell indices are1,7,13,14,15; the value white cell indices are5,9,10,13,14,15.
Horizontal threshold sampling at photo y726 gives phase white ranges
x278-311,527-560,781-816,824-859,868-903. At y754 the value white ranges are
x443-476,610-644,652-687,781-815,824-859,868-903. These identify0x4107 and
0x0467=1127 with high confidence. The value matches the independent M41
on-disk audit's nondata/nonVM fixed-view count1127.

The cumulative kalloc bands1240/1280/1320/1360/1400 are present. At photo
x500 their white ranges are y1020-1031,1049-1060,1077-1089,1107-1118,
1136-1148. Bands1440/1480/1520/1560 are absent. Callback states1600/1660/1720
are present at y1287-1299,1333-1346,1380-1393;1780 is absent.
Loop/later markers1880 onward are absent. A one-dimensional projective fit
at x500 has maximum error2.37px and predicts absent1440/1480/1520/1560 band
centers at photo y1172/1202/1232/1263 and1780 at1434.

Phase0x4107 follows the return of `kalloc_type_create_iterators_fixed()`.
Therefore fixed-view parsing, the two count/capacity assertions, qsort and
fixed iterator construction have returned. Phase0x4108, which follows
`kalloc_type_create_zones_fixed()`, is not observed. The fixed-view function
and current kalloc_init callback also have no completion marker.

The next narrowed interval is after fixed iterators returned and before the
fixed-zone completion phase: the call/return interval of
`kalloc_type_create_zones_fixed()` and its immediately adjacent probe
boundaries. The photo does not identify an exact internal instruction, prove
an exception, or distinguish a hang from slow progress. It does not justify
skipping zone creation or altering allocation metadata. Per the user's
instruction, analyze and update the handoff only; do not start a new build.
