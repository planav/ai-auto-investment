"""LLM service for AI-powered portfolio analysis — powered by Anthropic Claude."""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import anthropic
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

_MODEL = "claude-haiku-4-5-20251001"


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


def _parse_json_from_text(text: str) -> dict:
    """Extract the first JSON object from a text response."""
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return json.loads(text)


class LLMService:
    """Anthropic Claude integration for AI-powered investment analysis."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or settings.anthropic_api_key
        self._client: Optional[anthropic.AsyncAnthropic] = None

    def _get_client(self) -> Optional[anthropic.AsyncAnthropic]:
        if self._client is None and self._api_key:
            try:
                self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
                logger.info("Claude LLM service initialized (model: {})", _MODEL)
            except Exception as exc:
                logger.error("Failed to init Claude LLM service: {}", exc)
        return self._client

    async def _complete(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> Optional[str]:
        """Send a single user message and return the assistant's text."""
        client = self._get_client()
        if client is None:
            return None
        try:
            msg = await client.messages.create(
                model=_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as exc:
            logger.error("Claude API error: {}", exc)
            return None

    async def analyze_portfolio(
        self,
        holdings: List[Dict[str, Any]],
        market_context: Dict[str, Any],
        risk_tolerance: str = "moderate",
    ) -> Optional[PortfolioAnalysis]:
        """Generate AI portfolio analysis using Claude."""
        prompt = f"""Analyze this investment portfolio and provide structured recommendations.

Portfolio Holdings:
{json.dumps(holdings, indent=2)}

Current Market Context:
{json.dumps(market_context, indent=2)}

Risk Tolerance: {risk_tolerance}

Respond with ONLY valid JSON in exactly this format (no markdown, no extra text):
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
}}"""

        text = await self._complete(prompt, max_tokens=1024)
        if text is None:
            return None

        try:
            data = _parse_json_from_text(text)
            return PortfolioAnalysis(
                risk_assessment=data.get("risk_assessment", {}),
                diversification_score=data.get("diversification_score", 50),
                sector_allocation=data.get("sector_allocation", {}),
                recommendations=data.get("recommendations", []),
                overall_rating=data.get("overall_rating", "C"),
                summary=data.get("summary", "Analysis completed."),
            )
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse Claude portfolio analysis JSON: {}", exc)
            return None

    async def analyze_stock(
        self,
        symbol: str,
        quote_data: Dict[str, Any],
        company_info: Optional[Dict[str, Any]] = None,
    ) -> Optional[StockAnalysis]:
        """Generate AI stock analysis using Claude. Falls back to rule-based on error."""
        prompt = f"""Analyze this stock and provide an investment recommendation.

Stock: {symbol}
Current Price: ${quote_data.get('price', 'N/A')}
Change: {quote_data.get('change_percent', 0):.2f}%

Company Info:
{json.dumps(company_info or {}, indent=2)}

Respond with ONLY valid JSON (no markdown, no extra text):
{{
    "signal": "buy|hold|sell",
    "confidence": 0-100,
    "rationale": "2-3 sentence explanation",
    "key_factors": ["factor1", "factor2", "factor3"],
    "risk_level": "low|moderate|high"
}}"""

        text = await self._complete(prompt, max_tokens=512)
        if text is None:
            return self._rule_based_analysis(symbol, quote_data)

        try:
            data = _parse_json_from_text(text)
            return StockAnalysis(
                symbol=symbol,
                signal=data.get("signal", "hold"),
                confidence=data.get("confidence", 50),
                rationale=data.get("rationale", "No analysis available."),
                key_factors=data.get("key_factors", []),
                risk_level=data.get("risk_level", "moderate"),
            )
        except json.JSONDecodeError:
            return self._rule_based_analysis(symbol, quote_data)

    def _rule_based_analysis(self, symbol: str, quote_data: Dict[str, Any]) -> StockAnalysis:
        """Rule-based fallback when Claude is unavailable."""
        change_pct = quote_data.get("change_percent", 0)

        if change_pct > 2.5:
            signal, confidence, risk = "buy", 72, "medium"
            rationale = (
                f"{symbol} shows strong upward momentum with a {change_pct:+.2f}% gain today. "
                "Price action suggests continued buying interest."
            )
            factors = [f"Strong daily gain of {change_pct:+.2f}%", "Positive momentum", "Above-average activity"]
        elif change_pct > 0.5:
            signal, confidence, risk = "buy", 63, "low"
            rationale = f"{symbol} shows modest positive momentum ({change_pct:+.2f}%). Stable upward action."
            factors = [f"Positive change {change_pct:+.2f}%", "Stable price action", "Low volatility"]
        elif change_pct > -0.5:
            signal, confidence, risk = "hold", 60, "low"
            rationale = f"{symbol} is trading near flat ({change_pct:+.2f}%). No strong directional signal."
            factors = ["Neutral movement", "Consolidation pattern", "Await clearer signal"]
        elif change_pct > -2.5:
            signal, confidence, risk = "sell", 63, "medium"
            rationale = f"{symbol} is declining ({change_pct:+.2f}%). Negative price action warrants caution."
            factors = [f"Negative change {change_pct:+.2f}%", "Downward pressure", "Risk management"]
        else:
            signal, confidence, risk = "sell", 72, "high"
            rationale = f"{symbol} shows significant selling pressure ({change_pct:+.2f}%). Strong bearish momentum."
            factors = [f"Sharp decline {change_pct:+.2f}%", "Strong selling", "High-risk environment"]

        return StockAnalysis(
            symbol=symbol, signal=signal, confidence=confidence,
            rationale=rationale, key_factors=factors, risk_level=risk,
        )

    async def generate_market_summary(
        self,
        indices_data: Dict[str, Any],
        top_movers: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Generate a brief market summary using Claude."""
        prompt = f"""Generate a brief market summary based on the following data.

Major Indices:
{json.dumps(indices_data, indent=2)}

Top Movers:
{json.dumps(top_movers, indent=2)}

Write a concise 3-4 sentence summary covering:
1. Overall market direction
2. Notable movers or sectors
3. Key investor sentiment

Keep it brief and informative."""

        return await self._complete(prompt, max_tokens=256, temperature=0.4)

    async def explain_prediction(
        self,
        symbol: str,
        prediction_data: Dict[str, Any],
        user_level: str = "beginner",
    ) -> Optional[str]:
        """Explain a prediction in user-friendly terms using Claude."""
        level_guidance = {
            "beginner": "Use simple language. Avoid jargon. Explain any financial terms.",
            "intermediate": "Some financial knowledge assumed. Brief explanations.",
            "advanced": "Professional terminology acceptable.",
        }

        prompt = f"""Explain this stock prediction for {symbol}:

Prediction Data:
{json.dumps(prediction_data, indent=2)}

Audience: {user_level} investor
{level_guidance.get(user_level, level_guidance['beginner'])}

Provide a 2-3 sentence explanation of why this prediction was made. Focus on key factors."""

        return await self._complete(prompt, max_tokens=256)


# Global instance
llm_service = LLMService()
