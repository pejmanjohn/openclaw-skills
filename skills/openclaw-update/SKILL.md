---
name: openclaw-update
description: Use when the user wants to update or upgrade OpenClaw on their machine. Triggers on natural language like "update openclaw", "upgrade openclaw", "openclaw update", "is there a new openclaw", "new openclaw is out", "time to upgrade openclaw", "bump openclaw", "pull the latest openclaw". Guides a safe update with preflight inventory, backup, CLI update via `openclaw update`, post-update verification against the baseline, and a final highlights briefing on what's new in the parts of OpenClaw the user actually uses. Auto-loads the saved instance registry from local/state/instances.json on activation; auto-triggers openclaw-instance-discovery if the registry is missing.
---

# OpenClaw Update

Update OpenClaw the way the documented tooling wants it updated — no shortcuts, no in-session gateway restarts, no silent regressions. Treat the local CLI as runtime truth and use `openclaw update` plus its sibling commands (`update status`, `backup create`, `doctor`, `channels status --probe`) instead of manually invoking package managers or editing files.

The goal: at the end of a run, the user is on the target version, every channel/cron/plugin they depended on before is still healthy, they have a verified backup they can roll back to, and they know what's new in the parts of OpenClaw they actually use.

## Finding the repo root

**IMPORTANT:** The repo root is NOT your current working directory. It is the directory where the skill source checkout lives on disk. You must resolve it before reading or writing any `local/` path.

Run this command to find it:

```bash
REPO_ROOT=""
for d in \
  ~/.claude/skills/openclaw-update \
  ~/.claude/skills/openclaw-troubleshooting \
  ~/.claude/skills/openclaw-instance-discovery \
  ~/.openclaw/skills/openclaw-update \
  ~/.openclaw/skills/openclaw-troubleshooting \
  ~/.codex/skills/openclaw-update \
  ~/.codex/skills/openclaw-troubleshooting \
  ~/src/openclaw-skills/skills/openclaw-update; do
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

The result must contain both `local/` and `skills/` directories. Use `$REPO_ROOT` for all paths below.

## Quick start

- **PREFLIGHT — Load the instance registry.** Read `$REPO_ROOT/local/state/instances.json`. If the file is missing, unreadable, or malformed, **auto-trigger `openclaw-instance-discovery`** before doing anything else. After discovery writes the registry, announce the target using the same plain-language format as the troubleshooting skill (see "STOP — Announce target" below).
- **Resolve the active profile.** Check `openclaw config file` AND the service manager env vars (`OPENCLAW_PROFILE`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`). If they differ, pass `--profile <X>` on every command.
- **Refuse to update on a broken baseline.** If `openclaw doctor` is red, `openclaw config validate` fails, or the gateway is crash-looping before you start, stop and hand off to `openclaw-troubleshooting`. Do not layer an update on top of an already-unhealthy install.
- **Know when it's safe to restart the gateway from within a session.** The hard rule is for **OpenClaw-native agents** (agents that route their own commands through the gateway they're restarting) — for those, `openclaw gateway restart` kills the agent mid-command and leaves stale locks. **External harnesses** (Claude Code, Codex CLI, a plain shell) are not routing through the gateway, so they can safely execute the two-step `stop` + `launchctl bootstrap` sequence documented in Phase 5. If you're an OpenClaw-native agent, emit the manual commands for the user instead. If you're an external harness, you may run them yourself. When in doubt, emit and wait — the skill is always correct if it hands off the restart.
- **Always pass `--no-restart` to `openclaw update`.** This is non-negotiable. The skill uses `--no-restart --yes` and then asks the user to restart the gateway.
- **One approval gate, then flow.** The only boundary that always asks for approval is the end of Phase 1: "we're upgrading from X to Y, proceed?" After that yes, Phases 2-8 auto-advance. The skill only stops again if something anomalous happens: release notes flag a BREAKING change or deprecation, a backup fails to verify, the update command exits non-zero, the gateway doesn't come back healthy after restart, or a post-update gate goes yellow/red. A smooth run surfaces the highlights at the end without asking mid-flight.

## STOP — Announce the target before ANY work

**Before running ANY `openclaw` command beyond the registry load, before reading ANY log file, before starting inventory, you MUST announce the target.**

If you have not produced the announcement below, you have skipped the preflight. Go back to the Quick start and complete it.

1. Load the registry from `$REPO_ROOT/local/state/instances.json` (auto-trigger discovery if the file is missing)
2. Read the default instance from the registry
3. State the target using this exact format:

