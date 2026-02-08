from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, EmailStr, Field

if TYPE_CHECKING:
    from app.schemas.portfolio import PortfolioResponse


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    risk_tolerance: str = "moderate"
    investment_horizon: int = 5
    initial_investment: float = 10000.0
    monthly_contribution: float = 0.0
    preferred_assets: Optional[str] = "stocks,etfs"


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


# Properties to receive via API on update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_horizon: Optional[int] = None
    initial_investment: Optional[float] = None
    monthly_contribution: Optional[float] = None
    preferred_assets: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


# Properties stored in DB
class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True


# Properties to return via API
class UserResponse(UserInDB):
    pass


# User with portfolios
class UserWithPortfolios(UserResponse):
    portfolios: List["PortfolioResponse"] = []


# Login schemas
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
