import React from "react";

export default function TrainModelButton() {
  const handleTrain = async () => {
    const res = await fetch("/api/model/train-model", { method: "POST" });
    const data = await res.json();
    console.log("Training started:", data);
  };

  return <button onClick={handleTrain}>Train Model</button>;
}
