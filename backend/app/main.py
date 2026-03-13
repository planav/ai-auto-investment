from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import gemini
from app.api.routes import router
from app.core.config import get_settings
from app.routers import backtest
from app.routers import stream
from app.routers import model

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.app_name} in {settings.environment} mode")
    yield
    # Shutdown
    print(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    description="AI-powered auto-investment platform with deep learning models",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

#  Register Gemini router here (not inside FastAPI constructor)
app.include_router(gemini.router, prefix="/api", tags=["Gemini"])

#  Register your existing API routes
app.include_router(router, prefix="/api")

# register backtest routers
app.include_router(backtest.router, prefix="/api", tags=["Backtest"])

# register streaming routers
app.include_router(stream.router, prefix="/api", tags=["Streaming"])

# register model routers
app.include_router(model.router, prefix="/api/model", tags=["Model"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
