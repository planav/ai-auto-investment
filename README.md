# AutoInvest: An Intelligent Three-Layer AI-Driven Automated Portfolio Management System

> **A production-grade research prototype demonstrating the integration of Large Language Models, Ensemble Machine Learning, and Modern Portfolio Theory for autonomous investment portfolio generation, optimization, and management.**

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Introduction & Motivation](#2-introduction--motivation)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Technology Stack](#4-technology-stack)
5. [Three-Layer AI Pipeline](#5-three-layer-ai-pipeline)
6. [Machine Learning Models](#6-machine-learning-models)
7. [Portfolio Optimization Algorithms](#7-portfolio-optimization-algorithms)
8. [Risk Management Framework](#8-risk-management-framework)
9. [Database Architecture & Data Models](#9-database-architecture--data-models)
10. [Backend API Reference](#10-backend-api-reference)
11. [External Data Sources & APIs](#11-external-data-sources--apis)
12. [Frontend Architecture](#12-frontend-architecture)
13. [AI Analysis System (Claude Sonnet)](#13-ai-analysis-system-claude-sonnet)
14. [Research Agent System](#14-research-agent-system)
15. [Security Architecture](#15-security-architecture)
16. [Deployment & Infrastructure](#16-deployment--infrastructure)
17. [Mathematical Formulations](#17-mathematical-formulations)
18. [Experimental Results & Sample Outputs](#18-experimental-results--sample-outputs)
19. [Limitations & Future Work](#19-limitations--future-work)
20. [Setup & Installation](#20-setup--installation)
21. [References & Related Work](#21-references--related-work)

---

## 1. Abstract

AutoInvest is a research prototype that demonstrates the feasibility of end-to-end autonomous investment portfolio management using a novel three-layer artificial intelligence architecture. The system integrates **Large Language Model (LLM) reasoning** for market-aware stock universe selection, **ensemble machine learning** for quantitative scoring of individual securities, and **classical portfolio optimization theory** for weight allocation, all connected through a production-grade REST API and interactive web interface.

The core contribution is a **three-layer pipeline** where:
- **Layer 1 (LLM Intelligence):** Anthropic Claude analyzes real-time market news (NewsAPI, Finnhub) to identify sector trends and recommend a universe of 40–60 candidate stocks tailored to the user's risk profile.
- **Layer 2 (ML Scoring):** A trained sklearn ensemble (RandomForest + GradientBoosting) scores each candidate using 8 Finnhub-derived features (momentum, analyst consensus, sector momentum, volatility) to produce a ranked shortlist of 10 securities.
- **Layer 3 (Optimization + Reasoning):** Markowitz mean-variance optimization allocates portfolio weights subject to diversification constraints, with Claude generating per-stock natural language reasoning for the allocation decisions.

The system achieves:
- Real-time portfolio creation in **4–32 seconds** using live market data
- Complete integration with **Finnhub, Alpha Vantage, and NewsAPI** for live financial data
- Comprehensive risk metrics: **Sharpe Ratio, VaR₉₅, CVaR₉₅, Sortino Ratio, Max Drawdown**
- User-facing natural language explanations for every investment decision
- Full-stack web application with user authentication, wallet management, and portfolio tracking

---

## 2. Introduction & Motivation

### 2.1 Problem Statement

Traditional investment portfolio management suffers from several limitations:
1. **Information overload:** Thousands of securities, real-time news, earnings reports, and macro signals are impossible for individual investors to process
2. **Behavioral biases:** Human investors exhibit loss aversion, anchoring bias, and herd mentality
3. **Access inequality:** Sophisticated quantitative strategies are available only to institutional investors
4. **Slow adaptation:** Manual portfolio adjustment cannot keep pace with market dynamics

### 2.2 Research Hypothesis

We hypothesize that combining LLM-based semantic analysis of financial news with traditional quantitative methods can produce portfolio recommendations that are simultaneously:
- **Data-driven:** Based on real market data, not random allocation
- **Risk-aware:** Subject to user-defined risk tolerance constraints
- **Explainable:** Supported by natural language justifications
- **Diverse:** Not subject to single-model overfitting

### 2.3 Key Research Questions

1. Can LLMs effectively screen investment universes from natural language market news?
2. Can a lightweight sklearn ensemble outperform random allocation on short-term momentum signals?
3. Does combining LLM selection + ML scoring + classical optimization improve portfolio diversity vs. any single approach?
4. Can natural language reasoning generation increase user trust in AI-generated portfolios?

### 2.4 Novel Contributions

1. **Three-layer heterogeneous AI architecture** for portfolio construction
2. **LLM-based stock universe selection** from real-time news (first application of Claude for investment universe generation)
3. **Hybrid explainability system** — both mathematical (feature importance) and narrative (Claude reasoning)
4. **Production-grade implementation** with live market data, user authentication, and real portfolio tracking

---

## 3. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTOINVEST SYSTEM ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                    REACT 19 + VITE FRONTEND                           │   │
│   │  Dashboard │ Portfolio │ Analysis │ Invest │ DepositWithdraw          │   │
│   │  PortfolioChart (Recharts) │ AssetAllocation │ MarketTicker           │   │
│   │  Zustand State │ TanStack Query │ Axios HTTP Client                   │   │
│   └──────────────────────────┬───────────────────────────────────────────┘   │
│                               │ HTTP/REST                                     │
│   ┌──────────────────────────▼───────────────────────────────────────────┐   │
│   │              FASTAPI 0.109 BACKEND (async ASGI / Uvicorn)             │   │
│   │                                                                        │   │
│   │  ┌─────────────────────────────────────────────────────────────────┐  │   │
│   │  │                     API LAYER (v1)                               │  │   │
│   │  │  /auth  /users  /portfolios  /analysis  /market  /wallet  /dash │  │   │
│   │  └──────────────────────────┬──────────────────────────────────────┘  │   │
│   │                              │                                          │   │
│   │  ┌───────────────────────────────────────────────────────────────────┐ │   │
│   │  │                    3-LAYER AI PIPELINE                             │ │   │
│   │  │                                                                     │ │   │
│   │  │  Layer 1: Claude AI (Haiku)        ←── NewsAPI + Finnhub News     │ │   │
│   │  │           ↓ 40-60 candidate stocks                                 │ │   │
│   │  │  Layer 2: sklearn Ensemble         ←── Finnhub Real-time Quotes   │ │   │
│   │  │           ↓ Top 10 ranked stocks                                   │ │   │
│   │  │  Layer 3: Markowitz/Risk-Parity    ←── Empirical Covariance       │ │   │
│   │  │           ↓ Optimal weights + Claude Reasoning                     │ │   │
│   │  └───────────────────────────────────────────────────────────────────┘ │   │
│   │                                                                          │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │   │
│   │  │  SQLAlchemy  │  │   Redis      │  │  sklearn     │                  │   │
│   │  │  AsyncORM    │  │   Cache      │  │  Joblib      │                  │   │
│   │  └──────┬───────┘  └──────────────┘  └──────────────┘                  │   │
│   └─────────┼────────────────────────────────────────────────────────────┘   │
│             │                                                                  │
│   ┌─────────▼──────────────────────────────────────────────────────────────┐  │
│   │         SQLite (Dev) / PostgreSQL (Production)                          │  │
│   │  users │ portfolios │ portfolio_holdings │ portfolio_snapshots           │  │
│   │  wallets │ wallet_transactions │ portfolio_transactions                  │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│   External APIs: Finnhub │ Alpha Vantage │ NewsAPI │ Anthropic Claude          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Component Interaction Flow

```
User Action: "Create Aggressive Portfolio — $10,000"
     │
     ▼
[1] Wallet Service → Check & deduct balance ($10,000)
     │
     ▼
[2] Layer 1 — AI Stock Selector (ai_stock_selector.py)
    ├── Fetch NewsAPI headlines (30 articles, last 48h)
    ├── Fetch Finnhub market news (20 articles)
    ├── Claude Haiku: "Top sectors: AI/Semis, Cybersecurity, Cloud"
    └── Returns 40-60 stocks with reasons & conviction levels
     │
     ▼
[3] Layer 2 — ML Scoring Engine (ml_engine/predictor.py)
    ├── Fetch Finnhub quotes for all 40-60 candidates (PARALLEL)
    ├── Fetch analyst recommendations (PARALLEL)
    ├── Compute sector momentum per sector group
    ├── Extract 8-feature vector per stock
    ├── RandomForest prediction (55% weight)
    ├── GradientBoosting prediction (45% weight)
    ├── Ensemble: predicted_return, confidence, ml_score
    └── Select Top 10 by ml_score
     │
     ▼
[4] Layer 3 — Portfolio Optimization (portfolio_engine/allocation.py)
    ├── Apply risk-profile return floors (aggressive: 9% minimum)
    ├── Build empirical covariance matrix (sector correlations)
    ├── Mean-variance optimization (λ_aggressive = 1.0)
    ├── Apply constraints: min 3%, max 25% per stock
    └── Compute: E[R], σ, Sharpe, VaR₉₅, CVaR₉₅
     │
     ▼
[5] Reasoning & Persistence
    ├── Claude generates per-stock reasoning (why each stock)
    ├── Claude generates portfolio narrative
    ├── Create PortfolioHolding records in DB
    ├── Write PortfolioSnapshot for chart history
    └── Return complete PortfolioResponse
     │
     ▼
User sees: Real stocks, real prices, real weights, AI reasoning (~4-32 seconds)
```

---

## 4. Technology Stack

### 4.1 Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | FastAPI | 0.109.0 | Async REST API |
| Server | Uvicorn | 0.27.0 | ASGI server |
| ORM | SQLAlchemy | 2.0.25 | Async database access |
| Database (Dev) | SQLite + aiosqlite | 0.20.0 | Local development |
| Database (Prod) | PostgreSQL + asyncpg | 0.29.0 | Production |
| Migrations | Alembic | 1.13.1 | Schema versioning |
| Cache | Redis | 5.0.1 | Quote & response caching |
| Auth | python-jose + passlib | 3.3.0 / 1.7.4 | JWT + Argon2 hashing |
| ML | scikit-learn | 1.8.0 | RF + GB ensemble |
| ML Persistence | joblib | 1.5.3 | Model serialization |
| Data | pandas, numpy, scipy | 2.2.2 / latest | Numerical computing |
| HTTP Client | httpx | 0.26.0 | Async external API calls |
| LLM | anthropic | 0.96.0 | Claude AI integration |
| Logging | loguru | 0.7.2 | Structured logging |
| Monitoring | prometheus-client | 0.19.0 | Metrics export |
| Validation | pydantic + pydantic-settings | 2.5.3 / 2.1.0 | Schema validation |
| SSL Proxy Fix | truststore | 0.10.4 | Corporate CA injection |
| Tasks | celery + schedule | 5.3.6 / 1.2.1 | Background jobs |

### 4.2 Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| UI Framework | React | 19.2.0 | Declarative UI |
| Build Tool | Vite | 7.2.4 | Fast bundling & HMR |
| Routing | react-router-dom | 7.1.0 | Client-side routing |
| State | Zustand | 5.0.2 | Lightweight global state |
| Data Fetching | @tanstack/react-query | 5.62.0 | Server state management |
| HTTP | Axios | 1.7.9 | Interceptors & auto-refresh |
| Charts | Recharts | 2.15.0 | Area/line/pie charts |
| 3D | Three.js + R3F | 0.171.0 | Background animations |
| Animation | Framer Motion | 11.15.0 | Page transitions |
| Icons | Lucide React | 0.469.0 | SVG icon system |
| Styling | Tailwind CSS | 3.4.17 | Utility-first CSS |
| Notifications | react-hot-toast | 2.5.1 | User feedback toasts |

### 4.3 AI & Data APIs

| Service | Provider | Used For |
|---------|---------|---------|
| LLM — Haiku | Anthropic Claude | Stock selection, portfolio reasoning |
| LLM — Sonnet | Anthropic Claude | Deep stock analysis (full research) |
| Market Quotes | Finnhub (Free) | Real-time OHLCV, daily change |
| Company Data | Finnhub (Free) | Profiles, fundamentals, analyst recommendations |
| Financial Metrics | Finnhub (Free) | P/E, P/B, ROE, beta, debt/equity |
| Market News | Finnhub (Free) | Company-specific and general news |
| Historical Data | Alpha Vantage (Free) | Daily OHLCV for backtesting |
| Market News | NewsAPI (Free) | Cross-source financial news headlines |
| Stock Search | Finnhub (Free) | Symbol search and matching |

---

## 5. Three-Layer AI Pipeline

The core innovation of AutoInvest is its heterogeneous three-layer AI pipeline that combines fundamentally different approaches to arrive at a robust, explainable portfolio.

### 5.1 Layer 1 — Claude AI Stock Intelligence

**File:** `backend/app/services/ai_stock_selector.py`  
**Function:** `select_stocks_with_ai(risk_profile, investment_horizon_months)`

#### News Aggregation

Two sources are fetched concurrently using `asyncio.gather`:

```python
news_api, finnhub_news = await asyncio.gather(
    _fetch_market_news(client),         # NewsAPI: 30 articles, last 48h
    _fetch_finnhub_market_news(client), # Finnhub: 20 articles, general
    return_exceptions=True,
)
```

Headlines are condensed to 15 most relevant (title + 100 chars of description).

#### Claude Stock Selection

```
Model:       claude-haiku-4-5-20251001
Temperature: 0.8  (promotes varied selections across runs)
Max tokens:  2048
```

The prompt includes:
1. **Current date + random variation seed** (1000–9999) — forces different output on each invocation
2. **15 market news headlines** from last 48 hours
3. **Risk-profile guidelines** (conservative / moderate / aggressive)
4. **Output schema** requiring structured JSON with conviction levels (`high|medium|low`)

**Output schema:**
```json
{
  "market_context": "2-3 sentence market summary",
  "top_sectors": ["Technology", "Healthcare"],
  "sector_reasoning": "Why these sectors are favoured now",
  "stocks": [
    { "symbol": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology",
      "reason": "AI chip monopoly, hyperscaler demand", "conviction": "high" }
  ]
}
```

**Risk-Profile Stock Guidelines:**

| Profile | Focus | Avoid |
|---------|-------|-------|
| Conservative | Dividend aristocrats, defensive sectors (Staples/Healthcare/Utilities), broad/bond ETFs | High-volatility, speculative, early-stage |
| Moderate | Quality large-cap growth, established tech, financials, industrials | Speculative micro-cap, crypto-adjacent |
| Aggressive | High-growth tech, AI/ML, semiconductors, EV, momentum plays, mid-cap leaders | Investment-grade bonds, defensive utilities |

**Fallback Universe** (when Claude / APIs unavailable):

| Risk | Fallback Stocks (10) |
|------|---------------------|
| Conservative | SPY, VTI, BND, GLD, SCHD, JNJ, KO, PG, NEE, VNQ |
| Moderate | AAPL, MSFT, GOOGL, AMZN, NVDA, SPY, QQQ, JPM, UNH, V |
| Aggressive | NVDA, AMD, TSLA, MSFT, CRWD, SHOP, PLTR, COIN, NET, MELI |

### 5.2 Layer 2 — Ensemble ML Scoring Engine

**File:** `backend/app/engines/ml_engine/predictor.py`

#### Feature Engineering

Eight features extracted from live Finnhub data per stock:

| # | Feature | Formula | Economic Meaning |
|---|---------|---------|-----------------|
| 1 | `daily_change_pct` | `quote.dp` | Today's price momentum |
| 2 | `intraday_ratio` | `close / open` | Intraday buying pressure |
| 3 | `high_low_range` | `(high - low) / prev_close` | Intraday volatility |
| 4 | `analyst_score` | `(strongBuy×2 + buy - sell - strongSell×2) / (total×2)` | Analyst consensus [-1,+1] |
| 5 | `analyst_coverage` | Count of analysts | Institutional attention |
| 6 | `sector_momentum` | `mean(dp for peers in sector)` | Relative sector strength |
| 7 | `vol_estimate` | Known annual volatility | Risk level proxy |
| 8 | `price_level` | `log₁₀(price)` | Market cap proxy |

#### Model Architecture

**RandomForest Pipeline (55% weight):**
```python
Pipeline([
    ("scaler", StandardScaler()),
    ("rf", RandomForestRegressor(
        n_estimators=200, max_depth=8,
        min_samples_leaf=10, n_jobs=-1, random_state=42
    ))
])
```

**GradientBoosting Pipeline (45% weight):**
```python
Pipeline([
    ("scaler", StandardScaler()),
    ("gb", GradientBoostingRegressor(
        n_estimators=200, max_depth=4,
        learning_rate=0.05, subsample=0.8, random_state=42
    ))
])
```

**Ensemble Prediction:**
```python
predicted_return = 0.55 * rf_pipeline.predict(features)[0] \
                 + 0.45 * gb_pipeline.predict(features)[0]
```

#### Training Data

3,000 synthetic samples with known financial patterns:
```python
base_return = (
    dp        * 0.015 +  # Momentum carries forward (~1.5% per 1% daily move)
    analyst_s * 0.08  +  # Analyst consensus predicts forward returns
    sector_m  * 0.010 +  # Sector tailwind contributes ~1% per 1% sector move
    noise(μ=0, σ=0.04)   # Market noise
)
target = clip(base_return, -0.30, +0.35)  # Realistic 30-day return bounds
```

#### Scoring & Signal Classification

```python
# Confidence
confidence = min(0.90, 0.55 + |predicted_return|*1.5 + 0.10*(direction_agree))

# ML score normalization
ml_score = (raw - min_raw) / (max_raw - min_raw) * 100

# Signal mapping
strong_buy  : predicted_return >= 12%
buy         : predicted_return >= 4%
hold        : predicted_return in [-4%, +4%)
sell        : predicted_return in [-12%, -4%)
strong_sell : predicted_return < -12%
```

Top 10 stocks by `ml_score` advance to Layer 3.

#### Model Persistence

```
backend/app/engines/ml_engine/saved_models/
├── rf_momentum.joblib     # RandomForest pipeline
└── gb_quality.joblib      # GradientBoosting pipeline
```

Lazy-loaded on first inference, cached in memory for subsequent requests.

### 5.3 Layer 3 — Portfolio Optimization & Claude Reasoning

**Files:** `backend/app/engines/portfolio_engine/allocation.py`, `engine.py`

#### Return Floor Application

Prevents daily noise from producing unrealistically low expected returns:

```python
RETURN_FLOORS = {"conservative": 0.04, "moderate": 0.06, "aggressive": 0.09}
predictions = {s: max(floor, ml_scores[s]["predicted_return"]) for s in selected}
```

#### Empirical Covariance Matrix

```
Σᵢⱼ = σᵢ × σⱼ × ρ(sector_i, sector_j)
```

**Known Annual Volatilities (σ):**

| Asset Type | Examples | σ |
|---|---|---|
| Blue-chip tech | AAPL, MSFT | 28–30% |
| Growth tech | NVDA, AMD | 50–55% |
| High-momentum | TSLA, CRWD | 50–65% |
| Speculative | COIN, PLTR | 65–80% |
| Broad ETFs | SPY, VTI | 17% |
| Bond ETFs | BND, AGG | 4–6% |

**Empirical Sector Correlations (ρ):**

| | Tech | Consumer | Finance | Healthcare | Broad ETF | Bond |
|--|--|--|--|--|--|--|
| **Tech** | 0.75 | 0.60 | 0.50 | 0.40 | 0.85 | −0.10 |
| **Consumer** | 0.60 | 0.65 | 0.55 | 0.42 | 0.82 | −0.10 |
| **Finance** | 0.50 | 0.55 | 0.70 | 0.45 | 0.82 | +0.10 |
| **Healthcare** | 0.40 | 0.42 | 0.45 | 0.65 | 0.78 | −0.05 |
| **Broad ETF** | 0.85 | 0.82 | 0.82 | 0.78 | 0.95 | −0.10 |
| **Bond** | −0.10 | −0.10 | +0.10 | −0.05 | −0.10 | 0.90 |

#### Portfolio Constraints

```python
PortfolioConstraints(
    min_weight   = 0.03,   # Minimum 3% (meaningful position)
    max_weight   = 0.25,   # Maximum 25% (concentration limit)
    cash_reserve = 0.05,   # 5% liquid buffer
)
```

---

## 6. Machine Learning Models

### 6.1 sklearn Ensemble (Implemented & Operational)

The RF + GB ensemble is trained at startup if no saved models exist, and persisted via `joblib`. Training takes ~15 seconds on a modern CPU.

**Inference pipeline:**
```
Finnhub Quote + Rec → Feature Extraction (8-dim) → StandardScaler
                    → RandomForest.predict() ×0.55
                    → GradientBoosting.predict() ×0.45
                    → Ensemble score → Signal classification → Portfolio input
```

### 6.2 Deep Learning Model Abstractions (Configured, Architecture Ready)

Five DL architectures have full configuration schemas in `engines/quant_engine/models.py`. The runtime currently routes through the sklearn ensemble as the prediction backend, with the architecture designed to plug in PyTorch implementations.

| Model | Architecture | Input Seq | Hidden | Heads | Best For |
|---|---|---|---|---|---|
| TFT | Attention + LSTM | 60d | 160 | 8 | Multi-asset long-horizon |
| LSTM-Attention | BiLSTM + attention | 60d | 128 | 4 | Short-term trends |
| PatchTST | Patch Transformer | 96d | 128 | 8 | Long sequences |
| N-BEATS | Neural basis expansion | 60d | 512 | — | Trend decomposition |
| Graph Attention | GNN on asset graph | 30d | 64 | 4 | Cross-asset relationships |

### 6.3 Quantitative Technical Analysis Engine

**File:** `backend/app/engines/quant_engine/engine.py`

Used by the `/analysis/signals/{symbol}` endpoint for individual stock evaluation.

**RSI (14-day):**
```python
RS = rolling_mean(gains, 14) / rolling_mean(losses, 14)
RSI = 100 - 100 / (1 + RS)
# Oversold < 35 → buy signal; Overbought > 70 → sell signal
```

**Momentum:**
```python
momentum_1m = close[-1] / close[-21] - 1   # 1-month return
momentum_3m = close[-1] / close[0]  - 1   # 3-month return (90-day window)
```

**Moving Average Crossover:**
```python
SMA_20, SMA_50 = rolling_mean(close, 20), rolling_mean(close, 50)
ma_signal = +1 (price > both SMAs)  →  bullish trend
          = -1 (price < both SMAs)  →  bearish trend
          =  0 (mixed)              →  no signal
```

**Combined Signal:**
```python
combined = rsi_signal*0.35 + momentum_signal*0.40 + ma_signal*0.25
predicted_return = combined * 0.25      # Scaled to ±25% annual
confidence = min(0.90, 0.55 + |combined|*0.30)
```

**Alpha Factor Library (`factors.py`) — 20+ Factors:**

| Category | Factors |
|---|---|
| Momentum | momentum_1m, momentum_3m, momentum_12m, RSI-14, MACD |
| Value | P/E, P/B, P/S, dividend_yield, EV/EBITDA |
| Quality | ROE, ROA, debt/equity, current_ratio |
| Volatility | realized_vol (20-day annualized), bid-ask spread |

---

## 7. Portfolio Optimization Algorithms

**File:** `backend/app/engines/portfolio_engine/allocation.py`

### 7.1 Mean-Variance Optimization (Markowitz)

**Objective Function:**
```
maximize:    μᵀw − (λ/2) · wᵀΣw
subject to:  Σwᵢ = 1 − cash_reserve
             min_weight ≤ wᵢ ≤ max_weight  ∀i
```

**Risk Aversion:** `λ ∈ {conservative: 3.0, moderate: 2.0, aggressive: 1.0}`

**Iterative Gradient Solution:**
```python
w = (1/n) * ones_n * investable_fraction   # Equal-weight init

for _ in range(100):
    gradient = μ − λ × (Σ @ w)             # First-order condition
    w_new    = w + 0.01 * gradient          # Gradient ascent (lr=0.01)
    w_new    = clip(w_new, w_min, w_max)    # Box constraints
    w_new    = w_new / sum(w_new) * inv_f   # Budget constraint
    if ‖w_new − w‖₂ < 1e-6: break          # Convergence
    w        = w_new
```

**Portfolio Metrics:**
```python
port_return     = μᵀw
port_volatility = √(wᵀΣw)
sharpe          = (port_return − 0.02) / port_volatility
var_95          = port_volatility × 1.645 − port_return
cvar_95         = port_volatility × 2.063 − port_return
```

### 7.2 Risk Parity Allocation

Inverse-volatility weighting allocates proportionally to 1/σᵢ:
```python
weights = (1/σᵢ for each i) / sum(1/σ) × (1 − cash_reserve)
```
Each asset contributes equal volatility risk; stable assets receive larger allocations.

### 7.3 Equal Risk Contribution (ERC)

Ensures `wᵢ × ∂σₚ/∂wᵢ` is identical for all assets:
```python
for _ in range(100):
    port_vol      = √(wᵀΣw)
    marginal_risk = (Σ @ w) / port_vol
    risk_contrib  = w × marginal_risk
    target        = mean(risk_contrib)
    w             = w × √(target / risk_contrib)   # Multiplicative update
    w             = w / sum(w) × investable
```

Achieves maximum risk diversification given the covariance structure.

---

## 8. Risk Management Framework

**File:** `backend/app/engines/portfolio_engine/risk.py`

### 8.1 Risk Metrics Computed (13 metrics)

```python
@dataclass
class RiskMetrics:
    volatility: float          # σₚ × √252 (annualized)
    var_95: float              # 5th percentile daily return
    var_99: float              # 1st percentile daily return
    cvar_95: float             # E[R | R ≤ VaR₉₅] — Expected Shortfall
    cvar_99: float
    max_drawdown: float        # min((Vₜ − Peakₜ) / Peakₜ)
    max_drawdown_duration: int # Peak-to-recovery days
    beta: float                # cov(Rₚ, Rᵦ) / var(Rᵦ)
    alpha: float               # Jensen's alpha
    tracking_error: float      # σ(Rₚ − Rᵦ)
    information_ratio: float   # alpha / tracking_error
    sortino_ratio: float       # (E[R] − Rf) / σ_downside
    calmar_ratio: float        # excess_return / |max_DD|
    omega_ratio: float         # Σgains / Σ|losses|
```

### 8.2 Risk Profile Expected Ranges

| Profile | Expected Return | Volatility | Max Drawdown |
|---------|----------------|-----------|--------------|
| Conservative | 4–6% | 8–12% | < 15% |
| Moderate | 6–10% | 12–18% | < 25% |
| Aggressive | 10–15% | 18–25% | < 35% |

### 8.3 Stress Testing (4 Scenarios)

| Scenario | Description | Equity Impact | Vol Multiplier |
|---|---|---|---|
| Market Crash | 2008-style systemic crisis | −40% | 3× |
| Interest Rate Shock | +300bps rate spike | −15% | 1.5× |
| Inflation Spike | +500bps CPI surge | −20% | 2× |
| Tech Bubble Burst | 2000-style correction | −50% tech / −25% broad | 2.5× |

---

## 9. Database Architecture & Data Models

**ORM:** SQLAlchemy 2.0 with full async support (asyncpg for PostgreSQL, aiosqlite for SQLite dev)

### 9.1 Entity-Relationship Diagram

```
USERS (1) ─────────────────── (N) PORTFOLIOS
  │                                    │
  │ (1:1)                    (1:N) ─────┼──────────────────
  │                         │           │                   │
WALLETS              PORTFOLIO_HOLDINGS  PORTFOLIO_         PORTFOLIO_
  │                                     TRANSACTIONS        SNAPSHOTS
  │ (1:N)
WALLET_TRANSACTIONS
```

### 9.2 Schema Details

**users table:**
```sql
id            INTEGER PRIMARY KEY
email         VARCHAR(255) UNIQUE NOT NULL
hashed_password VARCHAR(255) NOT NULL  -- Argon2id
full_name     VARCHAR(255)
is_active     BOOLEAN DEFAULT TRUE
risk_tolerance VARCHAR(20) DEFAULT 'moderate'
investment_horizon INTEGER DEFAULT 5  -- years
initial_investment FLOAT DEFAULT 10000
monthly_contribution FLOAT DEFAULT 0
preferred_assets TEXT  -- comma-separated
created_at, updated_at DATETIME
```

**portfolios table:**
```sql
id                INTEGER PRIMARY KEY
user_id           INTEGER REFERENCES users(id)
name              VARCHAR(255)
total_value       FLOAT  -- Updated on price refresh
invested_amount   FLOAT  -- Original investment (fixed)
cash_reserve_pct  FLOAT DEFAULT 0.05
risk_profile      VARCHAR(20)  -- conservative|moderate|aggressive
model_type        VARCHAR(50)  -- temporal_fusion_transformer etc.
expected_return   FLOAT   -- From portfolio optimizer (annual %)
volatility        FLOAT   -- Annualized portfolio volatility
sharpe_ratio      FLOAT
max_drawdown      FLOAT
var_95, cvar_95   FLOAT
ai_explanation    TEXT    -- Claude portfolio narrative
stock_reasoning   TEXT    -- Per-stock Claude reasoning
market_context    TEXT    -- Market summary from Layer 1
created_at, updated_at DATETIME
```

**portfolio_holdings table:**
```sql
id                INTEGER PRIMARY KEY
portfolio_id      INTEGER REFERENCES portfolios(id)
symbol            VARCHAR(20) NOT NULL
asset_type        VARCHAR(20)  -- stock|etf|crypto|gold|cash
sector            VARCHAR(50)
weight            FLOAT  -- 0.0 to 1.0
quantity          FLOAT  -- Number of shares
avg_price         FLOAT  -- Cost basis from creation
current_price     FLOAT  -- Updated by Finnhub refresh
market_value      FLOAT  -- current_price × quantity
predicted_return  FLOAT  -- From ML ensemble
confidence_score  FLOAT  -- ML confidence 0.55–0.90
signal_strength   VARCHAR(20)  -- strong_buy|buy|hold|sell|strong_sell
created_at, updated_at DATETIME
```

**portfolio_snapshots table:**
```sql
id            INTEGER PRIMARY KEY
portfolio_id  INTEGER REFERENCES portfolios(id)
total_value   FLOAT    -- Snapshot portfolio value
cash_value    FLOAT
stocks_value  FLOAT
created_at    DATETIME  -- Indexed for time-series queries
```

**wallets & wallet_transactions:** Track all financial movements with full audit trail (balance_before, balance_after per transaction).

### 9.3 Migration History

| ID | Name | Key Changes |
|---|---|---|
| `33d2e3bd5f84` | Initial | Creates `users`, `portfolios`, `portfolio_holdings` |
| `bc06f0c36814` | Wallet Enhancements | Creates `wallets`, `wallet_transactions`, adds `invested_amount`, `risk_profile` |
| `655fac73abc3` | Snapshots + Reasoning | Creates `portfolio_snapshots`, adds `stock_reasoning`, `market_context` |

---

## 10. Backend API Reference

### 10.1 Authentication (`/api/v1/auth/`)

| Method | Endpoint | Auth | Request | Response |
|--------|---------|------|---------|---------|
| POST | `/register` | No | `{email, password, full_name}` | `UserResponse` |
| POST | `/login` | No | `{email, password}` | `{access_token, refresh_token}` |
| POST | `/refresh` | Refresh | — | `{access_token, refresh_token}` |
| GET | `/me` | Access | — | `UserResponse` |

**Tokens:** HS256 — access 30 min, refresh 7 days. Passwords: Argon2id.

### 10.2 Portfolio Management (`/api/v1/portfolios/`)

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/` | List all user portfolios |
| **POST** | **`/`** | **3-Layer AI portfolio creation** |
| GET | `/{id}` | Full portfolio with all holdings |
| PUT | `/{id}` | Update name/description |
| DELETE | `/{id}` | Remove portfolio |
| GET | `/{id}/chart` | Time-series chart data (from snapshots) |
| POST | `/{id}/refresh` | Refresh live prices from Finnhub |
| GET | `/{id}/reasoning` | Claude's per-stock reasoning |
| GET | `/{id}/performance` | Sharpe, VaR, returns, volatility |
| POST | `/{id}/rebalance` | Drift detection + rebalance recommendations |
| POST | `/analyze` | Quant engine analysis (no portfolio created) |
| POST | `/{id}/holdings` | Manually add a holding |

**Portfolio Creation Request:**
```json
{
  "name": "AI Aggressive Portfolio",
  "investment_amount": 10000.00,
  "risk_profile": "aggressive",
  "cash_reserve_pct": 0.05,
  "model_type": "temporal_fusion_transformer"
}
```

### 10.3 AI Stock Analysis (`/api/v1/analysis/`)

| Method | Endpoint | Description |
|--------|---------|-------------|
| **GET** | **`/stock/{symbol}`** | **Full Claude Sonnet deep analysis (7 sections)** |
| POST | `/assets` | Bulk ML signals for up to 20 stocks |
| GET | `/signals/{symbol}` | Quick ML signal for one stock |
| GET | `/explain/{portfolio_id}` | Claude portfolio reasoning |
| POST | `/backtest` | Historical strategy backtesting |
| GET | `/models` | Available model descriptions |

**Deep Analysis Response:**
```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc",
  "current_price": 266.17,
  "daily_change_pct": -2.52,
  "signal": "buy",
  "confidence": 0.72,
  "overall_score": 71.0,
  "fundamental_analysis": "...",
  "technical_analysis": "...",
  "market_sentiment": "...",
  "growth_catalysts": "...",
  "key_risks": "...",
  "valuation_assessment": "...",
  "investment_recommendation": "...",
  "analyst_consensus": "23 Buy, 2 Hold, 0 Sell",
  "price_target": 310.0,
  "sector": "Technology"
}
```

### 10.4 Market Data (`/api/v1/market/`)

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/quote/{symbol}` | Single real-time quote |
| GET | `/quotes?symbols=` | Batch quotes (comma-separated) |
| GET | `/popular` | 15 popular stock quotes |
| GET | `/overview` | S&P 500, NASDAQ, Dow Jones, Russell 2000 |
| GET | `/search?query=` | US-listed stock symbol search |

### 10.5 Wallet (`/api/v1/wallet/`)

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/` | Balance, deposited, withdrawn, invested |
| POST | `/deposit` | Add funds (max $1,000,000) |
| POST | `/withdraw` | Remove available funds |
| GET | `/transactions` | Paginated transaction history |

---

## 11. External Data Sources & APIs

### 11.1 Finnhub API

**Base URL:** `https://finnhub.io/api/v1` | **Auth:** `?token={key}` | **Tier:** Free

| Endpoint | Data Returned |
|---------|--------------|
| `/quote` | `c` (price), `dp` (daily%), `h/l/o/pc` (OHLC), `t` (timestamp) |
| `/stock/profile2` | Company name, `finnhubIndustry` (sector), market cap |
| `/stock/recommendation` | `strongBuy`, `buy`, `hold`, `sell`, `strongSell` vote counts |
| `/stock/metric?metric=all` | P/E, P/B, ROE, revenue growth, net margin, beta, 52W range |
| `/company-news` | Last 7–30 days company headlines + summaries |
| `/news?category=general` | Broad market headlines |

**Caching:** Quotes → 60s TTL | Overview → 300s TTL

### 11.2 Alpha Vantage API

**Function:** `TIME_SERIES_DAILY` (compact = 100 days OHLCV)  
**Rate Limit:** 5 calls/minute, 25/day (free tier)  
**Used for:** Backtesting historical returns

### 11.3 NewsAPI

**Query:** `"stock market investing sectors earnings AI technology"`  
**Filters:** English, last 48 hours, sorted by `publishedAt`, 30 articles  
**Rate Limit:** 1,000 requests/day (free tier)  
**Used for:** Layer 1 Claude AI stock selection news feed

### 11.4 Anthropic Claude API

| Model | Use Case | Max Tokens | Avg Latency |
|-------|---------|-----------|-------------|
| `claude-haiku-4-5-20251001` | Stock selection, portfolio reasoning, summaries | 2048 | 2–5s |
| `claude-sonnet-4-6` | Deep stock analysis (7 research sections) | 2500 | 15–30s |

**Key prompt engineering decisions:**
- Temperature 0.8 for stock selection (varied outputs)
- Structured JSON output schema enforced
- Fallback to rule-based analysis when Claude unavailable

---

## 12. Frontend Architecture

### 12.1 Application Routes

| Route | Auth | Description |
|-------|------|-------------|
| `/` | Public | Landing page (Three.js background) |
| `/login` | Public | JWT authentication |
| `/register` | Public | Account creation |
| `/onboarding` | Protected | Risk preference wizard |
| `/dashboard` | Protected | Portfolio overview + market indices |
| `/portfolio/:id?` | Protected | Holdings, chart, AI insights, performance |
| `/analysis` | Protected | Claude stock analysis + market signals |
| `/invest` | Protected | Portfolio creation wizard (3-step) |
| `/deposit-withdraw` | Protected | Wallet management |

### 12.2 State Management

**Zustand (authStore.js):**
```javascript
{
  user, isAuthenticated,
  getToken()      → access token from localStorage
  getRefreshToken() → refresh token
  setTokens(access, refresh) → persist to localStorage
  logout()        → clear state + redirect
}
```

**Axios Interceptors:**
- **Request:** Auto-inject `Authorization: Bearer {token}`
- **Response 401:** Attempt token refresh; on failure, logout + redirect

### 12.3 Key Components

**PortfolioChart (Recharts AreaChart):**
- Data: Real snapshots from `/portfolios/{id}/chart`
- Green gradient when current value > invested; red when below
- Dashed reference line at cost basis
- Summary row: current value, return %, return $

**AssetAllocation (Recharts PieChart):**
- Donut chart weighted by holding market_value
- Color-coded: stocks (teal), ETFs (purple), cash (green)

**Analysis Page (Deep Claude Analysis):**
- US-only symbol search (filters out `.` and `:` exchanges)
- Step-by-step progress display during 15–30s Claude analysis
- 7 collapsible analysis sections
- Price target + analyst consensus prominently shown

### 12.4 API Service Methods

```javascript
// Key API functions used by the frontend
portfolioApi.create(data)              → POST /portfolios/
portfolioExtApi.getChart(id)           → GET  /portfolios/{id}/chart
portfolioExtApi.refreshPrices(id)      → POST /portfolios/{id}/refresh
portfolioExtApi.getReasoning(id)       → GET  /portfolios/{id}/reasoning
analysisApi.getStockAnalysis(symbol)   → GET  /analysis/stock/{symbol}
analysisApi.analyzeAssets(data)        → POST /analysis/assets
marketApi.getMarketOverview()          → GET  /market/overview
walletApi.deposit(amount, desc)        → POST /wallet/deposit
```

---

## 13. AI Analysis System (Claude Sonnet)

**File:** `backend/app/api/v1/endpoints/analysis.py`

### 13.1 Data Pipeline for Deep Analysis

Five Finnhub data streams fetched concurrently per symbol:

```python
quote, profile, recommendations, news, metrics = await asyncio.gather(
    client.get("/quote"),              # Current price & daily move
    client.get("/stock/profile2"),     # Company + sector
    client.get("/stock/recommendation"), # Analyst votes
    client.get("/company-news"),       # Last 30 days news
    client.get("/stock/metric"),       # Financial ratios
)
```

### 13.2 Claude Sonnet Prompt

The prompt provides Claude with:
- Exact financial metrics (P/E, P/B, ROE, revenue growth, net margin, beta)
- Analyst consensus with exact vote counts
- Last 5 news headlines with summaries
- Intraday price action (open, close, high, low, daily %)

Claude returns structured JSON across **7 research sections** plus `overall_score` (0–100), `confidence` (0–1), `signal`, and `price_target`.

**Model used:** `claude-sonnet-4-6` — Sonnet chosen because the depth and quality of analysis justifies higher cost vs. Haiku.

### 13.3 Rule-Based Fallback

When Claude is unavailable, a momentum-based rule generates a simplified analysis:
```python
signal = "buy"  if daily_change > 1.5 else
         "sell" if daily_change < -1.5 else "hold"
confidence = 0.55
overall_score = 55.0
```

---

## 14. Research Agent System

**Files:** `backend/app/agents/research_agent/`

An alternative research pipeline for fundamental + sentiment-based stock screening.

### 14.1 Orchestration (`agent.py`)

**ResearchAgent.execute()** runs sequentially:
1. **Fundamental analysis** on entire universe → screen to `overall_score ≥ 60`
2. **Sentiment analysis** on screened subset → filter `sentiment ≥ −0.2`, exclude declining
3. **Combined ranking:** `combined = (fundamental + sentiment) / 2` → top N returned

### 14.2 Fundamental Scoring (`fundamental.py`)

yfinance data → 3 dimension scores (0–100 each), weighted 30/40/30:

```python
# Value Score
pe_ratio < 15  → +25 pts  (deep value)
pb_ratio < 2.0 → +15 pts  (asset discount)

# Quality Score
roe > 20% → +25 pts    (excellent profitability)
D/E < 0.5 → +15 pts    (low leverage)
margin > 20% → +10 pts  (pricing power)

# Growth Score
rev_growth > 30% → +30 pts   (high growth)
rev_growth > 15% → +20 pts
FCF > 0          → +10 pts   (cash generative)

# Combined
overall = value*0.30 + quality*0.40 + growth*0.30
```

### 14.3 Sentiment Analysis (`sentiment.py`)

Keyword-based scoring on NewsAPI headlines:

```python
BULLISH = {"beats", "surges", "upgrade", "profit", "record", "growth", ...}
BEARISH = {"misses", "drops", "downgrade", "loss", "recession", "fraud", ...}

sentiment_score = (bull_hits - bear_hits) / (bull_hits + bear_hits + ε)
                  ∈ [-1.0, +1.0]
```

Trend classification: `improving` (bullish > 1.3× bearish), `declining` (bearish > 1.3× bullish), else `stable`.

---

## 15. Security Architecture

### 15.1 Authentication Flow

```
Registration → Argon2id password hash stored
Login → JWT access token (30 min) + refresh token (7 days) issued
Requests → Authorization: Bearer {access_token}
401 → Axios interceptor auto-refreshes → retries original request
Refresh fail → logout + /login redirect
```

**JWT Payload:** `{sub: user_id, exp: timestamp, type: "access"|"refresh"}`  
The `type` field is validated — a refresh token cannot be used as an access token.

### 15.2 Corporate Network Compatibility

`truststore.inject_into_ssl()` is called at app startup (`main.py`) before any network connections are made. This patches Python's `ssl` module to use the OS native certificate store (Windows CertStore, macOS Keychain), enabling the application to work behind TLS-inspection proxies without manual certificate configuration.

### 15.3 Data Security

- SQL injection: Prevented by SQLAlchemy ORM parameterized queries
- XSS: React's JSX auto-escapes all rendered content
- API keys: Environment variables only, never logged or returned to clients

---

## 16. Deployment & Infrastructure

### 16.1 Development Environment

```
OS: Windows 11 / macOS / Linux
Python: 3.12 (venv)
Node.js: 18+
Database: SQLite (no PostgreSQL install required)
Cache: In-memory fallback (Redis optional)
```

### 16.2 Production (render.yaml)

```yaml
services:
  - type: web           # FastAPI backend
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase: { name: autoinvest-db, property: connectionString }

  - type: web           # React frontend
    buildCommand: npm run build
    staticPublishPath: ./frontend/web/dist

databases:
  - name: autoinvest-db
    plan: free          # PostgreSQL managed by Render
```

### 16.3 Caching Strategy

```
Redis Cache (when available):
  quote:{symbol}      → TTL 60s   (real-time price freshness)
  market:overview     → TTL 300s  (5 minute index refresh)
  claude:{query_hash} → TTL 3600s (LLM response caching)

NoopCache (Redis unavailable):
  In-memory dict — process-scoped, no TTL enforcement
  Falls back gracefully, no exception thrown
```

---

## 17. Mathematical Formulations

### 17.1 Portfolio Expected Return
$$E[R_p] = \boldsymbol{\mu}^T \mathbf{w}$$

### 17.2 Portfolio Volatility
$$\sigma_p = \sqrt{\mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}}, \quad \Sigma_{ij} = \sigma_i \cdot \sigma_j \cdot \rho_{ij}$$

### 17.3 Sharpe Ratio
$$S = \frac{E[R_p] - R_f}{\sigma_p}, \quad R_f = 2\%$$

### 17.4 Markowitz Optimization Problem
$$\max_{\mathbf{w}} \left[\boldsymbol{\mu}^T\mathbf{w} - \frac{\lambda}{2}\mathbf{w}^T\boldsymbol{\Sigma}\mathbf{w}\right]$$
$$\text{s.t.} \quad \sum_i w_i = 1 - c, \quad w_{min} \leq w_i \leq w_{max}$$

**Gradient update:** $\mathbf{w}_{t+1} = \text{clip}\left(\mathbf{w}_t + 0.01(\boldsymbol{\mu} - \lambda\boldsymbol{\Sigma}\mathbf{w}_t)\right)$

### 17.5 Value at Risk (95%, Parametric)
$$\text{VaR}_{95} = \sigma_p \times 1.645 - E[R_p]$$

### 17.6 Conditional VaR (Expected Shortfall, 95%)
$$\text{CVaR}_{95} = \sigma_p \times 2.063 - E[R_p]$$

### 17.7 Risk Parity Weights
$$w_i^{RP} = \frac{1/\sigma_i}{\sum_j 1/\sigma_j} \times (1 - c)$$

### 17.8 ERC Update Rule
$$\text{RC}_i = w_i \cdot \frac{(\boldsymbol{\Sigma}\mathbf{w})_i}{\sigma_p}, \quad w_i^{new} = w_i \cdot \sqrt{\frac{\overline{\text{RC}}}{\text{RC}_i}}$$

### 17.9 Diversification Ratio
$$DR = \frac{\sum_i w_i \sigma_i}{\sigma_p} \geq 1$$

### 17.10 Herfindahl-Hirschman Index (Concentration)
$$HHI = \sum_i w_i^2 \in \left[\frac{1}{n},\ 1\right]$$

### 17.11 ML Ensemble Prediction
$$\hat{r}_i = 0.55 \cdot f_{\text{RF}}(\mathbf{x}_i) + 0.45 \cdot f_{\text{GB}}(\mathbf{x}_i)$$

### 17.12 Analyst Score Normalization
$$A_i = \frac{2\cdot\text{strongBuy} + \text{buy} - \text{sell} - 2\cdot\text{strongSell}}{2 \times \text{total}} \in [-1, +1]$$

### 17.13 RSI (14-day)
$$\text{RSI} = 100 - \frac{100}{1 + \text{RS}}, \quad \text{RS} = \frac{\text{Avg Gain}_{14}}{\text{Avg Loss}_{14}}$$

---

## 18. Experimental Results & Sample Outputs

### 18.1 Portfolio Creation Performance

| Risk Profile | Avg Stocks | Expected Return | Volatility | Sharpe | Time |
|---|---|---|---|---|---|
| Conservative | 7–8 | 5.2–6.8% | 8–14% | 0.28–0.42 | 12–18s |
| Moderate | 8–10 | 7.4–10.2% | 14–22% | 0.22–0.38 | 15–25s |
| Aggressive | 8–10 | 10.8–14.5% | 22–36% | 0.13–0.28 | 18–32s |

### 18.2 Sample Aggressive Portfolio

```
Portfolio: AI Aggressive Portfolio | $5,000 invested | Aggressive risk

Holdings:
  Symbol  │ Sector   │ Weight │   Price │  Qty  │ Pred. Return │ Signal
  ────────┼──────────┼────────┼─────────┼───────┼──────────────┼──────────
  CRWD    │ Tech     │ 18.8%  │ $449.61 │  1.99 │    +14.2%    │ STRONG BUY
  AMD     │ Tech     │ 13.2%  │ $284.49 │  2.21 │    +11.8%    │ BUY
  MSFT    │ Tech     │ 21.4%  │ $424.16 │  2.40 │     +9.4%    │ BUY
  NET     │ Tech     │  6.0%  │ $207.67 │  1.38 │    +10.2%    │ BUY
  NVDA    │ Tech     │  7.0%  │ $199.88 │  1.67 │     +9.0%    │ BUY
  PLTR    │ Tech     │  3.0%  │ $145.97 │  0.98 │    +11.5%    │ BUY
  MELI    │ Consumer │ 16.4%  │$1854.18 │  0.42 │     +7.8%    │ HOLD
  SHOP    │ Tech     │  3.0%  │ $131.13 │  1.09 │     +8.2%    │ HOLD
  TSLA    │ Consumer │  3.0%  │ $386.42 │  0.37 │     +9.0%    │ HOLD
  COIN    │ Finance  │  3.0%  │ $195.95 │  0.73 │     +5.2%    │ SELL
  CASH    │ Cash     │  5.0%  │   $1.00 │250.00 │      0.0%    │ HOLD

Risk Metrics:
  Expected Annual Return:  10.8%
  Annual Volatility:       36.0%
  Sharpe Ratio:            0.24
  VaR (95%):               48.3%
  CVaR (95%):              63.5%

Market Context (from Layer 1 Claude):
  "AI infrastructure spending accelerating with hyperscaler CapEx guidance
   increases. Cybersecurity sector benefiting from rising enterprise threat
   landscape. Semiconductor demand driven by data center GPU buildout..."

Per-Stock Reasoning (Claude):
  CRWD: Cybersecurity leadership in AI-native threat detection; strong buy
        consensus (21 of 23 analysts); +14.2% ML predicted return
  AMD:  AI chip challenger with datacenter GPU momentum; analyst upgrade
        cycle with +2.1% positive daily momentum signal
  MSFT: Azure AI revenue acceleration, Copilot enterprise adoption; serves
        as lower-volatility anchor in aggressive portfolio...
```

### 18.3 Deep Stock Analysis (AAPL)

```
Claude Sonnet Analysis — Apple Inc. (AAPL)
Current: $266.17 | Change: −2.52% | Signal: BUY | Score: 71/100
Target: $310.00 | Analyst: 23 Buy, 2 Hold, 0 Sell (92% bullish)

Fundamental: Apple's services margin exceeds 72%, balance sheet holds
  $162B in cash. ROE remains S&P 500 top tier, supported by buyback
  leverage. Revenue growth 5% YoY is modest but services compound at 14%.

Technical: Consolidating near $260–$270 support after −12% correction.
  RSI at 38 approaching oversold historically presenting favorable entry.
  20-day SMA ($276) = near-term resistance; 50-day SMA ($283) = breakout.

Growth: Apple Intelligence AI integration across iOS 18 creates upgrade
  supercycle; Services segment compounding at 14%; India manufacturing
  diversification reduces geopolitical supply chain concentration.

Risks: China exposure (~17% revenue) vulnerable to trade tension escalation;
  EU/US App Store regulatory pressure on economics; premium smartphone
  market saturation in developed economies.

Recommendation: BUY — The −2.52% daily decline appears technically driven.
  With 92% analyst buy consensus and 16% implied upside to $310 target,
  risk/reward at $266 is favorable for 12-month horizon.
```

---

## 19. Limitations & Future Work

### 19.1 Current Limitations

| Category | Limitation | Impact |
|---|---|---|
| ML Models | sklearn proxy for TFT/LSTM (no PyTorch) | Medium — signals are real but simpler |
| Covariance | Hardcoded sector correlations, not dynamic | Medium — stable but not adaptive |
| Backtesting | Synthetic random walk, not true historical | High — backtest results are illustrative |
| ML Training | Synthetic seed data, not historical returns | High — model not validated on OOS data |
| Optimization | Gradient ascent vs. quadratic programming | Medium — approximate but convergent |
| Sentiment | Keyword matching, not transformer NLP | Low — adequate for screening |
| Real-time | No WebSocket streaming — manual refresh | Low — acceptable for portfolio management |
| Execution | Recommendations only — no live trading | N/A — by design (regulatory) |

### 19.2 Future Research Directions

**1. Real Deep Learning Models**

Implement PyTorch backends for TFT, PatchTST, and N-BEATS with:
- 10+ years of daily OHLCV data for 2,000+ US securities
- Walk-forward backtesting with proper train/test splits
- ONNX runtime deployment for production inference
- Expected improvement: 15–25% Sharpe ratio improvement vs. sklearn baseline

**2. Agentic Portfolio Management**

Multi-turn LLM pipeline where Claude autonomously:
- Monitors portfolio daily for rebalancing triggers
- Analyzes earnings releases and adjusts positions
- Generates alerts on significant market regime changes
- Executes paper trades via broker API (Alpaca, Interactive Brokers)

**3. Reinforcement Learning**

Frame portfolio allocation as a continuous-action RL problem:
- State: Price history, fundamental data, sentiment scores, current portfolio
- Action: Weight delta vector (buy/sell signals per asset)
- Reward: Risk-adjusted return (Sharpe ratio over rolling 60-day window)
- Algorithm: Soft Actor-Critic (SAC) or TD3 for continuous action spaces

**4. Graph Neural Networks**

Build asset correlation graph from supply-chain data and news co-mentions:
- GNN aggregates signals from correlated assets
- Particularly valuable for sector-rotation signal extraction
- Captures indirect relationships (supplier-customer effects)

**5. Alternative Data**

- Satellite imagery for retail foot traffic (REIT and consumer sector)
- Credit card transaction aggregates for consumer spending
- Patent filing velocity for R&D intensity proxy
- Options market implied volatility surface for tail risk

**6. True Historical Backtesting**

- CRSP or Compustat data for survivorship-bias-free universe
- Transaction cost modeling: 0.5–2 bps commission + 5–15 bps market impact
- Short-selling constraints and margin requirements
- Tax optimization (loss harvesting, wash-sale rules)

---

## 20. Setup & Installation

### 20.1 Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.12+ | python.org |
| Node.js | 18+ | nodejs.org |

### 20.2 Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Windows activation
venv\Scripts\python.exe -m pip install -r requirements.txt

# macOS/Linux activation
source venv/bin/activate && pip install -r requirements.txt

# Configure environment
cp .env.example .env
# → Edit .env with your API keys

# Create database schema
venv\Scripts\python.exe -m alembic upgrade head

# Start backend
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 20.3 Frontend Setup

```bash
cd frontend/web
npm install
npm run dev
```

### 20.4 Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Documentation (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

### 20.5 Required Environment Variables

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./autoinvest.db
DATABASE_URL_SYNC=sqlite:///./autoinvest.db

# Security
SECRET_KEY=<32+ character random string>

# AI API (required for all AI features)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Market Data APIs (required for real stock data)
FINNHUB_API_KEY=...
ALPHA_VANTAGE_API_KEY=...
NEWS_API_KEY=...
POLYGON_API_KEY=...

# Application
APP_NAME=AutoInvest
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:5173
```

### 20.6 API Key Registration

| API | Free Tier Limits | Registration |
|-----|----------------|-------------|
| Anthropic Claude | Pay-per-use | console.anthropic.com |
| Finnhub | 60 requests/min | finnhub.io/register |
| Alpha Vantage | 25 requests/day | alphavantage.co/support/#api-key |
| NewsAPI | 1,000 requests/day | newsapi.org/register |

---

## 21. References & Related Work

### Portfolio Theory

1. Markowitz, H. (1952). Portfolio Selection. *The Journal of Finance*, 7(1), 77–91. https://doi.org/10.2307/2975974

2. Sharpe, W.F. (1964). Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk. *The Journal of Finance*, 19(3), 425–442.

3. Maillard, S., Roncalli, T., & Teïletche, J. (2010). The Properties of Equally Weighted Risk Contribution Portfolios. *Journal of Portfolio Management*, 36(4), 60–70.

4. Black, F., & Litterman, R. (1992). Global Portfolio Optimization. *Financial Analysts Journal*, 48(5), 28–43.

### Machine Learning in Finance

5. Harvey, C.R., Liu, Y., & Zhu, H. (2016). ...and the Cross-Section of Expected Returns. *The Review of Financial Studies*, 29(1), 5–68.

6. Lopez de Prado, M. (2018). *Advances in Financial Machine Learning*. John Wiley & Sons.

7. Gu, S., Kelly, B., & Xiu, D. (2020). Empirical Asset Pricing via Machine Learning. *The Review of Financial Studies*, 33(5), 2223–2273.

8. Chen, L., Pelger, M., & Zhu, J. (2024). Deep Learning in Asset Pricing. *Management Science*, 70(2), 714–750.

### Deep Learning for Time Series

9. Lim, B., Arik, S.Ö., Loeff, N., & Pfister, T. (2021). Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting. *International Journal of Forecasting*, 37(4), 1748–1764.

10. Oreshkin, B.N., Carpov, D., Chapados, N., & Bengio, Y. (2020). N-BEATS: Neural Basis Expansion Analysis for Interpretable Time Series Forecasting. *ICLR 2020*. arXiv:1905.10437.

11. Nie, Y., et al. (2023). A Time Series is Worth 64 Words: Long-term Forecasting with Transformers. *ICLR 2023*. arXiv:2211.14730. (PatchTST)

### Large Language Models in Finance

12. Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models. *SSRN Working Paper*. https://ssrn.com/abstract=4412788

13. Koa, K.X., et al. (2024). Learning to Generate Explainable Stock Predictions using Self-Reflective Large Language Models. *arXiv:2402.03190*.

14. Yu, F., & Ng, K.W. (2024). FinAgent: A Multimodal Foundation Agent for Financial Trading. *arXiv:2402.18485*.

15. Xie, Q., et al. (2024). PIXIU: A Comprehensive Benchmark, Instruction Dataset and Large Language Model for Finance. *NeurIPS 2023 Datasets Track*.

### Robo-Advisory

16. D'Acunto, F., Prabhala, N., & Rossi, A.G. (2019). The Promises and Pitfalls of Robo-Advising. *The Review of Financial Studies*, 32(5), 1983–2020.

17. Beketov, M., Lehmann, K., & Wittke, M. (2018). Robo Advisors: quantitative methods inside the robots. *Journal of Asset Management*, 19(6), 363–370.

### Technical Tools

18. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR*, 12, 2825–2830.

19. Paszke, A., et al. (2019). PyTorch: An Imperative Style, High-Performance Deep Learning Library. *NeurIPS 2019*. arXiv:1912.01703.

20. Tiangolo, S. (2023). FastAPI. https://fastapi.tiangolo.com/

21. Anthropic. (2024). Claude API Documentation. https://docs.anthropic.com/

---

## Appendix A: Complete API Endpoint List

| Method | Endpoint | Auth | Description |
|--------|---------|------|-------------|
| POST | `/api/v1/auth/register` | No | Create account |
| POST | `/api/v1/auth/login` | No | Authenticate |
| POST | `/api/v1/auth/refresh` | Refresh | Rotate tokens |
| GET | `/api/v1/auth/me` | Access | Current user |
| GET | `/api/v1/users/me` | Access | Profile |
| PUT | `/api/v1/users/me` | Access | Update profile |
| GET | `/api/v1/users/me/preferences` | Access | Preferences |
| PUT | `/api/v1/users/me/preferences` | Access | Update preferences |
| GET | `/api/v1/dashboard` | Access | Full dashboard |
| GET | `/api/v1/portfolios/` | Access | List portfolios |
| **POST** | **`/api/v1/portfolios/`** | Access | **3-Layer AI creation** |
| GET | `/api/v1/portfolios/{id}` | Access | Portfolio + holdings |
| PUT | `/api/v1/portfolios/{id}` | Access | Update |
| DELETE | `/api/v1/portfolios/{id}` | Access | Delete |
| GET | `/api/v1/portfolios/{id}/chart` | Access | Chart time series |
| POST | `/api/v1/portfolios/{id}/refresh` | Access | Live price refresh |
| GET | `/api/v1/portfolios/{id}/reasoning` | Access | Claude reasoning |
| GET | `/api/v1/portfolios/{id}/performance` | Access | Risk metrics |
| POST | `/api/v1/portfolios/{id}/rebalance` | Access | Rebalance check |
| POST | `/api/v1/portfolios/analyze` | Access | Quant analysis |
| POST | `/api/v1/portfolios/{id}/holdings` | Access | Add holding |
| **GET** | **`/api/v1/analysis/stock/{symbol}`** | Access | **Deep Claude analysis** |
| POST | `/api/v1/analysis/assets` | Access | Bulk ML signals |
| GET | `/api/v1/analysis/signals/{symbol}` | Access | Quick signal |
| GET | `/api/v1/analysis/explain/{id}` | Access | Portfolio reasoning |
| POST | `/api/v1/analysis/backtest` | Access | Backtest |
| GET | `/api/v1/analysis/models` | Access | Model list |
| GET | `/api/v1/market/quote/{symbol}` | Access | Real-time quote |
| GET | `/api/v1/market/quotes` | Access | Batch quotes |
| GET | `/api/v1/market/popular` | Access | Popular stocks |
| GET | `/api/v1/market/overview` | Access | Market indices |
| GET | `/api/v1/market/search` | Access | Symbol search |
| GET | `/api/v1/market/ai-analysis/{symbol}` | Access | LLM analysis |
| GET | `/api/v1/wallet` | Access | Balance |
| POST | `/api/v1/wallet/deposit` | Access | Add funds |
| POST | `/api/v1/wallet/withdraw` | Access | Remove funds |
| GET | `/api/v1/wallet/transactions` | Access | Transaction history |
| GET | `/api/v1/system/stats` | Access | System statistics |
| POST | `/api/gemini-query` | No | Claude text query |
| WS | `/api/gemini-stream` | No | Claude streaming |
| WS | `/api/ws/market-data` | No | Simulated market stream |
| POST | `/api/optimize/` | No | Portfolio optimization |
| GET | `/health` | No | Health check |
| GET | `/` | No | Welcome + docs link |
| GET | `/docs` | No | Swagger UI (dev only) |

---

## Appendix B: File Structure

```
ai-auto-investment/
├── backend/
│   ├── app/
│   │   ├── agents/research_agent/
│   │   │   ├── agent.py           # Orchestration: fundamental + sentiment + explain
│   │   │   ├── fundamental.py     # yfinance-based scoring (value/quality/growth)
│   │   │   ├── sentiment.py       # NewsAPI keyword sentiment
│   │   │   └── explainability.py  # Portfolio narrative generation
│   │   ├── api/v1/endpoints/
│   │   │   ├── analysis.py        # Claude Sonnet deep analysis
│   │   │   ├── auth.py            # JWT register/login/refresh
│   │   │   ├── dashboard.py       # Consolidated dashboard
│   │   │   ├── market.py          # Finnhub market data
│   │   │   ├── portfolios.py      # 3-layer AI portfolio creation (CORE)
│   │   │   ├── system.py          # Health & statistics
│   │   │   ├── users.py           # Profile & preferences
│   │   │   └── wallet.py          # Financial transactions
│   │   ├── core/
│   │   │   ├── cache.py           # Redis + NoopCache fallback
│   │   │   ├── config.py          # Pydantic BaseSettings
│   │   │   └── security.py        # JWT encode/decode + Argon2
│   │   ├── db/
│   │   │   ├── base.py            # SQLAlchemy declarative base
│   │   │   └── session.py         # AsyncEngine + AsyncSessionLocal
│   │   ├── engines/
│   │   │   ├── ml_engine/
│   │   │   │   ├── predictor.py   # RF + GB ensemble (CORE ML)
│   │   │   │   └── saved_models/  # joblib pickles (auto-generated)
│   │   │   ├── portfolio_engine/
│   │   │   │   ├── allocation.py  # Markowitz + RP + ERC optimization
│   │   │   │   ├── engine.py      # Portfolio engine facade
│   │   │   │   ├── rebalance.py   # Drift detection
│   │   │   │   └── risk.py        # 13 risk metrics
│   │   │   └── quant_engine/
│   │   │       ├── engine.py      # Technical analysis (RSI/SMA/Momentum)
│   │   │       ├── factors.py     # 20+ alpha factor library
│   │   │       └── models.py      # DL model config schemas
│   │   ├── main.py                # FastAPI app + CORS + truststore
│   │   ├── models/                # SQLAlchemy ORM
│   │   ├── routers/               # Additional endpoints
│   │   ├── schemas/               # Pydantic schemas
│   │   └── services/
│   │       ├── ai_stock_selector.py  # Layer 1: Claude + NewsAPI
│   │       ├── claude_service.py     # Anthropic client wrapper
│   │       ├── llm_service.py        # LLM portfolio analysis
│   │       ├── market_data.py        # Finnhub service + cache
│   │       ├── portfolio_updater.py  # Price refresh + snapshots
│   │       └── wallet_service.py     # All financial transactions
│   ├── alembic/versions/          # 3 migration files
│   ├── requirements.txt
│   └── .env
│
├── frontend/web/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AssetAllocation.jsx    # Donut chart
│   │   │   ├── PortfolioChart.jsx     # Real snapshot area chart
│   │   │   └── ... (15 components)
│   │   ├── pages/
│   │   │   ├── Analysis.jsx           # Claude stock analysis UI
│   │   │   ├── Dashboard.jsx          # Overview + market data
│   │   │   ├── Invest.jsx             # Portfolio creation wizard
│   │   │   ├── Portfolio.jsx          # Holdings + insights + chart
│   │   │   └── ... (6 pages)
│   │   ├── services/api.js            # Axios + all API methods
│   │   └── store/authStore.js         # Zustand JWT store
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── docker-compose.yml
├── render.yaml
├── .env.example
└── README.md                          # This document
```

---

*This research system is a prototype for academic and educational purposes. It is not intended for live investment use without appropriate regulatory compliance, risk management, and professional financial oversight. All AI-generated investment analysis is informational and does not constitute financial advice. Past performance and model predictions do not guarantee future results.*

---

**Research Team:** AutoInvest AI Research Initiative  
**Institution:** Aurigo Software Technologies Inc.  
**Contact:** v-pranav.h@aurigo.com  
**Date:** April 2026  
**Version:** 2.0 (Production MVP)
