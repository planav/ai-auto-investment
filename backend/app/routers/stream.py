from fastapi import APIRouter, WebSocket
import asyncio
import random
import datetime

router = APIRouter()

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
