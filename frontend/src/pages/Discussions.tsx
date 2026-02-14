import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchDiscussions } from '../api/discussions'
import DiscussionCard from '../components/discussions/DiscussionCard'
import Button from '../components/ui/Button'
import Skeleton from '../components/ui/Skeleton'
import Card from '../components/ui/Card'
import { useToast } from '../hooks/useToast'
import { useEffect } from 'react'

function Discussions() {
  const navigate = useNavigate()
  const { showToast } = useToast()

  const { data: discussions, isLoading, error } = useQuery({
    queryKey: ['discussions'],
    queryFn: fetchDiscussions,
  })

  useEffect(() => {
    if (error) {
      showToast('Unable to load discussions', 'error')
    }
  }, [error, showToast])

  // Sort by creation date (newest first)
  const sortedDiscussions = discussions
    ? [...discussions].sort(
        (a, b) =>
          new Date(b.created).getTime() - new Date(a.created).getTime()
      )
    : []

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl text-charcoal">Discussions</h1>
        <Button onClick={() => navigate('/discussions/new')}>
          Start New Discussion
        </Button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i}>
              <div className="space-y-3">
                <Skeleton variant="title" className="w-3/4" />
                <div className="flex gap-4">
                  <Skeleton variant="text" className="w-24" />
                  <Skeleton variant="text" className="w-24" />
                  <Skeleton variant="text" className="w-32" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : sortedDiscussions.length > 0 ? (
        <div className="grid grid-cols-1 gap-4">
          {sortedDiscussions.map((discussion) => (
            <DiscussionCard key={discussion.id} discussion={discussion} />
          ))}
        </div>
      ) : (
        <Card>
          <div className="text-center py-12 space-y-4">
            <p className="font-sans text-lg text-charcoal-light">
              No discussions yet. Start a conversation!
            </p>
            <div className="pt-4">
              <Button onClick={() => navigate('/discussions/new')}>
                Start Discussion
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default Discussions
