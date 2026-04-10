---
name: openclaw-troubleshooting-compound
description: Use after resolving an OpenClaw troubleshooting incident to capture learnings. Drafts a structured incident-log entry and optional error-signature additions, then applies on user confirmation.
---

# Compound Learnings

This skill closes the loop after an OpenClaw troubleshooting session. It drafts structured learnings from what just happened and applies them on confirmation — so the next session starts smarter without requiring the user to write anything manually.

Learnings are written to the **local** installed copy of the troubleshooting skill. They are specific to this user's environment — exact paths, ports, profile names, config quirks. This is personal institutional memory, not upstream documentation.

## When to trigger

- The user explicitly runs `/openclaw-troubleshooting-compound`
- The troubleshooting skill (`openclaw-troubleshooting`) suggests it after a resolution

## Workflow

### 1. Gather context

Review the current conversation for:

- **Symptoms**: What the user reported and what diagnostic output showed
- **Root cause**: What was actually wrong
- **Dead ends**: Approaches that were tried but failed or wasted time
- **Fix**: What actually resolved the issue, step by step
- **Prevention**: What would have avoided this entirely or caught it faster

Also read the current state of these files in the **locally installed** `openclaw-troubleshooting` skill directory:

- `references/local/incident-log.md` — to avoid duplicating an existing local entry
- `references/local/common-signatures.md` — to check if new local error signatures should be added
- `references/incident-log.md` — shipped patterns, for context (do not write to this file)
- `references/common-signatures.md` — shipped signatures, for context (do not write to this file)

### 2. Locate the local skill directory

The compound skill writes to the user's installed copy of `openclaw-troubleshooting`, not to a git checkout or upstream repo. Find it by checking these locations in order:

1. A sibling directory: `../openclaw-troubleshooting/` relative to this skill
2. `~/.claude/skills/openclaw-troubleshooting/`
3. `~/.openclaw/skills/openclaw-troubleshooting/`
4. The workspace `skills/openclaw-troubleshooting/` if present

If the directory is a symlink, follow it — write to whatever the symlink points to.

### 3. Draft the learnings

Produce two artifacts for the user to review:

**A. Incident log entry** (always)

Draft a structured entry following this format:

```markdown
## Short description of the incident

**Date:** YYYY-MM-DD

**Environment:** Relevant setup details (profile, OS, service manager, ports, paths).

**Symptoms:** What the user saw.

**Root cause:** What was actually wrong.

**What didn't work:** Approaches that failed or wasted time.

**What fixed it:** The actual fix, step by step. Include exact commands that worked.

**Prevention:** What would have avoided this or caught it faster next time.
```

Include specific details from this user's environment: exact paths, port numbers, profile names, config file locations, service labels. These details are what make the entry useful for this specific user's future sessions.

**B. New error signatures** (if applicable)

Draft new rows for the common-signatures table if the incident surfaced error strings or log signatures that aren't already covered:

```markdown
| `exact error string or log pattern` | Next action description. |
```

### 4. Deduplication check

Before presenting the draft:

- Check `references/local/incident-log.md` for existing local entries with the **same root cause**. If found, propose updating that entry with new details instead of creating a new one.
- Also check `references/incident-log.md` (shipped patterns). If the shipped file already has a general version of this incident, the local entry should focus on environment-specific details that go beyond the general pattern — don't duplicate what's already shipped.
- If the root cause is related but distinct, create a new entry.

### 5. Present and confirm

Show the user:

1. The drafted incident-log entry (or proposed updates to an existing entry)
2. Any new common-signatures rows
3. Which files will be modified and where they live on disk

Ask: **"Should I apply these learnings?"**

Wait for explicit confirmation. The user may:
- Approve as-is
- Request edits (apply their changes, then confirm again)
- Decline (do nothing)

### 6. Apply

On confirmation:

1. Create `references/local/` directory if it doesn't exist
2. If `references/local/incident-log.md` doesn't exist, create it with the header:
   ```
   # Local Incident Log
   
   Environment-specific learnings from this machine's troubleshooting sessions. This file is gitignored and written by `/openclaw-troubleshooting-compound`.
   ```
3. Append the incident-log entry to `references/local/incident-log.md` (add a `---` separator before the new entry), or update an existing local entry if deduplicating
4. If `references/local/common-signatures.md` doesn't exist and there are new signatures, create it with the header and table header:
   ```
   # Local Signatures
   
   Environment-specific error signatures from this machine. This file is gitignored and written by `/openclaw-troubleshooting-compound`.
   
   | Signature or symptom | Next action |
   | --- | --- |
   ```
5. Append any new signature rows to `references/local/common-signatures.md`
6. Show the user the exact changes made

These files are gitignored — they won't show up in `git status` or accidentally get pushed upstream.

## Quality rules

- **Be specific, not generic.** "Gateway runs on port 18789 under `--profile dev` with state at `~/.openclaw-dev`" is more useful than "check which profile is active." The troubleshooting skill already has the generic guidance — this log exists for the specifics.
- **Include exact commands that worked.** Future sessions can copy-paste instead of rediscovering.
- **One entry per root cause.** If an incident had cascading failures, focus on what started the chain. Mention the cascade in the symptoms.
- **Error signatures should use the exact string** from logs or terminal output, not a paraphrase.
- **Keep entries terse but complete.** This is a lookup table, not a postmortem narrative.
