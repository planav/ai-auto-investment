"""Market data API endpoints."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.services.market_data import market_data_service, StockQuote

router = APIRouter()


class QuoteResponse(BaseModel):
    """Stock quote response model."""
    symbol: str
    price: float
    change: float
    change_percent: float
    high: float
    low: float
    open: float
    previous_close: float
    timestamp: int
    is_positive: bool


class MarketOverviewResponse(BaseModel):
    """Market overview response."""
    indices: dict
    timestamp: str
    market_status: str


class StockSearchResult(BaseModel):
    """Stock search result."""
    symbol: str
    name: str
    type: Optional[str] = None


class AIStockAnalysisResponse(BaseModel):
    """AI stock analysis response."""
    symbol: str
    signal: str
    confidence: int
    rationale: str
    key_factors: List[str]
    risk_level: str


@router.get("/quote/{symbol}", response_model=QuoteResponse)
async def get_quote(
    symbol: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get real-time quote for a stock symbol."""
    quote = await market_data_service.get_quote(symbol)
    
    if not quote:
        raise HTTPException(
            status_code=404,
            detail=f"Quote not found for symbol: {symbol}"
        )
    
    return QuoteResponse(
        symbol=quote.symbol,
        price=quote.price,
        change=quote.change,
        change_percent=quote.change_percent,
        high=quote.high,
        low=quote.low,
        open=quote.open,
        previous_close=quote.previous_close,
        timestamp=quote.timestamp,
        is_positive=quote.is_positive
    )


@router.get("/quotes", response_model=List[QuoteResponse])
async def get_batch_quotes(
    symbols: str = Query(..., description="Comma-separated list of stock symbols"),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get real-time quotes for multiple symbols."""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    if len(symbol_list) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 symbols allowed per request"
        )
    
    quotes = await market_data_service.get_batch_quotes(symbol_list)
    
    return [
        QuoteResponse(
            symbol=q.symbol,
            price=q.price,
            change=q.change,
            change_percent=q.change_percent,
            high=q.high,
            low=q.low,
            open=q.open,
            previous_close=q.previous_close,
            timestamp=q.timestamp,
            is_positive=q.is_positive
        )
        for q in quotes.values()
    ]


@router.get("/popular", response_model=List[QuoteResponse])
async def get_popular_stocks(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get quotes for popular stocks."""
    quotes = await market_data_service.get_popular_stocks()
    
    return [
        QuoteResponse(
            symbol=q.symbol,
            price=q.price,
            change=q.change,
            change_percent=q.change_percent,
            high=q.high,
            low=q.low,
            open=q.open,
            previous_close=q.previous_close,
            timestamp=q.timestamp,
            is_positive=q.is_positive
        )
        for q in quotes.values()
    ]


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get market overview with major indices."""
    overview = await market_data_service.get_market_overview()
    return MarketOverviewResponse(**overview)


@router.get("/search", response_model=List[StockSearchResult])
async def search_stocks(
    query: str = Query(..., min_length=1, max_length=50),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Search for stock symbols."""
    results = await market_data_service.search_symbols(query)
    return [StockSearchResult(**r) for r in results]


@router.get("/ai-analysis/{symbol}", response_model=AIStockAnalysisResponse)
async def get_ai_stock_analysis(
    symbol: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get AI analysis for a stock."""
    from app.services.llm_service import llm_service
    
    # Get quote data
    quote = await market_data_service.get_quote(symbol)
    if not quote:
        raise HTTPException(
            status_code=404,
            detail=f"Stock not found: {symbol}"
        )
    
    # Get company profile
    profile = await market_data_service.finnhub.get_company_profile(symbol)
    
    # Prepare data for AI analysis
    quote_data = {
        "price": quote.price,
        "change": quote.change,
        "change_percent": quote.change_percent,
        "high": quote.high,
        "low": quote.low,
        "open": quote.open,
        "previous_close": quote.previous_close
    }
    
    company_info = None
    if profile:
        company_info = {
            "name": profile.name,
            "industry": profile.industry,
            "sector": profile.sector,
            "market_cap": profile.market_cap
        }
    
    # Get AI analysis
    analysis = await llm_service.analyze_stock(symbol, quote_data, company_info)
    
    if not analysis:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI analysis"
        )
    
    return AIStockAnalysisResponse(
        symbol=analysis.symbol,
        signal=analysis.signal,
        confidence=analysis.confidence,
        rationale=analysis.rationale,
        key_factors=analysis.key_factors,
        risk_level=analysis.risk_level
    )
