---
name: openclaw-troubleshooting-compound
description: Use after resolving an OpenClaw troubleshooting incident to capture learnings. Drafts a structured incident-log entry and optional error-signature additions, then applies on user confirmation.
---

# Compound Learnings

This skill closes the loop after an OpenClaw troubleshooting session. It drafts structured learnings from what just happened and applies them on confirmation — so the next session starts smarter without requiring the user to write anything manually.

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

Also read the current state of these files (they are relative to the `openclaw-troubleshooting` skill directory):

- `references/incident-log.md` — to avoid duplicating an existing entry
- `references/common-signatures.md` — to check if new error signatures should be added

### 2. Draft the learnings

Produce two artifacts for the user to review:

**A. Incident log entry** (always)

Draft a structured entry following this format:

```markdown
## Short description of the incident

**Precondition:** (optional) Setup-specific conditions that make this relevant.

**Symptoms:** What the user saw.

**Root cause:** What was actually wrong.

**What didn't work:** Approaches that failed or wasted time.

**What fixed it:** The actual fix, step by step.

**Prevention:** How to avoid this in the future.
```

**B. New error signatures** (if applicable)

Draft new rows for the common-signatures table if the incident surfaced error strings or log signatures that aren't already covered:

```markdown
| `exact error string or log pattern` | Next action description. |
```

### 3. Generalization check

Before presenting the draft, review it for:

- **Machine-specific details**: Replace specific paths, ports, profile names, hostnames with generic placeholders or describe the pattern instead
- **Duplication**: If an existing incident-log entry covers the same root cause, propose updating that entry instead of adding a new one
- **Relevance**: Only include learnings that would help someone else hitting the same problem. Skip anything that's only useful in this exact environment.

### 4. Present and confirm

Show the user:

1. The drafted incident-log entry
2. Any new common-signatures rows
3. Which files will be modified

Ask: **"Should I apply these learnings?"**

Wait for explicit confirmation. The user may:
- Approve as-is
- Request edits (apply their changes, then confirm again)
- Decline (do nothing)

### 5. Apply

On confirmation:

1. Append the incident-log entry to `references/incident-log.md` (add a `---` separator before the new entry)
2. Insert any new signature rows into the table in `references/common-signatures.md` (before the first existing row, to keep new entries prominent)
3. Show the user the exact changes made

Do NOT commit or push. The user decides when to commit. If they want to contribute upstream, they can create a PR from the changes.

## Quality rules

- Keep entries terse. The incident log is a lookup table, not a narrative.
- Generalize aggressively. "Port mismatch between config and service manager" is useful. "Port 18789 didn't match port 19001 on Ada's Mac mini" is not.
- One entry per root cause. If an incident had multiple cascading failures, focus on the root cause that started the chain.
- Don't duplicate. If the root cause is already in the incident log, update the existing entry with any new details instead of adding a new one.
- Error signatures should use the exact string a user would see in logs or terminal output, not a paraphrase.
