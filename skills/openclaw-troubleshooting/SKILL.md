---
name: openclaw-troubleshooting
description: Use when OpenClaw install/setup, gateway, dashboard/control UI, channels, auth/pairing, config, exec approvals, tool/node, or plugins need troubleshooting, diagnosis, repair, or safe reconfiguration. Also triggers on natural-language phrasings like "openclaw isn't working", "openclaw isn't responding", "my agents aren't replying" or "not replying", "the dashboard won't load", "openclaw won't start", "fix my openclaw", "something's wrong with openclaw". Auto-loads the saved instance registry from local/state/instances.json on activation; auto-triggers openclaw-instance-discovery if the registry is missing.
---

# OpenClaw Troubleshooting

Treat the local machine as the primary evidence source. The agent and OpenClaw run on the same host, so local CLI output, config files, runtime state, and logs are runtime truth. Treat `docs.openclaw.ai` as procedural truth for the latest release, but verify every command and flag against the installed binary because website docs may be ahead of the local version.

## Finding the repo root

**IMPORTANT:** The repo root is NOT your current working directory. It is the directory where the skill source checkout lives on disk. You must resolve it before reading or writing any `local/` path.

Run this command to find it:

```bash
REPO_ROOT=""
for d in \
  ~/.claude/skills/openclaw-instance-discovery \
  ~/.claude/skills/openclaw-troubleshooting \
  ~/.openclaw/skills/openclaw-troubleshooting \
  ~/.codex/skills/openclaw-troubleshooting \
  ~/src/openclaw-skills/skills/openclaw-troubleshooting; do
  if [ -e "$d" ]; then
    resolved="$(readlink "$d" 2>/dev/null || echo "$d")"
    candidate="$(cd "$resolved/../.." 2>/dev/null && pwd)"
    if [ -d "$candidate/local" ] && [ -d "$candidate/skills" ]; then
      REPO_ROOT="$candidate"
      break
    fi
  fi
done
echo "${REPO_ROOT:?Could not find openclaw-skills repo root}"
```

The result must contain both `local/` and `skills/` directories. Use `$REPO_ROOT` for all paths below.

## Quick start

