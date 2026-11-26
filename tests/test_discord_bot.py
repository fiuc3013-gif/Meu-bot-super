import asyncio
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISCORD_HOST = ROOT / "discord-host"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DISCORD_HOST))


class DiscordBotFoundationTests(unittest.TestCase):
    def test_required_bot_modules_exist(self):
        for directory in ("core", "events", "commands", "modules", "services", "utils", "config", "exceptions"):
            self.assertTrue((DISCORD_HOST / "bot" / directory).is_dir())

    def test_basic_commands_load_and_guild_configs_are_isolated(self):
        from bot.core.bot import MiyoraBot

        async def verify():
            bot = MiyoraBot()
            await bot.load_extensions()

            command_names = {command.name for command in bot.tree.walk_commands()}
            self.assertIn("ping", command_names)
            self.assertIn("botinfo", command_names)
            self.assertIn("ajuda", command_names)

            first = bot.guild_config.set_locale(101, "pt-BR")
            second = bot.guild_config.get(202)
            self.assertEqual(first.guild_id, 101)
            self.assertEqual(second.guild_id, 202)
            self.assertEqual(second.locale, "pt-BR")

            await bot.close()

        asyncio.run(verify())

    def test_database_service_requires_central_database_url(self):
        from bot.services.database import DatabaseService
        from shared.database.session import SessionLocal

        if SessionLocal is None:
            with self.assertRaisesRegex(RuntimeError, "DATABASE_URL"):
                with DatabaseService.session():
                    pass


if __name__ == "__main__":
    unittest.main()
