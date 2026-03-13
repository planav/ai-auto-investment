import React from "react";

export default function RebalanceButton({ onRebalance }) {
  return (
    <button onClick={onRebalance}>
      Rebalance Now
    </button>
  );
}
