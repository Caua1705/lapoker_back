from pydantic import BaseModel


class AccessRequestCreate(BaseModel):
    """Schema for the public access request form."""
    name: str
    phone: str
    instagram: str | None = None
    email: str | None = None


class AccessRequestResponse(BaseModel):
    """Schema for the access request response."""
    success: bool
    message: str
    registration_status: str
