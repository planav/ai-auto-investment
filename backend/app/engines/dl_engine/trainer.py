"""
Training Pipeline for DL Models

Trains TFT, LSTM-Attention, and N-BEATS on historical Alpha Vantage data.
Saves best model weights. Supports early stopping and learning rate scheduling.
"""

from __future__ import annotations
import time
from pathlib import Path
from typing import Optional, Tuple, Dict

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split
from loguru import logger

from app.engines.dl_engine.models import (
    TemporalFusionTransformer,
    LSTMAttention,
    NBEATS,
    DLEnsemble,
)
from app.engines.dl_engine.data_pipeline import SEQ_LEN, N_FEATURES

_MODEL_DIR = Path(__file__).parent / "saved_models"
_MODEL_DIR.mkdir(parents=True, exist_ok=True)

_MODEL_PATHS = {
    "tft":      _MODEL_DIR / "tft.pt",
    "lstm":     _MODEL_DIR / "lstm_attention.pt",
    "nbeats":   _MODEL_DIR / "nbeats.pt",
    "ensemble": _MODEL_DIR / "ensemble.pt",
}


def _build_models() -> Dict[str, nn.Module]:
    flat_size = SEQ_LEN * N_FEATURES
    return {
        "tft":    TemporalFusionTransformer(N_FEATURES, SEQ_LEN, hidden_size=64, num_heads=4, dropout=0.1),
        "lstm":   LSTMAttention(N_FEATURES, hidden_size=128, num_layers=2, num_heads=4, dropout=0.2),
        "nbeats": NBEATS(flat_size, hidden_size=256, n_blocks=4, n_layers=4, dropout=0.1),
    }


def _train_model(
    model: nn.Module,
    X_train: torch.Tensor,
    y_train: torch.Tensor,
    X_val: torch.Tensor,
    y_val: torch.Tensor,
    epochs: int = 100,
    batch_size: int = 64,
    lr: float = 1e-3,
    patience: int = 15,
    model_name: str = "model",
) -> Tuple[nn.Module, float]:
    """
    Train a single model with early stopping + cosine LR schedule.
    Returns the best-validation-loss model and its val loss.
    """
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.HuberLoss(delta=0.05)   # robust to outlier returns

    train_ds = TensorDataset(X_train, y_train)
    loader   = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    best_val_loss = float("inf")
    best_state    = None
    patience_cnt  = 0

    for epoch in range(1, epochs + 1):
        # ── Train ────────────────────────────────────────────────────────
        model.train()
        train_loss = 0.0
        for xb, yb in loader:
            optimizer.zero_grad()
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item() * len(xb)
        train_loss /= len(X_train)

        # ── Validate ─────────────────────────────────────────────────────
        model.eval()
        with torch.no_grad():
            val_pred = model(X_val)
            val_loss = criterion(val_pred, y_val).item()

        scheduler.step()

        if epoch % 10 == 0 or epoch == 1:
            logger.info(
                "  [{}] epoch {:3d}/{} | train_loss={:.5f} | val_loss={:.5f}",
                model_name, epoch, epochs, train_loss, val_loss,
            )

        # Early stopping
        if val_loss < best_val_loss - 1e-6:
            best_val_loss = val_loss
            best_state    = {k: v.clone() for k, v in model.state_dict().items()}
            patience_cnt  = 0
        else:
            patience_cnt += 1
            if patience_cnt >= patience:
                logger.info("  Early stopping at epoch {} (patience={})", epoch, patience)
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    return model, best_val_loss


