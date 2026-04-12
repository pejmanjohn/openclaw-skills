---
name: openclaw-troubleshooting-compound
description: Use after resolving an OpenClaw troubleshooting incident to capture learnings. Drafts a structured incident-log entry and optional error-signature additions, then applies on user confirmation.
---

# Compound Learnings

This skill closes the loop after an OpenClaw troubleshooting session. It drafts structured learnings from what just happened and applies them on confirmation — so the next session starts smarter without requiring the user to write anything manually.

Learnings are written to a **shared local memory** directory at the repo root (`local/memory/`). They are specific to this user's environment — exact paths, ports, profile names, config quirks. This is personal institutional memory, not upstream documentation. Multiple installs (Claude Code, Codex, OpenClaw itself) sharing the same source checkout all read and write the same memory.

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

Also read the current state of these files:

- `$REPO_ROOT/local/memory/incident-log.md` — to avoid duplicating an existing local entry
- `$REPO_ROOT/local/memory/common-signatures.md` — to check if new local error signatures should be added
- `$REPO_ROOT/skills/openclaw-troubleshooting/playbooks/incident-log.md` — shipped patterns, for context (do not write to this file)
- `$REPO_ROOT/skills/openclaw-troubleshooting/playbooks/common-signatures.md` — shipped signatures, for context (do not write to this file)

### 2. Locate the shared local memory directory

The compound skill writes to the shared `local/memory/` directory at the repo root — not to any skill-specific subdirectory. All installs (Claude Code, Codex, OpenClaw itself) that symlink back to the same source checkout share this directory automatically.

**IMPORTANT:** The repo root is NOT your current working directory. It is the directory where the skill source checkout lives on disk. You must resolve it explicitly.

Run this command to find the repo root:

```bash
REPO_ROOT=""
for d in \
  ~/.claude/skills/openclaw-instance-discovery \
  ~/.claude/skills/openclaw-troubleshooting \
  ~/.openclaw/skills/openclaw-troubleshooting \
  ~/.codex/skills/openclaw-troubleshooting \
  ~/src/openclaw-skills/skills/openclaw-troubleshooting; do
  if [ -e "$d" ]; then
    resolved="$(readlink "$d" 2>/dev/null || echo "$d")"
    candidate="$(cd "$resolved/../.." 2>/dev/null && pwd)"
    if [ -d "$candidate/local" ] && [ -d "$candidate/skills" ]; then
      REPO_ROOT="$candidate"
      break
    fi
  fi
done
echo "${REPO_ROOT:?Could not find openclaw-skills repo root}"
```

The result must contain both `local/` and `skills/` directories. Then use `$REPO_ROOT/local/memory/` for all read and write operations below.

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

- Check `$REPO_ROOT/local/memory/incident-log.md` for existing local entries with the **same root cause**. If found, propose updating that entry with new details instead of creating a new one.
- Also check `$REPO_ROOT/skills/openclaw-troubleshooting/playbooks/incident-log.md` (shipped patterns). If the shipped file already has a general version of this incident, the local entry should focus on environment-specific details that go beyond the general pattern — don't duplicate what's already shipped.
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

1. Create `$REPO_ROOT/local/memory/` directory if it doesn't exist
2. If `$REPO_ROOT/local/memory/incident-log.md` doesn't exist, create it with the header:
   ```
   # Local Incident Log
   
   Environment-specific learnings from this machine's troubleshooting sessions. This file is gitignored and written by `/openclaw-troubleshooting-compound`.
   ```
3. Append the incident-log entry to `$REPO_ROOT/local/memory/incident-log.md` (add a `---` separator before the new entry), or update an existing local entry if deduplicating
4. If `$REPO_ROOT/local/memory/common-signatures.md` doesn't exist and there are new signatures, create it with the header and table header:
   ```
   # Local Signatures
   
   Environment-specific error signatures from this machine. This file is gitignored and written by `/openclaw-troubleshooting-compound`.
   
   | Signature or symptom | Next action |
   | --- | --- |
   ```
5. Append any new signature rows to `$REPO_ROOT/local/memory/common-signatures.md`
6. Show the user the exact changes made

These files are gitignored — they won't show up in `git status` or accidentally get pushed upstream.

## Quality rules

- **Be specific, not generic.** "Gateway runs on port 18789 under `--profile dev` with state at `~/.openclaw-dev`" is more useful than "check which profile is active." The troubleshooting skill already has the generic guidance — this log exists for the specifics.
- **Include exact commands that worked.** Future sessions can copy-paste instead of rediscovering.
- **One entry per root cause.** If an incident had cascading failures, focus on what started the chain. Mention the cascade in the symptoms.
- **Error signatures should use the exact string** from logs or terminal output, not a paraphrase.
- **Keep entries terse but complete.** This is a lookup table, not a postmortem narrative.
