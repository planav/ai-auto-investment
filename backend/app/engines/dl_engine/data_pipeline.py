"""
Data Pipeline for DL Model Training — Polygon.io powered

Uses Polygon.io (no daily limit, 5 req/min free tier) for historical daily OHLCV.
Falls back to Alpha Vantage if Polygon unavailable.

Training universe: 200+ diverse US-listed stocks across all major sectors.
With 300+ days per stock and a 20-day sliding window:
  200 stocks × ~280 sequences = ~56,000 training sequences

Features (11-dimensional per timestep):
  0  daily_return    — log(close_t / close_{t-1})
  1  volume_change   — log(volume_t / volume_{t-1})
  2  rsi_14          — RSI(14) normalised to [-1, +1]
  3  macd_signal     — MACD histogram / price
  4  sma20_ratio     — close / SMA(20) - 1
  5  sma50_ratio     — close / SMA(50) - 1
  6  bb_position     — Bollinger Band position normalised
  7  high_low_range  — (high - low) / close
  8  momentum_5d     — close / close_{t-5} - 1
  9  volatility_10d  — rolling 10-day std of returns
  10 atr_ratio       — ATR(14) / close
"""

from __future__ import annotations
import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
from loguru import logger

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import httpx

_CACHE_DIR = Path(__file__).parent.parent.parent.parent.parent / "data" / "stock_cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

SEQ_LEN    = 20
HORIZON    = 5
N_FEATURES = 11

# ---------------------------------------------------------------------------
# Training Universe — 200+ diverse US stocks across all sectors
# ---------------------------------------------------------------------------

TRAINING_UNIVERSE = [
    # ── AI / Semiconductors (25) ─────────────────────────────────────────
    "NVDA", "AMD", "ARM", "SMCI", "MRVL", "AVGO", "MU", "ON", "LRCX",
    "KLAC", "AMAT", "ASML", "QCOM", "TXN", "INTC", "MPWR", "WOLF",
    "SWKS", "MTSI", "CRUS", "SIMO", "DIOD", "ACLS", "ALGM", "COHU",

    # ── Cloud / SaaS / AI Software (25) ──────────────────────────────────
    "MSFT", "GOOGL", "META", "AAPL", "AMZN", "ORCL", "CRM", "NOW",
    "ADBE", "INTU", "WDAY", "HUBS", "BILL", "MNDY", "DDOG", "SNOW",
    "MDB", "CRWD", "PANW", "NET", "ZS", "OKTA", "S", "CFLT", "GTLB",

    # ── AI / Disruptive Tech (15) ─────────────────────────────────────────
    "PLTR", "AI", "PATH", "SOUN", "BBAI", "RBLX", "U", "TTD", "MGNI",
    "AXON", "TMDX", "DUOL", "NTRA", "RXRX", "HIMS",

    # ── Consumer Discretionary (20) ───────────────────────────────────────
    "TSLA", "RIVN", "LCID", "MELI", "ABNB", "DASH", "UBER", "LYFT",
    "NFLX", "DIS", "CMCSA", "RBLX", "CHWY", "W", "ETSY", "PTON",
    "SNAP", "PINS", "SPOT", "MTCH",

    # ── Finance / Fintech / Crypto (20) ──────────────────────────────────
    "JPM", "GS", "MS", "BAC", "V", "MA", "AXP", "BLK",
    "COIN", "MARA", "MSTR", "RIOT", "SQ", "SOFI", "AFRM", "UPST",
    "HOOD", "PYPL", "FIS", "WEX",

    # ── Healthcare / Biotech (20) ─────────────────────────────────────────
    "UNH", "LLY", "ABBV", "JNJ", "MRK", "PFE", "TMO", "ABT",
    "ISRG", "AMGN", "GILD", "REGN", "VRTX", "MRNA", "BNTX",
    "CRSP", "BEAM", "EDIT", "NTLA", "RXRX",

    # ── Energy (15) ───────────────────────────────────────────────────────
    "XOM", "CVX", "COP", "EOG", "MPC", "VLO", "SLB", "OXY",
    "ENPH", "SEDG", "PLUG", "BE", "FSLR", "RUN", "BLNK",

    # ── Industrials (15) ──────────────────────────────────────────────────
    "BA", "CAT", "HON", "DE", "LMT", "RTX", "NOC", "UPS",
    "FDX", "MMM", "EMR", "ETN", "ROK", "ITW", "CARR",

    # ── Consumer Staples / Defensive (15) ────────────────────────────────
    "WMT", "COST", "KO", "PEP", "PG", "MCD", "SBUX", "NKE",
    "HD", "TGT", "MNST", "CHD", "CL", "KMB", "GIS",

    # ── Materials / Commodities (10) ──────────────────────────────────────
    "LIN", "APD", "SHW", "FCX", "NEM", "AA", "CF", "MOS", "ALB", "BALL",

    # ── REITs / Real Estate (10) ──────────────────────────────────────────
    "PLD", "AMT", "CCI", "EQIX", "SPG", "AVB", "O", "WELL", "ARE", "BXP",

    # ── Broad ETFs (15) ───────────────────────────────────────────────────
    "SPY", "QQQ", "IWM", "VTI", "GLD", "BND", "AGG",
    "XLK", "XLF", "XLV", "XLE", "XLU", "XLI", "XLY", "XLC",
]

