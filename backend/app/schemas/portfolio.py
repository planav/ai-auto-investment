from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# Portfolio Holding Schemas
class PortfolioHoldingBase(BaseModel):
    symbol: str
    asset_type: str = Field(..., pattern="^(stock|crypto|etf|gold|cash)$")
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
    model_type: str = "temporal_fusion_transformer"
    investment_amount: float = Field(..., gt=0.0)


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cash_reserve_pct: Optional[float] = Field(None, ge=0.0, le=0.5)


from datetime import datetime

class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int
    model_type: str
    expected_return: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    var_95: Optional[float] = None
    cvar_95: Optional[float] = None
    ai_explanation: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    holdings: List[PortfolioHoldingResponse] = []
    
    class Config:
        from_attributes = True


# Portfolio Analysis Request
class PortfolioAnalysisRequest(BaseModel):
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


# System Stats Schema
class SystemStats(BaseModel):
    assets_analyzed: int = Field(default=0, description="Total number of assets in database")
    avg_annual_return: Optional[float] = Field(default=None, description="Average annual return from backtests (%)")
    prediction_accuracy: Optional[float] = Field(default=None, description="Prediction accuracy from backtests (%)")
    analysis_time_ms: Optional[float] = Field(default=None, description="Average API analysis response time (ms)")
    model_status: Dict[str, str] = Field(default_factory=dict, description="Training status for each model")
    
    class Config:
        from_attributes = True
