import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function DualEquityChart({ userCurve, optimizedCurve, dates }) {
  if (!userCurve || !optimizedCurve || !dates) {
    return <p>No equity curve data available.</p>;
  }

  // Format data for Recharts
  const chartData = dates.map((date, i) => ({
    date,
    user: userCurve[i],
    optimized: optimizedCurve[i],
  }));

  return (
    <div className="p-4 border rounded bg-white shadow mt-6">
      <h2 className="text-lg font-bold mb-2">📈 Equity Curve Comparison</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="user"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            name="User Portfolio"
          />
          <Line
            type="monotone"
            dataKey="optimized"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Optimized Portfolio"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
