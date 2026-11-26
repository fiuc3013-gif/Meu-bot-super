import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FinalIntegrationTests(unittest.TestCase):
    def test_miyora_system_cogs_exist(self):
        files = (
            "discord-host/bot/commands/economy.py",
            "discord-host/bot/commands/moderation.py",
            "discord-host/bot/commands/xp.py",
            "discord-host/bot/commands/community.py",
            "discord-host/bot/events/autorole.py",
            "discord-host/bot/events/giveaway_participants.py",
            "discord-host/app/services/economy.py",
        )
        for path in files:
            self.assertTrue((ROOT / path).is_file())

    def test_shared_models_and_migration_exist(self):
        self.assertTrue((ROOT / "shared/database/models.py").is_file())
        self.assertTrue((ROOT / "discord-host/alembic/versions/20261125_002_miyora_systems.py").is_file())

    def test_public_and_owner_integration_routes_exist(self):
        files = (
            "public-site/app/api/public/guilds/[guildId]/channels/route.ts",
            "public-site/app/api/public/guilds/[guildId]/roles/route.ts",
            "owner-panel/app/api/admin/members/search/[memberId]/transactions/route.ts",
            "owner-panel/app/api/admin/audit/route.ts",
        )
        for path in files:
            self.assertTrue((ROOT / path).is_file())


if __name__ == "__main__":
    unittest.main()
