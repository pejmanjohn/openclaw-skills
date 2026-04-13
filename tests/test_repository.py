import json
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
            ROOT / "scripts",
            ROOT / "skills" / "openclaw-troubleshooting",
            ROOT / "skills" / "openclaw-troubleshooting" / "playbooks",
            ROOT / "skills" / "openclaw-troubleshooting" / "scripts",
            ROOT / "skills" / "openclaw-troubleshooting" / "agents",
            ROOT / "skills" / "openclaw-instance-discovery",
            ROOT / "skills" / "openclaw-instance-discovery" / "playbooks",
            ROOT / "local",
            ROOT / "local" / "memory",
            ROOT / "local" / "state",
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
            "docs-navigation.md",
            "config-writing.md",
        ]:
            self.assertIn(name, text)

    def test_reference_files_exist_and_include_core_invariants(self) -> None:
        playbooks = ROOT / "skills" / "openclaw-troubleshooting" / "playbooks"
        expected = {
            "triage.md": [
                "# Triage",
                "## Contents",
                "## First 60 seconds",
                "openclaw [--profile X] status --all",
                "instances.json",
                "verify",
                "Option B",
            ],
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
                "## Scenario: first-time user with no instance registry",
                "Pass expectations:",
            ],
            "docs-navigation.md": [
                "# Docs Navigation",
                "## Core rule",
                "summary",
                "read_when",
                "title",
                "## Search strategy",
                "Docs are for intended behavior. The installed CLI and machine state are still runtime truth.",
            ],
            "config-writing.md": [
                "# Config Writing",
                "## Core rule",
                "Never batch-write the entire `openclaw.json`.",
                "## Required sequence",
                "### 1. Resolve the active target first",
                "### 6. Validate immediately",
                "### 7. Revert immediately on validation failure",
            ],
        }
        for name, phrases in expected.items():
            path = playbooks / name
            with self.subTest(playbook=name):
                self.assertTrue(path.is_file(), f"missing playbook {name}")
                text = path.read_text()
                for phrase in phrases:
                    self.assertIn(phrase, text)

    def test_skill_description_includes_natural_language_phrasings(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        front = text.split("---")[1] if text.startswith("---") else text.split("---")[0]
        for phrase in [
            "isn't working",
            "isn't responding",
            "not replying",
            "won't load",
            "won't start",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, front)

    def test_skill_points_to_docs_navigation_guidance(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        triage = (ROOT / "skills" / "openclaw-troubleshooting" / "playbooks" / "triage.md").read_text()
        for haystack in [text, triage]:
            self.assertIn("docs-navigation.md", haystack)
        self.assertIn("summary", text)
        self.assertIn("read_when", text)

    def test_skill_points_to_config_writing_guidance(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        config_playbook = (ROOT / "skills" / "openclaw-troubleshooting" / "playbooks" / "config.md").read_text()
        for haystack in [text, config_playbook]:
            self.assertIn("config-writing.md", haystack)
        self.assertIn("Never batch-write the entire `openclaw.json`.", (ROOT / "skills" / "openclaw-troubleshooting" / "playbooks" / "config-writing.md").read_text())


class RepositoryDocumentationTests(unittest.TestCase):
    def test_readme_covers_installation_and_local_first_model(self) -> None:
        text = (ROOT / "README.md").read_text()
        for phrase in [
            "openclaw-troubleshooting",
            "openclaw-instance-discovery",
            "openclaw-troubleshooting-compound",
            "local binary/help/config/state/logs",
            "docs.openclaw.ai",
            "latest release",
            "Workspace: `<workspace>/skills`",
            "Project agent skills: `<workspace>/.agents/skills`",
            "Personal agent skills: `~/.agents/skills`",
            "Managed/local: `~/.openclaw/skills`",
            "## OpenClaw: Install",
            "git clone https://github.com/pejmanjohn/openclaw-skills.git ~/src/openclaw-skills",
            "git -C ~/src/openclaw-skills pull",
            "install-openclaw-skill.sh",
            "## Codex: Install",
            "~/.codex/skills",
            "install-codex-skill.sh",
            "restart Codex",
            "## Claude Code: Install",
            "install-claude-skill.sh",
            ".claude/skills/openclaw-troubleshooting/SKILL.md",
            "Future expansion",
            "## Instance Discovery",
            "## Shared Local Memory",
            "local/memory/",
            "local/state/",
            "instances.json",
            "auto-trigger",
        ]:
            with self.subTest(phrase=phrase):
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


class InstallScriptTests(unittest.TestCase):
    def test_codex_install_script_creates_symlink_in_codex_home(self) -> None:
        script = ROOT / "scripts" / "install-codex-skill.sh"
        with tempfile.TemporaryDirectory() as td:
            codex_home = pathlib.Path(td) / "codex-home"
            env = os.environ.copy()
            env["HOME"] = td
            env["CODEX_HOME"] = str(codex_home)
            result = subprocess.run(["/bin/sh", str(script)], capture_output=True, text=True, env=env)
            target = codex_home / "skills" / "openclaw-troubleshooting"
            self.assertEqual(result.returncode, 0)
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), ROOT / "skills" / "openclaw-troubleshooting")

    def test_claude_install_script_creates_symlink_in_requested_dir(self) -> None:
        script = ROOT / "scripts" / "install-claude-skill.sh"
        with tempfile.TemporaryDirectory() as td:
            dest_dir = pathlib.Path(td) / "project" / ".claude" / "skills"
            env = os.environ.copy()
            env["HOME"] = td
            result = subprocess.run(
                ["/bin/sh", str(script), "--dest", str(dest_dir)],
                capture_output=True,
                text=True,
                env=env,
            )
            target = dest_dir / "openclaw-troubleshooting"
            self.assertEqual(result.returncode, 0)
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), ROOT / "skills" / "openclaw-troubleshooting")

    def test_openclaw_install_script_creates_symlink_in_override_dir(self) -> None:
        script = ROOT / "scripts" / "install-openclaw-skill.sh"
        with tempfile.TemporaryDirectory() as td:
            env = os.environ.copy()
            env["HOME"] = td
            env["OPENCLAW_SKILLS_DIR"] = str(pathlib.Path(td) / "openclaw-skills")
            result = subprocess.run(["/bin/sh", str(script)], capture_output=True, text=True, env=env)
            target = pathlib.Path(env["OPENCLAW_SKILLS_DIR"]) / "openclaw-troubleshooting"
            self.assertEqual(result.returncode, 0)
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), ROOT / "skills" / "openclaw-troubleshooting")


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


