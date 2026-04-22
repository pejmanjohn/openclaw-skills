# Upgrade History

Per-user ledger of past OpenClaw updates. Analogous to the troubleshooting-compound skill's local incident log — the ledger lives in the user's gitignored `local/memory/` directory, accumulates entries over time, and is read by future update runs for context.

This shipped file is the **format template only**. No actual entries live here. Entries go to `$REPO_ROOT/local/memory/upgrade-history.md`, which is gitignored.

## Where the actual ledger lives

```
$REPO_ROOT/local/memory/upgrade-history.md
```

`local/memory/` is gitignored at the repo root. If the file doesn't exist when Phase 7 needs it, create it with this header:

```markdown
# Local Upgrade History

OpenClaw upgrade history for this machine. Written by `openclaw-update` after each run (success, rollback, or abort). Read by future update runs for context. Gitignored — never pushed upstream.

| Run ID | Date | From | To | Install kind | Duration | Result | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

Then append rows to the table.

## Entry format

Each upgrade gets one row in the table. Format:

```markdown
| 20260420-143022 | 2026-04-20 | 2026.4.5 | 2026.4.15 | pnpm (package) | 4m 12s | success | All gates passed. Highlights surfaced 3 items (telegram, cron, skills). |
```

### Columns

- **Run ID** — the timestamp used across all artifacts for this run. Same as the baseline snapshot filename suffix.
- **Date** — `YYYY-MM-DD` of the run. Easier to skim than a full timestamp.
- **From** — `installed.version` from the baseline snapshot.
- **To** — `installed.version` from the post snapshot (on success) or same as From (on abort / rollback).
- **Install kind** — `<packageManager> (<installKind>)` from the baseline snapshot, e.g. `pnpm (package)`, `brew (package)`, `git (git)`.
- **Duration** — wall-clock time from Phase 1 start to Phase 8 end. Use `Nm Ps` format. `—` if unknown.
- **Result** — one of:
  - `success` — all gates passed, no rollback
  - `success-with-warnings` — gates passed but yellow gates were accepted
  - `rolled-back` — red gate, rolled back via `playbooks/rollback.md`, baseline restored
  - `partial-rollback` — rollback partially succeeded, hand-off to troubleshooting
  - `aborted-preflight` — refused to update due to unhealthy baseline
  - `aborted-user` — user cancelled at a phase gate
- **Notes** — one short line. What's memorable about this run: the reason for an abort, the gate that triggered a rollback, the highlight the user most cared about.

## Extended entries (below the table)

For rollbacks, partial-rollbacks, or aborts, add a detailed block below the table with a `---` separator:

```markdown
---

## 20260115-143022 — rolled back (example plugin init failure)

**Symptoms:** `<plugin-name>` plugin init went from ok (baseline) to failed (post). Error: `Cannot find module '/path/to/.../<plugin-name>'`.

**Root cause suspicion:** Module path resolution changed in the target version — the plugin still points to the pre-update install root.

**Rollback steps run:**
1. `openclaw update --tag <previous-version> --no-restart --yes` — succeeded
2. Gateway restarted (three-step stop/enable/bootstrap) — succeeded
3. Re-ran gates against baseline — all pass

**Outcome:** Restored to `<previous-version>`. Logged as incident via `/openclaw-troubleshooting-compound`.

**Followup:** Wait for upstream fix or re-test on next release.
```

Extended entries explain what's non-obvious from the table row. Don't write them for straightforward success runs — the table row is enough.

## Reading the ledger in future runs

When the skill runs next time, Phase 1 reads the last 3-5 entries from the ledger before proposing an update. Surface anything notable in the release summary:

> Note from upgrade history: the last update flagged a plugin init warning that was accepted. Worth checking whether this update fixes or worsens it.

This turns the ledger into accumulating context that makes each run smarter without requiring the user to remember past issues.

## Deduplication

If the same run_id is ever encountered twice (shouldn't happen — timestamps are second-precision), update the existing row rather than appending a duplicate. The likely cause is a skill restart mid-run and a retry; the second run is the one that matters.

## Quality rules

- **Always write an entry, every run.** Success, failure, abort, rollback — all of them get logged. The ledger is only useful if it's complete.
- **Short notes.** One line in the table. Extended block only for non-trivial outcomes.
- **Cite the run_id everywhere** so the ledger entry, the baseline snapshot, the post snapshot, and the backup directory are all trivially cross-referenced.
- **Don't copy the extended block** above verbatim into the actual ledger — it's an example of shape, not content to transplant.
- **Read before writing.** Check the last few entries for context before writing the new one, so the new entry can reference prior state where relevant.
