import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { createDiscussion } from '../api/discussions'
import AgentSelector from '../components/discussions/AgentSelector'
import Card from '../components/ui/Card'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'

function DiscussionNew() {
  const navigate = useNavigate()
  const [topic, setTopic] = useState('')
  const [selectedAgentIds, setSelectedAgentIds] = useState<string[]>([])
  const [rounds, setRounds] = useState(5)
  const [errors, setErrors] = useState<{ topic?: string; agents?: string }>({})

  const mutation = useMutation({
    mutationFn: () => createDiscussion(topic, selectedAgentIds, rounds),
    onSuccess: (data) => {
      navigate(`/discussions/${data.id}`)
    },
    onError: (error: Error) => {
      console.error('Failed to create discussion:', error)
    },
  })

  const validate = () => {
    const newErrors: { topic?: string; agents?: string } = {}

    if (!topic.trim()) {
      newErrors.topic = 'Topic is required'
    }

    if (selectedAgentIds.length === 0) {
      newErrors.agents = 'Please select at least one agent'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (validate()) {
      mutation.mutate()
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl text-charcoal">
          New Discussion
        </h1>
        <Button variant="secondary" onClick={() => navigate('/discussions')}>
          Cancel
        </Button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Topic Input */}
        <Card>
          <div className="space-y-4">
            <Input
              label="Discussion Topic"
              placeholder="What should we discuss?"
              value={topic}
              onChange={(e) => {
                setTopic(e.target.value)
                if (errors.topic) {
                  setErrors({ ...errors, topic: undefined })
                }
              }}
              error={errors.topic}
              required
            />
          </div>
        </Card>

        {/* Agent Selector */}
        <Card>
          <AgentSelector
            selectedIds={selectedAgentIds}
            onChange={(ids) => {
              setSelectedAgentIds(ids)
              if (errors.agents) {
                setErrors({ ...errors, agents: undefined })
              }
            }}
          />
          {errors.agents && (
            <p className="mt-3 text-sm text-terracotta font-sans">
              {errors.agents}
            </p>
          )}
        </Card>

        {/* Rounds Input */}
        <Card>
          <div className="space-y-2">
            <label className="block font-display text-sm font-medium text-charcoal">
              Initial Rounds
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={rounds}
              onChange={(e) => setRounds(parseInt(e.target.value, 10))}
              className="w-full px-4 py-2 bg-parchment border border-charcoal-light rounded transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gold focus:border-gold"
            />
            <p className="text-sm text-charcoal-light font-sans">
              Number of rounds to run before your first turn
            </p>
          </div>
        </Card>

        {/* Submit Button */}
        <div className="flex justify-end">
          <Button
            type="submit"
            size="lg"
            loading={mutation.isPending}
            disabled={mutation.isPending}
          >
            Start Discussion
          </Button>
        </div>

        {/* Error Message */}
        {mutation.isError && (
          <Card className="border-terracotta bg-terracotta/5">
            <p className="text-sm text-terracotta font-sans">
              Failed to create discussion. Please try again.
            </p>
          </Card>
        )}
      </form>
    </div>
  )
}

export default DiscussionNew
