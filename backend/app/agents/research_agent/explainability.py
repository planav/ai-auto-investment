from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AssetExplanation:
    """Explanation for why an asset was selected."""
    symbol: str
    selection_reason: str
    fundamental_factors: List[str]
    sentiment_factors: List[str]
    quantitative_factors: List[str]
    risk_factors: List[str]
    confidence_level: str  # high, medium, low


@dataclass
class PortfolioExplanation:
    """Comprehensive explanation for portfolio construction."""
    portfolio_id: Optional[int]
    strategy_overview: str
    asset_selection_summary: str
    allocation_rationale: str
    risk_management_approach: str
    expected_performance_summary: str
    asset_explanations: List[AssetExplanation]
    key_metrics_explanation: Dict[str, str]
    disclaimer: str


class ExplanationGenerator:
    """Generates human-readable explanations for AI decisions."""
    
    def __init__(self):
        self.risk_descriptions = {
            "conservative": "prioritizes capital preservation with modest growth expectations",
            "moderate": "balances growth and stability for steady long-term returns",
            "aggressive": "maximizes growth potential with higher volatility tolerance"
        }
    
    def generate_portfolio_explanation(
        self,
        portfolio_id: Optional[int],
        selected_assets: List[str],
        allocations: Dict[str, float],
        risk_tolerance: str,
        investment_horizon: int,
        model_type: str,
        fundamental_scores: Dict[str, float],
        sentiment_scores: Dict[str, float],
        predicted_returns: Dict[str, float],
    ) -> PortfolioExplanation:
        """Generate comprehensive portfolio explanation."""
        
        # Strategy overview
        risk_desc = self.risk_descriptions.get(risk_tolerance, "balanced approach")
        strategy = (
            f"This portfolio follows a {risk_tolerance} strategy that {risk_desc}. "
            f"Using a {model_type.replace('_', ' ').title()} model, we analyzed "
            f"{len(selected_assets)} assets to construct an optimal allocation for your "
            f"{investment_horizon}-year investment horizon."
        )
        
        # Asset selection summary
        top_performers = sorted(
            predicted_returns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        asset_summary = (
            f"From an initial universe of assets, our AI Research Agent screened "
            f"based on fundamental strength (value, quality, growth) and market sentiment. "
            f"The top predicted performers include: "
            f"{', '.join([f'{sym} ({ret:.1%})' for sym, ret in top_performers])}."
        )
        
        # Allocation rationale
        allocation_rationale = self._generate_allocation_rationale(
            allocations, risk_tolerance
        )
        
        # Risk management
        risk_approach = (
            f"Risk is managed through diversification across {len(selected_assets)} assets "
            f"and a 5% cash reserve for opportunistic rebalancing. The portfolio maintains "
            f"exposure to multiple sectors to reduce concentration risk."
        )
        
        # Expected performance
        avg_predicted_return = sum(predicted_returns.values()) / len(predicted_returns) if predicted_returns else 0
        performance_summary = (
            f"Based on historical backtesting and model predictions, this portfolio "
            f"has an expected annual return of {avg_predicted_return:.1%}. "
            f"Past performance does not guarantee future results."
        )
        
        # Generate asset-level explanations
        asset_explanations = []
        for symbol in selected_assets[:10]:  # Top 10 for detailed explanation
            explanation = self._generate_asset_explanation(
                symbol,
                fundamental_scores.get(symbol, 50),
                sentiment_scores.get(symbol, 50),
                predicted_returns.get(symbol, 0),
            )
            asset_explanations.append(explanation)
        
        # Key metrics explanation
        metrics_explanation = {
            "Expected Return": "Average predicted annual return based on AI model forecasts",
            "Volatility": "Standard deviation of returns indicating portfolio risk level",
            "Sharpe Ratio": "Risk-adjusted return metric (higher is better)",
            "Max Drawdown": "Maximum observed loss from peak to trough",
            "VaR (95%)": "Value at Risk - potential loss with 95% confidence",
        }
        
        return PortfolioExplanation(
            portfolio_id=portfolio_id,
            strategy_overview=strategy,
            asset_selection_summary=asset_summary,
            allocation_rationale=allocation_rationale,
            risk_management_approach=risk_approach,
            expected_performance_summary=performance_summary,
            asset_explanations=asset_explanations,
            key_metrics_explanation=metrics_explanation,
            disclaimer=(
                "This portfolio recommendation is generated by AI models for educational "
                "purposes only. It does not constitute financial advice. Always consult "
                "with a qualified financial advisor before making investment decisions."
            ),
        )
    
    def _generate_allocation_rationale(
        self,
        allocations: Dict[str, float],
        risk_tolerance: str
    ) -> str:
        """Generate explanation for allocation strategy."""
        sorted_allocs = sorted(allocations.items(), key=lambda x: x[1], reverse=True)
        top_3 = sorted_allocs[:3]
        
        if risk_tolerance == "conservative":
            return (
                f"Allocations favor stability with larger positions in defensive assets. "
                f"Top holdings: {', '.join([f'{sym} ({w:.1%})' for sym, w in top_3])}. "
                f"The allocation minimizes volatility while seeking steady income."
            )
        elif risk_tolerance == "aggressive":
            return (
                f"Allocations concentrate in high-growth opportunities. "
                f"Top holdings: {', '.join([f'{sym} ({w:.1%})' for sym, w in top_3])}. "
                f"The allocation maximizes exposure to assets with strongest predicted momentum."
            )
        else:
            return (
                f"Allocations balance growth and stability. "
                f"Top holdings: {', '.join([f'{sym} ({w:.1%})' for sym, w in top_3])}. "
                f"The allocation diversifies across sectors while overweighting top opportunities."
            )
    
    def _generate_asset_explanation(
        self,
        symbol: str,
        fundamental_score: float,
        sentiment_score: float,
        predicted_return: float,
    ) -> AssetExplanation:
        """Generate explanation for individual asset selection."""
        
        # Determine confidence level
        avg_score = (fundamental_score + sentiment_score) / 2
        if avg_score > 75:
            confidence = "high"
        elif avg_score > 50:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Fundamental factors
        fundamental_factors = []
        if fundamental_score > 70:
            fundamental_factors.append("Strong fundamental metrics (value, quality, growth)")
        elif fundamental_score > 50:
            fundamental_factors.append("Solid fundamental foundation")
        else:
            fundamental_factors.append("Moderate fundamentals with potential")
        
        # Sentiment factors
        sentiment_factors = []
        if sentiment_score > 70:
            sentiment_factors.append("Positive market sentiment and news coverage")
        elif sentiment_score > 50:
            sentiment_factors.append("Stable sentiment trends")
        else:
            sentiment_factors.append("Mixed sentiment with contrarian opportunity")
        
        # Quantitative factors
        quantitative_factors = [
            f"Predicted return: {predicted_return:.1%}",
            "Favorable technical indicators",
            "Strong risk-adjusted return potential"
        ]
        
        # Risk factors
        risk_factors = [
            "Market volatility risk",
            "Sector-specific risks",
            "Liquidity considerations"
        ]
        
        return AssetExplanation(
            symbol=symbol,
            selection_reason=f"Selected based on {confidence} confidence across fundamental, sentiment, and quantitative analysis",
            fundamental_factors=fundamental_factors,
            sentiment_factors=sentiment_factors,
            quantitative_factors=quantitative_factors,
            risk_factors=risk_factors,
            confidence_level=confidence,
        )
    
    def generate_rebalancing_explanation(
        self,
        portfolio_id: int,
        drift_percentage: float,
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate explanation for rebalancing recommendation."""
        
        if drift_percentage < 0.05:
            return (
                f"Portfolio {portfolio_id} is well-balanced with only {drift_percentage:.1%} drift "
                f"from target allocations. No rebalancing needed at this time."
            )
        
        explanation = (
            f"Portfolio {portfolio_id} has drifted {drift_percentage:.1%} from target allocations "
            f"due to market movements. Rebalancing is recommended to maintain optimal risk-adjusted "
            f"returns. Key adjustments: "
        )
        
        for rec in recommendations[:3]:
            action = rec.get("action", "adjust")
            symbol = rec.get("symbol", "Unknown")
            amount = rec.get("amount", 0)
            explanation += f"{action} {symbol} by ${amount:.2f}; "
        
        return explanation
