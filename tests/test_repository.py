import os
import pathlib
import subprocess
import tempfile
import time
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
            "install/setup",
            "gateway",
            "dashboard",
            "control UI",
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
            "tools-and-nodes.md": [
                "# Tools And Nodes",
                "## Contents",
                "## Core checks",
                "## Exec approvals",
                "openclaw approvals get --gateway",
                "openclaw.extensions",
            ],
            "auth-and-pairing.md": ["# Auth And Pairing", "## Contents", "## DM pairing", "## Device pairing"],
            "common-signatures.md": [
                "# Common Signatures",
                "## Contents",
                "| Signature or symptom | Next action |",
                "gateway probe",
                "SYSTEM_RUN_DENIED",
                "openclaw.extensions",
            ],
            "validation-scenarios.md": [
                "# Validation Scenarios",
                "## Contents",
                "## Scenario: missing command from website docs",
                "## Scenario: OpenClaw installed but no replies on Telegram",
                "## Scenario: exec suddenly asks for approval",
                "## Scenario: safe config change and validation",
                "## Scenario: plugin install missing openclaw.extensions",
                "Pass expectations:",
            ],
        }
        for name, phrases in expected.items():
            path = references / name
            with self.subTest(reference=name):
                self.assertTrue(path.is_file(), f"missing reference {name}")
                text = path.read_text()
                for phrase in phrases:
                    self.assertIn(phrase, text)


class RepositoryDocumentationTests(unittest.TestCase):
    def test_readme_covers_installation_and_local_first_model(self) -> None:
        text = (ROOT / "README.md").read_text()
        for phrase in [
            "openclaw-troubleshooting",
            "local binary/help/config/state/logs",
            "docs.openclaw.ai",
            "latest release",
            "Workspace: `<workspace>/skills`",
            "Project agent skills: `<workspace>/.agents/skills`",
            "Personal agent skills: `~/.agents/skills`",
            "Managed/local: `~/.openclaw/skills`",
            "Install with OpenClaw",
            "Install with Codex",
            "~/.codex/skills",
            "restart Codex",
            "Install with Claude Code",
            ".claude/skills/openclaw-troubleshooting/SKILL.md",
            "Future expansion",
        ]:
            self.assertIn(phrase, text)

    def test_license_is_mit(self) -> None:
        text = (ROOT / "LICENSE").read_text()
        self.assertIn("MIT License", text)
        self.assertIn("Permission is hereby granted, free of charge", text)

    def test_codex_metadata_is_thin_and_secondary(self) -> None:
        path = ROOT / "skills" / "openclaw-troubleshooting" / "agents" / "openai.yaml"
        text = path.read_text()
        self.assertIn("name: openclaw-troubleshooting", text)
        self.assertIn("description:", text)
        self.assertNotIn("disable-model-invocation", text)
        self.assertNotIn("allowed-tools", text)


