# Gateway

Use this page for gateway runtime, probe, dashboard or Control UI connectivity, auth mode issues, and upgrade-related breakage.

## Contents

- Core checks
- Service and runtime
- Probe and status interpretation
- Dashboard and Control UI
- Auth and token drift
- Upgrade breakage

## Core checks

```bash
openclaw --version
openclaw gateway --help
openclaw gateway probe
openclaw gateway status
openclaw doctor
openclaw logs --follow
```

If the UI is involved, also inspect the dashboard or Control UI target shown by local status output and compare it with the browser URL actually in use.

## Service and runtime

Look for:

- service installed but not running
- probe reaches the wrong host or port
- bind failure, port collision, or auth mode refusal
- runtime starts but immediately exits after config validation or startup checks

When `openclaw doctor` reports a blocking issue, fix that first. Do not assume a UI problem is separate if the gateway runtime is unhealthy.

## Probe and status interpretation

- `probe` tells you whether the expected gateway target is reachable.
- `status` tells you whether the local runtime is alive, which URL it believes it serves, and whether RPC checks are healthy.

If probe succeeds but UI actions still fail, the next branch is usually auth, origin policy, or token drift rather than transport reachability.

## Dashboard and Control UI

Common classes:

- wrong URL, port, or base path
- browser origin not allowed
- insecure HTTP flow blocked because device identity is required
- stale shared token or stale device token
- local runtime upgraded but browser still holds old pairing or auth state

Use local logs to distinguish these. A generic browser failure is not enough evidence.

## Auth and token drift

Look for log signatures that indicate:

- missing token
- token mismatch
- stale device token
- pairing required
- origin not allowed
- device nonce or signature mismatch

If the UI can reach the runtime but gets repeated unauthorized responses, rotate or refresh the relevant auth material before changing transport settings.

## Upgrade breakage

When docs or memory suggest a command path that the local binary does not support:

1. verify the installed version with `openclaw --version`
2. inspect local help for the exact subcommand
3. compare the intended latest workflow from `docs.openclaw.ai`
4. adapt to the installed binary instead of mixing command surfaces

Treat mismatched docs and binary behavior as version drift until proven otherwise.
