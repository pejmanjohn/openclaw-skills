# Incident Log

Post-incident learnings from real troubleshooting sessions. Read this file AND `local/incident-log.md` (if it exists) before starting diagnosis — past gotchas prevent repeat mistakes.

## How this works

This file ships with the repo and contains **general patterns** — common gotchas that apply to any OpenClaw setup. It is tracked by git and updated via PRs.

Environment-specific learnings (your exact paths, ports, profile names, commands) live in `local/incident-log.md`, which is gitignored. The `/openclaw-troubleshooting-compound` skill writes there automatically after each resolved incident.

**Before diagnosing:** Scan both files for matching symptoms.

## Seed entries

---

## Gateway won't start after update — config migration + profile mismatch

**Precondition:** User runs a non-default profile (e.g., `--profile dev` with a separate state directory).

**Symptoms:** Gateway crash-looping (non-zero exit code in service manager), app says "can't connect to gateway", dashboard shows "too many failed authentication attempts" or "device token mismatch".

**Root cause:** OpenClaw update moves config keys to new schema locations. Config validation fails at startup, gateway exits immediately. `openclaw doctor --fix` (without the correct `--profile` flag) fixes the default profile's config, not the one the gateway actually reads.

**What didn't work:**
- `openclaw doctor --fix` without `--profile` — fixed wrong config file
- `openclaw --profile X doctor --fix` — may claim to migrate keys but not persist all changes
- Diagnosing while the service crash-loops — KeepAlive + low ThrottleInterval racks up auth lockout attempts in the background

**What fixed it:**
1. Stop the crash-looping service first
2. Run `openclaw --profile X doctor --fix`, then **verify the config file was actually modified**
3. If doctor didn't persist, migrate legacy keys manually
4. Align `gateway.port` in config with the port in service manager arguments
5. Full stop + restart to clear in-memory auth lockout
6. Use tokenized dashboard URL (`openclaw --profile X dashboard`) with correct port

**Prevention:**
- Always resolve active profile before any `openclaw` command (Step 0 in triage)
- Stop crash-looping services immediately — don't diagnose while they accumulate auth failures
- After `doctor --fix`, read the config file back to verify changes persisted
- Reconcile port across config, service arguments, and dashboard URL

---

## Gateway won't start — stale lock files after in-session restart

**Symptoms:** App says "can't connect to gateway", `openclaw gateway start` hangs, error log shows "gateway already running (pid X); lock timeout after 5000ms", service keeps crashing on restart interval.

**Root cause:** Running `openclaw gateway restart` from within an active session can kill the gateway mid-command. The second phase (start) never completes, leaving stale lock files at `$TMPDIR/openclaw-$UID/gateway.*.lock`.

**What fixed it:**
1. Kill any lingering gateway processes
2. Remove stale lock files: `rm -f $TMPDIR/openclaw-$UID/gateway.*.lock`
3. Unload and reload the service via the service manager

**Prevention:**
- Avoid `openclaw gateway restart` from within a session — use the two-step sequence: `openclaw gateway stop`, then start/bootstrap via the service manager
- If the gateway needs restarting during a session, do it from a separate terminal or let the service manager handle it
