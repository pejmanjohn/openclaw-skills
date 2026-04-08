# OpenClaw Troubleshooting Skill v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public, multi-agent-ready skill repo with a canonical `openclaw-troubleshooting` skill, supporting references, a repeatable diagnostics script, and installation docs for Codex and Claude Code.

**Architecture:** Keep one canonical skill source under `skills/openclaw-troubleshooting/` and treat local OpenClaw CLI/runtime state as primary truth. Add only thin agent-specific metadata where useful, and validate the repo with a small Python stdlib test harness plus scenario-based manual checks.

**Tech Stack:** Markdown, shell, YAML frontmatter, Python 3 stdlib `unittest`

---

## File Structure

- `LICENSE`
  - Repository license.
- `README.md`
  - Public repo overview, installation/use notes, architecture rationale, deferred work.
- `skills/openclaw-troubleshooting/SKILL.md`
  - Canonical agent-neutral skill definition.
- `skills/openclaw-troubleshooting/agents/openai.yaml`
  - Thin Codex-only metadata layer.
- `skills/openclaw-troubleshooting/references/*.md`
  - Progressive-disclosure troubleshooting references.
- `skills/openclaw-troubleshooting/scripts/collect-openclaw-diagnostics.sh`
  - Read-only diagnostics helper.
- `tests/test_repository.py`
  - Repo validation tests for structure, metadata, reference wiring, and diagnostics script behavior.

### Task 1: Create Repo Skeleton And Validation Harness

**Files:**
- Create: `tests/test_repository.py`
- Create: `skills/openclaw-troubleshooting/`
- Create: `skills/openclaw-troubleshooting/references/`
- Create: `skills/openclaw-troubleshooting/scripts/`
- Create: `skills/openclaw-troubleshooting/agents/`

- [ ] **Step 1: Write the failing test**

```python
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class RepositoryShapeTests(unittest.TestCase):
    def test_expected_v1_paths_exist(self) -> None:
        expected = [
            ROOT / "README.md",
            ROOT / "LICENSE",
            ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md",
            ROOT / "skills" / "openclaw-troubleshooting" / "references" / "triage.md",
            ROOT / "skills" / "openclaw-troubleshooting" / "scripts" / "collect-openclaw-diagnostics.sh",
        ]
        for path in expected:
            self.assertTrue(path.exists(), f"missing {path.relative_to(ROOT)}")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_repository.RepositoryShapeTests.test_expected_v1_paths_exist`
Expected: FAIL because the repo files do not exist yet.

- [ ] **Step 3: Create the directory skeleton**

```bash
mkdir -p tests \
  skills/openclaw-troubleshooting/references \
  skills/openclaw-troubleshooting/scripts \
  skills/openclaw-troubleshooting/agents
```

- [ ] **Step 4: Run the targeted test again**

Run: `python3 -m unittest tests.test_repository.RepositoryShapeTests.test_expected_v1_paths_exist`
Expected: still FAIL until the files themselves are added in later tasks.

- [ ] **Step 5: Commit**

```bash
git add tests skills docs/superpowers/plans/2026-04-08-openclaw-troubleshooting-v1.md
git commit -m "test: add repo validation harness skeleton"
```

### Task 2: Implement The Canonical Skill And Reference Map

**Files:**
- Create: `skills/openclaw-troubleshooting/SKILL.md`
- Create: `skills/openclaw-troubleshooting/references/triage.md`
- Create: `skills/openclaw-troubleshooting/references/gateway.md`
- Create: `skills/openclaw-troubleshooting/references/config.md`
- Create: `skills/openclaw-troubleshooting/references/channels.md`
- Create: `skills/openclaw-troubleshooting/references/tools-and-nodes.md`
- Create: `skills/openclaw-troubleshooting/references/auth-and-pairing.md`
- Create: `skills/openclaw-troubleshooting/references/common-signatures.md`
- Create: `skills/openclaw-troubleshooting/references/validation-scenarios.md`
- Modify: `tests/test_repository.py`

- [ ] **Step 1: Write the failing tests**

```python
class SkillMetadataTests(unittest.TestCase):
    def test_skill_frontmatter_uses_required_name_and_trigger_language(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        self.assertIn("name: openclaw-troubleshooting", text)
        self.assertIn("description: Use when", text)
        for needle in [
            "OpenClaw",
            "gateway",
            "dashboard",
            "channels",
            "auth",
            "pairing",
            "config",
            "tools",
            "nodes",
            "plugins",
        ]:
            self.assertIn(needle, text)

    def test_reference_map_mentions_each_reference_file(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        for name in [
            "triage.md",
            "gateway.md",
            "config.md",
            "channels.md",
            "tools-and-nodes.md",
            "auth-and-pairing.md",
            "common-signatures.md",
            "validation-scenarios.md",
        ]:
            self.assertIn(name, text)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_repository.SkillMetadataTests -v`
Expected: FAIL because `SKILL.md` and references are not implemented yet.

- [ ] **Step 3: Write the minimal implementation**

