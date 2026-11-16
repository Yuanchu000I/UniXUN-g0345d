# M41 native kalloc metadata audit

Read-only audit of kernel SHA256
`c8465e597181033976ca552fbc0e006dfecef51607b7e3495e31a88acd6d97bb`.
No source, configuration, image or device changes were made.

- The Mach-O filetype is MH_EXECUTE (2), not MH_FILESET.
- `__TEXT,__thread_starts` exists with size0. Under the current source's
  `arm_slide_rebase_and_sign_image`, this makes `static_kernelcache=false`;
  `PE_get_primary_kc_format` selects KCFormatKCGEN for this non-fileset image.
- `__PRELINK_TEXT,__text` exists with size0. There is no `__macho_list` section.
  Thus the KCGEN path can process the native XNU views and skip the empty kext
  traversal. This is not the missing-prelink-section assertion case.
- `__DATA_CONST,__kalloc_type` is81,536 bytes, exactly1,274 records of64 bytes.
  Every record has KT_CHANGED and KT_CHANGED2. Every name/signature pointer
  resolves within a file-backed segment to a bounded NUL-terminated string.
  Signature characters are only0/1/2/3. Raw sizes range4..6152 bytes.
- After excluding data-only and VM types,1,127 fixed records remain. The raw
  count1,274 is well below initial scratch pointer capacity32,768 and the
  fixed pointer+skip-list bound26,214 derived from the256 KiB scratch space.
- `__DATA_CONST,__kalloc_var` is32,160 bytes, exactly402 records of80 bytes.
  All version fields are1, all required changed flags are present, and all
  names/type signatures/non-NULL header signatures resolve to bounded strings.

No definite on-disk kalloc metadata corruption was found. This audit does not
prove the runtime memory contents, mutation permissions or internal allocator
execution. It supports diagnostic markers before/after fixed parsing, qsort,
iterator construction and zone creation; it does not justify changing the KC
format or bypassing type segregation.

Sources reviewed:
`osfmk/arm/arm_init.c:511`, `pexpert/gen/kcformat.c:190`,
`osfmk/kern/kalloc.c:957`, and `osfmk/kern/kalloc.h:304`.
JSON evidence: `M41-kalloc-metadata-audit.json`.
Reproduction script: `audit_M41_kalloc_metadata.py`.
