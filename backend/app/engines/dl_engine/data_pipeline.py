"""
Data Pipeline for DL Model Training

Fetches historical OHLCV from Alpha Vantage, computes 11 technical features,
and prepares (X, y) tensors for model training.

Features per timestep (11-dimensional):
  0  daily_return    — log(close_t / close_{t-1})
  1  volume_change   — log(volume_t / volume_{t-1})
  2  rsi_14          — RSI(14) normalised to [-1, +1]
  3  macd_signal     — MACD histogram normalised
  4  sma20_ratio     — close / SMA(20) - 1
  5  sma50_ratio     — close / SMA(50) - 1
  6  bb_position     — (close - BB_lower) / (BB_upper - BB_lower) normalised
  7  high_low_range  — (high - low) / close
  8  momentum_5d     — close / close_{t-5} - 1
  9  volatility_10d  — rolling 10-day std of returns
  10 atr_ratio       — Average True Range / close (price-normalised)

Target:
  5-day forward cumulative log return (clipped to ±30%)
"""

from __future__ import annotations
import asyncio
import json
import os
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

# Cache directory for fetched price data
_CACHE_DIR = Path(__file__).parent.parent.parent.parent.parent / "data" / "stock_cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Training universe — 25 liquid, diverse US stocks (within Alpha Vantage daily limit)
TRAINING_UNIVERSE = [
    # Tech / AI
    "NVDA", "AMD", "MSFT", "GOOGL", "AAPL", "META", "AMZN", "AVGO",
    # Cybersecurity / Cloud
    "CRWD", "NET", "DDOG", "PANW",
    # Finance
    "JPM", "GS", "V", "MA",
    # Healthcare
    "JNJ", "ABBV", "UNH",
    # Consumer
    "WMT", "KO", "HD",
    # Aggressive / Growth
    "TSLA", "PLTR", "COIN",
]

SEQ_LEN   = 20   # 20-day window as model input
HORIZON   = 5    # predict 5-day forward return
N_FEATURES = 11


# ---------------------------------------------------------------------------
# Alpha Vantage fetcher
# ---------------------------------------------------------------------------

async def fetch_av_daily(symbol: str, av_key: str) -> Optional[dict]:
    """Fetch daily OHLCV from Alpha Vantage (compact = last 100 trading days)."""
    cache_path = _CACHE_DIR / f"{symbol}.json"

    # Use cache if < 12h old
    if cache_path.exists():
        age_h = (Path.stat(cache_path).st_mtime - os.path.getmtime(cache_path)) / 3600
        if age_h < 12:
            with open(cache_path) as f:
                return json.load(f)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                "https://www.alphavantage.co/query",
                params={"function": "TIME_SERIES_DAILY", "symbol": symbol,
                        "outputsize": "compact", "apikey": av_key},
            )
        data = r.json()
        ts = data.get("Time Series (Daily)", {})
        if not ts:
            logger.warning("No AV data for {}: {}", symbol, list(data.keys()))
            return None
        with open(cache_path, "w") as f:
            json.dump(ts, f)
        return ts
    except Exception as exc:
        logger.error("AV fetch failed for {}: {}", symbol, exc)
        return None


def _compute_features(dates: List[str], ts: dict) -> Optional[np.ndarray]:
    """
    Build (T, 11) feature matrix from AV time-series dict.
    Returns None if insufficient data.
    """
    if len(dates) < SEQ_LEN + HORIZON + 10:
        return None

    closes  = np.array([float(ts[d]["4. close"])  for d in dates])
    highs   = np.array([float(ts[d]["2. high"])   for d in dates])
    lows    = np.array([float(ts[d]["3. low"])    for d in dates])
    volumes = np.array([float(ts[d]["5. volume"]) for d in dates])
    opens   = np.array([float(ts[d]["1. open"])   for d in dates])

    T = len(closes)

    # Daily return (log)
    daily_ret = np.zeros(T)
    daily_ret[1:] = np.log(closes[1:] / (closes[:-1] + 1e-9))

    # Volume change (log)
    vol_chg = np.zeros(T)
    vol_chg[1:] = np.log(volumes[1:] / (volumes[:-1] + 1e-9))

    # RSI 14
    delta = np.diff(closes, prepend=closes[0])
    gain  = np.where(delta > 0, delta, 0.0)
    loss  = np.where(delta < 0, -delta, 0.0)
    rsi   = np.zeros(T)
    for i in range(14, T):
        avg_g = gain[i-13:i+1].mean()
        avg_l = loss[i-13:i+1].mean()
        rsi[i] = (avg_g / (avg_l + 1e-9)) if avg_l > 0 else 100.0
        rsi[i] = (rsi[i] - 50) / 50       # normalise to [-1, +1]

    # MACD histogram (12-day EMA - 26-day EMA)
    def ema(arr, span):
        k = 2 / (span + 1)
        out = np.zeros_like(arr)
        out[0] = arr[0]
        for i in range(1, len(arr)):
            out[i] = arr[i] * k + out[i-1] * (1 - k)
        return out
    macd_hist = ema(closes, 12) - ema(closes, 26)
    macd_hist /= (closes + 1e-9)   # price-normalise

    # SMA ratios
    sma20 = np.convolve(closes, np.ones(20)/20, mode="same")
    sma50 = np.convolve(closes, np.ones(50)/50, mode="same")
    sma20_ratio = closes / (sma20 + 1e-9) - 1
    sma50_ratio = closes / (sma50 + 1e-9) - 1

    # Bollinger Band position (20-day, 2σ)
    bb_pos = np.zeros(T)
    for i in range(20, T):
        win = closes[i-20:i]
        m, s = win.mean(), win.std() + 1e-9
        upper, lower = m + 2*s, m - 2*s
        bb_pos[i] = (closes[i] - lower) / (upper - lower + 1e-9) - 0.5  # center at 0

    # High-low range
    hl_range = (highs - lows) / (closes + 1e-9)

    # 5-day momentum
    mom5 = np.zeros(T)
    mom5[5:] = closes[5:] / (closes[:-5] + 1e-9) - 1

    # 10-day rolling volatility
    vol10 = np.zeros(T)
    for i in range(10, T):
        vol10[i] = daily_ret[i-10:i].std()

    # Average True Range / close
    tr = np.maximum(
        highs - lows,
        np.maximum(np.abs(highs - np.roll(closes, 1)),
                   np.abs(lows  - np.roll(closes, 1)))
    )
    atr = np.convolve(tr, np.ones(14)/14, mode="same")
    atr_ratio = atr / (closes + 1e-9)

    features = np.column_stack([
        daily_ret, vol_chg, rsi, macd_hist, sma20_ratio, sma50_ratio,
        bb_pos, hl_range, mom5, vol10, atr_ratio,
    ])
    return np.clip(features, -3.0, 3.0)   # clip outliers


