from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update current user profile."""
    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Handle password separately
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Update user attributes
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/me/preferences")
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get user investment preferences."""
    return {
        "risk_tolerance": current_user.risk_tolerance,
        "investment_horizon": current_user.investment_horizon,
        "initial_investment": current_user.initial_investment,
        "monthly_contribution": current_user.monthly_contribution,
        "preferred_assets": current_user.preferred_assets,
    }


@router.put("/me/preferences")
async def update_user_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update user investment preferences."""
    allowed_fields = [
        "risk_tolerance",
        "investment_horizon",
        "initial_investment",
        "monthly_contribution",
        "preferred_assets",
    ]
    
    for field, value in preferences.items():
        if field in allowed_fields:
            setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "risk_tolerance": current_user.risk_tolerance,
        "investment_horizon": current_user.investment_horizon,
        "initial_investment": current_user.initial_investment,
        "monthly_contribution": current_user.monthly_contribution,
        "preferred_assets": current_user.preferred_assets,
    }
