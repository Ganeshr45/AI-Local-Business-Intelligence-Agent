"use client"

import { useEffect, useRef, useState } from "react"
import { getRunReport, streamUrl } from "@/lib/api"
import { AgentEvent, RunReport } from "@/lib/types"
import AgentTrace from "@/components/AgentTrace"
import CompetitorTable from "@/components/CompetitorTable"
import RatingChart from "@/components/RatingChart"
import SentimentChart from "@/components/SentimentChart"
import TopicFrequencyChart from "@/components/TopicFrequencyChart"
import OpportunityMatrix from "@/components/OpportunityMatrix"
import PriorityActionPlan from "@/components/PriorityActionPlan"
import EvidenceLog from "@/components/EvidenceLog"
import AskMarketChat from "@/components/AskMarketChat"

export default function DashboardPage({ params }: { params: { runId: string } }) {
  const { runId } = params
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [report, setReport] = useState<RunReport | null>(null)
  const [done, setDone] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    const source = new EventSource(streamUrl(runId))
    eventSourceRef.current = source

    source.addEventListener("progress", (event) => {
      const parsed = JSON.parse((event as MessageEvent).data)
      setEvents((prev) => [...prev, parsed])
    })

    source.addEventListener("done", () => {
      setDone(true)
      source.close()
    })

    source.onerror = () => {
      source.close()
    }

    return () => {
      source.close()
    }
  }, [runId])

  useEffect(() => {
    let cancelled = false
    let interval: ReturnType<typeof setInterval>

    async function poll() {
      try {
        const data = await getRunReport(runId)
        if (!cancelled) {
          setReport(data)
        }
      } catch (err) {
        // report not ready yet
      }
    }

    poll()
    interval = setInterval(poll, 2000)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [runId])

  useEffect(() => {
    if (done && report) {
      getRunReport(runId).then(setReport).catch(() => {})
    }
  }, [done, runId])

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-6">
          <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide">AI Local Business Intelligence Agent</p>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">
            {report?.query || "Researching your local market..."}
          </h1>
          {report ? (
            <p className="text-sm text-slate-500 mt-1">
              {report.category} · {report.location} · status: {report.status}
            </p>
          ) : null}
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr_320px] gap-6">
          <div>
            <AgentTrace events={events} />
          </div>

          <div className="space-y-6">
            {report ? (
              <>
                <CompetitorTable target={report.target_business} competitors={report.competitors} />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <RatingChart target={report.target_business} competitors={report.competitors} />
                  <SentimentChart reviews={report.reviews} />
                </div>
                <TopicFrequencyChart reviews={report.reviews} />
                <OpportunityMatrix recommendations={report.recommendations} />
                <PriorityActionPlan recommendations={report.recommendations} insights={report.insights} />
                <EvidenceLog insights={report.insights} evidenceCount={report.evidence_count} />
              </>
            ) : (
              <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400">
                Waiting for the agent pipeline to produce the first results...
              </div>
            )}
          </div>

          <div>
            <AskMarketChat runId={runId} />
          </div>
        </div>
      </div>
    </main>
  )
}
