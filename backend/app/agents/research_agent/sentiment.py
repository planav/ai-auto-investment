from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random


@dataclass
class NewsArticle:
    """News article data structure."""
    title: str
    source: str
    published_at: datetime
    sentiment_score: float  # -1 to 1
    relevance_score: float  # 0 to 1
    url: Optional[str] = None


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result for an asset."""
    symbol: str
    overall_sentiment: float  # -1 to 1
    sentiment_trend: str  # improving, stable, declining
    news_count: int
    bullish_count: int
    bearish_count: int
    neutral_count: int
    recent_articles: List[NewsArticle]
    key_topics: List[str]


class SentimentAnalyzer:
    """Analyzes market sentiment from news and social media."""
    
    def __init__(self):
        self.sentiment_cache: Dict[str, SentimentAnalysis] = {}
        self.sample_topics = [
            "earnings", "revenue", "growth", "innovation", "partnership",
            "expansion", "acquisition", "product launch", "market share",
            "regulatory", "competition", "leadership", "sustainability"
        ]
    
    async def analyze_sentiment(self, symbol: str) -> SentimentAnalysis:
        """Analyze sentiment for a single asset."""
        # In production, fetch from news APIs and social media
        # For now, generate realistic mock data
        
        news_count = random.randint(10, 50)
        bullish = random.randint(0, news_count)
        bearish = random.randint(0, news_count - bullish)
        neutral = news_count - bullish - bearish
        
        overall = (bullish - bearish) / news_count if news_count > 0 else 0
        
        # Generate recent articles
        articles = []
        for i in range(min(5, news_count)):
            sentiment = random.uniform(-0.8, 0.8)
            articles.append(NewsArticle(
                title=f"{'Positive' if sentiment > 0 else 'Negative'} news about {symbol}",
                source=random.choice(["Bloomberg", "Reuters", "CNBC", "WSJ", "FT"]),
                published_at=datetime.now() - timedelta(hours=random.randint(1, 72)),
                sentiment_score=sentiment,
                relevance_score=random.uniform(0.5, 1.0),
            ))
        
        # Determine trend
        if bullish > bearish * 1.5:
            trend = "improving"
        elif bearish > bullish * 1.5:
            trend = "declining"
        else:
            trend = "stable"
        
        analysis = SentimentAnalysis(
            symbol=symbol,
            overall_sentiment=overall,
            sentiment_trend=trend,
            news_count=news_count,
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            recent_articles=articles,
            key_topics=random.sample(self.sample_topics, k=random.randint(3, 6)),
        )
        
        self.sentiment_cache[symbol] = analysis
        return analysis
    
    async def analyze_sentiments(self, symbols: List[str]) -> Dict[str, SentimentAnalysis]:
        """Analyze sentiment for multiple assets."""
        results = {}
        for symbol in symbols:
            results[symbol] = await self.analyze_sentiment(symbol)
        return results
    
    def get_sentiment_score(self, symbol: str) -> float:
        """Get normalized sentiment score (0-100)."""
        if symbol not in self.sentiment_cache:
            return 50.0
        
        sentiment = self.sentiment_cache[symbol].overall_sentiment
        # Convert -1 to 1 range to 0 to 100
        return (sentiment + 1) * 50
    
    def filter_by_sentiment(
        self,
        analyses: Dict[str, SentimentAnalysis],
        min_sentiment: float = -0.3,
        exclude_declining: bool = True
    ) -> List[str]:
        """Filter assets by sentiment criteria."""
        filtered = []
        
        for symbol, analysis in analyses.items():
            if analysis.overall_sentiment < min_sentiment:
                continue
            
            if exclude_declining and analysis.sentiment_trend == "declining":
                continue
            
            filtered.append(symbol)
        
        return filtered
