# Preflight Inventory

Capture the current state of the OpenClaw install as a JSON snapshot so the post-update phase can diff against it. Everything in this phase is **read-only** — do not mutate config, restart services, or touch secrets.

The snapshot is the source of truth for "what was healthy before the update." If the update drops a channel, breaks a cron, or fails a plugin, the diff against this baseline will catch it.

## Where the snapshot goes

```
$REPO_ROOT/local/state/update-baseline-<timestamp>.json
```

Timestamp format: `YYYYMMDD-HHMMSS` (e.g. `20260420-143022`). Keep the timestamp identical across all files from the same run so backup and post-update snapshots line up.

Remember the timestamp — Phases 3 (backup), 6 (post-update snapshot), and 7 (upgrade history) all reuse it.

## Command ladder

Run these in order. If a command is unavailable on the installed binary (version drift), note it in the snapshot under `commands_missing` and continue — do not fail the preflight just because one command was renamed.

Use `--profile <X>` on every command if the resolved profile is not the default.

### Version and update availability

```bash
openclaw --version
openclaw update status --json
```

Capture from `update status --json`:
- `update.root` — install directory
- `update.installKind` — `package` (npm/pnpm/brew) or `git`
- `update.packageManager` — `npm`, `pnpm`, `brew`, or `git`
- `channel.value` — `stable`, `beta`, or `dev`
- `channel.source` — where the channel setting came from
- `availability.available` — is an update available
- `availability.latestVersion` — the target version

### Gateway

```bash
openclaw gateway status --json 2>/dev/null || openclaw gateway status
openclaw gateway probe --json 2>/dev/null || openclaw gateway probe
```

Capture: gateway PID, port, uptime, bind address, auth mode, RPC probe result.

### Health

```bash
openclaw doctor
openclaw config validate
```

Capture: doctor warnings/errors (count + text), validate pass/fail.

### Channels

```bash
openclaw channels list --json 2>/dev/null || openclaw channels list
openclaw channels status --probe
```

Capture per channel: provider, account identifier, enabled flag, probe result (ok/fail), auth profile, last error if any.

#### Fallback: plugin-load hard-fail at the CLI

On installs that use SecretRef-based credentials, `openclaw channels list`, `channels status`, `health`, and `status` can hard-fail at CLI startup with:

```
[openclaw] Failed to start CLI: PluginLoadFailureError: plugin load failed: <provider>:
  <provider>.accounts.<account>.<tokenKey>: unresolved SecretRef "file:..."
```

This is a CLI-side plugin loader limitation: the CLI tries to resolve credentials before the gateway runtime can provide them. The gateway itself is typically fine — the channels still work at runtime. A fix landed in `2026.4.20` for Slack-specifically via `file`/`exec` SecretRef sources, but earlier stable versions hit this.

When you see this error, fall back to this two-step enumeration:

1. **Channel list from the active config file:**
   ```bash
   jq -r '.channels | keys[]' "$(openclaw config file)"
   ```
   This gives you every configured provider (e.g. `bluebubbles`, `discord`, `slack`, `telegram`). The config is read directly — no plugin loading, no CLI side-effects.

2. **Channel probe status from `openclaw doctor`:**
   ```bash
   openclaw doctor 2>&1 | grep -E '^(Discord|Slack|Telegram|BlueBubbles|WhatsApp|Matrix|Mattermost): (ok|fail)'
   ```
   Doctor routes through the gateway runtime and captures per-channel probe status (provider name, display name, latency). This is the authoritative probe result when `channels status --probe` can't run.

Record in the snapshot under `channels[]` with `source: "config + doctor probe"` to mark that the fallback path was used. Also record the failure under `known_issues` so the post-update diff doesn't treat the fallback as a regression.

### Crons

```bash
openclaw cron list --json 2>/dev/null || openclaw cron list
openclaw cron status
```

Capture per cron: id, schedule, enabled flag, target command, last-run status.

### Plugins

```bash
openclaw plugins list --json 2>/dev/null || openclaw plugins list
```

Capture per plugin: id, enabled flag, init status (ok / failed), error message if failed.

### Skills

```bash
openclaw skills list --json 2>/dev/null || openclaw skills list
```

