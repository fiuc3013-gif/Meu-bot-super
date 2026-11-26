from fastapi import APIRouter, Depends, Request

from ..security import check_rate_limit, require_service_token

router = APIRouter(tags=["health"])


@router.get("/health")
def health(request: Request, _: None = Depends(require_service_token)):
    check_rate_limit(request.client.host if request.client else "unknown")
    return {"service": "miyora-bot-api", "status": "ok"}
