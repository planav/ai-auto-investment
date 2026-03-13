import { useEffect, useState } from "react";

export function useMarketStream() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/api/ws/market-data");

    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      setData(parsed);
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    return () => ws.close();
  }, []);

  return data;
}
