from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Portfolio configuration
    total_value: Mapped[float] = mapped_column(Float, default=0.0)
    invested_amount: Mapped[float] = mapped_column(
        Float, default=0.0
    )  # Amount invested from wallet
    cash_reserve_pct: Mapped[float] = mapped_column(
        Float, default=0.05
    )  # 5% cash reserve

    # Risk profile
    risk_profile: Mapped[str] = mapped_column(
        String(20), default="moderate"
    )  # conservative, moderate, aggressive
    # AI Analysis results
    model_type: Mapped[str] = mapped_column(
        String(50), default="temporal_fusion_transformer"
    )
    expected_return: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volatility: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sharpe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Risk metrics
    var_95: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # Value at Risk
    cvar_95: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # Conditional VaR

    # AI Explanation
    ai_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="portfolios")
    holdings: Mapped[List["PortfolioHolding"]] = relationship(
        "PortfolioHolding",
        back_populates="portfolio",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[List["PortfolioTransaction"]] = relationship(
        "PortfolioTransaction",
        back_populates="portfolio",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Portfolio(id={self.id}, name={self.name}, user_id={self.user_id})>"


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # stock, crypto, etf, gold
    sector: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # Technology, Healthcare, etc.

    # Allocation
    weight: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    avg_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    market_value: Mapped[float] = mapped_column(Float, nullable=False)

    # AI Signals
    predicted_return: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    signal_strength: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # strong_buy, buy, hold, sell, strong_sell

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="holdings"
    )

    def __repr__(self) -> str:
        return f"<PortfolioHolding(symbol={self.symbol}, weight={self.weight})>"


class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False
    )

    transaction_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # buy, sell, rebalance, deposit, withdraw
    symbol: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    amount: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # Total amount (positive for buy, negative for sell)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="transactions"
    )

    def __repr__(self) -> str:
        return f"<PortfolioTransaction(id={self.id}, type={self.transaction_type}, symbol={self.symbol})>"
