from decimal import Decimal
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.database.models import AuditLog, EconomyTransaction, EconomyWallet, GlobalBalance
from shared.database.session import SessionLocal


class EconomyService:
    def __init__(self) -> None:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is not configured")

    @staticmethod
    def _wallet(session: Session, guild_id: str, user_id: str) -> EconomyWallet:
        wallet = session.execute(
            select(EconomyWallet).where(
                EconomyWallet.guild_id == guild_id,
                EconomyWallet.user_id == user_id,
            ).with_for_update()
        ).scalar_one_or_none()
        if wallet is None:
            wallet = EconomyWallet(guild_id=guild_id, user_id=user_id, balance=Decimal("0"))
            session.add(wallet)
            session.flush()
        return wallet

    @staticmethod
    def _global(session: Session, user_id: str) -> GlobalBalance:
        balance = session.execute(
            select(GlobalBalance).where(GlobalBalance.user_id == user_id).with_for_update()
        ).scalar_one_or_none()
        if balance is None:
            balance = GlobalBalance(user_id=user_id, balance=Decimal("0"))
            session.add(balance)
            session.flush()
        return balance

    def local_balance(self, guild_id: str, user_id: str) -> Decimal:
        with SessionLocal() as session:
            return Decimal(self._wallet(session, guild_id, user_id).balance)

    def admin_adjust(self, administrator_id: str, user_id: str, guild_id: str | None, amount: Decimal, reason: str) -> Decimal:
        if amount == 0:
            raise ValueError("The amount must be different from zero")
        if not reason.strip():
            raise ValueError("A reason is required")
        idempotency = f"admin:{administrator_id}:{user_id}:{guild_id}:{amount}:{datetime.utcnow().isoformat()}"
        with SessionLocal() as session:
            if guild_id:
                wallet = self._wallet(session, guild_id, user_id)
                before = Decimal(wallet.balance)
                after = before + amount
                if after < 0:
                    raise ValueError("Negative balances are not allowed")
                wallet.balance = after
                entity_type = "guild_wallet"
            else:
                balance = self._global(session, user_id)
                before = Decimal(balance.balance)
                after = before + amount
                if after < 0:
                    raise ValueError("Negative balances are not allowed")
                balance.balance = after
                entity_type = "global_balance"
            session.add(EconomyTransaction(idempotency_key=idempotency, user_id=user_id, guild_id=guild_id, kind="admin_adjust", amount=amount, balance_before=before, balance_after=after, reason=reason.strip()))
            session.add(AuditLog(administrator_id=administrator_id, action="adjust_balance", entity_type=entity_type, entity_id=user_id, before_value={"balance": str(before)}, after_value={"balance": str(after)}, reason=reason.strip()))
            session.commit()
            return after

    def deposit(self, guild_id: str, user_id: str, amount: Decimal, idempotency_key: str) -> tuple[Decimal, Decimal]:
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        with SessionLocal() as session:
            existing = session.execute(select(EconomyTransaction).where(EconomyTransaction.idempotency_key == idempotency_key)).scalar_one_or_none()
            if existing:
                return Decimal(existing.balance_before), Decimal(existing.balance_after)
            wallet = self._wallet(session, guild_id, user_id)
            global_balance = self._global(session, user_id)
            local_before = Decimal(wallet.balance)
            global_before = Decimal(global_balance.balance)
            if local_before < amount:
                raise ValueError("Insufficient local balance")
            wallet.balance = local_before - amount
            global_balance.balance = global_before + amount
            session.add(EconomyTransaction(idempotency_key=idempotency_key, user_id=user_id, guild_id=guild_id, kind="deposit", amount=amount, balance_before=local_before, balance_after=local_before - amount, reason="Deposit to global bank"))
            session.commit()
            return wallet.balance, global_balance.balance
