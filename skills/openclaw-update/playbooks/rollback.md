# Rollback

If any post-update gate fails red, roll back before doing anything else. Do not attempt to fix forward in the middle of an update — the user's baseline was healthy, so getting back to the baseline is the lowest-risk path. Forward-fixes happen in a separate troubleshooting session, after rollback.

The backup from Phase 3 exists precisely for this. Use it.

## Rollback ladder

Walk these steps in order. Stop at the first step that successfully restores the pre-update gateway state.

### Step 1: Revert the CLI to the previous version

```bash
openclaw update --tag <previous-version> --no-restart --yes
```

`<previous-version>` is `installed.version` from the baseline snapshot (e.g. `2026.4.5`). This is the documented downgrade path — `openclaw update` knows how to downgrade per install kind.

- `--no-restart` — same rule as a forward update; the skill does not restart the gateway.
- `--yes` — accept the downgrade prompt (downgrades are confirmed by default).

After this runs, verify:

```bash
openclaw --version
```

Must match the baseline version. If not, this step didn't work; go to Step 2.

### Step 2: Restart the gateway

Use the same three-step sequence as Phase 5 (including `launchctl enable`, which is mandatory after `openclaw gateway stop`):

```bash
openclaw gateway stop
launchctl enable gui/$(id -u)/<serviceLabel>
launchctl bootstrap gui/$(id -u) <plistPath>
```

OpenClaw-native agents must emit for the user and wait. External harnesses (Claude Code, Codex, plain shell) may run it directly. Wait ~10 seconds for channel providers to initialize, then:

```bash
openclaw gateway status
openclaw gateway probe
```

Both should report ok.

### Step 3: Re-run the post-update gates against the baseline

This is counterintuitive: re-run Phase 6's command ladder and diff the post-rollback state against the **baseline**, not against the broken post-update state.

If every gate now passes, the rollback is complete. Announce:

> **Rollback complete.** Back on `<baseline-version>`. All gates pass against the pre-update baseline.

If any gate still fails, the update caused damage beyond what `openclaw update --tag` could reverse. Go to Step 4.

### Step 4: Restore from the native backup archive

```bash
openclaw backup verify <archive-path>
# then (path and command per openclaw docs):
openclaw backup restore <archive-path>
```

`<archive-path>` is in `$REPO_ROOT/local/backups/<runId>/archive-path.txt`.

If `openclaw backup restore` is unavailable or fails, fall back to the explicit config copy:

```bash
cp "$REPO_ROOT/local/backups/<runId>/openclaw.json" "$(openclaw config file)"
openclaw config validate
```

If `config validate` fails even with the restored config, this is a state-level problem (not a config-level problem). Hand off to `openclaw-troubleshooting` with the full rollback history.

### Step 5: Hand off to troubleshooting

If Steps 1-4 didn't fully restore the baseline, this has escalated beyond a rollback. Hand off to `openclaw-troubleshooting` with:

- The baseline snapshot (`$REPO_ROOT/local/state/update-baseline-<runId>.json`)
- The post-update snapshot (`$REPO_ROOT/local/state/update-post-<runId>.json`)
- The backup manifest (`$REPO_ROOT/local/backups/<runId>/manifest.json`)
- The exact error text from whichever gate failed
- A narrative of which rollback steps were attempted and their outcomes

Do not attempt to improvise further fixes within the update skill. The troubleshooting skill has the discipline (read-only diagnosis first, explicit repair approval) that this situation requires.

## Record the rollback in the upgrade history

Whether the rollback succeeds at Step 3 or requires escalation to Step 5, append an entry to `$REPO_ROOT/local/memory/upgrade-history.md` with the outcome. See `playbooks/upgrade-history.md` for the format — rollback entries use `result: rolled-back` or `result: partial-rollback` instead of `result: success`.

## What NOT to do during rollback

- **Do not edit the config file by hand** to try to make the broken post-update state work. Roll back first.
- **Do not run `openclaw update` forward** to a different version to "jump past" the broken version. That compounds risk and makes the history impossible to reason about.
- **Do not delete the broken post-update snapshot.** It's evidence. Keep it in `local/state/` — the troubleshooting skill may need it.
- **Follow the same restart-who-runs-it rule as Phase 5.** OpenClaw-native agents emit + wait. External harnesses may run directly. Always include `launchctl enable` between `stop` and `bootstrap`.
- **Do not skip `openclaw backup verify`** on the archive before restoring from it. A corrupt archive that restores into live state is worse than no restore.

## Quality rules

- **Stop at the first step that restores health.** Don't run Step 4 if Step 3 already passed.
- **Verify after every step.** "Probably worked" is not enough. `openclaw --version` + gate diff against baseline is the minimum confirmation.
- **Always announce the rollback decision to the user** before running Step 1. Rollback is a user-visible action; don't surprise them.
- **Hand off to troubleshooting, don't keep improvising.** The update skill's job ends at "restored to baseline" or "clearly escalated." It's not for deeper diagnosis.
- **Record the outcome** in the upgrade-history ledger regardless. Rollbacks are the most important entries to log — they teach future runs what can go wrong.
