"""LLM service for AI-powered portfolio analysis and explanations."""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from loguru import logger

from app.core.config import get_settings

settings = get_settings()


@dataclass
class PortfolioAnalysis:
    """AI-generated portfolio analysis."""
    risk_assessment: Dict[str, Any]
    diversification_score: int
    sector_allocation: Dict[str, float]
    recommendations: List[Dict[str, Any]]
    overall_rating: str
    summary: str


@dataclass
class StockAnalysis:
    """AI-generated stock analysis."""
    symbol: str
    signal: str  # buy, hold, sell
    confidence: int
    rationale: str
    key_factors: List[str]
    risk_level: str


class LLMService:
    """Google Gemini 2.0 Flash integration for AI analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = None
        self._initialized = False
        
    def _initialize(self):
        """Initialize Gemini model."""
        if self._initialized:
            return
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self._initialized = True
            logger.info("Gemini LLM service initialized successfully")
        except ImportError:
            logger.error("google-generativeai package not installed")
            raise
        except Exception as e:
            logger.error(f"Error initializing Gemini: {e}")
            raise
    
    async def analyze_portfolio(
        self,
        holdings: List[Dict[str, Any]],
        market_context: Dict[str, Any],
        risk_tolerance: str = "moderate"
    ) -> Optional[PortfolioAnalysis]:
        """
        Generate AI portfolio analysis.
        
        Args:
            holdings: List of portfolio holdings with symbol, weight, etc.
            market_context: Current market conditions
            risk_tolerance: User's risk tolerance level
            
        Returns:
            PortfolioAnalysis object or None if error
        """
        try:
            self._initialize()
            
            prompt = f"""Analyze this investment portfolio and provide structured recommendations.

Portfolio Holdings:
{json.dumps(holdings, indent=2)}

Current Market Context:
{json.dumps(market_context, indent=2)}

Risk Tolerance: {risk_tolerance}

Provide analysis in this exact JSON format:
{{
    "risk_assessment": {{
        "level": "low|moderate|high",
        "score": 0-100,
        "factors": ["factor1", "factor2"]
    }},
    "diversification_score": 0-100,
    "sector_allocation": {{
        "technology": 0-100,
        "healthcare": 0-100,
        "finance": 0-100,
        "consumer": 0-100,
        "energy": 0-100,
        "other": 0-100
    }},
    "recommendations": [
        {{
            "action": "buy|hold|sell|reduce",
            "symbol": "TICKER",
            "confidence": 0-100,
            "rationale": "explanation"
        }}
    ],
    "overall_rating": "A|B|C|D|F",
    "summary": "2-3 sentence summary"
}}

Be concise and actionable. Focus on practical investment advice."""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 1024,
                }
            )
            
            # Parse JSON response
            try:
                # Try to extract JSON from response
                text = response.text
                # Find JSON block
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = text[start:end]
                    data = json.loads(json_str)
                else:
                    data = json.loads(text)
                
                return PortfolioAnalysis(
                    risk_assessment=data.get("risk_assessment", {}),
                    diversification_score=data.get("diversification_score", 50),
                    sector_allocation=data.get("sector_allocation", {}),
                    recommendations=data.get("recommendations", []),
                    overall_rating=data.get("overall_rating", "C"),
                    summary=data.get("summary", "Analysis completed.")
                )
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing LLM response: {e}")
                logger.debug(f"Response text: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {e}")
            return None
    
    async def analyze_stock(
        self,
        symbol: str,
        quote_data: Dict[str, Any],
        company_info: Optional[Dict[str, Any]] = None
    ) -> Optional[StockAnalysis]:
        """
        Generate AI stock analysis.
        
        Args:
            symbol: Stock symbol
            quote_data: Current quote data
            company_info: Optional company information
            
        Returns:
            StockAnalysis object or None if error
        """
        try:
            self._initialize()
            
            prompt = f"""Analyze this stock and provide investment recommendation.

Stock: {symbol}
Current Price: ${quote_data.get('price', 'N/A')}
Change: {quote_data.get('change_percent', 0):.2f}%

Company Info:
{json.dumps(company_info or {}, indent=2)}

Provide analysis in this exact JSON format:
{{
    "signal": "buy|hold|sell",
    "confidence": 0-100,
    "rationale": "2-3 sentence explanation",
    "key_factors": ["factor1", "factor2", "factor3"],
    "risk_level": "low|moderate|high"
}}

Focus on recent price action and technical factors. Be concise."""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 512,
                }
            )
            
            # Parse JSON response
            try:
                text = response.text
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = text[start:end]
                    data = json.loads(json_str)
                else:
                    data = json.loads(text)
                
                return StockAnalysis(
                    symbol=symbol,
                    signal=data.get("signal", "hold"),
                    confidence=data.get("confidence", 50),
                    rationale=data.get("rationale", "No analysis available."),
                    key_factors=data.get("key_factors", []),
                    risk_level=data.get("risk_level", "moderate")
                )
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing LLM response: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error in stock analysis: {e}")
            return None
    
    async def generate_market_summary(
        self,
        indices_data: Dict[str, Any],
        top_movers: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Generate market summary.
        
        Args:
            indices_data: Major indices performance
            top_movers: Top gaining/losing stocks
            
        Returns:
            Summary text or None if error
        """
        try:
            self._initialize()
            
            prompt = f"""Generate a brief market summary based on the following data.

Major Indices:
{json.dumps(indices_data, indent=2)}

Top Movers:
{json.dumps(top_movers, indent=2)}

Provide a concise 3-4 sentence summary highlighting:
1. Overall market direction
2. Notable movers or sectors
3. Key sentiment

Keep it brief and informative for investors."""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.4,
                    "max_output_tokens": 256,
                }
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating market summary: {e}")
            return None
    
    async def explain_prediction(
        self,
        symbol: str,
        prediction_data: Dict[str, Any],
        user_level: str = "beginner"
    ) -> Optional[str]:
        """
        Explain a prediction in user-friendly terms.
        
        Args:
            symbol: Stock symbol
            prediction_data: Prediction details
            user_level: User experience level (beginner/intermediate/advanced)
            
        Returns:
            Explanation text or None if error
        """
        try:
            self._initialize()
            
            level_guidance = {
                "beginner": "Use simple language. Avoid jargon. Explain any financial terms.",
                "intermediate": "Some financial knowledge assumed. Brief explanations.",
                "advanced": "Professional terminology acceptable."
            }
            
            prompt = f"""Explain this stock prediction for {symbol}:

Prediction Data:
{json.dumps(prediction_data, indent=2)}

Audience: {user_level} investor
{level_guidance.get(user_level, level_guidance["beginner"])}

Provide a 2-3 sentence explanation of why this prediction was made.
Focus on the key factors."""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 256,
                }
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error explaining prediction: {e}")
            return None


# Global instance
llm_service = LLMService()
