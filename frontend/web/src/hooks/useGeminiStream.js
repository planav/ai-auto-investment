import { useState, useEffect, useRef } from "react";

export function useGeminiStream() {
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState("");
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  const runStream = (query) => {
    setLoading(true);
    setOutput("");
    setError(null);

    // Close any existing connection before starting a new one
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const ws = new WebSocket("ws://localhost:8000/api/gemini-stream");
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ query }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.response) {
          setOutput((prev) => prev + data.response);
        } else if (data.error) {
          setError(data.error);
          setLoading(false);
        }
      } catch {
        // Fallback if backend sends plain text
        setOutput((prev) => prev + event.data);
      }
    };

    ws.onerror = () => {
      setError("WebSocket connection error");
      setLoading(false);
    };

    ws.onclose = () => {
      setLoading(false);
      wsRef.current = null;
    };
  };

  // Cleanup WebSocket when component unmounts
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  return { runStream, output, loading, error };
}
