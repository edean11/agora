import { useState } from 'react'
import Badge from '../ui/Badge'
import type { MemoryEntry } from '../../api/types'

interface MemoryTimelineProps {
  entries: MemoryEntry[]
}

function MemoryTimeline({ entries }: MemoryTimelineProps) {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  const toggleExpanded = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getTypeBadgeVariant = (
    type: string
  ): 'observation' | 'own_statement' | 'reflection' | 'user_interaction' => {
    switch (type) {
      case 'observation':
        return 'observation'
      case 'own_statement':
        return 'own_statement'
      case 'reflection':
        return 'reflection'
      case 'user_interaction':
        return 'user_interaction'
      default:
        return 'observation'
    }
  }

  const truncateContent = (content: string, limit = 200) => {
    if (content.length <= limit) return content
    return content.substring(0, limit) + '...'
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="font-sans text-charcoal-light">
          No memory entries yet.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {entries.map((entry) => {
        const isExpanded = expandedIds.has(entry.id)
        const needsTruncation = entry.content.length > 200

        return (
          <div
            key={entry.id}
            className="bg-marble-light border border-marble-dark/30 rounded-lg p-4 space-y-3"
          >
            {/* Header with timestamp and type */}
            <div className="flex items-center justify-between">
              <span className="font-sans text-sm text-charcoal-light">
                {formatTimestamp(entry.timestamp)}
              </span>
              <Badge variant={getTypeBadgeVariant(entry.type)}>
                {entry.type.replace('_', ' ')}
              </Badge>
            </div>

            {/* Importance bar */}
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-sans text-xs text-charcoal-light">
                  Importance
                </span>
                <span className="font-sans text-xs font-medium text-charcoal">
                  {entry.importance}/10
                </span>
              </div>
              <div className="h-1.5 bg-marble-dark/30 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gold rounded-full transition-all duration-300"
                  style={{ width: `${(entry.importance / 10) * 100}%` }}
                />
              </div>
            </div>

            {/* Content */}
            <div className="space-y-2">
              <p className="font-sans text-sm text-charcoal leading-relaxed">
                {isExpanded ? entry.content : truncateContent(entry.content)}
              </p>
              {needsTruncation && (
                <button
                  onClick={() => toggleExpanded(entry.id)}
                  className="font-sans text-xs text-gold hover:text-gold/80 transition-colors"
                >
                  {isExpanded ? 'Show less' : 'Show more'}
                </button>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default MemoryTimeline
