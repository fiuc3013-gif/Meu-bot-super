import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public-site"


class PublicSiteFoundationTests(unittest.TestCase):
    def test_public_pages_exist(self):
        for path in (
            "app/page.tsx",
            "app/sobre/page.tsx",
            "app/adicionar/page.tsx",
            "app/dashboard/page.tsx",
            "app/dashboard/[guildId]/page.tsx",
        ):
            self.assertTrue((PUBLIC / path).is_file())

    def test_oauth_routes_exist(self):
        for path in (
            "app/api/auth/discord/route.ts",
            "app/api/auth/discord/callback/route.ts",
            "app/api/auth/logout/route.ts",
        ):
            self.assertTrue((PUBLIC / path).is_file())

    def test_oauth_session_helpers_exist(self):
        content = (PUBLIC / "lib/auth.ts").read_text()
        self.assertIn("signPublicSession", content)
        self.assertIn("verifyPublicSession", content)


if __name__ == "__main__":
    unittest.main()
