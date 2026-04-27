import React, { useState } from "react";
import { useGeminiStream } from "../hooks/useGeminiStream";

export default function InsightsPanel() {
  const { runStream, output, loading, error } = useGeminiStream();
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      runStream(query);
    }
  };

  return (
    <div className="p-4 border rounded bg-white shadow">
      <h2 className="text-lg font-bold mb-2">Gemini Insights</h2>

      <form onSubmit={handleSubmit} className="mb-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask Gemini about the market..."
          className="border p-2 w-full mb-2"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Run Stream
        </button>
      </form>

      {loading && <p>Streaming...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}
      <div className="whitespace-pre-wrap">{output}</div>
    </div>
  );
}
