import React, { useState } from "react";
import BacktestChart from "../components/BacktestChart";

export default function BacktestPanel() {
  const [result, setResult] = useState(null);

  const runBacktest = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/backtest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prices: [
            { date: "2024-01-01", AAPL: 150, TSLA: 700 },
            { date: "2024-01-02", AAPL: 152, TSLA: 710 },
            { date: "2024-01-03", AAPL: 148, TSLA: 690 }
          ],
          weights: { AAPL: 0.6, TSLA: 0.4 }
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Backtest error:", err);
    }
  };

  return (
    <div className="p-6 border rounded shadow bg-white">
      <button
        onClick={runBacktest}
        className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
      >
        Run Backtest
      </button>

      {result && (
        <div className="mt-6">
          {/* Metrics Summary */}
          <h3 className="font-bold mb-4">Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-blue-50 rounded shadow">
              <h4 className="font-semibold">Sharpe Ratio</h4>
              <p>{result.sharpe_ratio?.toFixed(2)}</p>
            </div>
            <div className="p-4 bg-green-50 rounded shadow">
              <h4 className="font-semibold">Sortino Ratio</h4>
              <p>{result.sortino_ratio?.toFixed(2)}</p>
            </div>
            <div className="p-4 bg-red-50 rounded shadow">
              <h4 className="font-semibold">Max Drawdown</h4>
              <p>{(result.max_drawdown * 100).toFixed(2)}%</p>
            </div>
          </div>

          {/* Equity Curve Chart */}
          <div className="mt-6">
            <BacktestChart equityCurve={result.equity_curve} />
          </div>
        </div>
      )}
    </div>
  );
}
