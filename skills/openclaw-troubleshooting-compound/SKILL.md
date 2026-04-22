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

The incident log is read by the troubleshooting skill on every future run. Every word costs context on every future session. Write for that — aim for ~200-300 words per entry. If you're writing more, you're probably narrating the postmortem instead of indexing it.

Use this tight format:

```markdown
## <one-line title: what broke, root-cause-flavored if possible>

**Date:** YYYY-MM-DD
**Install:** <install-kind, OS, the one or two env details a future session needs to recognize this>
**Signature:** `<most distinctive error string or observable symptom, one line>`

**Root cause:** One or two sentences. What was actually wrong.

**Fix:**
```bash
# the minimum copy-pasteable commands that resolved it
```

**Trap:** *(include only if there's something non-obvious that would waste future-you's time — otherwise omit this section entirely)* one or two bullets max.
```

**Field discipline:**
- **Title** — root-cause-flavored, not symptom-flavored, so scanning the log tells you what class of problem each entry represents.
- **Install** — one line. The troubleshooting skill can query live state; this field is for recognition, not re-derivation. Example: `macOS, package/pnpm, default profile`.
- **Signature** — the exact error string a future session would grep for. Goes in code ticks. One line.
- **Root cause** — plain prose, 1-2 sentences. Don't restate symptoms; explain what was happening underneath.
- **Fix** — a code block, nothing else. Commands as run, not described. If the fix required a multi-step manual procedure, keep the block minimal and link to a playbook section instead of inlining the procedure.
- **Trap** — omit by default. Only include if there's a concrete dead-end pattern a future session would fall into (e.g. "inspect/list commands don't trigger the lazy-stage, only load paths do"). Not for tutorial content.

**Do NOT include:**
- A separate **Symptoms** section — the Signature line does this job; longer symptom narratives bloat context without adding lookup value.
- A **What didn't work** section for every entry — only the `Trap:` bullets above, and only when genuinely non-obvious. Most failed hypotheses are noise in a log file.
- A **Prevention** section — if prevention means "edit a skill/playbook", that belongs in a PR to this repo, not the incident log. If it means "be careful", it's too generic to be useful. The log captures what happened; the skills capture how to avoid it next time.
- Environment details beyond the one-line Install field — paths/ports/versions that future sessions can trivially query from live state.

**When your draft runs long:** cut paragraphs to sentences, cut sentences to clauses, cut clauses to code comments inside the Fix block. If the incident genuinely can't be compressed, the entry might be describing multiple distinct failures — split it into separate root-cause-specific entries instead of one sprawling one.

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

- **The incident log is a lookup table, not a postmortem narrative.** The troubleshooting skill loads it into context on every future run. Aim for ~200-300 words per entry. If you're writing more, delete before you write more.
- **One entry per root cause.** Cascading failures? Focus on what started the chain; mention the cascade inside the Root-cause sentence if it matters.
- **Title on root cause, not symptom.** "Bundled plugin staging incomplete on pnpm install" scans better than "openclaw update ERROR".
- **Signature strings are exact.** Copy-paste from terminal or logs, in code ticks. Not paraphrased, not lowercased, not prettied.
- **Commands, not descriptions.** The Fix block is literal shell. If you catch yourself writing "first X, then Y", rewrite as commands.
- **Omit empty sections.** Every field is opt-in if there's nothing useful to put there. Don't keep a Trap bullet just because the template has that slot.
- **Environment minimalism.** One line of install shape. Live state is queryable; frozen snapshots bloat context without paying it back.
- **Error signatures use the exact string** from logs or terminal output, not a paraphrase.
