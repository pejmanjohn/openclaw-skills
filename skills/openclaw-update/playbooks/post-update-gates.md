# Post-Update Gates

After the user has restarted the gateway (Phase 5), re-capture the full inventory and diff it against the baseline. This phase is the proof that the update didn't silently break anything.

The diff is not optional. Every inventory item captured in `preflight-inventory.md` must be re-captured and compared. A pass is only a pass if **every** item that was healthy before is healthy after.

## Capture the post-update snapshot

Re-run the exact same command ladder from `preflight-inventory.md`. Save the result as:

```
$REPO_ROOT/local/state/update-post-<runId>.json
```

`<runId>` is the same timestamp used for the baseline. Matching run IDs is how diff tooling (now or later) pairs them up.

The post snapshot shape is identical to the baseline shape, with the version bumped to the new `installed.version`.

## Diff rules

Pairwise comparison between `baseline.json` and `post.json`. Match records by id/name, not by array index — the order must be stable per the preflight rules, but a dropped record would shift indices and cause false positives.

### Version

**Baseline → Post:** `installed.version` must change from the old version to the target version.

- If unchanged: **red gate.** The update didn't take effect despite Phase 4 reporting success. Halt. Investigate via `openclaw-troubleshooting`.
- If changed to an unexpected version (not the target): **yellow gate.** Probably a channel mismatch; surface to the user and ask whether to accept.

### Gateway

**Baseline → Post:** `gateway.status` stays `running`, `gateway.probe` stays `ok`.

- New PID is expected (because the user restarted). Don't treat PID change as a regression.
- If status or probe is not ok: **red gate.** Offer rollback.

### Doctor

**Baseline → Post:** `health.doctor` stays `ok` (or at worst, `warnings` with the same or fewer warning lines).

- New warnings that weren't in baseline: **yellow gate.** Show the exact new warning text. Ask the user if it's acceptable.
- Doctor went from `ok` to `error`: **red gate.** Offer rollback.

### Config validate

**Baseline → Post:** stays `ok`.

- If it went from `ok` to fail: **red gate.** Post-update config drift means the new version has a schema or validation change the old config doesn't match. Offer rollback.

### Channels

**Baseline → Post:** every channel present in baseline must still be present in post with the same `enabled` and `provider`; every channel that had `probe: ok` in baseline must still have `probe: ok` in post.

- Missing channel (present in baseline, absent in post): **red gate.**
- Channel present but `probe` went from `ok` to `fail`: **red gate.** Likely auth/transport breakage from the version bump.
- New channel (absent in baseline, present in post): **yellow gate.** Should not happen on a normal update — surface to the user.
- Channel probe flipped from `fail` to `ok`: **pass.** Update may have fixed something that was broken before. Note this in the highlights phase.

Probe latency jitter (e.g. 170ms → 260ms) is **not a regression**. Providers do real network work; absolute latency varies run-to-run. Only flag a channel as regressed if `probe` flipped from `ok` to `fail`.

### Crons

**Baseline → Post:** count unchanged; every cron present in baseline is present in post with the same `enabled` flag; no cron that was `enabled: true` in baseline is now `enabled: false` in post.

- Missing cron: **red gate.**
- Cron disabled that was enabled: **red gate.**
- Last-run status regressed: **yellow gate.** May be unrelated (crons run on their own schedule); note and move on.

### Plugins

**Baseline → Post:** every plugin present with `init: ok` in baseline must still be `init: ok` in post.

- Plugin that was `init: ok` now `init: failed`: **red gate.** This is the classic update-breaks-plugin case. Surface the error text and offer rollback.
- New plugin init failure that wasn't in baseline: **red gate.**
- A plugin that was `init: failed` in baseline and is now `init: ok`: **pass.** Probably intentional — the update fixed something. Note it.
- Net-new plugins shipped by the update (total count increased): **pass, informational.** Surface the count delta and the new plugin names in the Phase 8 highlights. Not a regression.

### Skills

**Baseline → Post:** every skill present and enabled in baseline must still be present and enabled in post.

- Skill disappeared (present in baseline, absent in post): **yellow gate.** May have been deprecated upstream. Surface the skill name and let the user decide.
- Skill went from enabled to disabled: **yellow gate.** Same.
- Net-new skills shipped by the update (total count increased): **pass, informational.** Surface in Phase 8 highlights. Not a regression.

## Gate verdicts

### All green → proceed to Phase 7

Every item above passes. Announce:

> **All post-update gates pass.**
> - Version: `<old>` → `<new>`
> - Channels: `<N>`/`<N>` healthy
> - Crons: `<M>`/`<M>` present and enabled
> - Plugins: `<P>`/`<P>` initialized
> - Doctor: `<status>`, config validate: `<status>`
>
> Ready to append to the upgrade history ledger.

### Any yellow → ask user

Show the user each yellow item with full context (baseline value vs. post value, exact error text if any). Ask whether to:

- Accept the regression and continue to Phase 7
- Roll back via `playbooks/rollback.md`
- Pause for investigation (not a rollback; the user wants to look at something manually before deciding)

Do not auto-accept yellows. They exist specifically to force a human judgement call.

### Any red → rollback ladder

Go straight to `playbooks/rollback.md`. Do not proceed to Phase 7. Do not write an upgrade-history entry yet — the update is not complete until the red gate is resolved (either via rollback or via a deliberate accept with a clear reason recorded in the history ledger).

## What the diff OUTPUT should look like

A rendered diff for the user should group changes by category and surface the exact before/after values:

```
Version:    2026.4.5 → 2026.4.15    [PASS]
Gateway:    running (new PID)        [PASS]
Doctor:     ok → ok                  [PASS]
Config:     ok → ok                  [PASS]

Channels (3/3 healthy):
  telegram:default   ok → ok          [PASS]
  discord:default    ok → ok          [PASS]
  bluebubbles:main   ok → ok          [PASS]

Crons (6/6 enabled):
  morning-digest     enabled → enabled [PASS]
  ... (5 more)

Plugins:
  slack              ok → ok          [PASS]
  web-tools          ok → ok          [PASS]
  (+4 new plugins shipped by 2026.4.15)           [informational]

Result: ALL GATES PASS
```

If any gate fails, put that category at the TOP of the output so the user doesn't have to scroll past passes to see the problem.

## Quality rules

- **Re-run every baseline command.** No shortcuts like "the gateway is probably fine, skip it." If it was in the baseline, it's in the post.
- **Match by id, not index.** Sorting order may shift between runs in edge cases.
- **Surface raw command output for any failed gate.** The user needs the actual error text, not a paraphrase.
- **Never claim a pass without having run the comparison.** "Looks fine to me" is not a pass; a field-by-field comparison is.
- **Yellows go to the user.** Don't auto-resolve. The whole point of yellow is that it needs human judgment.
- **Reds go to rollback.** Don't try to hot-fix a red gate in place — rollback first, investigate second.
