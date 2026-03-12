from fastapi import APIRouter, Request
import pandas as pd
from app.services.backtest_service import run_backtest

router = APIRouter()

@router.post("/backtest")
async def backtest(request: Request):
    data = await request.json()
    prices = pd.DataFrame(data["prices"])  # {date: , asset1: , asset2: }
    weights = data["weights"]              # {"AAPL":0.5, "TSLA":0.5}
    result = run_backtest(prices, weights)
    return result
