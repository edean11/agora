import { useNavigate } from 'react-router-dom'
import Card from '../ui/Card'
import Badge from '../ui/Badge'
import type { DiscussionSummary } from '../../api/types'

interface DiscussionCardProps {
  discussion: DiscussionSummary
}

function DiscussionCard({ discussion }: DiscussionCardProps) {
  const navigate = useNavigate()

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const getStatusVariant = (
    status: string
  ): 'active' | 'completed' | 'paused' => {
    const normalized = status.toLowerCase()
    if (normalized === 'active') return 'active'
    if (normalized === 'completed') return 'completed'
    return 'paused'
  }

  return (
    <Card
      hover
      onClick={() => navigate(`/discussions/${discussion.id}`)}
      className="cursor-pointer"
    >
      <div className="space-y-3">
        {/* Topic and Status */}
        <div className="flex items-start justify-between gap-4">
          <h3 className="font-display text-lg text-charcoal flex-1">
            {discussion.topic}
          </h3>
          <Badge variant={getStatusVariant(discussion.status)}>
            {discussion.status}
          </Badge>
        </div>

        {/* Metadata */}
        <div className="flex items-center gap-4 text-sm text-charcoal-light font-sans">
          <span>
            {discussion.participant_count} agent
            {discussion.participant_count !== 1 ? 's' : ''}
          </span>
          <span>
            {discussion.message_count} message
            {discussion.message_count !== 1 ? 's' : ''}
          </span>
          <span>{formatDate(discussion.created)}</span>
        </div>
      </div>
    </Card>
  )
}

export default DiscussionCard
