import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ApiFoundationTests(unittest.TestCase):
    def test_three_api_surfaces_exist(self):
        paths = (
            ROOT / "public-site/app/api",
            ROOT / "owner-panel/app/api",
            ROOT / "discord-host/app/api",
        )
        for path in paths:
            self.assertTrue(path.is_dir())

    def test_public_and_owner_routes_exist(self):
        paths = (
            "public-site/app/api/public/bot/route.ts",
            "public-site/app/api/public/guilds/route.ts",
            "public-site/app/api/public/guilds/[guildId]/config/route.ts",
            "owner-panel/app/api/admin/info/route.ts",
            "owner-panel/app/api/admin/guilds/route.ts",
            "owner-panel/app/api/admin/stats/route.ts",
            "owner-panel/app/api/admin/economy/route.ts",
            "owner-panel/app/api/admin/operations/route.ts",
        )
        for path in paths:
            self.assertTrue((ROOT / path).is_file())

    def test_bot_api_and_migration_exist(self):
        paths = (
            "discord-host/app/api/health.py",
            "discord-host/app/api/guilds.py",
            "discord-host/app/api/admin.py",
            "discord-host/app/services/guild_config_store.py",
            "discord-host/alembic/versions/20261125_001_create_guild_configs.py",
        )
        for path in paths:
            self.assertTrue((ROOT / path).is_file())


if __name__ == "__main__":
    unittest.main()
