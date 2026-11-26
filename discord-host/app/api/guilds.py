from fastapi import APIRouter, Depends, HTTPException, Path, Request

from ..bot_registry import bot_registry
from ..schemas.guild import GuildConfigResponse, GuildConfigUpdate
from ..security import check_rate_limit, require_service_token
from ..services.guild_config_store import GuildConfigStore
from shared.database.models import AutoMessage, ModerationRule
from shared.database.session import SessionLocal
from ..services.store import StoreService
from pydantic import BaseModel, Field

router = APIRouter(dependencies=[Depends(require_service_token)], tags=["guilds"])


class AutoMessageUpdate(BaseModel):
    event: str = Field(pattern=r"^(welcome|leave)$")
    channel_id: str = Field(pattern=r"^\d+$")
    template: str = Field(min_length=1, max_length=2000)


class StorePurchaseRequest(BaseModel):
    product_id: int = Field(gt=0)
    user_id: str = Field(pattern=r"^\d+$")
    idempotency_key: str = Field(min_length=3, max_length=128)


class ModerationRuleUpdate(BaseModel):
    rule_type: str = Field(pattern=r"^(flood|invite_filter|trap)$")
    enabled: bool = True
    action: str = Field(pattern=r"^(record_only|timeout|kick|ban)$")
    channel_id: str | None = Field(default=None, pattern=r"^\d+$")
    keywords: list[str] = Field(default_factory=list, max_length=50)
    except_users: list[str] = Field(default_factory=list, max_length=100)
    except_roles: list[str] = Field(default_factory=list, max_length=100)


def guild_id(value: str = Path(..., min_length=1, max_length=32, pattern=r"^\d+$")) -> str:
    return value


@router.get("/bot/status")
def bot_status(request: Request):
    check_rate_limit(request.client.host if request.client else "unknown")
    bot = bot_registry.get()
    if bot is None:
        return {"connected": False, "guild_count": 0, "latency_ms": None}
    return {
        "connected": bot.is_ready(),
        "guild_count": len(bot.guilds),
        "latency_ms": round(bot.latency * 1000),
    }


@router.get("/guilds")
def guilds(request: Request):
    check_rate_limit(request.client.host if request.client else "unknown")
    bot = bot_registry.get()
    if bot is None:
        return {"guilds": []}
    return {"guilds": [{"guild_id": str(guild.id), "name": guild.name} for guild in bot.guilds]}


@router.get("/guilds/{guild_id}/config")
def get_guild_config(guild_id: str = Depends(guild_id)):
    try:
        record = GuildConfigStore().get(guild_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if record is None:
        return GuildConfigResponse(guild_id=guild_id, locale="pt-BR", enabled_modules=[])
    return GuildConfigResponse(guild_id=guild_id, locale=record.locale, enabled_modules=record.enabled_modules, welcome_config=record.welcome_config, moderation_config=record.moderation_config, xp_config=record.xp_config, economy_config=record.economy_config, ticket_config=record.ticket_config)


@router.put("/guilds/{guild_id}/config")
def update_guild_config(payload: GuildConfigUpdate, guild_id: str = Depends(guild_id)):
    bot = bot_registry.get()
    if bot is not None:
        bot.guild_config.set_locale(int(guild_id), payload.locale)
    try:
        record = GuildConfigStore().upsert(guild_id, payload.locale, payload.enabled_modules, payload.welcome_config, payload.moderation_config, payload.xp_config, payload.economy_config, payload.ticket_config)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return GuildConfigResponse(guild_id=guild_id, locale=record.locale, enabled_modules=record.enabled_modules, welcome_config=record.welcome_config, moderation_config=record.moderation_config, xp_config=record.xp_config, economy_config=record.economy_config, ticket_config=record.ticket_config)


@router.get("/guilds/{guild_id}/store/products")
def guild_store_products(guild_id: str = Depends(guild_id)):
    try:
        products = StoreService().list_products("server", guild_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"products": [{"id": item.id, "name": item.name, "description": item.description, "price": str(item.price), "stock": item.stock} for item in products]}


@router.post("/guilds/{guild_id}/store/purchase")
def purchase_server_product(payload: StorePurchaseRequest, guild_id: str = Depends(guild_id)):
    try:
        purchase = StoreService().purchase(payload.user_id, payload.product_id, f"{guild_id}:{payload.idempotency_key}")
    except (RuntimeError, LookupError, ValueError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, (LookupError, ValueError)) else 503, detail=str(exc)) from exc
    if purchase.guild_id != guild_id:
        raise HTTPException(status_code=403, detail="Product belongs to another guild")
    return {"purchase_id": purchase.id, "product_id": purchase.product_id, "amount": str(purchase.amount)}


