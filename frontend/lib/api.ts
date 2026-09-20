import { RunReport } from "./types"

const API_BASE = "https://retying-sugar-marbling.ngrok-free.dev"

export async function createRun(query: string): Promise<{ run_id: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/runs?ngrok-skip-browser-warning=true`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
   },
    body: JSON.stringify({ query })
  })
  if (!response.ok) {
    throw new Error("Failed to create run")
  }
  return response.json()
}

export async function getRunReport(runId: string): Promise<RunReport> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}?ngrok-skip-browser-warning=true`)
   
  if (!response.ok) {
    throw new Error("Failed to fetch run report")
  }
  return response.json()
}

export async function askMarket(runId: string, question: string): Promise<{ answer: string; citations: string[] }> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/ask?ngrok-skip-browser-warning=true', {
    method: "POST",
    headers: {
    "Content-Type": "application/json"
    },
    body: JSON.stringify({ question })
  })
  if (!response.ok) {
    throw new Error("Failed to get answer")
  }
  return response.json()
}

export function streamUrl(runId: string): string {
  return '${API_BASE}/api/runs/${runId}/stream?ngrok-skip-browser-warning=true`
}
