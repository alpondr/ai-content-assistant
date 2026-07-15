"""
Pydantic schemas for User & auth.

Why not just reuse the SQLAlchemy model? Because the ORM model shows what's
in the DB (including hashed_password), while a schema shows exactly what the
API should accept/return. Keeping them separate means we never accidentally
leak a password hash in a JSON response.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """What the client sends when registering."""

    email: EmailStr
    password: str = Field(min_length=8, description="Plain password, hashed before saving")


class UserOut(BaseModel):
    """What we send back to the client. Notice: no password field at all."""

    id: int
    email: EmailStr
    created_at: datetime

    # lets us build this schema directly from a SQLAlchemy User object,
    # e.g. UserOut.model_validate(user_orm_instance)
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Response shape for the /login endpoint."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """What we expect to find inside a decoded JWT."""

    sub: str | None = None  # "subject" = the user's email, our unique identifier
