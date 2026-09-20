"use client"

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts"
import { Business } from "@/lib/types"

type Props = {
  target: Business | null
  competitors: Business[]
}

export default function RatingChart({ target, competitors }: Props) {
  const businesses = target ? [target, ...competitors] : competitors
  const data = businesses
    .filter((b) => b.rating !== null)
    .map((b) => ({ name: b.is_target ? `${b.name} (You)` : b.name, rating: b.rating, isTarget: b.is_target }))

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <h3 className="text-base font-semibold text-slate-800 mb-2">Rating Comparison</h3>
        <p className="text-sm text-slate-400">No rating data available.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="text-base font-semibold text-slate-800 mb-4">Rating Comparison</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
          <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={70} />
          <YAxis domain={[0, 5]} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="rating" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.isTarget ? "#2563eb" : "#94a3b8"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
