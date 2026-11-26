import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PendingCompletionTests(unittest.TestCase):
    def test_pending_migration_exists(self):
        path = ROOT / "discord-host/alembic/versions/20261125_003_pending_features.py"
        self.assertTrue(path.is_file())

    def test_advanced_services_exist(self):
        for path in (
            "discord-host/app/services/store.py",
            "discord-host/app/services/loans.py",
            "discord-host/app/services/boosters.py",
            "discord-host/bot/events/safety.py",
            "discord-host/bot/events/giveaway_participants.py",
        ):
            self.assertTrue((ROOT / path).is_file())

    def test_store_loan_booster_routes_exist(self):
        for path in (
            "owner-panel/app/api/admin/store/products/route.ts",
            "owner-panel/app/api/admin/loans/route.ts",
            "owner-panel/app/api/admin/boosters/route.ts",
            "owner-panel/components/economy-admin.tsx",
        ):
            self.assertTrue((ROOT / path).is_file())

    def test_giveaway_payments_and_safety_exist(self):
        for path in (
            "discord-host/alembic/versions/20261125_004_giveaway_winners.py",
            "discord-host/bot/events/safety.py",
            "owner-panel/app/api/admin/loans/[loanId]/payments/route.ts",
            "owner-panel/app/api/admin/loans/[loanId]/payments/[installment]/route.ts",
            "public-site/app/api/public/guilds/[guildId]/store/route.ts",
        ):
            self.assertTrue((ROOT / path).is_file())

    def test_public_config_routes_exist(self):
        for path in (
            "public-site/app/api/public/guilds/[guildId]/messages/route.ts",
            "public-site/app/api/public/guilds/[guildId]/moderation/rules/route.ts",
        ):
            self.assertTrue((ROOT / path).is_file())

    def test_financial_guards_are_present(self):
        loan = (ROOT / "discord-host/app/services/loans.py").read_text()
        store = (ROOT / "discord-host/app/services/store.py").read_text()
        self.assertIn("50000", loan)
        self.assertIn("0.25", loan)
        self.assertIn("idempotency_key", store)


if __name__ == "__main__":
    unittest.main()
