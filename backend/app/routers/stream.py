from fastapi import APIRouter, WebSocket
import asyncio
import random
import datetime
import json

from app.services.claude_service import stream_claude

router = APIRouter()


# Simulated Market Data Stream
@router.websocket("/ws/market-data")
async def market_data_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "AAPL": round(150 + random.uniform(-2, 2), 2),
                "TSLA": round(700 + random.uniform(-5, 5), 2),
                "NIFTY": round(22000 + random.uniform(-50, 50), 2),
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except Exception:
        await websocket.close()


# Claude AI Streaming (WebSocket)
@router.websocket("/gemini-stream")
async def claude_stream_ws(websocket: WebSocket):
    """WebSocket streaming endpoint powered by Anthropic Claude."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            query = payload.get("query", "")

            async for chunk in stream_claude(query):
                await websocket.send_text(json.dumps(chunk))
    except Exception as exc:
        await websocket.send_text(json.dumps({"error": str(exc)}))
        await websocket.close()