class DiagnosticsScriptTests(unittest.TestCase):
    def test_script_checks_for_openclaw_before_processing_arguments(self) -> None:
        script = ROOT / "skills" / "openclaw-troubleshooting" / "scripts" / "collect-openclaw-diagnostics.sh"
        with tempfile.TemporaryDirectory() as td:
            env = os.environ.copy()
            env["PATH"] = td
            result = subprocess.run(
                ["/bin/sh", str(script), "--help"],
                capture_output=True,
                text=True,
                env=env,
            )
        output = result.stderr + result.stdout
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing required binary: openclaw", output)
        self.assertNotIn("Usage:", output)

    def test_script_runs_full_default_ladder_and_continues_after_failures(self) -> None:
        script = ROOT / "skills" / "openclaw-troubleshooting" / "scripts" / "collect-openclaw-diagnostics.sh"
        with tempfile.TemporaryDirectory() as td:
            fake = pathlib.Path(td) / "openclaw"
            command_log = pathlib.Path(td) / "commands.log"
            fake.write_text(
                "#!/bin/sh\n"
                "log_file=${OPENCLAW_FAKE_LOG:?}\n"
                "printf '%s\\n' \"$*\" >> \"$log_file\"\n"
                "if [ \"$1\" = \"--version\" ]; then echo 'openclaw 0.0-test'; exit 0; fi\n"
                "if [ \"$1\" = \"doctor\" ]; then echo 'doctor failed' >&2; exit 17; fi\n"
                "echo \"CMD:$*\"\n"
            )
            fake.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{td}:{env['PATH']}"
            env["OPENCLAW_FAKE_LOG"] = str(command_log)
            result = subprocess.run(["/bin/sh", str(script)], capture_output=True, text=True, env=env)
            commands = command_log.read_text().splitlines()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            commands,
            [
                "--version",
                "config file",
                "status",
                "status --all",
                "gateway probe",
                "gateway status",
                "doctor",
                "channels status --probe",
                "config validate",
                "update status",
            ],
        )
        self.assertIn("== Version ==", result.stdout)
        self.assertIn("== Diagnostic ladder ==", result.stdout)
        self.assertIn("[exit 17]", result.stdout)
        self.assertIn("CMD:channels status --probe", result.stdout)
        self.assertIn("CMD:update status", result.stdout)
        self.assertNotIn("logs --follow", result.stdout)

    def test_script_prints_environment_overrides(self) -> None:
        script = ROOT / "skills" / "openclaw-troubleshooting" / "scripts" / "collect-openclaw-diagnostics.sh"
        with tempfile.TemporaryDirectory() as td:
            fake = pathlib.Path(td) / "openclaw"
            fake.write_text(
                "#!/bin/sh\n"
                "if [ \"$1\" = \"--version\" ]; then echo 'openclaw 0.0-test'; exit 0; fi\n"
                "echo \"CMD:$*\"\n"
            )
            fake.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{td}:{env['PATH']}"
            env["OPENCLAW_HOME"] = "/tmp/openclaw-home"
            env["OPENCLAW_STATE_DIR"] = "/tmp/openclaw-state"
            env["OPENCLAW_CONFIG_PATH"] = "/tmp/openclaw.json"
            env["OPENCLAW_LOG_LEVEL"] = "debug"
            result = subprocess.run(["/bin/sh", str(script)], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("OPENCLAW_HOME=/tmp/openclaw-home", result.stdout)
        self.assertIn("OPENCLAW_STATE_DIR=/tmp/openclaw-state", result.stdout)
        self.assertIn("OPENCLAW_CONFIG_PATH=/tmp/openclaw.json", result.stdout)
        self.assertIn("OPENCLAW_LOG_LEVEL=debug", result.stdout)

    def test_script_only_follows_logs_when_flagged_and_stops_quickly(self) -> None:
        script = ROOT / "skills" / "openclaw-troubleshooting" / "scripts" / "collect-openclaw-diagnostics.sh"
        with tempfile.TemporaryDirectory() as td:
            fake = pathlib.Path(td) / "openclaw"
            command_log = pathlib.Path(td) / "commands.log"
            fake.write_text(
                "#!/bin/sh\n"
                "log_file=${OPENCLAW_FAKE_LOG:?}\n"
                "printf '%s\\n' \"$*\" >> \"$log_file\"\n"
                "if [ \"$1\" = \"--version\" ]; then echo 'openclaw 0.0-test'; exit 0; fi\n"
                "if [ \"$1\" = \"logs\" ] && [ \"${2-}\" = \"--follow\" ]; then\n"
                "  echo 'streaming logs'\n"
                "  sleep 10\n"
                "  exit 0\n"
                "fi\n"
                "echo \"CMD:$*\"\n"
            )
            fake.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{td}:{env['PATH']}"
            env["OPENCLAW_FAKE_LOG"] = str(command_log)
            start = time.monotonic()
            result = subprocess.run(
                ["/bin/sh", str(script), "--follow-logs", "--follow-seconds", "1"],
                capture_output=True,
                text=True,
                env=env,
            )
            elapsed = time.monotonic() - start
            commands = command_log.read_text().splitlines()
        self.assertEqual(result.returncode, 0)
        self.assertLess(elapsed, 5)
        self.assertEqual(commands[-1], "logs --follow")
        self.assertIn("auto-stop after 1s", result.stdout)

    def test_script_skips_follow_logs_without_timeout_or_python3(self) -> None:
        script = ROOT / "skills" / "openclaw-troubleshooting" / "scripts" / "collect-openclaw-diagnostics.sh"
        with tempfile.TemporaryDirectory() as td:
            fake = pathlib.Path(td) / "openclaw"
            command_log = pathlib.Path(td) / "commands.log"
            fake.write_text(
                "#!/bin/sh\n"
                "log_file=${OPENCLAW_FAKE_LOG:?}\n"
                "printf '%s\\n' \"$*\" >> \"$log_file\"\n"
                "if [ \"$1\" = \"--version\" ]; then echo 'openclaw 0.0-test'; exit 0; fi\n"
                "echo \"CMD:$*\"\n"
            )
            fake.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = td
            env["OPENCLAW_FAKE_LOG"] = str(command_log)
            result = subprocess.run(
                ["/bin/sh", str(script), "--follow-logs", "--follow-seconds", "1"],
                capture_output=True,
                text=True,
                env=env,
            )
            commands = command_log.read_text().splitlines()
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("logs --follow", commands)
        self.assertIn("Skipping log follow: requires timeout or python3", result.stdout)

    def test_script_rejects_invalid_follow_seconds(self) -> None:
        script = ROOT / "skills" / "openclaw-troubleshooting" / "scripts" / "collect-openclaw-diagnostics.sh"
        with tempfile.TemporaryDirectory() as td:
            fake = pathlib.Path(td) / "openclaw"
            fake.write_text("#!/bin/sh\nexit 0\n")
            fake.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{td}:{env['PATH']}"
            result = subprocess.run(
                ["/bin/sh", str(script), "--follow-seconds", "abc"],
                capture_output=True,
                text=True,
                env=env,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Invalid value for --follow-seconds", result.stderr)
