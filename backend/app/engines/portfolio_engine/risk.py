from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics for a portfolio."""
    portfolio_id: int
    volatility: float
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    max_drawdown: float
    max_drawdown_duration: int
    beta: float
    alpha: float
    tracking_error: float
    information_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    omega_ratio: float


@dataclass
class StressTestResult:
    """Result of stress test scenario."""
    scenario_name: str
    description: str
    portfolio_loss_pct: float
    var_breach: bool
    recovery_time_days: int
    worst_affected_assets: List[str]


class RiskEngine:
    """Portfolio risk analysis and management."""
    
    def __init__(self):
        self.confidence_levels = [0.95, 0.99]
        self.risk_free_rate = 0.02
    
    def calculate_risk_metrics(
        self,
        portfolio_id: int,
        returns: np.ndarray,
        weights: np.ndarray,
        benchmark_returns: Optional[np.ndarray] = None
    ) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics.
        
        Args:
            portfolio_id: Portfolio identifier
            returns: Asset return series (T x N)
            weights: Portfolio weights (N)
            benchmark_returns: Benchmark return series (T)
            
        Returns:
            RiskMetrics with all risk calculations
        """
        # Portfolio returns
        portfolio_returns = returns @ weights
        
        # Basic metrics
        volatility = float(np.std(portfolio_returns) * np.sqrt(252))
        
        # VaR calculations (parametric)
        var_95 = float(np.percentile(portfolio_returns, 5))
        var_99 = float(np.percentile(portfolio_returns, 1))
        
        # CVaR (Expected Shortfall)
        cvar_95 = float(portfolio_returns[portfolio_returns <= var_95].mean())
        cvar_99 = float(portfolio_returns[portfolio_returns <= var_99].mean())
        
        # Drawdown analysis
        max_dd, max_dd_duration = self._calculate_drawdown_metrics(portfolio_returns)
        
        # Beta and Alpha (if benchmark provided)
        if benchmark_returns is not None:
            beta, alpha = self._calculate_beta_alpha(
                portfolio_returns, benchmark_returns
            )
            tracking_error = float(np.std(portfolio_returns - benchmark_returns) * np.sqrt(252))
            information_ratio = alpha / tracking_error if tracking_error > 0 else 0
        else:
            beta, alpha = 1.0, 0.0
            tracking_error = 0.0
            information_ratio = 0.0
        
        # Sortino ratio (downside deviation)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_std = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        excess_return = np.mean(portfolio_returns) * 252 - self.risk_free_rate
        sortino = excess_return / downside_std if downside_std > 0 else 0
        
        # Calmar ratio
        calmar = excess_return / abs(max_dd) if max_dd != 0 else 0
        
        # Omega ratio
        omega = self._calculate_omega_ratio(portfolio_returns)
        
        return RiskMetrics(
            portfolio_id=portfolio_id,
            volatility=volatility,
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99,
            max_drawdown=max_dd,
            max_drawdown_duration=max_dd_duration,
            beta=beta,
            alpha=alpha,
            tracking_error=tracking_error,
            information_ratio=information_ratio,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            omega_ratio=omega,
        )
    
    def _calculate_drawdown_metrics(self, returns: np.ndarray) -> Tuple[float, int]:
        """Calculate maximum drawdown and its duration."""
        # Calculate cumulative returns
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        max_drawdown = float(np.min(drawdown))
        
        # Find max drawdown duration
        max_dd_duration = 0
        current_duration = 0
        in_drawdown = False
        
        for dd in drawdown:
            if dd < 0:
                if not in_drawdown:
                    in_drawdown = True
                    current_duration = 1
                else:
                    current_duration += 1
            else:
                if in_drawdown:
                    max_dd_duration = max(max_dd_duration, current_duration)
                    in_drawdown = False
                    current_duration = 0
        
        return max_drawdown, max_dd_duration
    
    def _calculate_beta_alpha(
        self,
        portfolio_returns: np.ndarray,
        benchmark_returns: np.ndarray
    ) -> Tuple[float, float]:
        """Calculate beta and alpha relative to benchmark."""
        # Remove NaN values
        mask = ~(np.isnan(portfolio_returns) | np.isnan(benchmark_returns))
        p_returns = portfolio_returns[mask]
        b_returns = benchmark_returns[mask]
        
        if len(p_returns) < 2:
            return 1.0, 0.0
        
        # Calculate beta
        covariance = np.cov(p_returns, b_returns)[0, 1]
        benchmark_variance = np.var(b_returns)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
        
        # Calculate alpha (annualized)
        alpha = (np.mean(p_returns) - beta * np.mean(b_returns)) * 252
        
        return float(beta), float(alpha)
    
    def _calculate_omega_ratio(self, returns: np.ndarray, threshold: float = 0) -> float:
        """Calculate Omega ratio."""
        excess_returns = returns - threshold
        gains = excess_returns[excess_returns > 0].sum()
        losses = abs(excess_returns[excess_returns < 0].sum())
        
        return float(gains / losses) if losses > 0 else float('inf')
    
    def stress_test(
        self,
        portfolio_weights: Dict[str, float],
        scenario: str = "market_crash"
    ) -> StressTestResult:
        """
        Run stress test on portfolio.
        
        Args:
            portfolio_weights: Asset weights
            scenario: Stress test scenario name
            
        Returns:
            StressTestResult with impact analysis
        """
        scenarios = {
            "market_crash": {
                "description": "2008-style market crash (-40% market decline)",
                "market_decline": -0.40,
                "volatility_spike": 3.0,
            },
            "interest_rate_shock": {
                "description": "Rapid interest rate increase (+300bps)",
                "rate_increase": 0.03,
                "market_decline": -0.15,
            },
            "inflation_spike": {
                "description": "Unexpected inflation surge",
                "inflation_increase": 0.05,
                "market_decline": -0.20,
            },
            "tech_bubble_burst": {
                "description": "Technology sector collapse",
                "tech_decline": -0.50,
                "market_decline": -0.25,
            },
        }
        
        scenario_data = scenarios.get(scenario, scenarios["market_crash"])
        
        # Simulate portfolio loss (simplified)
        base_loss = abs(scenario_data.get("market_decline", -0.20))
        portfolio_loss = base_loss * np.random.uniform(0.8, 1.2)
        
        # Determine VaR breach
        var_breach = portfolio_loss > 0.05  # 5% daily VaR
        
        # Estimate recovery time
        recovery_time = int(30 + portfolio_loss * 200)
        
        # Identify worst affected assets
        worst_assets = list(portfolio_weights.keys())[:3]
        
        return StressTestResult(
            scenario_name=scenario,
            description=scenario_data["description"],
            portfolio_loss_pct=portfolio_loss * 100,
            var_breach=var_breach,
            recovery_time_days=recovery_time,
            worst_affected_assets=worst_assets,
        )
    
    def calculate_correlation_matrix(
        self,
        returns: np.ndarray,
        assets: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between assets."""
        corr_matrix = np.corrcoef(returns.T)
        
        result = {}
        for i, asset1 in enumerate(assets):
            result[asset1] = {}
            for j, asset2 in enumerate(assets):
                result[asset1][asset2] = float(corr_matrix[i, j])
        
        return result
    
    def detect_concentration_risk(
        self,
        weights: Dict[str, float],
        threshold: float = 0.10
    ) -> List[Dict[str, Any]]:
        """Detect concentration risks in portfolio."""
        risks = []
        
        for asset, weight in weights.items():
            if weight > threshold:
                risks.append({
                    "asset": asset,
                    "weight": weight,
                    "severity": "high" if weight > 0.20 else "medium",
                    "recommendation": f"Consider reducing position below {threshold:.0%}",
                })
        
        return risks
