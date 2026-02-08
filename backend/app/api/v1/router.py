from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, portfolios, analysis, market, system

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
