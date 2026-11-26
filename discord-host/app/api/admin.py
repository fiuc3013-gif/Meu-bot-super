from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..bot_registry import bot_registry
from ..security import check_rate_limit, require_owner
from ..services.economy import EconomyService
from shared.database.models import AuditLog, EconomyTransaction
from shared.database.session import SessionLocal
from ..config import settings
from decimal import Decimal
from ..services.store import StoreService
from ..services.loans import LoanService
from ..services.boosters import BoosterService
from shared.database.models import Loan, LoanPayment, BoosterRequest, StoreProduct, GlobalBalance

router = APIRouter(dependencies=[Depends(require_owner)], tags=["admin"])


class BalanceAdjustmentRequest(BaseModel):
    user_id: str = Field(pattern=r"^\d+$", min_length=1, max_length=32)
    guild_id: str | None = Field(default=None, pattern=r"^\d+$")
    amount: float
    reason: str = Field(min_length=3, max_length=500)


class StoreProductRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    price: float = Field(gt=0)
    stock: int | None = Field(default=None, ge=0)
    guild_id: str | None = Field(default=None, pattern=r"^\d+$")


class LoanDecisionRequest(BaseModel):
    approved_amount: float | None = Field(default=None, gt=0)
    reason: str = Field(min_length=3, max_length=500)


class BoosterDecisionRequest(BaseModel):
    approve: bool
    reason: str = Field(min_length=3, max_length=500)


class OperationRequest(BaseModel):
    guild_id: str | None = Field(default=None, pattern=r"^\d+$")
    operation: str = Field(min_length=1, max_length=64)


@router.get("/info")
def admin_info(request: Request):
    check_rate_limit(request.client.host if request.client else "unknown")
    bot = bot_registry.get()
    return {"name": "Miyora", "bot_connected": bool(bot and bot.is_ready())}


@router.get("/guilds")
def admin_guilds(request: Request):
    check_rate_limit(request.client.host if request.client else "unknown")
    bot = bot_registry.get()
    if bot is None:
        return {"guilds": []}
    return {"guilds": [{"guild_id": str(g.id), "name": g.name, "member_count": g.member_count} for g in bot.guilds]}


@router.get("/stats")
def admin_stats():
    bot = bot_registry.get()
    if bot is None:
        return {"guild_count": 0, "member_count": 0, "future_modules": []}
    return {"guild_count": len(bot.guilds), "member_count": sum(g.member_count or 0 for g in bot.guilds), "future_modules": []}


@router.get("/economy")
def admin_economy():
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        bank = session.get(GlobalBalance, "MIYORA_BANK")
        pending_loans = session.query(Loan).filter_by(status="pending").count()
    return {"implemented": True, "guild_count": len(bot_registry.get().guilds) if bot_registry.get() else 0, "total_balance": str(bank.balance) if bank else "0.00", "pending_loans": pending_loans}


@router.get("/members/{member_id}")
def admin_member(member_id: str):
    if not member_id.isdigit():
        raise HTTPException(status_code=400, detail="Invalid member_id")
    bot = bot_registry.get()
    if bot is None:
        raise HTTPException(status_code=503, detail="Bot is not available")
    matches = []
    for guild in bot.guilds:
        member = guild.get_member(int(member_id))
        if member is not None:
            matches.append({"guild_id": str(guild.id), "guild_name": guild.name, "display_name": member.display_name})
    if not matches:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"member_id": member_id, "guilds": matches}


@router.post("/balances/adjust")
def admin_adjust_balance(payload: BalanceAdjustmentRequest, request: Request):
    check_rate_limit(request.client.host if request.client else "unknown")
    try:
        administrator_id = settings.owner_discord_user_id or "owner"
        balance = EconomyService().admin_adjust(administrator_id, payload.user_id, payload.guild_id, __import__("decimal").Decimal(str(payload.amount)), payload.reason)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"user_id": payload.user_id, "guild_id": payload.guild_id, "balance": str(balance)}


@router.get("/members/{member_id}/transactions")
def admin_member_transactions(member_id: str):
    if not member_id.isdigit():
        raise HTTPException(status_code=400, detail="Invalid member_id")
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        items = session.query(EconomyTransaction).filter_by(user_id=member_id).order_by(EconomyTransaction.created_at.desc()).limit(100).all()
    return {"member_id": member_id, "transactions": [{"id": item.id, "kind": item.kind, "amount": str(item.amount), "reason": item.reason, "created_at": item.created_at.isoformat()} for item in items]}


@router.get("/audit")
def admin_audit_logs():
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        items = session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return {"logs": [{"id": item.id, "administrator_id": item.administrator_id, "action": item.action, "entity_type": item.entity_type, "entity_id": item.entity_id, "reason": item.reason, "created_at": item.created_at.isoformat()} for item in items]}


@router.get("/store/products")
def admin_store_products():
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        items = session.query(StoreProduct).filter_by(active=True).order_by(StoreProduct.id.desc()).all()
    return {"products": [{"id": item.id, "scope": item.scope, "guild_id": item.guild_id, "name": item.name, "description": item.description, "price": str(item.price), "stock": item.stock} for item in items]}


