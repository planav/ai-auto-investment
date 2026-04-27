"""
Layer 2: ML Scoring Engine
Real sklearn ensemble (RandomForest + GradientBoosting) that scores stocks
based on features derived from real Finnhub market data.

Training data: Initially seeded from known financial patterns.
Can be retrained via /api/model/train endpoint.
Persisted to disk with joblib.
"""

from __future__ import annotations
import os
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

from loguru import logger

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed — ML engine will use rule-based fallback")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_MODEL_DIR = Path(__file__).parent / "saved_models"
_MODEL_DIR.mkdir(parents=True, exist_ok=True)
_RF_PATH = _MODEL_DIR / "rf_momentum.joblib"
_GB_PATH = _MODEL_DIR / "gb_quality.joblib"
_SECTOR_MOMENTUM_PATH = _MODEL_DIR / "sector_momentum.json"

# ---------------------------------------------------------------------------
# Feature definition
# ---------------------------------------------------------------------------
# Features extracted from Finnhub quote + analyst data:
#   0  daily_change_pct     — today's % price change  (momentum proxy)
#   1  intraday_ratio       — close / open ratio       (intraday direction)
#   2  high_low_range       — (high-low)/prev_close    (daily volatility)
#   3  analyst_score        — normalized (strongBuy*2+buy-sell-strongSell*2) / total*2
#   4  analyst_coverage     — number of analysts covering
#   5  sector_momentum      — average daily_change_pct of sector peers
#   6  vol_estimate         — known annual volatility for this stock
#   7  price_level          — log10(current_price) for size proxy
FEATURE_NAMES = [
    "daily_change_pct", "intraday_ratio", "high_low_range",
    "analyst_score", "analyst_coverage", "sector_momentum",
    "vol_estimate", "price_level",
]


def _extract_features(
    quote: dict,
    rec: Optional[dict],
    sector_momentum: float,
    vol_estimate: float,
) -> np.ndarray:
    """
    Extract feature vector from Finnhub quote + recommendation data.
    Returns shape (1, 8).
    """
    c  = float(quote.get("c",  100) or 100)
    o  = float(quote.get("o",  c)   or c)
    h  = float(quote.get("h",  c)   or c)
    l  = float(quote.get("l",  c)   or c)
    pc = float(quote.get("pc", c)   or c)
    dp = float(quote.get("dp", 0)   or 0)

    intraday_ratio  = c / o if o > 0 else 1.0
    high_low_range  = (h - l) / pc if pc > 0 else 0.0
    price_level     = np.log10(max(c, 0.01))

    # Analyst score: normalised to [-1, +1]
    analyst_score    = 0.0
    analyst_coverage = 0.0
    if rec:
        sb = rec.get("strongBuy", 0)
        b  = rec.get("buy", 0)
        h_ = rec.get("hold", 0)
        s  = rec.get("sell", 0)
        ss = rec.get("strongSell", 0)
        total = sb + b + h_ + s + ss
        analyst_coverage = float(total)
        if total > 0:
            analyst_score = (sb*2 + b*1 + h_*0 + s*(-1) + ss*(-2)) / (total * 2)

    return np.array([[
        dp, intraday_ratio, high_low_range,
        analyst_score, analyst_coverage, sector_momentum,
        vol_estimate, price_level,
    ]])


# ---------------------------------------------------------------------------
# Seed training data — based on known financial patterns
# (In production, replace with real historical returns)
# ---------------------------------------------------------------------------

