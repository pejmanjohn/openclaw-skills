# Channels

Use this page when a channel appears configured or connected but delivery is wrong, missing, or inconsistent.

## Contents

- Transport versus delivery
- Core checks
- Allowlists and mention gating
- Pairing
- Connected but no replies

## Transport versus delivery

Separate these questions:

- Is the transport connected?
- Is the sender or room allowed?
- Is a mention required?
- Is pairing required and still pending?
- Is the message reaching the gateway but being intentionally dropped by policy?

A connected transport does not prove delivery is allowed.

## Core checks

```bash
openclaw status
openclaw channels status --probe
openclaw config get channels
openclaw logs --follow
```

If pairing is relevant, add the local pairing help or list command surface supported by the installed binary.

## Allowlists and mention gating

Common causes of connected-but-no-replies:

- sender not in `allowFrom`
- room, guild, or group allowlist mismatch
- group reply requires a mention
- mention pattern mismatch
- policy changed in config but the service is reading another config file

Look for log lines that explicitly say the message was blocked, dropped, filtered, or required a mention.

## Pairing

Pairing is a policy decision, not a transport failure. If logs show pending pairing or approval required, route to `auth-and-pairing.md` and resolve approval state before reconnecting anything.

## Connected but no replies

Use this logic:

1. confirm transport health with `channels status --probe`
2. confirm gateway health with `gateway status`
3. inspect logs for block, allowlist, mention, or pairing language
4. verify the sender and target in config
5. rerun with a known-good sender or room after the smallest policy fix

Avoid broad reconnect steps until policy-based filtering is ruled out.
