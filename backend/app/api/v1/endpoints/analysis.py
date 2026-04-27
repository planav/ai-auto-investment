"""
Analysis endpoints — powered by Claude AI + Finnhub real data.

/analysis/stock/{symbol}      — Full fundamental + technical + AI analysis of any stock
/analysis/assets              — Bulk signals for a list of stocks
/analysis/signals/{symbol}    — Quick signal for a single stock
/analysis/explain/{portfolio_id} — AI reasoning for portfolio allocation
/analysis/backtest            — Strategy backtest
/analysis/models              — Available ML models
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from loguru import logger

from app.api.deps import get_current_user
from app.models.user import User
from app.services.market_data import market_data_service

router = APIRouter()

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class StockAnalysisResponse(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    daily_change_pct: float
    signal: str                  # strong_buy | buy | hold | sell | strong_sell
    confidence: float
    overall_score: float         # 0–100
    fundamental_analysis: str
    technical_analysis: str
    market_sentiment: str
    growth_catalysts: str
    key_risks: str
    valuation_assessment: str
    investment_recommendation: str
    analyst_consensus: Optional[str] = None
    price_target: Optional[float] = None
    sector: Optional[str] = None


class AssetSignalResponse(BaseModel):
    symbol: str
    asset_type: str
    current_price: float
    predicted_return: Optional[float] = None
    confidence_score: Optional[float] = None
    signal_strength: str = "hold"
    fundamental_score: Optional[float] = None
    ai_explanation: Optional[str] = None


class AssetAnalysisRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=1, max_length=50)
    include_fundamentals: bool = True
    include_sentiment: bool = True


class BacktestRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    symbols: List[str] = Field(..., min_length=1, max_length=50)
    start_date: str
    end_date: str
    initial_capital: float = Field(..., gt=0)
    model_type: str = "temporal_fusion_transformer"
    rebalance_frequency: str = "monthly"


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


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

async def _get_finnhub_data(symbol: str) -> dict:
    """
    Fetch all available free-tier Finnhub data for a symbol:
    quote, company_profile, recommendation_trends, news.
    """
    import httpx
    from app.core.config import get_settings
    cfg = get_settings()
    if not cfg.finnhub_api_key:
        return {}

    async with httpx.AsyncClient(timeout=10) as client:
        import asyncio
        q_task    = client.get("https://finnhub.io/api/v1/quote",
                               params={"symbol": symbol, "token": cfg.finnhub_api_key})
        prof_task = client.get("https://finnhub.io/api/v1/stock/profile2",
                               params={"symbol": symbol, "token": cfg.finnhub_api_key})
        rec_task  = client.get("https://finnhub.io/api/v1/stock/recommendation",
                               params={"symbol": symbol, "token": cfg.finnhub_api_key})
        news_task = client.get("https://finnhub.io/api/v1/company-news",
                               params={"symbol": symbol, "token": cfg.finnhub_api_key,
                                       "from": "2026-04-01", "to": "2026-04-22"})
        metric_task = client.get("https://finnhub.io/api/v1/stock/metric",
                                 params={"symbol": symbol, "metric": "all",
                                         "token": cfg.finnhub_api_key})

        results = await asyncio.gather(q_task, prof_task, rec_task, news_task, metric_task,
                                       return_exceptions=True)

    data = {}
    labels = ["quote", "profile", "recommendations", "news", "metrics"]
    for label, r in zip(labels, results):
        if isinstance(r, Exception):
            data[label] = {}
        else:
            try:
                data[label] = r.json()
            except Exception:
                data[label] = {}

    return data


def _summarise_news(articles: list, n: int = 5) -> str:
    if not articles:
        return "No recent news available."
    summaries = []
    for a in articles[:n]:
        headline = a.get("headline") or a.get("title", "")
        summary  = a.get("summary", "")
        if headline:
            summaries.append(f"• {headline}: {summary[:120]}")
    return "\n".join(summaries) if summaries else "No recent news."


def _summarise_recommendations(recs: list) -> str:
    if not recs:
        return "No analyst recommendations available."
    latest = recs[0]
    sb = latest.get("strongBuy", 0)
    b  = latest.get("buy", 0)
    h  = latest.get("hold", 0)
    s  = latest.get("sell", 0)
    ss = latest.get("strongSell", 0)
    total = sb + b + h + s + ss
    period = latest.get("period", "latest")
    if total == 0:
        return "No analyst coverage."
    pct_buy = (sb + b) / total * 100
    return (f"As of {period}: {total} analysts — "
            f"Strong Buy: {sb}, Buy: {b}, Hold: {h}, Sell: {s}, Strong Sell: {ss}. "
            f"{pct_buy:.0f}% bullish consensus.")


def _extract_key_metrics(metrics_data: dict) -> str:
    m = metrics_data.get("metric", {})
    if not m:
        return "Financial metrics unavailable."
    parts = []
    pe = m.get("peNormalizedAnnual") or m.get("peExclExtraTTM")
    if pe:
        parts.append(f"P/E: {pe:.1f}")
    pb = m.get("pb")
    if pb:
        parts.append(f"P/B: {pb:.1f}")
    roe = m.get("roeTTM")
    if roe:
        parts.append(f"ROE: {roe:.1%}")
    rev_growth = m.get("revenueGrowthTTMYoy")
    if rev_growth:
        parts.append(f"Revenue Growth (YoY): {rev_growth:.1%}")
    margin = m.get("netProfitMarginTTM")
    if margin:
        parts.append(f"Net Margin: {margin:.1%}")
    debt_eq = m.get("totalDebt/totalEquityAnnual")
    if debt_eq:
        parts.append(f"Debt/Equity: {debt_eq:.2f}")
    beta = m.get("beta")
    if beta:
        parts.append(f"Beta: {beta:.2f}")
    wk52_high = m.get("52WeekHigh")
    wk52_low  = m.get("52WeekLow")
    if wk52_high and wk52_low:
        parts.append(f"52W Range: ${wk52_low:.2f}–${wk52_high:.2f}")
    return ", ".join(parts) if parts else "Key metrics not available."


# ---------------------------------------------------------------------------
# Main deep analysis endpoint
# ---------------------------------------------------------------------------

@router.get("/stock/{symbol}", response_model=StockAnalysisResponse)
async def get_deep_stock_analysis(
    symbol: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Full Claude AI analysis of a stock:
    Fundamental analysis + technical signals + news sentiment +
    growth catalysts + risks + valuation + recommendation.
    """
    symbol = symbol.upper().strip()
    logger.info("Deep analysis requested for {}", symbol)

    # Fetch all Finnhub data
    fh = await _get_finnhub_data(symbol)

    quote   = fh.get("quote", {})
    profile = fh.get("profile", {})
    recs    = fh.get("recommendations", [])
    news    = fh.get("news", []) if isinstance(fh.get("news"), list) else []
    metrics = fh.get("metrics", {})

    current_price   = float(quote.get("c", 0) or 0)
    daily_change    = float(quote.get("dp", 0) or 0)
    company_name    = profile.get("name", symbol)
    sector          = profile.get("finnhubIndustry", "Unknown")
    market_cap      = profile.get("marketCapitalization", 0)
    country         = profile.get("country", "US")
    exchange        = profile.get("exchange", "")
    description     = profile.get("weburl", "")

    rec_summary  = _summarise_recommendations(recs)
    news_summary = _summarise_news(news)
    key_metrics  = _extract_key_metrics(metrics)

    # Technical signals from quote
    c, pc = current_price, float(quote.get("pc", current_price) or current_price)
    h, l  = float(quote.get("h", c) or c), float(quote.get("l", c) or c)
    o     = float(quote.get("o", c) or c)
    intraday_move = (c - o) / o * 100 if o > 0 else 0
    range_pct     = (h - l) / pc * 100 if pc > 0 else 0

    if not current_price:
        raise HTTPException(status_code=404, detail=f"No market data found for {symbol}")

    # Build comprehensive Claude prompt
    from app.core.config import get_settings
    cfg = get_settings()

    if not cfg.anthropic_api_key:
        # Fallback rule-based analysis
        return _rule_based_analysis(symbol, company_name, sector, current_price,
                                    daily_change, rec_summary, key_metrics)

    prompt = f"""You are a senior equity research analyst at a top investment bank.
Provide a COMPREHENSIVE investment analysis for {symbol} ({company_name}).

=== MARKET DATA ===
Current Price: ${current_price:.2f}
Daily Change: {daily_change:+.2f}%
Today's Range: ${l:.2f} – ${h:.2f}
Open: ${o:.2f} | Prev Close: ${pc:.2f}
Intraday Move: {intraday_move:+.2f}%
Day Range %: {range_pct:.2f}%

=== COMPANY INFO ===
Sector: {sector}
Market Cap: ${market_cap/1000:.1f}B (approx, in thousands)
Exchange: {exchange} | Country: {country}

=== KEY FINANCIAL METRICS ===
{key_metrics}

=== ANALYST CONSENSUS ===
{rec_summary}

=== RECENT NEWS (last 30 days) ===
{news_summary}

=== YOUR TASK ===
Write a professional, detailed investment analysis covering ALL of the following sections.
Each section must be 2-4 sentences with specific, actionable insights. Use the data above.

1. FUNDAMENTAL_ANALYSIS: Revenue trends, profitability, balance sheet strength, ROE, margins, debt levels
2. TECHNICAL_ANALYSIS: Price action, momentum, support/resistance levels, volatility, trend direction
3. MARKET_SENTIMENT: News sentiment, analyst consensus, institutional interest, market conditions
4. GROWTH_CATALYSTS: Key growth drivers, product pipeline, market expansion, competitive advantages
5. KEY_RISKS: Main risk factors, competitive threats, regulatory risks, macro headwinds
6. VALUATION_ASSESSMENT: Is it cheap/fair/expensive vs peers and history? P/E, P/B context
7. INVESTMENT_RECOMMENDATION: Specific recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell) with reasoning and suggested time horizon

Also provide:
- OVERALL_SCORE: A score from 0-100 (where 100 = best investment opportunity)
- PRICE_TARGET: Your 12-month price target in USD

Return ONLY a valid JSON object with these exact keys (no markdown, no extra text):
{{
  "fundamental_analysis": "...",
  "technical_analysis": "...",
  "market_sentiment": "...",
  "growth_catalysts": "...",
  "key_risks": "...",
  "valuation_assessment": "...",
  "investment_recommendation": "...",
  "signal": "strong_buy|buy|hold|sell|strong_sell",
  "confidence": 0.0-1.0,
  "overall_score": 0-100,
  "price_target": 0.0,
  "analyst_consensus": "..."
}}"""

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",  # Use Sonnet for richer analysis
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()

        import json, re
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        analysis = json.loads(m.group() if m else raw)

        return StockAnalysisResponse(
            symbol=symbol,
            company_name=company_name,
            current_price=current_price,
            daily_change_pct=daily_change,
            signal=analysis.get("signal", "hold"),
            confidence=float(analysis.get("confidence", 0.65)),
            overall_score=float(analysis.get("overall_score", 50)),
            fundamental_analysis=analysis.get("fundamental_analysis", ""),
            technical_analysis=analysis.get("technical_analysis", ""),
            market_sentiment=analysis.get("market_sentiment", ""),
            growth_catalysts=analysis.get("growth_catalysts", ""),
            key_risks=analysis.get("key_risks", ""),
            valuation_assessment=analysis.get("valuation_assessment", ""),
            investment_recommendation=analysis.get("investment_recommendation", ""),
            analyst_consensus=analysis.get("analyst_consensus", rec_summary),
            price_target=float(analysis.get("price_target", 0)) or None,
            sector=sector,
        )

    except Exception as exc:
        logger.error("Claude analysis failed for {}: {}", symbol, exc)
        return _rule_based_analysis(symbol, company_name, sector, current_price,
                                    daily_change, rec_summary, key_metrics)


def _rule_based_analysis(
    symbol, company_name, sector, price, daily_change, rec_summary, key_metrics
) -> StockAnalysisResponse:
    """Simple fallback when Claude is unavailable."""
    signal = ("buy" if daily_change > 1.5 else
              "sell" if daily_change < -1.5 else "hold")
    return StockAnalysisResponse(
        symbol=symbol, company_name=company_name, current_price=price,
        daily_change_pct=daily_change, signal=signal, confidence=0.55,
        overall_score=55.0,
        fundamental_analysis=f"{key_metrics}. Further analysis requires Claude AI.",
        technical_analysis=f"Daily change: {daily_change:+.2f}%. AI analysis unavailable.",
        market_sentiment=rec_summary,
        growth_catalysts="Detailed growth analysis requires Claude AI configuration.",
        key_risks="Risk analysis requires Claude AI configuration.",
        valuation_assessment="Valuation analysis requires Claude AI configuration.",
        investment_recommendation=f"Hold — limited data available. {rec_summary}",
        sector=sector,
    )


# ---------------------------------------------------------------------------
# Bulk signals endpoint
# ---------------------------------------------------------------------------

@router.post("/assets", response_model=List[AssetSignalResponse])
async def analyze_assets(
    request: AssetAnalysisRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Quick signals for a list of stocks using Finnhub + ML scoring."""
    from app.engines.ml_engine.predictor import score_stocks, compute_sector_momentum
    from app.core.config import get_settings
    import httpx, asyncio

    cfg = get_settings()
    symbols = [s.upper() for s in request.symbols[:20]]

    if not cfg.finnhub_api_key:
        raise HTTPException(status_code=503, detail="Finnhub API key not configured")

    async with httpx.AsyncClient(timeout=10) as client:
        q_tasks  = [client.get("https://finnhub.io/api/v1/quote",
                               params={"symbol":s,"token":cfg.finnhub_api_key}) for s in symbols]
        rec_tasks= [client.get("https://finnhub.io/api/v1/stock/recommendation",
                               params={"symbol":s,"token":cfg.finnhub_api_key}) for s in symbols]
        quotes_raw, recs_raw = await asyncio.gather(
            asyncio.gather(*q_tasks, return_exceptions=True),
            asyncio.gather(*rec_tasks, return_exceptions=True),
        )

    quotes, recs = {}, {}
    for sym, q, r in zip(symbols, quotes_raw, recs_raw):
        if isinstance(q, Exception): continue
        try:
            qd = q.json()
            if qd.get("c",0) > 0:
                quotes[sym] = qd
                recs[sym] = r.json()[0] if not isinstance(r, Exception) and r.json() else None
        except Exception:
            pass

    sector_momentum = compute_sector_momentum(quotes, {s: "Other" for s in quotes})
    ml_scores = score_stocks(
        symbols=list(quotes.keys()), quotes=quotes, recommendations=recs,
        sector_momentum=sector_momentum,
        vol_estimates={s: 0.30 for s in quotes},
        sectors={s: "Other" for s in quotes},
    )

    results = []
    for sym in symbols:
        score = ml_scores.get(sym, {})
        q = quotes.get(sym, {})
        price = score.get("current_price", 0) or float(q.get("c", 0))
        pred  = score.get("predicted_return", 0.05)
        conf  = score.get("confidence", 0.55)
        sig   = score.get("signal_strength", "hold")
        expl = (f"{sym}: ML score {score.get('ml_score',50):.0f}/100. "
                f"Predicted 30d return: {pred:+.1%}. "
                f"Daily change: {score.get('daily_change_pct',0):+.2f}%. "
                f"Analyst: {score.get('analyst_score',0):+.2f}.")
        results.append(AssetSignalResponse(
            symbol=sym, asset_type="stock", current_price=price,
            predicted_return=round(pred,4), confidence_score=round(conf,4),
            signal_strength=sig, ai_explanation=expl,
        ))

    return results


@router.get("/signals/{symbol}", response_model=AssetSignalResponse)
async def get_asset_signals(
    symbol: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Quick ML signal for a single stock."""
    result = await analyze_assets(
        AssetAnalysisRequest(symbols=[symbol]),
        current_user=current_user,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Could not analyse {symbol}")
    return result[0]


@router.get("/explain/{portfolio_id}")
async def get_portfolio_explanation(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Return Claude's per-stock reasoning for a portfolio (stored during creation)."""
    from app.db.session import get_db
    from sqlalchemy import select
    from app.models.portfolio import Portfolio

    # Note: can't use FastAPI DI here directly, so we import the DB
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
        )
        portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return {
        "portfolio_id": portfolio_id,
        "market_context": portfolio.market_context or "Market context not available.",
        "stock_reasoning": portfolio.stock_reasoning or "Stock reasoning not available.",
        "ai_explanation": portfolio.ai_explanation or "AI explanation not available.",
        "key_factors": [
            "Claude AI analyzed real market news to select candidate stocks",
            "sklearn ML ensemble (RandomForest + GradientBoosting) scored and ranked candidates",
            "Mean-variance portfolio optimization allocated weights based on risk profile",
            "Claude generated per-stock reasoning explaining each allocation decision",
            f"Risk profile: {portfolio.risk_profile} | Expected return: "
            f"{(portfolio.expected_return or 0):.1%} | Sharpe: {(portfolio.sharpe_ratio or 0):.2f}",
        ],
    }


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(
    request: BacktestRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Run equal-weight backtest over historical data using Alpha Vantage."""
    import asyncio
    import numpy as np
    from app.services.backtest_service import run_backtest as _run_backtest
    from app.core.config import get_settings as _gs
    import httpx

    cfg = _gs()
    try:
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end   = datetime.strptime(request.end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Fetch AV data sequentially (rate limit: 5/min)
    import pandas as pd
    prices_dict = {}
    async with httpx.AsyncClient(timeout=15) as client:
        for sym in request.symbols[:5]:   # cap to avoid rate limits
            try:
                r = await client.get(
                    "https://www.alphavantage.co/query",
                    params={"function":"TIME_SERIES_DAILY","symbol":sym,
                            "outputsize":"full","apikey":cfg.alpha_vantage_api_key or "demo"},
                )
                ts = r.json().get("Time Series (Daily)", {})
                if ts:
                    series = {d: float(v["4. close"]) for d, v in ts.items()
                              if request.start_date <= d <= request.end_date}
                    if series:
                        prices_dict[sym] = pd.Series(series).sort_index()
            except Exception as exc:
                logger.warning("AV fetch failed for {}: {}", sym, exc)
            await asyncio.sleep(0.5)

    if not prices_dict:
        raise HTTPException(status_code=400, detail="Could not fetch historical price data.")

    prices = pd.DataFrame(prices_dict).dropna(how="all")
    weights = {sym: 1.0/len(prices.columns) for sym in prices.columns}
    result = _run_backtest(prices, weights)

    days = (end - start).days
    cum = result.get("cumulative_returns", [1.0])
    final_cum = cum[-1] if cum else 1.0
    total_return = request.initial_capital * (final_cum - 1.0)
    total_return_pct = (final_cum - 1.0) * 100.0
    annualized = ((final_cum) ** (365.0/max(days,1)) - 1) if days > 0 else 0.0

    if len(cum) > 1:
        arr = np.array(cum)
        daily_ret = np.diff(arr) / arr[:-1]
        vol = float(np.std(daily_ret) * (252**0.5))
    else:
        vol = 0.0

    equity_curve = [
        {"date": d, "value": round(request.initial_capital * r, 2)}
        for d, r in zip(result.get("dates",[]), cum)
    ]

    return BacktestResult(
        total_return=round(total_return, 2),
        total_return_pct=round(total_return_pct, 4),
        annualized_return=round(annualized, 4),
        volatility=round(vol, 4),
        sharpe_ratio=round(float(result.get("sharpe_ratio",0)), 4),
        max_drawdown=round(abs(float(result.get("max_drawdown",0))), 4),
        win_rate=0.0, trades_count=len(request.symbols),
        equity_curve=equity_curve, monthly_returns=[],
    )


@router.get("/models")
async def get_available_models(
    current_user: User = Depends(get_current_user),
) -> Any:
    return {
        "models": [
            {"id": "temporal_fusion_transformer", "name": "TFT — GradientBoosting Ensemble",
             "description": "GradientBoosting + momentum signals (sklearn)", "status": "active"},
            {"id": "lstm_attention", "name": "LSTM Attention — RandomForest Ensemble",
             "description": "RandomForest on technical features (sklearn)", "status": "active"},
            {"id": "graph_attention", "name": "Graph Attention — ExtraTrees",
             "description": "ExtraTreesRegressor with sector graphs (sklearn)", "status": "active"},
        ]
    }
