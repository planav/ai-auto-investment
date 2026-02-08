from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.portfolio import Portfolio


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Investment preferences
    risk_tolerance: Mapped[str] = mapped_column(String(20), default="moderate")  # conservative, moderate, aggressive
    investment_horizon: Mapped[int] = mapped_column(Integer, default=5)  # years
    initial_investment: Mapped[float] = mapped_column(Float, default=10000.0)
    monthly_contribution: Mapped[float] = mapped_column(Float, default=0.0)
    preferred_assets: Mapped[Optional[str]] = mapped_column(Text, default="stocks,etfs")  # comma-separated
    
    # Relationships
    portfolios: Mapped[List["Portfolio"]] = relationship("Portfolio", back_populates="user", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