```markdown
Create `SKILL.md` with:
- frontmatter `name` and concise trigger-oriented `description`
- explicit local-first/version-aware workflow
- quick-start ladder
- reference map pointing to all reference files
- quality rules and fallback rules

Create each reference file with a short table of contents and focused troubleshooting content aligned to current OpenClaw docs.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_repository.SkillMetadataTests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_repository.py skills/openclaw-troubleshooting
git commit -m "feat: add canonical openclaw troubleshooting skill"
```

### Task 3: Implement The Diagnostics Script With Tests

**Files:**
- Create: `skills/openclaw-troubleshooting/scripts/collect-openclaw-diagnostics.sh`
- Modify: `tests/test_repository.py`

- [ ] **Step 1: Write the failing tests**

```python
import os
import subprocess
import tempfile

class DiagnosticsScriptTests(unittest.TestCase):
    def test_script_shows_missing_binary_message(self) -> None:
        script = ROOT / "skills" / "openclaw-troubleshooting" / "scripts" / "collect-openclaw-diagnostics.sh"
        result = subprocess.run(["bash", str(script)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("openclaw", result.stderr + result.stdout)

    def test_script_runs_read_only_ladder_against_fake_binary(self) -> None:
        script = ROOT / "skills" / "openclaw-troubleshooting" / "scripts" / "collect-openclaw-diagnostics.sh"
        with tempfile.TemporaryDirectory() as td:
            fake = pathlib.Path(td) / "openclaw"
            fake.write_text("#!/bin/sh\\nif [ \"$1\" = \"--version\" ]; then echo 'openclaw 0.0-test'; exit 0; fi\\necho \"CMD:$*\"\\n")
            fake.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f\"{td}:{env['PATH']}\"
            result = subprocess.run(["bash", str(script)], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("CMD:status", result.stdout)
        self.assertIn("CMD:config file", result.stdout)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_repository.DiagnosticsScriptTests -v`
Expected: FAIL because the script does not exist or does not implement the ladder.

- [ ] **Step 3: Write the minimal implementation**

```bash
Implement a shell script that:
- checks for `openclaw`
- prints section headers
- prints env override visibility
- runs `openclaw --version`
- runs `config file`, `status`, `status --all`, `gateway probe`, `gateway status`, `doctor`, `channels status --probe`, `config validate`
- supports optional `--follow-logs`
- uses a short timeout for follow mode
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_repository.DiagnosticsScriptTests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_repository.py skills/openclaw-troubleshooting/scripts/collect-openclaw-diagnostics.sh
git commit -m "feat: add repeatable openclaw diagnostics script"
```

### Task 4: Add README, License, Metadata, And Final Validation Coverage

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `skills/openclaw-troubleshooting/agents/openai.yaml`
- Modify: `tests/test_repository.py`

- [ ] **Step 1: Write the failing tests**

```python
class DocumentationTests(unittest.TestCase):
    def test_readme_explains_local_first_and_version_aware_design(self) -> None:
        text = (ROOT / "README.md").read_text()
        self.assertIn("local", text.lower())
        self.assertIn("same machine", text.lower())
        self.assertIn("latest release", text.lower())
        self.assertIn(".claude/skills", text)
        self.assertIn("Codex", text)

    def test_openai_metadata_is_thin_and_non_authoritative(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "agents" / "openai.yaml").read_text()
        self.assertIn("display_name:", text)
        self.assertIn("short_description:", text)
        self.assertNotIn("workflow:", text)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_repository.DocumentationTests -v`
Expected: FAIL because the README, license, and metadata are not implemented yet.

- [ ] **Step 3: Write the minimal implementation**

```markdown
README must cover:
- repo purpose and current scope
- canonical skill source and agent-neutral structure
- Codex install/use notes
- Claude Code install/use notes
- local-first and version-aware troubleshooting rationale
- deferred compatibility work

`agents/openai.yaml` must stay thin: display metadata only.
`LICENSE` should use MIT text.
```

- [ ] **Step 4: Run the full test suite**

Run: `python3 -m unittest tests.test_repository -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md LICENSE skills/openclaw-troubleshooting/agents/openai.yaml tests/test_repository.py
git commit -m "docs: add repository guidance and metadata"
```

### Task 5: Verify, Review, And Report

**Files:**
- Modify: `docs/superpowers/plans/2026-04-08-openclaw-troubleshooting-v1.md`

- [ ] **Step 1: Run repository verification**

```bash
python3 -m unittest tests.test_repository -v
bash -n skills/openclaw-troubleshooting/scripts/collect-openclaw-diagnostics.sh
git status --short
```

- [ ] **Step 2: Pressure-test the skill manually**

Check each scenario in `skills/openclaw-troubleshooting/references/validation-scenarios.md` against the final `SKILL.md` and confirm:
- trigger language is plausible
- first move is local evidence gathering
- reference routing is correct
- final step is verifiable

- [ ] **Step 3: Update completed checkboxes in this plan**

Mark the finished steps as complete for auditability.

- [ ] **Step 4: Commit plan tracking updates if needed**

```bash
git add docs/superpowers/plans/2026-04-08-openclaw-troubleshooting-v1.md
git commit -m "chore: record implementation progress"
```
