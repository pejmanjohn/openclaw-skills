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
- Gateway crash-looping after update
- Doctor fix had no effect on a non-default profile
- Dashboard shows auth lockout after crash loop
- Dashboard shows device token mismatch
- First-time user with no instance registry

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
- checks port alignment between config, service args, and the dashboard URL (see `gateway.md` Port alignment)
- distinguishes dashboard reachability from gateway runtime and auth state
- routes to `gateway.md`
- ends with a concrete reconnect or refresh step tied to a gateway-state check

Fail expectations:

- jumps straight to reinstalling OpenClaw
- treats this as a generic network issue with no gateway evidence
- does not verify the dashboard URL port matches the actual gateway port

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

- resolves active profile first (Step 0) — the edited file may not be the one the service reads
- asks for `openclaw config file` and compares with the service manager's config path
- checks env and service-manager overrides
- routes to config validation and runtime truth from local commands

Fail expectations:

- assumes that `~/.openclaw/openclaw.json` is always the active file
- ignores background-service environment differences
- does not check profile resolution

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

## Scenario: gateway crash-looping after update

Prompt:
"My gateway won't start after an update. launchctl shows it keeps restarting with exit code 1."

Pass expectations:

- stops the crash-looping service immediately before further diagnosis (Step 0.5)
- resolves the active profile before running any openclaw commands (Step 0)
- checks the service manager's error output or log path for the crash reason
- routes to `common-signatures.md` and `gateway.md`
- checks `playbooks/incident-log.md` for matching patterns
- ends with a fix-then-restart sequence, not a restart-then-fix sequence

Fail expectations:

- runs diagnostic commands while the service continues to crash-loop
- attempts to restart the service before identifying the crash reason
- ignores profile resolution and runs bare openclaw commands

## Scenario: doctor fix had no effect on a non-default profile

Prompt:
"I ran `openclaw doctor --fix` but the gateway still won't start with the same config error."

Pass expectations:

- checks which profile the gateway service uses (Step 0)
- compares `openclaw config file` output with the service manager's config path
- identifies that doctor may have fixed a different profile's config
- re-runs doctor with the correct `--profile` flag
- verifies the config file was actually modified after the fix
- routes to `config.md` and `common-signatures.md`

Fail expectations:

- re-runs `openclaw doctor --fix` without a profile flag and expects a different result
- does not verify the target config file was actually modified
- assumes `~/.openclaw/openclaw.json` is the only config file

## Scenario: dashboard shows auth lockout after crash loop

Prompt:
"Dashboard says 'too many failed authentication attempts (retry later)' and I can't connect."

Pass expectations:

- identifies this as an in-memory rate limit, not a permanent auth failure
- checks whether the gateway was recently crash-looping (which accumulates failed attempts)
- stops the gateway, fixes any underlying issue, restarts to clear the lockout
- routes to `common-signatures.md` and `gateway.md`

Fail expectations:

- treats this as a permanent auth or token problem requiring rotation
- waits for a timeout to expire without addressing the underlying crash cause
- does not check for crash-loop history before attempting auth fixes

## Scenario: dashboard shows device token mismatch

Prompt:
"The dashboard page loads but shows 'device token mismatch (rotate/reissue device token)' when I try to connect."

Pass expectations:

- recommends using `openclaw [--profile X] dashboard` to get a tokenized URL instead of connecting manually
- verifies the port in the generated URL matches the actual gateway listening port
- checks for port alignment issues between config, service args, and dashboard URL
- routes to `gateway.md` (Port alignment and Dashboard sections)

Fail expectations:

- manually rotates device tokens without first checking the dashboard URL and port
- treats this as a pairing issue without verifying basic connectivity and port match

## Scenario: first-time user with no instance registry

Prompt:
"openclaw is broken"

(Run on a Mac where `local/state/instances.json` does not exist yet. The user is a non-technical first-time user.)

Pass expectations:

- recognizes the vague phrasing as a troubleshooting trigger (matches the natural-language description)
- on activation, attempts to load `<repo-root>/local/state/instances.json` and finds it missing
- automatically hands off to `openclaw-instance-discovery` without asking the user to invoke a separate command
- discovery runs the 6-phase sequence silently and produces a draft machine model
- in the single-instance common case, auto-saves the registry with `id` and `label` both set to `default` and asks no questions
- in the multi-instance case, presents candidates in plain language with neutral descriptions like "default launchd service on port 18789" (not "your prod install")
- after writing the registry, returns control to the troubleshooting skill
- troubleshooting announces the chosen target in plain language before any deeper diagnostics, including the `discoveredFrom` evidence string for trust
- only then proceeds to the actual troubleshooting work the user originally asked for

Fail expectations:

- asks the user "which OpenClaw install should I use?" without first attempting discovery
- refuses to act because the registry is missing
- writes an empty or invalid registry and proceeds blindly
- guesses human semantics like "I'll target your prod install" without evidence
- silently inherits state from no registry without announcing the target
- runs deeper diagnostics before announcing what it's targeting
