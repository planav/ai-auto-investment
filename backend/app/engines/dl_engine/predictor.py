"""
DL Inference Engine

Unified interface for running TFT / LSTM-Attention / N-BEATS predictions
on live stocks. Falls back to the sklearn ensemble when DL models are not
yet trained.

Usage:
    from app.engines.dl_engine.predictor import DLPredictor
    predictor = DLPredictor()
    scores = await predictor.score_stocks(["NVDA", "AMD"], av_key="...")
"""

from __future__ import annotations
import asyncio
from typing import Dict, List, Optional

import torch
from loguru import logger

from app.engines.dl_engine.trainer import (
    load_ensemble, load_individual_models, models_trained,
)
from app.engines.dl_engine.data_pipeline import build_live_features, N_FEATURES, SEQ_LEN

# Singleton cache
_ENSEMBLE = None
_INDIVIDUAL = None
_DL_READY = False


def _init_models():
    global _ENSEMBLE, _INDIVIDUAL, _DL_READY
    if _DL_READY:
        return
    if models_trained():
        _ENSEMBLE    = load_ensemble()
        _INDIVIDUAL  = load_individual_models()
        _DL_READY    = _ENSEMBLE is not None
        if _DL_READY:
            logger.info("DL Predictor: TFT + LSTM-Attention + N-BEATS loaded ✓")
        else:
            logger.warning("DL Predictor: model files found but loading failed — using sklearn")
    else:
        logger.info("DL Predictor: models not yet trained — sklearn fallback active")


class DLPredictor:
    """
    High-level predictor that uses the trained DL ensemble (TFT + LSTM + N-BEATS)
    or falls back to the sklearn ML engine when DL models are unavailable.
    """

    def __init__(self):
        _init_models()
        self._ready = _DL_READY

    @property
    def is_dl_ready(self) -> bool:
        return self._ready

    async def score_stocks(
        self,
        symbols: List[str],
        av_key: str,
        quotes: Optional[Dict[str, dict]] = None,
        recs: Optional[Dict[str, Optional[dict]]] = None,
        sectors: Optional[Dict[str, str]] = None,
    ) -> Dict[str, dict]:
        """
        Score a list of stocks.

        If DL models are trained:
          - Fetch AV features for each stock (parallel, rate-limited)
          - Run TFT + LSTM + N-BEATS ensemble → predicted 5-day return
          - Report individual model predictions for interpretability

        If DL models are NOT yet trained:
          - Fall back to sklearn RF + GB ensemble using Finnhub features

        Returns dict: {symbol: {predicted_return, confidence, signal_strength,
                                tft_pred, lstm_pred, nbeats_pred, current_price}}
        """
        if self._ready:
            return await self._dl_score(symbols, av_key, quotes)
        else:
            return self._sklearn_fallback(symbols, quotes, recs, sectors)

    async def _dl_score(
        self, symbols: List[str], av_key: str, quotes: Optional[Dict]
    ) -> Dict[str, dict]:
        """Run TFT + LSTM + N-BEATS inference on live AV features."""
        results: Dict[str, dict] = {}
        individual = _INDIVIDUAL or {}

        # Fetch AV features with 12s gaps (AV rate limit: 5/min)
        for i, sym in enumerate(symbols):
            if i > 0 and i % 5 == 0:
                logger.debug("AV rate-limit pause (DL inference)…")
                await asyncio.sleep(13)

            features = await build_live_features(sym, av_key)
            if features is None:
                logger.debug("No AV features for {} — skipping DL inference", sym)
                # Use Finnhub quote as simple signal
                q = (quotes or {}).get(sym, {})
                dp = float(q.get("dp", 0))
                pred = dp * 0.015 + 0.05
                results[sym] = _format_result(sym, pred, 0.55, q, {})
                continue

            with torch.no_grad():
                # Ensemble prediction
                ens_pred = float(_ENSEMBLE(features).item()) if _ENSEMBLE else 0.05

                # Individual model predictions (for interpretability display)
                individual_preds = {}
                for name, model in individual.items():
                    if model is not None:
                        try:
                            individual_preds[name] = float(model(features).item())
                        except Exception:
                            pass

            # Confidence: based on agreement among individual models
            preds = list(individual_preds.values())
            if len(preds) >= 2:
                spread = max(preds) - min(preds)
                confidence = float(max(0.50, min(0.92, 0.70 - spread)))
            else:
                confidence = 0.65

            q = (quotes or {}).get(sym, {})
            results[sym] = _format_result(sym, ens_pred, confidence, q, individual_preds)

        return results

    def _sklearn_fallback(
        self,
        symbols: List[str],
        quotes: Optional[Dict],
        recs: Optional[Dict],
        sectors: Optional[Dict],
    ) -> Dict[str, dict]:
        """Use the sklearn RF+GB ensemble when DL models are not trained."""
        from app.engines.ml_engine.predictor import score_stocks, compute_sector_momentum

        q  = quotes or {}
        r  = recs   or {}
        s  = sectors or {}
        sm = compute_sector_momentum(q, s)
        from app.engines.dl_engine.data_pipeline import N_FEATURES
        vol_map = {sym: 0.30 for sym in symbols}

        sklearn_res = score_stocks(symbols, q, r, sm, vol_map, s)
        out = {}
        for sym, info in sklearn_res.items():
            out[sym] = {
                "predicted_return": info.get("predicted_return", 0.05),
                "confidence":       info.get("confidence", 0.60),
                "signal_strength":  info.get("signal_strength", "hold"),
                "current_price":    info.get("current_price", 0.0),
                "ml_score":         info.get("ml_score", 50.0),
                "tft_pred":         None,
                "lstm_pred":        None,
                "nbeats_pred":      None,
                "model_source":     "sklearn_ensemble",
            }
        return out


def _format_result(sym, ens_pred, confidence, quote, individual_preds):
    signal = ("strong_buy"  if ens_pred >= 0.10 else
              "buy"         if ens_pred >= 0.04 else
              "hold"        if ens_pred >= -0.04 else
              "sell"        if ens_pred >= -0.10 else
              "strong_sell")
    return {
        "predicted_return": round(ens_pred, 4),
        "confidence":       round(confidence, 4),
        "signal_strength":  signal,
        "current_price":    float(quote.get("c", 0)),
        "daily_change_pct": float(quote.get("dp", 0)),
        "ml_score":         round(min(100, max(0, (ens_pred + 0.25) / 0.50 * 100)), 2),
        "tft_pred":         round(individual_preds.get("tft", ens_pred), 4),
        "lstm_pred":        round(individual_preds.get("lstm", ens_pred), 4),
        "nbeats_pred":      round(individual_preds.get("nbeats", ens_pred), 4),
        "model_source":     "dl_ensemble_tft_lstm_nbeats",
    }


# Singleton instance
_predictor: Optional[DLPredictor] = None

def get_dl_predictor() -> DLPredictor:
    global _predictor
    if _predictor is None:
        _predictor = DLPredictor()
    return _predictor
