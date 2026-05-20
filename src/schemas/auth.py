from pydantic import BaseModel, Field, field_validator

from src.schemas.user import normalize_email


class LoginRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
