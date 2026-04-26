# 🦞 openclaw-admin-skills

Natural-language skills for running OpenClaw. Tell your AI harness to "update openclaw" or "fix my openclaw" in plain English, and get a safe, reviewable workflow — preflight checks, evidence-based diagnosis, explicit approval before any change, and per-user memory that makes every next run smarter.

## What's included

| Skill | Triggers on | What it does |
|---|---|---|
| **openclaw-update** | `"update openclaw"`, `"is there a new openclaw"`, `"time to upgrade"` | End-to-end update. Captures a baseline inventory, checks release notes for breaking changes, backs up, runs `openclaw update`, verifies every channel/cron/plugin still healthy after, and finishes with a **personalized highlights briefing** filtered against the features you actually use. |
| **openclaw-troubleshooting** | `"openclaw isn't working"`, `"not replying"`, `"won't start"`, `"fix my openclaw"` | Evidence-based diagnosis. Reads live CLI output, config, and logs before touching anything. Explicit approval required before any repair — diagnosis and repair are separate phases. |
| **openclaw-instance-discovery** | `"find my openclaw"`, `"rescan"` | Builds a registry of OpenClaw installs on this machine. Auto-triggered by troubleshooting on first run; you rarely invoke it directly. |
| **openclaw-troubleshooting-compound** | After an incident resolves | Drafts a tight incident-log entry + error signatures and writes them to your per-user local memory. Next session reads them back as context. |
| **openclaw-babysit** | `"babysit my openclaw"`, `"keep openclaw running"`, `"watch my channels"`. Designed to wrap with `/loop` (e.g. `/loop 5m /openclaw-babysit`). | Recurring channel-health monitor. Each tick checks every enabled channel and either alerts (default) or, with `--auto-fix`, invokes troubleshooting in authorized mode to apply allowlisted restart-family fixes autonomously. Bounded iterations, channels-as-success criterion. |

Non-technical users can fire up Claude Code in any directory, say "openclaw is broken", and these skills figure out which OpenClaw to target and what to do — without the user needing to know where OpenClaw is installed.

## Quick start (Claude Code)

```bash
mkdir -p ~/src
git clone https://github.com/pejmanjohn/openclaw-skills.git ~/src/openclaw-skills
~/src/openclaw-skills/scripts/install-claude-skill.sh
```

Then in any Claude Code session, just talk:

```
> update openclaw
> openclaw isn't responding
> find my openclaw
```

Or wrap a recurring health check around your channels with Claude Code's `/loop`:

```
> /loop 5m /openclaw-babysit              # alert mode — tells you when channels degrade
> /loop 5m /openclaw-babysit --auto-fix   # autonomous mode — applies allowlisted fixes and verifies
```

