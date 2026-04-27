"""
Portfolio endpoints — 3-layer AI investment system:
  Layer 1: Claude AI selects stocks from market news & sector analysis
  Layer 2: ML scoring engine (sklearn) ranks and scores candidates
  Layer 3: Portfolio optimizer + Claude reasoning per stock
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import asyncio
import json

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.portfolio import Portfolio, PortfolioHolding
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate, PortfolioResponse, PortfolioUpdate,
    PortfolioAnalysisRequest, PortfolioPerformance, RebalanceRecommendation,
    PortfolioHoldingCreate, SellHoldingRequest,
)
from app.engines.portfolio_engine.engine import PortfolioEngine
from app.services.wallet_service import WalletService

router = APIRouter()
portfolio_engine = PortfolioEngine()

_ETF_SYMBOLS = {"SPY","QQQ","VTI","BND","GLD","AGG","IEF","SCHD","VEA","VWO","VNQ",
                "XLF","XLK","XLV","XLE","XLU","XLI","IWM","SLV","DVY","VYM","TLT",
                "ARKK","SOXL"}

# Known annual volatilities — used for covariance matrix
_KNOWN_VOL: Dict[str, float] = {
    "AAPL":0.30,"MSFT":0.28,"GOOGL":0.30,"AMZN":0.35,"NVDA":0.50,
    "META":0.38,"TSLA":0.65,"AMD":0.55,"CRM":0.35,"SHOP":0.55,
    "JPM":0.25,"JNJ":0.18,"BAC":0.30,"GS":0.30,"V":0.25,"MA":0.25,
    "SPY":0.17,"QQQ":0.22,"VTI":0.17,"BND":0.05,"GLD":0.15,
    "AGG":0.04,"IEF":0.06,"SCHD":0.18,"SCHD":0.18,
    "CRWD":0.50,"NET":0.55,"PLTR":0.65,"COIN":0.80,"PYPL":0.40,
    "UNH":0.25,"PG":0.18,"KO":0.18,"WMT":0.20,"HD":0.22,"NEE":0.20,
}

_SECTOR_CLASS: Dict[str, str] = {
    "Technology":"tech","Consumer":"consumer","Finance":"finance",
    "Healthcare":"healthcare","US Equities":"broad_etf","Tech ETF":"tech_etf",
    "Bonds":"bond","Commodities":"gold","Dividend ETF":"dividend_etf",
    "Energy":"energy","Industrial":"industrial","Utilities":"utilities",
    "Real Estate":"reit","Materials":"materials","Communication":"tech",
    "Disruptive Tech":"tech","Semiconductor":"tech","Small-Cap ETF":"broad_etf",
}
_CLASS_CORR: Dict[tuple,float] = {
    ("tech","tech"):0.75,("tech","consumer"):0.60,("tech","finance"):0.50,
    ("tech","healthcare"):0.40,("tech","broad_etf"):0.85,("tech","tech_etf"):0.90,
    ("tech","bond"):-0.10,("tech","gold"):0.05,("tech","energy"):0.30,
    ("tech","utilities"):0.20,("tech","reit"):0.40,("tech","industrial"):0.50,
    ("consumer","consumer"):0.65,("consumer","finance"):0.55,("consumer","broad_etf"):0.82,
    ("consumer","tech_etf"):0.80,("consumer","bond"):-0.10,
    ("finance","finance"):0.70,("finance","broad_etf"):0.82,("finance","bond"):0.10,
    ("healthcare","healthcare"):0.65,("healthcare","broad_etf"):0.78,
    ("broad_etf","broad_etf"):0.95,("broad_etf","tech_etf"):0.90,
    ("broad_etf","bond"):-0.10,("broad_etf","gold"):0.05,
    ("tech_etf","bond"):-0.12,("bond","bond"):0.90,("gold","gold"):1.0,
    ("energy","energy"):0.70,("energy","broad_etf"):0.65,
    ("utilities","utilities"):0.70,("utilities","broad_etf"):0.60,
    ("reit","reit"):1.0,("reit","broad_etf"):0.70,
    ("industrial","industrial"):0.70,("industrial","broad_etf"):0.78,
}

def _get_corr(a_sector: str, b_sector: str) -> float:
    ca = _SECTOR_CLASS.get(a_sector, "tech")
    cb = _SECTOR_CLASS.get(b_sector, "tech")
    if ca == cb:
        return _CLASS_CORR.get((ca, cb), 0.65)
    key = (ca,cb) if (ca,cb) in _CLASS_CORR else (cb,ca)
    return _CLASS_CORR.get(key, 0.50)

def _build_cov_matrix(symbols: List[str], sectors: Dict[str,str]) -> np.ndarray:
    n = len(symbols)
    vols = [_KNOWN_VOL.get(s, 0.30) for s in symbols]
    cov = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            corr = 1.0 if i == j else _get_corr(sectors.get(symbols[i],"Other"), sectors.get(symbols[j],"Other"))
            cov[i,j] = vols[i] * vols[j] * corr
    return cov


async def _fetch_finnhub_quote(sym: str, api_key: str, client) -> Optional[dict]:
    try:
        r = await client.get("https://finnhub.io/api/v1/quote",
                              params={"symbol": sym, "token": api_key}, timeout=8)
        d = r.json()
        return d if d.get("c",0) > 0 else None
    except Exception:
        return None

async def _fetch_finnhub_rec(sym: str, api_key: str, client) -> Optional[dict]:
    try:
        r = await client.get("https://finnhub.io/api/v1/stock/recommendation",
                              params={"symbol": sym, "token": api_key}, timeout=8)
        data = r.json()
        return data[0] if data else None
    except Exception:
        return None


async def _generate_stock_reasoning(
    selected_stocks: List[dict],
    weights: Dict[str,float],
    scores: Dict[str,dict],
    risk_profile: str,
    market_context: str,
) -> str:
    """Claude generates per-stock reasoning for portfolio allocation."""
    try:
        from app.services.claude_service import query_claude
        stock_details = []
        for s in selected_stocks:
            sym = s["symbol"]
            w = weights.get(sym, 0)
            score = scores.get(sym, {})
            stock_details.append(
                f"{sym} ({s.get('sector','?')}): weight={w:.1%}, "
                f"ml_score={score.get('ml_score',0):.1f}/100, "
                f"predicted_return={score.get('predicted_return',0):.1%}, "
                f"daily_chg={score.get('daily_change_pct',0):+.2f}%"
            )
        prompt = (
            f"You are a portfolio manager explaining stock selections to a {risk_profile} investor.\n\n"
            f"Market context: {market_context[:300]}\n\n"
            f"Portfolio holdings:\n" + "\n".join(stock_details) + "\n\n"
            f"For each stock, write ONE sentence explaining:\n"
            f"1. Why this stock was selected (fundamentals + momentum + sector)\n"
            f"2. Why it's appropriate for a {risk_profile} investor\n\n"
            f"Format: SYMBOL: [reason]\nBe specific, factual, and professional. No markdown."
        )
        result = query_claude(prompt)
        return result.get("result", "")
    except Exception as exc:
        logger.warning("Claude reasoning failed: {}", exc)
        return ""


async def _generate_portfolio_explanation(
    name: str, risk_profile: str, assets: List[str],
    exp_return: float, volatility: float, sharpe: float,
    market_context: str,
) -> str:
    try:
        from app.services.claude_service import query_claude
        prompt = (
            f"Write a 4-sentence investment explanation for '{name}' ({risk_profile} risk portfolio). "
            f"Holdings: {', '.join(assets[:8])}. "
            f"Expected return: {exp_return:.1%}, volatility: {volatility:.1%}, Sharpe: {sharpe:.2f}. "
            f"Market context: {market_context[:200]}. "
            f"Explain: what this portfolio is, how it fits {risk_profile} profile, "
            f"what market trends it captures, and the key risk. Be professional and specific."
        )
        return query_claude(prompt).get("result", "")
    except Exception:
        return (f"AI-optimised {risk_profile} portfolio across {len(assets)} positions. "
                f"Expected return {exp_return:.1%}, volatility {volatility:.1%}.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0, limit: int = 100,
) -> Any:
    result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == current_user.id).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_in: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    3-Layer AI Portfolio Creation:
    1. Claude AI selects stocks from real market news + sector analysis
    2. ML engine (sklearn) scores & ranks all candidates with technical analysis
    3. Portfolio optimizer allocates weights + Claude explains each selection
    """
    from app.core.config import get_settings as _gs
    cfg = _gs()

    # ── Wallet check & deduction ───────────────────────────────────────────
    wallet_service = WalletService(db)
    wallet = await wallet_service.get_or_create_wallet(current_user.id)
    if wallet.balance < portfolio_in.investment_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Required: ${portfolio_in.investment_amount:,.2f}, "
                   f"Available: ${wallet.balance:,.2f}",
        )
    await wallet_service.deduct_for_investment(
        user_id=current_user.id,
        amount=portfolio_in.investment_amount,
        reference_id="portfolio_creation",
    )

    risk_profile = portfolio_in.risk_profile or current_user.risk_tolerance or "moderate"
    investment_horizon = getattr(current_user, "investment_horizon", 12) or 12

    # ── Create portfolio record ────────────────────────────────────────────
    portfolio = Portfolio(
        user_id=current_user.id,
        name=portfolio_in.name,
        description=portfolio_in.description,
        total_value=portfolio_in.investment_amount,
        invested_amount=portfolio_in.investment_amount,
        cash_reserve_pct=portfolio_in.cash_reserve_pct,
        risk_profile=risk_profile,
        model_type=portfolio_in.model_type,
        ai_explanation="AI analysis in progress…",
    )
    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)

    try:
        # ══ LAYER 1: Claude AI Stock Selection ════════════════════════════
        logger.info("Layer 1: Claude AI selecting stocks for {} profile", risk_profile)
        from app.services.ai_stock_selector import select_stocks_with_ai
        ai_selection = await select_stocks_with_ai(
            risk_profile=risk_profile,
            investment_horizon_months=investment_horizon,
        )
        candidate_stocks = ai_selection.get("stocks", [])
        market_context = ai_selection.get("market_context", "")
        logger.info("Layer 1 complete: {} candidates selected (source={})",
                    len(candidate_stocks), ai_selection.get("source"))

        # ══ LAYER 2: Fetch Finnhub data + ML Scoring ═════════════════════
        candidate_symbols = [s["symbol"] for s in candidate_stocks][:60]
        sectors_by_symbol = {s["symbol"]: s.get("sector","Other") for s in candidate_stocks}

        if not cfg.finnhub_api_key:
            raise HTTPException(status_code=503, detail="Finnhub API key not configured")

        logger.info("Layer 2: Fetching Finnhub data for {} candidates", len(candidate_symbols))
        import httpx
        async with httpx.AsyncClient(timeout=12) as client:
            q_tasks  = [_fetch_finnhub_quote(sym, cfg.finnhub_api_key, client) for sym in candidate_symbols]
            rec_tasks= [_fetch_finnhub_rec(sym, cfg.finnhub_api_key, client) for sym in candidate_symbols]
            quotes_raw, recs_raw = await asyncio.gather(
                asyncio.gather(*q_tasks, return_exceptions=True),
                asyncio.gather(*rec_tasks, return_exceptions=True),
            )

        quotes: Dict[str,dict] = {}
        recs: Dict[str,Optional[dict]] = {}
        for sym, q, r in zip(candidate_symbols, quotes_raw, recs_raw):
            if isinstance(q, dict) and q.get("c", 0) > 0:
                quotes[sym] = q
                recs[sym] = r if isinstance(r, dict) else None

        if not quotes:
            raise HTTPException(status_code=503, detail="Market data unavailable. Please retry.")

        # ── ML / DL Scoring ──────────────────────────────────────────────
        # Try DL ensemble (TFT + LSTM + N-BEATS) first;
        # fall back to sklearn RF+GB if models not yet trained.
        from app.engines.dl_engine.predictor import get_dl_predictor
        from app.engines.ml_engine.predictor import compute_sector_momentum

        dl_predictor    = get_dl_predictor()
        sector_momentum = compute_sector_momentum(quotes, sectors_by_symbol)
        vol_estimates   = {sym: _KNOWN_VOL.get(sym, 0.30) for sym in quotes}

        ml_scores = await dl_predictor.score_stocks(
            symbols       = list(quotes.keys()),
            av_key        = cfg.alpha_vantage_api_key or "",
            # Polygon.io is used as the primary historical data source
            quotes        = quotes,
            recs          = recs,
            sectors       = sectors_by_symbol,
        )

        model_source = next(
            (v.get("model_source","sklearn") for v in ml_scores.values()), "sklearn"
        )
        logger.info("Layer 2 complete — {} stocks scored via {}",
                    len(ml_scores), model_source)

        # Rank and select top 10 by ml_score
        ranked = sorted(
            [(sym, info) for sym, info in ml_scores.items()],
            key=lambda x: x[1].get("ml_score", 0),
            reverse=True,
        )
        selected_symbols = [sym for sym, _ in ranked[:10]]
        selected_stocks_info = [s for s in candidate_stocks if s["symbol"] in set(selected_symbols)]
        logger.info("Top {} stocks selected by {} model", len(selected_symbols), model_source)

        # ══ LAYER 3: Portfolio Optimization ══════════════════════════════
        # Apply risk-profile floors so expected_return is never misleadingly low
        _RETURN_FLOORS = {"conservative": 0.04, "moderate": 0.06, "aggressive": 0.09}
        _floor = _RETURN_FLOORS.get(risk_profile, 0.06)
        predictions = {
            sym: max(_floor, ml_scores[sym]["predicted_return"])
            for sym in selected_symbols
        }
        cov_matrix  = _build_cov_matrix(selected_symbols, sectors_by_symbol)

        from app.engines.portfolio_engine.allocation import PortfolioConstraints
        constraints = PortfolioConstraints(
            min_weight=0.03, max_weight=0.25, min_assets=3, max_assets=10,
            cash_reserve=portfolio_in.cash_reserve_pct,
        )
        allocation = await portfolio_engine.optimize_allocation(
            assets=selected_symbols, predictions=predictions, risk_profile=risk_profile,
            constraints=constraints, optimization_method="mean_variance", cov_matrix=cov_matrix,
        )

        # ══ Claude Reasoning per stock ════════════════════════════════════
        logger.info("Layer 3: Generating Claude per-stock reasoning")
        stock_reasoning = await _generate_stock_reasoning(
            selected_stocks_info, allocation.weights, ml_scores, risk_profile, market_context
        )

        # ══ Create holdings ═══════════════════════════════════════════════
        # NOTE: allocation.weights already represent fractions of the TOTAL portfolio
        # (optimizer normalises to investable_fraction=0.95 for stock weights, 0.05 for cash).
        # So market_value = total_investment × weight — NOT investable × weight.
        # Using investable would double-count the 5% cash deduction.
        total_investment = portfolio_in.investment_amount
        cash_amount = total_investment * portfolio_in.cash_reserve_pct

        for sym, weight in allocation.weights.items():
            if weight < 0.01:
                continue
            score = ml_scores.get(sym, {})
            current_price = score.get("current_price", 0)
            if current_price <= 0:
                continue
            market_value = total_investment * weight   # correct: weight is fraction of total
            db.add(PortfolioHolding(
                portfolio_id=portfolio.id,
                symbol=sym,
                asset_type="etf" if sym in _ETF_SYMBOLS else "stock",
                sector=sectors_by_symbol.get(sym, "Other"),
                weight=weight,
                quantity=round(market_value / current_price, 6),
                avg_price=round(current_price, 4),
                current_price=round(current_price, 4),
                market_value=round(market_value, 2),
                predicted_return=score.get("predicted_return", 0.05),
                confidence_score=score.get("confidence", 0.60),
                signal_strength=score.get("signal_strength", "hold"),
            ))

        db.add(PortfolioHolding(
            portfolio_id=portfolio.id, symbol="CASH", asset_type="cash",
            weight=portfolio_in.cash_reserve_pct, quantity=cash_amount,
            avg_price=1.0, current_price=1.0, market_value=cash_amount,
            predicted_return=0.0, confidence_score=1.0, signal_strength="hold",
        ))

        # ══ AI Explanation ════════════════════════════════════════════════
        ai_text = await _generate_portfolio_explanation(
            portfolio_in.name, risk_profile, selected_symbols,
            allocation.expected_return, allocation.volatility, allocation.sharpe_ratio,
            market_context,
        )

        portfolio.expected_return = allocation.expected_return
        portfolio.volatility      = allocation.volatility
        portfolio.sharpe_ratio    = allocation.sharpe_ratio
        portfolio.var_95          = allocation.var_95
        portfolio.cvar_95         = allocation.cvar_95
        portfolio.ai_explanation  = ai_text
        portfolio.stock_reasoning = stock_reasoning
        portfolio.market_context  = market_context

        # Initial snapshot
        from app.models.portfolio import PortfolioSnapshot
        db.add(PortfolioSnapshot(
            portfolio_id=portfolio.id,
            total_value=total_investment,
            cash_value=cash_amount,
            stocks_value=total_investment - cash_amount,
        ))

        await db.commit()
        await db.refresh(portfolio)
        logger.info("Portfolio {} created — {} stocks, er={:.1%}, vol={:.1%}, src={}",
                    portfolio.id, len(selected_symbols),
                    allocation.expected_return, allocation.volatility,
                    ai_selection.get("source"))
        return portfolio

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Portfolio creation failed: {}", exc, exc_info=True)
        # Refund wallet
        try:
            await wallet_service.refund_investment(
                user_id=current_user.id,
                amount=portfolio_in.investment_amount,
                reference_id=f"portfolio_{portfolio.id}_refund",
            )
            await db.delete(portfolio)
            await db.commit()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio creation failed: {exc}",
        )


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return portfolio


