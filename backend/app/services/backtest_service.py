import pandas as pd
import numpy as np

def run_backtest(prices: pd.DataFrame, weights: dict):
    """
    prices: DataFrame with datetime index and asset columns
    weights: dict of {asset: weight}
    """
    # Normalize weights
    w = np.array([weights.get(asset, 0) for asset in prices.columns])
    w = w / np.sum(w)

    # Calculate portfolio returns
    returns = prices.pct_change().dropna()
    portfolio_returns = returns.dot(w)

    # Metrics
    cumulative = (1 + portfolio_returns).cumprod()
    sharpe = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252)
    sortino = (portfolio_returns.mean() / portfolio_returns[portfolio_returns < 0].std()) * np.sqrt(252)
    max_drawdown = (cumulative / cumulative.cummax() - 1).min()

    return {
        "cumulative_returns": cumulative.tolist(),
        "dates": cumulative.index.strftime("%Y-%m-%d").tolist(),
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_drawdown
    }
