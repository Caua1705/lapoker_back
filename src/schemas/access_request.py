import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class AccessRequestCreate(BaseModel):
    """Schema for the public access request form."""
    name: str = Field(..., min_length=2, max_length=120)
    phone: str
    instagram: str | None = None
    email: EmailStr | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if not 10 <= len(digits) <= 15:
            raise ValueError("Phone must have between 10 and 15 digits.")
        return digits

    @field_validator("instagram")
    @classmethod
    def validate_instagram(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v.startswith("@"):
            v = f"@{v}"
        return v


class AccessRequestResponse(BaseModel):
    """Schema for the access request response."""
    success: bool
    message: str
    registration_status: str
