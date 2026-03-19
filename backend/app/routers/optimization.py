from fastapi import APIRouter, Request, HTTPException
import numpy as np
import pandas as pd

router = APIRouter(prefix="/api/optimize", tags=["Optimization"])

@router.post("/")
async def optimize_portfolio(request: Request):
    """
    Optimize portfolio weights using mean-variance optimization.
    Expects JSON:
    {
      "returns": [
        {"date":"2024-01-01","AAPL":0.01,"TSLA":-0.02},
        {"date":"2024-01-02","AAPL":0.015,"TSLA":0.005},
        {"date":"2024-01-03","AAPL":-0.01,"TSLA":0.02}
      ]
    }
    """
    try:
        data = await request.json()
        returns = pd.DataFrame(data["returns"]).drop(columns=["date"], errors="ignore")

        # Mean returns and covariance
        mean_returns = returns.mean()
        cov_matrix = returns.cov()

        # Mean-variance optimization (maximize Sharpe with risk-free=0)
        inv_cov = np.linalg.pinv(cov_matrix.values)
        weights = inv_cov @ mean_returns.values
        weights = weights / weights.sum()

        # Expected metrics
        exp_return = float(mean_returns.values @ weights)
        exp_volatility = float(np.sqrt(weights @ cov_matrix.values @ weights))
        sharpe_ratio = exp_return / exp_volatility if exp_volatility > 0 else 0.0

        return {
            "optimized_weights": dict(zip(returns.columns, weights.round(4))),
            "expected_return": round(exp_return, 4),
            "expected_volatility": round(exp_volatility, 4),
            "sharpe_ratio": round(sharpe_ratio, 4),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
