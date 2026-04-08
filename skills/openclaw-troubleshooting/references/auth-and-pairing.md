# Auth And Pairing

Use this page when the failure is about who is allowed to connect or act, rather than whether transport exists.

## Contents

- Common branches
- DM pairing
- Device pairing
- Token mismatch
- launchctl and service env overrides

## Common branches

- DM pairing pending or denied
- device pairing pending or revoked
- shared token mismatch
- stale device token
- secure-context requirements for browser auth
- service manager loading a different environment than the shell

## DM pairing

When message delivery stalls because a sender is unknown:

- confirm the channel is connected
- inspect logs for pairing-required language
- inspect the locally available pairing list or approval commands
- approve the right sender, then rerun the same message path

Do not reconnect the channel before approval state is clear.

## Device pairing

For dashboard, Control UI, or device-backed flows:

- confirm the installed CLI has the expected device commands with local help
- inspect whether the device is known, pending, revoked, or stale
- rotate or reapprove the specific device token when mismatch symptoms repeat

## Token mismatch

If the gateway is reachable but auth fails:

- compare the client token source with the current gateway token source
- check whether the browser or client cached an old token
- verify that a service restart did not pick up a different config or env source than the shell

Repeated unauthorized responses after reconnect attempts usually point to token drift, not reachability.

## launchctl and service env overrides

The active runtime may inherit env vars from a service manager rather than the current terminal. Check:

- `OPENCLAW_HOME`
- `OPENCLAW_STATE_DIR`
- `OPENCLAW_CONFIG_PATH`
- auth or API-key env vars from launchctl, systemd, or wrapper scripts

If shell commands succeed but the background service behaves differently, compare those environments before making any product-level conclusions.