@router.get("/{portfolio_id}/chart")
async def get_portfolio_chart(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Return real time-series data for portfolio performance chart."""
    from app.services.portfolio_updater import get_portfolio_chart_data
    data = await get_portfolio_chart_data(db, portfolio_id)
    return {"portfolio_id": portfolio_id, "chart_data": data}


@router.post("/{portfolio_id}/refresh")
async def refresh_portfolio_prices(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Refresh holding prices from Finnhub and update portfolio total_value."""
    from app.services.portfolio_updater import update_portfolio_prices
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    new_value = await update_portfolio_prices(db, portfolio_id)
    await db.refresh(portfolio)
    return {"portfolio_id": portfolio_id, "new_total_value": new_value, "portfolio": portfolio}


@router.get("/{portfolio_id}/reasoning")
async def get_portfolio_reasoning(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Return Claude's per-stock reasoning for this portfolio."""
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {
        "portfolio_id": portfolio_id,
        "market_context": portfolio.market_context or "",
        "stock_reasoning": portfolio.stock_reasoning or "",
        "ai_explanation": portfolio.ai_explanation or "",
    }


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    portfolio_update: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    for field, value in portfolio_update.model_dump(exclude_unset=True).items():
        setattr(portfolio, field, value)
    await db.commit()
    await db.refresh(portfolio)
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_200_OK)
async def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    await db.delete(portfolio)
    await db.commit()
    return {"message": "Portfolio deleted successfully"}


@router.get("/{portfolio_id}/performance", response_model=PortfolioPerformance)
async def get_portfolio_performance(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    invested = portfolio.invested_amount or 0
    total_value = portfolio.total_value or 0
    total_return = total_value - invested
    total_return_pct = (total_return / invested * 100) if invested > 0 else 0
    return PortfolioPerformance(
        portfolio_id=portfolio.id, total_return=total_return, total_return_pct=total_return_pct,
        annualized_return=portfolio.expected_return or 0, volatility=portfolio.volatility or 0,
        sharpe_ratio=portfolio.sharpe_ratio or 0, max_drawdown=portfolio.max_drawdown or 0,
        var_95=portfolio.var_95 or 0, cvar_95=portfolio.cvar_95 or 0,
    )


@router.post("/{portfolio_id}/rebalance", response_model=RebalanceRecommendation)
async def rebalance_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    total = portfolio.total_value or 0
    current_weights = {h.symbol: h.market_value/total if total > 0 else 0 for h in portfolio.holdings}
    target_weights  = {h.symbol: h.weight for h in portfolio.holdings}
    check = await portfolio_engine.check_rebalance_needed(current_weights, target_weights, threshold=0.05)
    return RebalanceRecommendation(
        portfolio_id=portfolio.id, rebalance_needed=check.rebalance_needed,
        drift_pct=check.drift_pct,
        recommendations=[{"symbol":s,"action":"rebalance"} for s in current_weights if check.rebalance_needed],
    )


@router.post("/{portfolio_id}/sell", response_model=PortfolioResponse)
async def sell_holding(
    portfolio_id: int,
    sell_in: SellHoldingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Sell a stock holding (fully or partially).

    - Sell by `quantity` (shares), `amount` (dollars), or `sell_all=true`
    - Proceeds are credited to the user's wallet instantly
    - Portfolio total_value and holding weights are recalculated
    """

    # ── Fetch portfolio ─────────────────────────────────────────────────────
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # ── Find the holding ────────────────────────────────────────────────────
    symbol = sell_in.symbol.upper()
    holding = next(
        (h for h in portfolio.holdings if h.symbol == symbol and h.asset_type != "cash"),
        None,
    )
    if not holding:
        raise HTTPException(status_code=404, detail=f"Holding '{symbol}' not found in this portfolio")

    current_price = holding.current_price
    if current_price <= 0:
        raise HTTPException(status_code=400, detail="Cannot sell — current price is unavailable")

    # ── Determine quantity to sell ───────────────────────────────────────────
    if sell_in.sell_all:
        qty_to_sell = holding.quantity
    elif sell_in.quantity:
        qty_to_sell = sell_in.quantity
    elif sell_in.amount:
        qty_to_sell = sell_in.amount / current_price
    else:
        raise HTTPException(status_code=400, detail="Provide quantity, amount, or sell_all=true")

    qty_to_sell = round(min(qty_to_sell, holding.quantity), 6)
    if qty_to_sell <= 0:
        raise HTTPException(status_code=400, detail="Quantity to sell must be greater than 0")

    proceeds = round(qty_to_sell * current_price, 2)

    # ── Update or remove the holding ─────────────────────────────────────────
    remaining_qty = round(holding.quantity - qty_to_sell, 6)
    if remaining_qty < 0.0001:  # selling everything
        await db.delete(holding)
    else:
        holding.quantity    = remaining_qty
        holding.market_value = round(remaining_qty * current_price, 2)

    # ── Credit proceeds to wallet ─────────────────────────────────────────────
    wallet_service = WalletService(db)
    await wallet_service.add_from_sale(
        user_id=current_user.id,
        amount=proceeds,
        reference_id=f"port_{portfolio_id}_sell_{symbol}",
        description=f"Sale: {qty_to_sell:.4f} × {symbol} @ ${current_price:.2f}",
    )

    # ── Record portfolio transaction ──────────────────────────────────────────
    from app.models.portfolio import PortfolioTransaction
    cost_basis_sold = round(qty_to_sell * holding.avg_price, 2)
    db.add(PortfolioTransaction(
        portfolio_id=portfolio_id,
        transaction_type="sell",
        symbol=symbol,
        quantity=qty_to_sell,
        price=current_price,
        amount=proceeds,
        description=f"Sold {qty_to_sell:.4f} shares at ${current_price:.2f}",
    ))

    # ── Reduce invested_amount by cost basis of shares sold ───────────────────
    # This keeps "Since Creation" meaningful: it always reflects unrealised P&L
    # on the remaining shares (not distorted by what went to wallet).
    portfolio.invested_amount = round(
        max(0.0, (portfolio.invested_amount or 0) - cost_basis_sold), 2
    )

    # ── Flush so SQLAlchemy sees the deleted/updated holding ──────────────────
    await db.flush()
    await db.refresh(portfolio)

    # ── Recalculate portfolio total_value and weights ─────────────────────────
    remaining_holdings = [h for h in portfolio.holdings]
    new_total = round(sum(h.market_value for h in remaining_holdings), 2)
    portfolio.total_value = new_total

    if new_total > 0:
        for h in remaining_holdings:
            h.weight = round(h.market_value / new_total, 6)

    await db.commit()
    await db.refresh(portfolio)
    logger.info(
        "Sold {} shares of {} from portfolio {} — proceeds ${}, new total ${}",
        qty_to_sell, symbol, portfolio_id, proceeds, new_total,
    )
    return portfolio


@router.post("/analyze")
async def analyze_portfolio(
    analysis_request: PortfolioAnalysisRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    from app.engines.quant_engine.engine import QuantEngine, ModelType
    qe = QuantEngine()
    mt = ModelType.TEMPORAL_FUSION_TRANSFORMER
    if analysis_request.model_type == "lstm_attention":
        mt = ModelType.LSTM_ATTENTION
    elif analysis_request.model_type == "graph_attention":
        mt = ModelType.GRAPH_ATTENTION
    assets = analysis_request.preferred_assets or ["AAPL","MSFT","GOOGL","AMZN","NVDA"]
    signals = await qe.generate_signals(assets=assets[:10], model_type=mt)
    return {
        "status":"success","assets_analyzed":len(assets),
        "top_picks":signals.rankings[:5],"market_regime":signals.market_regime,
        "overall_confidence":signals.overall_confidence,
        "predictions":{s:{"predicted_return":p.predicted_return,"confidence":p.confidence}
                        for s,p in signals.predictions.items()},
    }


@router.post("/{portfolio_id}/holdings", response_model=PortfolioResponse)
async def add_holding(
    portfolio_id: int,
    holding_in: PortfolioHoldingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    from app.services.market_data import market_data_service
    quote = await market_data_service.get_quote(holding_in.symbol)
    price = quote.price if quote else holding_in.avg_price
    holding = PortfolioHolding(
        portfolio_id=portfolio_id, symbol=holding_in.symbol, asset_type=holding_in.asset_type,
        weight=holding_in.weight, quantity=holding_in.quantity,
        avg_price=holding_in.avg_price, current_price=price,
        market_value=holding_in.quantity * price,
    )
    db.add(holding)
    portfolio.total_value = (portfolio.total_value or 0) + holding.market_value
    await db.commit()
    await db.refresh(portfolio)
    return portfolio
