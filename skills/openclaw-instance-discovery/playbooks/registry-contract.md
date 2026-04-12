# Registry Contract

This document describes the v1 schema for `local/state/instances.json` — the
instance registry maintained by the openclaw-instance-discovery skill. The
registry is a single JSON file that captures every OpenClaw instance found on
the machine, together with enough metadata for any downstream skill or agent to
connect to the right instance without repeating discovery.

The example JSON block below is parsed and validated by the test suite to catch
drift between these docs and the implementation.

---

## Path

The registry lives at:

```
$REPO_ROOT/local/state/instances.json
```

### How to find `REPO_ROOT`

**IMPORTANT:** The repo root is NOT your current working directory. It is the directory where the skill source checkout lives on disk. You must resolve it explicitly.

Run this command to locate the repo root:

```bash
REPO_ROOT=""
for d in \
  ~/.claude/skills/openclaw-instance-discovery \
  ~/.claude/skills/openclaw-troubleshooting \
  ~/.openclaw/skills/openclaw-troubleshooting \
  ~/.codex/skills/openclaw-troubleshooting \
  ~/src/openclaw-skills/skills/openclaw-troubleshooting; do
  if [ -e "$d" ]; then
    resolved="$(readlink "$d" 2>/dev/null || echo "$d")"
    candidate="$(cd "$resolved/../.." 2>/dev/null && pwd)"
    if [ -d "$candidate/local" ] && [ -d "$candidate/skills" ]; then
      REPO_ROOT="$candidate"
      break
    fi
  fi
done
echo "${REPO_ROOT:?Could not find openclaw-skills repo root}"
```

**Verification:** The result must contain both a `local/` directory and a `skills/` directory. If it doesn't, the resolution failed — try the fallback paths manually.

**Why this matters:** In testing, agents that skipped this resolution and used the current working directory instead wrote `instances.json` into the wrong location entirely (e.g., the user's Documents folder). The registry must live in the skill repo's `local/state/`, not anywhere else.

The `local/state/` directory is gitignored; only `.gitkeep` is tracked. The
registry file is written at runtime and must never be committed.

All other skills that reference `$REPO_ROOT` (troubleshooting, compound) should use this same resolution command.

---

## v1 schema

```json
{
  "version": 1,
  "updatedAt": "2026-04-11T18:00:00Z",
  "defaultInstanceId": "default",
  "instances": [
    {
      "id": "default",
      "label": "default",
      "kind": "app-managed",
      "profile": null,
      "port": 18789,
      "configPath": "/Users/ada/.openclaw/openclaw.json",
      "stateDir": "/Users/ada/.openclaw",
      "serviceLabel": "ai.openclaw.gateway",
      "notes": "Mac app / likely day-to-day instance",
      "discoveredFrom": "launchd service ai.openclaw.gateway + config ~/.openclaw/openclaw.json"
    }
  ]
}
```

---

## Field guidance

### Top-level fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `version` | integer | yes | Always `1` for this schema. Increment when breaking changes are made. |
| `updatedAt` | string (ISO 8601) | yes | UTC timestamp of the last discovery run that wrote this file. |
| `defaultInstanceId` | string | yes | The `id` of the instance that should be used when the user has not specified one. Must resolve to an entry in `instances`. |
| `instances` | array | yes | Ordered list of discovered instances. May contain one or more entries. |

### Per-instance fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | Stable identifier for this instance. Typically `"default"`, `"instance-2"`, etc. Must be unique within the registry. |
| `label` | string | yes | Human-readable name shown in confirm / announce lines. Usually matches `id` or the profile name. |
| `kind` | string | yes | How the instance is managed. Known values: `"app-managed"` (Mac app / launchd), `"cli-managed"` (started by `openclaw gateway start`), `"unknown"`. |
| `profile` | string or null | yes | The `--profile` value passed to openclaw, or `null` for the default profile. |
| `port` | integer or null | yes | The gateway port number. `null` if unknown or not yet probed. |
| `configPath` | string or null | yes | Absolute path to the active `openclaw.json` config file for this instance. `null` if not resolved. |
| `stateDir` | string or null | yes | Absolute path to the state directory for this instance (e.g. `~/.openclaw`). `null` if not resolved. |
| `serviceLabel` | string or null | yes | The launchd service label for this instance (e.g. `ai.openclaw.gateway`), or `null` if not launchd-managed. |
| `notes` | string or null | no | Free-form human note written by the discovery agent. Useful for surfacing context like "Mac app / likely day-to-day instance". |
| `discoveredFrom` | string | yes | Single-sentence description of the evidence trail used to identify this instance. Powers the trust-building announce-target line shown to non-technical users. Must not be empty. Example: `"launchd service ai.openclaw.gateway + config ~/.openclaw/openclaw.json"`. |

---

## Schema rules

- Treat this file as a cached model. Stale is better than absent — if discovery
  fails partway through, write what was found rather than deleting the file.
- Keep it small: no log output, no raw `launchctl` dumps. Store only the
  synthesised facts a skill needs to connect.
- The `defaultInstanceId` must always resolve. Do not write a registry where
  `defaultInstanceId` points to a non-existent entry.
- All string fields that are marked "required" must be present even if their
  value is `null`. Do not omit required fields.
- The `discoveredFrom` field must be a non-empty string. It is required in v1
  because it is the primary source of the trust-building announce-target line
  for non-technical users.

---

## Ownership

### Who writes

The openclaw-instance-discovery skill (specifically the discovery-sequence
playbook) is the only writer. It writes (or overwrites) the registry at the
end of each successful discovery run, updating `updatedAt` and the `instances`
array.

No other skill or agent should write to this file. If a downstream consumer
(e.g. openclaw-troubleshooting) discovers the registry is stale or missing, it
should invoke the discovery skill rather than writing its own copy.

### Who reads

Any skill or agent that needs to connect to an OpenClaw gateway reads this
registry to find the right instance. Typical consumers:

- `openclaw-troubleshooting` — reads `defaultInstanceId` or asks the user to
  pick an instance when multiple are present.
- Ad-hoc agent tasks — reads the instance list to resolve `--url` and
  `--token` arguments without prompting the user.

Reading is safe at any time; consumers should handle the case where the file
does not exist (registry not yet populated) or is older than a configurable
staleness threshold.

---

## Schema versioning

The `version` field exists to allow non-breaking evolution of the registry:

- **Additive changes** (new optional fields, new `kind` values): no version
  bump required. Readers must ignore unknown fields.
- **Breaking changes** (rename required fields, change semantics of existing
  fields): increment `version` to `2` and document the migration path here.
- Readers that encounter a `version` they do not recognise should log a warning
  and fall back to invoking fresh discovery rather than crashing.
