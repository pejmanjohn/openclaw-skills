# Triage

Use this page for the first minute of diagnosis and to decide which deeper runbook to open.

## Contents

- First 60 seconds
- Healthy signals
- Fast classification
- Local env and path overrides
- Drift rule

## First 60 seconds

### Step 0: Resolve active profile (MANDATORY)

Before ANY `openclaw` command, determine which profile the gateway actually runs under. A bare `openclaw` targets the default profile, which may be different from the service profile.

```bash
# What does the CLI think?
openclaw config file

# What does the launchd service actually use? (macOS)
launchctl list | grep openclaw
# Inspect the plist for profile and state-dir overrides:
grep -A1 "OPENCLAW_PROFILE\|OPENCLAW_STATE_DIR\|OPENCLAW_CONFIG_PATH" ~/Library/LaunchAgents/ai.openclaw.*.plist

# On Linux, check the systemd unit environment instead:
# systemctl --user show openclaw-gateway | grep -i "environment\|openclaw"
```

If the service uses a different profile or state directory than the CLI default, ALL subsequent commands in this triage need the matching `--profile <name>` flag.

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
