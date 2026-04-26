---
name: openclaw-babysit
description: Use when the user wants to monitor OpenClaw channel health on a recurring basis and either alert or auto-fix when channels degrade. Designed to run inside `/loop` (e.g. `/loop 5m /openclaw-babysit` for alert mode, `/loop 5m /openclaw-babysit --auto-fix` for autonomous repair). Triggers on natural-language phrasings like "babysit my openclaw", "watch openclaw", "keep openclaw running", "make sure my agents stay reachable", "auto-fix openclaw if it breaks", "monitor my channels". One tick = one health check; a streak of healthy ticks closes any open incident, a degraded reading either alerts or invokes `/openclaw-troubleshooting` in authorized mode.
---

# OpenClaw Babysit

A monitoring skill that runs as a recurring health check over OpenClaw's channels (Slack, Discord, Telegram, BlueBubbles, etc.) and decides — based on its mode — whether to alert the user or invoke autonomous repair. Designed to be wrapped by Claude Code's `/loop` so each tick is a single health check.

The success criterion is **channels working** — the user can reach their agents through the channels they have enabled. Gateway-level health is a means to that end, not the end itself.

## Modes

This skill supports two modes, selected by the loop command:

| Mode | Invocation | Behavior on degradation |
| --- | --- | --- |
| Alert | `/loop <interval> /openclaw-babysit` | Print a clear summary of what's wrong and stop. The user runs `/openclaw-troubleshooting` interactively if they want to dig in. |
| Auto-fix | `/loop <interval> /openclaw-babysit --auto-fix` | Invoke `/openclaw-troubleshooting` with `OPENCLAW_TROUBLESHOOTING_AUTHORIZED=1`, let it apply allowlisted fixes, verify, and iterate up to the cap. On give-up, drop to alert. |

Default is alert-only. Auto-fix is opt-in and explicit.

## Finding the repo root

The skill must resolve the source repo root before reading or writing any `local/` path:

```bash
REPO_ROOT=""
for d in \
  ~/.claude/skills/openclaw-babysit \
  ~/.claude/skills/openclaw-troubleshooting \
  ~/.openclaw/skills/openclaw-babysit \
  ~/.codex/skills/openclaw-babysit \
  ~/src/openclaw-skills/skills/openclaw-babysit; do
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

- **PREFLIGHT — Load the instance registry.** Read `$REPO_ROOT/local/state/instances.json` for the default instance. If the file is missing or malformed, exit with a one-line message asking the user to run `/openclaw-troubleshooting` (which auto-triggers discovery). Do not invoke discovery from babysit itself — registry repair is interactive.
- **Load tick state.** Read `$REPO_ROOT/local/state/babysit-<instance-id>.json` if it exists. If not, this is a fresh start; treat all counters as unset.
- **Run one health check.** See `playbooks/health-check.md`.
- **Decide.** Healthy → record stable-tick streak; if streak ≥ 2 and an incident was open, mark it closed. Degraded → branch on mode (alert vs auto-fix).
- **Write tick state.** Always update the state file with current counters and current incident state before exiting the tick.
- **One line of output when healthy.** Verbose output only on state change (degraded → alerting, alerting → recovered, auto-fix → applied X, auto-fix → giving up).

## Workflow

A single tick is structured as:

```
1. Resolve repo root, instance, prior state.
2. Run health check (playbooks/health-check.md). Output: { status: healthy|degraded, evidence: {...} }.
3. Reconcile against prior state:
   - prior healthy + now healthy: increment consecutive-healthy counter, write state, emit one-line OK.
   - prior healthy + now degraded: open new incident in state, branch on mode.
   - prior degraded + now degraded: same incident, branch on mode (with iteration counters).
   - prior degraded + now healthy: increment consecutive-healthy. If ≥ 2, close the incident and emit a recovery line.
4. Mode branch:
   - Alert mode: print degradation summary, stop. Do NOT invoke troubleshooting.
   - Auto-fix mode: see "Auto-fix loop" below.
