import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchPersona } from '../api/personas'
import { askAgent } from '../api/agents'
import { useHealth } from '../hooks/useHealth'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Spinner from '../components/ui/Spinner'
import Skeleton from '../components/ui/Skeleton'
import AgentAvatar from '../components/discussions/AgentAvatar'
import { useToast } from '../hooks/useToast'

interface QAPair {
  question: string
  response: string
}

function AgentAsk() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { showToast } = useToast()
  const [question, setQuestion] = useState('')
  const [history, setHistory] = useState<QAPair[]>([])

  const { data: persona, isLoading, error } = useQuery({
    queryKey: ['persona', id],
    queryFn: () => fetchPersona(id!),
    enabled: !!id,
  })

  const { data: health } = useHealth()

  const askMutation = useMutation({
    mutationFn: (q: string) => askAgent(id!, q),
    onSuccess: (data, question) => {
      setHistory((prev) => [...prev, { question, response: data.response }])
      setQuestion('')
    },
    onError: () => {
      showToast('Failed to get response. Please try again.', 'error')
    },
  })

  useEffect(() => {
    if (error) {
      showToast('Unable to load agent', 'error')
    }
  }, [error, showToast])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (question.trim() && !askMutation.isPending) {
      askMutation.mutate(question.trim())
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

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
          <Skeleton variant="title" className="w-1/4" />
          <div className="mt-6">
            <Skeleton variant="card" className="h-64" />
          </div>
        </Card>
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

      {/* Chat Area */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">
            Ask a Question
          </h2>

          {/* Ollama down warning */}
          {health && !health.ollama_available && (
            <div className="px-4 py-3 bg-terracotta bg-opacity-20 border border-terracotta rounded">
              <p className="font-sans text-sm text-terracotta">
                <strong>Ollama is not running.</strong> Please start Ollama to
                ask questions.
              </p>
            </div>
          )}

          {/* Chat History */}
          <div className="space-y-4 min-h-[300px] max-h-[600px] overflow-y-auto">
            {history.length === 0 && !askMutation.isPending && (
              <div className="text-center py-12">
                <p className="font-sans text-charcoal-light">
                  Ask {persona.name} anything. They'll respond based on their
                  personality and memories.
                </p>
              </div>
            )}

            {history.map((qa, index) => (
              <div key={index} className="space-y-3">
                {/* User Question - Right aligned */}
                <div className="flex justify-end">
                  <div className="max-w-[80%] bg-charcoal text-parchment rounded-lg px-4 py-3">
                    <p className="font-sans text-sm">{qa.question}</p>
                  </div>
                </div>

                {/* Agent Response - Left aligned with avatar */}
                <div className="flex items-start gap-3">
                  <AgentAvatar name={persona.name} />
                  <div className="max-w-[80%] bg-olive-light border border-olive/30 rounded-lg px-4 py-3">
                    <p className="font-sans text-sm text-charcoal leading-relaxed whitespace-pre-wrap">
                      {qa.response}
                    </p>
                  </div>
                </div>
              </div>
            ))}

            {/* Loading State */}
            {askMutation.isPending && (
              <div className="space-y-3">
                {/* User's pending question */}
                <div className="flex justify-end">
                  <div className="max-w-[80%] bg-charcoal text-parchment rounded-lg px-4 py-3">
                    <p className="font-sans text-sm">{question}</p>
                  </div>
                </div>

                {/* Agent thinking */}
                <div className="flex items-start gap-3">
                  <AgentAvatar name={persona.name} />
                  <div className="max-w-[80%] bg-olive-light border border-olive/30 rounded-lg px-4 py-3">
                    <Spinner size="sm" text="Thinking..." />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <form onSubmit={handleSubmit} className="space-y-3">
            <Input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question..."
              disabled={askMutation.isPending || (health && !health.ollama_available)}
            />
            <div className="flex items-center justify-between">
              <p className="font-sans text-xs text-charcoal-light">
                Press Enter to send
              </p>
              <Button
                type="submit"
                disabled={!question.trim() || askMutation.isPending || (health && !health.ollama_available)}
                loading={askMutation.isPending}
              >
                Send
              </Button>
            </div>
          </form>
        </div>
      </Card>
    </div>
  )
}

export default AgentAsk
