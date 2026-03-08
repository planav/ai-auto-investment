from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.wallet import (
    WalletBalanceResponse,
    WalletResponse,
    DepositRequest,
    WithdrawRequest,
    TransactionResponseList,
)
from app.services.wallet_service import WalletService

router = APIRouter(tags=["wallet"])


@router.get("", response_model=WalletBalanceResponse)
async def get_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get current user's wallet balance."""
    wallet_service = WalletService(db)
    return await wallet_service.get_wallet_balance(current_user.id)


@router.post("/deposit", response_model=WalletResponse)
async def deposit(
    deposit_request: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Deposit fake money into wallet."""
    if deposit_request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit amount must be positive",
        )
    
    if deposit_request.amount > 1000000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum deposit amount is $1,000,000",
        )
    
    wallet_service = WalletService(db)
    wallet = await wallet_service.deposit(
        user_id=current_user.id,
        amount=deposit_request.amount,
        description=deposit_request.description,
    )
    
    return wallet


@router.post("/withdraw", response_model=WalletResponse)
async def withdraw(
    withdraw_request: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Withdraw money from wallet."""
    if withdraw_request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Withdrawal amount must be positive",
        )
    
    wallet_service = WalletService(db)
    wallet = await wallet_service.withdraw(
        user_id=current_user.id,
        amount=withdraw_request.amount,
        description=withdraw_request.description,
    )
    
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance",
        )
    
    return wallet


@router.get("/transactions", response_model=TransactionResponseList)
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> Any:
    """Get transaction history."""
    wallet_service = WalletService(db)
    return await wallet_service.get_transactions(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )
