# Health check

This is the babysit skill's read-only health check. It runs every tick and produces a verdict: `healthy` or `degraded`, with structured evidence.

The success criterion is **channels are reachable**, not "the gateway process is alive." A gateway with all channels crash-looping is degraded even if probe returns `ok` — the user can't reach their agents.

## Inputs

The check assumes the active instance is already resolved (see SKILL.md preflight). It needs:

- The instance's `configPath` (to read enabled channels)
- The instance's `serviceLabel` (for `launchctl list`)
- The instance's gateway `port` (for the probe)
- The previous tick's `lastRunsCounter` (to detect crash loops)

## Signals

The check reads these signals in order. Stop early when a clearly-degraded signal fires; stop early when a clearly-healthy composite is established.

### S1. Enabled channel set (from config)

Read `<configPath>` and enumerate channels where `channels.<name>.enabled === true`. This is the *expected* set — anything else (a channel disabled in config) is not babysit's concern.

```bash
jq -r '.channels | to_entries[] | select(.value.enabled == true) | .key' "$CONFIG_PATH"
```

If the config is unreadable or the jq filter throws, treat the tick as degraded with `evidence.config = "unreadable"` and stop. This is unusual and worth alerting on.

### S2. Gateway probe

```bash
openclaw gateway probe
```

A `Connect: ok` line is *necessary but not sufficient* for healthy. Probe failures are degraded immediately; probe success continues to S3.

### S3. `openclaw doctor` per-channel statuses

```bash
openclaw doctor 2>&1
```

Parse lines of the form `<Channel>: ok` or `<Channel>: <error>`. Cross-reference against the enabled channel set from S1:

- Every enabled channel must report `ok`.
- A channel reporting an error is a strong degraded signal.
- A channel in S1 not appearing in doctor output at all is also degraded (channel failed to register).
- A channel in doctor output not in S1 is fine — it just isn't enabled in the user's config.

Doctor's exit code is also informative: non-zero is degraded.

### S4. Recent log scan for channel-level errors

```bash
LOG=$(ls -t /tmp/openclaw/openclaw-*.log 2>/dev/null | head -1)
[ -n "$LOG" ] && tail -500 "$LOG" | python3 -c "$SCAN_SCRIPT"
```

The scan looks for lines from the last ~30 seconds matching:

- `channel exited:` (any subsystem under `gateway/channels/`)
- `auto-restart attempt N/10` (channel auto-restart in progress)
- `Unhandled promise rejection` (any subsystem)

Window is 30 seconds because:
- Long enough to catch active crash loops (~5s typical channel restart cadence)
- Short enough that stale errors from a prior incident don't keep the loop pinned to "degraded" forever

Any of these in the window is a degraded signal. The crash-loop indicators are the strongest — they confirm the channel is *currently* failing, not that it failed once an hour ago.

### S5. launchctl runs counter

```bash
launchctl list "$SERVICE_LABEL" | grep -E '"runs"|"LastExitStatus"'
```

Compare current `runs` to `state.lastRunsCounter`:

- Equal: no gateway restart since last tick (good).
- Greater: gateway restarted at least once since last tick. If the previous tick was healthy and we didn't trigger a fix, this means the gateway crashed on its own — strong degraded signal even if S2/S3/S4 currently look ok.
- First tick (no prior counter): record current value, do not flag as degraded on this signal.

`LastExitStatus != 0` is also a degraded signal regardless of `runs` delta.

## Verdict

Combine signals into a verdict:

| Composite | Verdict |
| --- | --- |
| S2 ok, S3 all enabled channels ok, S4 clean, S5 stable, exit codes 0 | healthy |
| Any of S2/S3/S5 fails, OR S4 shows current crash activity, OR config unreadable | degraded |
| S2 ok but S3 has any channel error AND S4 shows active auto-restart | degraded (strong) |

The "strong" qualifier is informational — it tells the auto-fix loop that the diagnosis is more likely to match an unambiguous allowlist signature.

## Evidence shape

Health check returns a structured result the rest of the skill can reason over:

```json
{
  "status": "degraded",
  "expectedChannels": ["slack", "discord", "telegram", "bluebubbles"],
  "doctor": {
    "exitCode": 0,
    "channels": { "slack": "error: ...", "discord": "ok", "telegram": "ok", "bluebubbles": "ok" }
  },
  "probe": "ok",
  "recentLogActivity": {
    "channelExited": ["slack"],
    "autoRestartAttempts": ["slack"],
    "unhandledRejections": []
  },
  "launchctl": { "runs": 3, "lastExitStatus": 0, "delta": 1 },
  "primarySignature": "channel exited: The requested module 'openclaw/plugin-sdk/ssrf-runtime' does not provide an export named 'fetchWithSsrFGuard'"
}
```

`primarySignature` is the single most distinctive log line found, copied verbatim. It's what gets passed to `/openclaw-troubleshooting` as the diagnosis hint when in auto-fix mode.

## What this check does NOT do

- **Synthetic message ping.** Sending a real message through Slack/Telegram and checking for delivery would be a stronger signal but introduces noise (real messages in real channels) and requires a designated test endpoint. Out of scope for v1.
- **`openclaw status` parsing.** The CLI `status` command can throw on unresolved SecretRefs even when channels are actually healthy — it tries to scan raw config rather than asking the running gateway for resolved values. Doctor is the reliable per-channel signal; status is not, until that CLI behavior changes.
- **Cross-channel dependencies.** If channels share an upstream (e.g. all routing through a common plugin SDK), the health check reports each channel independently — diagnosis is the troubleshooting skill's job, not the health check's.
