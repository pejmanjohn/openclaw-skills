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
