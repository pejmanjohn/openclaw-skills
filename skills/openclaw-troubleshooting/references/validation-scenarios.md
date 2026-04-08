# Validation Scenarios

Use these to verify that the skill routes correctly and asks for evidence that can actually confirm or falsify a diagnosis.

## Contents

- Missing command from website docs
- OpenClaw installed but no replies on Telegram
- Dashboard opens but will not connect
- Exec suddenly asks for approval
- Safe config change and validation
- Gateway says unauthorized
- Config change had no effect
- Node capability fails after pairing
- Plugin install missing openclaw.extensions

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

## Scenario: OpenClaw installed but no replies on Telegram

Prompt:
"OpenClaw is installed but I am getting no replies on Telegram."

Pass expectations:

- asks for `openclaw channels status --probe`
- requests the relevant Telegram logs or the matching `openclaw logs --follow` window
- distinguishes transport from mention, allowlist, webhook, pairing, and delivery policy
- routes to `channels.md`
- ends with a specific re-test such as a direct message or a known-good group mention

Fail expectations:

- treats a connected channel as proof that replies should flow
- suggests reinstalling before checking channel status, policy, or logs

## Scenario: dashboard opens but will not connect

Prompt:
"The dashboard opens but will not connect."

Pass expectations:

- asks for `openclaw gateway probe`, `openclaw gateway status`, or the relevant gateway logs
- distinguishes dashboard reachability from gateway runtime and auth state
- routes to `gateway.md`
- ends with a concrete reconnect or refresh step tied to a gateway-state check

Fail expectations:

- jumps straight to reinstalling OpenClaw
- treats this as a generic network issue with no gateway evidence

## Scenario: exec suddenly asks for approval

Prompt:
"Why is exec suddenly asking for approval?"

Pass expectations:

- asks for the exact failing action and any matching log output
- distinguishes approval policy drift from pairing or generic tool failure
- routes to `tools-and-nodes.md`
- ends with a verifiable next check such as retrying the same exec path after inspecting approvals state

Fail expectations:

- treats the issue as a shell bug without checking approvals or policy
- suggests broad config changes with no evidence

## Scenario: safe config change and validation

Prompt:
"How do I safely change OpenClaw config and validate it?"

Pass expectations:

- starts with `openclaw config file`
- uses `openclaw config get`, `openclaw config schema`, and `openclaw config validate`
- routes to `config.md`
- prefers the smallest reversible edit and ends with a validation command

Fail expectations:

- tells the user to hand-edit `~/.openclaw/openclaw.json` without checking the active file
- claims success without validation output

## Scenario: gateway says unauthorized

Prompt:
"Gateway says unauthorized even though my config looks right."

Pass expectations:

- asks for `openclaw gateway status`, `openclaw gateway probe`, and the exact unauthorized log line
- distinguishes auth mismatch from config syntax or transport failure
- routes to `gateway.md` and `auth-and-pairing.md`
- ends with a specific re-check after correcting the token or device state

Fail expectations:

- treats the issue as a generic dashboard problem with no gateway evidence
- recommends random token rotation without first checking local runtime state

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

## Scenario: plugin install missing openclaw.extensions

Prompt:
"Plugin install fails with missing openclaw.extensions."

Pass expectations:

- asks for the exact install command and the plugin error output
- identifies this as a plugin metadata or packaging issue rather than a generic OpenClaw reinstall problem
- routes to `common-signatures.md` and the plugin-related guidance in `tools-and-nodes.md`
- ends with a concrete next diagnostic or repair step tied to the plugin package metadata

Fail expectations:

- treats this as proof that the whole OpenClaw install is broken
- invents undocumented plugin recovery steps with no error evidence
