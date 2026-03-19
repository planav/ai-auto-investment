from fastapi import APIRouter, WebSocket
import asyncio
import random
import datetime
import os
import json
from google import genai

router = APIRouter()

# ✅ Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------------
# 📊 Simulated Market Data Stream
# -------------------------------
@router.websocket("/ws/market-data")
async def market_data_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Simulated market data (replace with Polygon.io, Alpha Vantage, NSE/BSE feed)
            data = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "AAPL": round(150 + random.uniform(-2, 2), 2),
                "TSLA": round(700 + random.uniform(-5, 5), 2),
                "NIFTY": round(22000 + random.uniform(-50, 50), 2),
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)  # send every 2 seconds
    except Exception:
        await websocket.close()

# -------------------------------
# 🤖 Gemini AI Streaming
# -------------------------------
@router.websocket("/gemini-stream")
async def gemini_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive query from frontend
            data = await websocket.receive_text()
            payload = json.loads(data)
            query = payload.get("query", "")

            # Stream Gemini response
            stream = client.models.generate_content_stream(
                model="gemini-1.5-flash",
                contents=query
            )

            async for chunk in stream:
                if chunk.text:
                    await websocket.send_text(json.dumps({"response": chunk.text}))
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
        await websocket.close()