def _generate_seed_training_data(n: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training data with realistic financial patterns:
    - High momentum (dp > 2%) + positive analyst → positive 30d return
    - Negative momentum + sell analyst → negative 30d return
    - Neutral → near-zero return
    """
    rng = np.random.default_rng(42)

    features = []
    targets   = []

    for _ in range(n):
        dp              = rng.uniform(-6.0, 6.0)
        intraday_ratio  = rng.uniform(0.97, 1.03)
        high_low_range  = abs(rng.normal(0.02, 0.01))
        analyst_score   = rng.uniform(-1.0, 1.0)
        analyst_cov     = rng.uniform(5, 40)
        sector_mom      = rng.uniform(-3.0, 3.0)
        vol             = rng.uniform(0.15, 0.65)
        price_lvl       = rng.uniform(1.0, 3.5)

        # Target: 1-month forward return based on known patterns
        base_return = (
            dp            * 0.015   # momentum carries forward
          + analyst_score * 0.08    # analyst consensus is predictive
          + sector_mom    * 0.010   # sector tailwind
          + rng.normal(0, 0.04)     # noise
        )
        base_return = float(np.clip(base_return, -0.30, 0.35))

        features.append([dp, intraday_ratio, high_low_range, analyst_score,
                          analyst_cov, sector_mom, vol, price_lvl])
        targets.append(base_return)

    return np.array(features), np.array(targets)


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------

def train_models(X: Optional[np.ndarray] = None, y: Optional[np.ndarray] = None) -> bool:
    """
    Train the RF + GB ensemble and save to disk.
    If X/y not provided, uses synthetic seed data.
    """
    if not SKLEARN_AVAILABLE:
        logger.error("scikit-learn not available — cannot train ML models")
        return False

    if X is None or y is None:
        logger.info("Training ML models on synthetic seed data…")
        X, y = _generate_seed_training_data(n=3000)
    else:
        logger.info("Training ML models on {} real samples…", len(y))

    # RandomForest (captures non-linear momentum patterns)
    rf_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestRegressor(
            n_estimators=200, max_depth=8, min_samples_leaf=10,
            n_jobs=-1, random_state=42
        )),
    ])
    rf_pipeline.fit(X, y)
    joblib.dump(rf_pipeline, _RF_PATH)

    # GradientBoosting (captures sequential patterns better)
    gb_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("gb", GradientBoostingRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42
        )),
    ])
    gb_pipeline.fit(X, y)
    joblib.dump(gb_pipeline, _GB_PATH)

    logger.info("ML models trained and saved to {}", _MODEL_DIR)
    return True


def _load_models() -> Tuple[Optional[object], Optional[object]]:
    """Load persisted models or train fresh if not found."""
    rf = gb = None
    try:
        if _RF_PATH.exists():
            rf = joblib.load(_RF_PATH)
        if _GB_PATH.exists():
            gb = joblib.load(_GB_PATH)
    except Exception as exc:
        logger.warning("Failed to load saved models: {} — retraining", exc)

    if rf is None or gb is None:
        logger.info("No saved models found — training from seed data")
        train_models()
        try:
            rf = joblib.load(_RF_PATH)
            gb = joblib.load(_GB_PATH)
        except Exception as exc:
            logger.error("Model training/loading failed: {}", exc)

    return rf, gb


# Lazy-loaded model references
_RF_MODEL = None
_GB_MODEL = None

def _get_models():
    global _RF_MODEL, _GB_MODEL
    if _RF_MODEL is None:
        _RF_MODEL, _GB_MODEL = _load_models()
    return _RF_MODEL, _GB_MODEL


# ---------------------------------------------------------------------------
# Sector momentum calculation
# ---------------------------------------------------------------------------

def compute_sector_momentum(quotes_by_symbol: Dict[str, dict], sectors_by_symbol: Dict[str, str]) -> Dict[str, float]:
    """
    Compute average daily % change per sector from the quotes map.
    Returns {sector: avg_dp}.
    """
    sector_dps: Dict[str, List[float]] = {}
    for sym, q in quotes_by_symbol.items():
        sector = sectors_by_symbol.get(sym, "Other")
        dp = float(q.get("dp", 0) or 0)
        sector_dps.setdefault(sector, []).append(dp)

    return {sector: float(np.mean(dps)) for sector, dps in sector_dps.items()}


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def score_stocks(
    symbols: List[str],
    quotes: Dict[str, dict],
    recommendations: Dict[str, Optional[dict]],
    sector_momentum: Dict[str, float],
    vol_estimates: Dict[str, float],
    sectors: Dict[str, str],
) -> Dict[str, dict]:
    """
    Score and rank stocks using the ML ensemble.

    Returns {symbol: {ml_score, predicted_return, confidence, signal_strength}}.
    ml_score is normalized 0-100.
    """
    rf, gb = _get_models()

    results = {}
    raw_scores = []

    for sym in symbols:
        q = quotes.get(sym)
        if q is None or q.get("c", 0) <= 0:
            continue

        rec = recommendations.get(sym)
        sector = sectors.get(sym, "Other")
        sec_mom = sector_momentum.get(sector, 0.0)
        vol = vol_estimates.get(sym, 0.30)

        features = _extract_features(q, rec, sec_mom, vol)

        # Ensemble prediction
        if rf is not None and gb is not None:
            try:
                rf_pred = float(rf.predict(features)[0])
                gb_pred = float(gb.predict(features)[0])
                predicted_return = 0.55 * rf_pred + 0.45 * gb_pred
            except Exception:
                predicted_return = _rule_based_score(q, rec, sec_mom)
        else:
            predicted_return = _rule_based_score(q, rec, sec_mom)

        # Confidence from signal agreement
        dp = float(q.get("dp", 0) or 0)
        analyst_score = 0.0
        if rec:
            sb  = rec.get("strongBuy",  0)
            b   = rec.get("buy",        0)
            h_  = rec.get("hold",       0)
            s   = rec.get("sell",       0)
            ss  = rec.get("strongSell", 0)
            tot = sb + b + h_ + s + ss
            if tot:
                analyst_score = (sb*2 + b - s - ss*2) / (tot * 2)

        direction_agree = (dp > 0) == (analyst_score > 0)
        confidence = min(0.90, 0.55 + abs(predicted_return) * 1.5 + (0.10 if direction_agree else 0))

        raw_scores.append((sym, predicted_return))
        results[sym] = {
            "predicted_return": round(predicted_return, 4),
            "confidence": round(confidence, 4),
            "current_price": float(q.get("c", 0)),
            "daily_change_pct": float(q.get("dp", 0) or 0),
            "analyst_score": round(analyst_score, 4),
        }

    # Normalise to 0-100 ml_score
    if raw_scores:
        scores = np.array([v for _, v in raw_scores])
        min_s, max_s = scores.min(), scores.max()
        span = max_s - min_s if max_s > min_s else 1.0
        for sym, raw in raw_scores:
            ml_score = float((raw - min_s) / span * 100)
            results[sym]["ml_score"] = round(ml_score, 2)
            ret = results[sym]["predicted_return"]
            results[sym]["signal_strength"] = (
                "strong_buy"  if ret >= 0.12 else
                "buy"         if ret >= 0.04 else
                "hold"        if ret >= -0.04 else
                "sell"        if ret >= -0.12 else
                "strong_sell"
            )

    return results


def _rule_based_score(quote: dict, rec: Optional[dict], sector_mom: float) -> float:
    """Pure rule-based fallback when sklearn unavailable."""
    dp = float(quote.get("dp", 0) or 0)
    analyst = 0.0
    if rec:
        sb, b, s, ss = rec.get("strongBuy",0), rec.get("buy",0), rec.get("sell",0), rec.get("strongSell",0)
        tot = sb + b + rec.get("hold",0) + s + ss
        if tot:
            analyst = (sb*2 + b - s - ss*2) / (tot*2)
    return dp*0.015 + analyst*0.08 + sector_mom*0.010 + 0.05
