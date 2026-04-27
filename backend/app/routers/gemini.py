from fastapi import APIRouter, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.claude_service import query_claude, stream_claude

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


@router.post("/gemini-query")
def gemini_query(request: QueryRequest):
    """Handle AI queries — powered by Anthropic Claude."""
    result = query_claude(request.query)
    return JSONResponse(content=result)


@router.websocket("/gemini-stream")
async def gemini_stream(websocket: WebSocket):
    """Stream AI responses over WebSocket — powered by Anthropic Claude."""
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        query = data.get("query", "")
        async for chunk in stream_claude(query):
            await websocket.send_json(chunk)
    except Exception as exc:
        await websocket.send_json({"error": str(exc)})
    finally:
        await websocket.close()
