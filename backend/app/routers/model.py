"""
Model management endpoints — trigger DL training, check status.
"""

import asyncio
from fastapi import APIRouter, BackgroundTasks
from loguru import logger

router = APIRouter()

# Global training status
_TRAINING_STATUS = {"status": "idle", "progress": "", "results": None}


async def _run_training():
    """Background coroutine: collect AV data → train TFT + LSTM + N-BEATS."""
    global _TRAINING_STATUS
    _TRAINING_STATUS = {"status": "running", "progress": "Collecting Alpha Vantage data…", "results": None}
    try:
        from app.core.config import get_settings
        from app.engines.dl_engine.data_pipeline import collect_training_data, TRAINING_UNIVERSE
        from app.engines.dl_engine.trainer import train_all_models
        from app.engines.dl_engine.predictor import _init_models

        cfg = get_settings()
        if not cfg.alpha_vantage_api_key:
            _TRAINING_STATUS = {"status": "error", "progress": "ALPHA_VANTAGE_API_KEY not configured", "results": None}
            return

        _TRAINING_STATUS["progress"] = f"Downloading data for {len(TRAINING_UNIVERSE)} stocks (may take ~6 min due to AV rate limits)…"
        X, y = await collect_training_data(cfg.alpha_vantage_api_key)

        _TRAINING_STATUS["progress"] = f"Training TFT, LSTM-Attention, N-BEATS on {len(X)} sequences…"
        results = train_all_models(X, y, epochs=100)

        # Reload models into predictor singleton
        _init_models()

        _TRAINING_STATUS = {
            "status": "complete",
            "progress": f"Training done — {len(X)} sequences, {len(TRAINING_UNIVERSE)} stocks",
            "results": results,
        }
        logger.info("DL model training complete: {}", results)

    except Exception as exc:
        logger.error("DL training failed: {}", exc)
        _TRAINING_STATUS = {"status": "error", "progress": str(exc), "results": None}


@router.post("/train-model")
async def trigger_training(background_tasks: BackgroundTasks):
    """
    Trigger DL model training in the background.

    Downloads historical OHLCV from Alpha Vantage for 25 stocks,
    computes 11 technical features, then trains:
      - Temporal Fusion Transformer (TFT)
      - LSTM with Multi-Head Attention
      - N-BEATS

    Due to Alpha Vantage rate limits (5 req/min), data collection takes ~6 min.
    Training itself takes ~5-10 min on CPU.

    Poll /api/model/status to check progress.
    """
    if _TRAINING_STATUS["status"] == "running":
        return {"status": "already_running", "progress": _TRAINING_STATUS["progress"]}

    background_tasks.add_task(asyncio.run, _run_training())
    return {
        "status": "started",
        "message": (
            "DL model training started in background. "
            "TFT + LSTM + N-BEATS will be trained on 25 stocks × 100 days. "
            "Expected time: ~15 min. Poll /api/model/status for progress."
        ),
    }


@router.get("/status")
async def training_status():
    """Check current DL training status."""
    from app.engines.dl_engine.trainer import models_trained
    return {
        **_TRAINING_STATUS,
        "models_on_disk": models_trained(),
    }


@router.get("/info")
async def model_info():
    """Return information about the deployed DL models."""
    from app.engines.dl_engine.trainer import models_trained, _MODEL_PATHS
    from app.engines.dl_engine.predictor import get_dl_predictor
    predictor = get_dl_predictor()
    info = []
    for name, path in _MODEL_PATHS.items():
        size_kb = round(path.stat().st_size / 1024, 1) if path.exists() else 0
        info.append({"model": name, "trained": path.exists(), "size_kb": size_kb})
    return {
        "dl_ready": predictor.is_dl_ready,
        "models": info,
        "architecture": {
            "tft": "Temporal Fusion Transformer — Variable Selection + LSTM + Temporal Self-Attention (Lim et al. 2021)",
            "lstm": "BiLSTM with Multi-Head Self-Attention",
            "nbeats": "Neural Basis Expansion Analysis (Oreshkin et al. 2020)",
            "ensemble": "Learned-weight mixture of TFT (50%) + LSTM (35%) + N-BEATS (15%)",
        },
        "features": [
            "daily_return", "volume_change", "rsi_14", "macd_signal",
            "sma20_ratio", "sma50_ratio", "bb_position", "high_low_range",
            "momentum_5d", "volatility_10d", "atr_ratio",
        ],
        "input_seq_len": 20,
        "prediction_horizon": "5-day forward return",
    }


@router.post("/rebalance")
async def rebalance_portfolio(portfolio: dict):
    target_alloc  = portfolio.get("target_allocations", {"SPY": 0.5, "QQQ": 0.5})
    current_alloc = portfolio.get("allocations", {})
    suggestions = [
        {"asset": a, "action": "BUY" if current_alloc.get(a, 0) < t else "SELL",
         "drift": round(abs(current_alloc.get(a, 0) - t), 4)}
        for a, t in target_alloc.items()
        if abs(current_alloc.get(a, 0) - t) > 0.05
    ]
    return {"suggestions": suggestions}
