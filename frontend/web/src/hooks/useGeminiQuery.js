import { useState } from "react";

export function useGeminiQuery() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const runQuery = async (query) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/gemini-query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch Gemini response");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { runQuery, result, loading, error };
}
