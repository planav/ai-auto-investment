from typing import Dict, List, Optional, Any
import numpy as np

from app.engines.portfolio_engine.allocation import (
    AllocationOptimizer,
    AllocationResult,
    PortfolioConstraints,
)
from app.engines.portfolio_engine.risk import RiskEngine, RiskMetrics
from app.engines.portfolio_engine.rebalance import (
    RebalanceEngine,
    RebalanceRecommendation,
    RebalancePlan,
)


class PortfolioEngine:
    """
    Portfolio Engine for asset allocation, risk management, and rebalancing.
    Integrates with Quant Engine for predictions and Research Agent for analysis.
    """
    
    def __init__(self):
        self.allocation_optimizer = AllocationOptimizer()
        self.risk_engine = RiskEngine()
        self.rebalance_engine = RebalanceEngine()
    
    async def optimize_allocation(
        self,
        assets: List[str],
        predictions: Dict[str, float],
        risk_profile: str = "moderate",
        constraints: Optional[PortfolioConstraints] = None,
        optimization_method: str = "mean_variance"
    ) -> AllocationResult:
        """
        Optimize portfolio allocation.
        
        Args:
            assets: List of asset symbols
            predictions: Dictionary of predicted returns per asset
            risk_profile: Risk tolerance (conservative, moderate, aggressive)
            constraints: Portfolio constraints
            optimization_method: Optimization method to use
            
        Returns:
            AllocationResult with optimal weights and metrics
        """
        if constraints is None:
            constraints = PortfolioConstraints()
        
        # Generate covariance matrix (mock - in production use historical data)
        n_assets = len(assets)
        cov_matrix = self._generate_covariance_matrix(n_assets)
        
        # Run optimization based on method
        if optimization_method == "mean_variance":
            result = self.allocation_optimizer.optimize(
                assets=assets,
                expected_returns=predictions,
                cov_matrix=cov_matrix,
                constraints=constraints,
                risk_profile=risk_profile,
            )
        elif optimization_method == "risk_parity":
            result = self.allocation_optimizer.risk_parity_allocation(
                assets=assets,
                cov_matrix=cov_matrix,
                constraints=constraints,
            )
        elif optimization_method == "equal_risk_contribution":
            result = self.allocation_optimizer.equal_risk_contribution(
                assets=assets,
                cov_matrix=cov_matrix,
                constraints=constraints,
            )
        else:
            raise ValueError(f"Unknown optimization method: {optimization_method}")
        
        return result
    
    def _generate_covariance_matrix(self, n_assets: int) -> np.ndarray:
        """Generate a realistic covariance matrix."""
        # Create random correlation matrix
        random_matrix = np.random.randn(n_assets, n_assets)
        cov_matrix = random_matrix @ random_matrix.T
        
        # Scale to realistic volatilities (15-30% annual)
        volatilities = np.random.uniform(0.15, 0.30, n_assets)
        
        # Convert correlation to covariance
        for i in range(n_assets):
            for j in range(n_assets):
                cov_matrix[i, j] = cov_matrix[i, j] * volatilities[i] * volatilities[j]
        
        return cov_matrix
    
    async def calculate_risk_metrics(
        self,
        portfolio_id: int,
        weights: Dict[str, float],
        historical_returns: Optional[np.ndarray] = None
    ) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics for a portfolio.
        
        Args:
            portfolio_id: Portfolio identifier
            weights: Portfolio weights
            historical_returns: Historical returns matrix (optional)
            
        Returns:
            RiskMetrics with all risk calculations
        """
        # Generate mock returns if not provided
        if historical_returns is None:
            n_assets = len(weights)
            n_periods = 252  # 1 year of daily returns
            historical_returns = np.random.randn(n_periods, n_assets) * 0.02
        
        weights_array = np.array(list(weights.values()))
        
        return self.risk_engine.calculate_risk_metrics(
            portfolio_id=portfolio_id,
            returns=historical_returns,
            weights=weights_array,
        )
    
    async def check_rebalance_needed(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        threshold: float = 0.05
    ) -> RebalanceRecommendation:
        """
        Check if portfolio rebalancing is needed.
        
        Args:
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            threshold: Drift threshold
            
        Returns:
            RebalanceRecommendation with analysis
        """
        return self.rebalance_engine.check_rebalance_needed(
            current_weights=current_weights,
            target_weights=target_weights,
            threshold=threshold,
        )
    
    async def generate_rebalance_plan(
        self,
        portfolio_id: int,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        portfolio_value: float = 100000.0
    ) -> RebalancePlan:
        """
        Generate detailed rebalancing execution plan.
        
        Args:
            portfolio_id: Portfolio identifier
            current_weights: Current weights
            target_weights: Target weights
            portfolio_value: Total portfolio value
            
        Returns:
            RebalancePlan with execution details
        """
        return self.rebalance_engine.generate_rebalance_plan(
            portfolio_id=portfolio_id,
            current_weights=current_weights,
            target_weights=target_weights,
            portfolio_value=portfolio_value,
        )
    
    async def stress_test_portfolio(
        self,
        portfolio_weights: Dict[str, float],
        scenarios: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Run stress tests on portfolio.
        
        Args:
            portfolio_weights: Portfolio weights
            scenarios: List of stress test scenarios
            
        Returns:
            List of stress test results
        """
        if scenarios is None:
            scenarios = [
                "market_crash",
                "interest_rate_shock",
                "inflation_spike",
                "tech_bubble_burst",
            ]
        
        results = []
        for scenario in scenarios:
            result = self.risk_engine.stress_test(
                portfolio_weights=portfolio_weights,
                scenario=scenario,
            )
            results.append({
                "scenario": result.scenario_name,
                "description": result.description,
                "portfolio_loss_pct": result.portfolio_loss_pct,
                "var_breach": result.var_breach,
                "recovery_time_days": result.recovery_time_days,
                "worst_affected_assets": result.worst_affected_assets,
            })
        
        return results
    
    async def get_optimization_methods(self) -> List[Dict[str, Any]]:
        """Get available optimization methods."""
        return [
            {
                "id": "mean_variance",
                "name": "Mean-Variance Optimization",
                "description": "Classic Markowitz optimization maximizing risk-adjusted returns",
                "best_for": "Most investors seeking optimal risk-return tradeoff",
            },
            {
                "id": "risk_parity",
                "name": "Risk Parity",
                "description": "Allocates based on inverse volatility for balanced risk contribution",
                "best_for": "Risk-focused investors seeking diversification",
            },
            {
                "id": "equal_risk_contribution",
                "name": "Equal Risk Contribution",
                "description": "Each asset contributes equally to portfolio risk",
                "best_for": "Maximum diversification benefits",
            },
        ]
    
    async def get_risk_profiles(self) -> List[Dict[str, Any]]:
        """Get available risk profiles."""
        return [
            {
                "id": "conservative",
                "name": "Conservative",
                "description": "Prioritizes capital preservation with lower volatility",
                "expected_return": "4-6%",
                "expected_volatility": "8-12%",
                "max_drawdown": "<15%",
            },
            {
                "id": "moderate",
                "name": "Moderate",
                "description": "Balances growth and stability",
                "expected_return": "6-10%",
                "expected_volatility": "12-18%",
                "max_drawdown": "<25%",
            },
            {
                "id": "aggressive",
                "name": "Aggressive",
                "description": "Maximizes growth potential with higher volatility tolerance",
                "expected_return": "10-15%",
                "expected_volatility": "18-25%",
                "max_drawdown": "<35%",
            },
        ]
