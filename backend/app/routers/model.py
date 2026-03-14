# app/routes/model.py
from fastapi import APIRouter
from app.tasks import train_model_task

router = APIRouter()


@router.post("/train-model")
async def train_model():
    task = train_model_task.delay()
    return {"task_id": task.id, "status": "training started"}


@router.post("/rebalance")
async def rebalance_portfolio(portfolio: dict):
    # Example drift detection logic
    target_alloc = {"AAPL": 0.5, "TSLA": 0.5}
    current_alloc = portfolio.get("allocations", {})
    suggestions = []

    for asset, target in target_alloc.items():
        current = current_alloc.get(asset, 0)
        if abs(current - target) > 0.05:  # drift threshold
            action = "BUY" if current < target else "SELL"
            suggestions.append({"asset": asset, "action": action, "amount": abs(target - current)})

    return {"suggestions": suggestions}
