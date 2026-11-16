# M42 / v185 fixed type-view and parser phase codes

Preserves the M41 page and ladder. A new full-width white band at row280
identifies M42. It sits between calibration cells240-271 and index cells320-351.

Two new 16-bit binary cell rows show current phase and value:

- row800: current phase, high bit first.
- row840: phase-dependent value, truncated to16 bits.

Cell geometry is the same as M40: x60+60*n, 48 value pixels, 12 black gap,
height32, white1/black0, n0..15. The rows end831 and871, before argument880.
The original callback index, full function and argument pointers stay intact.
Use M42 final Mach-O mapping when checking the current function pointer.

| Phase | Last reached operation | Value |
| --- | --- | --- |
|4101|fixed initialization entered|0|
|4102|early_random returned and hash seed stored|0|
|4103|DLUT construction returned, before parser|0|
|4104|parser returned and kt_count stored, before assertions|kt_count|
|4105|count and scratch-capacity assertions passed, before qsort|kt_count|
|4106|qsort returned|kt_count|
|4107|fixed iterators returned|kt_count|
|4108|fixed zone creation returned|kt_count|
|4201|parser entered, before KC format query|type enum|
|4202|KC format query failed, before panic|type enum|
|4203|KC format query succeeded, before branch|KC format enum|
|4210|static format selected, before XNU views copy|type enum|
|4211|static XNU views copied|view count|
|4220|fileset branch entered|type enum|
|4230|KCGEN branch entered, before XNU views copy|type enum|
|4231|KCGEN XNU views copied|view count|
|4232|prelink text lookup returned, before assert|section exists 0/1|
|4233|prelink address and end loaded|prelink size /4096|
|4234|sparse index lookup returned, before validation|index exists 0/1|
|4235|index validation returned, before kext loop|index count|
|4236|current component address selected, before header validation|index position|
|4237|component header accepted, before command traversal|ncmds|
|4239|current kext type section found, before copy|index position|
|423A|kext type views copy returned|view count|
|4238|component load-command traversal ended|index position|
|42EE|unsupported format, before panic|KC format enum|
|42FF|parser about to return|view count|

The parser codes also apply to later variable-view parsing, with the type
enum distinguishing it. Phase advances only on the shown event. Each phase
write updates two rows in sequence; a partially painted row can occur during
a fault or reset. Cross-check the calibration, original callback state and
ladder rather than assuming a missing code equals zero.

M41 photo ba8842f61993a71365ecad98ef579a2f.jpg confirms kalloc_init index878,
argNULL, milestones1240-1400 present and1440 onward absent. Its fixed-view
initialization had not returned. Disk metadata audit found1274 fixed types,
1127 nondata/nonVM types and valid strings/required flags; prelink text exists
with size0 and no sparse index. This motivates diagnosis, not a format change.
