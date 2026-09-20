"use client"

import { useState } from "react"
import { Recommendation, Insight } from "@/lib/types"

type Props = {
  recommendations: Recommendation[]
  insights: Insight[]
}

export default function PriorityActionPlan({ recommendations, insights }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const insightById = (id: string) => insights.find((i) => i.id === id)

  if (recommendations.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <h3 className="text-base font-semibold text-slate-800 mb-2">Priority Action Plan</h3>
        <p className="text-sm text-slate-400">No recommendations available yet.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="text-base font-semibold text-slate-800 mb-4">Priority Action Plan</h3>
      <ol className="space-y-3">
        {recommendations.map((rec) => {
          const isOpen = expandedId === rec.id
          return (
            <li key={rec.id} className="border border-slate-100 rounded-lg">
              <button
                onClick={() => setExpandedId(isOpen ? null : rec.id)}
                className="w-full text-left p-3 flex items-start gap-3"
              >
                <span className="label-recommendation text-xs font-semibold px-2 py-0.5 rounded-full flex-shrink-0 mt-0.5">
                  #{rec.priority_rank}
                </span>
                <div className="flex-1">
                  <p className="text-sm text-slate-800">{rec.statement}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    Impact {rec.impact_score}/5 · Effort {rec.effort_score}/5
                  </p>
                </div>
                <span className="text-slate-400 text-xs">{isOpen ? "hide evidence" : "show evidence"}</span>
              </button>
              {isOpen ? (
                <div className="px-3 pb-3 space-y-2">
                  {rec.supporting_insight_ids.map((insightId) => {
                    const insight = insightById(insightId)
                    if (!insight) return null
                    return (
                      <div key={insightId} className="bg-slate-50 rounded-md p-2">
                        <span className="label-insight text-xs font-semibold px-2 py-0.5 rounded-full">AI INSIGHT</span>
                        <p className="text-xs text-slate-600 mt-1">{insight.statement}</p>
                        <p className="text-[11px] text-slate-400 mt-1">Confidence: {insight.confidence}</p>
                      </div>
                    )
                  })}
                </div>
              ) : null}
            </li>
          )
        })}
      </ol>
    </div>
  )
}