class TopLevelLocalLayoutTests(unittest.TestCase):
    def test_local_directory_exists_at_repo_root(self) -> None:
        self.assertTrue((ROOT / "local").is_dir(), "missing top-level local/")
        self.assertTrue((ROOT / "local" / "memory").is_dir(), "missing local/memory/")
        self.assertTrue((ROOT / "local" / "state").is_dir(), "missing local/state/")

    def test_local_subdirectories_have_gitkeep_files(self) -> None:
        self.assertTrue((ROOT / "local" / "memory" / ".gitkeep").is_file())
        self.assertTrue((ROOT / "local" / "state" / ".gitkeep").is_file())

    def test_local_state_files_are_gitignored(self) -> None:
        result = subprocess.run(
            ["git", "check-ignore", "-q", "local/state/instances.json"],
            cwd=ROOT, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, "local/state/instances.json should be gitignored")

    def test_local_memory_files_are_gitignored(self) -> None:
        result = subprocess.run(
            ["git", "check-ignore", "-q", "local/memory/incident-log.md"],
            cwd=ROOT, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, "local/memory/incident-log.md should be gitignored")

    def test_gitkeep_files_are_not_ignored(self) -> None:
        for keeper in ("local/memory/.gitkeep", "local/state/.gitkeep"):
            with self.subTest(path=keeper):
                result = subprocess.run(
                    ["git", "check-ignore", "-q", keeper],
                    cwd=ROOT, capture_output=True,
                )
                self.assertEqual(result.returncode, 1, f"{keeper} should NOT be gitignored")

    def test_per_skill_references_local_no_longer_exists(self) -> None:
        legacy = ROOT / "skills" / "openclaw-troubleshooting" / "playbooks" / "local"
        self.assertFalse(legacy.exists(), "playbooks/local/ should be gone after the hoist")