Single-instance announcement:

> I'm targeting the OpenClaw I found on this Mac:
> - port [port from registry]
> - config [configPath from registry]
> - service [serviceLabel from registry]
> - evidence: [discoveredFrom from registry]

Multi-instance announcement:

> I'm targeting your saved default OpenClaw:
> - label [label from registry]
> - port [port from registry]
> - config [configPath from registry]
>
> If you want me to update the other one instead, say `use the other one`.

4. **Only THEN** proceed to the preflight inventory.

Do not skip this step. Do not abbreviate it. Do not fold it into other output.

## Override grammar

The user can switch the active target at any point with one of these phrases:

- `use the other one` — switch to the next instance in the registry that isn't the current target
- `use <label>` — switch to the instance with the matching `label` field
- `use the one on <port>` — switch to the instance with the matching `port` field

After an override, restate the new target and restart the update flow from preflight. Do not carry a partially-completed baseline across instances.

## Do NOT write to Claude Code's memory system

Update-run data — baselines, post-update snapshots, upgrade history, backup manifests — lives ONLY in the skill repo's `local/` directory. Do NOT write update data to Claude Code's memory system (`memory/`, `MEMORY.md`, or any workspace memory files). The skill writes to these locations under `$REPO_ROOT/local/`:

- `local/state/update-baseline-<timestamp>.json` — preflight inventory snapshot
- `local/state/update-post-<timestamp>.json` — post-update snapshot for diffing
- `local/backups/<timestamp>/` — explicit config/credentials copies
- `local/memory/upgrade-history.md` — per-user ledger of past updates

`local/` is gitignored at the repo root, so nothing in it is ever pushed upstream.

## Workflow

The skill runs in phases. Each phase ends with a clear gate that requires user approval before continuing.

### Phase 0 — Target

Load the registry, auto-trigger discovery if missing, announce the target. See the sections above. Non-negotiable.

### Phase 1 — Preflight inventory

Read-only. Capture the current state as a JSON snapshot so Phase 6 can diff against it. See `playbooks/preflight-inventory.md` for the exact command list and snapshot shape.

Announce a short release summary:
- Current version, target (latest) version, update channel, install kind
- Counts: channels configured, crons configured, plugins loaded, skills available
- `doctor` status, `config validate` status

**Gate (anomaly):** If baseline doctor is red or config validate fails, refuse to proceed. Hand off to `openclaw-troubleshooting`.

**Gate (the one approval gate):** Otherwise, ask the user to confirm the upgrade from `<installed>` to `<target>` before advancing. This is the only routine approval gate; after this yes, Phases 2-8 run automatically and only stop on anomalies.

### Phase 2 — Release-notes pre-check (soft, non-blocking)

Fetch release notes for the version range from current to target (multiple point releases may be involved). Skim for BREAKING changes, deprecations, or migration steps. Summarize anything flagged in 1-3 bullets.

**Gate (anomaly-only):** If BREAKING changes or deprecations are flagged in the version range, stop and surface them before continuing — the user may want to bail out. Otherwise auto-advance to Phase 3; the summary is informational and the user can read it after the fact in the Phase 8 highlights.

See `playbooks/post-update-highlights.md` for how to fetch release notes (the same source is reused in Phase 7).

### Phase 3 — Backup

Run `openclaw backup create` (native archive covering config, credentials, sessions, workspaces) AND make an explicit copy of the active config file plus the baseline snapshot into `$REPO_ROOT/local/backups/<timestamp>/`. Verify the archive with `openclaw backup verify`.

See `playbooks/backup.md` for the full sequence and manifest format.

**Gate (anomaly-only):** If `backup verify` fails or the explicit copy can't be created, halt. Otherwise auto-advance to Phase 4.

### Phase 4 — Run the update

Preview first:

```bash
openclaw update --dry-run
```

Then, on approval:

```bash
openclaw update --no-restart --yes
```

`--no-restart` is mandatory — see Quick start. `--yes` skips downgrade prompts in the rare case the target is older than the current version.

See `playbooks/cli-update.md` for install-kind notes (pnpm/npm/brew/git-checkout — all handled by `openclaw update` internally; the skill does not invoke package managers directly) and the exact flag reference.

**Gate (anomaly-only):** If `openclaw update` exits non-zero OR `openclaw --version` still reports the old version after, halt and consult `openclaw-troubleshooting`. Otherwise run the staging-completeness check below and auto-advance to Phase 5.

