import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function ComparisonChart({ userWeights, optimizedWeights }) {
  if (!userWeights || !optimizedWeights) {
    return <p>No weight data available.</p>;
  }

  // Format data for Recharts
  const assets = Object.keys(userWeights);
  const chartData = assets.map((asset) => ({
    asset,
    user: userWeights[asset] * 100,       // convert to %
    optimized: optimizedWeights[asset] * 100,
  }));

  return (
    <div className="p-4 border rounded bg-white shadow mt-6">
      <h2 className="text-lg font-bold mb-2">📊 Weight Comparison</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="asset" />
          <YAxis unit="%" />
          <Tooltip />
          <Legend />
          <Bar dataKey="user" fill="#2563eb" name="User Weights" />
          <Bar dataKey="optimized" fill="#10b981" name="Optimized Weights" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
