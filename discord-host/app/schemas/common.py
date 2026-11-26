from pydantic import BaseModel


class HealthResponse(BaseModel):
    service: str
    status: str


class ErrorResponse(BaseModel):
    error: str
    code: str
