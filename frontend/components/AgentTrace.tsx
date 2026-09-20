"use client"

import { AgentEvent } from "@/lib/types"

const AGENT_ORDER = [
  { key: "query_planner", label: "Query Planner" },
  { key: "local_business_research", label: "Local Business Research" },
  { key: "competitor_analysis", label: "Competitor Analysis" },
  { key: "review_intelligence", label: "Review Intelligence" },
  { key: "website_analyzer", label: "Website Analyzer" },
  { key: "market_gap", label: "Market Gap Detection" },
  { key: "insight_generator", label: "Insight Generator" },
  { key: "recommendation_agent", label: "Recommendation Agent" },
  { key: "report_generator", label: "Report Generator" }
]

type Props = {
  events: AgentEvent[]
}

function statusFor(node: string, events: AgentEvent[]): "pending" | "active" | "done" | "failed" | "skipped" {
  const nodeEvents = events.filter((e) => e.node === node)
  if (nodeEvents.length === 0) return "pending"
  const last = nodeEvents[nodeEvents.length - 1]
  if (last.status === "completed") return "done"
  if (last.status === "failed") return "failed"
  if (last.status === "skipped") return "skipped"
  return "active"
}

export default function AgentTrace({ events }: Props) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sticky top-4">
      <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">Agent Trace</h3>
      <ol className="space-y-3">
        {AGENT_ORDER.map((agent) => {
          const status = statusFor(agent.key, events)
          const detail = events.filter((e) => e.node === agent.key).slice(-1)[0]?.detail
          return (
            <li key={agent.key} className="flex items-start gap-3">
              <span
                className={
                  "mt-1 h-2.5 w-2.5 rounded-full flex-shrink-0 " +
                  (status === "done"
                    ? "bg-green-500"
                    : status === "active"
                    ? "bg-blue-500 animate-pulse"
                    : status === "failed"
                    ? "bg-red-500"
                    : status === "skipped"
                    ? "bg-yellow-400"
                    : "bg-slate-200")
                }
              />
              <div>
                <p className={"text-sm " + (status === "pending" ? "text-slate-400" : "text-slate-800 font-medium")}>
                  {agent.label}
                </p>
                {detail ? <p className="text-xs text-slate-400 mt-0.5">{detail}</p> : null}
              </div>
            </li>
          )
        })}
      </ol>
    </div>
  )
}