@router.get("/guilds/{guild_id}/messages")
def get_auto_messages(guild_id: str = Depends(guild_id)):
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        records = session.query(AutoMessage).filter_by(guild_id=guild_id).all()
    return {"messages": [{"event": record.event, "channel_id": record.channel_id, "template": record.template} for record in records]}


@router.put("/guilds/{guild_id}/messages")
def update_auto_message(payload: AutoMessageUpdate, guild_id: str = Depends(guild_id)):
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        record = session.query(AutoMessage).filter_by(guild_id=guild_id, event=payload.event).first()
        if record is None:
            record = AutoMessage(guild_id=guild_id)
            record.event = payload.event
            session.add(record)
        record.channel_id = payload.channel_id
        record.template = payload.template
        session.commit()
    return {"guild_id": guild_id, "event": payload.event, "channel_id": payload.channel_id}


@router.put("/guilds/{guild_id}/moderation/rules")
def update_moderation_rule(payload: ModerationRuleUpdate, guild_id: str = Depends(guild_id)):
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
    with SessionLocal() as session:
        record = session.query(ModerationRule).filter_by(guild_id=guild_id, rule_type=payload.rule_type).first()
        if record is None:
            record = ModerationRule(guild_id=guild_id, rule_type=payload.rule_type)
            session.add(record)
        record.enabled = payload.enabled
        record.config = {"action": payload.action, "channel_id": payload.channel_id, "keywords": payload.keywords, "except_users": payload.except_users, "except_roles": payload.except_roles}
        session.commit()
    return {"guild_id": guild_id, "rule_type": payload.rule_type, "enabled": payload.enabled, "action": payload.action, "channel_id": payload.channel_id, "keywords": payload.keywords, "except_users": payload.except_users, "except_roles": payload.except_roles}


@router.get("/guilds/{guild_id}/channels")
def guild_channels(guild_id: str = Depends(guild_id)):
    bot = bot_registry.get()
    if bot is None:
        raise HTTPException(status_code=503, detail="Bot is not available")
    guild = bot.get_guild(int(guild_id))
    if guild is None:
        raise HTTPException(status_code=404, detail="Guild not found")
    return {"channels": [{"id": str(channel.id), "name": channel.name, "kind": str(channel.type)} for channel in guild.channels]}


@router.get("/guilds/{guild_id}/roles")
def guild_roles(guild_id: str = Depends(guild_id)):
    bot = bot_registry.get()
    if bot is None:
        raise HTTPException(status_code=503, detail="Bot is not available")
    guild = bot.get_guild(int(guild_id))
    if guild is None:
        raise HTTPException(status_code=404, detail="Guild not found")
    return {"roles": [{"id": str(role.id), "name": role.name} for role in guild.roles if not role.is_default()]}


@router.get("/guilds/{guild_id}/members/{member_id}")
def member_info(guild_id: str = Depends(guild_id), member_id: str = Path(..., pattern=r"^\d+$")):
    bot = bot_registry.get()
    if bot is None:
        raise HTTPException(status_code=503, detail="Bot is not available")
    guild = bot.get_guild(int(guild_id))
    if guild is None:
        raise HTTPException(status_code=404, detail="Guild not found")
    member = guild.get_member(int(member_id))
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"guild_id": guild_id, "member_id": str(member.id), "display_name": member.display_name}
