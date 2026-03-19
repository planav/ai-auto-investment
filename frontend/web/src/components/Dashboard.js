import React, { useState } from "react";
import { useMarketData } from "../hooks/useMarketData";
import { useGeminiStream } from "../hooks/useGeminiStream";

export default function Dashboard() {
  const { marketData } = useMarketData(); // updates every 2s
  const { runStream, output, loading, error } = useGeminiStream();
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      runStream(query);
    }
  };

  return (
    <div className="grid grid-cols-2 gap-4 p-6">
      {/* Market Data Panel */}
      <div className="p-4 border rounded bg-white shadow">
        <h2 className="text-lg font-bold mb-2">📈 Market Data</h2>
        {marketData ? (
          <pre className="text-sm whitespace-pre-wrap">
            {JSON.stringify(marketData, null, 2)}
          </pre>
        ) : (
          <p>Loading market data...</p>
        )}
      </div>

      {/* Gemini Insights Panel */}
      <div className="p-4 border rounded bg-white shadow">
        <h2 className="text-lg font-bold mb-2">🤖 Gemini Insights</h2>

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
        <div className="whitespace-pre-wrap text-sm">{output}</div>
      </div>
    </div>
  );
}
