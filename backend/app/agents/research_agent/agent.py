from typing import Any, Dict, List, Optional

from app.agents.base_agent import AgentContext, AgentResult, BaseAgent
from app.agents.research_agent.fundamental import FundamentalAnalyzer, FundamentalMetrics
from app.agents.research_agent.sentiment import SentimentAnalyzer, SentimentAnalysis
from app.agents.research_agent.explainability import ExplanationGenerator, PortfolioExplanation


class ResearchAgent(BaseAgent):
    """
    AI Research Agent that performs fundamental analysis, sentiment analysis,
    and generates explainable investment insights.
    """
    
    def __init__(self):
        super().__init__(
            name="Research Agent",
            description="Analyzes assets using fundamental and sentiment analysis"
        )
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.explanation_generator = ExplanationGenerator()
    
    async def initialize(self) -> None:
        """Initialize the research agent."""
        # Any initialization logic here
        await super().initialize()
    
    async def execute(
        self,
        context: AgentContext,
        asset_universe: List[str],
        max_assets: int = 50,
        **kwargs
    ) -> AgentResult:
        """
        Execute research analysis on asset universe.
        
        Args:
            context: Agent execution context
            asset_universe: List of asset symbols to analyze
            max_assets: Maximum number of assets to return
            
        Returns:
            AgentResult with filtered assets and analysis data
        """
        try:
            # Step 1: Fundamental Analysis
            fundamental_results = await self.fundamental_analyzer.analyze_assets(
                asset_universe
            )
            
            # Step 2: Screen assets based on fundamentals
            screened_assets = self.fundamental_analyzer.screen_assets(
                fundamental_results,
                min_score=60.0,
                max_assets=max_assets * 2  # Keep more for sentiment filtering
            )
            
            # Step 3: Sentiment Analysis
            sentiment_results = await self.sentiment_analyzer.analyze_sentiments(
                screened_assets
            )
            
            # Step 4: Filter by sentiment
            final_assets = self.sentiment_analyzer.filter_by_sentiment(
                sentiment_results,
                min_sentiment=-0.2,
                exclude_declining=True
            )[:max_assets]
            
            # Step 5: Prepare results
            asset_scores = {}
            for symbol in final_assets:
                fund_score = fundamental_results.get(symbol, FundamentalMetrics(symbol)).overall_score
                sent_score = self.sentiment_analyzer.get_sentiment_score(symbol)
                # Combined score (equal weighting)
                asset_scores[symbol] = (fund_score + sent_score) / 2
            
            # Sort by combined score
            final_assets.sort(key=lambda x: asset_scores[x], reverse=True)
            
            return AgentResult(
                success=True,
                data={
                    "filtered_assets": final_assets,
                    "asset_scores": asset_scores,
                    "fundamental_metrics": {
                        symbol: {
                            "pe_ratio": fundamental_results[symbol].pe_ratio,
                            "pb_ratio": fundamental_results[symbol].pb_ratio,
                            "roe": fundamental_results[symbol].roe,
                            "overall_score": fundamental_results[symbol].overall_score,
                        }
                        for symbol in final_assets if symbol in fundamental_results
                    },
                    "sentiment_metrics": {
                        symbol: {
                            "overall_sentiment": sentiment_results[symbol].overall_sentiment,
                            "sentiment_trend": sentiment_results[symbol].sentiment_trend,
                            "news_count": sentiment_results[symbol].news_count,
                        }
                        for symbol in final_assets if symbol in sentiment_results
                    },
                },
                explanation=f"Analyzed {len(asset_universe)} assets, selected top {len(final_assets)} based on fundamental and sentiment analysis",
                confidence=sum(asset_scores.values()) / len(asset_scores) / 100 if asset_scores else 0,
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                errors=[str(e)],
            )
    
    async def generate_portfolio_explanation(
        self,
        portfolio_id: Optional[int],
        selected_assets: List[str],
        allocations: Dict[str, float],
        context: AgentContext,
        model_type: str,
        predicted_returns: Dict[str, float],
    ) -> PortfolioExplanation:
        """
        Generate comprehensive explanation for portfolio decisions.
        
        Args:
            portfolio_id: ID of the portfolio
            selected_assets: List of selected asset symbols
            allocations: Dictionary of asset allocations
            context: Agent context with user preferences
            model_type: Type of ML model used
            predicted_returns: Dictionary of predicted returns per asset
            
        Returns:
            PortfolioExplanation with detailed rationale
        """
        # Get fundamental scores
        fundamental_scores = {
            symbol: self.fundamental_analyzer.metrics_cache.get(
                symbol, FundamentalMetrics(symbol)
            ).overall_score
            for symbol in selected_assets
        }
        
        # Get sentiment scores
        sentiment_scores = {
            symbol: self.sentiment_analyzer.get_sentiment_score(symbol)
            for symbol in selected_assets
        }
        
        return self.explanation_generator.generate_portfolio_explanation(
            portfolio_id=portfolio_id,
            selected_assets=selected_assets,
            allocations=allocations,
            risk_tolerance=context.risk_tolerance,
            investment_horizon=context.investment_horizon,
            model_type=model_type,
            fundamental_scores=fundamental_scores,
            sentiment_scores=sentiment_scores,
            predicted_returns=predicted_returns,
        )
    
    async def analyze_single_asset(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a single asset.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Dictionary with analysis results
        """
        fundamental = await self.fundamental_analyzer.analyze_asset(symbol)
        sentiment = await self.sentiment_analyzer.analyze_sentiment(symbol)
        
        return {
            "symbol": symbol,
            "fundamental": {
                "pe_ratio": fundamental.pe_ratio,
                "pb_ratio": fundamental.pb_ratio,
                "roe": fundamental.roe,
                "revenue_growth": fundamental.revenue_growth,
                "overall_score": fundamental.overall_score,
            },
            "sentiment": {
                "overall_sentiment": sentiment.overall_sentiment,
                "sentiment_trend": sentiment.sentiment_trend,
                "news_count": sentiment.news_count,
                "bullish_count": sentiment.bullish_count,
                "bearish_count": sentiment.bearish_count,
                "key_topics": sentiment.key_topics,
            },
            "combined_score": (
                fundamental.overall_score + 
                self.sentiment_analyzer.get_sentiment_score(symbol)
            ) / 2,
        }
