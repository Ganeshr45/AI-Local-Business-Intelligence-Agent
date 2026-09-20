"use client"

import { useState } from "react"
import { Insight } from "@/lib/types"

type Props = {
  insights: Insight[]
  evidenceCount: number
}

const LABEL_CLASS: Record<string, string> = {
  FACT: "label-fact",
  OBSERVATION: "label-observation",
  AI_INSIGHT: "label-insight"
}

export default function EvidenceLog({ insights, evidenceCount }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-800">Evidence & AI Insights</h3>
        <span className="text-xs text-slate-400">{evidenceCount} evidence records collected · {open ? "hide" : "show"}</span>
      </button>
      {open ? (
        <div className="mt-4 space-y-2">
          {insights.length === 0 ? (
            <p className="text-sm text-slate-400">No AI insights generated for this run.</p>
          ) : (
            insights.map((insight) => (
              <div key={insight.id} className="border border-slate-100 rounded-md p-2">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${LABEL_CLASS[insight.category] || "label-observation"}`}>
                  {insight.category.replace("_", " ")}
                </span>
                <p className="text-sm text-slate-700 mt-1">{insight.statement}</p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Confidence: {insight.confidence} · {insight.supporting_evidence_ids.length} supporting evidence item(s)
                </p>
              </div>
            ))
          )}
        </div>
      ) : null}
    </div>
  )
}
