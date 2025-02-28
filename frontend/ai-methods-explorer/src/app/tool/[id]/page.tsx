"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface AIMethod {
  id: string;
  name: string;
  description: string;
  model: string;
  endpoint: string;
}

interface SummarizeResult {
  result: string;
}

interface SentimentResult {
  sentiment: string;
  score: number;
}

// Union type for all possible types
type AIResult = SummarizeResult | SentimentResult | null;

export default function ToolPage() {
  const params = useParams();
  const router = useRouter();
  const toolId = params.id as string;

  const [method, setMethod] = useState<AIMethod | null>(null);
  const [inputText, setInputText] = useState("");
  const wordCount = inputText.trim().split(/\s+/).length;
  const wordsOverLimit = Math.max(0, wordCount - 512);
  const [isTextTruncated, setIsTextTruncated] = useState(false);
  const [result, setResult] = useState<AIResult>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMethodDetails = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/methods");

        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        const foundMethod = data.methods.find((m: AIMethod) => m.id === toolId);

        if (foundMethod) {
          setMethod(foundMethod);
          setError(null);
        } else {
          setError("AI method not found");
          setTimeout(() => router.push("/"), 2000);
        }
      } catch (err) {
        console.error("Failed to fetch AI method details:", err);
        setError("Failed to load AI method details");
      }
    };

    if (toolId) {
      fetchMethodDetails();
    }
  }, [toolId, router]);

  // Function to truncate text to 512 words
  const truncateText = (text: string) => {
    const words = text.trim().split(/\s+/);
    return words.slice(0, 512).join(" ");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputText.trim() || !method) return;

    // Add warning text if text is too long (over 512 tokens)
    if (!inputText.trim() || !method) return;
    setIsTextTruncated(wordsOverLimit > 0);

    setLoading(true);
    setError(null);

    try {
      // Automatically use truncated text for API call
      const truncatedText = truncateText(inputText);
      const response = await fetch(`http://localhost:8000${method.endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: truncatedText }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(`Failed to process with ${method.name}:`, err);
      if (err instanceof Error && err.message.includes("413")) {
        setError(
          "Text is too long. Please enter text with less than 512 tokens."
        );
      } else {
        setError(`Failed to process with ${method.name}. Please try again.`);
      }
    } finally {
      setLoading(false);
    }
  };

  // Type guard functions
  function isSummarizeResult(result: AIResult): result is SummarizeResult {
    return result !== null && "result" in result;
  }

  function isSentimentResult(result: AIResult): result is SentimentResult {
    return result !== null && "sentiment" in result && "score" in result;
  }

  const insertLimitMarker = (text: string): string => {
    const words = text.trim().split(/\s+/);
    if (words.length <= 512) return text;

    const validWords = words.slice(0, 512);
    const overflowWords = words.slice(512);

    return validWords.join(" ") + " │⚠️│ " + overflowWords.join(" ");
  };

  const renderResult = () => {
    if (!result) return null;

    if (method?.id === "summarize" && isSummarizeResult(result)) {
      return (
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-2">Summary</h3>
          <p className="p-4 bg-gray-50 dark:bg-gray-800 rounded">
            {result.result}
          </p>
        </div>
      );
    }

    if (method?.id === "sentiment" && isSentimentResult(result)) {
      return (
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-2">Sentiment Analysis</h3>
          <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded">
            <p className="mb-2">
              <span className="font-medium">Sentiment:</span> {result.sentiment}
            </p>
            <p>
              <span className="font-medium">Confidence:</span>{" "}
              {(result.score * 100).toFixed(2)}%
            </p>
            <div className="w-full bg-gray-200 dark:bg-gray-700 h-2 mt-2 rounded-full overflow-hidden">
              <div
                className={`h-full ${
                  result.sentiment.toLowerCase() === "positive"
                    ? "bg-green-500"
                    : "bg-red-500"
                }`}
                style={{ width: `${result.score * 100}%` }}
              />
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">Result</h3>
        <pre className="p-4 bg-gray-50 dark:bg-gray-800 rounded overflow-x-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      </div>
    );
  };

  return (
    <div className="min-h-screen p-8">
      {/* Header */}
      <header className="flex justify-between items-center mb-12">
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            ← Back to Home
          </Link>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-4xl mx-auto">
        {error ? (
          <div className="p-4 border border-red-300 bg-red-50 text-red-800 rounded-lg">
            {error}
          </div>
        ) : !method ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-foreground"></div>
          </div>
        ) : (
          <section>
            <h1 className="text-3xl font-bold mb-2">{method.name}</h1>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              {method.description}
            </p>

            <form onSubmit={handleSubmit} className="mb-8">
              <div className="mb-4">
                <label
                  htmlFor="inputText"
                  className="block text-sm font-medium mb-2"
                >
                  Enter your text:
                </label>
                <textarea
                  id="inputText"
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[150px] bg-background text-foreground"
                  value={insertLimitMarker(inputText)}
                  onChange={(e) => {
                    // Remove marker when updating input
                    const cleanText = e.target.value.replace("│", "");
                    setInputText(cleanText);
                  }}
                  placeholder={`Enter text for ${method.name.toLowerCase()}...`}
                  required
                />
                {isTextTruncated && (
                  <p className="mt-2 text-sm text-amber-600">
                    Your text exceeds 512 words. Only the first 512 words will
                    be processed.
                    <span className="block mt-1">
                      Words that will be ignored: {wordsOverLimit}
                    </span>
                  </p>
                )}
              </div>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                disabled={loading || !inputText.trim()}
              >
                {loading ? "Processing..." : `Process with ${method.name}`}
              </button>
            </form>

            {loading ? (
              <div className="flex justify-center items-center h-40">
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-foreground"></div>
              </div>
            ) : (
              renderResult()
            )}
          </section>
        )}
      </main>

      {/* <ChatBot /> */}
    </div>
  );
}
