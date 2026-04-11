---
name: openclaw-troubleshooting
description: Use when OpenClaw install/setup, gateway, dashboard/control UI, no-replies channels, auth/pairing, config, exec approvals, tool/node, or plugins need troubleshooting, diagnosis, repair, or safe reconfiguration.
---

# OpenClaw Troubleshooting

Treat the local machine as the primary evidence source. The agent and OpenClaw run on the same host, so local CLI output, config files, runtime state, and logs are runtime truth. Treat `docs.openclaw.ai` as procedural truth for the latest release, but verify every command and flag against the installed binary because website docs may be ahead of the local version.

## Quick start

- **FIRST: Resolve the active profile.** Check `openclaw config file` AND the service manager env vars (`OPENCLAW_PROFILE`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`). If they differ, use `--profile <X>` on every command. See `playbooks/triage.md` Step 0.
- **If crash-looping:** Stop the service immediately before diagnosing. Crash loops accumulate auth lockout.
- **Check past incidents:** Read `playbooks/incident-log.md` (shipped patterns) AND `playbooks/local/incident-log.md` (if it exists — environment-specific learnings) before starting fresh diagnosis.
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

## Workflow

0. **Resolve profile and stop any crash loops** — see Quick start. This is non-negotiable.
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
- `playbooks/common-signatures.md` -> terse log or error signature to next action lookup. Also check `playbooks/local/common-signatures.md` if it exists.
- `playbooks/validation-scenarios.md` -> scenario prompts with pass or fail expectations for trigger choice, evidence gathering, routing, and verifiable next steps.
- `playbooks/incident-log.md` -> general post-incident patterns (shipped with repo). Also check `playbooks/local/incident-log.md` for environment-specific learnings from past sessions on this machine.

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
