import React, { useState } from "react";
import { useGeminiStream } from "../hooks/useGeminiStream";

export default function GeminiStreamPanel() {
  const [input, setInput] = useState("");
  const { runStream, output, loading, error } = useGeminiStream();

  const handleSubmit = (e) => {
    e.preventDefault();
    runStream(input);
  };

  return (
    <div className="p-4 border rounded shadow">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Gemini..."
          className="border p-2 w-full"
        />
        <button
          type="submit"
          className="mt-2 bg-blue-500 text-white px-4 py-2 rounded"
        >
          Stream
        </button>
      </form>

      {loading && <p>Streaming response...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}
      {output && (
        <div className="mt-4 whitespace-pre-wrap">
          {output}
        </div>
      )}
    </div>
  );
}
