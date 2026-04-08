# Validation Scenarios

Use these to verify that the skill routes correctly and asks for evidence that can actually confirm or falsify a diagnosis.

## Contents

- Missing command from website docs
- Dashboard opens but cannot authenticate
- Connected channel with no replies
- Config change had no effect
- Node capability fails after pairing

## Scenario: missing command from website docs

Prompt:
"Docs say to run a gateway subcommand, but my local `openclaw` says unknown command."

Pass expectations:

- asks for `openclaw --version`
- asks for `openclaw help` or the local subcommand help output
- states that local CLI availability is runtime truth
- treats `docs.openclaw.ai` as latest-release guidance, not proof of the installed surface

Fail expectations:

- assumes the docs command must exist locally
- tells the user to keep trying website commands without checking local help

## Scenario: dashboard opens but cannot authenticate

Prompt:
"The dashboard loads, but it keeps saying unauthorized."

Pass expectations:

- asks for `openclaw gateway status` and relevant log output
- distinguishes reachability from auth mismatch
- routes to gateway and auth or pairing checks
- suggests a verifiable retry after token or device-state correction

Fail expectations:

- jumps straight to reinstalling OpenClaw
- treats this as a generic network issue with no auth evidence

## Scenario: connected channel with no replies

Prompt:
"WhatsApp looks connected, but the bot ignores a group chat."

Pass expectations:

- asks for `openclaw channels status --probe` and logs
- distinguishes transport from mention, allowlist, and pairing policy
- suggests a specific re-test with a known-good sender or mention pattern

Fail expectations:

- treats connection state as proof that delivery should work
- suggests reconnecting before inspecting logs or policy

## Scenario: config change had no effect

Prompt:
"I edited `~/.openclaw/openclaw.json`, but nothing changed."

Pass expectations:

- asks for `openclaw config file`
- checks env and service-manager overrides
- routes to config validation and runtime truth from local commands

Fail expectations:

- assumes that `~/.openclaw/openclaw.json` is always the active file
- ignores background-service environment differences

## Scenario: node capability fails after pairing

Prompt:
"My node is paired, but browser or camera actions still fail."

Pass expectations:

- distinguishes pairing from permissions and approvals
- routes to `tools-and-nodes.md`
- requests logs or local help output for the exact capability

Fail expectations:

- claims pairing alone proves the node can perform every tool action
