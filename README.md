# openclaw-skills

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

## Local First, Version Aware

Use the installed OpenClaw binary as runtime truth:

- `openclaw --version`
- `openclaw help` and `openclaw <subcommand> --help`
- `openclaw config file`
- `openclaw status`, `openclaw gateway probe`, `openclaw doctor`, and logs

Treat [docs.openclaw.ai](https://docs.openclaw.ai/) as procedural truth for the latest release, not as proof that the local install has the same commands, flags, or config keys. If the docs and the local binary disagree, trust the local install and treat the difference as version drift.

## Canonical Layout

The source of truth lives in one place:

- `skills/openclaw-troubleshooting/SKILL.md`
- `skills/openclaw-troubleshooting/references/`
- `skills/openclaw-troubleshooting/scripts/`

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

## Install with OpenClaw

If you want OpenClaw itself to load the skill, symlink or copy the canonical folder into one of OpenClaw's skill locations.

From the repo root:

```bash
REPO_ROOT="$(pwd)"
mkdir -p ~/.openclaw/skills
ln -s "$REPO_ROOT/skills/openclaw-troubleshooting" ~/.openclaw/skills/openclaw-troubleshooting
```

For a workspace-only install, place it in the active OpenClaw workspace instead:

```bash
REPO_ROOT="$(pwd)"
WORKSPACE="/path/to/openclaw-workspace"
mkdir -p "$WORKSPACE/skills"
ln -s "$REPO_ROOT/skills/openclaw-troubleshooting" "$WORKSPACE/skills/openclaw-troubleshooting"
```

## Install with Codex

Codex can use the same canonical folder; no Codex-only copy is needed. Install it into `$CODEX_HOME/skills` or `~/.codex/skills`, then restart Codex so it picks up the new skill.

From the repo root:

```bash
REPO_ROOT="$(pwd)"
mkdir -p ~/.codex/skills
ln -s "$REPO_ROOT/skills/openclaw-troubleshooting" ~/.codex/skills/openclaw-troubleshooting
```

`skills/openclaw-troubleshooting/agents/openai.yaml` is optional metadata only. The canonical instructions remain in `SKILL.md`.

## Install with Claude Code

Claude Code uses the same `SKILL.md` shape and supporting files, but it discovers project skills from `.claude/skills/<skill-name>/SKILL.md` and personal skills from `~/.claude/skills/<skill-name>/SKILL.md`.

Install the same canonical folder into either location:

```bash
REPO_ROOT="$(pwd)"
mkdir -p .claude/skills
ln -s "$REPO_ROOT/skills/openclaw-troubleshooting" .claude/skills/openclaw-troubleshooting
```

or:

```bash
REPO_ROOT="$(pwd)"
mkdir -p ~/.claude/skills
ln -s "$REPO_ROOT/skills/openclaw-troubleshooting" ~/.claude/skills/openclaw-troubleshooting
```

Supporting files next to `SKILL.md` are allowed, so the same `references/` and `scripts/` layout can be reused without creating a second skill source.
The canonical entrypoint is `.claude/skills/openclaw-troubleshooting/SKILL.md` in a project install or `~/.claude/skills/openclaw-troubleshooting/SKILL.md` in a personal install.

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
