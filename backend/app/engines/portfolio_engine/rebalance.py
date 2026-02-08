from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class RebalanceRecommendation:
    """Recommendation for portfolio rebalancing."""
    rebalance_needed: bool
    drift_percentage: float
    threshold_breached: bool
    transactions: List[Dict]
    estimated_cost: float
    tax_impact: float
    expected_improvement: float


@dataclass
class RebalancePlan:
    """Detailed rebalancing execution plan."""
    portfolio_id: int
    current_weights: Dict[str, float]
    target_weights: Dict[str, float]
    trades: List[Dict]
    total_turnover: float
    estimated_cost: float
    execution_strategy: str


class RebalanceEngine:
    """Portfolio rebalancing engine."""
    
    def __init__(self):
        self.default_threshold = 0.05  # 5% drift threshold
        self.transaction_cost_rate = 0.001  # 0.1% per trade
    
    def check_rebalance_needed(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        threshold: Optional[float] = None
    ) -> RebalanceRecommendation:
        """
        Check if portfolio rebalancing is needed.
        
        Args:
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            threshold: Drift threshold (default 5%)
            
        Returns:
            RebalanceRecommendation with analysis
        """
        threshold = threshold or self.default_threshold
        
        # Calculate drift for each asset
        all_assets = set(current_weights.keys()) | set(target_weights.keys())
        drifts = {}
        
        for asset in all_assets:
            current = current_weights.get(asset, 0.0)
            target = target_weights.get(asset, 0.0)
            drifts[asset] = abs(current - target)
        
        # Calculate overall drift
        max_drift = max(drifts.values()) if drifts else 0
        avg_drift = np.mean(list(drifts.values())) if drifts else 0
        
        # Determine if rebalance is needed
        threshold_breached = max_drift > threshold
        
        # Generate transactions if needed
        transactions = []
        if threshold_breached:
            transactions = self._generate_transactions(
                current_weights, target_weights
            )
        
        # Estimate costs
        estimated_cost = len(transactions) * self.transaction_cost_rate
        
        return RebalanceRecommendation(
            rebalance_needed=threshold_breached,
            drift_percentage=max_drift,
            threshold_breached=threshold_breached,
            transactions=transactions,
            estimated_cost=estimated_cost,
            tax_impact=0.0,  # Would calculate in production
            expected_improvement=avg_drift * 0.5,  # Simplified estimate
        )
    
    def _generate_transactions(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float]
    ) -> List[Dict]:
        """Generate list of transactions needed for rebalancing."""
        transactions = []
        all_assets = set(current_weights.keys()) | set(target_weights.keys())
        
        for asset in all_assets:
            current = current_weights.get(asset, 0.0)
            target = target_weights.get(asset, 0.0)
            diff = target - current
            
            if abs(diff) > 0.001:  # Minimum trade threshold
                action = "buy" if diff > 0 else "sell"
                transactions.append({
                    "asset": asset,
                    "action": action,
                    "current_weight": current,
                    "target_weight": target,
                    "delta": abs(diff),
                })
        
        # Sort by delta (largest changes first)
        transactions.sort(key=lambda x: x["delta"], reverse=True)
        return transactions
    
    def generate_rebalance_plan(
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
        transactions = self._generate_transactions(current_weights, target_weights)
        
        # Calculate trades with dollar amounts
        trades = []
        total_turnover = 0.0
        
        for txn in transactions:
            dollar_amount = txn["delta"] * portfolio_value
            total_turnover += txn["delta"]
            
            trades.append({
                "asset": txn["asset"],
                "action": txn["action"],
                "current_weight": txn["current_weight"],
                "target_weight": txn["target_weight"],
                "delta_weight": txn["delta"],
                "dollar_amount": dollar_amount,
            })
        
        # Estimate total cost
        estimated_cost = total_turnover * portfolio_value * self.transaction_cost_rate
        
        # Determine execution strategy
        if total_turnover > 0.3:
            execution_strategy = "gradual"  # Execute over multiple days
        elif total_turnover > 0.15:
            execution_strategy = "phased"  # Execute in a few tranches
        else:
            execution_strategy = "immediate"  # Execute all at once
        
        return RebalancePlan(
            portfolio_id=portfolio_id,
            current_weights=current_weights,
            target_weights=target_weights,
            trades=trades,
            total_turnover=total_turnover,
            estimated_cost=estimated_cost,
            execution_strategy=execution_strategy,
        )
    
    def calculate_rebalance_frequency(
        self,
        volatility: float,
        transaction_costs: float,
        risk_tolerance: str = "moderate"
    ) -> str:
        """
        Calculate optimal rebalancing frequency.
        
        Args:
            volatility: Portfolio volatility
            transaction_costs: Transaction cost rate
            risk_tolerance: Risk tolerance level
            
        Returns:
            Recommended rebalancing frequency
        """
        # Higher volatility = more frequent rebalancing needed
        # Higher transaction costs = less frequent rebalancing
        
        if risk_tolerance == "conservative":
            base_frequency = 30  # Monthly
        elif risk_tolerance == "aggressive":
            base_frequency = 90  # Quarterly
        else:
            base_frequency = 60  # Bi-monthly
        
        # Adjust for volatility
        if volatility > 0.25:
            base_frequency = max(7, base_frequency // 2)
        elif volatility < 0.10:
            base_frequency = min(365, base_frequency * 2)
        
        # Adjust for transaction costs
        if transaction_costs > 0.005:
            base_frequency = min(365, int(base_frequency * 1.5))
        
        # Convert to string
        if base_frequency <= 7:
            return "weekly"
        elif base_frequency <= 30:
            return "monthly"
        elif base_frequency <= 90:
            return "quarterly"
        else:
            return "annually"
    
    def band_based_rebalancing(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        bandwidth: float = 0.10
    ) -> List[Dict]:
        """
        Apply tolerance bands to reduce unnecessary rebalancing.
        
        Only rebalance if weight drifts outside the tolerance band.
        
        Args:
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            bandwidth: Tolerance band width (e.g., 0.10 = +/- 10%)
            
        Returns:
            List of required transactions
        """
        transactions = []
        all_assets = set(current_weights.keys()) | set(target_weights.keys())
        
        for asset in all_assets:
            current = current_weights.get(asset, 0.0)
            target = target_weights.get(asset, 0.0)
            
            # Calculate tolerance band
            lower_bound = target * (1 - bandwidth)
            upper_bound = target * (1 + bandwidth)
            
            # Check if outside band
            if current < lower_bound:
                # Need to buy
                transactions.append({
                    "asset": asset,
                    "action": "buy",
                    "current_weight": current,
                    "target_weight": target,
                    "delta": target - current,
                    "reason": "below_tolerance_band",
                })
            elif current > upper_bound:
                # Need to sell
                transactions.append({
                    "asset": asset,
                    "action": "sell",
                    "current_weight": current,
                    "target_weight": target,
                    "delta": current - target,
                    "reason": "above_tolerance_band",
                })
        
        return transactions
    
    def cash_flow_rebalancing(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        cash_inflow: float = 0.0,
        cash_outflow: float = 0.0,
        portfolio_value: float = 100000.0
    ) -> List[Dict]:
        """
        Incorporate cash flows into rebalancing decisions.
        
        Use cash inflows to buy underweight assets.
        Use cash outflows to sell overweight assets.
        
        Args:
            current_weights: Current weights
            target_weights: Target weights
            cash_inflow: New cash to invest
            cash_outflow: Cash to withdraw
            portfolio_value: Current portfolio value
            
        Returns:
            List of transactions
        """
        transactions = []
        
        # Calculate deviations from target
        deviations = {}
        for asset in target_weights:
            current = current_weights.get(asset, 0.0)
            deviations[asset] = current - target_weights[asset]
        
        # Handle inflows - buy underweight assets
        if cash_inflow > 0:
            underweight_assets = [
                asset for asset, dev in deviations.items() if dev < -0.01
            ]
            
            if underweight_assets:
                inflow_per_asset = cash_inflow / len(underweight_assets)
                for asset in underweight_assets:
                    weight_delta = inflow_per_asset / portfolio_value
                    transactions.append({
                        "asset": asset,
                        "action": "buy",
                        "amount": inflow_per_asset,
                        "weight_delta": weight_delta,
                        "reason": "cash_inflow",
                    })
        
        # Handle outflows - sell overweight assets
        if cash_outflow > 0:
            overweight_assets = [
                asset for asset, dev in deviations.items() if dev > 0.01
            ]
            
            if overweight_assets:
                outflow_per_asset = cash_outflow / len(overweight_assets)
                for asset in overweight_assets:
                    weight_delta = outflow_per_asset / portfolio_value
                    transactions.append({
                        "asset": asset,
                        "action": "sell",
                        "amount": outflow_per_asset,
                        "weight_delta": weight_delta,
                        "reason": "cash_outflow",
                    })
        
        return transactions
