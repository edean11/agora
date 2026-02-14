import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchPersonas } from '../../api/personas'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Spinner from '../ui/Spinner'
import type { PersonaSummary } from '../../api/types'

interface AgentSelectorProps {
  selectedIds: string[]
  onChange: (ids: string[]) => void
}

function AgentSelector({ selectedIds, onChange }: AgentSelectorProps) {
  const { data: personas, isLoading } = useQuery({
    queryKey: ['personas'],
    queryFn: fetchPersonas,
  })

  // Initialize with all selected on first load
  useEffect(() => {
    if (personas && personas.length > 0 && selectedIds.length === 0) {
      onChange(personas.map((p) => p.id))
    }
  }, [personas, selectedIds.length, onChange])

  const toggleAgent = (id: string) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((selectedId) => selectedId !== id))
    } else {
      onChange([...selectedIds, id])
    }
  }

  const selectAll = () => {
    if (personas) {
      onChange(personas.map((p) => p.id))
    }
  }

  const deselectAll = () => {
    onChange([])
  }

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  if (isLoading) {
    return (
      <div className="py-8">
        <Spinner size="md" text="Loading personas..." />
      </div>
    )
  }

  if (!personas || personas.length === 0) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="font-sans text-charcoal-light">
            No personas available. Create some first!
          </p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with controls */}
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg text-charcoal">
          Select Participants
        </h3>
        <div className="flex items-center gap-3">
          <span className="font-sans text-sm text-charcoal-light">
            {selectedIds.length} of {personas.length} selected
          </span>
          <Button size="sm" variant="secondary" onClick={selectAll}>
            Select All
          </Button>
          <Button size="sm" variant="secondary" onClick={deselectAll}>
            Deselect All
          </Button>
        </div>
      </div>

      {/* Grid of mini persona cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {personas.map((persona: PersonaSummary) => {
          const isSelected = selectedIds.includes(persona.id)
          return (
            <Card
              key={persona.id}
              hover
              onClick={() => toggleAgent(persona.id)}
              className={`cursor-pointer transition-all duration-200 ${
                isSelected
                  ? 'border-gold border-2 bg-gold/5'
                  : 'border-marble-dark/30'
              }`}
            >
              <div className="space-y-2">
                {/* Checkbox indicator */}
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    <div
                      className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                        isSelected
                          ? 'bg-gold border-gold'
                          : 'bg-parchment border-charcoal-light'
                      }`}
                    >
                      {isSelected && (
                        <svg
                          className="w-3 h-3 text-charcoal"
                          fill="none"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>

                  {/* Persona info */}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-display text-base text-charcoal truncate">
                      {persona.name}
                    </h4>
                    <p className="font-sans text-xs text-charcoal-light mt-1">
                      Age {persona.age}
                    </p>
                  </div>
                </div>

                {/* Background snippet */}
                <p className="font-sans text-xs text-charcoal-light leading-relaxed">
                  {truncateText(persona.background_brief, 50)}
                </p>
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

export default AgentSelector