def _build_sequences(features: np.ndarray, closes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Slide a window of SEQ_LEN over the feature matrix to build (X, y) pairs.
    y = 5-day forward log return (clipped to ±30%).
    """
    T   = len(features)
    X, y = [], []
    for i in range(SEQ_LEN, T - HORIZON):
        X.append(features[i - SEQ_LEN : i])           # (SEQ_LEN, F)
        fwd = np.log(closes[i + HORIZON] / (closes[i] + 1e-9))
        y.append(np.clip(fwd, -0.30, 0.30))
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32).reshape(-1, 1)


# ---------------------------------------------------------------------------
# Main data collection function
# ---------------------------------------------------------------------------

async def collect_training_data(av_key: str, symbols: List[str] = None) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Fetch + process data for all symbols, combine into single (X, y) dataset.
    Returns tensors ready for training.
    """
    if symbols is None:
        symbols = TRAINING_UNIVERSE

    logger.info("Collecting training data for {} symbols (Alpha Vantage)…", len(symbols))

    all_X, all_y = [], []

    # Fetch sequentially (rate limit: 5/min → 12s apart)
    for i, sym in enumerate(symbols):
        if i > 0 and i % 5 == 0:
            logger.info("Rate-limit pause between AV requests…")
            await asyncio.sleep(61)

        ts = await fetch_av_daily(sym, av_key)
        if ts is None:
            continue

        # Sort dates ascending
        dates = sorted(ts.keys())
        closes = np.array([float(ts[d]["4. close"]) for d in dates])
        features = _compute_features(dates, ts)

        if features is None or len(features) < SEQ_LEN + HORIZON + 10:
            logger.warning("Skipping {} — insufficient data ({} rows)", sym, len(dates))
            continue

        X, y = _build_sequences(features, closes)
        all_X.append(X)
        all_y.append(y)
        logger.info("  {} → {} sequences", sym, len(X))

    if not all_X:
        raise RuntimeError("No training data collected. Check Alpha Vantage API key.")

    X_all = torch.tensor(np.concatenate(all_X, axis=0))
    y_all = torch.tensor(np.concatenate(all_y, axis=0))
    logger.info("Total training sequences: {} | X: {} | y: {}", len(X_all), X_all.shape, y_all.shape)
    return X_all, y_all


# ---------------------------------------------------------------------------
# Inference feature builder — for a single live stock
# ---------------------------------------------------------------------------

async def build_live_features(symbol: str, av_key: str) -> Optional[torch.Tensor]:
    """
    Build a single (1, SEQ_LEN, N_FEATURES) tensor for live inference.
    Uses cached AV data if fresh, otherwise fetches.
    """
    ts = await fetch_av_daily(symbol, av_key)
    if ts is None:
        return None

    dates = sorted(ts.keys())
    if len(dates) < SEQ_LEN + 10:
        return None

    closes   = np.array([float(ts[d]["4. close"]) for d in dates])
    features = _compute_features(dates, ts)
    if features is None:
        return None

    # Take the last SEQ_LEN rows as the current input window
    window = features[-SEQ_LEN:]                     # (SEQ_LEN, F)
    return torch.tensor(window, dtype=torch.float32).unsqueeze(0)  # (1, SEQ_LEN, F)
