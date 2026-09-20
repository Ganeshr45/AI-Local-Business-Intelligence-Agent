"use client"

import { useState } from "react"
import { askMarket } from "@/lib/api"

type Props = {
  runId: string
}

type ChatMessage = {
  role: "user" | "agent"
  text: string
}

const SUGGESTED_QUESTIONS = [
  "What are customers complaining about most?",
  "What price range should I target?",
  "Which competitor should I study?",
  "What are the biggest opportunities?"
]

export default function AskMarketChat({ runId }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleAsk(question: string) {
    if (!question.trim() || loading) return
    setMessages((prev) => [...prev, { role: "user", text: question }])
    setInput("")
    setLoading(true)
    try {
      const result = await askMarket(runId, question)
      setMessages((prev) => [...prev, { role: "agent", text: result.answer }])
    } catch (err) {
      setMessages((prev) => [...prev, { role: "agent", text: "Something went wrong answering that question." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 flex flex-col h-[520px] sticky top-4">
      <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">Ask Your Local Market</h3>

      <div className="flex-1 overflow-y-auto space-y-3 mb-3">
        {messages.length === 0 ? (
          <div className="space-y-2">
            <p className="text-xs text-slate-400 mb-2">Try asking:</p>
            {SUGGESTED_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => handleAsk(q)}
                className="block w-full text-left text-xs bg-slate-50 hover:bg-slate-100 rounded-md px-3 py-2 text-slate-600"
              >
                {q}
              </button>
            ))}
          </div>
        ) : (
          messages.map((m, idx) => (
            <div key={idx} className={m.role === "user" ? "text-right" : "text-left"}>
              <span
                className={
                  "inline-block rounded-lg px-3 py-2 text-sm max-w-[90%] " +
                  (m.role === "user" ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-700")
                }
              >
                {m.text}
              </span>
            </div>
          ))
        )}
        {loading ? <p className="text-xs text-slate-400">Retrieving grounded evidence...</p> : null}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          handleAsk(input)
        }}
        className="flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your local market..."
          className="flex-1 border border-slate-200 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button type="submit" className="bg-blue-600 text-white text-sm px-3 py-2 rounded-md hover:bg-blue-700">
          Ask
        </button>
      </form>
    </div>
  )
}
