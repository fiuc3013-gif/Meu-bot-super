from decimal import Decimal
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from shared.database.models import AuditLog, EconomyTransaction, EconomyWallet, GlobalBalance, StoreProduct, StorePurchase
from shared.database.session import SessionLocal


class StoreService:
    def __init__(self) -> None:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is not configured")

    def list_products(self, scope: str, guild_id: str | None = None):
        with SessionLocal() as session:
            query = select(StoreProduct).where(StoreProduct.scope == scope, StoreProduct.active == True)
            if scope == "server":
                query = query.where(StoreProduct.guild_id == guild_id)
            return session.execute(query).scalars().all()

    def upsert_product(self, administrator_id: str, scope: str, name: str, description: str, price: Decimal, stock: int | None, guild_id: str | None = None, product_id: int | None = None):
        if price <= 0:
            raise ValueError("Price must be positive")
        if stock is not None and stock < 0:
            raise ValueError("Stock cannot be negative")
        if not name.strip():
            raise ValueError("Name is required")
        with SessionLocal() as session:
            product = session.get(StoreProduct, product_id) if product_id else None
            before = None
            if product is None:
                product = StoreProduct(scope=scope, guild_id=guild_id)
                session.add(product)
            else:
                before = {"name": product.name, "price": str(product.price), "stock": product.stock}
            product.name = name.strip()
            product.description = description.strip()
            product.price = price
            product.stock = stock
            product.active = True
            session.flush()
            session.add(AuditLog(administrator_id=administrator_id, action="upsert_product", entity_type="store_product", entity_id=str(product.id), before_value=before, after_value={"name": product.name, "price": str(product.price), "stock": product.stock}, reason="Store product update"))
            session.commit()
            session.refresh(product)
            return product

    def remove_product(self, administrator_id: str, product_id: int):
        with SessionLocal() as session:
            product = session.get(StoreProduct, product_id)
            if product is None:
                raise LookupError("Product not found")
            product.active = False
            session.add(AuditLog(administrator_id=administrator_id, action="remove_product", entity_type="store_product", entity_id=str(product.id), before_value={"active": True}, after_value={"active": False}, reason="Store product removal"))
            session.commit()

    def purchase(self, user_id: str, product_id: int, idempotency_key: str) -> StorePurchase:
        with SessionLocal() as session:
            existing = session.execute(select(StorePurchase).where(StorePurchase.idempotency_key == idempotency_key)).scalar_one_or_none()
            if existing:
                return existing
            product = session.get(StoreProduct, product_id)
            if product is None or not product.active:
                raise LookupError("Product unavailable")
            if product.stock == 0:
                raise ValueError("Out of stock")
            if product.stock is not None:
                product.stock -= 1
            brasilia = timezone(timedelta(hours=-3))
            weekday = datetime.now(brasilia).weekday()
            tax = product.price * Decimal("0.05") if product.scope == "server" and weekday < 5 else Decimal("0")
            if product.scope == "global":
                balance = session.execute(select(GlobalBalance).where(GlobalBalance.user_id == user_id).with_for_update()).scalar_one_or_none()
                if balance is None:
                    raise ValueError("Insufficient global balance")
                before = Decimal(balance.balance)
                if before < product.price:
                    raise ValueError("Insufficient global balance")
                balance.balance = before - product.price
            else:
                if product.guild_id is None:
                    raise ValueError("Server product has no guild_id")
                wallet = session.execute(select(EconomyWallet).where(EconomyWallet.guild_id == product.guild_id, EconomyWallet.user_id == user_id).with_for_update()).scalar_one_or_none()
                if wallet is None:
                    raise ValueError("Insufficient local balance")
                before = Decimal(wallet.balance)
                if before < product.price:
                    raise ValueError("Insufficient local balance")
                wallet.balance = before - product.price
            if tax > 0:
                bank = session.execute(select(GlobalBalance).where(GlobalBalance.user_id == "MIYORA_BANK").with_for_update()).scalar_one_or_none()
                if bank is None:
                    bank = GlobalBalance(user_id="MIYORA_BANK", balance=tax)
                    session.add(bank)
                else:
                    bank.balance = Decimal(bank.balance) + tax
            purchase = StorePurchase(idempotency_key=idempotency_key, product_id=product.id, user_id=user_id, guild_id=product.guild_id, amount=product.price)
            session.add(purchase)
            session.add(EconomyTransaction(idempotency_key=f"purchase:{idempotency_key}", user_id=user_id, guild_id=product.guild_id, kind="store_purchase", amount=product.price, balance_before=before, balance_after=before - product.price, reason=f"Store purchase; server tax={tax}"))
            session.commit()
            session.refresh(purchase)
            return purchase
