# Post-Update Highlights

After all gates pass and the upgrade history ledger is written, give the user a short briefing on what's new in the parts of OpenClaw they actually use. The goal is signal, not a changelog dump — filter release notes against the user's inventory so the user only sees items that intersect with their setup.

This phase also runs in Phase 2 as a pre-update **soft-check** for BREAKING changes. The release-notes fetching logic is shared between Phase 2 and Phase 8 — only the filtering and output differ.

## Release-notes source (in priority order)

Try each source in this order until one returns usable content:

### 1. `openclaw docs` search

```bash
openclaw docs "release notes <version>"
openclaw docs "<version> changelog"
```

The local `openclaw docs` command searches the release's bundled documentation. When available, this is the most authoritative source because it matches the installed binary's version.

### 2. GitHub releases

Fetch the releases page for the OpenClaw repo. Most canonical path:

```
https://github.com/openclaw-ai/openclaw/releases
```

(Confirm the exact org/repo name from `openclaw --version` output or from the `update.root` package metadata if it's ambiguous.)

Each GitHub release has a tag matching the OpenClaw version (e.g. `v2026.4.15`) and a body with the changelog. Fetch the tag range from baseline → post version.

### 3. docs.openclaw.ai changelog pages

```
https://docs.openclaw.ai/changelog
```

Or per-version pages if they exist. Docs may be ahead of the installed binary — cite the source in the output so the user knows if they're seeing docs-level info vs. binary-level info.

### If no source works

Skip Phase 2 (pre-check) and Phase 8 (highlights) with a brief note: "Release notes were unreachable from <sources tried>. Update proceeded without the soft-check; all post-update gates passed, so the update is verified good." Do not block the update or the highlights on network failures reading changelog pages.

## Enumerating the version range

From the baseline snapshot:

- `installed.version` — the version before the update (e.g. `2026.4.5`)
- `target_version.latestVersion` — the version after the update (e.g. `2026.4.15`)

These are rarely adjacent. Between `2026.4.5` and `2026.4.15` there are ten point releases. Fetch notes for each release in the range — the set of intermediate versions matters because any one of them may have shipped the feature the user cares about.

Parsing strategy:

- The version format is `YYYY.M.N` where `N` is a per-month release counter. Iterate `N` from baseline+1 to target inclusive.
- Edge case: month boundaries. If baseline is `2026.3.30` and target is `2026.4.5`, the range spans two months. Fetch all `2026.3.*` releases above baseline AND all `2026.4.*` releases up to target.
- Do not parse versions as semver — `2026.4.15` is not "major 2026, minor 4, patch 15" semantically; OpenClaw uses date-based versioning.

## Inventory intersection

The baseline snapshot has the user's full configuration. For each release note item, classify it by which area it touches, then intersect against the user's inventory.

### Intersection matrix

| Release note area | Inventory field | Relevance rule |
|-------------------|-----------------|----------------|
| Channel provider (telegram, discord, bluebubbles, slack, whatsapp, etc.) | `channels[].provider` | Relevant iff the user has at least one channel with that provider. |
| Plugin name | `plugins[].id` | Relevant iff the plugin is present in baseline. |
| Cron / scheduler | `crons` (is the list non-empty) | Relevant iff the user has ≥1 cron. |
| Skill system | `skills` (is the list non-empty) | Relevant iff the user has ≥1 non-builtin skill. |
| Gateway | always relevant (every install has a gateway) | Include gateway improvements by default if they're user-visible. |
| Auth / pairing | `channels[].authProfile` (any present?) | Relevant iff the user has configured auth profiles. |
| Config / schema | `config_validate` status + the specific config keys mentioned in the release note | Relevant iff any mentioned config key appears in the user's `openclaw.json`. |
| CLI command surface | none directly — but tracks `commands_missing` changes | Include only significant new subcommands (e.g. a new top-level `openclaw <verb>`). |
| Tools / nodes / browser | baseline presence of tools/nodes configuration | Relevant iff the user has node/tool config. |
| Secrets | user's secret provider setup | Relevant iff the user uses non-default secret providers. |

### Filtering out noise

Skip these even if they technically intersect:

- "Bug fixes and improvements" without specifics
- Version bumps of transitive dependencies
- Internal refactors, test changes, CI changes
- Performance improvements under 10% unless the user specifically uses the affected code path
- Docs-only changes

Keep these even if the intersection is weak:

- Any BREAKING change in an area the user touches (even if they don't heavily use it)
- Security fixes — mention once at the top regardless of intersection
- Deprecations that apply to a user-configured feature

## Output shape

Group by area. Skip areas with no matches. Cap the total output at ~5-8 bullets — this is a briefing, not an exhaustive summary. If there are many more, mention that and point to the full changelog.

Example:

> **What's new for you** (2026.4.5 → 2026.4.15)
>
> **Telegram:**
> - 2026.4.9: reply-threading accuracy improved in group chats (you have 3 Telegram channels)
>
> **Cron scheduler:**
> - 2026.4.12: new `--at` flag for absolute-time scheduling (you have 6 cron jobs)
> - 2026.4.7: `openclaw cron runs` now supports `--since` filter
>
> **Skills:**
> - 2026.4.14: `skills.load.extraDirs` now supports glob patterns (you use 3 custom skill directories)
>
> **Gateway:**
> - 2026.4.11: probe endpoint returns structured auth status
>
> Full changelog: <link to source>

## Phase 2 mode (pre-update soft-check)

When this playbook is invoked during Phase 2 rather than Phase 8, the filter is different: look specifically for BREAKING changes, deprecations, and migration notes across the version range. Output shape:

> **Heads-up from the release notes**
>
> - **BREAKING (2026.4.10):** `openclaw config migrate` renamed to `openclaw config upgrade` (you have config files that may be affected)
> - **DEPRECATED (2026.4.7):** `openclaw daemon` subcommand removed in favor of `openclaw gateway` (you use neither — informational only)
>
> Proceed with the update? (This is informational — the update is still safe to run.)

If no BREAKING/deprecation items are found: "No breaking changes flagged across the version range. Safe to proceed."

## Quality rules

- **Filter aggressively.** A highlights briefing with 20 bullets the user doesn't care about is worse than no briefing. 5-8 is the sweet spot.
- **Intersect against actual inventory**, not against what the user "probably uses." The baseline snapshot is the ground truth.
- **Cite version per item.** The user should know when a feature landed so they can decide if it was in effect during earlier sessions.
- **Cite the source.** Link to the GitHub release, docs page, or `openclaw docs` search query used.
- **Never fabricate changelog items.** If you can't verify a release note from a concrete source, omit it. Hallucinated changelog entries erode trust faster than a terse briefing.
- **Skip this phase entirely on network failure.** Don't guess. A note saying "couldn't fetch release notes" is better than an invented summary.
- **Phase 2 is soft.** Non-blocking. Even if BREAKING changes are flagged, the update can still proceed at the user's discretion.
- **Phase 8 is after gates pass.** Never run the highlights briefing if any gate was red. A rollback situation is not the time for "here's what's new."
