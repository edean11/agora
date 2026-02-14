import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchPersona } from '../api/personas'
import { fetchMemory, fetchReflections, triggerReflection } from '../api/agents'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'
import AgentAvatar from '../components/discussions/AgentAvatar'
import MemoryTimeline from '../components/agents/MemoryTimeline'

function AgentMemory() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: persona, isLoading: personaLoading } = useQuery({
    queryKey: ['persona', id],
    queryFn: () => fetchPersona(id!),
    enabled: !!id,
  })

  const { data: memoryEntries = [], isLoading: memoryLoading } = useQuery({
    queryKey: ['memory', id],
    queryFn: () => fetchMemory(id!, 50),
    enabled: !!id,
  })

  const { data: reflectionsData, isLoading: reflectionsLoading } = useQuery({
    queryKey: ['reflections', id],
    queryFn: () => fetchReflections(id!),
    enabled: !!id,
  })

  const reflectMutation = useMutation({
    mutationFn: () => triggerReflection(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memory', id] })
      queryClient.invalidateQueries({ queryKey: ['reflections', id] })
    },
  })

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
      <div className="py-12">
        <Spinner size="lg" text="Loading memory..." />
      </div>
    )
  }

  if (!persona) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <div className="text-center py-12">
            <p className="font-sans text-lg text-charcoal-light">
              Agent not found
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

      {/* Reflection Success Message */}
      {reflectMutation.isSuccess && (
        <div className="bg-olive-light border border-olive/30 rounded-lg px-4 py-3">
          <p className="font-sans text-sm text-charcoal">
            Reflection completed successfully. New insights have been generated.
          </p>
        </div>
      )}

      {/* Reflection Error Message */}
      {reflectMutation.isError && (
        <div className="bg-terracotta/10 border border-terracotta/30 rounded-lg px-4 py-3">
          <p className="font-sans text-sm text-charcoal">
            Failed to trigger reflection. Please try again.
          </p>
        </div>
      )}

      {/* Reflections Section */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">Reflections</h2>
          {reflections.length === 0 ? (
            <div className="text-center py-8">
              <p className="font-sans text-charcoal-light">
                No reflections yet. Trigger one above.
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
          <MemoryTimeline entries={memoryEntries} />
        </div>
      </Card>
    </div>
  )
}

export default AgentMemory
