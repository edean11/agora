// Persona types
export interface PersonaSummary {
  id: string
  name: string
  age: number
  background_brief: string
}

export interface BigFiveTrait {
  level: string  // "Low" | "Medium" | "High"
  description: string
}

export interface PersonaFull {
  id: string
  name: string
  age: number
  background: string
  openness: BigFiveTrait
  conscientiousness: BigFiveTrait
  extraversion: BigFiveTrait
  agreeableness: BigFiveTrait
  neuroticism: BigFiveTrait
  true_colors_primary: string
  true_colors_primary_description: string
  true_colors_secondary: string
  true_colors_secondary_description: string
  care: number; fairness: number; loyalty: number
  authority: number; sanctity: number; liberty: number
  reasoning: string; reasoning_description: string
  thinking_mode: string; thinking_mode_description: string
  argument_style: string; argument_style_description: string
  pace: string; pace_description: string
  formality: string; formality_description: string
  directness: string; directness_description: string
  emotionality: string; emotionality_description: string
  conflict_approach: string; conflict_approach_description: string
  consensus: string; consensus_description: string
  focus: string; focus_description: string
  strengths: string; blind_spots: string; trigger_points: string
}

// Discussion types
export interface TranscriptEntry {
  timestamp: string
  speaker: string
  content: string
}

export interface DiscussionSummary {
  id: string
  topic: string
  created: string
  status: string
  participant_count: number
  message_count: number
}

export interface DiscussionFull {
  id: string
  topic: string
  created: string
  status: string
  participants: string[]
  transcript: TranscriptEntry[]
}

// Agent/Memory types
export interface MemoryEntry {
  id: string
  timestamp: string
  type: string
  importance: number
  content: string
}

export interface AskResponse {
  agent_name: string
  agent_id: string
  response: string
}

// WebSocket event types
export interface WSEvent {
  type: string
  [key: string]: unknown
}
