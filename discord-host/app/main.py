from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from .api.admin import router as admin_router
from .api.guilds import router as guilds_router
from .api.health import router as health_router

app = FastAPI(title="Miyora Bot API", version="0.2.0")
app.include_router(health_router)
app.include_router(guilds_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1/admin")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = "not_found" if exc.status_code == 404 else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail), "code": code},
    )
