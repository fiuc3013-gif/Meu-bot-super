from sqlalchemy import select

from shared.database.models import AuditLog, BoosterRequest
from shared.database.session import SessionLocal


class BoosterService:
    def __init__(self) -> None:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is not configured")

    def request(self, guild_id: str, user_id: str, benefit: str):
        if not benefit.strip():
            raise ValueError("Benefit is required")
        with SessionLocal() as session:
            existing = session.execute(select(BoosterRequest).where(BoosterRequest.guild_id == guild_id, BoosterRequest.user_id == user_id, BoosterRequest.status == "pending")).scalar_one_or_none()
            if existing:
                return existing
            request = BoosterRequest(guild_id=guild_id, user_id=user_id, benefit=benefit.strip())
            session.add(request)
            session.commit()
            session.refresh(request)
            return request

    def decide(self, administrator_id: str, request_id: int, approve: bool, reason: str):
        if not reason.strip():
            raise ValueError("A reason is required")
        with SessionLocal() as session:
            request = session.get(BoosterRequest, request_id)
            if request is None:
                raise LookupError("Booster request not found")
            if request.status != "pending":
                raise ValueError("Booster request is not pending")
            request.status = "approved" if approve else "rejected"
            request.reviewed_by = administrator_id
            session.add(AuditLog(administrator_id=administrator_id, action="approve_booster" if approve else "reject_booster", entity_type="booster_request", entity_id=str(request.id), before_value={"status": "pending"}, after_value={"status": request.status}, reason=reason.strip()))
            session.commit()
            session.refresh(request)
            return request
