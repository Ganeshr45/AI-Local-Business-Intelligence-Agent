import { RunReport } from "./types"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000"

export async function createRun(query: string): Promise<{ run_id: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  })
  if (!response.ok) {
    throw new Error("Failed to create run")
  }
  return response.json()
}

export async function getRunReport(runId: string): Promise<RunReport> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}`)
  if (!response.ok) {
    throw new Error("Failed to fetch run report")
  }
  return response.json()
}

export async function askMarket(runId: string, question: string): Promise<{ answer: string; citations: string[] }> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  })
  if (!response.ok) {
    throw new Error("Failed to get answer")
  }
  return response.json()
}

export function streamUrl(runId: string): string {
  return `${API_BASE}/api/runs/${runId}/stream`
}
