from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.portfolio import Portfolio, PortfolioHolding
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioUpdate,
    PortfolioAnalysisRequest,
    PortfolioPerformance,
    RebalanceRecommendation,
    PortfolioHoldingCreate,
)
from app.agents.research_agent.agent import ResearchAgent
from app.engines.quant_engine.engine import QuantEngine, ModelType
from app.engines.portfolio_engine.engine import PortfolioEngine
from app.services.market_data import market_data_service

router = APIRouter()

# Initialize engines
research_agent = ResearchAgent()
quant_engine = QuantEngine()
portfolio_engine = PortfolioEngine()


@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get all portfolios for current user."""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    portfolios = result.scalars().all()
    return portfolios


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_in: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new portfolio with AI-generated holdings."""
    # Create portfolio
    portfolio = Portfolio(
        user_id=current_user.id,
        name=portfolio_in.name,
        description=portfolio_in.description,
        total_value=portfolio_in.investment_amount,
        cash_reserve_pct=portfolio_in.cash_reserve_pct,
        model_type=portfolio_in.model_type,
    )
    
    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)
    
    # Generate AI portfolio based on user preferences
    try:
        # Define asset universe based on user preferences
        preferred_assets = current_user.preferred_assets or "stocks,etfs"
        
        # Popular stocks for the portfolio
        asset_universe = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX",
            "AMD", "CRM", "ADBE", "PYPL", "UBER", "COIN", "SHOP", "SQ",
            "SPY", "QQQ", "VTI", "VEA", "VWO", "BND", "VNQ"
        ]
        
        # Use Research Agent to filter assets
        research_result = await research_agent.execute(
            context=None,
            asset_universe=asset_universe,
            max_assets=15,
        )
        
        filtered_assets = research_result.data.get("filtered_assets", asset_universe[:10])
        
        # Use Quant Engine to generate predictions
        model_type = ModelType.TEMPORAL_FUSION_TRANSFORMER
        if portfolio_in.model_type == "lstm_attention":
            model_type = ModelType.LSTM_ATTENTION
        elif portfolio_in.model_type == "graph_attention":
            model_type = ModelType.GRAPH_ATTENTION
            
        signals = await quant_engine.generate_signals(
            assets=filtered_assets[:10],
            model_type=model_type,
        )
        
        # Get predictions for portfolio optimization
        predictions = {
            symbol: pred.predicted_return 
            for symbol, pred in signals.predictions.items()
        }
        
        # Use Portfolio Engine to optimize allocation
        from app.engines.portfolio_engine.allocation import PortfolioConstraints
        
        constraints = PortfolioConstraints(
            min_weight=0.02,  # Min 2% per asset
            max_weight=0.20,  # Max 20% per asset
            min_assets=5,
            max_assets=10,
            cash_reserve=portfolio_in.cash_reserve_pct,
        )
        
        allocation_result = await portfolio_engine.optimize_allocation(
            assets=list(predictions.keys()),
            predictions=predictions,
            risk_profile=current_user.risk_tolerance or "moderate",
            constraints=constraints,
            optimization_method="mean_variance",
        )
        
        # Create holdings based on allocation
        cash_amount = portfolio_in.investment_amount * portfolio_in.cash_reserve_pct
        investable_amount = portfolio_in.investment_amount - cash_amount
        
        holdings_created = []
        for symbol, weight in allocation_result.weights.items():
            if weight > 0.01:  # Only include significant allocations
                # Get current price
                quote = await market_data_service.get_quote(symbol)
                current_price = quote.price if quote else 100.0
                
                # Calculate quantity
                market_value = investable_amount * weight
                quantity = market_value / current_price if current_price > 0 else 0
                
                # Get prediction for this asset
                prediction = signals.predictions.get(symbol)
                
                holding = PortfolioHolding(
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    asset_type="stock" if symbol not in ["SPY", "QQQ", "VTI", "VEA", "VWO", "BND", "VNQ"] else "etf",
                    weight=weight,
                    quantity=quantity,
                    avg_price=current_price,
                    current_price=current_price,
                    market_value=market_value,
                    predicted_return=prediction.predicted_return if prediction else 0.0,
                    confidence_score=prediction.confidence if prediction else 0.5,
                    signal_strength="buy" if prediction and prediction.predicted_return > 0.05 else "hold",
                )
                db.add(holding)
                holdings_created.append(holding)
        
        # Add cash holding
        cash_holding = PortfolioHolding(
            portfolio_id=portfolio.id,
            symbol="CASH",
            asset_type="cash",
            weight=portfolio_in.cash_reserve_pct,
            quantity=cash_amount,
            avg_price=1.0,
            current_price=1.0,
            market_value=cash_amount,
            predicted_return=0.0,
            confidence_score=1.0,
            signal_strength="hold",
        )
        db.add(cash_holding)
        
        # Update portfolio with AI metrics
        portfolio.expected_return = allocation_result.expected_return
        portfolio.volatility = allocation_result.volatility
        portfolio.sharpe_ratio = allocation_result.sharpe_ratio
        portfolio.var_95 = allocation_result.var_95
        portfolio.cvar_95 = allocation_result.cvar_95
        portfolio.ai_explanation = (
            f"AI-generated portfolio using {portfolio_in.model_type} model. "
            f"Optimized for {current_user.risk_tolerance} risk profile with "
            f"{current_user.investment_horizon}-year horizon. "
            f"Expected return: {allocation_result.expected_return:.1%}, "
            f"Volatility: {allocation_result.volatility:.1%}."
        )
        
        await db.commit()
        await db.refresh(portfolio)
        
    except Exception as e:
        # Log error but don't fail portfolio creation
        print(f"Error generating AI portfolio: {e}")
        # Create a simple default holding
        cash_holding = PortfolioHolding(
            portfolio_id=portfolio.id,
            symbol="CASH",
            asset_type="cash",
            weight=1.0,
            quantity=portfolio_in.investment_amount,
            avg_price=1.0,
            current_price=1.0,
            market_value=portfolio_in.investment_amount,
            predicted_return=0.0,
            confidence_score=1.0,
            signal_strength="hold",
        )
        db.add(cash_holding)
        await db.commit()
        await db.refresh(portfolio)
    
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get a specific portfolio by ID."""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    portfolio_update: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update a portfolio."""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    update_data = portfolio_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)
    
    await db.commit()
    await db.refresh(portfolio)
    
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a portfolio."""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    await db.delete(portfolio)
    await db.commit()


@router.get("/{portfolio_id}/performance", response_model=PortfolioPerformance)
async def get_portfolio_performance(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get portfolio performance metrics."""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    # Calculate performance metrics from real holdings
    total_value = portfolio.total_value or 0
    total_cost = sum(h.avg_price * h.quantity for h in portfolio.holdings if h.symbol != "CASH")
    total_return = total_value - total_cost if total_cost > 0 else 0
    total_return_pct = (total_return / total_cost * 100) if total_cost > 0 else 0
    
    return PortfolioPerformance(
        portfolio_id=portfolio.id,
        total_return=total_return,
        total_return_pct=total_return_pct,
        annualized_return=portfolio.expected_return or 0.0,
        volatility=portfolio.volatility or 0.0,
        sharpe_ratio=portfolio.sharpe_ratio or 0.0,
        max_drawdown=portfolio.max_drawdown or 0.0,
        var_95=portfolio.var_95 or 0.0,
        cvar_95=portfolio.cvar_95 or 0.0,
    )


