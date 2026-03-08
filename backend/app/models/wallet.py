from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRADE_BUY = "trade_buy"
    TRADE_SELL = "trade_sell"
    DIVIDEND = "dividend"
    FEE = "fee"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_deposited: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_withdrawn: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_invested: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="wallet")
    transactions: Mapped[List["WalletTransaction"]] = relationship(
        "WalletTransaction", 
        back_populates="wallet", 
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Wallet(id={self.id}, user_id={self.user_id}, balance={self.balance})>"


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance_before: Mapped[float] = mapped_column(Float, nullable=False)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(SQLEnum(TransactionStatus), default=TransactionStatus.COMPLETED, nullable=False)
    
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<WalletTransaction(id={self.id}, type={self.type}, amount={self.amount})>"
