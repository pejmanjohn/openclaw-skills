---
name: openclaw-troubleshooting
description: Use when OpenClaw install/setup, gateway, dashboard/control UI, channels, auth/pairing, config, exec approvals, tool/node, or plugins need troubleshooting, diagnosis, repair, or safe reconfiguration. Also triggers on natural-language phrasings like "openclaw isn't working", "openclaw isn't responding", "my agents aren't replying" or "not replying", "the dashboard won't load", "openclaw won't start", "fix my openclaw", "something's wrong with openclaw". Auto-loads the saved instance registry from local/state/instances.json on activation; auto-triggers openclaw-instance-discovery if the registry is missing.
---

# OpenClaw Troubleshooting

Treat the local machine as the primary evidence source. The agent and OpenClaw run on the same host, so local CLI output, config files, runtime state, and logs are runtime truth. Treat `docs.openclaw.ai` as procedural truth for the latest release, but verify every command and flag against the installed binary because website docs may be ahead of the local version.

## Quick start

- **PREFLIGHT — Load the instance registry.** Read `<repo-root>/local/state/instances.json` (the repo root is two directories up from this SKILL.md, even when invoked through a symlinked install). If the file is missing, unreadable, or malformed, **auto-trigger `openclaw-instance-discovery`** before doing anything else. After discovery writes the registry, resume here. Then announce the chosen target in plain language to the user before any further diagnostics — see the "Announce target" section below.
- **FIRST: Resolve the active profile.** Check `openclaw config file` AND the service manager env vars (`OPENCLAW_PROFILE`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`). If they differ, use `--profile <X>` on every command. See `playbooks/triage.md` Step 0.
- **If crash-looping:** Stop the service immediately before diagnosing. Crash loops accumulate auth lockout.
- **Check past incidents:** Read `playbooks/incident-log.md` (shipped patterns) AND `<repo-root>/local/memory/incident-log.md` (if it exists — environment-specific learnings) before starting fresh diagnosis. The repo root is two directories up from this SKILL.md (`../../`), even when invoked through a symlinked install.
- Confirm the installed build and local command surface: `openclaw --version`, `openclaw help`, `openclaw <subcommand> --help`.
- Locate the active config before diagnosing behavior: `openclaw config file`.
- Run the fast ladder in order and stop when the failure class is obvious:
  `openclaw status`
  `openclaw status --all`
  `openclaw gateway probe`
  `openclaw gateway status`
  `openclaw doctor`
  `openclaw channels status --probe`
- Use `openclaw logs --follow` when you need the live error signature, timing, or confirmation that a fix changed behavior.

## Announce target

After loading the registry (and after auto-triggering discovery if needed), state in plain language which OpenClaw instance you are about to operate on. This is non-negotiable. Never silently inherit state from a saved registry.

Single-instance announcement:

> I'm targeting the OpenClaw I found on this Mac:
> - port 18789
> - config `~/.openclaw/openclaw.json`
> - service `ai.openclaw.gateway`

Multi-instance announcement:

> I'm targeting your saved default OpenClaw:
> - label `default`
> - port 18789
> - config `~/.openclaw/openclaw.json`
>
> If you want me to use the other one instead, say `use the other one`.

The instance details should come from the registry's `discoveredFrom`, `port`, `configPath`, and `serviceLabel` fields for the saved default instance.

## Override grammar

The user can switch the active target at any point in the conversation with one of these phrases:

- `use the other one` — switch to the next instance in the registry that isn't the current target
- `use <label>` — switch to the instance with the matching `label` field
- `use the one on <port>` — switch to the instance with the matching `port` field

After an override, restate the new target clearly using the same plain-language announcement format above. Then continue troubleshooting against the new target.

## Workflow

0. **Preflight: load the instance registry, auto-trigger discovery if needed, and announce the target.** Then resolve profile and stop any crash loops — see Quick start and the Announce target section. This is non-negotiable. Without a known target, every other step risks operating on the wrong install.
1. Verify local version and command availability with `openclaw --version`, `openclaw help`, and the specific `openclaw <subcommand> --help` pages you plan to use.
2. Find the active config path with `openclaw config file`, then inspect local config, env overrides, launchctl or service environment, and current logs before changing anything.
3. Classify the problem quickly: gateway/runtime, dashboard or Control UI, channels and delivery, auth or pairing, config validation, tools, nodes, or plugin surface.
4. Prefer local runtime truth when local output conflicts with memory or website docs. If `docs.openclaw.ai` shows a newer command flow, adapt it to the locally installed command surface instead of assuming the docs are wrong or the binary is broken.
5. Make the smallest reversible fix, rerun the exact failing command, and capture the before and after evidence.

## Reference map

Read only the file that matches the observed symptom:

- `playbooks/triage.md` -> first 60 seconds, healthy signals, fast classification, local env and path overrides.
- `playbooks/gateway.md` -> gateway runtime, probe and status, dashboard and Control UI, auth modes, token drift, upgrade breakage.
- `playbooks/config.md` -> active config path, schema and validation, safe edits, `config get`, `config schema`, `config validate`, env override confusion.
- `playbooks/channels.md` -> transport versus delivery, allowlists, mentions, pairing, connected-but-no-replies routing.
- `playbooks/tools-and-nodes.md` -> exec approvals, browser failures, tool routing, and node pairing versus permissions versus approvals.
- `playbooks/auth-and-pairing.md` -> DM pairing, device pairing, token mismatch, launchctl or daemon env overrides.
- `playbooks/common-signatures.md` -> terse log or error signature to next action lookup. Also check `<repo-root>/local/memory/common-signatures.md` if it exists.
- `playbooks/validation-scenarios.md` -> scenario prompts with pass or fail expectations for trigger choice, evidence gathering, routing, and verifiable next steps.
- `playbooks/incident-log.md` -> general post-incident patterns (shipped with repo). Also check `<repo-root>/local/memory/incident-log.md` for environment-specific learnings from past sessions on this machine.

## After resolving an incident

Once the issue is confirmed fixed, suggest running `/openclaw-troubleshooting-compound` to capture learnings. That skill reviews the conversation, drafts a structured incident-log entry (and any new error signatures), and applies them on user confirmation. This keeps the incident log growing without requiring the user to write anything manually.

## Quality rules

- Start from live diagnostics and local artifacts, not remembered docs.
- Keep the top-level skill lean; put detailed troubleshooting branches in the reference files.
- Cite exact local commands, paths, and log signatures when proposing a fix.
- If local output and `docs.openclaw.ai` differ, state the version drift explicitly and prefer the installed binary for runtime behavior.
- Do not claim a fix without rerunning the relevant command or scenario.

## Tooling/fallback notes

- Prefer shell inspection of local config, logs, service state, and command help before browsing docs.
- Use `docs.openclaw.ai` to understand the latest intended workflow, migration notes, or renamed commands, then verify those steps locally with `openclaw help`.
- If a documented command is unavailable locally, fall back to the nearest installed help surface and record the mismatch as version drift rather than forcing the website procedure verbatim.
