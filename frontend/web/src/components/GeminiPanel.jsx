import React, { useState } from "react";
import { useGeminiQuery } from "../hooks/useGeminiQuery";

export default function GeminiPanel() {
  const [input, setInput] = useState("");
  const { runQuery, result, loading, error } = useGeminiQuery();

  const handleSubmit = (e) => {
    e.preventDefault();
    runQuery(input);
  };

  return (
    <div className="p-4 border rounded shadow">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Gemini about finance..."
          className="border p-2 w-full"
        />
        <button
          type="submit"
          className="mt-2 bg-blue-500 text-white px-4 py-2 rounded"
        >
          Query
        </button>
      </form>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}
      {result && (
        <div className="mt-4">
          <h3 className="font-bold">Result:</h3>
          <p>{result.result}</p>
          <p className="text-gray-600">
            Explanation: {result.explanation}
          </p>
          <p className="text-sm text-gray-400">
            Confidence: {result.confidence}
          </p>
        </div>
      )}
    </div>
  );
}
