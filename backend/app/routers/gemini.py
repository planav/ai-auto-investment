from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.services.gemini_service import query_gemini, stream_gemini

router = APIRouter()


@router.post("/gemini-query")
async def gemini_query(request: Request):
    data = await request.json()
    query = data.get("query")
    return query_gemini(query)


@router.post("/gemini-stream")
async def gemini_stream(request: Request):
    data = await request.json()
    query = data.get("query")
    return StreamingResponse(stream_gemini(query), media_type="text/event-stream")
