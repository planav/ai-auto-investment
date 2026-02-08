from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class AllocationResult:
    """Result from portfolio optimization."""
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    var_95: float  # Value at Risk
    cvar_95: float  # Conditional VaR
    diversification_ratio: float
    concentration_risk: float
    sector_allocation: Dict[str, float]


@dataclass
class PortfolioConstraints:
    """Constraints for portfolio optimization."""
    min_weight: float = 0.0
    max_weight: float = 0.2  # Max 20% in single asset
    min_assets: int = 5
    max_assets: int = 30
    cash_reserve: float = 0.05  # 5% cash reserve
    sector_limits: Optional[Dict[str, float]] = None
    
    # Risk constraints
    max_volatility: Optional[float] = None
    max_drawdown: Optional[float] = None
    target_return: Optional[float] = None


class AllocationOptimizer:
    """Portfolio allocation optimizer using mean-variance optimization."""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
    
    def optimize(
        self,
        assets: List[str],
        expected_returns: Dict[str, float],
        cov_matrix: np.ndarray,
        constraints: PortfolioConstraints,
        risk_profile: str = "moderate"
    ) -> AllocationResult:
        """
        Optimize portfolio allocation.
        
        Args:
            assets: List of asset symbols
            expected_returns: Dictionary of expected returns per asset
            cov_matrix: Covariance matrix of returns
            constraints: Portfolio constraints
            risk_profile: Risk tolerance level
            
        Returns:
            AllocationResult with optimal weights and metrics
        """
        n_assets = len(assets)
        
        # Adjust for cash reserve
        investable_fraction = 1.0 - constraints.cash_reserve
        
        # Get expected returns array
        mu = np.array([expected_returns.get(asset, 0.0) for asset in assets])
        
        # Risk profile adjustments
        risk_aversion = self._get_risk_aversion(risk_profile)
        
        # Simple mean-variance optimization
        # In production, use cvxpy or scipy.optimize for proper constrained optimization
        weights = self._mean_variance_optimization(
            mu, cov_matrix, risk_aversion, constraints, investable_fraction
        )
        
        # Normalize weights to sum to investable fraction
        weights = weights / weights.sum() * investable_fraction
        
        # Create weights dictionary
        weight_dict = {asset: float(w) for asset, w in zip(assets, weights)}
        
        # Calculate portfolio metrics
        port_return = float(mu @ weights)
        port_volatility = float(np.sqrt(weights @ cov_matrix @ weights))
        sharpe = (port_return - self.risk_free_rate) / port_volatility if port_volatility > 0 else 0
        
        # Calculate VaR and CVaR (assuming normal distribution)
        var_95 = port_volatility * 1.645 - port_return  # 95% VaR
        cvar_95 = port_volatility * 2.063 - port_return  # 95% CVaR (approximate)
        
        # Calculate diversification metrics
        diversification_ratio = self._calculate_diversification_ratio(weights, cov_matrix)
        concentration_risk = self._calculate_concentration_risk(weights)
        
        # Mock sector allocation (in production, map assets to sectors)
        sector_allocation = self._estimate_sector_allocation(assets, weights)
        
        return AllocationResult(
            weights=weight_dict,
            expected_return=port_return,
            volatility=port_volatility,
            sharpe_ratio=sharpe,
            var_95=var_95,
            cvar_95=cvar_95,
            diversification_ratio=diversification_ratio,
            concentration_risk=concentration_risk,
            sector_allocation=sector_allocation,
        )
    
    def _mean_variance_optimization(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_aversion: float,
        constraints: PortfolioConstraints,
        investable_fraction: float
    ) -> np.ndarray:
        """
        Perform mean-variance optimization.
        
        Simple implementation - in production use proper quadratic programming.
        """
        n = len(expected_returns)
        
        # Initialize with equal weights
        weights = np.ones(n) / n * investable_fraction
        
        # Iterative optimization (simplified)
        # Higher risk aversion = more weight to lower variance assets
        for _ in range(100):  # Max iterations
            # Calculate gradient
            grad = expected_returns - risk_aversion * (cov_matrix @ weights)
            
            # Update weights in direction of gradient
            step_size = 0.01
            new_weights = weights + step_size * grad
            
            # Apply constraints
            new_weights = np.clip(new_weights, constraints.min_weight, constraints.max_weight)
            new_weights = new_weights / new_weights.sum() * investable_fraction
            
            # Check convergence
            if np.linalg.norm(new_weights - weights) < 1e-6:
                break
                
            weights = new_weights
        
        return weights
    
    def _get_risk_aversion(self, risk_profile: str) -> float:
        """Get risk aversion parameter based on risk profile."""
        risk_aversion_map = {
            "conservative": 3.0,
            "moderate": 2.0,
            "aggressive": 1.0,
        }
        return risk_aversion_map.get(risk_profile, 2.0)
    
    def _calculate_diversification_ratio(
        self,
        weights: np.ndarray,
        cov_matrix: np.ndarray
    ) -> float:
        """Calculate diversification ratio."""
        # DR = (sum of weighted volatilities) / portfolio volatility
        individual_vols = np.sqrt(np.diag(cov_matrix))
        weighted_vols = weights * individual_vols
        portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
        
        return float(weighted_vols.sum() / portfolio_vol) if portfolio_vol > 0 else 1.0
    
    def _calculate_concentration_risk(self, weights: np.ndarray) -> float:
        """Calculate concentration risk using Herfindahl index."""
        # HHI = sum of squared weights
        return float(np.sum(weights ** 2))
    
    def _estimate_sector_allocation(
        self,
        assets: List[str],
        weights: np.ndarray
    ) -> Dict[str, float]:
        """Estimate sector allocation (mock implementation)."""
        # In production, map each asset to its sector
        sectors = ["Technology", "Healthcare", "Finance", "Consumer", "Energy", "Industrial"]
        
        # Distribute weights randomly across sectors for demo
        sector_allocation = {}
        remaining_weight = weights.sum()
        
        for i, sector in enumerate(sectors):
            if i == len(sectors) - 1:
                sector_allocation[sector] = round(remaining_weight, 4)
            else:
                weight = remaining_weight * np.random.uniform(0.1, 0.3)
                sector_allocation[sector] = round(weight, 4)
                remaining_weight -= weight
        
        return sector_allocation
    
    def risk_parity_allocation(
        self,
        assets: List[str],
        cov_matrix: np.ndarray,
        constraints: PortfolioConstraints
    ) -> AllocationResult:
        """
        Create risk parity allocation where each asset contributes equally to risk.
        """
        n = len(assets)
        
        # Initialize with inverse volatility weights
        inv_vols = 1.0 / np.sqrt(np.diag(cov_matrix))
        weights = inv_vols / inv_vols.sum() * (1.0 - constraints.cash_reserve)
        
        weight_dict = {asset: float(w) for asset, w in zip(assets, weights)}
        
        port_volatility = float(np.sqrt(weights @ cov_matrix @ weights))
        
        return AllocationResult(
            weights=weight_dict,
            expected_return=0.0,  # Not optimized for return
            volatility=port_volatility,
            sharpe_ratio=0.0,
            var_95=port_volatility * 1.645,
            cvar_95=port_volatility * 2.063,
            diversification_ratio=1.5,  # Typically higher for risk parity
            concentration_risk=self._calculate_concentration_risk(weights),
            sector_allocation=self._estimate_sector_allocation(assets, weights),
        )
    
    def equal_risk_contribution(
        self,
        assets: List[str],
        cov_matrix: np.ndarray,
        constraints: PortfolioConstraints
    ) -> AllocationResult:
        """
        Create equal risk contribution portfolio.
        """
        n = len(assets)
        
        # Iterative algorithm for ERC
        weights = np.ones(n) / n * (1.0 - constraints.cash_reserve)
        
        for _ in range(100):
            # Calculate marginal risk contributions
            portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
            marginal_risk = (cov_matrix @ weights) / portfolio_vol
            risk_contrib = weights * marginal_risk
            
            # Update weights to equalize risk contributions
            target_risk = risk_contrib.mean()
            adjustment = target_risk / (risk_contrib + 1e-8)
            weights = weights * np.sqrt(adjustment)
            weights = weights / weights.sum() * (1.0 - constraints.cash_reserve)
        
        weight_dict = {asset: float(w) for asset, w in zip(assets, weights)}
        port_volatility = float(np.sqrt(weights @ cov_matrix @ weights))
        
        return AllocationResult(
            weights=weight_dict,
            expected_return=0.0,
            volatility=port_volatility,
            sharpe_ratio=0.0,
            var_95=port_volatility * 1.645,
            cvar_95=port_volatility * 2.063,
            diversification_ratio=1.5,
            concentration_risk=self._calculate_concentration_risk(weights),
            sector_allocation=self._estimate_sector_allocation(assets, weights),
        )
