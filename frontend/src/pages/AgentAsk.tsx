import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchPersona } from '../api/personas'
import { askAgent } from '../api/agents'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Spinner from '../components/ui/Spinner'
import AgentAvatar from '../components/discussions/AgentAvatar'

interface QAPair {
  question: string
  response: string
}

function AgentAsk() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [question, setQuestion] = useState('')
  const [history, setHistory] = useState<QAPair[]>([])

  const { data: persona, isLoading } = useQuery({
    queryKey: ['persona', id],
    queryFn: () => fetchPersona(id!),
    enabled: !!id,
  })

  const askMutation = useMutation({
    mutationFn: (q: string) => askAgent(id!, q),
    onSuccess: (data, question) => {
      setHistory((prev) => [...prev, { question, response: data.response }])
      setQuestion('')
    },
  })

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
      <div className="py-12">
        <Spinner size="lg" text="Loading agent..." />
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
              disabled={askMutation.isPending}
            />
            <div className="flex items-center justify-between">
              <p className="font-sans text-xs text-charcoal-light">
                Press Enter to send
              </p>
              <Button
                type="submit"
                disabled={!question.trim() || askMutation.isPending}
                loading={askMutation.isPending}
              >
                Send
              </Button>
            </div>
          </form>

          {/* Error State */}
          {askMutation.isError && (
            <div className="bg-terracotta/10 border border-terracotta/30 rounded-lg px-4 py-3">
              <p className="font-sans text-sm text-charcoal">
                Failed to get response. Please try again.
              </p>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}

export default AgentAsk
