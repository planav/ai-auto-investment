from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class AlphaFactor:
    """Represents an alpha factor for prediction."""
    name: str
    description: str
    category: str  # momentum, value, quality, volatility, liquidity
    formula: Optional[str] = None


class FactorEngine:
    """Generates alpha factors for deep learning models."""
    
    def __init__(self):
        self.factors = self._initialize_factors()
    
    def _initialize_factors(self) -> Dict[str, AlphaFactor]:
        """Initialize all available alpha factors."""
        return {
            # Momentum factors
            "momentum_1m": AlphaFactor(
                name="momentum_1m",
                description="1-month price momentum",
                category="momentum",
                formula="(close - close_20) / close_20"
            ),
            "momentum_3m": AlphaFactor(
                name="momentum_3m",
                description="3-month price momentum",
                category="momentum",
                formula="(close - close_60) / close_60"
            ),
            "momentum_12m": AlphaFactor(
                name="momentum_12m",
                description="12-month price momentum (excluding last month)",
                category="momentum",
                formula="(close_20 - close_240) / close_240"
            ),
            "rsi": AlphaFactor(
                name="rsi",
                description="Relative Strength Index",
                category="momentum",
            ),
            "macd": AlphaFactor(
                name="macd",
                description="MACD indicator",
                category="momentum",
            ),
            
            # Value factors
            "pe_ratio": AlphaFactor(
                name="pe_ratio",
                description="Price to Earnings ratio",
                category="value",
            ),
            "pb_ratio": AlphaFactor(
                name="pb_ratio",
                description="Price to Book ratio",
                category="value",
            ),
            "ps_ratio": AlphaFactor(
                name="ps_ratio",
                description="Price to Sales ratio",
                category="value",
            ),
            "dividend_yield": AlphaFactor(
                name="dividend_yield",
                description="Dividend yield",
                category="value",
            ),
            "ev_ebitda": AlphaFactor(
                name="ev_ebitda",
                description="Enterprise Value to EBITDA",
                category="value",
            ),
            
            # Quality factors
            "roe": AlphaFactor(
                name="roe",
                description="Return on Equity",
                category="quality",
            ),
            "roa": AlphaFactor(
                name="roa",
                description="Return on Assets",
                category="quality",
            ),
            "gross_margin": AlphaFactor(
                name="gross_margin",
                description="Gross profit margin",
                category="quality",
            ),
            "debt_to_equity": AlphaFactor(
                name="debt_to_equity",
                description="Debt to Equity ratio",
                category="quality",
            ),
            "current_ratio": AlphaFactor(
                name="current_ratio",
                description="Current ratio",
                category="quality",
            ),
            
            # Volatility factors
            "volatility_20d": AlphaFactor(
                name="volatility_20d",
                description="20-day realized volatility",
                category="volatility",
            ),
            "volatility_60d": AlphaFactor(
                name="volatility_60d",
                description="60-day realized volatility",
                category="volatility",
            ),
            "max_drawdown_1m": AlphaFactor(
                name="max_drawdown_1m",
                description="1-month maximum drawdown",
                category="volatility",
            ),
            "beta": AlphaFactor(
                name="beta",
                description="Market beta",
                category="volatility",
            ),
            
            # Liquidity factors
            "avg_volume": AlphaFactor(
                name="avg_volume",
                description="Average trading volume",
                category="liquidity",
            ),
            "volume_volatility": AlphaFactor(
                name="volume_volatility",
                description="Volume volatility",
                category="liquidity",
            ),
            "turnover": AlphaFactor(
                name="turnover",
                description="Share turnover ratio",
                category="liquidity",
            ),
            
            # Technical factors
            "sma_ratio": AlphaFactor(
                name="sma_ratio",
                description="Price to Simple Moving Average ratio",
                category="technical",
            ),
            "bb_position": AlphaFactor(
                name="bb_position",
                description="Bollinger Bands position",
                category="technical",
            ),
            "atr": AlphaFactor(
                name="atr",
                description="Average True Range",
                category="technical",
            ),
        }
    
    def calculate_technical_factors(
        self,
        prices: pd.DataFrame,
        volumes: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate technical factors from price and volume data.
        
        Args:
            prices: DataFrame with price data (OHLC)
            volumes: DataFrame with volume data
            
        Returns:
            DataFrame with calculated factors
        """
        factors = pd.DataFrame(index=prices.index)
        
        # Momentum factors
        factors["momentum_1m"] = self._calculate_momentum(prices, 20)
        factors["momentum_3m"] = self._calculate_momentum(prices, 60)
        factors["momentum_12m"] = self._calculate_momentum(prices, 240, offset=20)
        factors["rsi"] = self._calculate_rsi(prices, 14)
        factors["macd"] = self._calculate_macd(prices)
        
        # Volatility factors
        factors["volatility_20d"] = self._calculate_volatility(prices, 20)
        factors["volatility_60d"] = self._calculate_volatility(prices, 60)
        factors["max_drawdown_1m"] = self._calculate_max_drawdown(prices, 20)
        
        # Technical factors
        factors["sma_ratio"] = self._calculate_sma_ratio(prices, 20)
        factors["bb_position"] = self._calculate_bb_position(prices, 20)
        factors["atr"] = self._calculate_atr(prices, 14)
        
        # Volume factors
        factors["volume_sma_ratio"] = volumes / volumes.rolling(20).mean()
        
        return factors
    
    def _calculate_momentum(
        self,
        prices: pd.DataFrame,
        period: int,
        offset: int = 0
    ) -> pd.Series:
        """Calculate price momentum."""
        close = prices["close"] if "close" in prices.columns else prices.iloc[:, -1]
        if offset > 0:
            return (close.shift(offset) - close.shift(period + offset)) / close.shift(period + offset)
        return (close - close.shift(period)) / close.shift(period)
    
    def _calculate_rsi(self, prices: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        close = prices["close"] if "close" in prices.columns else prices.iloc[:, -1]
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.DataFrame) -> pd.Series:
        """Calculate MACD."""
        close = prices["close"] if "close" in prices.columns else prices.iloc[:, -1]
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        return ema_12 - ema_26
    
    def _calculate_volatility(self, prices: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate realized volatility."""
        close = prices["close"] if "close" in prices.columns else prices.iloc[:, -1]
        returns = close.pct_change()
        return returns.rolling(window=period).std() * np.sqrt(252)
    
    def _calculate_max_drawdown(self, prices: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate maximum drawdown."""
        close = prices["close"] if "close" in prices.columns else prices.iloc[:, -1]
        rolling_max = close.rolling(window=period, min_periods=1).max()
        drawdown = (close - rolling_max) / rolling_max
        return drawdown.rolling(window=period, min_periods=1).min()
    
    def _calculate_sma_ratio(self, prices: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate price to SMA ratio."""
        close = prices["close"] if "close" in prices.columns else prices.iloc[:, -1]
        sma = close.rolling(window=period).mean()
        return close / sma
    
    def _calculate_bb_position(self, prices: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Bollinger Bands position."""
        close = prices["close"] if "close" in prices.columns else prices.iloc[:, -1]
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        return (close - lower) / (upper - lower)
    
    def _calculate_atr(self, prices: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high = prices["high"] if "high" in prices.columns else prices.iloc[:, 0]
        low = prices["low"] if "low" in prices.columns else prices.iloc[:, 1]
        close = prices["close"] if "close" in prices.columns else prices.iloc[:, -1]
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    def get_factor_list(self) -> List[str]:
        """Get list of all available factor names."""
        return list(self.factors.keys())
    
    def get_factors_by_category(self, category: str) -> List[str]:
        """Get factors filtered by category."""
        return [
            name for name, factor in self.factors.items()
            if factor.category == category
        ]
