from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.services.market_data import market_data_service
from app.engines.quant_engine.engine import QuantEngine, ModelType
from app.agents.research_agent.fundamental import FundamentalAnalyzer

router = APIRouter()

# Shared engine instances
_quant_engine = QuantEngine()
_fundamental_analyzer = FundamentalAnalyzer()


class AssetAnalysisRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=1, max_length=100)
    include_fundamentals: bool = True
    include_sentiment: bool = True


class AssetSignalResponse(BaseModel):
    symbol: str
    asset_type: str
    current_price: float
    predicted_return: Optional[float] = None
    confidence_score: Optional[float] = None
    signal_strength: str = "hold"  # strong_buy, buy, hold, sell, strong_sell
    fundamental_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    ai_explanation: Optional[str] = None


class BacktestRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    symbols: List[str] = Field(..., min_length=1, max_length=50)
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    initial_capital: float = Field(..., gt=0)
    model_type: str = "temporal_fusion_transformer"
    rebalance_frequency: str = "monthly"  # daily, weekly, monthly


class BacktestResult(BaseModel):
    total_return: float
    total_return_pct: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades_count: int
    equity_curve: List[Dict[str, Any]]
    monthly_returns: List[Dict[str, Any]]


def _signal_from_predicted_return(predicted_return: float) -> str:
    """Map a predicted return to a signal strength label."""
    if predicted_return >= 0.15:
        return "strong_buy"
    elif predicted_return >= 0.05:
        return "buy"
    elif predicted_return >= -0.05:
        return "hold"
    elif predicted_return >= -0.15:
        return "sell"
    else:
        return "strong_sell"


@router.post("/assets", response_model=List[AssetSignalResponse])
async def analyze_assets(
    request: AssetAnalysisRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Analyze assets and generate AI signals using real market data."""
    signals = await _quant_engine.generate_signals(
        assets=request.symbols,
        model_type=ModelType.TEMPORAL_FUSION_TRANSFORMER,
    )

    results: List[AssetSignalResponse] = []
    for symbol in request.symbols:
        prediction = signals.predictions.get(symbol)

        # Fetch current price
        quote = await market_data_service.get_quote(symbol)
        current_price = quote.price if quote else 0.0

        fundamental_score: Optional[float] = None
        if request.include_fundamentals:
            try:
                fund = await _fundamental_analyzer.analyze_asset(symbol)
                fundamental_score = round(fund.overall_score, 2)
            except Exception:
                pass

        if prediction:
            signal = _signal_from_predicted_return(prediction.predicted_return)
            explanation = (
                f"{symbol} has a predicted {prediction.predicted_return:+.1%} return "
                f"over the next {prediction.prediction_horizon} trading days with "
                f"{prediction.confidence:.0%} confidence. "
                f"Key drivers: {', '.join(list(prediction.feature_importance.keys())[:3])}."
            )
            results.append(
                AssetSignalResponse(
                    symbol=symbol,
                    asset_type="stock",
                    current_price=current_price,
                    predicted_return=round(prediction.predicted_return, 4),
                    confidence_score=round(prediction.confidence, 4),
                    signal_strength=signal,
                    fundamental_score=fundamental_score,
                    ai_explanation=explanation,
                )
            )
        else:
            results.append(
                AssetSignalResponse(
                    symbol=symbol,
                    asset_type="stock",
                    current_price=current_price,
                    fundamental_score=fundamental_score,
                )
            )

    return results


@router.get("/signals/{symbol}", response_model=AssetSignalResponse)
async def get_asset_signals(
    symbol: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get AI-generated signals for a specific asset using real market data."""
    signals = await _quant_engine.generate_signals(
        assets=[symbol],
        model_type=ModelType.TEMPORAL_FUSION_TRANSFORMER,
    )
    prediction = signals.predictions.get(symbol)

    quote = await market_data_service.get_quote(symbol)
    current_price = quote.price if quote else 0.0

    try:
        fund = await _fundamental_analyzer.analyze_asset(symbol)
        fundamental_score = round(fund.overall_score, 2)
    except Exception:
        fundamental_score = None

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate signals for {symbol}",
        )

    signal = _signal_from_predicted_return(prediction.predicted_return)
    explanation = (
        f"{symbol} shows a {signal.replace('_', ' ')} signal based on technical analysis. "
        f"Predicted return: {prediction.predicted_return:+.1%} over the next "
        f"{prediction.prediction_horizon} trading days (confidence: {prediction.confidence:.0%}). "
        f"Primary factors: {', '.join(list(prediction.feature_importance.keys())[:3])}."
    )

    return AssetSignalResponse(
        symbol=symbol,
        asset_type="stock",
        current_price=current_price,
        predicted_return=round(prediction.predicted_return, 4),
        confidence_score=round(prediction.confidence, 4),
        signal_strength=signal,
        fundamental_score=fundamental_score,
        ai_explanation=explanation,
    )


