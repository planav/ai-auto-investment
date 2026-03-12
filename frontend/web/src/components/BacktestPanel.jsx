import React, { useState } from "react";
import { Line } from "react-chartjs-2";

export default function BacktestPanel() {
  const [result, setResult] = useState(null);

  const runBacktest = async () => {
    const response = await fetch("http://localhost:8000/api/backtest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prices: [
          {"date":"2024-01-01","AAPL":150,"TSLA":700},
          {"date":"2024-01-02","AAPL":152,"TSLA":710},
          {"date":"2024-01-03","AAPL":148,"TSLA":690}
        ],
        weights: {"AAPL":0.6,"TSLA":0.4}
      })
    });
    const data = await response.json();
    setResult(data);
  };

  return (
    <div className="p-4 border rounded shadow">
      <button onClick={runBacktest} className="bg-green-500 text-white px-4 py-2 rounded">
        Run Backtest
      </button>

      {result && (
        <div className="mt-4">
          <h3 className="font-bold">Metrics</h3>
          <p>Sharpe Ratio: {result.sharpe_ratio.toFixed(2)}</p>
          <p>Sortino Ratio: {result.sortino_ratio.toFixed(2)}</p>
          <p>Max Drawdown: {(result.max_drawdown * 100).toFixed(2)}%</p>

          <Line
            data={{
              labels: result.dates,
              datasets: [
                {
                  label: "Cumulative Returns",
                  data: result.cumulative_returns,
                  borderColor: "blue",
                  fill: false,
                },
              ],
            }}
          />
        </div>
      )}
    </div>
  );
}
