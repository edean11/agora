import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchPersonas } from '../api/personas'
import { fetchDiscussions } from '../api/discussions'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'

function Home() {
  const navigate = useNavigate()

  const { data: personas, isLoading: personasLoading } = useQuery({
    queryKey: ['personas'],
    queryFn: fetchPersonas,
  })

  const { data: discussions, isLoading: discussionsLoading } = useQuery({
    queryKey: ['discussions'],
    queryFn: fetchDiscussions,
  })

  const personaCount = personas?.length ?? 0
  const discussionCount = discussions?.length ?? 0
  const recentDiscussions = discussions?.slice(0, 5) ?? []

  const isLoading = personasLoading || discussionsLoading

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-olive text-parchment'
      case 'completed':
        return 'bg-charcoal-light text-parchment'
      case 'pending':
        return 'bg-gold text-charcoal'
      default:
        return 'bg-marble-dark text-charcoal'
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-12">
      {/* Hero Section */}
      <section className="text-center py-8 space-y-4">
        <h1 className="font-serif text-4xl md:text-5xl text-charcoal">
          Welcome to the Agora
        </h1>
        <p className="font-serif italic text-xl text-charcoal-light">
          Where great minds convene
        </p>
        {/* Decorative laurel wreath or thin gold line */}
        <div className="flex justify-center mt-6">
          <svg
            width="120"
            height="40"
            viewBox="0 0 120 40"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="text-gold"
          >
            {/* Simple laurel wreath decoration */}
            <path
              d="M10 20 Q20 10, 30 20 T50 20 T70 20 T90 20 T110 20"
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
            />
            <circle cx="20" cy="15" r="2" fill="currentColor" />
            <circle cx="40" cy="15" r="2" fill="currentColor" />
            <circle cx="60" cy="20" r="2" fill="currentColor" />
            <circle cx="80" cy="15" r="2" fill="currentColor" />
            <circle cx="100" cy="15" r="2" fill="currentColor" />
          </svg>
        </div>
      </section>

      {/* Quick Stats Row */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <div className="text-center space-y-2">
            <p className="font-sans text-sm uppercase tracking-wide text-charcoal-light">
              Personas
            </p>
            <p className="font-serif text-5xl font-bold text-gold">
              {personasLoading ? '—' : personaCount}
            </p>
          </div>
        </Card>
        <Card>
          <div className="text-center space-y-2">
            <p className="font-sans text-sm uppercase tracking-wide text-charcoal-light">
              Discussions
            </p>
            <p className="font-serif text-5xl font-bold text-gold">
              {discussionsLoading ? '—' : discussionCount}
            </p>
          </div>
        </Card>
      </section>

      {/* Recent Discussions */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="font-serif text-2xl text-charcoal">Recent Discussions</h2>
          {discussions && discussions.length > 5 && (
            <button
              onClick={() => navigate('/discussions')}
              className="font-sans text-sm text-gold hover:text-gold-dark transition-colors"
            >
              View All →
            </button>
          )}
        </div>

        {isLoading ? (
          <div className="py-12">
            <Spinner size="lg" text="Loading discussions..." />
          </div>
        ) : recentDiscussions.length === 0 ? (
          <Card>
            <div className="text-center py-8 space-y-4">
              <p className="font-sans text-charcoal-light">
                No discussions yet. Start one!
              </p>
              <Button onClick={() => navigate('/discussions/new')}>
                Start Discussion
              </Button>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {recentDiscussions.map((discussion) => (
              <Card
                key={discussion.id}
                hover
                onClick={() => navigate(`/discussions/${discussion.id}`)}
                className="cursor-pointer"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <h3 className="font-serif text-lg text-charcoal">
                      {discussion.topic}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-charcoal-light">
                      <span className="font-sans">
                        {discussion.participant_count} participant
                        {discussion.participant_count !== 1 ? 's' : ''}
                      </span>
                      <span className="font-sans">
                        {discussion.message_count} message
                        {discussion.message_count !== 1 ? 's' : ''}
                      </span>
                      <span className="font-sans">
                        {formatDate(discussion.created)}
                      </span>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-sans uppercase tracking-wide ${getStatusColor(discussion.status)}`}
                  >
                    {discussion.status}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Quick Actions */}
      <section className="flex flex-col sm:flex-row items-center justify-center gap-4 pb-8">
        <Button size="lg" onClick={() => navigate('/discussions/new')}>
          Start Discussion
        </Button>
        <Button
          size="lg"
          variant="secondary"
          onClick={() => navigate('/personas')}
        >
          Browse Personas
        </Button>
      </section>
    </div>
  )
}

export default Home
