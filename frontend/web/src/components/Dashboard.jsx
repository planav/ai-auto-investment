import React, { useState } from "react";
import { useMarketData } from "../hooks/useMarketData";
import { useGeminiStream } from "../hooks/useGeminiStream";
import { useBacktest } from "../hooks/useBacktest";
import BacktestPanel from "../components/BacktestPanel";
import OptimizationPanel from "../components/OptimizationPanel";

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
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">AI Auto-Investment Dashboard</h1>

      {/* Grid layout for panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Market Data + Optimization */}
        <div className="p-4 border rounded bg-white shadow">
          <h2 className="text-lg font-bold mb-2">📈 Market Data</h2>
          {marketData ? (
            <pre className="text-sm whitespace-pre-wrap">
              {JSON.stringify(marketData, null, 2)}
            </pre>
          ) : (
            <p>Loading market data...</p>
          )}

          {/* Optimization Panel nested here */}
          <OptimizationPanel />
        </div>

        {/* Gemini Insights */}
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

        {/* Backtest Panel */}
        <BacktestPanel />
      </div>
    </div>
  );
}
