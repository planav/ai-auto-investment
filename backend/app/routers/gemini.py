from fastapi import APIRouter, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.gemini_service import query_gemini, stream_gemini

router = APIRouter()

# Define request schema


class GeminiQueryRequest(BaseModel):
    query: str


@router.post("/gemini-query")
async def gemini_query(request: GeminiQueryRequest):
    """
    Handle synchronous Gemini queries.
    """
    result = query_gemini(request.query)
    return JSONResponse(content=result)


@router.websocket("/gemini-stream")
async def gemini_stream(websocket: WebSocket):
    """
    Handle streaming Gemini responses over WebSocket.
    """
    await websocket.accept()
    # Receive initial query from client
    data = await websocket.receive_json()
    query = data.get("query")

    # Stream Gemini output chunk by chunk
    async for chunk in stream_gemini(query):
        await websocket.send_json(chunk)

    await websocket.close()