def train_all_models(
    X: torch.Tensor,
    y: torch.Tensor,
    epochs: int = 100,
    val_split: float = 0.15,
    batch_size: int = 64,
) -> Dict[str, float]:
    """
    Train TFT, LSTM-Attention, N-BEATS individually then train ensemble.
    Returns dict of {model_name: best_val_loss}.
    """
    logger.info("Starting DL model training — {} sequences, {} features", len(X), N_FEATURES)
    t0 = time.time()

    # Train/val split
    n_val   = int(len(X) * val_split)
    n_train = len(X) - n_val
    # Use chronological split (no shuffle — preserves time order)
    X_train, X_val = X[:n_train], X[n_train:]
    y_train, y_val = y[:n_train], y[n_train:]
    logger.info("Train: {} | Val: {}", n_train, n_val)

    models   = _build_models()
    results  = {}

    for name, model in models.items():
        logger.info("Training {} …", name.upper())
        trained_model, val_loss = _train_model(
            model, X_train, y_train, X_val, y_val,
            epochs=epochs, batch_size=batch_size, model_name=name,
        )
        torch.save(trained_model.state_dict(), _MODEL_PATHS[name])
        results[name] = round(val_loss, 6)
        logger.info("  {} saved — val_loss={:.5f}", name.upper(), val_loss)

    # Train ensemble (all parameters jointly)
    logger.info("Training DL Ensemble (TFT + LSTM + N-BEATS)…")
    ensemble = DLEnsemble(N_FEATURES, SEQ_LEN)
    # Load pre-trained weights into sub-models
    ensemble.tft.load_state_dict(torch.load(_MODEL_PATHS["tft"], weights_only=True))
    ensemble.lstm.load_state_dict(torch.load(_MODEL_PATHS["lstm"], weights_only=True))
    ensemble.nbeats.load_state_dict(torch.load(_MODEL_PATHS["nbeats"], weights_only=True))

    # Fine-tune mixing weights (freeze sub-model weights)
    for p in ensemble.tft.parameters():    p.requires_grad = False
    for p in ensemble.lstm.parameters():   p.requires_grad = False
    for p in ensemble.nbeats.parameters(): p.requires_grad = False

    ensemble_trained, ens_loss = _train_model(
        ensemble, X_train, y_train, X_val, y_val,
        epochs=30, batch_size=batch_size, lr=1e-3, patience=10, model_name="ensemble",
    )
    torch.save(ensemble_trained.state_dict(), _MODEL_PATHS["ensemble"])
    results["ensemble"] = round(ens_loss, 6)

    elapsed = time.time() - t0
    logger.info("All models trained in {:.1f}s | Results: {}", elapsed, results)
    return results


def models_trained() -> bool:
    """Return True if all model weights exist on disk."""
    return all(p.exists() for p in _MODEL_PATHS.values())


def load_ensemble() -> Optional[DLEnsemble]:
    """Load the trained DL ensemble from disk. Returns None if not trained."""
    if not models_trained():
        return None
    try:
        ensemble = DLEnsemble(N_FEATURES, SEQ_LEN)
        ensemble.load_state_dict(
            torch.load(_MODEL_PATHS["ensemble"], weights_only=True, map_location="cpu")
        )
        ensemble.eval()
        logger.info("DL Ensemble loaded from disk")
        return ensemble
    except Exception as exc:
        logger.error("Failed to load ensemble: {}", exc)
        return None


def load_individual_models() -> Dict[str, Optional[nn.Module]]:
    """Load all individual models. Returns dict, any can be None if not found."""
    loaded = {}
    flat_size = SEQ_LEN * N_FEATURES
    specs = {
        "tft":    TemporalFusionTransformer(N_FEATURES, SEQ_LEN, hidden_size=64),
        "lstm":   LSTMAttention(N_FEATURES, hidden_size=128, num_layers=2, num_heads=4),
        "nbeats": NBEATS(flat_size, hidden_size=256),
    }
    for name, model in specs.items():
        path = _MODEL_PATHS[name]
        if path.exists():
            try:
                model.load_state_dict(torch.load(path, weights_only=True, map_location="cpu"))
                model.eval()
                loaded[name] = model
            except Exception as exc:
                logger.warning("Could not load {}: {}", name, exc)
                loaded[name] = None
        else:
            loaded[name] = None
    return loaded
