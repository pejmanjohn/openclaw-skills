# 🦞 openclaw-skills

This repository is the canonical source for OpenClaw skills. It ships two skills that work together: `openclaw-troubleshooting` for diagnosing and repairing a broken OpenClaw install, and `openclaw-troubleshooting-compound` for capturing learnings after each incident so the troubleshooting skill gets smarter over time.

## Current Scope

This repo focuses on local, evidence-based troubleshooting for:

- install and setup issues
- gateway and runtime issues
- dashboard and control UI connectivity
- channel delivery problems
- auth, token, and pairing drift
- tools, nodes, permissions, and approvals
- config validation and safe config changes
- plugin-related failures where relevant

The first skill is troubleshooting-focused because that is the fastest way to make the repo useful on day one. When OpenClaw is running on the same machine as the agent, local binary/help/config/state/logs are more trustworthy than assumptions or the latest docs alone.

## Compounding Knowledge

Most troubleshooting skills are static: they ship a fixed set of instructions and never learn from the incidents they help resolve. This repo is designed to get smarter over time — for **each user individually**.

The cycle works like this:

**Diagnose → Fix → Compound → Repeat**

After resolving an incident, the troubleshooting skill suggests running `/openclaw-troubleshooting-compound`. That companion skill reviews what just happened in the conversation — symptoms, dead ends, root cause, fix — and drafts a structured entry for your **local** incident log (`playbooks/local/incident-log.md`) and any new error signatures (`playbooks/local/common-signatures.md`). You review the draft, confirm, and the learnings are written. No manual writing required. The `local/` directory is gitignored, so your entries never conflict with upstream updates.

The next time the troubleshooting skill triggers, it reads the incident log before starting diagnosis, so it arrives with the full history of **your** past incidents instead of starting from zero.

### Why local, not upstream?

The most useful troubleshooting knowledge is specific: your exact ports, profile names, config paths, service labels, the commands that worked on your machine. Generic patterns are already in the skill's reference files. The incident log is where your environment's quirks accumulate — the things no upstream documentation could anticipate.

The repo ships two layers of knowledge:

| Layer | Location | Tracked by git | Contains |
|---|---|---|---|
| **Shipped** | `playbooks/incident-log.md`, `playbooks/common-signatures.md` | Yes | General patterns, seed entries |
| **Local** | `playbooks/local/incident-log.md`, `playbooks/local/common-signatures.md` | No (gitignored) | Your environment-specific entries |

The troubleshooting skill reads both layers. `git pull` updates the shipped patterns without touching your local learnings.

This means:
- The first time you hit a problem, you work through it. The second time, the skill already has your exact fix — paths, ports, and all.
- Error signatures that required investigation once become instant lookups with your specific next-action steps.
- Upstream improvements arrive via `git pull` without merge conflicts.

### How it works

```
┌─────────────────────────┐     ┌──────────────────────────────┐
│ openclaw-troubleshooting │     │ openclaw-troubleshooting-     │
│                         │     │ compound                      │
│  1. Read incident log   │     │                              │
│  2. Diagnose & fix      │────▶│  1. Review conversation      │
│  3. Suggest /compound   │     │  2. Draft incident-log entry │
│                         │     │  3. Draft new signatures     │
└─────────────────────────┘     │  4. Check for duplicates     │
                                │  5. Present for confirmation │
                                │  6. Write to local install   │
                                └──────────────────────────────┘
```

### Contributing upstream

If you resolve an incident that reveals a **general pattern** other users would benefit from, you can contribute it back. Generalize the entry (replace machine-specific details with placeholders) and open a PR to `playbooks/incident-log.md` or `playbooks/common-signatures.md`.

## Local First, Version Aware

Use the installed OpenClaw binary as runtime truth:

- `openclaw --version`
- `openclaw help` and `openclaw <subcommand> --help`
- `openclaw config file`
- `openclaw status`, `openclaw gateway probe`, `openclaw doctor`, and logs