@router.post("/{portfolio_id}/rebalance", response_model=RebalanceRecommendation)
async def rebalance_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Check if portfolio needs rebalancing."""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    # Calculate current weights
    total_value = portfolio.total_value or 0
    current_weights = {}
    target_weights = {}
    
    for holding in portfolio.holdings:
        if total_value > 0:
            current_weights[holding.symbol] = holding.market_value / total_value
            target_weights[holding.symbol] = holding.weight
    
    # Check if rebalancing is needed
    rebalance_check = await portfolio_engine.check_rebalance_needed(
        current_weights=current_weights,
        target_weights=target_weights,
        threshold=0.05,
    )
    
    return RebalanceRecommendation(
        portfolio_id=portfolio.id,
        rebalance_needed=rebalance_check.rebalance_needed,
        drift_pct=rebalance_check.drift_pct,
        recommendations=[
            {"symbol": symbol, "action": "rebalance"}
            for symbol in current_weights.keys()
        ] if rebalance_check.rebalance_needed else [],
    )


@router.post("/analyze")
async def analyze_and_create_portfolio(
    analysis_request: PortfolioAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Analyze assets and create an AI-generated portfolio."""
    try:
        # Use Research Agent to filter assets
        research_result = await research_agent.execute(
            context=None,
            asset_universe=analysis_request.preferred_assets,
            max_assets=analysis_request.max_assets,
        )
        
        filtered_assets = research_result.data.get("filtered_assets", [])
        
        # Use Quant Engine to generate predictions
        model_type = ModelType.TEMPORAL_FUSION_TRANSFORMER
        if analysis_request.model_type == "lstm_attention":
            model_type = ModelType.LSTM_ATTENTION
        elif analysis_request.model_type == "graph_attention":
            model_type = ModelType.GRAPH_ATTENTION
            
        signals = await quant_engine.generate_signals(
            assets=filtered_assets,
            model_type=model_type,
        )
        
        return {
            "status": "success",
            "assets_analyzed": len(filtered_assets),
            "top_picks": signals.rankings[:5],
            "market_regime": signals.market_regime,
            "overall_confidence": signals.overall_confidence,
            "predictions": {
                symbol: {
                    "predicted_return": pred.predicted_return,
                    "confidence": pred.confidence,
                }
                for symbol, pred in signals.predictions.items()
            },
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio analysis failed: {str(e)}",
        )


@router.post("/{portfolio_id}/holdings", response_model=PortfolioResponse)
async def add_holding(
    portfolio_id: int,
    holding_in: PortfolioHoldingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Add a holding to a portfolio."""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    # Get current price
    quote = await market_data_service.get_quote(holding_in.symbol)
    current_price = quote.price if quote else holding_in.avg_price
    
    holding = PortfolioHolding(
        portfolio_id=portfolio_id,
        symbol=holding_in.symbol,
        asset_type=holding_in.asset_type,
        weight=holding_in.weight,
        quantity=holding_in.quantity,
        avg_price=holding_in.avg_price,
        current_price=current_price,
        market_value=holding_in.quantity * current_price,
    )
    
    db.add(holding)
    
    # Update portfolio total value
    portfolio.total_value = (portfolio.total_value or 0) + holding.market_value
    
    await db.commit()
    await db.refresh(portfolio)
    
    return portfolio
