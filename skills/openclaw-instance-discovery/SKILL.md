---
name: openclaw-instance-discovery
description: Use when you need to find OpenClaw installs on this Mac, build or refresh a registry of which Gateways exist, or rescan after adding/removing an install. Triggers on natural language like "find my openclaw", "rescan openclaw", "I added another openclaw", "re-detect openclaw", "discover openclaw instances". Auto-triggered by openclaw-troubleshooting when no instance registry exists at local/state/instances.json.
---

# OpenClaw Instance Discovery

Build a registry of OpenClaw Gateway instances on this machine so the troubleshooting skill knows which one to operate on. Discovery is grounded in OpenClaw's documented Gateway, profile, and service-manager model — see https://docs.openclaw.ai for native commands and platform behaviors.

The goal is **not** to reverse-engineer OpenClaw's internal model. The goal is to be exceptionally good at navigating the system OpenClaw already exposes, plus the documented platform behaviors of launchd on macOS.

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

The result must contain both `local/` and `skills/` directories. Use `$REPO_ROOT` for all paths below. See `playbooks/registry-contract.md` for the full explanation.

## Quick start

- **Goal:** by the end of a discovery run, this machine has a saved registry at `$REPO_ROOT/local/state/instances.json` with a chosen default target.
- **Single-instance common case:** auto-save with no questions asked.
- **Multi-instance case:** ask once for the default; auto-label as `default` / `instance-2`. Don't front-load naming.
- **Never dead-end:** if discovery finds nothing, walk through the fallback ladder before asking the user one tractable question.
- **Always announce the chosen target** in plain language at the end of the run, before handing back to the troubleshooting skill.
- **Auto-trigger context:** When `openclaw-troubleshooting` activates and the registry is missing, unreadable, or malformed, it pauses and hands off to this skill. After this skill writes the registry and announces the target, troubleshooting resumes.

## When auto-triggered by troubleshooting

When you were called because troubleshooting found no registry (not because the user explicitly invoked `/openclaw-instance-discovery`), the user is waiting for troubleshooting to continue. Minimize friction:

- **Single instance found with high confidence?** Save immediately as `default`. Do NOT ask for confirmation. Do NOT pause. Write the registry, announce the target, and return control.
- **Single instance found with medium confidence?** Ask one yes/no question: "I found one likely OpenClaw on this Mac. Want me to save it as your default troubleshooting target?"
- **Multiple instances found?** Ask ONLY which should be the default: "I found two OpenClaw instances. Which should I target by default?" Use `default` / `instance-2` labels.
- **After saving the registry, announce the target and STOP.** Return control to troubleshooting. Do NOT ask follow-up questions. Do NOT offer to rescan. The user wants troubleshooting help, not a discovery conversation.

## Workflow

1. **Run the 6-phase discovery sequence.** See `playbooks/discovery-sequence.md` for the exact commands and what to do with their output.
2. **If discovery finds nothing useful, walk the fallback ladder.** See `playbooks/fallback-ladder.md`. Never dead-end — escalate through documented common locations and ask one tractable question only as a last resort.
3. **Cluster the evidence into candidate Gateway identities.** Multiple signals must line up before you call something an "instance" — service label, config path, state dir, port, optional profile.
4. **Verify each candidate explicitly with `--url` + token.** Bare `--profile X` routing is empirically unreliable in multi-instance setups. The `--url` + per-candidate auth token fallback is documented in `playbooks/discovery-sequence.md` Phase 4.
5. **Present candidates in plain language and confirm with the minimum required input.** Use neutral descriptions like "default launchd service on port 18789" rather than human guesses like "your prod install."
6. **Save the registry** at `$REPO_ROOT/local/state/instances.json`. See `playbooks/registry-contract.md` for the v1 schema and field guidance.
7. **Announce the chosen default target** in plain language so the user knows what subsequent troubleshooting will operate on.

## Reference map

Read only the file you need:

- `playbooks/discovery-sequence.md` -> the 6-phase sequence: native overview, service-manager discovery, candidate clustering, per-candidate verification, summary, confirmation. Includes the empirical `--url` fallback for multi-instance setups.
- `playbooks/fallback-ladder.md` -> what to do when discovery finds nothing: PATH check, common config locations, common state dirs, launchd plist files on disk, listening ports, last-resort question. Never dead-end.
- `playbooks/registry-contract.md` -> v1 schema for `local/state/instances.json`, field guidance, schema rules, ownership (discovery writes; troubleshooting reads).

## Quality rules

- Use native OpenClaw commands first; ground every command and flag in https://docs.openclaw.ai.
- Stay neutral about human semantics during clustering — describe what you found, not what you assume it means.
- Optimize for the single-instance common case. Most users have one OpenClaw and should pay no UX cost for the multi-instance case.
- Use plain language, not internal jargon. A non-technical user is the primary audience.
- Always announce the chosen target before any deeper diagnostic work.
- Never silently pick a target when ambiguity is high.
- Treat the registry as a cached machine model, not absolute truth. Live verification still matters.
