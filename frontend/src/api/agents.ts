import { apiFetch } from './client'
import type { AskResponse, MemoryEntry } from './types'

export async function askAgent(agentId: string, question: string): Promise<AskResponse> {
  return apiFetch<AskResponse>(`/api/agents/${agentId}/ask`, {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
}

export async function fetchMemory(agentId: string, last?: number): Promise<MemoryEntry[]> {
  const params = last !== undefined ? `?last=${last}` : ''
  return apiFetch<MemoryEntry[]>(`/api/agents/${agentId}/memory${params}`)
}

export async function triggerReflection(agentId: string): Promise<unknown> {
  return apiFetch<unknown>(`/api/agents/${agentId}/reflect`, {
    method: 'POST',
  })
}

export async function fetchReflections(
  agentId: string
): Promise<{ agent_id: string; agent_name: string; reflections: string }> {
  return apiFetch<{ agent_id: string; agent_name: string; reflections: string }>(
    `/api/agents/${agentId}/reflections`
  )
}