# Deduplicate while preserving order
_seen = set()
TRAINING_UNIVERSE = [s for s in TRAINING_UNIVERSE if not (s in _seen or _seen.add(s))]

logger.info("Training universe: {} stocks", len(TRAINING_UNIVERSE))


# ---------------------------------------------------------------------------
# Polygon.io fetcher — primary data source (no daily call limit)
# ---------------------------------------------------------------------------

async def _fetch_polygon(
    symbol: str, api_key: str, client: httpx.AsyncClient,
    days_back: int = 400,
) -> Optional[List[dict]]:
    """
    Fetch daily OHLCV from Polygon.io aggregates endpoint.
    Returns list of dicts with keys: t (ms timestamp), o, h, l, c, v.
    """
    end_date   = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    try:
        r = await client.get(
            f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}",
            params={"adjusted": "true", "sort": "asc", "limit": 500, "apiKey": api_key},
            timeout=12,
        )
        data = r.json()
        if data.get("status") == "OK" and data.get("results"):
            return data["results"]
    except Exception as exc:
        logger.debug("Polygon fetch failed for {}: {}", symbol, exc)
    return None


async def _fetch_alpha_vantage(
    symbol: str, av_key: str, client: httpx.AsyncClient
) -> Optional[dict]:
    """Alpha Vantage fallback (100 days, 25/day limit)."""
    try:
        r = await client.get(
            "https://www.alphavantage.co/query",
            params={"function": "TIME_SERIES_DAILY", "symbol": symbol,
                    "outputsize": "compact", "apikey": av_key},
            timeout=12,
        )
        ts = r.json().get("Time Series (Daily)", {})
        return ts if ts else None
    except Exception:
        return None