class InstanceDiscoverySkillMetadataTests(unittest.TestCase):
    SKILL_PATH = ROOT / "skills" / "openclaw-instance-discovery" / "SKILL.md"

    def test_skill_file_exists(self) -> None:
        self.assertTrue(self.SKILL_PATH.is_file(), "missing skills/openclaw-instance-discovery/SKILL.md")

    def test_skill_frontmatter_is_valid(self) -> None:
        text = self.SKILL_PATH.read_text()
        self.assertIn("name: openclaw-instance-discovery", text)
        self.assertIn("description: Use when", text)

    def test_skill_description_includes_natural_language_triggers(self) -> None:
        text = self.SKILL_PATH.read_text()
        for needle in ["find", "openclaw", "rescan", "discover", "instance"]:
            with self.subTest(needle=needle):
                self.assertIn(needle, text.lower())

    def test_skill_description_mentions_auto_trigger(self) -> None:
        text = self.SKILL_PATH.read_text()
        self.assertIn("auto-triggered", text.lower())

    def test_skill_includes_required_top_level_sections(self) -> None:
        text = self.SKILL_PATH.read_text()
        for heading in ["## Quick start", "## Workflow", "## Reference map", "## Quality rules"]:
            with self.subTest(heading=heading):
                self.assertIn(heading, text)

    def test_reference_map_mentions_each_playbook_file(self) -> None:
        text = self.SKILL_PATH.read_text()
        for name in ["discovery-sequence.md", "fallback-ladder.md", "registry-contract.md"]:
            with self.subTest(name=name):
                self.assertIn(name, text)

    def test_skill_grounds_in_openclaw_docs(self) -> None:
        text = self.SKILL_PATH.read_text()
        self.assertIn("docs.openclaw.ai", text)


