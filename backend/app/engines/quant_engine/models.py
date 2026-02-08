from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class ModelType(str, Enum):
    """Available deep learning model types."""
    TEMPORAL_FUSION_TRANSFORMER = "temporal_fusion_transformer"
    LSTM_ATTENTION = "lstm_attention"
    PATCH_TST = "patch_tst"
    NBEATS = "nbeats"
    NHITS = "nhits"
    INFORMER = "informer"
    AUTOFORMER = "autoformer"
    GRAPH_ATTENTION = "graph_attention"
    STGNN = "stgnn"


@dataclass
class ModelConfig:
    """Configuration for a deep learning model."""
    model_type: ModelType
    input_sequence_length: int = 60  # Lookback window
    prediction_horizon: int = 5  # Days ahead
    hidden_size: int = 128
    num_layers: int = 2
    num_heads: int = 8
    dropout: float = 0.1
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    early_stopping_patience: int = 10


@dataclass
class PredictionResult:
    """Result from a prediction model."""
    symbol: str
    model_type: ModelType
    predicted_return: float
    confidence: float  # 0-1
    uncertainty: float  # Standard deviation of prediction
    feature_importance: Dict[str, float]
    attention_weights: Optional[List[float]] = None
    prediction_horizon: int = 5


@dataclass
class SignalResult:
    """Complete signal generation result."""
    predictions: Dict[str, PredictionResult]
    rankings: List[str]  # Symbols ranked by predicted return
    market_regime: str  # bull, bear, sideways
    overall_confidence: float
    model_metadata: Dict[str, Any]


@dataclass
class BacktestResult:
    """Backtest simulation result."""
    total_return: float
    total_return_pct: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int  # days
    win_rate: float
    profit_factor: float
    trades_count: int
    avg_trade_return: float
    equity_curve: List[Dict[str, Any]]
    monthly_returns: List[Dict[str, Any]]
    drawdown_series: List[Dict[str, Any]]
    trade_history: List[Dict[str, Any]]


@dataclass
class FactorExposure:
    """Factor exposure analysis."""
    portfolio_id: int
    market_beta: float
    size_factor: float
    value_factor: float
    momentum_factor: float
    quality_factor: float
    volatility_factor: float
    dividend_factor: float
    growth_factor: float