def _polygon_to_ohlcv(results: List[dict]) -> Tuple[List[str], np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Convert Polygon results to sorted arrays."""
    # Sort by timestamp
    results = sorted(results, key=lambda x: x["t"])
    dates   = [datetime.fromtimestamp(r["t"] / 1000).strftime("%Y-%m-%d") for r in results]
    opens   = np.array([r["o"] for r in results], dtype=np.float64)
    highs   = np.array([r["h"] for r in results], dtype=np.float64)
    lows    = np.array([r["l"] for r in results], dtype=np.float64)
    closes  = np.array([r["c"] for r in results], dtype=np.float64)
    volumes = np.array([r["v"] for r in results], dtype=np.float64)
    return dates, opens, highs, lows, closes, volumes


def _av_to_ohlcv(ts: dict) -> Tuple[List[str], np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Convert Alpha Vantage time series to sorted arrays."""
    dates   = sorted(ts.keys())
    opens   = np.array([float(ts[d]["1. open"])   for d in dates])
    highs   = np.array([float(ts[d]["2. high"])   for d in dates])
    lows    = np.array([float(ts[d]["3. low"])    for d in dates])
    closes  = np.array([float(ts[d]["4. close"])  for d in dates])
    volumes = np.array([float(ts[d]["5. volume"]) for d in dates])
    return dates, opens, highs, lows, closes, volumes


# ---------------------------------------------------------------------------
# Feature computation
# ---------------------------------------------------------------------------

def _compute_features(
    opens: np.ndarray, highs: np.ndarray, lows: np.ndarray,
    closes: np.ndarray, volumes: np.ndarray,
) -> Optional[np.ndarray]:
    """Build (T, 11) feature matrix from OHLCV arrays."""
    T = len(closes)
    if T < SEQ_LEN + HORIZON + 15:
        return None

    # 1. Daily return (log)
    daily_ret = np.zeros(T)
    daily_ret[1:] = np.log(closes[1:] / (closes[:-1] + 1e-9))

    # 2. Volume change (log)
    vol_chg = np.zeros(T)
    vol_chg[1:] = np.log(volumes[1:] / (volumes[:-1] + 1e-9))

    # 3. RSI-14 normalised to [-1, +1]
    delta = np.diff(closes, prepend=closes[0])
    gain  = np.where(delta > 0, delta, 0.0)
    loss  = np.where(delta < 0, -delta, 0.0)
    rsi   = np.zeros(T)
    for i in range(14, T):
        ag = gain[i-13:i+1].mean()
        al = loss[i-13:i+1].mean()
        r  = ag / (al + 1e-9)
        rsi[i] = ((100 - 100 / (1 + r)) - 50) / 50

    # 4. MACD histogram (price-normalised)
    def ema(arr, span):
        k, out = 2/(span+1), np.zeros_like(arr)
        out[0] = arr[0]
        for i in range(1, len(arr)):
            out[i] = arr[i]*k + out[i-1]*(1-k)
        return out
    macd = (ema(closes, 12) - ema(closes, 26)) / (closes + 1e-9)

    # 5-6. SMA ratios
    sma20 = np.convolve(closes, np.ones(20)/20, "same")
    sma50 = np.convolve(closes, np.ones(50)/50, "same")
    sma20_r = closes/(sma20+1e-9) - 1
    sma50_r = closes/(sma50+1e-9) - 1

    # 7. Bollinger Band position
    bb_pos = np.zeros(T)
    for i in range(20, T):
        win = closes[i-20:i]
        m, s = win.mean(), win.std() + 1e-9
        bb_pos[i] = (closes[i] - (m-2*s)) / (4*s) - 0.5

    # 8. High-low range
    hl_range = (highs - lows) / (closes + 1e-9)

    # 9. 5-day momentum
    mom5 = np.zeros(T)
    mom5[5:] = closes[5:] / (closes[:-5] + 1e-9) - 1

    # 10. 10-day rolling volatility
    vol10 = np.zeros(T)
    for i in range(10, T):
        vol10[i] = daily_ret[i-10:i].std()

    # 11. ATR / close
    tr = np.maximum(highs-lows, np.maximum(
        np.abs(highs - np.roll(closes,1)),
        np.abs(lows  - np.roll(closes,1))
    ))
    atr = np.convolve(tr, np.ones(14)/14, "same")
    atr_r = atr / (closes + 1e-9)

    features = np.column_stack([
        daily_ret, vol_chg, rsi, macd, sma20_r, sma50_r,
        bb_pos, hl_range, mom5, vol10, atr_r,
    ])
    return np.clip(features, -3.0, 3.0)


def _build_sequences(features: np.ndarray, closes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Sliding window → (X, y) pairs."""
    T = len(features)
    X, y = [], []
    for i in range(SEQ_LEN, T - HORIZON):
        X.append(features[i-SEQ_LEN:i])
        fwd = np.log(closes[i+HORIZON] / (closes[i]+1e-9))
        y.append(np.clip(fwd, -0.30, 0.30))
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32).reshape(-1,1)


# ---------------------------------------------------------------------------
# Main collection function
# ---------------------------------------------------------------------------

async def collect_training_data(
    polygon_key: str = None,
    av_key: str = None,
    symbols: List[str] = None,
    days_back: int = 400,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Download historical data for all training symbols and return (X, y) tensors.

    Strategy:
      1. Check disk cache (24h TTL — Polygon data)
      2. If not cached: fetch from Polygon.io (primary, no daily limit)
      3. If Polygon fails: try Alpha Vantage (fallback, 25/day limit)
      4. Rate limit: 5 requests/minute → batches of 5 with 12s sleep between
    """
    if symbols is None:
        symbols = TRAINING_UNIVERSE

    total = len(symbols)
    logger.info("Starting data collection for {} stocks (primary=Polygon.io)…", total)

    all_X, all_y = [], []
    success_count = 0

    async with httpx.AsyncClient(timeout=15) as client:
        for batch_start in range(0, total, 5):
            batch = symbols[batch_start : batch_start + 5]
            batch_num = batch_start // 5 + 1
            total_batches = (total + 4) // 5
            logger.info("Batch {}/{}: {}", batch_num, total_batches, batch)

            # Run 5 fetches concurrently
            tasks = [_fetch_one(sym, polygon_key, av_key, client, days_back) for sym in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for sym, res in zip(batch, results):
                if isinstance(res, Exception) or res is None:
                    logger.debug("  {} → skip (no data)", sym)
                    continue
                X, y = res
                if len(X) > 0:
                    all_X.append(X)
                    all_y.append(y)
                    success_count += 1
                    logger.info("  {} → {} sequences ✓", sym, len(X))

            # Rate-limit: stay within 5 req/min
            if batch_start + 5 < total:
                await asyncio.sleep(12)   # 5 per minute = 12s between batches

    if not all_X:
        raise RuntimeError("No training data collected. Check API keys.")

    X_all = torch.tensor(np.concatenate(all_X, axis=0))
    y_all = torch.tensor(np.concatenate(all_y, axis=0))
    logger.info(
        "Collection complete: {}/{} stocks → {} total sequences",
        success_count, total, len(X_all)
    )
    return X_all, y_all


async def _fetch_one(
    symbol: str, polygon_key: str, av_key: str,
    client: httpx.AsyncClient, days_back: int,
) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """Fetch, cache, and featurize one stock. Returns (X, y) or None."""
    cache_path = _CACHE_DIR / f"{symbol}_polygon.json"

    # Check cache (24h TTL)
    raw = None
    if cache_path.exists():
        age_h = (datetime.now().timestamp() - cache_path.stat().st_mtime) / 3600
        if age_h < 24:
            with open(cache_path) as f:
                raw = json.load(f)

    # Fetch if not cached
    if raw is None:
        if polygon_key:
            raw = await _fetch_polygon(symbol, polygon_key, client, days_back)
            if raw:
                with open(cache_path, "w") as f:
                    json.dump(raw, f)
        if raw is None and av_key:
            # AV fallback — save in AV-format cache
            av_cache = _CACHE_DIR / f"{symbol}.json"
            av_data = await _fetch_alpha_vantage(symbol, av_key, client)
            if av_data:
                with open(av_cache, "w") as f:
                    json.dump(av_data, f)
                # Convert AV format to list of dicts for unified processing
                dates, opens, highs, lows, closes, volumes = _av_to_ohlcv(av_data)
                raw = [{"t": 0, "o": opens[i], "h": highs[i], "l": lows[i],
                         "c": closes[i], "v": volumes[i]} for i in range(len(dates))]

    if not raw or len(raw) < SEQ_LEN + HORIZON + 15:
        return None

    # Determine if it's Polygon format (has 't' timestamp) or raw arrays
    if isinstance(raw[0], dict) and "t" in raw[0] and raw[0]["t"] > 1e6:
        _, opens, highs, lows, closes, volumes = _polygon_to_ohlcv(raw)
    else:
        opens   = np.array([r.get("o", 0) for r in raw])
        highs   = np.array([r.get("h", 0) for r in raw])
        lows    = np.array([r.get("l", 0) for r in raw])
        closes  = np.array([r.get("c", 0) for r in raw])
        volumes = np.array([r.get("v", 1) for r in raw])

    features = _compute_features(opens, highs, lows, closes, volumes)
    if features is None:
        return None

    return _build_sequences(features, closes)


# ---------------------------------------------------------------------------
# Inference — build features for a single live stock
# ---------------------------------------------------------------------------

async def build_live_features(symbol: str, polygon_key: str = None, av_key: str = None) -> Optional[torch.Tensor]:
    """Build (1, SEQ_LEN, N_FEATURES) tensor for live inference."""
    async with httpx.AsyncClient(timeout=12) as client:
        result = await _fetch_one(symbol, polygon_key, av_key, client, days_back=60)
    if result is None:
        return None
    X, _ = result
    if len(X) == 0:
        return None
    # Return the LAST sequence (most recent 20-day window)
    return torch.tensor(X[-1]).unsqueeze(0)   # (1, 20, 11)
