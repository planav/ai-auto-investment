from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import JSONResponse
from app.services.gemini_service import query_gemini, stream_gemini

router = APIRouter()

@router.post("/gemini-query")
async def gemini_query(request: Request):
    """
    Handle synchronous Gemini queries.
    """
    data = await request.json()
    query = data.get("query")
    result = query_gemini(query)
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
