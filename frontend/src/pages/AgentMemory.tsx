import { useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchPersona } from '../api/personas'
import { fetchMemory, fetchReflections, triggerReflection } from '../api/agents'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Skeleton from '../components/ui/Skeleton'
import AgentAvatar from '../components/discussions/AgentAvatar'
import MemoryTimeline from '../components/agents/MemoryTimeline'
import { useToast } from '../hooks/useToast'

function AgentMemory() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showToast } = useToast()

  const { data: persona, isLoading: personaLoading, error: personaError } = useQuery({
    queryKey: ['persona', id],
    queryFn: () => fetchPersona(id!),
    enabled: !!id,
  })

  const { data: memoryEntries = [], isLoading: memoryLoading, error: memoryError } = useQuery({
    queryKey: ['memory', id],
    queryFn: () => fetchMemory(id!, 50),
    enabled: !!id,
  })

  const { data: reflectionsData, isLoading: reflectionsLoading, error: reflectionsError } = useQuery({
    queryKey: ['reflections', id],
    queryFn: () => fetchReflections(id!),
    enabled: !!id,
  })

  const reflectMutation = useMutation({
    mutationFn: () => triggerReflection(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memory', id] })
      queryClient.invalidateQueries({ queryKey: ['reflections', id] })
      showToast('Reflection completed successfully', 'success')
    },
    onError: () => {
      showToast('Failed to trigger reflection', 'error')
    },
  })

  useEffect(() => {
    if (personaError) {
      showToast('Unable to load agent', 'error')
    }
  }, [personaError, showToast])

  useEffect(() => {
    if (memoryError) {
      showToast('Unable to load memory', 'error')
    }
  }, [memoryError, showToast])

  useEffect(() => {
    if (reflectionsError) {
      showToast('Unable to load reflections', 'error')
    }
  }, [reflectionsError, showToast])

  const handleTriggerReflection = () => {
    reflectMutation.mutate()
  }

  const parseReflections = (reflectionsText: string) => {
    if (!reflectionsText || reflectionsText.trim() === '') {
      return []
    }

    // Split by question pattern (lines starting with "Question:")
    const sections = reflectionsText.split(/^Question:/gm).filter((s) => s.trim())

    return sections.map((section) => {
      const lines = section.trim().split('\n')
      const question = lines[0].trim()

      // Extract evidence IDs (lines with "Evidence:")
      const evidenceMatch = section.match(/Evidence: \[(.*?)\]/s)
      const evidenceIds = evidenceMatch ? evidenceMatch[1].split(',').map((id) => id.trim()) : []

      // Extract insight (everything after "Insight:")
      const insightMatch = section.match(/Insight:\s*([\s\S]*?)(?=Question:|$)/s)
      const insight = insightMatch ? insightMatch[1].trim() : ''

      return { question, evidenceIds, insight }
    })
  }

  const isLoading = personaLoading || memoryLoading || reflectionsLoading

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <div className="flex items-start gap-4">
            <Skeleton variant="circle" className="h-16 w-16" />
            <div className="flex-1 space-y-2">
              <Skeleton variant="title" className="w-1/3" />
              <Skeleton variant="text" className="w-2/3" />
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <Skeleton variant="title" className="w-1/4" />
            <Skeleton variant="text" className="w-32 h-10" />
          </div>
        </Card>
        {[1, 2].map((i) => (
          <Card key={i}>
            <div className="space-y-4">
              <Skeleton variant="title" className="w-1/3" />
              <Skeleton variant="text" className="w-full" />
              <Skeleton variant="text" className="w-3/4" />
            </div>
          </Card>
        ))}
      </div>
    )
  }

  if (!persona) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <div className="text-center py-12 space-y-4">
            <h1 className="font-serif text-2xl text-gold">Agent not found</h1>
            <p className="font-sans text-charcoal-light">
              The agent you're looking for doesn't exist or may have been deleted.
            </p>
            <div className="pt-4">
              <Button onClick={() => navigate('/personas')}>
                Back to Personas
              </Button>
            </div>
          </div>
        </Card>
      </div>
    )
  }

  const reflections = reflectionsData ? parseReflections(reflectionsData.reflections) : []

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Agent Header */}
      <Card>
        <div className="flex items-start gap-4">
          <AgentAvatar name={persona.name} />
          <div className="flex-1">
            <h1 className="font-display text-3xl text-charcoal">
              {persona.name}
            </h1>
            <p className="font-sans text-sm text-charcoal-light mt-2 line-clamp-2">
              {persona.background}
            </p>
          </div>
        </div>
      </Card>

      {/* Actions Bar */}
      <Card>
        <div className="flex items-center justify-between">
          <h2 className="font-display text-2xl text-charcoal">Memory Stream</h2>
          <Button
            onClick={handleTriggerReflection}
            loading={reflectMutation.isPending}
            disabled={reflectMutation.isPending}
          >
            Trigger Reflection
          </Button>
        </div>
      </Card>

      {/* Reflections Section */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">Reflections</h2>
          {reflections.length === 0 ? (
            <div className="text-center py-8">
              <p className="font-sans text-charcoal-light">
                No reflections yet. Trigger one using the button above.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {reflections.map((reflection, index) => (
                <div
                  key={index}
                  className="border-l-4 border-olive-light pl-4 space-y-3"
                >
                  {/* Question */}
                  <p className="font-sans text-sm italic text-charcoal-light">
                    {reflection.question}
                  </p>

                  {/* Evidence IDs */}
                  {reflection.evidenceIds.length > 0 && (
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-sans text-xs text-charcoal-light">
                        Evidence:
                      </span>
                      {reflection.evidenceIds.map((id) => (
                        <span
                          key={id}
                          className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-sans font-medium bg-marble-dark/20 text-charcoal"
                        >
                          {id}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Insight */}
                  <div className="bg-olive-light/30 rounded-lg px-4 py-3">
                    <p className="font-sans text-sm text-charcoal leading-relaxed whitespace-pre-wrap">
                      {reflection.insight}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* Memory Timeline */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">
            Memory Entries (Last 50)
          </h2>
          {memoryEntries.length === 0 ? (
            <div className="text-center py-8">
              <p className="font-sans text-charcoal-light">
                This agent has no memories yet. Start a discussion to create memories.
              </p>
            </div>
          ) : (
            <MemoryTimeline entries={memoryEntries} />
          )}
        </div>
      </Card>
    </div>
  )
}

export default AgentMemory
