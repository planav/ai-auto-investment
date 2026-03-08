from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.wallet import TransactionType, TransactionStatus


class WalletBase(BaseModel):
    balance: float = 0.0
    currency: str = "USD"


class WalletCreate(WalletBase):
    pass


class WalletUpdate(BaseModel):
    pass


class WalletInDB(WalletBase):
    id: int
    user_id: int
    total_deposited: float
    total_withdrawn: float
    total_invested: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WalletResponse(WalletInDB):
    pass


class WalletWithTransactions(WalletResponse):
    transactions: List["WalletTransactionResponse"] = []


class TransactionBase(BaseModel):
    type: TransactionType
    amount: float = Field(..., gt=0)
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionInDB(TransactionBase):
    id: int
    wallet_id: int
    balance_before: float
    balance_after: float
    status: TransactionStatus
    reference_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionResponse(TransactionInDB):
    pass


class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0, le=1000000, description="Amount to deposit (max $1,000,000)")
    description: Optional[str] = "Deposit to investment wallet"


class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to withdraw")
    description: Optional[str] = "Withdrawal from investment wallet"


class WalletBalanceResponse(BaseModel):
    balance: float
    total_deposited: float
    total_withdrawn: float
    total_invested: float
    currency: str = "USD"


class TransactionResponseList(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
