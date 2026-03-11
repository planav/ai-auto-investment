from fastapi import APIRouter, Request
from app.services.gemini_service import query_gemini

router = APIRouter()

@router.post("/gemini-query")
async def gemini_query(request: Request):
    data = await request.json()
    query = data.get("query")
    return query_gemini(query)
