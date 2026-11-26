from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FoundationTests(unittest.TestCase):
    def test_required_directories_exist(self):
        for directory in ("public-site", "owner-panel", "discord-host", "shared", "docs"):
            self.assertTrue((ROOT / directory).is_dir())

    def test_required_entrypoints_exist(self):
        for path in (
            "public-site/app/api/health/route.ts",
            "owner-panel/app/api/health/route.ts",
            "discord-host/main.py",
            "discord-host/app/main.py",
            "discord-host/alembic.ini",
            "shared/database/base.py",
            "public-site/app/layout.tsx",
            "owner-panel/app/layout.tsx",
        ):
            self.assertTrue((ROOT / path).is_file())

    def test_no_real_env_values_are_committed(self):
        for env_example in ROOT.rglob(".env.example"):
            content = env_example.read_text()
            for forbidden in ("MTE", "MTM", "postgresql://neondb_owner:"):
                self.assertNotIn(forbidden, content)


if __name__ == "__main__":
    unittest.main()
