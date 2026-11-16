# Publication checklist and present limits

This tree is ready to publish as an experimental source snapshot. It is not yet
a fully reproducible device release satisfying every official completion step.
The organization follows the official guides pinned in source-pins.toml.

| Requirement | State in this export |
| --- | --- |
| Format 2 board and matching format 1 record | Present, G0345D/MSM8996/21H461 |
| Required areas and selected component dependencies | 14 areas and 11 IDs, checked locally |
| Ordered functional inputs and source pins | Preserved, hash checked; original dirty worktree identified |
| Board package and firmware sources | Device selection present; companion firmware export pending |
| External firmware inputs and hashes | Known M34 template hash retained; full OEM extraction provenance pending |
| Standard package entry | Unchanged official template and board package mapping present |
| End-to-end clean release | Pending; legacy firmware/container integration incomplete |
| Record CI | Repository-specific workflow runs on push; check the matching commit in Actions |
| Manual package CI | Explicit failing prerequisite gate; no artifacts produced |
| GitHub repository | Published to Yuanchu000I/UniXUN-g0345d; original initialization history retained |
| unixnu topic, website | Topic configured during publication; website ingestion remains unverified |

## Record-checker compatibility

The official strict CLI loads its own catalog and does not discover custom IDs
from the device feed. At the pinned official revision its catalog omits four
selected MSM8996 IDs. The record job runs the unmodified official checker with
the hash-checked catalog from the tested fork. It checks the full dependency
closure including VerifiedRoot and ArmSmmu4K. Its success is not the success of
the stock upstream reusable workflow; component registration/migration is pending.

The official website scanner at the same revision explicitly permits custom
component IDs, so a complete record can be eligible for scanning. It cannot
infer unknown IDs' dependencies; this repository records the fork's full closure.
Actual remote ingestion and its generated page remain unverified. See
[official scanner source](https://github.com/UniXNU/UniXNU/blob/21d683dff61c66f219f03ab9d8b9249026514788/scripts/sync-devices.py).

The four scaffold implementations are tracked in the pinned tools fork, under
`drivers/NativeUfs8996`, `drivers/Blsp8996`, `drivers/Adreno530` and
`kits/Msm8996Platform`. The catalog's LOCAL-SCAFFOLD markers are not independent
commit pins; do not attempt to fetch their nominal future standalone repositories
or describe them as proven devices. These bundled probes do not perform UFS
transfers, I2C transactions or GPU submission.

## Publication and future updates

The source snapshot was committed using the owner's configured Git identity and
published to [Yuanchu000I/UniXUN-g0345d](https://github.com/Yuanchu000I/UniXUN-g0345d)
on 2026-11-16. The repository name retains the owner's chosen spelling.
Its initial GitHub commit, `3058d69bb630776104fc78731f1d87c6db374210`,
contained only a GPLv3 license. Both histories are retained by a merge.
The original license text is archived verbatim at
[github-initial-LICENSE.txt](provenance/github-initial-LICENSE.txt); see the
[license provenance note](provenance/github-initial-license.md).
The inherited root license and component-specific notices remain in effect;
this archive does not relicense the source snapshot.

For future source updates, review the actual changes and use an existing remote
base for record ownership checks:

```sh
git status --short
python3 scripts/check-repository.py --base origin/main
git diff --cached --check
git commit -m "Describe the source or record change"
git push origin main
```

Verify the matching commit's [Porting record job](https://github.com/Yuanchu000I/UniXUN-g0345d/actions)
and the repository's `unixnu` topic. Website/device-catalog ingestion remains a
separate unverified step; request a scan through the upstream project's supported
process when appropriate. Do not label the gated package workflow a successful
release. GitHub credentials are not part of the repository.

Before describing this port as meeting every official publication requirement,
complete the companion firmware repository and lawful external-input manifest,
resolve stock CLI catalog compatibility, and demonstrate the standard clean
release with revision-bound evidence. Hardware tests remain paused.
