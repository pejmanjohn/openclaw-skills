# Backup

Before running `openclaw update`, make two independent backups of the install:

1. The **native OpenClaw backup archive** via `openclaw backup create` — covers config, credentials, sessions, and workspaces in the documented archive format.
2. An **explicit local copy** of the active config file plus the baseline snapshot into `$REPO_ROOT/local/backups/<runId>/` — small, hand-inspectable, easy to diff.

Two backups because they serve different rollback paths. The archive is the authoritative restore source if the update corrupts state. The explicit copy is the fast lookup if you just need to see "what did the config look like before the update?"

## Where the explicit backup goes

```
$REPO_ROOT/local/backups/<runId>/
  ├── openclaw.json                   # copy of the active config
  ├── baseline.json                   # copy of the preflight snapshot
  ├── archive-path.txt                # path to the `openclaw backup` archive
  └── manifest.json                   # run metadata (timestamps, versions, paths)
```

`<runId>` matches the timestamp used for the baseline snapshot from the preflight phase. Keep them identical so every artifact from a run is trivially findable.

`local/backups/` is gitignored at the repo root. The directory is created on demand — no pre-committed skeleton is needed.

## Sequence

### 1. Create the native archive

```bash
openclaw backup create --verify --no-include-workspace --output "$BACKUP_DIR" --json
```

`--no-include-workspace` is the right default for update-triggered backups. The workspace is unchanged by a CLI update, so including it can bloat the archive by gigabytes — especially when the workspace lives on a cloud-synced drive or contains large attachments — without providing any rollback value. If the user explicitly asks to include workspace files — e.g. they're combining an update with a workspace migration — drop the flag. Otherwise keep it.

`--verify` writes and then immediately validates the archive in one step.

`--output "$BACKUP_DIR"` places the archive in `$REPO_ROOT/local/backups/<runId>/` next to the explicit copies, so everything for this run lives in one directory.

`--json` returns structured output — prefer it for parsing the archive path, verify flag, and any skipped assets.

Capture the archive path from the `archivePath` field of the JSON output. If `--json` is unavailable on the installed binary, parse from the text output and note the version drift.

### 2. Verify the archive

If you ran `backup create --verify` in step 1, the archive is already verified — confirm `verified: true` in the JSON output. Otherwise:

```bash
openclaw backup verify <archive-path>
```

If verify fails, halt. Do not proceed to the update — a failed backup verify means the rollback path is broken and the update becomes too risky.

### 3. Make the explicit copy

```bash
RUN_ID="<runId>"                       # e.g. 20260420-143022
BACKUP_DIR="$REPO_ROOT/local/backups/$RUN_ID"
mkdir -p "$BACKUP_DIR"

# Config file (path from Phase 1 snapshot)
cp "$(openclaw config file)" "$BACKUP_DIR/openclaw.json"

# Baseline snapshot (already at this path from preflight)
cp "$REPO_ROOT/local/state/update-baseline-$RUN_ID.json" "$BACKUP_DIR/baseline.json"

# Record the archive path
echo "<archive-path>" > "$BACKUP_DIR/archive-path.txt"
```

### 4. Write the manifest

`$BACKUP_DIR/manifest.json`:

```json
{
  "version": 1,
  "runId": "20260420-143022",
  "createdAt": "2026-04-20T14:30:22Z",
  "installed_version_before": "2026.4.5",
  "target_version": "2026.4.15",
  "archivePath": "/path/to/openclaw-backup-<...>.tar.gz",
  "archiveVerified": true,
  "configPath": "/Users/<user>/.openclaw/openclaw.json",
  "instanceId": "default"
}
```

`installed_version_before` and `target_version` come from the baseline snapshot. The manifest lets a future run (or a support conversation) quickly identify what this backup is from.

## Permissions

The active config file may contain references to secrets (SecretRef objects). The file itself is typically not sensitive, but if the config uses inline tokens (legacy installs), the backup copy inherits those. Tighten permissions on the explicit backup directory:

```bash
chmod 700 "$BACKUP_DIR"
chmod 600 "$BACKUP_DIR/openclaw.json"
```

`openclaw backup create` handles its own archive permissions — don't second-guess it.

## Announce the backup state to the user

After both backups exist and verify:

> **Backup complete**
> - Native archive: `<archive-path>` (verified OK)
> - Explicit copy: `$REPO_ROOT/local/backups/<runId>/`
> - Rollback path: `openclaw update --tag <previous-version>` + restore from archive if state needs rolling back
>
> Ready to preview the update?

## What NOT to back up

- **Secrets files** (`~/.openclaw/secrets.json`). These are covered by `openclaw backup create` via the credentials scope. The explicit copy intentionally does not duplicate secrets in a skill-managed directory — keep the secret blast radius small.
- **Log files.** Not useful for rollback and bloats the backup directory. Logs stay where they are.
- **The state directory.** Same reason as secrets — covered by the native archive; duplicating it in skill-managed paths is wasteful.

If the user insists on a fuller copy, point them at `openclaw backup create` with any available scope flags rather than rolling a bespoke copy in the skill.

## Quality rules

- **Two backups, not one.** Archive + explicit copy. If either fails, halt.
- **Verify the archive before proceeding.** A backup you haven't verified is wishful thinking.
- **Same `runId` everywhere.** Baseline snapshot, backup directory, post-update snapshot, upgrade-history entry all share the same timestamp. No alignment gaps.
- **Permissions tightened** on any file in `$BACKUP_DIR` that originated from a potentially-sensitive source.
- **No secrets duplication** — rely on `openclaw backup create` for credentials coverage.
- **Record the archive path** in a plain text file so future rollback doesn't have to guess where the archive went.
- **Default to `--no-include-workspace`.** Workspace content doesn't change during a CLI update; including it wastes disk and time. Override only when the user explicitly asks for a workspace-inclusive backup.
