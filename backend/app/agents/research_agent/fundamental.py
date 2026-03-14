from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FundamentalMetrics:
    """Fundamental analysis metrics for an asset."""
    symbol: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    roe: Optional[float] = None
    revenue_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    free_cash_flow: Optional[float] = None
    
    # Scores
    value_score: float = 0.0  # 0-100
    quality_score: float = 0.0  # 0-100
    growth_score: float = 0.0  # 0-100
    overall_score: float = 0.0  # 0-100


class FundamentalAnalyzer:
    """Analyzes fundamental metrics of assets using real market data."""
    
    def __init__(self):
        self.metrics_cache: Dict[str, FundamentalMetrics] = {}
    
    async def analyze_asset(self, symbol: str) -> FundamentalMetrics:
        """Analyze fundamental metrics for a single asset using yfinance."""
        import asyncio
        import yfinance as yf

        def _fetch():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info or {}
                return info
            except Exception:
                return {}

        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(None, _fetch)

        # Extract fundamental metrics (handle missing fields gracefully)
        pe_ratio = info.get("forwardPE") or info.get("trailingPE")
        pb_ratio = info.get("priceToBook")
        raw_dte = info.get("debtToEquity")
        debt_to_equity = raw_dte / 100.0 if raw_dte is not None else None
        roe = info.get("returnOnEquity")
        revenue_growth = info.get("revenueGrowth")
        profit_margin = info.get("profitMargins")
        free_cash_flow = info.get("freeCashflow")

        metrics = FundamentalMetrics(
            symbol=symbol,
            pe_ratio=float(pe_ratio) if pe_ratio is not None else None,
            pb_ratio=float(pb_ratio) if pb_ratio is not None else None,
            debt_to_equity=float(debt_to_equity) if debt_to_equity is not None else None,
            roe=float(roe) if roe is not None else None,
            revenue_growth=float(revenue_growth) if revenue_growth is not None else None,
            profit_margin=float(profit_margin) if profit_margin is not None else None,
            free_cash_flow=float(free_cash_flow) if free_cash_flow is not None else None,
        )
        
        # Calculate scores
        metrics.value_score = self._calculate_value_score(metrics)
        metrics.quality_score = self._calculate_quality_score(metrics)
        metrics.growth_score = self._calculate_growth_score(metrics)
        metrics.overall_score = (
            metrics.value_score * 0.3 +
            metrics.quality_score * 0.4 +
            metrics.growth_score * 0.3
        )
        
        self.metrics_cache[symbol] = metrics
        return metrics
    
    async def analyze_assets(self, symbols: List[str]) -> Dict[str, FundamentalMetrics]:
        """Analyze fundamental metrics for multiple assets."""
        results = {}
        for symbol in symbols:
            results[symbol] = await self.analyze_asset(symbol)
        return results
    
    def _calculate_value_score(self, metrics: FundamentalMetrics) -> float:
        """Calculate value score based on valuation metrics."""
        score = 50.0  # Base score
        
        if metrics.pe_ratio:
            if metrics.pe_ratio < 15:
                score += 25
            elif metrics.pe_ratio < 25:
                score += 10
            else:
                score -= 10
        
        if metrics.pb_ratio:
            if metrics.pb_ratio < 2:
                score += 15
            elif metrics.pb_ratio < 4:
                score += 5
            else:
                score -= 5
        
        return max(0, min(100, score))
    
    def _calculate_quality_score(self, metrics: FundamentalMetrics) -> float:
        """Calculate quality score based on profitability and stability."""
        score = 50.0
        
        if metrics.roe:
            if metrics.roe > 0.20:
                score += 25
            elif metrics.roe > 0.15:
                score += 15
            elif metrics.roe > 0.10:
                score += 5
            else:
                score -= 10
        
        if metrics.debt_to_equity:
            if metrics.debt_to_equity < 0.5:
                score += 15
            elif metrics.debt_to_equity < 1.0:
                score += 5
            else:
                score -= 10
        
        if metrics.profit_margin:
            if metrics.profit_margin > 0.20:
                score += 10
            elif metrics.profit_margin < 0.05:
                score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_growth_score(self, metrics: FundamentalMetrics) -> float:
        """Calculate growth score based on growth metrics."""
        score = 50.0
        
        if metrics.revenue_growth:
            if metrics.revenue_growth > 0.30:
                score += 30
            elif metrics.revenue_growth > 0.15:
                score += 20
            elif metrics.revenue_growth > 0.05:
                score += 10
            elif metrics.revenue_growth < 0:
                score -= 15
        
        if metrics.free_cash_flow and metrics.free_cash_flow > 0:
            score += 10
        
        return max(0, min(100, score))
    
    def screen_assets(
        self,
        metrics: Dict[str, FundamentalMetrics],
        min_score: float = 60.0,
        max_assets: int = 50
    ) -> List[str]:
        """Screen assets based on fundamental criteria."""
        filtered = [
            symbol for symbol, m in metrics.items()
            if m.overall_score >= min_score
        ]
        
        # Sort by overall score and take top assets
        filtered.sort(
            key=lambda s: metrics[s].overall_score,
            reverse=True
        )
        
        return filtered[:max_assets]
