import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchPersona, deletePersona } from '../api/personas'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import Modal from '../components/ui/Modal'
import Skeleton from '../components/ui/Skeleton'
import { useToast } from '../hooks/useToast'

function PersonaDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showToast } = useToast()
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const { data: persona, isLoading, error } = useQuery({
    queryKey: ['persona', id],
    queryFn: () => fetchPersona(id!),
    enabled: !!id,
  })

  const deleteMutation = useMutation({
    mutationFn: () => deletePersona(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['personas'] })
      showToast('Persona deleted successfully', 'success')
      navigate('/personas')
    },
    onError: () => {
      showToast('Failed to delete persona', 'error')
    },
  })

  useEffect(() => {
    if (error) {
      showToast('Unable to load persona', 'error')
    }
  }, [error, showToast])

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-8">
        <Card>
          <div className="space-y-4">
            <Skeleton variant="title" className="w-1/2" />
            <Skeleton variant="text" className="w-24" />
            <Skeleton variant="text" className="w-full" />
            <Skeleton variant="text" className="w-3/4" />
          </div>
        </Card>
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <div className="space-y-4">
              <Skeleton variant="title" className="w-1/3" />
              <Skeleton variant="text" className="w-full" />
              <Skeleton variant="text" className="w-2/3" />
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
            <h1 className="font-serif text-2xl text-gold">Persona not found</h1>
            <p className="font-sans text-charcoal-light">
              The persona you're looking for doesn't exist or may have been deleted.
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

  const trueColorsMap: Record<string, string> = {
    Orange: '#E87D3E',
    Gold: '#C9A84C',
    Green: '#4A5D3A',
    Blue: '#4A7AB5',
  }

  const getLevelWidth = (level: string) => {
    switch (level) {
      case 'Low':
        return '20%'
      case 'Medium':
        return '50%'
      case 'High':
        return '100%'
      default:
        return '50%'
    }
  }

  const getMoralFoundationWidth = (score: number) => {
    return `${(score / 10) * 100}%`
  }

  const bigFiveTraits = [
    { label: 'Openness', key: 'openness' },
    { label: 'Conscientiousness', key: 'conscientiousness' },
    { label: 'Extraversion', key: 'extraversion' },
    { label: 'Agreeableness', key: 'agreeableness' },
    { label: 'Neuroticism', key: 'neuroticism' },
  ] as const

  const moralFoundations = [
    { label: 'Care', key: 'care' },
    { label: 'Fairness', key: 'fairness' },
    { label: 'Loyalty', key: 'loyalty' },
    { label: 'Authority', key: 'authority' },
    { label: 'Sanctity', key: 'sanctity' },
    { label: 'Liberty', key: 'liberty' },
  ] as const

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <Card>
        <div className="space-y-4">
          <div>
            <h1 className="font-display text-3xl text-charcoal">
              {persona.name}
            </h1>
            <p className="font-sans text-sm text-charcoal-light mt-1">
              Age {persona.age}
            </p>
          </div>
          <p className="font-sans text-base text-charcoal leading-relaxed">
            {persona.background}
          </p>
        </div>
      </Card>

      {/* Big Five Personality */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">
            Big Five Personality
          </h2>
          <div className="space-y-4">
            {bigFiveTraits.map((trait) => {
              const traitData = persona[trait.key]
              return (
                <div key={trait.key} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-sans font-medium text-charcoal">
                      {trait.label}
                    </span>
                    <span className="font-sans text-sm text-charcoal-light">
                      {traitData.level}
                    </span>
                  </div>
                  <div className="h-2 bg-marble-dark/30 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-olive rounded-full transition-all duration-300"
                      style={{ width: getLevelWidth(traitData.level) }}
                    />
                  </div>
                  <p className="font-sans text-sm text-charcoal-light">
                    {traitData.description}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      </Card>

      {/* True Colors */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">True Colors</h2>
          <div className="space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="font-sans font-medium text-charcoal">
                  Primary:
                </span>
                <span
                  className="inline-block px-3 py-1 rounded-full font-sans text-sm font-medium text-parchment"
                  style={{
                    backgroundColor:
                      trueColorsMap[persona.true_colors_primary] || '#4A5D3A',
                  }}
                >
                  {persona.true_colors_primary}
                </span>
              </div>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.true_colors_primary_description}
              </p>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="font-sans font-medium text-charcoal">
                  Secondary:
                </span>
                <span
                  className="inline-block px-3 py-1 rounded-full font-sans text-sm font-medium text-parchment"
                  style={{
                    backgroundColor:
                      trueColorsMap[persona.true_colors_secondary] || '#4A5D3A',
                  }}
                >
                  {persona.true_colors_secondary}
                </span>
              </div>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.true_colors_secondary_description}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Moral Foundations */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">
            Moral Foundations
          </h2>
          <div className="space-y-4">
            {moralFoundations.map((foundation) => {
              const score = persona[foundation.key]
              return (
                <div key={foundation.key} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-sans font-medium text-charcoal">
                      {foundation.label}
                    </span>
                    <span className="font-sans text-sm text-charcoal-light">
                      {score}/10
                    </span>
                  </div>
                  <div className="h-2 bg-marble-dark/30 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gold rounded-full transition-all duration-300"
                      style={{ width: getMoralFoundationWidth(score) }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </Card>

      {/* Cognitive Style */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">
            Cognitive Style
          </h2>
          <div className="space-y-4">
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Reasoning: {persona.reasoning}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.reasoning_description}
              </p>
            </div>
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Thinking Mode: {persona.thinking_mode}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.thinking_mode_description}
              </p>
            </div>
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Argument Style: {persona.argument_style}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.argument_style_description}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Communication Style */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">
            Communication Style
          </h2>
          <div className="space-y-4">
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Pace: {persona.pace}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.pace_description}
              </p>
            </div>
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Formality: {persona.formality}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.formality_description}
              </p>
            </div>
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Directness: {persona.directness}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.directness_description}
              </p>
            </div>
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Emotionality: {persona.emotionality}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.emotionality_description}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Discussion Tendencies */}
      <Card>
        <div className="space-y-6">
          <h2 className="font-display text-2xl text-charcoal">
            Discussion Tendencies
          </h2>
          <div className="space-y-4">
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Conflict Approach: {persona.conflict_approach}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.conflict_approach_description}
              </p>
            </div>
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Consensus: {persona.consensus}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.consensus_description}
              </p>
            </div>
            <div>
              <p className="font-sans font-medium text-charcoal mb-1">
                Focus: {persona.focus}
              </p>
              <p className="font-sans text-sm text-charcoal-light">
                {persona.focus_description}
              </p>
            </div>
            <div className="pt-4 space-y-3 border-t border-marble-dark/30">
              <div>
                <p className="font-sans font-medium text-charcoal mb-1">
                  Strengths
                </p>
                <p className="font-sans text-sm text-charcoal-light">
                  {persona.strengths}
                </p>
              </div>
              <div>
                <p className="font-sans font-medium text-charcoal mb-1">
                  Blind Spots
                </p>
                <p className="font-sans text-sm text-charcoal-light">
                  {persona.blind_spots}
                </p>
              </div>
              <div>
                <p className="font-sans font-medium text-charcoal mb-1">
                  Trigger Points
                </p>
                <p className="font-sans text-sm text-charcoal-light">
                  {persona.trigger_points}
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button onClick={() => navigate(`/agents/${id}/ask`)}>
              Ask a Question
            </Button>
            <Button
              variant="secondary"
              onClick={() => navigate(`/agents/${id}/memory`)}
            >
              View Memory
            </Button>
          </div>
          <Button variant="danger" onClick={() => setShowDeleteModal(true)}>
            Delete
          </Button>
        </div>
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Persona"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setShowDeleteModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => deleteMutation.mutate()}
              loading={deleteMutation.isPending}
            >
              Delete
            </Button>
          </>
        }
      >
        <p className="font-sans text-charcoal">
          Are you sure you want to delete{' '}
          <span className="font-medium">{persona.name}</span>? This action
          cannot be undone.
        </p>
      </Modal>
    </div>
  )
}

export default PersonaDetail