Capture per skill: name, source (builtin / user / workspace), enabled flag.

### Config file path

```bash
openclaw config file
```

Capture the active config path. Phase 3 (backup) copies this file verbatim.

## Snapshot JSON shape

```json
{
  "version": 1,
  "capturedAt": "2026-04-20T14:30:22Z",
  "runId": "20260420-143022",
  "target": {
    "instanceId": "default",
    "label": "default",
    "port": 18789,
    "configPath": "/Users/<user>/.openclaw/openclaw.json",
    "serviceLabel": "ai.openclaw.gateway",
    "profile": null
  },
  "installed": {
    "version": "2026.4.5",
    "installKind": "package",
    "packageManager": "pnpm",
    "installRoot": "/opt/homebrew/lib/node_modules/openclaw"
  },
  "channel": {
    "value": "stable",
    "source": "config"
  },
  "target_version": {
    "available": true,
    "latestVersion": "2026.4.15"
  },
  "health": {
    "doctor": "ok",
    "doctor_warnings": [],
    "config_validate": "ok"
  },
  "gateway": {
    "status": "running",
    "pid": 12345,
    "probe": "ok",
    "uptime_seconds": 864000
  },
  "channels": [
    {
      "provider": "telegram",
      "account": "default",
      "enabled": true,
      "probe": "ok",
      "authProfile": "telegram:default"
    }
  ],
  "crons": [
    {
      "id": "morning-digest",
      "schedule": "0 8 * * *",
      "enabled": true,
      "last_run": "ok"
    }
  ],
  "plugins": [
    {
      "id": "slack",
      "enabled": true,
      "init": "ok"
    }
  ],
  "skills": [
    {
      "name": "openclaw-troubleshooting",
      "source": "user",
      "enabled": true
    }
  ],
  "commands_missing": []
}
```

## Field guidance

- **`version`** — schema version for this snapshot format. Bump when the shape changes. Post-update snapshot must match.
- **`runId`** — shared across all artifacts in this run (baseline, post, backup dir). Used to pair them up.
- **`target`** — copied verbatim from the instance registry, not re-derived. Source of truth is `$REPO_ROOT/local/state/instances.json`.
- **`installed.version`** — string from `openclaw --version`, no parsing. Compare as strings in the diff, not semver.
- **`health.doctor`** — one of `ok`, `warnings`, `error`. If warnings, populate `doctor_warnings` with the exact text lines.
- **Arrays of channels/crons/plugins/skills** — ordered deterministically (by id/name). The diff in Phase 6 uses id-based matching, not index-based.
- **`commands_missing`** — array of command names that errored with "unknown command" or returned nothing. Signals version drift and informs the post-update diff (if a command appears post-update that was missing pre-update, that's new capability, not a regression).

## Announcing the release summary

After the snapshot is captured, present a 5-line summary to the user before proceeding:

> **Release summary**
> - Installed: `<installed.version>` (`<installKind>` via `<packageManager>`)
> - Target: `<latestVersion>` on the `<channel>` channel
> - Inventory: `<N>` channels, `<M>` crons, `<P>` plugins, `<S>` skills
> - Health: doctor `<status>`, config validate `<status>`
> - Gateway: `<status>` on port `<port>` (uptime `<human-readable>`)

Follow with one of:

- "All green. Ready to continue to the backup phase?" (if everything is healthy)
- "Baseline is unhealthy — I can't safely update on top of this. Want me to hand off to the troubleshooting skill first?" (if doctor or validate is red)

## Quality rules

- **Read-only.** No command in this phase may mutate state. If you need a command that's not on the ladder above, verify it doesn't write before running it.
- **No secret values.** The snapshot records that credentials exist and are used, not the values themselves. `authProfile` is a name/reference; the actual token stays in `secrets.json`.
- **Deterministic order.** Arrays must be sorted by id/name before writing, so diff output is stable run-to-run.
- **Fail soft on missing commands.** Record missing commands in `commands_missing` and continue. Don't halt the preflight on a renamed subcommand.
- **One snapshot per run.** Don't overwrite the file — the timestamp in the filename keeps runs separate. Old snapshots are useful for cross-run comparison.