5. Write tick state.
```

## Auto-fix loop

When degraded in auto-fix mode:

1. **Check iteration cap.** If the current incident's `fixesTried` length ≥ 3, or the same fix was just attempted in the previous tick and didn't recover, drop to alert mode for this incident: emit a "tried X, Y, Z; giving up; need manual intervention" message and stop applying fixes for the rest of this incident. Do not retry until the user clears the state or recovery is observed independently.

2. **Invoke `/openclaw-troubleshooting` in authorized mode.** Set `OPENCLAW_TROUBLESHOOTING_AUTHORIZED=1` in the shell environment for any commands the troubleshooting skill runs, and pass the diagnosis hint (the symptoms babysit observed). The troubleshooting skill will diagnose, check `playbooks/auto-fix-allowlist.md`, and either:
   - Apply an allowlisted fix and report the verification result.
   - Emit a one-paragraph diagnosis and exit (no fix applied).

3. **Record the attempt.** Append to the current incident's `fixesTried` with the signature matched and the fix applied (or "no allowlisted fix"). Update `lastFixAt` to now.

4. **Re-run the health check.** A single tick can include the apply-and-verify cycle; do not wait for the next loop interval. If healthy: emit a "fix X applied; channels back" message and continue; the next tick will confirm stability. If still degraded: stop here for this tick — the next loop interval will pick up where this one left off (the iteration cap counts the cumulative attempts, not per-tick).

5. **Never apply config edits in auto-fix mode.** This rule is enforced by the troubleshooting skill's allowlist; babysit relies on it. If the troubleshooting skill returns "no allowlisted fix" because the matched signature is config-shaped, treat this as a give-up signal and drop to alert mode for this incident.

## State file

Path: `$REPO_ROOT/local/state/babysit-<instance-id>.json`. One per OpenClaw instance.

Schema:

```json
{
  "version": 1,
  "instanceId": "default",
  "lastTickAt": "<ISO-8601 UTC timestamp>",
  "lastRunsCounter": 1,
  "consecutiveHealthyTicks": 4,
  "currentIncident": null
}
```

When an incident is open, `currentIncident` is:

```json
{
  "id": "incident-<UTC timestamp slug>",
  "startedAt": "<ISO-8601 UTC timestamp>",
  "lastSignature": "<verbatim primary signature from the health check>",
  "fixesTried": [
    { "appliedAt": "<ISO-8601 UTC timestamp>", "signature": "<allowlist entry id, e.g. A1>", "result": "verified-healthy" }
  ],
  "lastFixAt": "<ISO-8601 UTC timestamp>",
  "givenUp": false
}
```

The state file is written atomically (write to `<path>.tmp`, then rename) to avoid partial writes if a tick is interrupted. The file is gitignored under the existing `local/state/*` pattern.

## Per-tick output discipline

Loops generate a lot of text. Babysit must keep its per-tick output proportional to what changed:

- **Healthy, no incident open:** one line. e.g. `babysit: OK — 4 ticks healthy, channels: slack, discord, telegram, bluebubbles all ok`.
- **Healthy, recovery (incident just closed):** 2-3 lines. Note the closed incident, what fixed it (if known), and the tick streak.
- **Degraded, alert mode:** structured summary of evidence and the recommended next step (`/openclaw-troubleshooting`). No tail output beyond that.
- **Degraded, auto-fix mode:** report what was tried, the result, and whether the incident is open or closed at end of tick.

If babysit is producing more than ~10 lines per healthy tick, something is wrong with the implementation, not the install.

## Reference map

- `playbooks/health-check.md` -> the channels-focused health check: which signals to read, how to combine them, healthy vs degraded thresholds.
- `../openclaw-troubleshooting/SKILL.md` (`## Authorized-fix mode`) -> the contract babysit uses to invoke troubleshooting non-interactively.
- `../openclaw-troubleshooting/playbooks/auto-fix-allowlist.md` -> the bounded set of fixes troubleshooting may apply in authorized mode.
- `../openclaw-troubleshooting/playbooks/triage.md` -> referenced by the health check for command surface and fast classification.
- `../openclaw-troubleshooting/playbooks/common-signatures.md` -> referenced by the health check for log-scan patterns.
- `$REPO_ROOT/local/memory/incident-log.md` -> environment-specific learnings; consulted by troubleshooting in authorized mode for signature recognition.

## Quality rules

- **Channels-as-success.** All decisions trace back to "are the user's enabled channels reachable?" Gateway probe alone never decides healthy.
- **Composite health, not single-signal.** A degraded reading must be backed by at least two signals (e.g. doctor reporting `ok` plus crash-loop log activity is still degraded). One signal in disagreement with the others triggers a fresh check, not a verdict.
- **Two consecutive healthy ticks to close an incident.** Single-tick recovery is suspicious — transient probe-during-healthy-window readings have fooled human troubleshooters; don't let them fool the loop.
- **Iteration cap is a hard stop.** ≤ 3 distinct fixes per incident. Repeated identical fix recommendation = stop and alert.
- **Babysit never edits config in auto-fix mode.** Enforced via the troubleshooting skill's allowlist; documented here as a contract the user can rely on.
- **Per-tick output stays proportional.** Healthy ticks are one-liners. Verbose only on state change.
- **State writes are atomic.** Tmp-file + rename, never overwrite in place.

## Tooling/fallback notes

- The skill assumes invocation from an external harness (Claude Code, Codex CLI, plain shell). Restarting the gateway from these harnesses is safe because the harness itself does not route its own tool calls through the gateway. Do **not** run this skill from inside an OpenClaw-native agent: an auto-fix restart would kill the agent mid-turn.
- Babysit reads from but never writes to `local/memory/`. That namespace belongs to `/openclaw-troubleshooting-compound`.
- If the registry at `local/state/instances.json` is missing, exit with a one-liner. Babysit does not own discovery; pushing the user back to interactive troubleshooting is the right escape hatch.
- If `OPENCLAW_TROUBLESHOOTING_AUTHORIZED` is set when babysit runs in alert mode (no `--auto-fix`), unset it before invoking troubleshooting — alert mode must never apply fixes.