Babysit reports a one-line OK on healthy ticks; a degraded reading either alerts you (default) or, in `--auto-fix` mode, invokes troubleshooting non-interactively to apply restart-family fixes from a bounded allowlist. See [openclaw-babysit](#openclaw-babysit) below for the full contract.

Update the skill itself later with:

```bash
git -C ~/src/openclaw-skills pull
~/src/openclaw-skills/scripts/install-claude-skill.sh
```

## Install

Keep one canonical source checkout and install into whichever agents you use. The repo ships three install scripts that symlink back to the canonical checkout — so `git pull` picks up updates everywhere.

One-time clone, shared by all three flows below:

```bash
mkdir -p ~/src
git clone https://github.com/pejmanjohn/openclaw-skills.git ~/src/openclaw-skills
```

### Claude Code: Install

```bash
~/src/openclaw-skills/scripts/install-claude-skill.sh
```

Symlinks into `~/.claude/skills/`. The canonical entrypoint on disk is `~/.claude/skills/openclaw-troubleshooting/SKILL.md` (a symlink to the repo).

For project-local install instead of personal:

```bash
~/src/openclaw-skills/scripts/install-claude-skill.sh --dest "/path/to/project/.claude/skills"
```

### Codex: Install

```bash
~/src/openclaw-skills/scripts/install-codex-skill.sh
```

Symlinks into `$CODEX_HOME/skills` or `~/.codex/skills`. After install, restart Codex so it reloads.

### OpenClaw: Install

OpenClaw loads skills from these locations, highest precedence first:

- Workspace: `<workspace>/skills`
- Project agent skills: `<workspace>/.agents/skills`
- Personal agent skills: `~/.agents/skills`
- Managed/local: `~/.openclaw/skills`
- Bundled skills
- `skills.load.extraDirs`

```bash
~/src/openclaw-skills/scripts/install-openclaw-skill.sh
```

Symlinks into `~/.openclaw/skills`. For workspace-local install:

```bash
~/src/openclaw-skills/scripts/install-openclaw-skill.sh --dest "/path/to/workspace/skills"
```

### Updating

```bash
git -C ~/src/openclaw-skills pull
# then re-run the install script(s) for the agent(s) you use
```

## How it works

Three principles do most of the work:

**1. Local is runtime truth.** The agent and OpenClaw run on the same host, so local binary/help/config/state/logs are what actually govern behavior. Docs at [docs.openclaw.ai](https://docs.openclaw.ai) are procedural truth for the latest release, but if the local binary disagrees with the docs, trust the local binary. Every skill grounds in live `openclaw <subcommand> --help` output before acting.

**2. Skills chain together.** Troubleshooting auto-triggers instance discovery on first run. Update and troubleshooting both read the saved instance registry. After an incident, troubleshooting suggests the compound skill to capture learnings. Each skill is lean; together they're an end-to-end workflow.

**3. Local memory compounds.** Every install has a gitignored `local/` tree. Incident-log entries written by the compound skill, the instance registry written by discovery, and the upgrade-history ledger written by update — all live there, per machine, never pushed upstream. Future sessions read them as context, so the troubleshooting that took an hour the first time becomes a 30-second lookup the next time.

```
┌──────────────────────────┐     ┌──────────────────────────────┐
│ openclaw-troubleshooting │     │ openclaw-troubleshooting-    │
│                          │     │ compound                      │
│  1. Read incident log    │     │                              │
│  2. Diagnose & fix       │────▶│  1. Review conversation      │
│  3. Suggest /compound    │     │  2. Draft tight incident     │
│                          │     │  3. Draft new signatures     │
└──────────────────────────┘     │  4. Check for duplicates     │
                                 │  5. Write to local memory    │
                                 └──────────────────────────────┘
```

## The skills in depth

### openclaw-update

Safe, reviewable update from the installed version to the latest on your channel — one approval gate up front ("go from X to Y?"), then the skill runs through eight phases and stops only if something anomalous happens. A clean run lands on a personalized highlights briefing filtered to features you actually use.

Under the hood: eight phases (target → preflight → release-notes pre-check → backup → update → restart → verify → highlights). Anomaly stops: BREAKING release-note flag, backup verify failure, non-zero update exit, gateway doesn't return healthy, or a post-update gate yellow/red.

What makes it safe:
- Captures a full JSON inventory snapshot before the update (channels, crons, plugins, skills, doctor state) and diffs after, so silent regressions are caught.
- Always passes `--no-restart` to `openclaw update`; never restarts the gateway mid-session on an OpenClaw-native agent (which would kill the agent); emits manual commands for that case.
- On pnpm/npm installs where dep state is uncertain, checks bundled-extension staging completeness before advancing to restart (the `stageRuntimeDependencies: true` case) and offers a scoped per-extension repair if needed.
- Finishes with a highlights briefing filtered against the user's inventory — only surfaces release-note items touching features the user actually has configured.

Full details: `skills/openclaw-update/SKILL.md` and `playbooks/`.

### openclaw-troubleshooting

Two phases, kept strictly separate: **diagnose** (read-only) and **repair** (requires explicit user approval). Running a command that reads state is always allowed; running a command that writes state never happens without a clear yes from the user. A broad prompt like "fix my openclaw" is not authorization to change config.

Loads the instance registry on activation; auto-triggers `openclaw-instance-discovery` if missing. Announces the target in plain language before touching anything. Reads past incidents (both shipped patterns and your local per-machine log) before starting fresh diagnosis.

### openclaw-instance-discovery

Rarely invoked directly. The first time the troubleshooting skill runs, it calls discovery to build a registry of OpenClaw Gateway instances on the machine — launchd/systemd services, config paths, state dirs, ports. The registry is small, hand-readable, and lives at `$REPO_ROOT/local/state/instances.json`.

Only rescan manually if you've added or removed an OpenClaw install.

### openclaw-troubleshooting-compound

Closes the loop after an incident. Reviews the conversation, drafts a tight incident-log entry, drafts any new error signatures, and applies on user confirmation.

The log is a lookup table, not a postmortem narrative: each entry targets ~200-300 words because future troubleshooting sessions read the whole log into context. Format discipline is spelled out in the skill's `SKILL.md`.

### openclaw-babysit

A recurring health check designed to be wrapped by `/loop`. The success criterion is **channels working** — can the user reach their agents through Slack, Discord, Telegram, BlueBubbles, etc. — not "is the gateway process alive." A gateway with `probe: ok` but every channel crash-looping is degraded.

Two modes, one flag:

- `/loop <interval> /openclaw-babysit` — alert mode (default). Reports degradation and stops, leaving the user to run `/openclaw-troubleshooting` interactively.
- `/loop <interval> /openclaw-babysit --auto-fix` — autonomous mode. Invokes `/openclaw-troubleshooting` with `OPENCLAW_TROUBLESHOOTING_AUTHORIZED=1`, which lets it apply fixes from a tightly bounded allowlist (`auto-fix-allowlist.md`) without the usual approval gate. Capped at three distinct fixes per incident; same fix recommended twice in a row triggers give-up. Auto-fix never modifies config — config-shaped signatures always go to the alert path because they are the most prone to misclassification.

Per-tick state lives at `local/state/babysit-<instance-id>.json` (gitignored, atomically written). An incident is closed only after two consecutive healthy ticks, so a single probe-during-healthy-window reading can't fool the loop into declaring victory mid-flap.

## Shared Local Memory

All four skills share a single gitignored `local/` directory at the repo root. Inside it, `local/memory/` holds learned reference material (incident log, error signatures, upgrade history) and `local/state/` holds structured machine state (the instance registry).

Because `local/` lives at the repo root rather than inside any individual skill, **multiple installs share one memory automatically**. If Claude Code, Codex, and OpenClaw are all symlinked to the same source checkout at `~/src/openclaw-skills`, they read and write the same `local/memory/incident-log.md` and the same `local/state/instances.json`.

The entire `local/` directory is gitignored, so per-user entries never conflict with `git pull` and never get pushed upstream.

The shipped skills also contain their own seed content at `skills/openclaw-troubleshooting/playbooks/incident-log.md` and `playbooks/common-signatures.md` — general patterns that apply to any install. The troubleshooting skill reads both layers.

| Layer | Location | Tracked by git | Contains |
|---|---|---|---|
| **Shipped** | `skills/openclaw-troubleshooting/playbooks/*.md` | Yes | General patterns, seed entries |
| **Local** | `local/memory/*.md` | No (gitignored) | Your environment-specific entries |

### Contributing upstream

If you resolve an incident that reveals a **general pattern** other users would benefit from, you can contribute it back. Generalize the entry (replace machine-specific details with placeholders), and open a PR adding it to the shipped playbooks. See `CLAUDE.md` for PR-writing discipline — the short version: write capability specs, not trip reports.

## Instance Discovery

Beyond what's covered in *The skills in depth* above, two details worth knowing:

- The registry records `discoveredFrom` — a short evidence string per instance (e.g. `launchd service ai.openclaw.gateway + config ~/.openclaw/openclaw.json`). When the troubleshooting skill announces "I'm targeting the OpenClaw I found at port 18789," it can cite exactly what evidence it used.
- Discovery never dead-ends. If it finds nothing, it walks documented common install locations (`/opt/homebrew/bin/openclaw`, `~/.openclaw/openclaw.json`, etc.) before asking the user one tractable question.

## Canonical layout

Source of truth lives in `skills/<skill-name>/`. Each skill is self-contained:

```
skills/openclaw-troubleshooting/
├── SKILL.md                  # entrypoint + routing logic
├── playbooks/                # deep runbooks per symptom class
│   ├── triage.md
│   ├── gateway.md
│   ├── config.md
│   ├── channels.md
│   ├── auth-and-pairing.md
│   ├── tools-and-nodes.md
│   ├── common-signatures.md
│   ├── incident-log.md
│   ├── validation-scenarios.md
│   ├── config-writing.md
│   └── docs-navigation.md
├── scripts/                  # helper diagnostic scripts
└── agents/openai.yaml        # thin Codex metadata (optional)
```

Other skills follow the same pattern: `SKILL.md` at the root, `playbooks/` for supporting files, optional `scripts/` for repeatable helpers.

Shared across all skills:

- `local/memory/` — per-user, gitignored, written at runtime by the compound skill
- `local/state/` — per-user, gitignored, written at runtime by discovery

## Agent-neutral vs. agent-specific

Agent-neutral (works for Claude Code, Codex, OpenClaw):

- `skills/<skill>/SKILL.md`
- `skills/<skill>/playbooks/**`
- `skills/<skill>/scripts/**`
- The shared `local/` tree

Agent-specific:

- `skills/openclaw-troubleshooting/agents/openai.yaml` — thin Codex metadata, does not replace `SKILL.md`
- Install paths and discovery rules per harness

The goal is canonical, portable skill content with any agent-specific metadata staying thin and optional. Future expansion (new skills) follows the same pattern: one canonical directory under `skills/`, a short trigger-oriented `SKILL.md`, supporting references in `playbooks/`, optional helper scripts.

See [`CLAUDE.md`](./CLAUDE.md) for contributor discipline — especially on PR descriptions (capability specs, not trip reports).
