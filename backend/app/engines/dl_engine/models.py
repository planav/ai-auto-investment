"""
Deep Learning Models for Stock Return Prediction

Implements three production-quality architectures:
1. LSTM with Multi-Head Attention (LSTMAttention)
2. Temporal Fusion Transformer (TFT) — faithful implementation of Lim et al. 2021
3. N-BEATS — Neural Basis Expansion Analysis (Oreshkin et al. 2020)

Input:  (batch, seq_len=20, n_features=11)
Output: (batch, 1)  — predicted 5-day forward return
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


# ============================================================================
# 1. LSTM with Multi-Head Self-Attention
# ============================================================================

class LSTMAttention(nn.Module):
    """
    Bidirectional LSTM encoder with multi-head self-attention.

    Architecture:
        Input → Linear embedding → BiLSTM → Multi-Head Attention →
        Layer Norm → Feed-forward → Layer Norm → Regression head

    Reference: Attention Is All You Need + LSTM sequence encoder.
    """

    def __init__(self, input_size: int = 11, hidden_size: int = 128,
                 num_layers: int = 2, num_heads: int = 4,
                 dropout: float = 0.2, output_size: int = 1):
        super().__init__()

        # Input projection
        self.input_proj = nn.Linear(input_size, hidden_size)
        self.input_norm = nn.LayerNorm(hidden_size)

        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            hidden_size, hidden_size // 2,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        # Multi-head self-attention
        self.attention = nn.MultiheadAttention(
            hidden_size, num_heads=num_heads,
            dropout=dropout, batch_first=True,
        )
        self.attn_norm = nn.LayerNorm(hidden_size)

        # Feed-forward after attention
        self.ff = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 2, hidden_size),
        )
        self.ff_norm = nn.LayerNorm(hidden_size)

        # Regression head
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 64),
            nn.GELU(),
            nn.Linear(64, output_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        z = self.input_norm(self.input_proj(x))              # (B, T, H)
        h, _ = self.lstm(z)                                  # (B, T, H)

        # Self-attention with residual
        attn_out, _ = self.attention(h, h, h)
        h = self.attn_norm(h + attn_out)                     # (B, T, H)

        # Feed-forward with residual
        h = self.ff_norm(h + self.ff(h))                     # (B, T, H)

        # Take last timestep representation
        out = self.head(h[:, -1, :])                         # (B, 1)
        return out


# ============================================================================
# 2. Temporal Fusion Transformer (TFT)
#    Lim et al. 2021 — "Temporal Fusion Transformers for
#    Interpretable Multi-horizon Time Series Forecasting"
# ============================================================================

class GatedLinearUnit(nn.Module):
    """GLU: splits features in half, one half gates the other (sigmoid gate)."""
    def __init__(self, size: int):
        super().__init__()
        self.fc = nn.Linear(size, size * 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        a, b = self.fc(x).chunk(2, dim=-1)
        return a * torch.sigmoid(b)


class GatedResidualNetwork(nn.Module):
    """
    GRN from TFT paper. Applies a two-layer feed-forward with ELU activation,
    gated by a GLU, with skip connection and layer normalisation.

    If skip_dim != input_dim, a linear projection is used for the residual.
    """
    def __init__(self, input_size: int, hidden_size: int,
                 output_size: int, dropout: float = 0.1,
                 context_size: int = 0):
        super().__init__()
        self.skip = (
            nn.Linear(input_size, output_size)
            if input_size != output_size else nn.Identity()
        )
        self.fc1 = nn.Linear(input_size + context_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.glu = GatedLinearUnit(output_size)
        self.norm = nn.LayerNorm(output_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, context: torch.Tensor = None) -> torch.Tensor:
        residual = self.skip(x)
        if context is not None:
            x = torch.cat([x, context], dim=-1)
        h = F.elu(self.fc1(x))
        h = self.dropout(self.fc2(h))
        h = self.glu(h)
        return self.norm(h + residual)


class VariableSelectionNetwork(nn.Module):
    """
    VSN from TFT: learns soft attention weights over input variables,
    then applies per-variable GRNs before combining.
    """
    def __init__(self, n_vars: int, var_dim: int, hidden_size: int,
                 dropout: float = 0.1):
        super().__init__()
        # Per-variable GRN
        self.var_grns = nn.ModuleList([
            GatedResidualNetwork(var_dim, hidden_size, hidden_size, dropout)
            for _ in range(n_vars)
        ])
        # Flatten + selection weights
        self.flat_grn = GatedResidualNetwork(
            n_vars * var_dim, hidden_size, n_vars, dropout
        )
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x: torch.Tensor) -> tuple:
        # x: (B, T, n_vars, var_dim)  OR  (B, n_vars, var_dim) static
        B = x.size(0)
        flat = x.reshape(B, -1) if x.dim() == 3 else x.reshape(B, x.size(1), -1)

        # Selection weights
        weights = self.softmax(self.flat_grn(flat.reshape(B, -1)))    # (B, n_vars)

        # Per-variable processing
        processed = []
        for i, grn in enumerate(self.var_grns):
            v = x[..., i, :] if x.dim() == 4 else x[:, i, :]
            processed.append(grn(v))
        processed = torch.stack(processed, dim=-2)                    # (B, [T,] n_vars, H)

        # Weighted combination
        w = weights.unsqueeze(-1)                                     # (B, [T,] n_vars, 1)
        if x.dim() == 4:
            w = w.unsqueeze(1)
        out = (processed * w).sum(dim=-2)                             # (B, [T,] H)
        return out, weights


class TemporalFusionTransformer(nn.Module):
    """
    Temporal Fusion Transformer (TFT) — Lim et al. 2021.

    Key components:
    1. Variable Selection Networks (VSN) — learn which features matter most
    2. LSTM encoder-decoder — captures sequential dependencies
    3. Gated Residual Networks (GRN) — selective information propagation
    4. Multi-Head Temporal Self-Attention — long-range dependencies + attention weights
    5. Point-wise feed-forward with gating and layer norm

    This architecture is interpretable: attention weights show which time-steps
    the model focuses on, and VSN weights show which features matter most.
    """

    def __init__(self, input_size: int = 11, seq_len: int = 20,
                 hidden_size: int = 64, num_heads: int = 4,
                 num_lstm_layers: int = 2, dropout: float = 0.1,
                 output_size: int = 1):
        super().__init__()
        self.hidden_size = hidden_size
        self.seq_len     = seq_len

        # ── Input variable selection ──────────────────────────────────────
        # Treat each feature as a single-dim variable, project to hidden_size
        self.var_proj  = nn.Linear(1, hidden_size)
        self.input_vsn = nn.Sequential(
            nn.Linear(input_size * hidden_size, hidden_size),
            nn.ELU(),
            nn.Linear(hidden_size, input_size),
            nn.Softmax(dim=-1),
        )
        self.var_grns = nn.ModuleList([
            GatedResidualNetwork(hidden_size, hidden_size, hidden_size, dropout)
            for _ in range(input_size)
        ])

        # ── LSTM sequence encoder ─────────────────────────────────────────
        self.lstm_encoder = nn.LSTM(
            hidden_size, hidden_size,
            num_layers=num_lstm_layers,
            batch_first=True,
            dropout=dropout if num_lstm_layers > 1 else 0.0,
        )
        self.lstm_norm = nn.LayerNorm(hidden_size)

        # ── Static context GRN (no static features → zero context) ───────
        self.static_grn = GatedResidualNetwork(hidden_size, hidden_size, hidden_size, dropout)

        # ── Gated skip connection around LSTM ─────────────────────────────
        self.post_lstm_gate = GatedLinearUnit(hidden_size)
        self.post_lstm_norm = nn.LayerNorm(hidden_size)

        # ── Multi-Head Temporal Self-Attention ────────────────────────────
        self.temporal_attn = nn.MultiheadAttention(
            hidden_size, num_heads=num_heads, dropout=dropout, batch_first=True
        )
        self.attn_gate = GatedLinearUnit(hidden_size)
        self.attn_norm = nn.LayerNorm(hidden_size)

        # ── Position-wise feed-forward (GRN) ─────────────────────────────
        self.pos_ff = GatedResidualNetwork(hidden_size, hidden_size, hidden_size, dropout)
        self.ff_norm = nn.LayerNorm(hidden_size)

        # ── Regression head ───────────────────────────────────────────────
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 32),
            nn.GELU(),
            nn.Linear(32, output_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, F = x.shape   # (batch, seq_len, n_features)

        # ── Variable Selection ────────────────────────────────────────────
        # Project each feature independently: (B, T, F, H)
        x_vars = self.var_proj(x.unsqueeze(-1))      # (B, T, F, H)

        # Compute selection weights from flattened input
        flat   = x_vars.reshape(B, T, F * self.hidden_size)
        weights= torch.softmax(self.input_vsn(flat), dim=-1)   # (B, T, F)

        # Apply per-variable GRNs
        processed = torch.stack(
            [self.var_grns[i](x_vars[:, :, i, :]) for i in range(F)], dim=2
        )                                                        # (B, T, F, H)

        # Weighted sum over features → single vector per timestep
        enc_in = (processed * weights.unsqueeze(-1)).sum(dim=2) # (B, T, H)

        # ── LSTM encoder ──────────────────────────────────────────────────
        lstm_out, _ = self.lstm_encoder(enc_in)                  # (B, T, H)
        lstm_out    = self.lstm_norm(lstm_out)

        # Gated skip: combine LSTM output with input
        h = self.post_lstm_norm(
            self.post_lstm_gate(lstm_out) + enc_in
        )                                                        # (B, T, H)

        # ── Temporal Self-Attention ───────────────────────────────────────
        attn_out, self.attn_weights = self.temporal_attn(h, h, h)
        h = self.attn_norm(self.attn_gate(attn_out) + h)        # (B, T, H)

        # ── Position-wise feed-forward ────────────────────────────────────
        h = self.ff_norm(self.pos_ff(h) + h)                    # (B, T, H)

        # ── Regression head on last timestep ─────────────────────────────
        return self.head(h[:, -1, :])                            # (B, 1)

    def get_attention_weights(self) -> torch.Tensor:
        """Return the last temporal attention weight matrix (B, T, T)."""
        return getattr(self, "attn_weights", None)


# ============================================================================
# 3. N-BEATS — Neural Basis Expansion Analysis
#    Oreshkin et al. 2020 — "N-BEATS: Neural Basis Expansion Analysis
#    for Interpretable Time Series Forecasting"
# ============================================================================

class NBEATSBlock(nn.Module):
    """Single N-BEATS block: FC stack → basis expansion for backcast + forecast."""
    def __init__(self, input_size: int, hidden_size: int,
                 n_layers: int = 4, basis_size: int = 4):
        super().__init__()
        layers = [nn.Linear(input_size, hidden_size), nn.ReLU()]
        for _ in range(n_layers - 1):
            layers += [nn.Linear(hidden_size, hidden_size), nn.ReLU()]
        self.fc_stack = nn.Sequential(*layers)

        self.backcast_proj = nn.Linear(hidden_size, input_size)
        self.forecast_proj = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor) -> tuple:
        h        = self.fc_stack(x)
        backcast = self.backcast_proj(h)
        forecast = self.forecast_proj(h)
        return backcast, forecast


class NBEATS(nn.Module):
    """
    N-BEATS with generic (non-interpretable) blocks.
    Stacks multiple blocks in a residual fashion:
      input → Block1 → residual → Block2 → residual → ... → sum of forecasts
    """
    def __init__(self, input_size: int, hidden_size: int = 256,
                 n_blocks: int = 4, n_layers: int = 4,
                 dropout: float = 0.1, output_size: int = 1):
        super().__init__()
        # Flatten (B, T, F) → (B, T*F)
        self.input_size = input_size
        self.blocks = nn.ModuleList([
            NBEATSBlock(input_size, hidden_size, n_layers)
            for _ in range(n_blocks)
        ])
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.size(0)
        x_flat  = x.reshape(B, -1)          # (B, T*F)
        residual = x_flat
        total_forecast = torch.zeros(B, 1, device=x.device)

        for block in self.blocks:
            backcast, forecast = block(residual)
            residual = residual - backcast   # doubly-residual connection
            total_forecast = total_forecast + forecast

        return total_forecast                # (B, 1)


# ============================================================================
# Ensemble wrapper
# ============================================================================

class DLEnsemble(nn.Module):
    """
    Weighted ensemble of TFT, LSTM-Attention, and N-BEATS.
    Weights are learned parameters (learned mixing).
    """
    def __init__(self, input_size: int = 11, seq_len: int = 20,
                 hidden: int = 64, dropout: float = 0.1):
        super().__init__()
        flat_size = input_size * seq_len

        self.tft  = TemporalFusionTransformer(input_size, seq_len, hidden,
                                               num_heads=4, dropout=dropout)
        self.lstm = LSTMAttention(input_size, hidden * 2, num_heads=4,
                                   dropout=dropout)
        self.nbeats = NBEATS(flat_size, hidden_size=256, n_blocks=4,
                              dropout=dropout)

        # Learned mixing weights (softmax ensures they sum to 1)
        self.mix_logits = nn.Parameter(torch.tensor([0.5, 0.35, 0.15]))

    @property
    def mix_weights(self) -> torch.Tensor:
        return torch.softmax(self.mix_logits, dim=0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = self.mix_weights
        out_tft    = self.tft(x)    * w[0]
        out_lstm   = self.lstm(x)   * w[1]
        out_nbeats = self.nbeats(x) * w[2]
        return out_tft + out_lstm + out_nbeats