- **PREFLIGHT — Load the instance registry.** Read `$REPO_ROOT/local/state/instances.json` (see "Finding the repo root" above — the repo root is NOT your CWD). If the file is missing, unreadable, or malformed, **auto-trigger `openclaw-instance-discovery`** before doing anything else. After discovery writes the registry, resume from the SECOND bullet below ("FIRST: Resolve the active profile"). Then announce the chosen target in plain language — see the "STOP — Announce target" section below.
- **FIRST: Resolve the active profile.** Check `openclaw config file` AND the service manager env vars (`OPENCLAW_PROFILE`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`). If they differ, use `--profile <X>` on every command. See `playbooks/triage.md` Step 0.
- **If crash-looping:** Stop the service immediately before diagnosing. Crash loops accumulate auth lockout.
- **Check past incidents:** Read `playbooks/incident-log.md` (shipped patterns) AND `$REPO_ROOT/local/memory/incident-log.md` (if it exists — environment-specific learnings) before starting fresh diagnosis.
- Confirm the installed build and local command surface: `openclaw --version`, `openclaw help`, `openclaw <subcommand> --help`.
- **When docs are needed:** Use `playbooks/docs-navigation.md` to find the right OpenClaw doc page quickly. The docs contain frontmatter like `summary` and `read_when` that help you locate the right page semantically instead of browsing randomly.
- Locate the active config before diagnosing behavior: `openclaw config file`.
- Run the fast ladder in order and stop when the failure class is obvious:
  `openclaw status`
  `openclaw status --all`
  `openclaw gateway probe`
  `openclaw gateway status`
  `openclaw doctor`
  `openclaw channels status --probe`
- Use `openclaw logs --follow` when you need the live error signature, timing, or confirmation that a fix changed behavior.

## STOP — Announce the target before ANY diagnostic work

**Before running ANY `openclaw` command, before reading ANY log file, before doing ANY diagnostic work, you MUST announce the target.**

If you have not produced the announcement below, you have skipped the preflight. Go back to the Quick start and complete it.

1. Load the registry from `$REPO_ROOT/local/state/instances.json` (auto-trigger discovery if the file is missing — see Quick start PREFLIGHT bullet)
2. Read the default instance from the registry
3. State the target using this exact format:

Single-instance announcement:

> I'm targeting the OpenClaw I found on this Mac:
> - port [port from registry]
> - config [configPath from registry]
> - service [serviceLabel from registry]
> - evidence: [discoveredFrom from registry]

Multi-instance announcement:

> I'm targeting your saved default OpenClaw:
> - label [label from registry]
> - port [port from registry]
> - config [configPath from registry]
>
> If you want me to use the other one instead, say `use the other one`.

4. **Only THEN** proceed to the diagnostic ladder, crash-loop checks, or any other troubleshooting work.

Do not skip this step. Do not abbreviate it. Do not fold it into other output. The announcement must be a clear, standalone statement before any diagnostics begin.

## Override grammar

The user can switch the active target at any point in the conversation with one of these phrases:

- `use the other one` — switch to the next instance in the registry that isn't the current target
- `use <label>` — switch to the instance with the matching `label` field
- `use the one on <port>` — switch to the instance with the matching `port` field

After an override, restate the new target clearly using the same plain-language announcement format above. Then continue troubleshooting against the new target.

## Do NOT write to Claude Code's memory system

Troubleshooting data — target selection, diagnostic results, instance information — lives ONLY in the skill repo's `local/` directory (specifically `$REPO_ROOT/local/state/instances.json` for the registry). Do NOT write troubleshooting or instance data to Claude Code's memory system (`memory/`, `MEMORY.md`, or any workspace memory files). These are different systems with different purposes.

## Read-only discipline

**Diagnosis is read-only. Do NOT modify config, disable plugins, restart services, or make any changes to the OpenClaw installation during diagnosis.**

Troubleshooting has two distinct phases:

1. **Diagnose** (read-only) — gather evidence, classify the problem, identify the root cause. Run commands that READ state (`openclaw status`, `openclaw config file`, `openclaw gateway probe`, `openclaw doctor`, log inspection). Do NOT run commands that WRITE state (`openclaw config set`, `openclaw gateway stop/start`, `openclaw plugin disable`, etc.).

2. **Repair** (requires explicit user approval) — propose a specific fix, explain what it will change, and **WAIT for the user to say yes** before executing it.

**Never skip from diagnosis to repair without asking.** Even if the fix seems obvious. Even if the user said "fix my openclaw." A broad troubleshooting prompt is NOT authorization to make config changes.

Example of correct behavior:

> I found that `plugins.entries.slack.enabled` is `true` but the Slack transport is failing with a connection error. One possible fix is to disable the Slack plugin temporarily while we investigate. Want me to run `openclaw config set plugins.entries.slack.enabled false`?

Example of WRONG behavior:

> I found a Slack plugin issue and disabled it. `plugins.entries.slack.enabled` is now `false`.

The second example is wrong because it made a config change without asking. Do not do this.

## Workflow

0. **Preflight: load the instance registry, auto-trigger discovery if needed, and announce the target.** Then resolve profile and stop any crash loops — see Quick start and the STOP — Announce target section. This is non-negotiable. Without a known target, every other step risks operating on the wrong install.
1. Verify local version and command availability with `openclaw --version`, `openclaw help`, and the specific `openclaw <subcommand> --help` pages you plan to use.
2. Find the active config path with `openclaw config file`, then inspect local config, env overrides, launchctl or service environment, and current logs before changing anything.
3. Classify the problem quickly: gateway/runtime, dashboard or Control UI, channels and delivery, auth or pairing, config validation, tools, nodes, or plugin surface.
4. Prefer local runtime truth when local output conflicts with memory or website docs. If `docs.openclaw.ai` shows a newer command flow, adapt it to the locally installed command surface instead of assuming the docs are wrong or the binary is broken.
5. **STOP and present your diagnosis.** Tell the user what you found, what you think the root cause is, and what you recommend as a fix. **Wait for explicit approval before making any changes.** Do not proceed to step 6 without a clear "yes" or equivalent from the user.
6. Make the smallest reversible fix the user approved, rerun the exact failing command, and capture the before and after evidence.

## Reference map

Read only the file that matches the observed symptom:

- `playbooks/triage.md` -> first 60 seconds, healthy signals, fast classification, local env and path overrides.
- `playbooks/gateway.md` -> gateway runtime, probe and status, dashboard and Control UI, auth modes, token drift, upgrade breakage.
- `playbooks/config.md` -> active config path, schema and validation, safe edits, `config get`, `config schema`, `config validate`, env override confusion.
- `playbooks/channels.md` -> transport versus delivery, allowlists, mentions, pairing, connected-but-no-replies routing.
- `playbooks/tools-and-nodes.md` -> exec approvals, browser failures, tool routing, and node pairing versus permissions versus approvals.
- `playbooks/auth-and-pairing.md` -> DM pairing, device pairing, token mismatch, launchctl or daemon env overrides.
- `playbooks/common-signatures.md` -> terse log or error signature to next action lookup. Also check `$REPO_ROOT/local/memory/common-signatures.md` if it exists.
- `playbooks/validation-scenarios.md` -> scenario prompts with pass or fail expectations for trigger choice, evidence gathering, routing, and verifiable next steps.
- `playbooks/incident-log.md` -> general post-incident patterns (shipped with repo). Also check `$REPO_ROOT/local/memory/incident-log.md` for environment-specific learnings from past sessions on this machine.
- `playbooks/docs-navigation.md` -> how to locate the right OpenClaw doc page using docs frontmatter (`summary`, `read_when`, `title`) before browsing or grepping blindly.

## After resolving an incident

Once the issue is confirmed fixed, suggest running `/openclaw-troubleshooting-compound` to capture learnings. That skill reviews the conversation, drafts a structured incident-log entry (and any new error signatures), and applies them on user confirmation. This keeps the incident log growing without requiring the user to write anything manually.

## Quality rules

- **Never modify config, services, or plugins without explicit user approval.** See "Read-only discipline" above. This is the most important quality rule.
- Start from live diagnostics and local artifacts, not remembered docs.
- Keep the top-level skill lean; put detailed troubleshooting branches in the reference files.
- Cite exact local commands, paths, and log signatures when proposing a fix.
- If local output and `docs.openclaw.ai` differ, state the version drift explicitly and prefer the installed binary for runtime behavior.
- Do not claim a fix without rerunning the relevant command or scenario.

## Tooling/fallback notes

- Prefer shell inspection of local config, logs, service state, and command help before browsing docs.
- When you do need docs, first read `playbooks/docs-navigation.md` so you search the local docs corpus deliberately instead of wandering by filename guesswork.
- Use `docs.openclaw.ai` to understand the latest intended workflow, migration notes, or renamed commands, then verify those steps locally with `openclaw help`.
- If a documented command is unavailable locally, fall back to the nearest installed help surface and record the mismatch as version drift rather than forcing the website procedure verbatim.
