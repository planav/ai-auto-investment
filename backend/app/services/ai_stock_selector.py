"""
Layer 1: AI Stock Selector — Genuinely analysis-driven.

Workflow:
  1. Fetch REAL market data from Finnhub: sector ETF performance, market indices, news
  2. Fetch financial news from NewsAPI (sector-specific, not generic)
  3. Send ALL data to Claude Sonnet with a structured analytical prompt
  4. Claude reads the data, identifies hot sectors, picks stocks with specific catalysts
  5. If Claude fails → dynamic fallback: score a large pool using Finnhub momentum (not static list)

Claude never picks from a predefined list. It makes its own decisions from the data.
"""

from __future__ import annotations
import asyncio
import json
import random
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import httpx
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


# ---------------------------------------------------------------------------
# Sector ETF proxies — used to measure TODAY's sector momentum
# ---------------------------------------------------------------------------

_SECTOR_ETFS = {
    "Technology":            "XLK",
    "Financials":            "XLF",
    "Healthcare":            "XLV",
    "Energy":                "XLE",
    "Utilities":             "XLU",
    "Industrials":           "XLI",
    "Consumer Discretionary":"XLY",
    "Consumer Staples":      "XLP",
    "Materials":             "XLB",
    "Real Estate":           "XLRE",
    "Communication":         "XLC",
}

# Large candidate pool used for the DYNAMIC fallback (momentum-ranked, not static)
_CANDIDATE_POOL = {
    "conservative": [
        "SPY","VTI","BND","AGG","GLD","SCHD","VYM","VNQ","XLU","XLV","IEF","TLT",
        "JNJ","PG","KO","PEP","WMT","MCD","ABBV","MRK","PFE","ABT","MDT","GILD",
        "NEE","DUK","SO","O","MO","PM","CL","KMB","GIS","HSY","BMY","CVS","WBA",
        "D","AEP","EXC","ED","SRE","VZ","T","CMCSA","USB","TFC","PNC","KEY",
    ],
    "moderate": [
        "AAPL","MSFT","GOOGL","AMZN","NVDA","META","AVGO","ORCL","CSCO","QCOM",
        "TXN","INTU","ADBE","CRM","NOW","ACN","IBM","INTC","MU","HPQ",
        "JPM","V","MA","GS","MS","BLK","BAC","WFC","AXP","PYPL","FIS",
        "UNH","ISRG","ZTS","AMGN","LLY","DHR","TMO","A","IDXX",
        "CAT","HON","DE","LMT","RTX","UPS","FDX","MMM","ETN","ROK",
        "XOM","CVX","COP","EOG","MPC","VLO","SLB",
        "COST","SBUX","NKE","HD","TGT","DIS","NFLX","ABNB",
        "SPY","QQQ","VTI","IWM","XLF","XLK",
    ],
    "aggressive": [
        # AI / Semiconductors
        "NVDA","AMD","ARM","SMCI","MRVL","AVGO","MU","ON","WOLF","AMAT","LRCX","KLAC",
        # Cloud / SaaS high-growth
        "CRWD","NET","PANW","ZS","DDOG","SNOW","MDB","NOW","OKTA","S","CFLT","GTLB",
        "TWLO","HUBS","BILL","APP","MNDY","DOCU","ZI","ASAN",
        # AI / Data disruptors
        "PLTR","AI","PATH","SOUN","BBAI","RBRK","RXRX","CELH","HIMS",
        # Consumer disruption
        "TSLA","RIVN","LCID","MELI","ABNB","DASH","UBER","LYFT","OPEN","Z",
        # Crypto / Fintech
        "COIN","MARA","MSTR","RIOT","CLSK","SQ","SOFI","AFRM","UPST","HOOD",
        # Biotech / Health innovation
        "MRNA","BNTX","CRSP","BEAM","EDIT","NTLA","RXRX","ACMR",
        # Clean energy / EV infrastructure
        "ENPH","SEDG","PLUG","BE","BLNK","CHPT","FSLR","RUN",
        # Momentum / high-beta
        "RBLX","U","TTD","MGNI","AXON","TMDX","DUOL","NTRA","IDYA",
    ],
}


