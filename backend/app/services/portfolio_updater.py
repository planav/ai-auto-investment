"""
Layer 3: Portfolio Real-Time Updater
Polls Finnhub every few minutes to refresh holding prices,
updates portfolio total_value, and writes snapshots for chart history.
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import httpx
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

settings = get_settings()

_POLL_INTERVAL_SECONDS = 300   # 5 minutes between updates


async def _fetch_quotes_batch(symbols: List[str], api_key: str) -> Dict[str, dict]:
    """Fetch Finnhub quotes for a list of symbols concurrently."""
    if not symbols or not api_key:
        return {}

    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [
            client.get("https://finnhub.io/api/v1/quote",
                       params={"symbol": sym, "token": api_key})
            for sym in symbols
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    result = {}
    for sym, resp in zip(symbols, responses):
        if isinstance(resp, Exception):
            continue
        try:
            data = resp.json()
            if data.get("c", 0) > 0:
                result[sym] = data
        except Exception:
            pass
    return result


async def update_portfolio_prices(db: AsyncSession, portfolio_id: int) -> Optional[float]:
    """
    Refresh all holding prices for a portfolio, update total_value,
    and write a snapshot record. Returns the new total_value.
    """
    from app.models.portfolio import Portfolio, PortfolioSnapshot

    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        return None

    stock_symbols = [h.symbol for h in portfolio.holdings if h.symbol != "CASH"]
    if not stock_symbols:
        return portfolio.total_value

    quotes = await _fetch_quotes_batch(stock_symbols, settings.finnhub_api_key or "")

    total_stocks_value = 0.0
    cash_value = 0.0

    for holding in portfolio.holdings:
        if holding.symbol == "CASH":
            cash_value = holding.market_value
            continue
        q = quotes.get(holding.symbol)
        if q and q.get("c", 0) > 0:
            new_price = float(q["c"])
            holding.current_price = new_price
            holding.market_value = round(new_price * holding.quantity, 2)
        total_stocks_value += holding.market_value

    new_total = total_stocks_value + cash_value
    portfolio.total_value = round(new_total, 2)

    # Write snapshot
    snapshot = PortfolioSnapshot(
        portfolio_id=portfolio.id,
        total_value=new_total,
        cash_value=cash_value,
        stocks_value=total_stocks_value,
    )
    db.add(snapshot)

    await db.commit()
    logger.debug("Updated portfolio {} prices → total_value={:.2f}", portfolio.id, new_total)
    return new_total


async def update_all_portfolios(db_factory) -> None:
    """
    Called periodically by background task.
    Refreshes prices for all portfolios.
    """
    from app.models.portfolio import Portfolio

    async with db_factory() as db:
        result = await db.execute(select(Portfolio.id))
        ids = [row[0] for row in result.fetchall()]

    for pid in ids:
        try:
            async with db_factory() as db:
                await update_portfolio_prices(db, pid)
        except Exception as exc:
            logger.error("Error updating portfolio {}: {}", pid, exc)
        await asyncio.sleep(0.5)   # small delay between portfolios


async def get_portfolio_chart_data(db: AsyncSession, portfolio_id: int) -> List[dict]:
    """
    Return time-series data for portfolio chart.
    Each entry: {date, value}.
    """
    from app.models.portfolio import PortfolioSnapshot, Portfolio

    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        return []

    snap_result = await db.execute(
        select(PortfolioSnapshot)
        .where(PortfolioSnapshot.portfolio_id == portfolio_id)
        .order_by(PortfolioSnapshot.created_at)
    )
    snapshots = snap_result.scalars().all()

    if not snapshots:
        # Return just creation and current values
        return [
            {
                "date": portfolio.created_at.strftime("%Y-%m-%d %H:%M"),
                "value": portfolio.invested_amount,
            },
            {
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                "value": portfolio.total_value,
            },
        ]

    return [
        {
            "date": s.created_at.strftime("%Y-%m-%d %H:%M"),
            "value": round(s.total_value, 2),
        }
        for s in snapshots
    ]
