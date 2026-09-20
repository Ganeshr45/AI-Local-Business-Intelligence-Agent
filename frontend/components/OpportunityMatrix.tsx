"use client"

import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts"
import { Recommendation } from "@/lib/types"

type Props = {
  recommendations: Recommendation[]
}

export default function OpportunityMatrix({ recommendations }: Props) {
  const data = recommendations.map((r) => ({
    x: r.effort_score,
    y: r.impact_score,
    label: r.statement
  }))

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <h3 className="text-base font-semibold text-slate-800 mb-2">Opportunity Matrix</h3>
        <p className="text-sm text-slate-400">No recommendations available yet.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="text-base font-semibold text-slate-800 mb-1">Opportunity Matrix</h3>
      <p className="text-xs text-slate-400 mb-4">Top-left is high impact, low effort: the quick wins</p>
      <ResponsiveContainer width="100%" height={260}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid stroke="#f1f5f9" />
          <XAxis type="number" dataKey="x" name="Effort" domain={[0, 5]} tick={{ fontSize: 12 }} label={{ value: "Effort", position: "insideBottom", offset: -5, fontSize: 12 }} />
          <YAxis type="number" dataKey="y" name="Impact" domain={[0, 5]} tick={{ fontSize: 12 }} label={{ value: "Impact", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <ZAxis range={[120, 120]} />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} content={({ payload }) => {
            if (!payload || payload.length === 0) return null
            const point = payload[0].payload
            return (
              <div className="bg-white border border-slate-200 rounded-lg p-2 text-xs max-w-xs shadow">
                {point.label}
              </div>
            )
          }} />
          <Scatter data={data} fill="#2563eb" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
