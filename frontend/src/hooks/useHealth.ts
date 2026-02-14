import { useQuery } from '@tanstack/react-query'

interface HealthResponse {
  status: string
  ollama_available: boolean
}

async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch('/api/health')
  if (!response.ok) {
    throw new Error('Health check failed')
  }
  return response.json()
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: checkHealth,
    refetchInterval: 30_000, // Check every 30 seconds
    retry: false, // Don't retry health checks
  })
}
