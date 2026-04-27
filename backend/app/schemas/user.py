import re
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

if TYPE_CHECKING:
    from app.schemas.portfolio import PortfolioResponse

_SPECIAL_CHARS = r"!@#$%^&*()_+\-=\[\]{};:'\",.<>?/\\|`~"


def _validate_password(v: str) -> str:
    """Enforce password policy: 8+ chars, 1 uppercase, 1 special character."""
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one capital letter (A–Z).")
    if not re.search(rf"[{_SPECIAL_CHARS}]", v):
        raise ValueError(
            "Password must contain at least one special character "
            "(!  @  #  $  %  ^  &  *  etc.)."
        )
    return v


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    risk_tolerance: str = "moderate"
    investment_horizon: int = 5
    initial_investment: float = 10000.0
    monthly_contribution: float = 0.0
    preferred_assets: Optional[str] = "stocks,etfs"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password(v)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_horizon: Optional[int] = None
    initial_investment: Optional[float] = None
    monthly_contribution: Optional[float] = None
    preferred_assets: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

    @field_validator("password", mode="before")
    @classmethod
    def password_strength(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_password(v)


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    pass


class UserWithPortfolios(UserResponse):
    portfolios: List["PortfolioResponse"] = []


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    type: Optional[str] = None


# OTP schemas
class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResendOTPRequest(BaseModel):
    email: EmailStr


class RegisterResponse(BaseModel):
    """Returned after registration. Includes OTP only in dev mode."""
    message: str
    email: str
    # Only populated when SMTP is NOT configured (dev mode)
    dev_otp: Optional[str] = None
