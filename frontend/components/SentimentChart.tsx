"use client"

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts"
import { Review } from "@/lib/types"

type Props = {
  reviews: Review[]
}

const COLORS: Record<string, string> = {
  positive: "#16a34a",
  neutral: "#94a3b8",
  negative: "#dc2626"
}

export default function SentimentChart({ reviews }: Props) {
  const counts = { positive: 0, neutral: 0, negative: 0 }
  reviews.forEach((r) => {
    if (r.sentiment && counts[r.sentiment as keyof typeof counts] !== undefined) {
      counts[r.sentiment as keyof typeof counts] += 1
    }
  })
  const data = Object.entries(counts).map(([sentiment, count]) => ({ sentiment, count }))

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="text-base font-semibold text-slate-800 mb-1">Review Sentiment Distribution</h3>
      <p className="text-xs text-slate-400 mb-4">Across {reviews.length} reviews (target + competitors)</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
          <XAxis dataKey="sentiment" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={COLORS[entry.sentiment]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
