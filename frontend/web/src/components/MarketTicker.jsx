import React from "react";
import { useMarketStream } from "../hooks/useMarketStream";

export default function MarketTicker() {
  const data = useMarketStream();

  return (
    <div className="p-4 border rounded shadow">
      <h3 className="font-bold">Live Market Data</h3>
      {data ? (
        <ul>
          <li>Time: {data.timestamp}</li>
          <li>AAPL: ${data.AAPL}</li>
          <li>TSLA: ${data.TSLA}</li>
          <li>NIFTY: {data.NIFTY}</li>
        </ul>
      ) : (
        <p>Connecting to live feed...</p>
      )}
    </div>
  );
}