@router.post("/store/products")
def admin_create_store_product(payload: StoreProductRequest):
    try:
        product = StoreService().upsert_product(settings.owner_discord_user_id or "owner", "global" if payload.guild_id is None else "server", payload.name, payload.description, Decimal(str(payload.price)), payload.stock, payload.guild_id)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, ValueError) else 503, detail=str(exc)) from exc
    return {"id": product.id, "name": product.name, "price": str(product.price), "stock": product.stock}


@router.put("/store/products/{product_id}")
def admin_update_store_product(product_id: int, payload: StoreProductRequest):
    try:
        product = StoreService().upsert_product(settings.owner_discord_user_id or "owner", "global" if payload.guild_id is None else "server", payload.name, payload.description, Decimal(str(payload.price)), payload.stock, payload.guild_id, product_id)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, ValueError) else 503, detail=str(exc)) from exc
    return {"id": product.id, "name": product.name, "price": str(product.price), "stock": product.stock}


@router.delete("/store/products/{product_id}")
def admin_remove_store_product(product_id: int):
    try:
        StoreService().remove_product(settings.owner_discord_user_id or "owner", product_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"removed": True, "product_id": product_id}


class StorePurchaseRequest(BaseModel):
    product_id: int = Field(gt=0)
    user_id: str = Field(pattern=r"^\d+$")
    idempotency_key: str = Field(min_length=3, max_length=128)


@router.post("/store/purchase")
def admin_purchase_global(payload: StorePurchaseRequest):
    try:
        purchase = StoreService().purchase(payload.user_id, payload.product_id, f"global:{payload.idempotency_key}")
    except (RuntimeError, LookupError, ValueError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, (LookupError, ValueError)) else 503, detail=str(exc)) from exc
    return {"purchase_id": purchase.id, "product_id": purchase.product_id, "amount": str(purchase.amount)}


@router.get("/loans")
def admin_loans(status: str | None = None):
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        query = session.query(Loan)
        if status:
            query = query.filter_by(status=status)
        items = query.order_by(Loan.created_at.desc()).limit(100).all()
    return {"loans": [{"id": item.id, "user_id": item.user_id, "requested_amount": str(item.requested_amount), "approved_amount": str(item.approved_amount) if item.approved_amount is not None else None, "installments": item.installments, "status": item.status, "created_at": item.created_at.isoformat()} for item in items]}


@router.post("/loans/{loan_id}/approve")
def admin_approve_loan(loan_id: int, payload: LoanDecisionRequest):
    try:
        loan = LoanService().approve(settings.owner_discord_user_id or "owner", loan_id, Decimal(str(payload.approved_amount)) if payload.approved_amount is not None else None)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (ValueError, LookupError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, ValueError) else 404, detail=str(exc)) from exc
    return {"id": loan.id, "status": loan.status, "approved_amount": str(loan.approved_amount)}


@router.get("/loans/{loan_id}/payments")
def admin_loan_payments(loan_id: int):
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        items = session.query(LoanPayment).filter_by(loan_id=loan_id).order_by(LoanPayment.installment_number).all()
    return {"loan_id": loan_id, "payments": [{"installment": item.installment_number, "amount": str(item.amount), "due_at": item.due_at.isoformat(), "paid_at": item.paid_at.isoformat() if item.paid_at else None} for item in items]}


@router.post("/loans/{loan_id}/payments/{installment_number}")
def admin_pay_loan_installment(loan_id: int, installment_number: int):
    try:
        payment = LoanService().pay(loan_id, installment_number)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (ValueError, LookupError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, ValueError) else 404, detail=str(exc)) from exc
    return {"loan_id": loan_id, "installment": installment_number, "paid_at": payment.paid_at.isoformat() if payment.paid_at else None}


@router.post("/loans/{loan_id}/reject")
def admin_reject_loan(loan_id: int, payload: LoanDecisionRequest):
    try:
        LoanService().reject(settings.owner_discord_user_id or "owner", loan_id, payload.reason)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (ValueError, LookupError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, ValueError) else 404, detail=str(exc)) from exc
    return {"id": loan_id, "status": "rejected"}


@router.get("/boosters")
def admin_boosters(status: str | None = None):
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        query = session.query(BoosterRequest)
        if status:
            query = query.filter_by(status=status)
        items = query.order_by(BoosterRequest.created_at.desc()).limit(100).all()
    return {"requests": [{"id": item.id, "guild_id": item.guild_id, "user_id": item.user_id, "benefit": item.benefit, "status": item.status, "created_at": item.created_at.isoformat()} for item in items]}


@router.post("/boosters/{request_id}/decision")
def admin_booster_decision(request_id: int, payload: BoosterDecisionRequest):
    try:
        request = BoosterService().decide(settings.owner_discord_user_id or "owner", request_id, payload.approve, payload.reason)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (ValueError, LookupError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, ValueError) else 404, detail=str(exc)) from exc
    return {"id": request.id, "status": request.status}


@router.post("/operations")
def admin_operation(payload: OperationRequest):
    allowed = {"health-check", "list-guilds"}
    if payload.operation not in allowed:
        raise HTTPException(status_code=400, detail="Operation is not available")
    return {"accepted": True, "operation": payload.operation, "guild_id": payload.guild_id}