# ---------------------------------------------------------------------------
# Data fetching helpers
# ---------------------------------------------------------------------------

async def _fetch_sector_performance(api_key: str) -> Dict[str, dict]:
    """Fetch today's % change for each major sector ETF from Finnhub."""
    results: Dict[str, dict] = {}
    if not api_key:
        return results
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = {
            sector: client.get(
                "https://finnhub.io/api/v1/quote",
                params={"symbol": etf, "token": api_key},
            )
            for sector, etf in _SECTOR_ETFS.items()
        }
        responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
    for (sector, _), resp in zip(tasks.items(), responses):
        if isinstance(resp, Exception):
            continue
        try:
            d = resp.json()
            if d.get("c", 0) > 0:
                results[sector] = {"price": d["c"], "change_pct": round(d.get("dp", 0), 2)}
        except Exception:
            pass
    return results


async def _fetch_market_indices(api_key: str) -> Dict[str, dict]:
    """Fetch SPY and QQQ as overall market sentiment."""
    indices: Dict[str, dict] = {}
    if not api_key:
        return indices
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = {
            "S&P 500 (SPY)": client.get("https://finnhub.io/api/v1/quote", params={"symbol": "SPY", "token": api_key}),
            "NASDAQ (QQQ)":  client.get("https://finnhub.io/api/v1/quote", params={"symbol": "QQQ", "token": api_key}),
            "Russell 2000 (IWM)": client.get("https://finnhub.io/api/v1/quote", params={"symbol": "IWM", "token": api_key}),
        }
        responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
    for (name, _), resp in zip(tasks.items(), responses):
        if isinstance(resp, Exception):
            continue
        try:
            d = resp.json()
            if d.get("c", 0) > 0:
                indices[name] = {"price": round(d["c"], 2), "change_pct": round(d.get("dp", 0), 2)}
        except Exception:
            pass
    return indices


async def _fetch_targeted_news(client: httpx.AsyncClient, risk_profile: str) -> List[dict]:
    """Fetch sector-specific news matched to the risk profile."""
    if not settings.news_api_key:
        return []
    queries = {
        "conservative": "dividend stocks bonds safe haven sector investing yield",
        "moderate": "earnings growth technology sector rotation quarterly results",
        "aggressive": "AI semiconductor earnings beat momentum breakout high growth tech",
    }
    query = queries.get(risk_profile, queries["moderate"])
    try:
        since = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        r = await client.get(
            "https://newsapi.org/v2/everything",
            params={"q": query, "apiKey": settings.news_api_key,
                    "pageSize": 20, "sortBy": "publishedAt", "language": "en", "from": since},
            timeout=10,
        )
        if r.status_code == 200:
            arts = r.json().get("articles", [])
            return [{"title": a.get("title",""), "source": a.get("source",{}).get("name",""),
                     "description": (a.get("description") or "")[:120]}
                    for a in arts[:15] if a.get("title") and len(a.get("title","")) > 20]
    except Exception as exc:
        logger.warning("NewsAPI fetch failed: {}", exc)
    return []


async def _fetch_finnhub_news(client: httpx.AsyncClient) -> List[dict]:
    """Fetch market news from Finnhub."""
    if not settings.finnhub_api_key:
        return []
    try:
        r = await client.get("https://finnhub.io/api/v1/news",
                              params={"category": "general", "token": settings.finnhub_api_key}, timeout=10)
        if r.status_code == 200:
            arts = r.json()[:15]
            return [{"title": a.get("headline",""), "source": a.get("source","Finnhub"),
                     "description": (a.get("summary") or "")[:120]}
                    for a in arts if a.get("headline")]
    except Exception as exc:
        logger.warning("Finnhub news fetch failed: {}", exc)
    return []


# ---------------------------------------------------------------------------
# Claude analytical prompt
# ---------------------------------------------------------------------------

