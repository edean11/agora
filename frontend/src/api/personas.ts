import { apiFetch } from './client'
import type { PersonaSummary, PersonaFull } from './types'

export interface PersonaCreateData {
  name: string
  age: number
  background: string
  openness?: string
  conscientiousness?: string
  extraversion?: string
  agreeableness?: string
  neuroticism?: string
  true_colors_primary?: string
  true_colors_secondary?: string
  care?: number
  fairness?: number
  loyalty?: number
  authority?: number
  sanctity?: number
  liberty?: number
  reasoning?: string
  thinking_mode?: string
  argument_style?: string
  pace?: string
  formality?: string
  directness?: string
  emotionality?: string
  conflict_approach?: string
  consensus?: string
  focus?: string
}

export interface PersonaDisambiguation {
  candidates: Array<{
    name: string
    description: string
  }>
}

export async function fetchPersonas(): Promise<PersonaSummary[]> {
  return apiFetch<PersonaSummary[]>('/api/personas')
}

export async function fetchPersona(id: string): Promise<PersonaFull> {
  return apiFetch<PersonaFull>(`/api/personas/${id}`)
}

export async function createPersona(data: PersonaCreateData): Promise<PersonaFull> {
  return apiFetch<PersonaFull>('/api/personas', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function generatePersonas(count: number): Promise<PersonaSummary[]> {
  return apiFetch<PersonaSummary[]>('/api/personas/generate', {
    method: 'POST',
    body: JSON.stringify({ count }),
  })
}

export async function createFromPerson(
  name: string,
  selectedIndex?: number
): Promise<PersonaFull | PersonaDisambiguation> {
  const body: { name: string; selected_index?: number } = { name }
  if (selectedIndex !== undefined) {
    body.selected_index = selectedIndex
  }
  return apiFetch<PersonaFull | PersonaDisambiguation>('/api/personas/from-person', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function deletePersona(id: string): Promise<void> {
  return apiFetch<void>(`/api/personas/${id}`, {
    method: 'DELETE',
  })
}
