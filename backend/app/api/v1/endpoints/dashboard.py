from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.portfolio import Portfolio, PortfolioHolding
from app.models.wallet import Wallet
from app.schemas.wallet import WalletBalanceResponse

router = APIRouter()


class MarketIndex(BaseModel):
    symbol: str
    name: str
    value: float
    change: float
    change_pct: float


class PortfolioSummary(BaseModel):
    id: int
    name: str
    total_value: float
    invested_amount: float
    risk_profile: str
    day_change: float = 0.0
    total_return: float = 0.0
    total_return_pct: float = 0.0
    holdings_count: int = 0
    
    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    user_id: int
    user_email: str
    user_name: str
    wallet: WalletBalanceResponse
    portfolios: List[PortfolioSummary]
    market: Optional[Any] = None
    total_portfolio_value: float
    total_invested: float
    total_available: float
    
    class Config:
        from_attributes = True


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get dashboard data for the current user."""
    from app.services.wallet_service import WalletService
    from app.services.market_data import market_data_service
    
    wallet_service = WalletService(db)
    wallet_balance = await wallet_service.get_wallet_balance(current_user.id)
    
    result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == current_user.id)
    )
    portfolios = result.scalars().all()
    
    portfolio_summaries = []
    total_portfolio_value = 0.0
    
    for portfolio in portfolios:
        holdings_count = len(portfolio.holdings)
        total_value = portfolio.total_value or 0.0
        invested = portfolio.invested_amount or 0.0
        
        day_change = 0.0
        total_return = 0.0
        total_return_pct = 0.0
        
        if invested > 0:
            total_return = total_value - invested
            total_return_pct = (total_return / invested) * 100
        
        portfolio_summaries.append(PortfolioSummary(
            id=portfolio.id,
            name=portfolio.name,
            total_value=total_value,
            invested_amount=invested,
            risk_profile=portfolio.risk_profile,
            day_change=day_change,
            total_return=total_return,
            total_return_pct=total_return_pct,
            holdings_count=holdings_count,
        ))
        
        total_portfolio_value += total_value
    
    total_invested = wallet_balance.total_invested
    total_available = wallet_balance.balance + (total_portfolio_value - total_invested)
    
    market_data = None
    try:
        market_data = await market_data_service.get_market_overview()
    except Exception:
        pass
    
    return DashboardResponse(
        user_id=current_user.id,
        user_email=current_user.email,
        user_name=current_user.full_name,
        wallet=wallet_balance,
        portfolios=portfolio_summaries,
        market=market_data,
        total_portfolio_value=total_portfolio_value,
        total_invested=total_invested,
        total_available=total_available,
    )
