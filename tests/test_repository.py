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
