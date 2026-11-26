import hmac
import os
from collections import deque
from time import monotonic

from fastapi import Header, HTTPException, status


_RATE = deque(maxlen=120)


def require_service_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("BOT_API_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="API authentication is not configured")
    if not authorization or not hmac.compare_digest(authorization, f"Bearer {expected}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def require_owner(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("OWNER_API_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Administrative authentication is not configured")
    if not authorization or not hmac.compare_digest(authorization, f"Bearer {expected}"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def check_rate_limit(client_id: str = "global") -> None:
    now = monotonic()
    key = f"{client_id}:{int(now)}"
    while _RATE and _RATE[0][1] < now - 60:
        _RATE.popleft()
    count = sum(1 for item, _ in _RATE if item.startswith(f"{client_id}:"))
    if count >= 120:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
    _RATE.append((key, now))
