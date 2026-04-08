import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class RepositoryShapeTests(unittest.TestCase):
    def test_task1_directory_skeleton_exists(self) -> None:
        expected = [
            ROOT / "skills" / "openclaw-troubleshooting",
            ROOT / "skills" / "openclaw-troubleshooting" / "references",
            ROOT / "skills" / "openclaw-troubleshooting" / "scripts",
            ROOT / "skills" / "openclaw-troubleshooting" / "agents",
        ]
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_dir(), f"missing directory {path.relative_to(ROOT)}")


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

    def test_skill_includes_required_top_level_sections(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        for heading in [
            "## Quick start",
            "## Workflow",
            "## Reference map",
            "## Quality rules",
            "## Tooling/fallback notes",
        ]:
            self.assertIn(heading, text)

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

    def test_reference_files_exist_and_include_core_invariants(self) -> None:
        references = ROOT / "skills" / "openclaw-troubleshooting" / "references"
        expected = {
            "triage.md": ["# Triage", "## Contents", "## First 60 seconds", "openclaw status --all"],
            "gateway.md": ["# Gateway", "## Contents", "## Core checks", "openclaw gateway probe"],
            "config.md": ["# Config", "## Contents", "## Active config path", "openclaw config file"],
            "channels.md": ["# Channels", "## Contents", "## Core checks", "openclaw channels status --probe"],
            "tools-and-nodes.md": ["# Tools And Nodes", "## Contents", "## Core checks", "## Exec approvals"],
            "auth-and-pairing.md": ["# Auth And Pairing", "## Contents", "## DM pairing", "## Device pairing"],
            "common-signatures.md": ["# Common Signatures", "## Contents", "| Signature or symptom | Next action |", "gateway probe"],
            "validation-scenarios.md": ["# Validation Scenarios", "## Contents", "## Scenario: missing command from website docs", "Pass expectations:"],
        }
        for name, phrases in expected.items():
            path = references / name
            with self.subTest(reference=name):
                self.assertTrue(path.is_file(), f"missing reference {name}")
                text = path.read_text()
                for phrase in phrases:
                    self.assertIn(phrase, text)


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
            fake.write_text("#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then echo 'openclaw 0.0-test'; exit 0; fi\necho \"CMD:$*\"\n")
            fake.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{td}:{env['PATH']}"
            result = subprocess.run(["bash", str(script)], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("CMD:status", result.stdout)
        self.assertIn("CMD:config file", result.stdout)
