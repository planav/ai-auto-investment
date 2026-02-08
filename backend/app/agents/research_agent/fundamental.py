from typing import Dict, List, Optional
from dataclasses import dataclass
import random


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
    """Analyzes fundamental metrics of assets."""
    
    def __init__(self):
        self.metrics_cache: Dict[str, FundamentalMetrics] = {}
    
    async def analyze_asset(self, symbol: str) -> FundamentalMetrics:
        """Analyze fundamental metrics for a single asset."""
        # In production, fetch from financial data APIs
        # For now, generate realistic mock data
        
        metrics = FundamentalMetrics(
            symbol=symbol,
            pe_ratio=random.uniform(10, 40),
            pb_ratio=random.uniform(1, 5),
            debt_to_equity=random.uniform(0.2, 1.5),
            roe=random.uniform(0.05, 0.30),
            revenue_growth=random.uniform(-0.1, 0.5),
            profit_margin=random.uniform(0.05, 0.25),
            free_cash_flow=random.uniform(1e6, 1e9),
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
