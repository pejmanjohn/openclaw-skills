import pathlib
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
