"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { createRun } from "@/lib/api"

const EXAMPLES = [
  "Coffee shop in Indiranagar, Bangalore",
  "Gym in Koramangala, Bangalore",
  "Bakery in HSR Layout, Bangalore"
]

export default function HomePage() {
  const router = useRouter()
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function handleSubmit(value: string) {
    if (!value.trim() || loading) return
    setLoading(true)
    setError("")
    try {
      const result = await createRun(value)
      router.push(`/dashboard/${result.run_id}`)
    } catch (err) {
      setError("Could not start the research run. Is the backend running?")
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="max-w-xl w-full text-center">
        <p className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-3">AI Local Business Intelligence Agent</p>
        <h1 className="text-3xl font-bold text-slate-900 mb-3">Understand your local market in minutes</h1>
        <p className="text-slate-500 mb-8">
          Enter a business, category, or idea with a location. An autonomous agent pipeline will research
          competitors, reviews, pricing, and gaps, then generate an evidence-backed report.
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSubmit(query)
          }}
          className="flex gap-2 mb-4"
        >
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Coffee shop in Indiranagar, Bangalore"
            className="flex-1 border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-5 py-3 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Starting..." : "Research"}
          </button>
        </form>

        {error ? <p className="text-sm text-red-500 mb-4">{error}</p> : null}

        <div className="flex flex-wrap gap-2 justify-center">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              onClick={() => handleSubmit(example)}
              className="text-xs bg-white border border-slate-200 rounded-full px-3 py-1.5 text-slate-500 hover:border-blue-300 hover:text-blue-600"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </main>
  )
}