def _build_analysis_prompt(
    risk_profile: str,
    horizon_months: int,
    sector_data: Dict[str, dict],
    indices: Dict[str, dict],
    headlines: List[dict],
    today: str,
) -> str:
    horizon = ("short-term (1-3 months)" if horizon_months <= 3 else
               "medium-term (6-12 months)" if horizon_months <= 12 else
               "long-term (1-5 years)")

    # Format sector performance table
    sector_lines = []
    for sector, data in sorted(sector_data.items(), key=lambda x: -x[1].get("change_pct", 0)):
        pct = data.get("change_pct", 0)
        arrow = "▲" if pct >= 0 else "▼"
        sector_lines.append(f"  {arrow} {sector:25s} {pct:+.2f}%")
    sector_text = "\n".join(sector_lines) if sector_lines else "  Sector data unavailable."

    # Format market indices
    idx_lines = []
    for name, data in indices.items():
        pct = data.get("change_pct", 0)
        arrow = "▲" if pct >= 0 else "▼"
        idx_lines.append(f"  {arrow} {name}: ${data['price']:.2f} ({pct:+.2f}%)")
    idx_text = "\n".join(idx_lines) if idx_lines else "  Market data unavailable."

    # Format news
    news_text = "\n".join(
        f"  [{i+1}] {a['title']}\n      {a['description'][:100]}" if a.get("description") else
        f"  [{i+1}] {a['title']}"
        for i, a in enumerate(headlines[:12])
    ) or "  No financial headlines available."

    profile_guidance = {
        "conservative": (
            "SELECT ONLY: Large-cap dividend stocks (yield ≥1.5%), defensive sectors "
            "(Consumer Staples, Healthcare, Utilities), broad market ETFs, bond ETFs. "
            "AVOID: Any stock with high beta (>1.2), speculative growth, crypto, biotech, EV startups. "
            "Focus: Capital preservation + steady income. Volatility < 20% annual."
        ),
        "moderate": (
            "SELECT: Quality large-cap growth + value blend (P/E < 35), established tech leaders, "
            "financial blue-chips, healthcare innovators, industrial leaders. Mix 60% growth + 40% value. "
            "AVOID: Speculative micro-caps, crypto, purely story-driven stocks with no earnings. "
            "Focus: 8-12% expected annual return. Balance risk and growth."
        ),
        "aggressive": (
            "SELECT: High-growth disruptors with strong momentum: AI/ML (semiconductors, data infrastructure), "
            "cybersecurity (cloud-native), SaaS with high NRR, crypto-adjacent, EV/clean energy, biotech innovation. "
            "INCLUDE mid-caps and emerging leaders, not just mega-caps. "
            "AVOID: Conservative blue-chips like JNJ, KO, WMT, PG — they belong in conservative portfolios. "
            "Focus: 15%+ expected growth, accept 30-60% volatility for outsized returns."
        ),
    }[risk_profile]

    seed = random.randint(100, 999)

    return f"""You are a senior portfolio manager at a quantitative hedge fund. Analyze the data below and select stocks.

TODAY: {today} | HORIZON: {horizon} | PROFILE: {risk_profile.upper()} | Run #{seed}

═══ LIVE MARKET DATA (from Finnhub, just now) ═══

MARKET INDICES (today's performance):
{idx_text}

SECTOR PERFORMANCE (today's change%):
{sector_text}

═══ LATEST FINANCIAL NEWS ═══
{news_text}

═══ YOUR TASK ═══

STEP 1 — SECTOR ANALYSIS:
Based on the sector performance data AND news above, identify:
- Which 2-3 sectors have the strongest momentum or catalyst TODAY?
- Which sectors should be avoided (declining or headwinds from news)?

STEP 2 — STOCK SELECTION:
Select exactly 25 US-listed stocks for a {risk_profile.upper()} portfolio.

CONSTRAINTS:
{profile_guidance}

RULES:
1. Each stock MUST have a specific current reason tied to the news OR sector momentum above
2. Do NOT pick generic "safe" choices — pick stocks with a SPECIFIC catalyst
3. Vary by sub-sector within your chosen sectors (no more than 5 stocks per sub-sector)
4. Include a mix of market caps (not all mega-caps)
5. The "reason" must reference something in the data above (sector trend, news event, etc.)

Return ONLY this JSON (no markdown, no text outside JSON):
{{
  "market_analysis": "2-3 sentences: what is the market doing today based on the data?",
  "hot_sectors": ["Sector1", "Sector2", "Sector3"],
  "avoid_sectors": ["Sector1"],
  "sector_reasoning": "Why these sectors given today's data",
  "stocks": [
    {{
      "symbol": "CRWD",
      "name": "CrowdStrike Holdings",
      "sector": "Cybersecurity",
      "reason": "Cybersecurity sector up 3.2% on news of new federal mandate; CRWD market leader",
      "conviction": "high",
      "catalyst": "sector_momentum"
    }}
  ]
}}

catalyst values: "news_event" | "sector_momentum" | "earnings_catalyst" | "macro_tailwind"
conviction values: "high" | "medium" | "low"
"""


