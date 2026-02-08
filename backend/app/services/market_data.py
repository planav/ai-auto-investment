"""Market data service for fetching real-time and historical stock data."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import httpx
import pandas as pd
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


@dataclass
class StockQuote:
    """Real-time stock quote data."""
    symbol: str
    price: float
    change: float
    change_percent: float
    high: float
    low: float
    open: float
    previous_close: float
    timestamp: int
    
    @property
    def is_positive(self) -> bool:
        return self.change >= 0


@dataclass
class CompanyProfile:
    """Company profile information."""
    symbol: str
    name: str
    industry: str
    sector: str
    country: str
    market_cap: Optional[float] = None
    website: Optional[str] = None
    description: Optional[str] = None


@dataclass
class MarketNews:
    """Market news item."""
    headline: str
    source: str
    url: str
    datetime: int
    summary: Optional[str] = None
    image: Optional[str] = None


class FinnhubClient:
    """Client for Finnhub API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.finnhub_api_key
        self.base_url = "https://finnhub.io/api/v1"
        self._client: Optional[httpx.AsyncClient] = None
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def get_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get real-time quote for a symbol."""
        try:
            client = await self._get_client()
            url = f"{self.base_url}/quote"
            params = {"symbol": symbol.upper(), "token": self.api_key}
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API error
            if data.get("error"):
                logger.error(f"Finnhub API error for {symbol}: {data['error']}")
                return None
            
            return StockQuote(
                symbol=symbol.upper(),
                price=data.get("c", 0.0),
                change=data.get("d", 0.0),
                change_percent=data.get("dp", 0.0),
                high=data.get("h", 0.0),
                low=data.get("l", 0.0),
                open=data.get("o", 0.0),
                previous_close=data.get("pc", 0.0),
                timestamp=data.get("t", 0)
            )
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    async def get_batch_quotes(self, symbols: List[str]) -> Dict[str, StockQuote]:
        """Get quotes for multiple symbols."""
        tasks = [self.get_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        quotes = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, StockQuote):
                quotes[symbol.upper()] = result
            elif isinstance(result, Exception):
                logger.error(f"Error fetching {symbol}: {result}")
        
        return quotes
    
    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """Get company profile."""
        try:
            client = await self._get_client()
            url = f"{self.base_url}/stock/profile2"
            params = {"symbol": symbol.upper(), "token": self.api_key}
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data or data.get("error"):
                return None
            
            return CompanyProfile(
                symbol=symbol.upper(),
                name=data.get("name", ""),
                industry=data.get("finnhubIndustry", ""),
                sector=data.get("sector", ""),
                country=data.get("country", ""),
                market_cap=data.get("marketCapitalization"),
                website=data.get("weburl"),
                description=data.get("description")
            )
        except Exception as e:
            logger.error(f"Error fetching profile for {symbol}: {e}")
            return None
    
    async def get_candles(
        self,
        symbol: str,
        resolution: str = "D",
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """Get historical candlestick data."""
        try:
            # Default to last year if not specified
            if to_timestamp is None:
                to_timestamp = int(datetime.now().timestamp())
            if from_timestamp is None:
                from_timestamp = int((datetime.now() - timedelta(days=365)).timestamp())
            
            client = await self._get_client()
            url = f"{self.base_url}/stock/candle"
            params = {
                "symbol": symbol.upper(),
                "resolution": resolution,
                "from": from_timestamp,
                "to": to_timestamp,
                "token": self.api_key
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("s") != "ok":
                logger.error(f"Error fetching candles for {symbol}: {data}")
                return None
            
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(data["t"], unit="s"),
                "open": data["o"],
                "high": data["h"],
                "low": data["l"],
                "close": data["c"],
                "volume": data["v"]
            })
            
            return df
        except Exception as e:
            logger.error(f"Error fetching candles for {symbol}: {e}")
            return None
    
    async def get_news(
        self,
        symbol: Optional[str] = None,
        category: str = "general",
        min_id: Optional[int] = None
    ) -> List[MarketNews]:
        """Get market news."""
        try:
            client = await self._get_client()
            
            if symbol:
                url = f"{self.base_url}/company-news"
                # Get news from last 7 days
                to_date = datetime.now()
                from_date = to_date - timedelta(days=7)
                params = {
                    "symbol": symbol.upper(),
                    "from": from_date.strftime("%Y-%m-%d"),
                    "to": to_date.strftime("%Y-%m-%d"),
                    "token": self.api_key
                }
            else:
                url = f"{self.base_url}/news"
                params = {"category": category, "token": self.api_key}
                if min_id:
                    params["minId"] = min_id
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            news_items = []
            for item in data[:20]:  # Limit to 20 items
                news_items.append(MarketNews(
                    headline=item.get("headline", ""),
                    source=item.get("source", ""),
                    url=item.get("url", ""),
                    datetime=item.get("datetime", 0),
                    summary=item.get("summary"),
                    image=item.get("image")
                ))
            
            return news_items
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    async def get_market_indices(self) -> Dict[str, Dict[str, Any]]:
        """Get major market indices data."""
        indices = {
            "SPY": "S&P 500",
            "QQQ": "NASDAQ",
            "DIA": "Dow Jones",
            "IWM": "Russell 2000"
        }
        
        quotes = await self.get_batch_quotes(list(indices.keys()))
        
        result = {}
        for symbol, name in indices.items():
            quote = quotes.get(symbol)
            if quote:
                result[symbol] = {
                    "name": name,
                    "price": quote.price,
                    "change": quote.change,
                    "change_percent": quote.change_percent
                }
        
        return result


class MarketDataService:
    """High-level market data service with caching."""
    
    def __init__(self):
        self.finnhub = FinnhubClient()
        self._cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, datetime] = {}
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key."""
        return f"{prefix}:{identifier}"
    
    def _is_cache_valid(self, key: str, ttl_seconds: int = 60) -> bool:
        """Check if cache entry is still valid."""
        if key not in self._cache_ttl:
            return False
        expiry = self._cache_ttl[key]
        return datetime.now() < expiry
    
    def _set_cache(self, key: str, value: Any, ttl_seconds: int = 60):
        """Set cache entry with TTL."""
        self._cache[key] = value
        self._cache_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    async def get_quote(self, symbol: str, use_cache: bool = True) -> Optional[StockQuote]:
        """Get quote with caching."""
        cache_key = self._get_cache_key("quote", symbol.upper())
        
        if use_cache and self._is_cache_valid(cache_key, 60):
            return self._cache.get(cache_key)
        
        quote = await self.finnhub.get_quote(symbol)
        if quote:
            self._set_cache(cache_key, quote, 60)
        
        return quote
    
    async def get_batch_quotes(self, symbols: List[str]) -> Dict[str, StockQuote]:
        """Get multiple quotes with individual caching."""
        result = {}
        symbols_to_fetch = []
        
        # Check cache first
        for symbol in symbols:
            cache_key = self._get_cache_key("quote", symbol.upper())
            if self._is_cache_valid(cache_key, 60):
                result[symbol.upper()] = self._cache[cache_key]
            else:
                symbols_to_fetch.append(symbol)
        
        # Fetch missing quotes
        if symbols_to_fetch:
            quotes = await self.finnhub.get_batch_quotes(symbols_to_fetch)
            for symbol, quote in quotes.items():
                cache_key = self._get_cache_key("quote", symbol)
                self._set_cache(cache_key, quote, 60)
                result[symbol] = quote
        
        return result
    
    async def get_popular_stocks(self) -> Dict[str, StockQuote]:
        """Get quotes for popular stocks."""
        popular_symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "META", "NVDA", "NFLX", "AMD", "INTC",
            "CRM", "ADBE", "PYPL", "UBER", "COIN"
        ]
        return await self.get_batch_quotes(popular_symbols)
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get market overview with indices and sentiment."""
        cache_key = "market:overview"
        
        if self._is_cache_valid(cache_key, 300):  # 5 minute cache
            return self._cache.get(cache_key)
        
        indices = await self.finnhub.get_market_indices()
        
        overview = {
            "indices": indices,
            "timestamp": datetime.now().isoformat(),
            "market_status": "open"  # Could be enhanced with actual market hours
        }
        
        self._set_cache(cache_key, overview, 300)
        return overview
    
    async def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """Search for stock symbols."""
        try:
            client = await self.finnhub._get_client()
            url = f"{self.finnhub.base_url}/search"
            params = {"q": query, "token": self.finnhub.api_key}
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("result", [])[:10]:
                results.append({
                    "symbol": item.get("symbol"),
                    "name": item.get("description"),
                    "type": item.get("type")
                })
            
            return results
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return []
    
    async def close(self):
        """Cleanup resources."""
        await self.finnhub.close()


# Global instances
finnhub_client = FinnhubClient()
market_data_service = MarketDataService()
