# 🦞 openclaw-skills

This repository is the canonical source for OpenClaw skills in this public repo. v1 ships one skill, `openclaw-troubleshooting`, so agents can diagnose and repair a broken OpenClaw install before anything else.

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

Most troubleshooting skills are static: they ship a fixed set of instructions and never learn from the incidents they help resolve. This skill is designed to get smarter over time.

The cycle works like this:

**Diagnose → Fix → Document → Compound → Repeat**

Each resolved incident produces a structured entry in the [incident log](skills/openclaw-troubleshooting/references/incident-log.md) — symptoms, root cause, what didn't work, what fixed it, and how to prevent it next time. The next time the skill triggers, it reads that log before starting diagnosis, so it arrives with the full history of past gotchas instead of starting from zero.

This means:
- The first time you hit a profile mismatch, you spend 30 minutes chasing the wrong config file. The second time, the skill already knows the pattern and skips straight to the fix.
- Error signatures that required investigation once become instant lookups in [common-signatures.md](skills/openclaw-troubleshooting/references/common-signatures.md).
- Edge cases that no documentation covers — because they only emerge from real incidents — accumulate as institutional knowledge.

The skill doesn't learn autonomously. **You** close the loop by appending what you learned after each incident. The skill just makes sure that knowledge is loaded at the right moment — the start of every future troubleshooting session.

### Contributing learnings

After resolving an incident, append an entry to `references/incident-log.md`:

```markdown
## Short description of the incident

**Precondition:** (optional) Setup-specific conditions that make this relevant.

**Symptoms:** What the user saw.

**Root cause:** What was actually wrong.

**What didn't work:** Approaches that failed or wasted time.

**What fixed it:** The actual fix, step by step.

**Prevention:** How to avoid this in the future.
```

Keep entries general — describe patterns, not machine-specific details. If a gotcha only applies to a specific setup, note the precondition so others can judge relevance.

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
- `skills/openclaw-troubleshooting/references/` — deep reference files per symptom class
  - `incident-log.md` — compounding knowledge from resolved incidents
  - `common-signatures.md` — error string → next action lookup table
  - `validation-scenarios.md` — behavioral test scenarios for the skill
  - `triage.md`, `gateway.md`, `config.md`, `channels.md`, `auth-and-pairing.md`, `tools-and-nodes.md` — domain runbooks
- `skills/openclaw-troubleshooting/scripts/` — helper scripts for diagnostics

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

Supporting files next to `SKILL.md` are allowed, so the same `references/` and `scripts/` layout can be reused without creating a second skill source. The canonical entrypoint is `.claude/skills/openclaw-troubleshooting/SKILL.md` in a project install or `~/.claude/skills/openclaw-troubleshooting/SKILL.md` in a personal install.

## Agent-Neutral Vs Agent-Specific

Agent-neutral:

- `skills/openclaw-troubleshooting/SKILL.md`
- `skills/openclaw-troubleshooting/references/`
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