Treat [docs.openclaw.ai](https://docs.openclaw.ai/) as procedural truth for the latest release, not as proof that the local install has the same commands, flags, or config keys. If the docs and the local binary disagree, trust the local install and treat the difference as version drift.

## Canonical Layout

The source of truth lives in one place:

- `skills/openclaw-troubleshooting/SKILL.md` — entrypoint and routing logic
- `skills/openclaw-troubleshooting/playbooks/` — deep reference files per symptom class
  - `incident-log.md` — compounding knowledge from resolved incidents
  - `common-signatures.md` — error string → next action lookup table
  - `validation-scenarios.md` — behavioral test scenarios for the skill
  - `triage.md`, `gateway.md`, `config.md`, `channels.md`, `auth-and-pairing.md`, `tools-and-nodes.md` — domain runbooks
- `skills/openclaw-troubleshooting/scripts/` — helper scripts for diagnostics

- `skills/openclaw-troubleshooting-compound/SKILL.md` — companion skill that drafts and applies post-incident learnings

`skills/openclaw-troubleshooting/agents/openai.yaml` is optional Codex metadata only. It is intentionally thin and does not replace `SKILL.md`.

## How OpenClaw Finds Skills

OpenClaw loads skills from these locations, highest precedence first:

- Workspace: `<workspace>/skills`
- Project agent skills: `<workspace>/.agents/skills`
- Personal agent skills: `~/.agents/skills`
- Managed/local: `~/.openclaw/skills`
- Bundled skills
- `skills.load.extraDirs`

That means you can keep one canonical skill folder in this repo and install it into whichever of those locations makes sense for your workflow. Workspace-local installation is best when the skill should apply only to the current project. Shared installation is best when you want it available everywhere on the machine.

## OpenClaw: Install

If you want OpenClaw itself to load the skill, the recommended path is a source checkout managed at `~/src/openclaw-skills` plus a symlink into `~/.openclaw/skills`:

```bash
mkdir -p ~/src
git clone https://github.com/pejmanjohn/openclaw-skills.git ~/src/openclaw-skills
~/src/openclaw-skills/scripts/install-openclaw-skill.sh
```

Update to the latest version with:

```bash
git -C ~/src/openclaw-skills pull
~/src/openclaw-skills/scripts/install-openclaw-skill.sh
```

If you want a workspace-local OpenClaw install instead of the shared machine-wide path, use:

```bash
WORKSPACE="/path/to/openclaw-workspace"
~/src/openclaw-skills/scripts/install-openclaw-skill.sh --dest "$WORKSPACE/skills"
```

## Codex: Install

For Codex, the recommended local install path is a source checkout at `~/src/openclaw-skills` plus a symlink into `$CODEX_HOME/skills` or `~/.codex/skills`:

```bash
mkdir -p ~/src
git clone https://github.com/pejmanjohn/openclaw-skills.git ~/src/openclaw-skills
~/src/openclaw-skills/scripts/install-codex-skill.sh
```

Update to the latest version with:

```bash
git -C ~/src/openclaw-skills pull
~/src/openclaw-skills/scripts/install-codex-skill.sh
```

Then restart Codex so it reloads the installed skill.

`skills/openclaw-troubleshooting/agents/openai.yaml` is optional metadata only. The canonical instructions remain in `SKILL.md`.

## Claude Code: Install

For Claude Code, the recommended local install path is a source checkout at `~/src/openclaw-skills` plus a symlink into `~/.claude/skills`:

```bash
mkdir -p ~/src
git clone https://github.com/pejmanjohn/openclaw-skills.git ~/src/openclaw-skills
~/src/openclaw-skills/scripts/install-claude-skill.sh
```

Update to the latest version with:

```bash
git -C ~/src/openclaw-skills pull
~/src/openclaw-skills/scripts/install-claude-skill.sh
```

For a project-local Claude install instead of a personal install, use:

```bash
PROJECT_ROOT="/path/to/project"
~/src/openclaw-skills/scripts/install-claude-skill.sh --dest "$PROJECT_ROOT/.claude/skills"
```

Supporting files next to `SKILL.md` are allowed, so the same `playbooks/` and `scripts/` layout can be reused without creating a second skill source. The canonical entrypoint is `.claude/skills/openclaw-troubleshooting/SKILL.md` in a project install or `~/.claude/skills/openclaw-troubleshooting/SKILL.md` in a personal install.

## Agent-Neutral Vs Agent-Specific

Agent-neutral:

- `skills/openclaw-troubleshooting/SKILL.md`
- `skills/openclaw-troubleshooting/playbooks/`
- `skills/openclaw-troubleshooting/scripts/collect-openclaw-diagnostics.sh`

Agent-specific:

- `skills/openclaw-troubleshooting/agents/openai.yaml`
- installation paths and discovery rules for Codex and Claude Code

The goal is to keep the troubleshooting content canonical and portable, while any agent-specific metadata stays thin and optional.

## Future expansion

Future skills should follow the same pattern:

- one canonical skill directory under `skills/`
- a short trigger-oriented `SKILL.md`
- supporting references for details
- small helper scripts for repeatable diagnostics

That keeps the repo easy to extend without drifting into duplicated Codex- or Claude-specific trees.
