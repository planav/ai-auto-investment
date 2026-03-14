from fastapi import APIRouter, Request
import pandas as pd
from app.services.backtest_service import run_backtest
import numpy as np

router = APIRouter()


@router.post("/backtest")
async def backtest(request: Request):
    data = await request.json()
    prices = pd.DataFrame(data["prices"])  # {date: , asset1: , asset2: }
    weights = data["weights"]              # {"AAPL":0.5, "TSLA":0.5}
    result = run_backtest(prices, weights)
    return result


def sharpe_ratio(returns, risk_free_rate=0.0):
    excess_returns = returns - risk_free_rate
    return float(np.mean(excess_returns) / np.std(excess_returns))


def sortino_ratio(returns, risk_free_rate=0.0):
    downside = returns[returns < risk_free_rate]
    return float(np.mean(returns - risk_free_rate) / np.std(downside))


def max_drawdown(returns):
    cum_returns = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(cum_returns)
    drawdown = (cum_returns - peak) / peak
    return float(np.min(drawdown))


@router.post("/backtest/metrics")
async def calculate_metrics(request: Request):
    data = await request.json()
    returns = np.array(data["returns"])  # expects list of daily returns
    return {
        "sharpe_ratio": sharpe_ratio(returns),
        "sortino_ratio": sortino_ratio(returns),
        "max_drawdown": max_drawdown(returns)
    }
