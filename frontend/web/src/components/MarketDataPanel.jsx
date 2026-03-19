import { useMarketData } from "../hooks/useMarketData.js";

function MarketDataPanel() {
  const { data, error } = useMarketData();

  if (error) {
    return <p style={{ color: "red" }}>{error}</p>;
  }

  if (!data) {
    return <p>Loading market data...</p>;
  }

  return (
    <div className="market-data-panel">
      <h2>Live Market Data</h2>
      <p>
        <strong>Timestamp:</strong> {data.timestamp}
      </p>
      <ul>
        <li>
          <strong>AAPL:</strong> ${data.AAPL}
        </li>
        <li>
          <strong>TSLA:</strong> ${data.TSLA}
        </li>
        <li>
          <strong>NIFTY:</strong> {data.NIFTY}
        </li>
      </ul>
    </div>
  );
}

export default MarketDataPanel;
