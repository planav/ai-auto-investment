import React, { useState } from "react";

export default function OptimizationPanel() {
  const [returns, setReturns] = useState([
    { date: "2024-01-01", AAPL: 0.01, TSLA: -0.02 },
    { date: "2024-01-02", AAPL: 0.015, TSLA: 0.005 },
    { date: "2024-01-03", AAPL: -0.01, TSLA: 0.02 },
  ]);
  const [optimized, setOptimized] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("http://localhost:8000/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ returns }),
      });
      const data = await response.json();
      setOptimized(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 border rounded shadow bg-white mt-6">
      <h2 className="text-lg font-bold mb-4">⚖️ Portfolio Optimization</h2>

      <button
        onClick={runOptimization}
        className="bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600"
      >
        Run Optimization
      </button>

      {loading && <p className="mt-4">Optimizing portfolio...</p>}
      {error && <p className="mt-4 text-red-500">Error: {error}</p>}

      {optimized && (
        <div className="mt-6">
          <h3 className="font-bold mb-2">Optimized Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 rounded shadow">
              <h4 className="font-semibold">Optimized Weights</h4>
              <pre className="text-sm whitespace-pre-wrap">
                {JSON.stringify(optimized.optimized_weights, null, 2)}
              </pre>
            </div>
            <div className="p-4 bg-green-50 rounded shadow">
              <h4 className="font-semibold">Metrics</h4>
              <p>Expected Return: {optimized.expected_return}</p>
              <p>Expected Volatility: {optimized.expected_volatility}</p>
              <p>Sharpe Ratio: {optimized.sharpe_ratio}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
