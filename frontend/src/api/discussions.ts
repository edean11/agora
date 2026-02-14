import { apiFetch } from './client'
import type { DiscussionSummary, DiscussionFull } from './types'

export async function fetchDiscussions(): Promise<DiscussionSummary[]> {
  return apiFetch<DiscussionSummary[]>('/api/discussions')
}

export async function fetchDiscussion(id: string): Promise<DiscussionFull> {
  return apiFetch<DiscussionFull>(`/api/discussions/${id}`)
}

export async function createDiscussion(
  topic: string,
  agentIds?: string[],
  rounds?: number
): Promise<DiscussionSummary> {
  const body: { topic: string; agent_ids?: string[]; rounds?: number } = { topic }
  if (agentIds !== undefined) {
    body.agent_ids = agentIds
  }
  if (rounds !== undefined) {
    body.rounds = rounds
  }
  return apiFetch<DiscussionSummary>('/api/discussions', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function updateDiscussionStatus(
  id: string,
  status: string
): Promise<DiscussionSummary> {
  return apiFetch<DiscussionSummary>(`/api/discussions/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}

export async function deleteDiscussion(id: string): Promise<void> {
  return apiFetch<void>(`/api/discussions/${id}`, {
    method: 'DELETE',
  })
}
