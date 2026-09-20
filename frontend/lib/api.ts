import { RunReport } from "./types"

const API_BASE = "https://retying-sugar-marbling.ngrok-free.dev"

export async function createRun(query: string): Promise<{ run_id: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/runs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "69420"
    },
    body: JSON.stringify({ query })
  })
  if (!response.ok) {
    throw new Error("Failed to create run")
  }
  return response.json()
}

export async function getRunReport(runId: string): Promise<RunReport> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}`, {
    headers: {
      "ngrok-skip-browser-warning": "69420"
    }
  })
  if (!response.ok) {
    throw new Error("Failed to fetch run report")
  }
  return response.json()
}

export async function askMarket(runId: string, question: string): Promise<{ answer: string; citations: string[] }> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json",
             "ngrok-skip-browser-warning":"69420"
    },
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
