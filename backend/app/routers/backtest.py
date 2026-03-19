from fastapi import APIRouter, Request, HTTPException
import pandas as pd
import numpy as np
from app.services.backtest_service import run_backtest

router = APIRouter(prefix="/api/backtest", tags=["backtest"])

# --- Utility Metrics ---
def sharpe_ratio(returns, risk_free_rate: float = 0.0) -> float:
    excess_returns = returns - risk_free_rate
    denom = np.std(excess_returns)
    return float(np.mean(excess_returns) / denom) if denom > 0 else 0.0

def sortino_ratio(returns, risk_free_rate: float = 0.0) -> float:
    downside = returns[returns < risk_free_rate]
    denom = np.std(downside) if len(downside) > 0 else 1.0
    return float(np.mean(returns - risk_free_rate) / denom)

def max_drawdown(returns) -> float:
    cum_returns = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(cum_returns)
    drawdown = (cum_returns - peak) / peak
    return float(np.min(drawdown))

# --- Routes ---
@router.post("/")
async def backtest(request: Request):
    """
    Run a portfolio backtest given price data and weights.
    Expects JSON: { "prices": {date: {asset: price}}, "weights": {"AAPL":0.5,"TSLA":0.5} }
    """
    try:
        data = await request.json()
        prices = pd.DataFrame(data["prices"])   # {date: , asset1: , asset2: }
        weights = data["weights"]               # {"AAPL":0.5, "TSLA":0.5}
        result = run_backtest(prices, weights)  # delegate to service
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/metrics")
async def calculate_metrics(request: Request):
    """
    Calculate risk metrics from a list of daily returns.
    Expects JSON: { "returns": [0.01, -0.02, 0.005] }
    """
    try:
        data = await request.json()
        returns = np.array(data["returns"], dtype=float)
        return {
            "sharpe_ratio": sharpe_ratio(returns),
            "sortino_ratio": sortino_ratio(returns),
            "max_drawdown": max_drawdown(returns),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
