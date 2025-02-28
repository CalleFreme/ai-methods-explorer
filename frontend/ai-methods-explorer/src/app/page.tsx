"use client";

import { useEffect, useState } from "react";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import Link from "next/link";
//import ChatBot from "@/components/ChatBot";

interface AIMethod {
  id: string;
  name: string;
  description: string;
  model: string;
  endpoint: string;
}

export default function Home() {
  const [methods, setMethods] = useState<AIMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMethods = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://localhost:8000/api/methods");

        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        setMethods(data.methods);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch AI methods:", err);
        setError(
          "Failed to load AI methods. Please make sure the backend server is running."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchMethods();
  }, []);

  return (
    <div className="min-h-screen p-8">
      {/* Header */}
      <header className="flex justify-between items-center mb-12">
        <div className="flex items-center gap-4">
          <h1 className="text-3xl font-bold">AI Methods Explorer</h1>
        </div>
        <nav className="hidden md:block">
          <ul className="flex gap-6">
            <li>
              <Link href="/" className="hover:underline font-medium">
                Home
              </Link>
            </li>
            <li>
              <Link href="/history" className="hover:underline">
                History
              </Link>
            </li>
            <li>
              <Link href="/about" className="hover:underline">
                About
              </Link>
            </li>
          </ul>
        </nav>
      </header>

      {/* Main content */}
      <main>
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-6">Explore AI Methods</h2>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-foreground"></div>
            </div>
          ) : error ? (
            <div className="p-4 border border-red-300 bg-red-50 text-red-800 rounded-lg">
              {error}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {methods.map((method) => (
                <Link
                  href={`/tool/${method.id}`}
                  key={method.id}
                  className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
                >
                  <div className="p-6">
                    <h3 className="text-xl font-semibold mb-2">
                      {method.name}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 mb-4">
                      {method.description}
                    </p>
                    <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <span>Model: {method.model.split("/").pop()}</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* <ChatBot />*/}
    </div>
  );
}
