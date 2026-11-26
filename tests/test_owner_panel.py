import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT / "owner-panel"


class OwnerPanelFoundationTests(unittest.TestCase):
    def test_owner_pages_exist(self):
        for path in (
            "app/page.tsx",
            "app/dashboard/page.tsx",
            "app/servidores/page.tsx",
            "app/membros/page.tsx",
            "app/economia/page.tsx",
            "app/logs/page.tsx",
        ):
            self.assertTrue((OWNER / path).is_file())

    def test_owner_auth_routes_exist(self):
        for path in (
            "app/api/auth/discord/route.ts",
            "app/api/auth/discord/callback/route.ts",
            "app/api/auth/logout/route.ts",
        ):
            self.assertTrue((OWNER / path).is_file())

    def test_owner_user_id_is_configured_as_variable(self):
        env = (OWNER / ".env.example").read_text()
        self.assertIn("OWNER_DISCORD_USER_ID=", env)


if __name__ == "__main__":
    unittest.main()
