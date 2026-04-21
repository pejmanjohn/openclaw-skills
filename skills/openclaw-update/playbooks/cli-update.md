# CLI Update

Run `openclaw update` to install the new version. The skill delegates all install-kind branching to the `openclaw update` command — it detects pnpm, npm, brew, or a git checkout and routes accordingly. Do not invoke package managers directly from the skill.

## Core rule: `--no-restart` is mandatory

`openclaw update --no-restart --yes`

The `--no-restart` flag skips the post-update gateway restart. The skill emits the restart commands manually in Phase 5 so the user runs them in their own shell — not in the skill's subprocess. Gateway restarts that happen inside the skill's session kill the gateway mid-command and leave stale lock files that block future startups.

There are no exceptions to this rule. If the user asks the skill to run `openclaw update` without `--no-restart`, explain why and refuse.

## Sequence

### 1. Preview with `--dry-run`

```bash
openclaw update --dry-run
```

The dry-run shows what the update would do: which package manager it'll invoke, which version it'll install, whether it would restart anything. Read the output and summarize for the user:

- Install kind it detected (pnpm/npm/brew/git)
- Package target (version / dist-tag / git ref)
- Expected duration if the command reports it

**Gate:** Present the dry-run summary. Ask explicit approval before running the real update.

### 2. Run the update

```bash
openclaw update --no-restart --yes
```

Flags:
- `--no-restart` — mandatory. Skip restarting the gateway.
- `--yes` — non-interactive. Accepts downgrade prompts (rare, happens if the target version is lower than the current version).

Optional flags — only use when the user explicitly asks:
- `--channel stable|beta|dev` — switch the update channel and persist it in config.
- `--tag <version|dist-tag|spec>` — override the package target for a one-off update.
- `--timeout <seconds>` — per-step timeout, defaults to 1200s.
- `--json` — structured output. Prefer this when the installed binary supports it — it makes the exit state easier to verify.

Capture the exit code and full stdout/stderr. If the command prefers JSON output, use:

```bash
openclaw update --no-restart --yes --json
```

### 3. Verify the CLI actually updated

```bash
openclaw --version
```

The version string must match the target version from `openclaw update status --json` in the preflight snapshot. If it didn't change, the update didn't take effect — halt and investigate. Common causes:

- Install kind detection was wrong (edge case; usually means the install is broken in ways that `openclaw doctor` already flagged)
- The target version was already the installed version (shouldn't happen — the release-summary gate should have caught this)
- A package-manager permission error that `openclaw update` surfaced but the skill ignored

### 4. Confirm the update did NOT restart the gateway

```bash
openclaw gateway status
```

The gateway should still be running on the old binary (PID unchanged, uptime continuing from before the update). This confirms `--no-restart` was honored. The new binary is installed on disk but not loaded yet — Phase 5's manual restart is what activates it.

## Install-kind specifics (reference only — do not invoke directly)

The skill does NOT call these directly. `openclaw update` routes to the right one internally. This reference exists so you understand what `--dry-run` output means.

| Install kind | `openclaw update` routes to | Notes |
|--------------|-----------------------------|-------|
| `package` via `pnpm` | `pnpm add -g openclaw@<target>` or equivalent in the install root | Most common for CLI-only installs |
| `package` via `npm` | `npm install -g openclaw@<target>` | |
| `package` via `brew` | `brew upgrade openclaw` | Homebrew taps |
| `git` | `git fetch && git checkout <ref> && <package-manager> install && build` | Source checkouts under `~/src/openclaw` or similar |

If `--dry-run` shows an install-kind the user didn't expect, pause and ask them to confirm before running the real update. An unexpected install kind often means the install registry got confused (e.g. a reinstall through a different package manager left dual install paths).

## Handling errors mid-update

If `openclaw update` exits non-zero:

1. **Do NOT re-run the update command blindly.** It may have partially completed.
2. Check `openclaw --version` — did the version change?
3. Check `openclaw gateway status` — is the gateway still up on the old binary?
4. If both are unchanged, the update aborted cleanly. The user is still on the old version with no side effects. Read the error output and halt for user review.
5. If the version bumped but the command still exited non-zero, the install succeeded but a post-install step failed (commonly `doctor` running inside `openclaw update`). Treat this as the update having completed; surface the doctor warning for user review before proceeding to Phase 5.
6. If the version is inconsistent (e.g. the binary reports a new version but `openclaw update status` still shows "update available"), hand off to `openclaw-troubleshooting` — this is a corrupted install, not an update flow problem.

## What NOT to do

- **Do not run `npm install -g openclaw` directly**, or any other package-manager command. Always go through `openclaw update`.
- **Do not `git pull` in a source checkout.** `openclaw update` knows how to update a git install (it runs `git fetch`, resolves the target, rebases, rebuilds, runs doctor). Manual git operations skip the rebuild and doctor steps.
- **Do not omit `--no-restart`.** No "just this once." No "it'll be faster." No.
- **Do not run `openclaw update` a second time during the same run** to "make sure it worked." The first run either succeeded or didn't. Re-running doesn't add signal; it risks compounding an error.
- **Do not invoke the interactive wizard (`openclaw update wizard`).** The wizard is for humans at a terminal. The skill drives `openclaw update` non-interactively with flags.

## Quality rules

- `--no-restart` and `--yes` on every real update invocation.
- Always dry-run first, always gate on user approval between dry-run and the real run.
- Verify the version bumped after the update. Claiming "update complete" without `openclaw --version` confirmation is not allowed.
- Verify the gateway stayed up on the old binary — that's proof `--no-restart` worked.
- If anything looks off, stop and hand off to troubleshooting. Do not improvise a fix in the middle of an update.
