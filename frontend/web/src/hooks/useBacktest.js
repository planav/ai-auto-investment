import { useState } from "react";
import axios from "axios";

export function useBacktest() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runBacktest = async (prices, weights) => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post("http://localhost:8000/api/backtest", {
        prices,
        weights,
      });
      setResult(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateMetrics = async (returns) => {
    try {
      const res = await axios.post("http://localhost:8000/api/backtest/metrics", {
        returns,
      });
      return res.data;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  return { runBacktest, calculateMetrics, result, loading, error };
}