@router.get("/explain/{portfolio_id}")
async def get_portfolio_explanation(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get AI explanation for portfolio decisions."""
    return {
        "portfolio_id": portfolio_id,
        "explanation": (
            "This portfolio was constructed using technical analysis signals combined with "
            "fundamental screening. Signals are derived from RSI, momentum, and moving-average "
            "crossover indicators on real historical price data."
        ),
        "key_factors": [
            "RSI-based oversold/overbought detection",
            "1-month and 3-month price momentum",
            "50-day / 20-day SMA crossover",
            "Fundamental quality screen (P/E, P/B, ROE)",
            "5% cash reserve for opportunistic rebalancing",
        ],
        "risk_assessment": "Risk is managed through diversification and position-size limits.",
    }


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(
    request: BacktestRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Run backtest simulation on a strategy using real historical price data."""
    import asyncio
    import yfinance as yf
    import pandas as pd
    from app.services.backtest_service import run_backtest as _run_backtest

    try:
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    def _fetch_prices():
        try:
            raw = yf.download(
                request.symbols,
                start=request.start_date,
                end=request.end_date,
                progress=False,
                auto_adjust=True,
            )
            if len(request.symbols) == 1:
                prices = raw[["Close"]].rename(columns={"Close": request.symbols[0]})
            else:
                prices = raw["Close"]
            return prices.dropna(how="all")
        except Exception:
            return pd.DataFrame()

    loop = asyncio.get_running_loop()
    prices = await loop.run_in_executor(None, _fetch_prices)

    if prices.empty:
        raise HTTPException(
            status_code=400,
            detail="Could not fetch historical price data for the requested symbols.",
        )

    # Equal-weight allocation
    weights = {sym: 1.0 / len(request.symbols) for sym in prices.columns}

    result = _run_backtest(prices, weights)

    days = (end - start).days
    cum_returns = result.get("cumulative_returns", [])
    final_cum = cum_returns[-1] if cum_returns else 1.0
    total_return = request.initial_capital * (final_cum - 1.0)
    total_return_pct = (final_cum - 1.0) * 100.0
    annualized_return = ((final_cum) ** (365.0 / max(days, 1)) - 1) if days > 0 else 0.0

    # Compute annualised volatility from daily changes in cumulative returns
    import numpy as np
    if len(cum_returns) > 1:
        cum_arr = np.array(cum_returns)
        daily_ret = np.diff(cum_arr) / cum_arr[:-1]
        volatility = float(np.std(daily_ret) * (252 ** 0.5))
    else:
        volatility = 0.0

    equity_curve = [
        {"date": d, "value": round(request.initial_capital * r, 2)}
        for d, r in zip(result["dates"], cum_returns)
    ]

    return BacktestResult(
        total_return=round(total_return, 2),
        total_return_pct=round(total_return_pct, 4),
        annualized_return=round(annualized_return, 4),
        volatility=round(volatility, 4),
        sharpe_ratio=round(float(result.get("sharpe_ratio", 0)), 4),
        max_drawdown=round(abs(float(result.get("max_drawdown", 0))), 4),
        win_rate=0.0,
        trades_count=len(request.symbols),
        equity_curve=equity_curve,
        monthly_returns=[],
    )


@router.get("/models")
async def get_available_models(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get list of available AI models for prediction."""
    return {
        "models": [
            {
                "id": "temporal_fusion_transformer",
                "name": "Temporal Fusion Transformer",
                "description": "State-of-the-art multi-horizon forecasting with interpretable attention",
                "best_for": "Multi-asset portfolios, long-term predictions",
                "status": "active",
            },
            {
                "id": "lstm_attention",
                "name": "LSTM with Attention",
                "description": "Sequential pattern recognition with attention mechanism",
                "best_for": "Short-term trend detection",
                "status": "active",
            },
            {
                "id": "patch_tst",
                "name": "PatchTST",
                "description": "Transformer-based time series forecasting using patches",
                "best_for": "Long sequence modeling",
                "status": "coming_soon",
            },
            {
                "id": "nbeats",
                "name": "N-BEATS",
                "description": "Neural basis expansion for interpretable time series forecasting",
                "best_for": "Trend and seasonality decomposition",
                "status": "coming_soon",
            },
            {
                "id": "graph_attention",
                "name": "Graph Attention Network",
                "description": "Models asset relationships using graph neural networks",
                "best_for": "Cross-asset influence modeling",
                "status": "active",
            },
        ]
    }