class DiscoverySequencePlaybookTests(unittest.TestCase):
    PLAYBOOK_PATH = (
        ROOT / "skills" / "openclaw-instance-discovery"
        / "playbooks" / "discovery-sequence.md"
    )

    def test_playbook_exists(self) -> None:
        self.assertTrue(self.PLAYBOOK_PATH.is_file())

    def test_playbook_has_six_phases(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        for phase in [
            "## Phase 1",
            "## Phase 2",
            "## Phase 3",
            "## Phase 4",
            "## Phase 5",
            "## Phase 6",
        ]:
            with self.subTest(phase=phase):
                self.assertIn(phase, text)

    def test_phase_1_uses_native_openclaw_commands(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        for command in [
            "openclaw --version",
            "openclaw gateway status --deep --json",
            "openclaw gateway probe --json",
            "openclaw config file",
        ]:
            with self.subTest(command=command):
                self.assertIn(command, text)

    def test_phase_2_inspects_launchd_layout(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        for needle in [
            "launchctl list",
            "ai.openclaw",
            "OPENCLAW_PROFILE",
            "OPENCLAW_CONFIG_PATH",
            "OPENCLAW_STATE_DIR",
            "OPENCLAW_GATEWAY_PORT",
        ]:
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_phase_4_documents_url_token_fallback(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        self.assertIn("--url ws://127.0.0.1", text)
        self.assertIn("--token", text)
        self.assertIn("--profile", text)

    def test_phase_6_handles_single_and_multi_instance_cases(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        self.assertIn("Single-instance", text)
        self.assertIn("Multi-instance", text)
        self.assertIn("default", text)
        self.assertIn("instance-2", text)

    def test_playbook_grounds_in_openclaw_docs(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        self.assertIn("docs.openclaw.ai", text)


class FallbackLadderPlaybookTests(unittest.TestCase):
    PLAYBOOK_PATH = (
        ROOT / "skills" / "openclaw-instance-discovery"
        / "playbooks" / "fallback-ladder.md"
    )

    def test_playbook_exists(self) -> None:
        self.assertTrue(self.PLAYBOOK_PATH.is_file())

    def test_ladder_checks_common_install_paths(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        for path in [
            "/usr/local/bin/openclaw",
            "/opt/homebrew/bin/openclaw",
            "/Applications/OpenClaw.app",
        ]:
            with self.subTest(path=path):
                self.assertIn(path, text)

    def test_ladder_checks_common_config_locations(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        for path in [
            "~/.openclaw/openclaw.json",
            "~/Library/Application Support/OpenClaw",
        ]:
            with self.subTest(path=path):
                self.assertIn(path, text)

    def test_ladder_includes_last_resort_user_question(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        self.assertIn("last resort", text.lower())
        self.assertIn("never dead-end", text.lower())

    def test_ladder_mentions_walking_the_steps_in_order(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        for step in ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5", "Step 6"]:
            with self.subTest(step=step):
                self.assertIn(step, text)


class RegistryContractPlaybookTests(unittest.TestCase):
    PLAYBOOK_PATH = (
        ROOT / "skills" / "openclaw-instance-discovery"
        / "playbooks" / "registry-contract.md"
    )

    def test_playbook_exists(self) -> None:
        self.assertTrue(self.PLAYBOOK_PATH.is_file())

    def _extract_first_json_block(self) -> dict:
        text = self.PLAYBOOK_PATH.read_text()
        marker = "```json"
        start = text.index(marker) + len(marker)
        end = text.index("```", start)
        return json.loads(text[start:end])

    def test_example_registry_parses_as_json(self) -> None:
        sample = self._extract_first_json_block()
        self.assertIsInstance(sample, dict)

    def test_example_registry_has_required_top_level_fields(self) -> None:
        sample = self._extract_first_json_block()
        for field in ("version", "updatedAt", "defaultInstanceId", "instances"):
            with self.subTest(field=field):
                self.assertIn(field, sample)

    def test_example_registry_version_is_one(self) -> None:
        sample = self._extract_first_json_block()
        self.assertEqual(sample["version"], 1)

    def test_example_registry_default_instance_resolves(self) -> None:
        sample = self._extract_first_json_block()
        ids = [inst["id"] for inst in sample["instances"]]
        self.assertIn(sample["defaultInstanceId"], ids)

    def test_each_instance_has_required_fields(self) -> None:
        sample = self._extract_first_json_block()
        for inst in sample["instances"]:
            with self.subTest(instance_id=inst.get("id")):
                self.assertIn("id", inst)
                self.assertIn("label", inst)

    def test_each_instance_includes_discoveredFrom(self) -> None:
        sample = self._extract_first_json_block()
        for inst in sample["instances"]:
            with self.subTest(instance_id=inst.get("id")):
                self.assertIn("discoveredFrom", inst)
                self.assertIsInstance(inst["discoveredFrom"], str)
                self.assertTrue(len(inst["discoveredFrom"]) > 0)

    def test_playbook_documents_field_guidance(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        for field in [
            "id", "label", "kind", "profile", "port",
            "configPath", "stateDir", "serviceLabel", "discoveredFrom",
        ]:
            with self.subTest(field=field):
                self.assertIn(field, text)

    def test_playbook_documents_ownership(self) -> None:
        text = self.PLAYBOOK_PATH.read_text()
        self.assertIn("Ownership", text)
        self.assertIn("writes", text.lower())
        self.assertIn("reads", text.lower())


class TroubleshootingRegistryIntegrationTests(unittest.TestCase):
    def test_skill_documents_registry_preflight(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        self.assertIn("local/state/instances.json", text)
        self.assertIn("preflight", text.lower())

    def test_skill_documents_auto_trigger_to_discovery(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        self.assertIn("openclaw-instance-discovery", text)
        self.assertIn("auto-trigger", text.lower())
        self.assertIn("missing", text.lower())

    def test_skill_documents_announce_target_step(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        self.assertIn("announce", text.lower())
        self.assertIn("plain language", text.lower())

    def test_skill_documents_override_grammar(self) -> None:
        text = (ROOT / "skills" / "openclaw-troubleshooting" / "SKILL.md").read_text()
        self.assertIn("use the other one", text.lower())
