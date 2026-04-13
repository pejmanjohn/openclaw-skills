# Triage

Use this page for the first minute of diagnosis and to decide which deeper runbook to open.

## Contents

- First 60 seconds
- Healthy signals
- Fast classification
- Local env and path overrides
- Drift rule

## First 60 seconds

### Step 0: Verify the saved instance still matches reality (Option B)

The preflight step in `SKILL.md` has already loaded `$REPO_ROOT/local/state/instances.json` and announced the chosen target. Step 0's job is to **verify** that the saved instance still matches reality before running deeper diagnostics. We do not re-derive from scratch on every run — that's discovery's job, and discovery already ran (either now via auto-trigger or in a prior session).

This is Option B from the workstream plan: the registry provides the target context, and Step 0 evolves from "derive" to "verify." Live verification still matters; we're just not duplicating discovery's work.

#### What to verify

For the saved default instance from the registry, confirm these still hold:

```bash
# 1. The configured port still matches what's listening
openclaw [--profile X] config get gateway.port
# Compare to instances.json defaultInstance.port

# 2. The active config file still matches
openclaw [--profile X] config file
# Compare to instances.json defaultInstance.configPath

# 3. The service is still registered (macOS)
launchctl list | grep <serviceLabel from instances.json>
```

If all three checks pass, the saved instance is live and Step 0 is done. Proceed to Step 0.5.

#### What to do if verification fails

If any check fails, the saved registry is stale relative to the current machine. **Do not silently rescan.** Tell the user clearly what mismatches you found and suggest re-running `/openclaw-instance-discovery` to refresh:

> Your saved OpenClaw target says it runs on port 18789 with config `~/.openclaw/openclaw.json`, but I'm seeing the gateway on port 18889 with a different config. Want me to rescan to refresh the saved instance map?

Stale-registry auto-refresh is deferred to a later PR. For now, the user explicitly chooses whether to rescan.

#### Notes on bare `openclaw` commands

A bare `openclaw` targets the default profile, which may differ from the saved instance's profile. Always use the `--profile <name>` flag from the saved instance's `profile` field on every command, where `<name>` comes from the registry. If the registry shows `profile: null`, run bare commands.

### Step 0.5: Stop crash loops immediately

If `launchctl list | grep openclaw` shows a non-zero exit code and the service has KeepAlive=true, **stop the service before doing anything else**:

```bash
openclaw [--profile X] gateway stop
# OR on macOS: launchctl bootout gui/$UID/<label>
# OR on Linux: systemctl --user stop <unit>
```

Crash-looping services accumulate failed auth attempts, which triggers dashboard lockout — a secondary problem that outlasts the original issue. Diagnose with the service stopped, fix the root cause, then restart.

### Step 1: Fast diagnostic ladder

Run, in order (with the correct profile flag):

```bash
openclaw [--profile X] --version
openclaw [--profile X] help
openclaw [--profile X] config file
openclaw [--profile X] status
openclaw [--profile X] status --all
openclaw [--profile X] gateway probe
openclaw [--profile X] gateway status
openclaw [--profile X] doctor
openclaw [--profile X] channels status --probe
```

Add `openclaw [--profile X] logs --follow` when the problem is intermittent or the earlier commands only show a generic failure.

## Healthy signals

- `openclaw --version` succeeds and matches the command surface you are using.
- `openclaw config file` points to the expected config path.
- `openclaw status` shows configured channels without obvious auth or startup errors.
- `openclaw gateway probe` reaches the expected target.
- `openclaw gateway status` shows a running runtime and an ok probe.
- `openclaw doctor` reports no blocking config or service issues.
- `openclaw channels status --probe` shows transport state and, where supported, probe or audit success.

## Fast classification

- Gateway does not start, probe fails, or dashboard URL is wrong: go to `gateway.md`.
- Config path is surprising, validation fails, or edits do not take effect: go to `config.md`.
- Transport is connected but messages do not reply or only some senders work: go to `channels.md`.
- Browser tools, exec, or node-backed capabilities fail: go to `tools-and-nodes.md`.
- DM pairing, device approval, shared token mismatch, or stale client auth shows up: go to `auth-and-pairing.md`.
- You already have a specific log line or error string: go to `common-signatures.md`.

## Local env and path overrides

Always check whether local state is being redirected:

- `OPENCLAW_HOME`
- `OPENCLAW_STATE_DIR`
- `OPENCLAW_CONFIG_PATH`
- `OPENCLAW_LOG_LEVEL`

Also check the process environment used by the actual service manager, not just the current shell. On macOS that often means `launchctl`; on Linux it may mean a systemd unit environment or wrapper script. If the CLI and service are reading different homes, state dirs, or config files, fix that before chasing higher-level symptoms.

## Drift rule

If `docs.openclaw.ai` documents a command or flag that the local binary does not have, prefer `openclaw help` and the installed subcommand help output. Treat the docs as guidance for the latest release, not proof of what is installed.