# ---------------------------------------------------------------------------
# Dynamic momentum-based fallback (Finnhub data, not static list)
# ---------------------------------------------------------------------------

async def _momentum_fallback(risk_profile: str, target_count: int = 30) -> Dict:
    """
    When Claude fails: fetch Finnhub quotes for the full candidate pool,
    rank by daily momentum (dp%), return top stocks.
    This is a REAL data-driven fallback, not a static list.
    """
    pool = _CANDIDATE_POOL.get(risk_profile, _CANDIDATE_POOL["moderate"])
    if not settings.finnhub_api_key:
        # Last resort: random sample
        sampled = random.sample(pool, min(target_count, len(pool)))
        stocks = [{"symbol": s, "name": s, "sector": "Unknown",
                   "reason": "Selected by random fallback", "conviction": "low"}
                  for s in sampled]
        return {"market_context": "Fallback mode (no API key)", "top_sectors": [],
                "stocks": stocks, "source": "fallback_random"}

    logger.info("Running momentum-based fallback for {} profile ({} candidates)", risk_profile, len(pool))
    async with httpx.AsyncClient(timeout=12) as client:
        tasks = [
            client.get("https://finnhub.io/api/v1/quote", params={"symbol": sym, "token": settings.finnhub_api_key})
            for sym in pool
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    scored: List[Tuple[str, float]] = []
    for sym, resp in zip(pool, responses):
        if isinstance(resp, Exception):
            continue
        try:
            d = resp.json()
            if d.get("c", 0) > 0:
                scored.append((sym, float(d.get("dp", 0))))
        except Exception:
            pass

    # Sort by momentum descending (best performers first)
    scored.sort(key=lambda x: -x[1])
    selected = scored[:target_count]

    stocks = [
        {
            "symbol": sym,
            "name": sym,
            "sector": _get_sector_hint(sym),
            "reason": f"Momentum-based: today {pct:+.2f}%",
            "conviction": "high" if pct > 1.0 else "medium" if pct > 0 else "low",
        }
        for sym, pct in selected
    ]
    logger.info("Momentum fallback selected {} stocks (top: {})", len(stocks), selected[:3])
    return {
        "market_context": f"Momentum-based selection from {len(pool)} candidates. Claude unavailable.",
        "top_sectors": [],
        "sector_reasoning": "",
        "stocks": stocks,
        "source": "fallback_momentum",
    }


def _get_sector_hint(symbol: str) -> str:
    """Return a rough sector label based on symbol knowledge."""
    tech = {"NVDA","AMD","ARM","SMCI","MRVL","AVGO","MU","CRWD","NET","PANW","ZS","DDOG",
            "SNOW","MDB","NOW","PLTR","AI","PATH","SOUN","ORCL","CSCO","INTC"}
    fin  = {"COIN","MARA","MSTR","RIOT","SQ","SOFI","AFRM","UPST","HOOD","JPM","V","MA","GS"}
    health={"MRNA","BNTX","CRSP","RXRX","HIMS","JNJ","PFE","ABBV","MRK","UNH"}
    energy={"ENPH","SEDG","PLUG","BE","BLNK","XOM","CVX","COP","FSLR"}
    if symbol in tech:    return "Technology"
    if symbol in fin:     return "Finance"
    if symbol in health:  return "Healthcare"
    if symbol in energy:  return "Energy"
    return "Mixed"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def select_stocks_with_ai(
    risk_profile: str,
    investment_horizon_months: int = 12,
    fallback_symbols: Optional[List[str]] = None,  # reserved for future custom universes
) -> Dict:
    """
    Full AI-driven stock selection:
    1. Fetch real sector data + news
    2. Claude Sonnet analyses data and picks stocks with specific catalysts
    3. If Claude fails → momentum-based dynamic fallback from Finnhub data
    """
    today = datetime.now().strftime("%B %d, %Y (%A)")

    # ── Step 1: Parallel data collection ──────────────────────────────────
    logger.info("Fetching market data for {} profile stock selection", risk_profile)
    async with httpx.AsyncClient(timeout=12) as client:
        sector_task = asyncio.create_task(
            _fetch_sector_performance(settings.finnhub_api_key or "")
        )
        index_task  = asyncio.create_task(
            _fetch_market_indices(settings.finnhub_api_key or "")
        )
        news_task   = asyncio.create_task(_fetch_targeted_news(client, risk_profile))
        fh_task     = asyncio.create_task(_fetch_finnhub_news(client))

        sector_data, indices, news_api, fh_news = await asyncio.gather(
            sector_task, index_task, news_task, fh_task, return_exceptions=True
        )

    if isinstance(sector_data, Exception): sector_data = {}
    if isinstance(indices, Exception):     indices = {}
    if isinstance(news_api, Exception):    news_api = []
    if isinstance(fh_news, Exception):     fh_news  = []

    all_news = news_api + fh_news
    logger.info(
        "Data collected — sectors: {}, indices: {}, news: {} articles",
        len(sector_data), len(indices), len(all_news),
    )

    # ── Step 2: Claude analysis ────────────────────────────────────────────
    if not settings.anthropic_api_key:
        logger.warning("No ANTHROPIC_API_KEY — running momentum fallback")
        return await _momentum_fallback(risk_profile)

    prompt = _build_analysis_prompt(
        risk_profile, investment_horizon_months,
        sector_data, indices, all_news, today,
    )

    for attempt in range(2):  # max 2 attempts before falling back
        try:
            import anthropic
            # Use Sonnet for genuine analytical quality
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            msg = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=8000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = msg.content[0].text.strip()

            # Extract JSON
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(m.group() if m else raw)

            stocks = data.get("stocks", [])
            # Deduplicate, normalise symbols
            seen, unique = set(), []
            for s in stocks:
                sym = s.get("symbol", "").upper().strip()
                if sym and sym not in seen:
                    seen.add(sym)
                    s["symbol"] = sym
                    unique.append(s)

            if len(unique) < 8:
                logger.warning("Claude attempt {} returned only {} stocks — retrying", attempt+1, len(unique))
                continue

            logger.info(
                "Claude Sonnet selected {} stocks for {} profile (source=claude, sectors={})",
                len(unique), risk_profile, data.get("hot_sectors", []),
            )
            return {
                "market_context":   data.get("market_analysis", data.get("market_context", "")),
                "top_sectors":      data.get("hot_sectors", []),
                "sector_reasoning": data.get("sector_reasoning", ""),
                "stocks":           unique,
                "source":           "claude",
            }

        except Exception as exc:
            logger.error("Claude attempt {} failed: {}", attempt+1, exc)
            if attempt == 0:
                logger.info("Retrying Claude with same prompt…")
                await asyncio.sleep(1)

    # ── Step 3: Momentum-based dynamic fallback ────────────────────────────
    logger.warning("Both Claude attempts failed — running Finnhub momentum fallback")
    return await _momentum_fallback(risk_profile)
