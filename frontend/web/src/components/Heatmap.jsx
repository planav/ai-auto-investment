import React from "react";
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip } from "recharts";

// Example data: factor exposure vs. risk contribution
const data = [
  { factor: "Value", exposure: 0.3, risk: 0.25 },
  { factor: "Growth", exposure: 0.5, risk: 0.45 },
  { factor: "Momentum", exposure: 0.2, risk: 0.15 },
  { factor: "Volatility", exposure: 0.4, risk: 0.35 },
];

export default function Heatmap() {
  return (
    <div style={{ width: "100%", height: 400 }}>
      <h3>Factor Exposure Heatmap</h3>
      <ResponsiveContainer>
        <ScatterChart>
          <XAxis type="category" dataKey="factor" name="Factor" />
          <YAxis type="number" dataKey="exposure" name="Exposure" />
          <ZAxis type="number" dataKey="risk" range={[100, 400]} name="Risk Contribution" />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} />
          <Scatter name="Portfolio Factors" data={data} fill="#8884d8" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
