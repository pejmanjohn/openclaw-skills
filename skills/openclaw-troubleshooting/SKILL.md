---
name: openclaw-troubleshooting
description: Use when OpenClaw is failing or behaving unexpectedly and you need a canonical, local-first troubleshooting path for gateway, dashboard, channels, auth, pairing, config, tools, nodes, or plugins.
---

# OpenClaw Troubleshooting

Treat the local machine as the primary evidence source. The agent and OpenClaw run on the same host, so local CLI output, config files, runtime state, and logs are runtime truth. Treat `docs.openclaw.ai` as procedural truth for the latest release, but verify every command and flag against the installed binary because website docs may be ahead of the local version.

## Quick start

- Confirm the installed build and local command surface first: `openclaw --version`, `openclaw help`, `openclaw <subcommand> --help`.
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

1. Verify local version and command availability with `openclaw --version`, `openclaw help`, and the specific `openclaw <subcommand> --help` pages you plan to use.
2. Find the active config path with `openclaw config file`, then inspect local config, env overrides, launchctl or service environment, and current logs before changing anything.
3. Classify the problem quickly: gateway/runtime, dashboard or Control UI, channels and delivery, auth or pairing, config validation, tools, nodes, or plugin surface.
4. Prefer local runtime truth when local output conflicts with memory or website docs. If `docs.openclaw.ai` shows a newer command flow, adapt it to the locally installed command surface instead of assuming the docs are wrong or the binary is broken.
5. Make the smallest reversible fix, rerun the exact failing command, and capture the before and after evidence.

## Reference map

Read only the file that matches the observed symptom:

- `references/triage.md` -> first 60 seconds, healthy signals, fast classification, local env and path overrides.
- `references/gateway.md` -> gateway runtime, probe and status, dashboard and Control UI, auth modes, token drift, upgrade breakage.
- `references/config.md` -> active config path, schema and validation, safe edits, `config get`, `config schema`, `config validate`, env override confusion.
- `references/channels.md` -> transport versus delivery, allowlists, mentions, pairing, connected-but-no-replies routing.
- `references/tools-and-nodes.md` -> exec approvals, browser failures, tool routing, and node pairing versus permissions versus approvals.
- `references/auth-and-pairing.md` -> DM pairing, device pairing, token mismatch, launchctl or daemon env overrides.
- `references/common-signatures.md` -> terse log or error signature to next action lookup.
- `references/validation-scenarios.md` -> scenario prompts with pass or fail expectations for trigger choice, evidence gathering, routing, and verifiable next steps.

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