**Extension-staging post-check (added after run 2):** After the update completes, enumerate bundled extensions whose `package.json` declares `openclaw.bundle.stageRuntimeDependencies: true` but whose sibling `node_modules/` directory is missing. If any enabled or currently-loaded plugin is in that set, a gateway restart will crash-load it. Offer a scoped repair — `pnpm install --prod` inside each at-risk extension directory — before advancing to Phase 5. See `playbooks/cli-update.md` for the exact enumeration + repair commands.

### Phase 5 — Gateway restart

The new CLI is on disk but the running gateway process is still on the old binary. It needs to be restarted for the update to take effect.

**Three-step sequence** (the `enable` step is mandatory — `bootstrap` will fail without it after a `gateway stop`):

```bash
openclaw gateway stop
launchctl enable gui/$(id -u)/<serviceLabel>
launchctl bootstrap gui/$(id -u) <plistPath>
```

`<serviceLabel>` and `<plistPath>` come from the instance registry (`serviceLabel` field, plus `<plistPath>` derived from `~/Library/LaunchAgents/<serviceLabel>.plist` on macOS). For the default case these are `ai.openclaw.gateway` and `~/Library/LaunchAgents/ai.openclaw.gateway.plist`.

**Why the `enable` step is mandatory:** `openclaw gateway stop` performs a `launchctl bootout`, which on macOS can leave the service in launchctl's **disabled** list. A subsequent `launchctl bootstrap` against a disabled service fails with a cryptic `"Bootstrap failed: 5: Input/output error"` and no further explanation. Running `launchctl enable` first re-enables the service and lets bootstrap succeed.

**Who runs the three commands:**

