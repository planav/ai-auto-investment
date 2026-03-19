import { useState, useEffect } from "react";

export function useMarketData() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/api/ws/market-data");

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed);
      } catch {
        setError("Failed to parse market data");
      }
    };

    ws.onerror = () => {
      setError("WebSocket connection error");
    };

    return () => {
      ws.close();
    };
  }, []);

  return { data, error };
}
