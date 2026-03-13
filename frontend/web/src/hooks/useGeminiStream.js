import { useState } from "react";

export function useGeminiStream() {
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState("");
  const [error, setError] = useState(null);

  const runStream = (query) => {
    setLoading(true);
    setOutput("");
    setError(null);

    const ws = new WebSocket("ws://localhost:8000/api/gemini-stream");

    ws.onopen = () => {
      ws.send(JSON.stringify({ query }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.response) {
          setOutput((prev) => prev + data.response);
        }
      } catch {
        setOutput((prev) => prev + event.data);
      }
    };

    ws.onerror = () => {
      setError("WebSocket connection error");
      setLoading(false);
    };

    ws.onclose = () => {
      setLoading(false);
    };
  };

  return { runStream, output, loading, error };
}