- **If you are an OpenClaw-native agent** (your turns route through the gateway you'd be restarting): emit the three commands for the user, wait for explicit confirmation, then proceed. Do not run them yourself — the `stop` step kills the gateway your own turn depends on.
- **If you are an external harness** (Claude Code, Codex, plain shell session): run the three commands yourself. You are not routing through the gateway; stopping and re-bootstrapping it does not affect your own process.

After the three commands complete, wait ~10 seconds for the gateway to come up and for channel providers to finish initializing. The first `openclaw gateway probe` may report a transient `Connect: failed - gateway closed (1006)` if run too soon; give it another 5-10 seconds before concluding the restart failed.

**Stale-lock recovery** — if `launchctl bootstrap` fails even after `enable`, check for stale lock files under `$TMPDIR/openclaw-$(id -u)/`:

```bash
rm -f "$TMPDIR/openclaw-$(id -u)/gateway."*.lock
# then re-run enable + bootstrap
```

**Gate (anomaly-only):** If `openclaw gateway probe` still fails past ~20s, or the reported `app` version doesn't match the target, halt and investigate. Otherwise auto-advance to Phase 6.

### Phase 6 — Post-update gates (diff vs. baseline)

Re-run every command from Phase 1 against the now-running new version. Save as `$REPO_ROOT/local/state/update-post-<timestamp>.json`. Diff field by field.

See `playbooks/post-update-gates.md` for the pass/fail criteria.

A PASS requires:
- Version bumped to the target
- Gateway RPC probe OK
- `doctor` clean (new warnings explained, not hidden)
- Channel count unchanged; every previously-healthy channel still probes green
- Cron count unchanged; every previously-enabled cron still enabled
- Plugin count unchanged; no new init failures
- `config validate` still passes

**Gate (anomaly-only):** On any red gate, halt and go to `playbooks/rollback.md`. On any yellow gate, surface the specifics and ask for a judgment call. On all-green, auto-advance to Phase 7.

### Phase 7 — Upgrade history ledger

Append an entry to `$REPO_ROOT/local/memory/upgrade-history.md` with from/to versions, install kind, timestamp, backup path, duration, and any notes. See `playbooks/upgrade-history.md` for the format template.

This is the per-user ledger — analogous to the troubleshooting-compound skill's local incident log. Gitignored, never pushed upstream.

### Phase 8 — Relevance briefing (what's new that matters to YOU)

Fetch release notes for the version range and intersect them against the user's actual inventory from the baseline snapshot: channels enabled, plugins active, cron jobs present, skills installed, auth profiles configured, config keys set.

Surface only items that intersect. Group by area. Cap at ~5-8 bullets. Skip areas with no matches entirely.

Examples of good output:
> - **Telegram:** improved reply-threading accuracy (relevant — you have Telegram connected)
> - **Cron scheduler:** new `--at` flag for absolute time scheduling (relevant — you have 6 cron jobs)
> - **Skills:** skills.load.extraDirs now supports globs (relevant — you use custom skills dirs)

Examples of what to SKIP:
- Discord features when the user doesn't have Discord
- WhatsApp changes when no WhatsApp account is configured
- Generic "bug fixes and improvements" items
- Changes to CLIs/subcommands the user never invokes

See `playbooks/post-update-highlights.md` for the full matching rules and release-notes source.

## Reference map

Read only the file that matches the phase you're in:

- `playbooks/preflight-inventory.md` -> command list, snapshot JSON shape, where it's saved.
- `playbooks/backup.md` -> `openclaw backup create` flow, explicit config copy, verify step, backup-manifest format.
- `playbooks/cli-update.md` -> `openclaw update` flag reference, install-kind delegation, the `--no-restart` rule, dry-run usage.
- `playbooks/post-update-gates.md` -> diff rules, pass/fail criteria, what to do on a red gate.
- `playbooks/post-update-highlights.md` -> release-notes source, version-range enumeration, inventory intersection, output shape.
- `playbooks/rollback.md` -> rollback ladder: `openclaw update --tag <previous>`, restore config from backup, restart sequence for the user.
- `playbooks/upgrade-history.md` -> shipped format template; actual entries live in `$REPO_ROOT/local/memory/upgrade-history.md` (gitignored, per-user).

## Quality rules

- **Know who's allowed to restart the gateway from within a session.** See Quick start. OpenClaw-native agents must emit manual commands and wait. External harnesses (Claude Code, Codex, plain shell) may run the three-step `stop` + `enable` + `bootstrap` sequence themselves. Either way, the `enable` step is mandatory — without it, `bootstrap` fails with a cryptic I/O error.
- **Always pass `--no-restart` to `openclaw update`.** No exceptions.
- **One approval gate, not many.** After the Phase 1 version-confirmation yes, Phases 2-8 auto-advance. Stop only on anomalies (BREAKING notes, verify failure, non-zero update exit, restart not healthy, yellow/red post-update gate). A clean run should feel like one yes → a short wait → a highlights briefing.
- **Refuse to update a broken install.** If baseline is red, fix it first via `openclaw-troubleshooting`, then come back.
- **Do not invoke package managers directly.** No `npm install -g openclaw`, no `brew upgrade openclaw`, no `git pull` in the source checkout. `openclaw update` handles install-kind routing internally.
- **Do not write to Claude Code's memory system.** All update state goes to `$REPO_ROOT/local/`.
- **Do not mix the update with unrelated config changes.** If the user asks for a config tweak that's not related to anything the update surfaced, decline and suggest doing it before or after. **Targeted fixes for yellow gates the update itself surfaced are allowed** — e.g. a model slug the new version dropped from the catalog, a schema key the new version renamed. Scope the fix to exactly the key that's warning; don't opportunistically clean up nearby config. Use the troubleshooting skill's `config-writing.md` discipline: propose the exact key/value change, back up (already done in Phase 3), `openclaw config set`, then `config validate`.
- **Verify before claiming success.** Every pass claim must cite the specific post-update command output that proves it.
- **Prefer the local binary over the docs.** If `openclaw update --help` on the installed binary differs from docs.openclaw.ai, follow the local binary. The docs may be ahead of the installed version.

## Tooling/fallback notes

- The skill delegates to `openclaw update` for the actual install step. That command detects the install kind (pnpm global, npm global, brew, git checkout) and routes accordingly. The skill does not need install-kind branching logic.
- If `openclaw update status --json` shows `installKind: unknown` or the update fails with an install-kind error, stop and ask the user to run `openclaw doctor` — install-kind detection failure is a troubleshooting problem, not an update problem.
- For release-notes fetching, prefer (in order): `openclaw docs` search for the version, the GitHub releases page of the OpenClaw repo, then docs.openclaw.ai changelog pages. Document which source you used in the highlights output.
- If release notes are unreachable, skip Phase 2 and Phase 8 with a brief explanation. Do not block the update on a network failure reading changelog pages.
- The shipped skill intentionally does not cover the macOS menu-bar app upgrade (codesign, notarize, staple, `/Applications/OpenClaw.app` cutover). That's a small subset of users; if the user has the Mac app, they should do the app cutover manually after the CLI update succeeds. Future versions of this skill may add a separate Mac-app phase.
