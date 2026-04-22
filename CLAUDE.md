# Contributing to openclaw-admin-skills

Notes for Claude Code, Codex, and other AI agents working on this repo. Human contributors will find most of this redundant with `CONTRIBUTING.md`-style common sense; the repetition is for the agents.

## Public artifacts are public record

PRs, issues, commit messages, code comments — anything pushed to this repo is read by strangers, indexed by search engines, and stays forever. Write the general version; keep the personal version local.

### PR descriptions are capability specs, not trip reports

When you write a PR body, describe what the change does in general terms — NOT what you hit while testing it on one specific setup.

**Drop:**
- Machine names ("on my Mac mini"), user handles, personal paths
- Trip-report framing ("observed to fail on real runs", "during a real run...", "in our test run")
- Raw numbers from one environment (backup archive sizes, session counts, specific memory usage)
- References to user-specific files (`memory/<personal-notes>`, personal skill names)
- Anecdotes about the specific run that led to the change

**Keep:**
- Version ranges and error strings — those are facts anyone hitting the same issue needs
- Architectural decisions and the reasoning behind them
- Trade-offs considered and rejected
- Links to relevant docs, issues, changelog entries

**Test before pushing:** would a stranger reading this PR learn about **the skill/system**, or about **the author's specific setup**? If the latter, rewrite.

### Same discipline for code comments and commit messages

Don't reference user-local files, personal memory trees, or setup-specific paths in code or comments that ship. Exception: referencing a file that's actually in this repo is fine (e.g. `$REPO_ROOT/local/memory/incident-log.md` is a documented path that lives in every install).

### Personal specifics still have homes, just not shipped ones

- **PR comment thread** — if reviewers need the trip-report context to evaluate the change, add it as a comment, not in the body
- **Gitignored `local/` tree** — per-user state, loaded by skills at runtime but never pushed
- **The contributor's own workspace** — private notes, per-machine memory

## Local vs shipped split in this repo

`local/**` is gitignored. Anything a user's runtime writes — incident log entries, instance registry, upgrade history, backups — goes there. `skills/**` is shipped; it's the general, reusable patterns.

When a skill learns something from a specific incident, the incident-specific details go to `local/memory/`. The generalizable pattern goes to `skills/<skill>/playbooks/`. See `skills/openclaw-troubleshooting-compound/SKILL.md` for the format discipline on local incident-log entries — they're read into context on every future session, so keep them tight.

## Before opening a PR

- Run `python3 -m unittest tests.test_repository` — 58 tests covering repo shape, skill metadata, install scripts, and diagnostic scripts. If any fail, fix before opening.
- Run the relevant skill's install script (`scripts/install-claude-skill.sh`, `scripts/install-codex-skill.sh`, or `scripts/install-openclaw-skill.sh`) to confirm the skill symlinks cleanly into the target directory.
- If your change touches shipped content that users read at runtime (SKILL.md files, playbooks), check for any personal-setup leakage before pushing.
