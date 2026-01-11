from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="AI Auto Investment API")

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "OK"}
