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
| Record CI | Repository-specific workflow provided; GitHub run pending |
| Manual package CI | Explicit failing prerequisite gate; no artifacts produced |
| GitHub repository, unixnu topic, website | Not created/verified during local preparation |

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

## Publish after reviewing the snapshot

The prepared directory has an independent main-branch Git repository with no
inherited remote. No commit is fabricated under the user's identity. Configure
your normal Git author identity if needed, review staged files, then commit:

```sh
git status --short
python3 scripts/check-repository.py
git diff --cached --check
git commit -m "Publish G0345D experimental M42 device snapshot"
```

With an authenticated GitHub CLI, replace the example owner with the actual
account, then create a new repository (do not use the old G0245D origin):

```sh
REPOSITORY=YOUR_OWNER/UniXNU-g0345d
gh repo create "$REPOSITORY" --public --source . --remote origin --push
gh repo edit "$REPOSITORY" --add-topic unixnu
gh repo view "$REPOSITORY" --json repositoryTopics --jq '.repositoryTopics[].name'
```

Verify the remote commit's Porting record job, the unixnu topic and actual device
catalog page. Request a scan through the upstream project's supported process
when appropriate. Do not label the gated package workflow a successful release.
The local export contains no GitHub credentials and no remote publishing was done.

Before describing this port as meeting every official publication requirement,
complete the companion firmware repository and lawful external-input manifest,
resolve stock CLI catalog compatibility, and demonstrate the standard clean
release with revision-bound evidence. Hardware tests remain paused.
