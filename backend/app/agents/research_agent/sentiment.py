"""Sentiment analyzer — uses NewsAPI for real news, keyword scoring for sentiment."""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import httpx
from loguru import logger


@dataclass
class NewsArticle:
    title: str
    source: str
    published_at: datetime
    sentiment_score: float   # -1 to +1
    relevance_score: float   # 0 to 1
    url: Optional[str] = None


@dataclass
class SentimentAnalysis:
    symbol: str
    overall_sentiment: float   # -1 to +1
    sentiment_trend: str       # improving | stable | declining
    news_count: int
    bullish_count: int
    bearish_count: int
    neutral_count: int
    recent_articles: List[NewsArticle] = field(default_factory=list)
    key_topics: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Keyword lists for simple title-based sentiment scoring
# ---------------------------------------------------------------------------
_BULLISH_WORDS = {
    "beats", "beat", "surges", "soars", "jumps", "rises", "gains", "record",
    "profit", "growth", "revenue", "upgrade", "outperforms", "buy", "strong",
    "rally", "breakthrough", "bullish", "positive", "upbeat", "exceeds",
    "raised", "dividend", "expansion", "partnership", "innovation", "award",
}
_BEARISH_WORDS = {
    "misses", "miss", "falls", "drops", "plunges", "declines", "loss",
    "layoffs", "lawsuit", "recall", "downgrade", "sell", "weak", "poor",
    "bearish", "negative", "debt", "warning", "cut", "recession", "risk",
    "fraud", "investigation", "fine", "penalty", "concern", "trouble",
}

_NEWSAPI_BASE = "https://newsapi.org/v2/everything"


def _score_title(title: str) -> float:
    """Return a sentiment score [-1, +1] from a news headline."""
    words = set(title.lower().split())
    bull = len(words & _BULLISH_WORDS)
    bear = len(words & _BEARISH_WORDS)
    total = bull + bear
    if total == 0:
        return 0.0
    return (bull - bear) / total


def _neutral_sentiment(symbol: str) -> SentimentAnalysis:
    """Return a neutral sentiment when data is unavailable."""
    return SentimentAnalysis(
        symbol=symbol,
        overall_sentiment=0.0,
        sentiment_trend="stable",
        news_count=0,
        bullish_count=0,
        bearish_count=0,
        neutral_count=0,
        recent_articles=[],
        key_topics=["market", "price action"],
    )


class SentimentAnalyzer:
    """Analyzes market sentiment from real NewsAPI headlines."""

    def __init__(self):
        self.sentiment_cache: Dict[str, SentimentAnalysis] = {}
        self._api_key: Optional[str] = None

    def _get_api_key(self) -> Optional[str]:
        if self._api_key is None:
            from app.core.config import get_settings
            self._api_key = get_settings().news_api_key or os.getenv("NEWS_API_KEY")
        return self._api_key

    async def analyze_sentiment(self, symbol: str) -> SentimentAnalysis:
        """Fetch real news from NewsAPI and score sentiment via keyword matching."""
        if symbol in self.sentiment_cache:
            return self.sentiment_cache[symbol]

        api_key = self._get_api_key()
        if not api_key:
            logger.debug("NEWS_API_KEY not set — using neutral sentiment for {}", symbol)
            return _neutral_sentiment(symbol)

        # Map symbol to a more descriptive search term
        search_term = symbol
        company_names = {
            "AAPL": "Apple stock", "MSFT": "Microsoft stock",
            "GOOGL": "Google Alphabet", "AMZN": "Amazon stock",
            "NVDA": "NVIDIA stock", "META": "Meta Facebook",
            "TSLA": "Tesla stock", "AMD": "AMD semiconductor",
            "SPY": "S&P 500 ETF", "QQQ": "Nasdaq QQQ ETF",
            "VTI": "Vanguard VTI", "BND": "Vanguard BND bond",
            "SHOP": "Shopify stock", "CRM": "Salesforce stock",
        }
        search_term = company_names.get(symbol, f"{symbol} stock")

        try:
            params = {
                "q": search_term,
                "apiKey": api_key,
                "pageSize": 20,
                "sortBy": "publishedAt",
                "language": "en",
                "from": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
            }
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.get(_NEWSAPI_BASE, params=params)
                if resp.status_code != 200:
                    logger.warning("NewsAPI {} for {}: {}", resp.status_code, symbol, resp.text[:200])
                    return _neutral_sentiment(symbol)
                articles_raw = resp.json().get("articles", [])
        except Exception as exc:
            logger.warning("NewsAPI request failed for {}: {}", symbol, exc)
            return _neutral_sentiment(symbol)

        articles: List[NewsArticle] = []
        scores: List[float] = []
        topics: set = set()

        for art in articles_raw[:15]:
            title = art.get("title") or ""
            description = art.get("description") or ""
            combined = f"{title} {description}"
            score = _score_title(combined)
            scores.append(score)
            articles.append(NewsArticle(
                title=title[:120],
                source=art.get("source", {}).get("name", "Unknown"),
                published_at=datetime.fromisoformat(
                    art.get("publishedAt", datetime.utcnow().isoformat()).replace("Z", "+00:00")
                ),
                sentiment_score=score,
                relevance_score=1.0,
                url=art.get("url"),
            ))
            # Extract simple topics from title words
            for word in title.lower().split():
                if len(word) > 4 and word.isalpha():
                    topics.add(word)

        if not scores:
            return _neutral_sentiment(symbol)

        bullish = sum(1 for s in scores if s > 0.1)
        bearish = sum(1 for s in scores if s < -0.1)
        neutral = len(scores) - bullish - bearish
        overall = float(sum(scores) / len(scores))

        trend = ("improving" if bullish > bearish * 1.3
                 else "declining" if bearish > bullish * 1.3
                 else "stable")

        result = SentimentAnalysis(
            symbol=symbol,
            overall_sentiment=overall,
            sentiment_trend=trend,
            news_count=len(scores),
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            recent_articles=articles[:5],
            key_topics=list(topics)[:6],
        )
        self.sentiment_cache[symbol] = result
        logger.info("Sentiment for {}: overall={:.2f} trend={} news={}", symbol, overall, trend, len(scores))
        return result

    async def analyze_sentiments(self, symbols: List[str]) -> Dict[str, SentimentAnalysis]:
        import asyncio
        results = await asyncio.gather(
            *[self.analyze_sentiment(s) for s in symbols], return_exceptions=True
        )
        return {
            sym: (res if isinstance(res, SentimentAnalysis) else _neutral_sentiment(sym))
            for sym, res in zip(symbols, results)
        }

    def get_sentiment_score(self, symbol: str) -> float:
        """Return normalized sentiment score 0-100."""
        if symbol not in self.sentiment_cache:
            return 50.0
        return (self.sentiment_cache[symbol].overall_sentiment + 1) * 50

    def filter_by_sentiment(
        self,
        analyses: Dict[str, SentimentAnalysis],
        min_sentiment: float = -0.3,
        exclude_declining: bool = True,
    ) -> List[str]:
        return [
            sym for sym, a in analyses.items()
            if a.overall_sentiment >= min_sentiment
            and not (exclude_declining and a.sentiment_trend == "declining")
        ]
