```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║        ██████╗ ██╗   ██╗████████╗ ██████╗ ██╗███╗   ██╗██╗   ██╗███████╗███████╗   ║
║       ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██║████╗  ██║██║   ██║██╔════╝██╔════╝   ║
║       ███████║██║   ██║   ██║   ██║   ██║██║██╔██╗ ██║██║   ██║█████╗  ███████╗   ║
║       ██╔══██║██║   ██║   ██║   ██║   ██║██║██║╚██╗██║╚██╗ ██╔╝██╔══╝  ╚════██║   ║
║       ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║██║ ╚████║ ╚████╔╝ ███████╗███████║   ║
║       ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚══════╝╚══════╝   ║
║                                                                                      ║
║          AI-POWERED AUTONOMOUS INVESTMENT PORTFOLIO MANAGEMENT SYSTEM               ║
║                                                                                      ║
║   TFT · LSTM-Attention · N-BEATS · Claude Sonnet · Markowitz Optimization           ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
```

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.11-red?style=for-the-badge&logo=pytorch)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)
![Claude](https://img.shields.io/badge/Claude-Sonnet_4.6-purple?style=for-the-badge)
![sklearn](https://img.shields.io/badge/scikit--learn-1.8-orange?style=for-the-badge&logo=scikit-learn)

**The world's most advanced open-source AI investment platform — combining LLMs, Deep Learning, and Quantitative Finance.**

</div>

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [The Three-Layer AI Pipeline — Deep Dive](#3-the-three-layer-ai-pipeline--deep-dive)
4. [Deep Learning Models Architecture](#4-deep-learning-models-architecture)
5. [Data Pipeline & Feature Engineering](#5-data-pipeline--feature-engineering)
6. [Complete End-to-End Technical Flow](#6-complete-end-to-end-technical-flow)
7. [Portfolio Optimization Engine](#7-portfolio-optimization-engine)
8. [Database Architecture & Schema](#8-database-architecture--schema)
9. [Backend API Architecture](#9-backend-api-architecture)
10. [Frontend Architecture](#10-frontend-architecture)
11. [Security & Authentication Architecture](#11-security--authentication-architecture)
12. [Real-Time Data Infrastructure](#12-real-time-data-infrastructure)
13. [Mathematical Formulations](#13-mathematical-formulations)
14. [Technology Stack](#14-technology-stack)
15. [Performance & Model Metrics](#15-performance--model-metrics)
16. [Setup & Installation](#16-setup--installation)
17. [API Reference](#17-api-reference)
18. [Academic References](#18-academic-references)

---

## 1. Executive Summary

AutoInvest is a **production-grade AI investment platform** that autonomously constructs, optimizes, and manages investment portfolios using a novel **three-layer heterogeneous AI architecture**. It is the first open-source platform to combine:

- **Claude Sonnet AI** (LLM) for real-time market news analysis and sector rotation identification
- **Temporal Fusion Transformer** (TFT, Lim et al. 2021) for multi-horizon return prediction with interpretable attention
- **LSTM with Multi-Head Self-Attention** for sequential momentum pattern recognition
- **N-BEATS** (Oreshkin et al. 2020) for trend/seasonality decomposition
- **Markowitz Mean-Variance Optimization** with empirical covariance matrices
- **Real-time Finnhub integration** for live market data, sector ETF performance, and analyst consensus

### Key Innovation

```
Traditional Robo-Advisors:        AutoInvest:
━━━━━━━━━━━━━━━━━━━━━━━━━━━       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Static asset allocation     →     Dynamic AI-driven stock selection from news
Rule-based rebalancing      →     DL model predictions (TFT + LSTM + N-BEATS)
No natural language         →     Claude Sonnet explains EVERY decision
Historical correlations     →     Live Finnhub sector ETF momentum
Same portfolio for everyone →     News-context-aware, unique per user per run
```

---

## 2. System Architecture Overview

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                      AUTOINVEST — COMPLETE SYSTEM ARCHITECTURE                           ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                          ║
║  ┌─────────────────────────────────────────────────────────────────────────────────┐    ║
║  │                        USER INTERFACE LAYER                                     │    ║
║  │                     React 19 + Vite 7 + Tailwind CSS                           │    ║
║  │                                                                                  │    ║
║  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │    ║
║  │  │Dashboard │  │Portfolio │  │Analysis  │  │  Invest  │  │Deposit/Withdraw  │  │    ║
║  │  │+ Market  │  │Holdings  │  │(Claude   │  │(3-Step   │  │Wallet Management │  │    ║
║  │  │Overview  │  │+ P&L     │  │Sonnet AI)│  │Wizard)   │  │+ Transactions    │  │    ║
║  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │    ║
║  │       └─────────────┴─────────────┴──────────────┘                  │            │    ║
║  │                              │ Axios HTTP + JWT                      │            │    ║
║  └──────────────────────────────┼───────────────────────────────────────┘            ║
║                                 │                                                    ║
║  ┌──────────────────────────────▼───────────────────────────────────────────────┐   ║
║  │                     FastAPI 0.109 — ASYNC REST API                            │   ║
║  │                    Uvicorn ASGI · Pydantic v2 · JWT Auth                      │   ║
║  │                                                                                │   ║
║  │   /auth  /users  /portfolios  /analysis  /market  /wallet  /dashboard         │   ║
║  │   /api/model/train  /api/model/status  /api/model/info                        │   ║
║  └──────────────────────────────┬───────────────────────────────────────────────┘   ║
║                                 │                                                    ║
║  ┌──────────────────────────────▼───────────────────────────────────────────────┐   ║
║  │                    THREE-LAYER AI PIPELINE (CORE)                             │   ║
║  │                                                                                │   ║
║  │  ┌─────────────────────────────────────────────────────────────────────────┐  │   ║
║  │  │ LAYER 1 — CLAUDE SONNET AI (Natural Language Intelligence)               │  │   ║
║  │  │                                                                           │  │   ║
║  │  │  NewsAPI ──►  Sector-targeted  ──►  Claude Sonnet  ──►  25 stocks        │  │   ║
║  │  │  Finnhub ──►  headlines (12)        real-time            with specific   │  │   ║
║  │  │  Sector  ──►  + live sector         analysis             news catalysts  │  │   ║
║  │  │  ETF data      performance          temperature=0.7      + conviction    │  │   ║
║  │  └─────────────────────────────────────────────────────────────────────────┘  │   ║
║  │                              ↓                                                 │   ║
║  │  ┌─────────────────────────────────────────────────────────────────────────┐  │   ║
║  │  │ LAYER 2 — DEEP LEARNING SCORING ENGINE (Torch 2.11)                     │  │   ║
║  │  │                                                                           │  │   ║
║  │  │  TFT (366K params)    ──┐                                                 │  │   ║
║  │  │  LSTM-Attn (341K)     ──┼──► Learned Ensemble ──► Ranked top-10 stocks  │  │   ║
║  │  │  N-BEATS (1.24M)      ──┘     (1.95M params)      by predicted 5-day    │  │   ║
║  │  │  ↑ 11 features × 20-day window (AV + Finnhub)       forward return      │  │   ║
║  │  └─────────────────────────────────────────────────────────────────────────┘  │   ║
║  │                              ↓                                                 │   ║
║  │  ┌─────────────────────────────────────────────────────────────────────────┐  │   ║
║  │  │ LAYER 3 — PORTFOLIO OPTIMIZATION + CLAUDE REASONING                     │  │   ║
║  │  │                                                                           │  │   ║
║  │  │  Markowitz MVo  ──►  Risk-profile  ──►  Optimal    ──►  Claude explains │  │   ║
║  │  │  Empirical Cov      constraints        weights         each stock pick  │  │   ║
║  │  │  Sector correl.     (min 3%, max 25%)  + metrics       in natural lang. │  │   ║
║  │  └─────────────────────────────────────────────────────────────────────────┘  │   ║
║  └──────────────────────────────┬───────────────────────────────────────────────┘   ║
║                                 │                                                    ║
║  ┌──────────────────────────────▼───────────────────────────────────────────────┐   ║
║  │                    DATA & PERSISTENCE LAYER                                   │   ║
║  │                                                                                │   ║
║  │  SQLAlchemy 2.0 Async    SQLite (Dev)    PostgreSQL (Prod)    Redis Cache     │   ║
║  │  Alembic Migrations      aiosqlite        asyncpg driver       (NoopCache     │   ║
║  │                                                                  fallback)     │   ║
║  └──────────────────────────────┬───────────────────────────────────────────────┘   ║
║                                 │                                                    ║
║  ┌──────────────────────────────▼───────────────────────────────────────────────┐   ║
║  │                    EXTERNAL API INTEGRATIONS                                  │   ║
║  │                                                                                │   ║
║  │  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │   ║
║  │  │Anthropic │  │   Finnhub    │  │  Alpha   │  │ NewsAPI  │  │  Polygon  │  │   ║
║  │  │ Claude   │  │  (Quotes,    │  │Vantage   │  │(Financial│  │  (Market  │  │   ║
║  │  │Sonnet+   │  │  Sector ETFs,│  │(Training │  │ News for │  │  data     │  │   ║
║  │  │ Haiku    │  │  Rec, News)  │  │  Data)   │  │  Claude) │  │ backup)   │  │   ║
║  │  └──────────┘  └──────────────┘  └──────────┘  └──────────┘  └───────────┘  │   ║
║  └──────────────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## 3. The Three-Layer AI Pipeline — Deep Dive

### Layer 1: Claude Sonnet AI — Market Intelligence

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        LAYER 1: CLAUDE SONNET AI STOCK SELECTOR                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  INPUTS (fetched in parallel via asyncio.gather):                                    │
│                                                                                       │
│  ┌──────────────────┐    ┌──────────────────────────────────────────────────────┐   │
│  │   NewsAPI.org    │    │              Finnhub Live Data                       │   │
│  │                  │    │                                                       │   │
│  │  Query: tailored │    │  11 Sector ETFs (today's % change):                  │   │
│  │  to risk profile │    │   XLK Tech    XLF Finance   XLV Health              │   │
│  │  e.g. "AI semi-  │    │   XLE Energy  XLU Utilities XLI Industrial          │   │
│  │  conductor earn- │    │   XLY Cons.D  XLP Cons.S    XLB Materials           │   │
│  │  ings momentum   │    │   XLRE Real E XLC Comm.      ...                    │   │
│  │  breakout"       │    │                                                       │   │
│  │  → 15 headlines  │    │  Market indices: SPY, QQQ, IWM                      │   │
│  └──────────┬───────┘    └──────────────────────┬────────────────────────────┘   │
│             │                                     │                                  │
│             └────────────────┬────────────────────┘                                 │
│                              │                                                       │
│  ┌───────────────────────────▼───────────────────────────────────────────────────┐  │
│  │                      CLAUDE SONNET 4.6 PROMPT                                  │  │
│  │                                                                                  │  │
│  │  System: "You are a senior portfolio manager at a quantitative hedge fund."     │  │
│  │                                                                                  │  │
│  │  Given:                                                                          │  │
│  │    - 12 market news headlines (last 48h, sector-specific)                       │  │
│  │    - Live sector ETF performance (today's % change per sector)                  │  │
│  │    - Market index levels and daily changes                                       │  │
│  │    - Risk profile: AGGRESSIVE / MODERATE / CONSERVATIVE                         │  │
│  │    - Investment horizon: short / medium / long term                              │  │
│  │    - Random session seed (forces unique output each call)                        │  │
│  │    - Temperature: 0.7 (creative but grounded)                                   │  │
│  │    - Max tokens: 8,000 (no truncation risk)                                     │  │
│  │                                                                                  │  │
│  │  Task: Step 1 → Identify 2-3 hot sectors from data                              │  │
│  │        Step 2 → Select 25 stocks with SPECIFIC current catalysts                │  │
│  │        Step 3 → Each stock: reason must reference news OR sector data           │  │
│  │                                                                                  │  │
│  │  Output: JSON with market_analysis, hot_sectors, 25 stocks with reasons         │  │
│  └───────────────────────────┬───────────────────────────────────────────────────┘  │
│                              │                                                       │
│  ┌───────────────────────────▼───────────────────────────────────────────────────┐  │
│  │  SAMPLE OUTPUT (Real, from live Claude analysis)                                │  │
│  │                                                                                  │  │
│  │  market_analysis: "Nasdaq surging +1.91% driven by AI/chip rally; Technology   │  │
│  │                   sector leads at +2.81%. Bond yields steady."                  │  │
│  │                                                                                  │  │
│  │  hot_sectors: ["Technology", "Energy", "Consumer Discretionary"]                │  │
│  │                                                                                  │  │
│  │  stocks[0]: { symbol: "NVDA", conviction: "high",                               │  │
│  │    reason: "Chips carry stocks higher headline; NVDA apex beneficiary of        │  │
│  │             AI infrastructure capex; Technology +2.81% today" }                 │  │
│  │                                                                                  │  │
│  │  stocks[3]: { symbol: "CEG", conviction: "medium",                              │  │
│  │    reason: "Nuclear power for AI data centers; energy demand surge from         │  │
│  │             hyperscalers cited in Constellation Energy deal news" }              │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  FALLBACK (when Claude fails): Dynamic Finnhub momentum ranking                      │
│    → Fetch live quotes for 50+ risk-profile candidates                               │
│    → Rank by today's dp% (daily momentum)                                            │
│    → Return top-30 by momentum — ALWAYS data-driven, never static                   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Layer 2: Deep Learning Scoring Engine

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      LAYER 2: PYTORCH DEEP LEARNING ENSEMBLE                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  INPUT: 25 Claude-selected stocks → Finnhub live quotes + AV historical data         │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                  FEATURE ENGINEERING (11 features × 20 days)                │    │
│  │                                                                               │    │
│  │  From Alpha Vantage (100-day daily OHLCV) + Finnhub (live quote):            │    │
│  │                                                                               │    │
│  │  1. daily_return      = log(close_t / close_{t-1})                           │    │
│  │  2. volume_change     = log(volume_t / volume_{t-1})                         │    │
│  │  3. rsi_14            = RSI(14) normalised → [-1, +1]                        │    │
│  │  4. macd_signal       = MACD histogram / price                               │    │
│  │  5. sma20_ratio       = close / SMA(20) - 1                                  │    │
│  │  6. sma50_ratio       = close / SMA(50) - 1                                  │    │
│  │  7. bb_position       = (close - BB_lower) / (BB_upper - BB_lower) - 0.5    │    │
│  │  8. high_low_range    = (high - low) / close                                 │    │
│  │  9. momentum_5d       = close / close_{t-5} - 1                             │    │
│  │  10. volatility_10d   = rolling 10-day std(daily_return)                    │    │
│  │  11. atr_ratio        = ATR(14) / close                                      │    │
│  │                                                                               │    │
│  │  All features clipped to ±3σ. Input tensor: (1, 20, 11)                     │    │
│  └────────────────────────────────────────────────────────────────┬────────────┘    │
│                                                                     │                 │
│  ┌──────────────────────────────┐  ┌──────────────────────────────▼──────────────┐  │
│  │  MODEL A: TFT (366K params)  │  │  MODEL B: LSTM-Attention (341K params)       │  │
│  │                              │  │                                               │  │
│  │  Input (1,20,11)             │  │  Input (1,20,11)                             │  │
│  │     ↓                        │  │     ↓                                         │  │
│  │  Variable Selection Net      │  │  Linear projection → (1,20,128)              │  │
│  │  (soft attention over 11     │  │     ↓                                         │  │
│  │   features per timestep)     │  │  BiLSTM × 2 layers                           │  │
│  │     ↓                        │  │  (hidden=64 each direction)                  │  │
│  │  Per-variable GRN            │  │     ↓                                         │  │
│  │  (Gated Residual Networks)   │  │  Multi-Head Self-Attention                   │  │
│  │     ↓                        │  │  (4 heads, captures temporal patterns)       │  │
│  │  LSTM encoder (2 layers)     │  │     ↓                                         │  │
│  │     ↓                        │  │  Feed-Forward (GELU) + LayerNorm             │  │
│  │  Gated skip connection       │  │     ↓                                         │  │
│  │  (post-LSTM gate + LN)       │  │  Last timestep → head → (1,1)               │  │
│  │     ↓                        │  │                                               │  │
│  │  Temporal Self-Attention     │  │  Returns: predicted 5-day return             │  │
│  │  (4 heads, interpretable)    │  │                                               │  │
│  │     ↓                        │  └──────────────────────────────────────────────┘  │
│  │  Position-wise GRN           │                                                  │  │
│  │     ↓                        │  ┌──────────────────────────────────────────────┐  │
│  │  Last timestep → (1,1)       │  │  MODEL C: N-BEATS (1.24M params)            │  │
│  │                              │  │                                               │  │
│  │  Attn weights = interpretable│  │  Flatten (1,20,11) → (1,220)                │  │
│  │  view of which days matter   │  │  4 blocks, doubly-residual:                  │  │
│  └──────────────────────────────┘  │    Block_i: FC-stack(256) → backcast+fcast  │  │
│                                     │    residual -= backcast                       │  │
│                                     │    forecast += fcast                         │  │
│                                     │  Final forecast: (1,1)                      │  │
│                                     └──────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                   LEARNED ENSEMBLE (1.95M total params)                      │    │
│  │                                                                               │    │
│  │   pred = softmax(w_logits)[0] × TFT(x)                                      │    │
│  │         + softmax(w_logits)[1] × LSTM(x)                                    │    │
│  │         + softmax(w_logits)[2] × NBEATS(x)                                  │    │
│  │                                                                               │    │
│  │   Learned mixing weights (initialized: TFT=50%, LSTM=35%, N-BEATS=15%)      │    │
│  │   Fine-tuned during ensemble training (sub-models frozen)                    │    │
│  │                                                                               │    │
│  │   Output: predicted_return (5-day), confidence, tft_pred, lstm_pred,         │    │
│  │           nbeats_pred, ml_score (0-100), signal_strength                     │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                       │
│  RANKING: Sort all 25 stocks by ml_score DESC → select TOP 10 for Layer 3            │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Layer 3: Portfolio Optimization + Claude Reasoning

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                  LAYER 3: OPTIMIZATION + NATURAL LANGUAGE REASONING                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  INPUTS: 10 DL-ranked stocks + predicted returns + risk profile                      │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │             COVARIANCE MATRIX CONSTRUCTION (Empirical)                       │    │
│  │                                                                               │    │
│  │   Σᵢⱼ = σᵢ × σⱼ × ρ(sector_i, sector_j)                                    │    │
│  │                                                                               │    │
│  │   Known volatilities:  NVDA=50%, AMD=55%, TSLA=65%, SPY=17%, BND=5%...      │    │
│  │   Sector correlations: Tech-Tech=0.75, Tech-Bond=-0.10, Bond-Bond=0.90...    │    │
│  │                                                                               │    │
│  │   Result: stable, regime-independent 10×10 covariance matrix                 │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │             MARKOWITZ MEAN-VARIANCE OPTIMIZATION                              │    │
│  │                                                                               │    │
│  │   max  μᵀw − (λ/2) wᵀΣw     (Maximize Sharpe-adjusted return)               │    │
│  │    w                                                                          │    │
│  │   s.t. Σwᵢ = 1 − cash_reserve                                               │    │
│  │        w_min ≤ wᵢ ≤ w_max     (3% ≤ each position ≤ 25%)                   │    │
│  │                                                                               │    │
│  │   Risk aversion λ by profile:  Conservative=3.0  Moderate=2.0  Aggressive=1.0│   │
│  │   Return floors:               4% / 6% / 9% (prevents noise-driven negatives)│   │
│  │                                                                               │    │
│  │   Solved via: Gradient ascent (100 iterations, lr=0.01, early stop 1e-6)     │    │
│  │                                                                               │    │
│  │   Metrics computed:   E[R] = μᵀw                                             │    │
│  │                       σₚ   = √(wᵀΣw)                                         │    │
│  │                       S    = (E[R] − Rf) / σₚ    [Sharpe, Rf=2%]            │    │
│  │                       VaR₉₅= σₚ×1.645 − E[R]                               │    │
│  │                       CVaR₉₅= σₚ×2.063 − E[R]                              │    │
│  │                       DR   = Σ(wᵢσᵢ) / σₚ       [Diversification Ratio]    │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │              CLAUDE HAIKU — PER-STOCK REASONING GENERATION                   │    │
│  │                                                                               │    │
│  │   Input to Claude: symbol, weight, ML score, predicted return, daily change  │    │
│  │                    sector, analyst score, market context from Layer 1        │    │
│  │                                                                               │    │
│  │   Output (stored in DB, displayed in UI):                                    │    │
│  │                                                                               │    │
│  │   "NVDA: Selected as foundational AI infrastructure play with 93.8 ML score  │    │
│  │    delivering +4.32% today while commanding 8.9% weight as core holding for  │    │
│  │    aggressive investors seeking GPU compute monopoly exposure..."             │    │
│  │                                                                               │    │
│  │   "AMD: Highest-conviction position at 100.0 ML score with 16.7% predicted   │    │
│  │    return, surging +13.91% today as it captures share in high-margin         │    │
│  │    data center AI accelerators..."                                            │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Deep Learning Models Architecture

### 4.1 Temporal Fusion Transformer (TFT)

*Lim, B., Arık, S.Ö., Loeff, N. & Pfister, T. (2021). Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting. IJF 37(4), 1748–1764.*

```
INPUT: x ∈ ℝ^(B × T × F)    [B=batch, T=20 days, F=11 features]
│
├─► Variable Selection Network (VSN)
│     ├─ Project each feature f_i: ℝ¹ → ℝ^H via Linear(1, H=64)
│     ├─ Flatten all projections: ℝ^(F×H) → compute selection weights via GRN
│     ├─ Softmax → α ∈ ℝ^F  (which features matter most, per timestep)
│     └─ Weighted sum:  ẑ = Σᵢ αᵢ · GRN_i(x_i)  ∈ ℝ^H
│
├─► LSTM Encoder (2 layers, hidden=H=64)
│     ├─ h, c = LSTM(ẑ)                            h ∈ ℝ^(B×T×H)
│     └─ Layer Norm → h_norm
│
├─► Gated Skip Connection (prevents irrelevant LSTM output)
│     ├─ gate  = σ(Linear(h_norm))                 gate ∈ [0,1]^H
│     └─ h_skip = LN(gate ⊙ h_norm + ẑ)
│
├─► Multi-Head Temporal Self-Attention (4 heads)
│     ├─ Q, K, V = h_skip → MultiheadAttention(h_skip, h_skip, h_skip)
│     │   [Each head learns which PAST DAYS most predict the future]
│     ├─ Attention weights A ∈ ℝ^(T×T) [INTERPRETABLE — shows temporal focus]
│     └─ h_attn = LN(GLU(attn_output) + h_skip)
│
├─► Position-wise Feed-Forward (GRN)
│     └─ h_ff = LN(GRN(h_attn) + h_attn)
│
└─► Regression Head: h_ff[:, -1, :] → Linear(H, 32) → GELU → Linear(32, 1)
                                                                ↓
                                              predicted_return ∈ ℝ  (5-day fwd)
```

**Key property**: The attention matrix A shows which historical days the model focuses on — making predictions interpretable, unlike black-box models.

### 4.2 LSTM with Multi-Head Self-Attention

```
INPUT: x ∈ ℝ^(B × T × F)
│
├─► Input Projection:  z = LN(Linear(F→H=128)(x))
│
├─► Bidirectional LSTM (2 layers, H/2=64 each direction)
│     → h ∈ ℝ^(B×T×H)   [Concatenated forward + backward states]
│     [Captures: upward trends, momentum reversals, volatility cycles]
│
├─► Multi-Head Self-Attention (4 heads, d_k=32 per head)
│     Q=K=V=h → MultiheadAttention
│     → Learns: "WHEN RSI was last oversold & momentum turned positive"
│     → Residual + LayerNorm → h_attn
│
├─► Feed-Forward Block (GELU activation)
│     FC(H→2H) → GELU → Dropout → FC(2H→H) → Residual + LN
│
└─► Head: h[:, -1, :] → Dropout → Linear(H→64) → GELU → Linear(64→1)
```

### 4.3 N-BEATS (Neural Basis Expansion)

*Oreshkin, B.N., Carpov, D., Chapados, N. & Bengio, Y. (2020). N-BEATS: Neural Basis Expansion Analysis for Interpretable Time Series Forecasting. ICLR 2020.*

```
INPUT: x ∈ ℝ^(B × T×F=220)  [Flattened]
│
│  ┌─────── Doubly-Residual Stack (4 Blocks) ──────┐
│  │                                                  │
│  │  Block 1 (FC-stack: 256 hidden units, 4 layers)│
│  │    h = FC₄(ReLU(FC₃(ReLU(FC₂(ReLU(FC₁(x)))))))│
│  │    backcast₁ = Linear(h → 220)    [removes from input]  │
│  │    forecast₁ = Linear(h → 1)      [contributes to pred] │
│  │    residual  = x − backcast₁      [doubly-residual]     │
│  │                                                  │
│  │  Block 2 ... Block 4  (same structure)          │
│  │    each block: remove its backcast, add forecast │
│  └─────────────────────────────────────────────────┘
│
└─► final_forecast = Σ(forecast_i)  for i=1..4
```

**Key property**: Each block specializes in a different component (trend, seasonality, momentum, noise) — making the architecture interpretable through basis expansion.

### 4.4 Ensemble Architecture

```
                    ┌─────────────────────────────────────────┐
                    │         LEARNED ENSEMBLE                  │
                    │                                           │
  x ─────────────► │  TFT(x)     ──►  w₀ = softmax(logit₀)   │
  │                │  LSTM(x)    ──►  w₁ = softmax(logit₁)   │──► pred = Σ(wᵢ × modelᵢ(x))
  └─────────────► │  NBEATS(x)  ──►  w₂ = softmax(logit₂)   │
                    │                                           │
                    │  w₀, w₁, w₂ are learned parameters       │
                    │  (sub-models frozen during ensemble train) │
                    └─────────────────────────────────────────┘

  Default initialization:  w = [0.50, 0.35, 0.15]  (TFT dominant)
  After fine-tuning:       w = learned from validation data
```

### 4.5 Training Configuration

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        TRAINING PIPELINE                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Data Collection:                                                          │
│    Source:    Alpha Vantage TIME_SERIES_DAILY (100 days per stock)        │
│    Universe:  25 diverse US stocks (NVDA, AMD, MSFT, CRWD, TSLA, ...)    │
│    Features:  11 technical indicators computed per trading day             │
│    Window:    seq_len=20 days input → HORIZON=5 day forward return       │
│    Sequences: ~80 per stock × 25 stocks = ~2,000 training samples         │
│    Split:     70% train / 15% val (chronological — no look-ahead leak)    │
│                                                                            │
│  Objective:    Huber Loss (δ=0.05) — robust to extreme return outliers    │
│                L(ŷ,y) = { ½(y-ŷ)²           if |y-ŷ| ≤ δ               │
│                         { δ(|y-ŷ| - ½δ)     otherwise                   │
│                                                                            │
│  Optimizer:    AdamW (lr=1e-3, weight_decay=1e-4)                        │
│  Scheduler:    CosineAnnealingLR (T_max=epochs)                          │
│  Regularisation: Gradient clipping (max_norm=1.0), Dropout (0.1-0.2)    │
│  Early Stopping: patience=15 epochs on validation loss                    │
│                                                                            │
│  Training order:                                                           │
│    1. Train TFT independently (100 epochs)                                │
│    2. Train LSTM independently (100 epochs)                               │
│    3. Train N-BEATS independently (100 epochs)                            │
│    4. Freeze sub-models, fine-tune ensemble mixing weights (30 epochs)    │
│                                                                            │
│  Trigger: POST /api/model/train-model  (background task, ~15 min CPU)    │
│  Status:  GET  /api/model/status                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Data Pipeline & Feature Engineering

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE DATA PIPELINE                                    │
└──────────────────────────────────────────────────────────────────────────────────┘

  TRAINING DATA COLLECTION (one-time, Alpha Vantage):
  ─────────────────────────────────────────────────────
  
  Alpha Vantage API ──► 25 stocks × 100 days OHLCV ──► Disk cache (JSON)
                                                          ↓
  Feature Engineering per stock:
  ─────────────────────────────
  
  Raw OHLCV (O, H, L, C, V) per day
  │
  ├─► daily_return    = log(Cₜ / Cₜ₋₁)
  ├─► volume_change   = log(Vₜ / Vₜ₋₁)
  ├─► rsi_14          = (100 - 100/(1+RS₁₄)) → normalised [-1,+1]
  │                     RS₁₄ = avg_gain₁₄ / avg_loss₁₄
  ├─► macd_signal     = EMA(C,12) - EMA(C,26), normalised by C
  ├─► sma20_ratio     = C / SMA(C,20) - 1
  ├─► sma50_ratio     = C / SMA(C,50) - 1
  ├─► bb_position     = (C - (SMA20 - 2σ)) / (4σ) - 0.5   [Bollinger]
  ├─► high_low_range  = (H - L) / C                         [daily range]
  ├─► momentum_5d     = C / Cₜ₋₅ - 1
  ├─► volatility_10d  = std(daily_return, window=10)
  └─► atr_ratio       = ATR(14) / C                         [volatility]
  
  All features clipped to ±3σ to remove outliers.
  
  Sliding window: step=1 day
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  Day  1 ──► Day 20  │  predict Day 25  (5-day forward log return)           │
  │  Day  2 ──► Day 21  │  predict Day 26                                        │
  │  ...                                                                          │
  │  Day 75 ──► Day 94  │  predict Day 99                                        │
  └──────────────────────────────────────────────────────────────────────────────┘
  
  Final tensor shapes:  X: (N, 20, 11)   y: (N, 1)
  
  
  INFERENCE DATA PIPELINE (live, per portfolio creation):
  ───────────────────────────────────────────────────────
  
  For each stock selected by Claude (Layer 1):
  
  1. Check AV disk cache (12h TTL) ──► if fresh, load
  2. If stale, fetch AV API         ──► save to cache
  3. Compute 11 features            ──► take last 20 rows
  4. Tensor: (1, 20, 11)            ──► DL ensemble inference
  5. Return: predicted_return, tft_pred, lstm_pred, nbeats_pred
  
  Rate-limit handling: 5 requests/min (12s gap after every 5 stocks)
```

---

## 6. Complete End-to-End Technical Flow

```
══════════════════════════════════════════════════════════════════════════════════════
                     PORTFOLIO CREATION — COMPLETE TECHNICAL FLOW
══════════════════════════════════════════════════════════════════════════════════════

USER: "Create Aggressive Portfolio — $10,000"
│
▼ [Frontend: Invest.jsx]
POST /api/v1/portfolios/  {name, investment_amount=10000, risk_profile=aggressive}
│
▼ [Backend: portfolios.py → create_portfolio()]
│
├─ STEP 1: WALLET VALIDATION
│   WalletService.get_or_create_wallet(user_id)
│   if wallet.balance < 10000: → raise 400 "Insufficient balance"
│   WalletService.deduct_for_investment(10000)
│   wallet.balance -= 10000 | wallet.total_invested += 10000
│   WalletTransaction(type=TRADE_BUY, amount=10000) created
│
├─ STEP 2: PORTFOLIO RECORD CREATED
│   Portfolio(total_value=10000, invested_amount=10000, risk_profile=aggressive)
│   → db.add() → db.commit() → id assigned (e.g., id=42)
│
├─ STEP 3: LAYER 1 — CLAUDE AI STOCK SELECTION (~5 seconds)
│   Parallel data fetch (asyncio.gather):
│   ├─ NewsAPI: 15 financial headlines (aggressive query: "AI semiconductor momentum")
│   ├─ Finnhub: 11 sector ETF quotes (XLK, XLF, XLV, XLE, XLI, XLY, XLP, XLB, XLRE, XLC, XLU)
│   └─ Finnhub: SPY + QQQ + IWM indices
│
│   Build prompt with REAL data:
│   "Technology +2.81% today. News: 'Chips carry stocks higher'..."
│
│   Claude Sonnet 4.6 (max_tokens=8000, temp=0.7):
│   → Identifies hot sectors: ["Technology", "Energy", "Consumer Discretionary"]
│   → Selects 25 stocks: [NVDA, AMD, SMCI, ARM, CRWD, CEG, ANET, DDOG, PANW, ...]
│   → Each with specific news-based catalyst reason
│
├─ STEP 4: LAYER 2 — DL ENSEMBLE SCORING (~8 seconds)
│   Parallel Finnhub fetch for all 25 stocks:
│   ├─ Quote: current price, dp (daily%), h, l, o, pc
│   └─ Recommendations: strongBuy, buy, hold, sell, strongSell counts
│
│   For each stock with AV historical data:
│   ├─ Load 100-day OHLCV from cache
│   ├─ Compute 11 features × 20 days → tensor (1, 20, 11)
│   ├─ TFT forward pass     → tft_pred
│   ├─ LSTM forward pass    → lstm_pred
│   ├─ N-BEATS forward pass → nbeats_pred
│   └─ Ensemble: pred = w₀×tft + w₁×lstm + w₂×nbeats
│
│   Sklearn fallback for stocks without AV data (Finnhub features only):
│   ├─ 8-feature vector: [dp, intraday_ratio, hl_range, analyst_score, ...]
│   └─ RandomForest + GradientBoosting ensemble
│
│   Sort all 25 stocks by ml_score DESC → SELECT TOP 10
│   e.g.: NVDA(ml_score=93.8), AMD(100.0), SMCI(87.3), CRWD(82.1)...
│
├─ STEP 5: LAYER 3 — PORTFOLIO OPTIMIZATION (~0.1 seconds)
│   Apply return floors: max(9%, predicted_return) for aggressive
│   Build 10×10 covariance matrix Σ (sector correlations + known vols)
│
│   Markowitz optimization (100 iterations gradient ascent):
│   max μᵀw − (1.0/2)wᵀΣw    subject to: Σwᵢ=0.95, 0.03≤wᵢ≤0.25
│   → Optimal weights per stock
│
│   Compute: E[R]=μᵀw, σₚ=√(wᵀΣw), Sharpe=(E[R]-0.02)/σₚ, VaR₉₅, CVaR₉₅
│
├─ STEP 6: HOLDINGS CREATION (Finnhub live prices)
│   For each of the 10 stocks:
│   ├─ market_value = $10,000 × weight   (e.g., NVDA: 8.9% → $890)
│   ├─ current_price = Finnhub live quote (e.g., NVDA: $208.27)
│   ├─ quantity = market_value / price   (e.g., 890/208.27 = 4.275 shares)
│   └─ PortfolioHolding(symbol, weight, qty, avg_price, current_price, market_value,
│                        predicted_return, confidence, signal_strength) created
│
│   Cash holding: PortfolioHolding(CASH, weight=0.05, market_value=500)
│   PortfolioSnapshot(total_value=10000) created for chart history
│
├─ STEP 7: CLAUDE HAIKU REASONING (~3 seconds)
│   For each of 10 holdings + market context:
│   → Claude generates per-stock explanation referencing ML score, daily price,
│     sector trend, and analyst consensus
│   → Stored in portfolio.stock_reasoning (displayed in AI Insights tab)
│
│   Claude also generates portfolio narrative (3-4 sentences)
│   → Stored in portfolio.ai_explanation
│
└─ STEP 8: RESPONSE + PERSISTENCE
    Portfolio saved: total_value, E[R], σₚ, Sharpe, VaR, CVaR, ai_explanation,
                     stock_reasoning, market_context
    
    HTTP 201 Created: Full PortfolioResponse with all holdings + metrics
    
    Frontend: Shows AI Analysis Summary screen with:
    ├─ Market context from Claude
    ├─ Per-stock reasoning (scrollable)
    ├─ Holdings allocation chips (color-coded by signal)
    └─ Expected return + Sharpe ratio

TOTAL TIME: ~16-36 seconds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Layer 1 (Claude + data fetch):  ~5-8s
Layer 2 (DL inference):         ~5-10s
Layer 3 (optimization):         ~0.1s
Claude reasoning:               ~3-5s
DB writes + response:           ~0.5s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Portfolio Optimization Engine

### 7.1 Optimization Methods Supported

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      THREE OPTIMIZATION ALGORITHMS                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  METHOD 1: Mean-Variance Optimization (Markowitz, 1952)                              │
│  ──────────────────────────────────────────────────────                               │
│  max  μᵀw − (λ/2)wᵀΣw                                                               │
│                                                                                       │
│  λ = {3.0 conservative, 2.0 moderate, 1.0 aggressive}                               │
│                                                                                       │
│  Solver: Gradient ascent                                                              │
│    ∇  = μ − λΣw                                                                     │
│    wₜ₊₁ = clip(wₜ + α∇, w_min, w_max),  α=0.01                                    │
│    wₜ₊₁ = wₜ₊₁ / Σwₜ₊₁ × investable_fraction                                      │
│    until ‖wₜ₊₁ − wₜ‖₂ < 1e-6  or  100 iterations                                 │
│                                                                                       │
│  METHOD 2: Risk Parity (Maillard et al., 2010)                                       │
│  ──────────────────────────────────────────────                                       │
│  wᵢ = (1/σᵢ) / Σⱼ(1/σⱼ) × (1 − cash_reserve)                                     │
│  Each asset contributes equal volatility risk                                         │
│                                                                                       │
│  METHOD 3: Equal Risk Contribution (ERC)                                              │
│  ──────────────────────────────────────                                               │
│  Solve: wᵢ × (Σw)ᵢ / σₚ = constant  ∀i                                             │
│                                                                                       │
│  Iterative:  RC_i  = wᵢ(Σw)ᵢ/σₚ                                                    │
│              w_new = w × √(RC̄/RC_i)   → renormalize                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Risk Metrics Computed

```
┌──────────────────────────────────────────────────────────────┐
│                   RISK METRICS SUITE (13 metrics)            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Portfolio Return:    E[Rₚ] = μᵀw                          │
│  Portfolio Variance:  σₚ²  = wᵀΣw                          │
│  Portfolio Volatility: σₚ  = √(wᵀΣw)                       │
│  Sharpe Ratio:        S   = (E[Rₚ] − Rf) / σₚ,  Rf=2%    │
│  VaR (95%):           VaR₉₅ = σₚ × 1.645 − E[Rₚ]         │
│  CVaR (95%):          CVaR₉₅ = σₚ × 2.063 − E[Rₚ]        │
│  Diversification:     DR  = Σ(wᵢσᵢ) / σₚ                  │
│  Concentration:       HHI = Σ(wᵢ²)  [Herfindahl index]    │
│  Max Drawdown:        DD_max = min((Vₜ−Peak_t)/Peak_t)     │
│  Sortino Ratio:       Sortino = E[Rₚ]/σ_downside           │
│  Calmar Ratio:        Calmar  = E[Rₚ]/|DD_max|             │
│  Tracking Error:      TE = σ(Rₚ − Rᵦ)                     │
│  Information Ratio:   IR = α / TE                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 8. Database Architecture & Schema

### 8.1 Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                       DATABASE SCHEMA (SQLite / PostgreSQL)                       │
└──────────────────────────────────────────────────────────────────────────────────┘

  users
  ─────────────────────────────────────────────────────────────────────────
  id (PK) │ email (unique) │ hashed_password (Argon2id)
  full_name │ is_active │ is_superuser │ is_verified (OTP email confirmed)
  risk_tolerance │ investment_horizon │ initial_investment │ monthly_contribution
  preferred_assets │ created_at │ updated_at
  
          │ 1                    │ 1
          │ ─────────────────    │
          ▼ N                    ▼ 1
  
  portfolios ◄──────────────── wallets
  ─────────────────────────────────── ─────────────────
  id (PK)                              id (PK)
  user_id (FK → users)                 user_id (FK, unique)
  name │ description                   balance
  total_value  [updated on refresh]    total_deposited
  invested_amount [adjusted on sell]   total_withdrawn
  cash_reserve_pct                     total_invested
  risk_profile                         currency
  model_type                           created_at │ updated_at
  expected_return │ volatility              │ 1
  sharpe_ratio │ var_95 │ cvar_95          │
  ai_explanation (Claude narrative)        ▼ N
  stock_reasoning (per-stock Claude)   wallet_transactions
  market_context (Layer 1 Claude)      ─────────────────────
  created_at │ updated_at              id │ wallet_id (FK)
      │                                type (DEPOSIT/WITHDRAW/
      │ 1                                   TRADE_BUY/TRADE_SELL)
      │                                amount │ balance_before
      ├──────────────────────────────  balance_after │ status
      ▼ N                              description │ reference_id
  portfolio_holdings
  ─────────────────────────────────
  id │ portfolio_id (FK)
  symbol │ asset_type (stock/etf/cash)
  sector
  weight [fraction of total value]
  quantity [shares owned]
  avg_price [cost basis at purchase]
  current_price [updated by Finnhub]
  market_value = current_price × qty
  predicted_return [DL ensemble output]
  confidence_score
  signal_strength (strong_buy/buy/hold/sell/strong_sell)
  created_at │ updated_at
  
      ▼ N  (from portfolios)
  portfolio_snapshots          portfolio_transactions
  ─────────────────────────    ─────────────────────────────
  id │ portfolio_id (FK)       id │ portfolio_id (FK)
  total_value                  transaction_type (buy/sell/rebalance)
  cash_value                   symbol │ quantity │ price
  stocks_value                 amount │ description
  created_at  ← TIME SERIES   created_at │ updated_at

  Migrations: Alembic (4 migrations, SQLite + PostgreSQL compatible)
  ORM: SQLAlchemy 2.0 async (asyncpg / aiosqlite)
```

### 8.2 Migration History

```
  33d2e3bd5f84  Initial migration
                → users, portfolios, portfolio_holdings

  bc06f0c36814  Wallet enhancements
                → wallets, wallet_transactions
                → adds: invested_amount, risk_profile to portfolios

  655fac73abc3  Portfolio snapshots + AI reasoning
                → portfolio_snapshots (time-series for charts)
                → adds: stock_reasoning, market_context to portfolios

  ea0a0dc2a7e9  Email OTP verification
                → adds: is_verified to users
```

---

## 9. Backend API Architecture

### 9.1 API Layer Structure

```
  FastAPI Application (app/main.py)
  ─────────────────────────────────
  
  truststore.inject_into_ssl()    ← Corporate CA injection (runs first)
  lifespan: startup/shutdown hooks
  CORSMiddleware (allow all methods, all headers)
  
  ┌─────────────────────────────────────────────────────────────────────┐
  │  Route Registry                                                       │
  ├──────────────────────────┬───────────────────────────────────────────┤
  │  /api/v1/auth            │  register, login, verify-otp, resend-otp │
  │  /api/v1/users           │  profile, preferences                     │
  │  /api/v1/dashboard       │  consolidated dashboard data              │
  │  /api/v1/portfolios      │  CRUD + AI creation + sell + chart        │
  │  /api/v1/analysis        │  deep stock analysis (Claude Sonnet)      │
  │  /api/v1/market          │  quotes, overview, search                 │
  │  /api/v1/wallet          │  deposit, withdraw, transactions          │
  │  /api/v1/system          │  stats, health                            │
  │  /api/gemini-query       │  Claude text query                        │
  │  /api/gemini-stream      │  Claude WebSocket streaming               │
  │  /api/ws/market-data     │  Simulated market WebSocket               │
  │  /api/model/train-model  │  Trigger DL training (background)        │
  │  /api/model/status       │  Training progress                        │
  │  /api/model/info         │  Model architecture + metrics             │
  │  /api/optimize           │  Standalone portfolio optimization        │
  │  /health                 │  Health check                             │
  │  /docs                   │  Swagger UI (dev mode only)               │
  └──────────────────────────┴───────────────────────────────────────────┘
```

### 9.2 Authentication Flow

```
  REGISTRATION FLOW (with OTP):
  ─────────────────────────────
  
  User submits form
      ↓
  POST /auth/register
      ├─ Pydantic validates: email (EmailStr), password (8+ chars, uppercase, special)
      ├─ Check no duplicate email
      ├─ Argon2id hash password → User(is_verified=False)
      ├─ Generate 6-digit OTP → store in Redis (TTL=10min)
      ├─ Send OTP email (SMTP/Gmail) OR return in dev_otp (dev mode)
      └─ Return: {message, email, dev_otp?}
      ↓
  POST /auth/verify-otp {email, otp}
      ├─ Fetch OTP from cache, check attempts (max 5)
      ├─ OTP match → User.is_verified = True
      ├─ Generate JWT: access_token (30min) + refresh_token (7 days)
      └─ Auto-login → redirect to /onboarding
  
  LOGIN FLOW:
  ──────────
  POST /auth/login → verify email + password + is_verified
      → create_access_token(sub=user_id) + create_refresh_token
      → Bearer tokens returned

  JWT Structure: HS256 | sub=user_id | exp | type=access|refresh
  Refresh: POST /auth/refresh → new access + refresh tokens (rotation)
  Guards: get_current_user() dependency → decode JWT → fetch user from DB
```

---

## 10. Frontend Architecture

### 10.1 Component Hierarchy

```
  App.jsx (React Router v7)
  │
  ├─ Navbar.jsx             (global navigation, auth state)
  ├─ Footer.jsx
  │
  ├── / Home.jsx            (landing, Three.js background)
  ├── /login Login.jsx      (JWT auth form)
  ├── /register Register.jsx (2-step: form + OTP verification boxes)
  │     ├─ Password strength meter (real-time checklist)
  │     ├─ OtpInput component (6 individual digit boxes, paste support)
  │     └─ Resend OTP (60s cooldown)
  │
  ├── /onboarding Onboarding.jsx (risk preference wizard)
  │
  ├── /dashboard Dashboard.jsx (protected)
  │     ├─ Market Overview (Finnhub sector data, real-time)
  │     ├─ Stats Grid (total value, return, invested, cash)
  │     ├─ Portfolio selector (multiple portfolios)
  │     ├─ PortfolioChart.jsx (real snapshots from DB)
  │     │     ├─ Area chart (Recharts)
  │     │     ├─ Green/red gradient (above/below cost basis)
  │     │     └─ Reference line at invested amount
  │     ├─ Holdings table (with signal badges)
  │     └─ AssetAllocation.jsx (donut chart by sector)
  │
  ├── /portfolio/:id Portfolio.jsx (protected)
  │     ├─ Overview tab: PortfolioChart + AssetAllocation
  │     ├─ Holdings tab: P&L table + Sell modal
  │     │     ├─ Per-stock: Symbol | Weight | Qty | Avg Cost | Current | Value | P&L | Signal | Action
  │     │     └─ Sell Modal: sell-all / by-quantity / by-amount
  │     ├─ AI Insights tab: market context + per-stock Claude reasoning
  │     └─ Performance tab: risk metrics + AI explanation
  │
  ├── /analysis Analysis.jsx (protected)
  │     ├─ Market indices (4 cards, Finnhub data)
  │     ├─ Search bar (US-stocks only filter)
  │     ├─ Deep Claude analysis display (7 sections, collapsible)
  │     │     ├─ Fundamental | Technical | Sentiment | Catalysts
  │     │     ├─ Risks | Valuation | Recommendation
  │     │     └─ Price target + analyst consensus
  │     └─ Popular stocks (click to analyse)
  │
  ├── /invest Invest.jsx (protected)
  │     ├─ Step 1: Investment amount (wallet balance check)
  │     ├─ Step 2: Risk profile selection
  │     ├─ Step 3: Review (AI processing notice)
  │     └─ AI Analysis Summary modal (after creation)
  │           ├─ Market context (what Claude saw)
  │           ├─ Expected return + Sharpe
  │           ├─ Per-stock Claude reasoning (scrollable)
  │           └─ Holdings chips (color-coded signals)
  │
  └── /deposit-withdraw DepositWithdraw.jsx (protected)
        ├─ 4 balance cards: available / deposited / withdrawn / invested
        ├─ Deposit / Withdraw tabs
        ├─ "Withdraw All" shortcut button
        └─ Transaction history (paginated)
```

### 10.2 State Management Architecture

```
  ┌────────────────────────────────────────────────────────────────┐
  │                    STATE MANAGEMENT                             │
  ├────────────────────────────────────────────────────────────────┤
  │                                                                 │
  │  Zustand (authStore.js)                                        │
  │  ─────────────────────                                         │
  │  { user, isAuthenticated }                                     │
  │  getToken()       → localStorage JWT access token              │
  │  getRefreshToken()→ localStorage JWT refresh token             │
  │  setTokens(a,r)   → persist both tokens                       │
  │  logout()         → clear state + localStorage                 │
  │                                                                 │
  │  Axios Interceptors (api.js)                                   │
  │  ──────────────────────────                                    │
  │  Request:  inject Authorization: Bearer {token}                │
  │  Response: on 401 → auto-refresh tokens → retry              │
  │            on refresh fail → logout() + /login redirect        │
  │                                                                 │
  │  Local component state (useState/useEffect):                   │
  │  ─────────────────────────────────────────                     │
  │  Portfolio page: selectedPortfolio, chartData, reasoning        │
  │  Dashboard:      portfolios, marketData, walletBalance          │
  │  Analysis:       stockAnalysis, searchResults, isAnalyzing      │
  │  Invest:         step, amount, riskProfile, aiResult (modal)   │
  └────────────────────────────────────────────────────────────────┘
```

---

## 11. Security & Authentication Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY ARCHITECTURE                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  1. PASSWORD SECURITY                                                                 │
│     Algorithm: Argon2id (memory-hard, GPU-resistant)                                 │
│     Policy: min 8 chars + 1 uppercase + 1 special char                              │
│     Validation: Pydantic field_validator → 422 with specific error message          │
│                                                                                       │
│  2. EMAIL VERIFICATION (OTP)                                                         │
│     6-digit OTP → stored in Redis (TTL=600s) with attempt counter (max 5)           │
│     Resend cooldown: 60 seconds (Redis TTL key)                                      │
│     SMTP: Gmail App Password (no plain password — only App Password)                 │
│     Dev mode: OTP in API response when SMTP not configured                           │
│                                                                                       │
│  3. JWT AUTHENTICATION                                                                │
│     Algorithm: HS256 signed with SECRET_KEY (32+ chars)                             │
│     Access token: 30 min TTL | sub=user_id | type=access                           │
│     Refresh token: 7 day TTL | sub=user_id | type=refresh                          │
│     Rotation: every refresh call issues new access + refresh tokens                  │
│     Type check: refresh tokens CANNOT be used as access tokens                      │
│                                                                                       │
│  4. CORPORATE PROXY COMPATIBILITY                                                     │
│     truststore.inject_into_ssl() called at app startup (main.py)                   │
│     → Patches Python ssl module to use OS native cert store                         │
│     → Enables Claude, Finnhub, NewsAPI, AV calls through TLS inspection proxy      │
│     Defensive: stripped from SMTP password (removes spaces from App Password)        │
│                                                                                       │
│  5. API SECURITY                                                                      │
│     CORS: configured for localhost:5173/5174 + production origins                   │
│     SQL injection: prevented by SQLAlchemy ORM parameterized queries                │
│     XSS: React JSX auto-escapes all rendered content                                │
│     Secrets: .env excluded from git (.gitignore), never logged                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Real-Time Data Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         REAL-TIME DATA FLOW                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  MARKET DATA (Finnhub API — every request):                                          │
│  ─────────────────────────────────────────                                           │
│  Quotes:   /api/v1/quote   → { c, d, dp, h, l, o, pc, t }                         │
│  Overview: Sector ETFs (XLK,XLF,...) + SPY,QQQ,IWM → sector performance           │
│  Recs:     /stock/recommendation → analyst vote counts                              │
│  News:     /news + /company-news → headlines for Claude + sentiment                 │
│  Search:   /search → symbol matching (US-only filter applied frontend)              │
│                                                                                       │
│  CACHING STRATEGY (Redis when available, in-memory NoopCache as fallback):          │
│  ─────────────────────────────────────────────────────────────────────────          │
│  Finnhub quotes:    TTL=60s     (fresh enough for portfolio decisions)               │
│  Market overview:   TTL=300s    (5 min, prevents Finnhub rate-limit)                │
│  Claude responses:  TTL=3600s   (1 hour, same query → same answer)                 │
│  OTP codes:         TTL=600s    (10 min, single-use after verification)             │
│                                                                                       │
│  AUTO-REFRESH SYSTEM:                                                                 │
│  ───────────────────                                                                  │
│  Portfolio page load → silentRefreshPrices(portfolio_id)                             │
│    → POST /portfolios/{id}/refresh                                                   │
│    → Fetch all stock holdings' current_price from Finnhub                           │
│    → Update each holding.current_price, holding.market_value                        │
│    → Recalculate portfolio.total_value = Σ(market_values)                           │
│    → Write PortfolioSnapshot (new chart data point)                                  │
│    → Silent UI update (no spinner)                                                   │
│                                                                                       │
│  Dashboard: Auto-refresh every 5 minutes (setInterval)                               │
│  Portfolio: Auto-refresh on load + every 5 minutes (setInterval)                     │
│  Portfolio switch: Immediate refresh on portfolio selection                           │
│                                                                                       │
│  PORTFOLIO CHART DATA (real time-series, not mock):                                  │
│  ─────────────────────────────────────────────────                                   │
│  GET /portfolios/{id}/chart → portfolio_snapshots table                              │
│  → List of {date, total_value} sorted by created_at                                 │
│  → New snapshot written on every price refresh                                        │
│  → Displayed as area chart (green above cost, red below)                            │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Mathematical Formulations

### Portfolio Theory

$$E[R_p] = \boldsymbol{\mu}^T \mathbf{w} \qquad \sigma_p = \sqrt{\mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}}$$

$$\Sigma_{ij} = \sigma_i \cdot \sigma_j \cdot \rho_{ij} \qquad S = \frac{E[R_p] - R_f}{\sigma_p}, \quad R_f = 2\%$$

$$\text{VaR}_{95} = \sigma_p \times 1.645 - E[R_p] \qquad \text{CVaR}_{95} = \sigma_p \times 2.063 - E[R_p]$$

$$\text{DR} = \frac{\sum_i w_i \sigma_i}{\sigma_p} \geq 1 \qquad \text{HHI} = \sum_i w_i^2 \in \left[\frac{1}{n}, 1\right]$$

### DL Model Equations

**TFT Variable Selection:**
$$\hat{z} = \sum_i \alpha_i \cdot \text{GRN}_i(x_i), \quad \alpha = \text{softmax}(\text{GRN}(\text{flatten}(x))) \in \mathbb{R}^F$$

**Gated Residual Network:**
$$\text{GRN}(x) = \text{LayerNorm}\left(\text{GLU}(\text{FC}_2(\text{ELU}(\text{FC}_1(x)))) + \text{skip}(x)\right)$$

**Temporal Self-Attention:**
$$\text{Attn}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V, \quad Q=K=V=h_{\text{skip}}$$

**N-BEATS Doubly-Residual:**
$$\text{residual}_{i+1} = \text{residual}_i - \text{backcast}_i, \quad \hat{y} = \sum_{i=1}^{B} \text{forecast}_i$$

**Ensemble:**
$$\hat{r} = \text{softmax}(\mathbf{l})^T \begin{bmatrix}f_{\text{TFT}}(x) \\ f_{\text{LSTM}}(x) \\ f_{\text{NBEATS}}(x)\end{bmatrix}, \quad \mathbf{l} \in \mathbb{R}^3 \text{ (learned)}$$

**Huber Loss (Training Objective):**
$$\mathcal{L}(y, \hat{y}) = \begin{cases} \frac{1}{2}(y-\hat{y})^2 & |y-\hat{y}| \leq \delta \\ \delta\left(|y-\hat{y}| - \frac{\delta}{2}\right) & \text{otherwise} \end{cases}, \quad \delta = 0.05$$

---

## 14. Technology Stack

### Backend

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Web Framework | FastAPI | 0.109.0 | Async REST API |
| Server | Uvicorn | 0.27.0 | ASGI production server |
| Deep Learning | PyTorch | 2.11.0 | TFT, LSTM, N-BEATS models |
| ML | scikit-learn | 1.8.0 | RF + GB fallback ensemble |
| ML Persistence | joblib | 1.5.3 | sklearn model serialization |
| ORM | SQLAlchemy | 2.0.25 | Async database access |
| DB (Dev) | SQLite + aiosqlite | 0.20.0 | Zero-install local development |
| DB (Prod) | PostgreSQL + asyncpg | 0.29.0 | Production persistence |
| Migrations | Alembic | 1.13.1 | Schema versioning |
| Cache | Redis → NoopCache | 5.0.1 | Quote/response caching |
| Auth | python-jose + passlib | 3.3.0 | JWT + Argon2id hashing |
| LLM (Analysis) | anthropic (Sonnet) | 0.96.0 | Deep stock analysis |
| LLM (Selection) | anthropic (Sonnet) | 0.96.0 | Stock universe generation |
| LLM (Reasoning) | anthropic (Haiku) | 0.96.0 | Per-stock reasoning |
| HTTP Client | httpx | 0.26.0 | Async external API calls |
| Data | pandas, numpy, scipy | latest | Numerical computing |
| Logging | loguru | 0.7.2 | Structured logging |
| Validation | pydantic + pydantic-settings | 2.5.3 | Schema validation |
| SSL Fix | truststore | 0.10.4 | Corporate proxy CA injection |

### Frontend

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| UI Framework | React | 19.2.0 | Declarative component UI |
| Build | Vite | 7.2.4 | Fast bundler + HMR |
| Routing | react-router-dom | 7.1.0 | Client-side routing |
| State | Zustand | 5.0.2 | Lightweight JWT + user state |
| HTTP | Axios | 1.7.9 | Interceptors + auto-refresh |
| Charts | Recharts | 2.15.0 | Area/Pie charts (real data) |
| Animation | Framer Motion | 11.15.0 | Page transitions + modals |
| 3D | Three.js + R3F | 0.171.0 | Background animations |
| Icons | Lucide React | 0.469.0 | SVG icon system |
| Styling | Tailwind CSS | 3.4.17 | Utility-first CSS |
| Feedback | react-hot-toast | 2.5.1 | User notifications |

### External APIs

| API | Provider | Tier | Data |
|---|---|---|---|
| LLM (Sonnet) | Anthropic | Paid | Stock analysis, portfolio reasoning, market summary |
| LLM (Haiku) | Anthropic | Paid | Stock selection, per-stock reasoning, summaries |
| Market Quotes | Finnhub | Free | Real-time OHLCV, daily change, company profiles |
| Analyst Consensus | Finnhub | Free | Buy/hold/sell vote counts |
| Financial Metrics | Finnhub | Free | P/E, P/B, ROE, beta, debt/equity |
| Sector ETFs | Finnhub | Free | XLK/XLF/XLV/... daily performance |
| Market News | Finnhub | Free | Company + general market headlines |
| Historical OHLCV | Alpha Vantage | Free | 100-day daily data (DL training) |
| Financial News | NewsAPI | Free | Cross-source financial headlines for Claude |

---

## 15. Performance & Model Metrics

### DL Model Architecture Summary

```
┌───────────────┬───────────┬────────────┬────────────────────────────────────────┐
│ Model         │ Params    │ Size       │ Architecture                           │
├───────────────┼───────────┼────────────┼────────────────────────────────────────┤
│ TFT           │ 366,412   │ 1.47 MB    │ VSN + GRN + LSTM + Temporal Attention  │
│ LSTM-Attention│ 341,249   │ 1.34 MB    │ BiLSTM × 2 + Multi-Head Self-Attention │
│ N-BEATS       │ 1,242,996 │ 4.87 MB    │ 4 Blocks × FC-256 + Doubly-Residual   │
│ Ensemble      │ 1,950,660 │ 7.69 MB    │ Learned mix: TFT + LSTM + N-BEATS      │
└───────────────┴───────────┴────────────┴────────────────────────────────────────┘

Training Configuration:
  Data:        25 stocks × 100 days × sliding window = ~2,000 sequences
  Features:    11-dimensional technical feature vector per timestep
  Seq length:  20 trading days
  Horizon:     5-day forward cumulative log return
  Loss:        Huber (δ=0.05) — robust to outlier returns
  Optimizer:   AdamW (lr=1e-3, weight_decay=1e-4)
  Scheduler:   CosineAnnealingLR
  Training:    ~15 min on CPU (data download ~6 min + training ~9 min)
```

### System Performance

```
Portfolio Creation:   16-36 seconds (Claude Sonnet + DL inference + optimization)
  Layer 1 (Claude):  5-8 seconds
  Layer 2 (DL):      5-10 seconds
  Layer 3 (optim):   0.1 seconds
  Reasoning:         3-5 seconds

Deep Stock Analysis: 15-30 seconds (Claude Sonnet 7-section report)
Market Overview:     1-2 seconds (11 parallel Finnhub calls)
Price Refresh:       2-3 seconds (batch Finnhub quotes)
OTP Email:           <3 seconds (SMTP via Gmail App Password)
```

---

## 16. Setup & Installation

### Prerequisites

| Tool | Min Version |
|---|---|
| Python | 3.12 |
| Node.js | 18+ |

### Quick Start

```bash
# 1. Clone
git clone https://github.com/planav/ai-auto-investment.git
cd ai-auto-investment

# 2. Backend setup
cd backend
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt   # Windows
# source venv/bin/activate && pip install -r requirements.txt  # Mac/Linux

# 3. Configure secrets
cp .env.example .env
# Edit .env — add your API keys (Anthropic, Finnhub, NewsAPI, Alpha Vantage)

# 4. Database setup
venv\Scripts\python.exe -m alembic upgrade head

# 5. Start backend
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Frontend setup (new terminal)
cd ../frontend/web
npm install
npm run dev

# 7. Trigger DL model training (runs in background ~15 min)
curl -X POST http://localhost:8000/api/model/train-model

# 8. Check training status
curl http://localhost:8000/api/model/status
```

### Access Points

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| Model Status | http://localhost:8000/api/model/status |
| Model Info | http://localhost:8000/api/model/info |

### Required API Keys

| API | Free Tier | Register |
|---|---|---|
| Anthropic Claude | Pay-per-use | console.anthropic.com |
| Finnhub | 60 req/min | finnhub.io/register |
| Alpha Vantage | 25 req/day | alphavantage.co/support/#api-key |
| NewsAPI | 1,000 req/day | newsapi.org/register |

### Database Access

```bash
# Via SQLite browser (GUI — recommended)
# Download: https://sqlitebrowser.org/
# Open: backend/autoinvest.db

# Via Python
cd backend
venv\Scripts\python.exe -c "
import sqlite3
conn = sqlite3.connect('autoinvest.db')
print([t[0] for t in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()])
"

# Via Alembic CLI
venv\Scripts\python.exe -m alembic current   # current schema version
venv\Scripts\python.exe -m alembic history   # migration history
venv\Scripts\python.exe -m alembic upgrade head   # apply pending migrations
```

### Restart Commands

```bash
# Kill all processes
taskkill /F /IM python.exe /T    # Windows
pkill -f uvicorn                   # Mac/Linux

taskkill /F /IM node.exe /T      # Windows
pkill -f vite                      # Mac/Linux

# Start backend
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start frontend
cd frontend/web
npm run dev
```

---

## 17. API Reference

### Portfolio Endpoints

```
POST   /api/v1/portfolios/                    → Create AI portfolio (3-layer)
GET    /api/v1/portfolios/                    → List all user portfolios
GET    /api/v1/portfolios/{id}                → Full portfolio with holdings
PUT    /api/v1/portfolios/{id}                → Update name/description
DELETE /api/v1/portfolios/{id}                → Delete portfolio
GET    /api/v1/portfolios/{id}/chart          → Time-series chart data
POST   /api/v1/portfolios/{id}/refresh        → Refresh live prices (Finnhub)
GET    /api/v1/portfolios/{id}/reasoning      → Claude per-stock reasoning
GET    /api/v1/portfolios/{id}/performance    → Sharpe, VaR, drawdown metrics
POST   /api/v1/portfolios/{id}/rebalance      → Drift detection + recommendations
POST   /api/v1/portfolios/{id}/sell           → Sell holding (qty/amount/all)
POST   /api/v1/portfolios/{id}/holdings       → Add manual holding
```

### Analysis Endpoints

```
GET    /api/v1/analysis/stock/{symbol}        → Full Claude Sonnet analysis (7 sections)
POST   /api/v1/analysis/assets                → Bulk ML signals for stock list
GET    /api/v1/analysis/signals/{symbol}      → Quick DL signal for one stock
GET    /api/v1/analysis/explain/{portfolio_id}→ Portfolio allocation reasoning
POST   /api/v1/analysis/backtest              → Historical backtest (Alpha Vantage)
GET    /api/v1/analysis/models                → Available model descriptions
```

### Model Management

```
POST   /api/model/train-model                 → Trigger DL training (background)
GET    /api/model/status                      → Training progress + results
GET    /api/model/info                        → Architecture + parameter counts
```

---

## 18. Academic References

### Portfolio Theory
1. **Markowitz, H.** (1952). Portfolio Selection. *The Journal of Finance*, 7(1), 77–91.
2. **Sharpe, W.F.** (1964). Capital Asset Prices. *The Journal of Finance*, 19(3), 425–442.
3. **Maillard, S., Roncalli, T. & Teïletche, J.** (2010). Properties of Equally Weighted Risk Contribution Portfolios. *Journal of Portfolio Management*, 36(4), 60–70.

### Deep Learning for Time Series
4. **Lim, B., Arık, S.Ö., Loeff, N. & Pfister, T.** (2021). Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting. *International Journal of Forecasting*, 37(4), 1748–1764.
5. **Oreshkin, B.N., Carpov, D., Chapados, N. & Bengio, Y.** (2020). N-BEATS: Neural Basis Expansion Analysis for Interpretable Time Series Forecasting. *ICLR 2020*. arXiv:1905.10437.
6. **Vaswani, A., et al.** (2017). Attention Is All You Need. *NeurIPS 2017*. arXiv:1706.03762.
7. **Hochreiter, S. & Schmidhuber, J.** (1997). Long Short-Term Memory. *Neural Computation*, 9(8), 1735–1780.

### LLMs in Finance
8. **Lopez-Lira, A. & Tang, Y.** (2023). Can ChatGPT Forecast Stock Price Movements? *SSRN Working Paper*. https://ssrn.com/abstract=4412788
9. **Koa, K.X., et al.** (2024). Learning to Generate Explainable Stock Predictions using Self-Reflective LLMs. arXiv:2402.03190.

### Quantitative Finance
10. **Gu, S., Kelly, B. & Xiu, D.** (2020). Empirical Asset Pricing via Machine Learning. *The Review of Financial Studies*, 33(5), 2223–2273.
11. **Lopez de Prado, M.** (2018). *Advances in Financial Machine Learning*. Wiley.
12. **D'Acunto, F., Prabhala, N. & Rossi, A.G.** (2019). The Promises and Pitfalls of Robo-Advising. *The Review of Financial Studies*, 32(5), 1983–2020.

---

<div align="center">

**Built with PyTorch · Claude Sonnet · FastAPI · React 19**

*AutoInvest — Where Deep Learning Meets Quantitative Finance*

**Research Team:** AutoInvest AI Research Initiative | Aurigo Software Technologies Inc.
**Contact:** v-pranav.h@aurigo.com | April 2026

</div>
