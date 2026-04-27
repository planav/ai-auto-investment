from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Portfolio Holding Schemas
class PortfolioHoldingBase(BaseModel):
    symbol: str
    asset_type: str = Field(..., pattern="^(stock|crypto|etf|gold|cash)$")
    sector: Optional[str] = None
    weight: float = Field(..., ge=0.0, le=1.0)
    quantity: float = Field(..., ge=0.0)
    avg_price: float = Field(..., ge=0.0)


class PortfolioHoldingCreate(PortfolioHoldingBase):
    pass


class PortfolioHoldingResponse(PortfolioHoldingBase):
    id: int
    portfolio_id: int
    current_price: float
    market_value: float
    predicted_return: Optional[float] = None
    confidence_score: Optional[float] = None
    signal_strength: Optional[str] = None

    class Config:
        from_attributes = True


# Portfolio Schemas
class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None
    total_value: float = 0.0
    cash_reserve_pct: float = Field(default=0.05, ge=0.0, le=0.5)


class PortfolioCreate(PortfolioBase):
    model_config = ConfigDict(protected_namespaces=())
    risk_profile: str = Field(
        default="moderate", pattern="^(conservative|moderate|aggressive)$"
    )
    model_type: str = "temporal_fusion_transformer"
    investment_amount: float = Field(..., gt=0.0)


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cash_reserve_pct: Optional[float] = Field(None, ge=0.0, le=0.5)


class PortfolioResponse(PortfolioBase):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    id: int
    user_id: int
    risk_profile: str
    invested_amount: float
    model_type: str
    expected_return: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    var_95: Optional[float] = None
    cvar_95: Optional[float] = None
    ai_explanation: Optional[str] = None
    stock_reasoning: Optional[str] = None
    market_context: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    holdings: List[PortfolioHoldingResponse] = []


# Portfolio Analysis Request
class PortfolioAnalysisRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    investment_amount: float = Field(..., gt=0.0)
    risk_tolerance: str = Field(..., pattern="^(conservative|moderate|aggressive)$")
    investment_horizon: int = Field(..., ge=1, le=30)
    preferred_assets: List[str] = Field(default=["stocks", "etfs"])
    model_type: str = "temporal_fusion_transformer"
    max_assets: int = Field(default=20, ge=5, le=50)


# Portfolio Performance
class PortfolioPerformance(BaseModel):
    portfolio_id: int
    total_return: float
    total_return_pct: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float
    cvar_95: float
    beta: Optional[float] = None
    alpha: Optional[float] = None


# Rebalance Recommendation
class RebalanceRecommendation(BaseModel):
    portfolio_id: int
    rebalance_needed: bool
    drift_pct: float
    recommendations: List[Dict] = []
    expected_transactions: int = 0
    estimated_cost: float = 0.0


# Portfolio Transaction Schema
class PortfolioTransactionResponse(BaseModel):
    id: int
    portfolio_id: int
    transaction_type: str
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    amount: float
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Investment Request Schema (for creating portfolio from wallet)
class InvestmentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to invest from wallet")
    risk_tolerance: str = Field(
        ...,
        pattern="^(conservative|moderate|aggressive)$",
        description="Risk tolerance level",
    )
    name: Optional[str] = Field(
        None, description="Portfolio name (auto-generated if not provided)"
    )
    description: Optional[str] = Field(None, description="Portfolio description")


# Investment Response Schema
class InvestmentResponse(BaseModel):
    portfolio: PortfolioResponse
    wallet_balance: float
    message: str


# System Stats Schema
class SystemStats(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    assets_analyzed: int = Field(
        default=0, description="Total number of assets in database"
    )
    avg_annual_return: Optional[float] = Field(
        default=None, description="Average annual return from backtests (%)"
    )
    prediction_accuracy: Optional[float] = Field(
        default=None, description="Prediction accuracy from backtests (%)"
    )
    analysis_time_ms: Optional[float] = Field(
        default=None, description="Average API analysis response time (ms)"
    )
    model_status: Dict[str, str] = Field(
        default_factory=dict, description="Training status for each model"
    )



# Sell holding request
class SellHoldingRequest(BaseModel):
    symbol: str
    quantity: Optional[float] = Field(None, gt=0, description="Sell by share quantity")
    amount: Optional[float]   = Field(None, gt=0, description="Sell by dollar amount")
    sell_all: bool            = Field(False,        description="Sell entire position")

    @model_validator(mode="before")
    @classmethod
    def require_sell_method(cls, v):
        if not v.get("sell_all") and not v.get("quantity") and not v.get("amount"):
            raise ValueError("Provide quantity, amount, or set sell_all=true")
        return v


# Sell response
class SellHoldingResponse(BaseModel):
    symbol: str
    quantity_sold: float
    price_per_share: float
    proceeds: float
    message: str
