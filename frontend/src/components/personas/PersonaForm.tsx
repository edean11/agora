import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Input from '../ui/Input'
import Textarea from '../ui/Textarea'
import Select from '../ui/Select'
import Slider from '../ui/Slider'
import Button from '../ui/Button'
import { createPersona, type PersonaCreateData } from '../../api/personas'

interface FormData extends PersonaCreateData {
  openness_level: string
  openness_description: string
  conscientiousness_level: string
  conscientiousness_description: string
  extraversion_level: string
  extraversion_description: string
  agreeableness_level: string
  agreeableness_description: string
  neuroticism_level: string
  neuroticism_description: string
  true_colors_primary_description: string
  true_colors_secondary_description: string
  reasoning_description: string
  thinking_mode_description: string
  argument_style_description: string
  pace_description: string
  formality_description: string
  directness_description: string
  emotionality_description: string
  conflict_approach_description: string
  consensus_description: string
  focus_description: string
  strengths: string
  blind_spots: string
  trigger_points: string
}

const traitLevelOptions = [
  { value: '', label: 'Select level' },
  { value: 'Low', label: 'Low' },
  { value: 'Medium', label: 'Medium' },
  { value: 'High', label: 'High' },
]

const trueColorsOptions = [
  { value: '', label: 'Select color' },
  { value: 'Orange', label: 'Orange' },
  { value: 'Gold', label: 'Gold' },
  { value: 'Green', label: 'Green' },
  { value: 'Blue', label: 'Blue' },
]

const reasoningOptions = [
  { value: '', label: 'Select reasoning style' },
  { value: 'Analytical', label: 'Analytical' },
  { value: 'Empirical', label: 'Empirical' },
  { value: 'Dialectical', label: 'Dialectical' },
  { value: 'Holistic', label: 'Holistic' },
  { value: 'Intuitive', label: 'Intuitive' },
]

const thinkingModeOptions = [
  { value: '', label: 'Select thinking mode' },
  { value: 'Convergent', label: 'Convergent' },
  { value: 'Divergent', label: 'Divergent' },
]

const argumentStyleOptions = [
  { value: '', label: 'Select argument style' },
  { value: 'Thesis-first', label: 'Thesis-first' },
  { value: 'Evidence-first', label: 'Evidence-first' },
  { value: 'Story-first', label: 'Story-first' },
]

const paceOptions = [
  { value: '', label: 'Select pace' },
  { value: 'Slow', label: 'Slow' },
  { value: 'Measured', label: 'Measured' },
  { value: 'Rapid', label: 'Rapid' },
]

const formalityOptions = [
  { value: '', label: 'Select formality' },
  { value: 'Casual', label: 'Casual' },
  { value: 'Professional', label: 'Professional' },
  { value: 'Academic', label: 'Academic' },
]

const directnessOptions = [
  { value: '', label: 'Select directness' },
  { value: 'Diplomatic', label: 'Diplomatic' },
  { value: 'Balanced', label: 'Balanced' },
  { value: 'Blunt', label: 'Blunt' },
]

const emotionalityOptions = [
  { value: '', label: 'Select emotionality' },
  { value: 'Detached', label: 'Detached' },
  { value: 'Neutral', label: 'Neutral' },
  { value: 'Expressive', label: 'Expressive' },
]

const conflictApproachOptions = [
  { value: '', label: 'Select conflict approach' },
  { value: 'Challenger', label: 'Challenger' },
  { value: 'Synthesizer', label: 'Synthesizer' },
  { value: 'Harmonizer', label: 'Harmonizer' },
]

const consensusOptions = [
  { value: '', label: 'Select consensus style' },
  { value: 'Contrarian', label: 'Contrarian' },
  { value: 'Pragmatist', label: 'Pragmatist' },
  { value: 'Consensus-seeker', label: 'Consensus-seeker' },
]

const focusOptions = [
  { value: '', label: 'Select focus' },
  { value: 'Abstract', label: 'Abstract' },
  { value: 'Concrete', label: 'Concrete' },
  { value: 'Both', label: 'Both' },
]

function PersonaForm() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState<FormData>({
    name: '',
    age: 30,
    background: '',
    openness_level: '',
    openness_description: '',
    conscientiousness_level: '',
    conscientiousness_description: '',
    extraversion_level: '',
    extraversion_description: '',
    agreeableness_level: '',
    agreeableness_description: '',
    neuroticism_level: '',
    neuroticism_description: '',
    true_colors_primary: '',
    true_colors_primary_description: '',
    true_colors_secondary: '',
    true_colors_secondary_description: '',
    care: 5,
    fairness: 5,
    loyalty: 5,
    authority: 5,
    sanctity: 5,
    liberty: 5,
    reasoning: '',
    reasoning_description: '',
    thinking_mode: '',
    thinking_mode_description: '',
    argument_style: '',
    argument_style_description: '',
    pace: '',
    pace_description: '',
    formality: '',
    formality_description: '',
    directness: '',
    directness_description: '',
    emotionality: '',
    emotionality_description: '',
    conflict_approach: '',
    conflict_approach_description: '',
    consensus: '',
    consensus_description: '',
    focus: '',
    focus_description: '',
    strengths: '',
    blind_spots: '',
    trigger_points: '',
  })

  const handleInputChange = (
    field: keyof FormData,
    value: string | number
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const nextStep = () => {
    setCurrentStep((prev) => Math.min(prev + 1, 7))
  }

  const prevStep = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1))
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    setError('')

    try {
      // Build payload - format Big Five traits as "level: description"
      const payload: PersonaCreateData = {
        name: formData.name,
        age: formData.age,
        background: formData.background,
        openness: formData.openness_level
          ? `${formData.openness_level}${formData.openness_description ? ': ' + formData.openness_description : ''}`
          : undefined,
        conscientiousness: formData.conscientiousness_level
          ? `${formData.conscientiousness_level}${formData.conscientiousness_description ? ': ' + formData.conscientiousness_description : ''}`
          : undefined,
        extraversion: formData.extraversion_level
          ? `${formData.extraversion_level}${formData.extraversion_description ? ': ' + formData.extraversion_description : ''}`
          : undefined,
        agreeableness: formData.agreeableness_level
          ? `${formData.agreeableness_level}${formData.agreeableness_description ? ': ' + formData.agreeableness_description : ''}`
          : undefined,
        neuroticism: formData.neuroticism_level
          ? `${formData.neuroticism_level}${formData.neuroticism_description ? ': ' + formData.neuroticism_description : ''}`
          : undefined,
        true_colors_primary: formData.true_colors_primary || undefined,
        true_colors_secondary: formData.true_colors_secondary || undefined,
        care: formData.care,
        fairness: formData.fairness,
        loyalty: formData.loyalty,
        authority: formData.authority,
        sanctity: formData.sanctity,
        liberty: formData.liberty,
        reasoning: formData.reasoning || undefined,
        thinking_mode: formData.thinking_mode || undefined,
        argument_style: formData.argument_style || undefined,
        pace: formData.pace || undefined,
        formality: formData.formality || undefined,
        directness: formData.directness || undefined,
        emotionality: formData.emotionality || undefined,
        conflict_approach: formData.conflict_approach || undefined,
        consensus: formData.consensus || undefined,
        focus: formData.focus || undefined,
      }

      const result = await createPersona(payload)
      navigate(`/personas/${result.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create persona')
      setIsSubmitting(false)
    }
  }

  const validateStep = () => {
    if (currentStep === 1) {
      return formData.name.trim() !== '' && formData.age > 0
    }
    return true
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Progress indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4, 5, 6, 7].map((step) => (
            <div
              key={step}
              className={`flex items-center justify-center w-10 h-10 rounded-full font-display font-medium transition-all duration-200 ${
                step === currentStep
                  ? 'bg-gold text-charcoal scale-110'
                  : step < currentStep
                    ? 'bg-olive text-parchment'
                    : 'bg-charcoal-light/20 text-charcoal-light'
              }`}
            >
              {step}
            </div>
          ))}
        </div>
        <div className="mt-2 text-center font-sans text-sm text-charcoal-light">
          Step {currentStep} of 7
        </div>
      </div>

      {/* Step content */}
      <div className="bg-parchment/50 border border-charcoal-light/20 rounded-lg p-6">
        {currentStep === 1 && (
          <div className="space-y-4">
            <h2 className="font-display text-2xl text-charcoal mb-6">
              Identity
            </h2>
            <Input
              label="Name *"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Enter persona name"
            />
            <Input
              label="Age *"
              type="number"
              value={formData.age}
              onChange={(e) =>
                handleInputChange('age', parseInt(e.target.value) || 0)
              }
              min={1}
              max={120}
            />
            <Textarea
              label="Background"
              value={formData.background}
              onChange={(e) => handleInputChange('background', e.target.value)}
              placeholder="Describe the persona's background, history, and context"
              rows={6}
            />
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-6">
            <h2 className="font-display text-2xl text-charcoal mb-6">
              Big Five Personality Traits
            </h2>

            <div className="space-y-4">
              <h3 className="font-display text-lg text-charcoal">Openness</h3>
              <p className="font-sans text-sm text-charcoal-light -mt-2">
                Imagination, curiosity, creativity
              </p>
              <Select
                options={traitLevelOptions}
                value={formData.openness_level}
                onChange={(e) =>
                  handleInputChange('openness_level', e.target.value)
                }
              />
              <Textarea
                placeholder="Describe how this trait manifests"
                value={formData.openness_description}
                onChange={(e) =>
                  handleInputChange('openness_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <h3 className="font-display text-lg text-charcoal">
                Conscientiousness
              </h3>
              <p className="font-sans text-sm text-charcoal-light -mt-2">
                Organization, discipline, reliability
              </p>
              <Select
                options={traitLevelOptions}
                value={formData.conscientiousness_level}
                onChange={(e) =>
                  handleInputChange('conscientiousness_level', e.target.value)
                }
              />
              <Textarea
                placeholder="Describe how this trait manifests"
                value={formData.conscientiousness_description}
                onChange={(e) =>
                  handleInputChange(
                    'conscientiousness_description',
                    e.target.value
                  )
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <h3 className="font-display text-lg text-charcoal">
                Extraversion
              </h3>
              <p className="font-sans text-sm text-charcoal-light -mt-2">
                Sociability, assertiveness, energy
              </p>
              <Select
                options={traitLevelOptions}
                value={formData.extraversion_level}
                onChange={(e) =>
                  handleInputChange('extraversion_level', e.target.value)
                }
              />
              <Textarea
                placeholder="Describe how this trait manifests"
                value={formData.extraversion_description}
                onChange={(e) =>
                  handleInputChange('extraversion_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <h3 className="font-display text-lg text-charcoal">
                Agreeableness
              </h3>
              <p className="font-sans text-sm text-charcoal-light -mt-2">
                Compassion, cooperation, trust
              </p>
              <Select
                options={traitLevelOptions}
                value={formData.agreeableness_level}
                onChange={(e) =>
                  handleInputChange('agreeableness_level', e.target.value)
                }
              />
              <Textarea
                placeholder="Describe how this trait manifests"
                value={formData.agreeableness_description}
                onChange={(e) =>
                  handleInputChange('agreeableness_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <h3 className="font-display text-lg text-charcoal">
                Neuroticism
              </h3>
              <p className="font-sans text-sm text-charcoal-light -mt-2">
                Emotional stability, anxiety, mood
              </p>
              <Select
                options={traitLevelOptions}
                value={formData.neuroticism_level}
                onChange={(e) =>
                  handleInputChange('neuroticism_level', e.target.value)
                }
              />
              <Textarea
                placeholder="Describe how this trait manifests"
                value={formData.neuroticism_description}
                onChange={(e) =>
                  handleInputChange('neuroticism_description', e.target.value)
                }
                rows={2}
              />
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-6">
            <h2 className="font-display text-2xl text-charcoal mb-6">
              True Colors
            </h2>

            <div className="space-y-4">
              <h3 className="font-display text-lg text-charcoal">
                Primary Color
              </h3>
              <Select
                options={trueColorsOptions}
                value={formData.true_colors_primary}
                onChange={(e) =>
                  handleInputChange('true_colors_primary', e.target.value)
                }
              />
              <Textarea
                placeholder="Describe how this color manifests"
                value={formData.true_colors_primary_description}
                onChange={(e) =>
                  handleInputChange(
                    'true_colors_primary_description',
                    e.target.value
                  )
                }
                rows={3}
              />
            </div>

            <div className="space-y-4">
              <h3 className="font-display text-lg text-charcoal">
                Secondary Color
              </h3>
              <Select
                options={trueColorsOptions}
                value={formData.true_colors_secondary}
                onChange={(e) =>
                  handleInputChange('true_colors_secondary', e.target.value)
                }
              />
              <Textarea
                placeholder="Describe how this color manifests"
                value={formData.true_colors_secondary_description}
                onChange={(e) =>
                  handleInputChange(
                    'true_colors_secondary_description',
                    e.target.value
                  )
                }
                rows={3}
              />
            </div>
          </div>
        )}

        {currentStep === 4 && (
          <div className="space-y-6">
            <h2 className="font-display text-2xl text-charcoal mb-6">
              Moral Foundations
            </h2>
            <p className="font-sans text-sm text-charcoal-light -mt-4 mb-6">
              Rate each moral foundation from 1 (low) to 10 (high)
            </p>

            <Slider
              label="Care"
              min={1}
              max={10}
              value={formData.care}
              onChange={(e) =>
                handleInputChange('care', parseInt(e.target.value))
              }
            />

            <Slider
              label="Fairness"
              min={1}
              max={10}
              value={formData.fairness}
              onChange={(e) =>
                handleInputChange('fairness', parseInt(e.target.value))
              }
            />

            <Slider
              label="Loyalty"
              min={1}
              max={10}
              value={formData.loyalty}
              onChange={(e) =>
                handleInputChange('loyalty', parseInt(e.target.value))
              }
            />

            <Slider
              label="Authority"
              min={1}
              max={10}
              value={formData.authority}
              onChange={(e) =>
                handleInputChange('authority', parseInt(e.target.value))
              }
            />

            <Slider
              label="Sanctity"
              min={1}
              max={10}
              value={formData.sanctity}
              onChange={(e) =>
                handleInputChange('sanctity', parseInt(e.target.value))
              }
            />

            <Slider
              label="Liberty"
              min={1}
              max={10}
              value={formData.liberty}
              onChange={(e) =>
                handleInputChange('liberty', parseInt(e.target.value))
              }
            />
          </div>
        )}

        {currentStep === 5 && (
          <div className="space-y-6">
            <h2 className="font-display text-2xl text-charcoal mb-6">
              Cognitive Style
            </h2>

            <div className="space-y-4">
              <Select
                label="Reasoning Style"
                options={reasoningOptions}
                value={formData.reasoning}
                onChange={(e) => handleInputChange('reasoning', e.target.value)}
              />
              <Textarea
                placeholder="Optional description"
                value={formData.reasoning_description}
                onChange={(e) =>
                  handleInputChange('reasoning_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <Select
                label="Thinking Mode"
                options={thinkingModeOptions}
                value={formData.thinking_mode}
                onChange={(e) =>
                  handleInputChange('thinking_mode', e.target.value)
                }
              />
              <Textarea
                placeholder="Optional description"
                value={formData.thinking_mode_description}
                onChange={(e) =>
                  handleInputChange('thinking_mode_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <Select
                label="Argument Style"
                options={argumentStyleOptions}
                value={formData.argument_style}
                onChange={(e) =>
                  handleInputChange('argument_style', e.target.value)
                }
              />
              <Textarea
                placeholder="Optional description"
                value={formData.argument_style_description}
                onChange={(e) =>
                  handleInputChange(
                    'argument_style_description',
                    e.target.value
                  )
                }
                rows={2}
              />
            </div>
          </div>
        )}

        {currentStep === 6 && (
          <div className="space-y-6">
            <h2 className="font-display text-2xl text-charcoal mb-6">
              Communication Style
            </h2>

            <div className="space-y-4">
              <Select
                label="Pace"
                options={paceOptions}
                value={formData.pace}
                onChange={(e) => handleInputChange('pace', e.target.value)}
              />
              <Textarea
                placeholder="Optional description"
                value={formData.pace_description}
                onChange={(e) =>
                  handleInputChange('pace_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <Select
                label="Formality"
                options={formalityOptions}
                value={formData.formality}
                onChange={(e) => handleInputChange('formality', e.target.value)}
              />
              <Textarea
                placeholder="Optional description"
                value={formData.formality_description}
                onChange={(e) =>
                  handleInputChange('formality_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <Select
                label="Directness"
                options={directnessOptions}
                value={formData.directness}
                onChange={(e) =>
                  handleInputChange('directness', e.target.value)
                }
              />
              <Textarea
                placeholder="Optional description"
                value={formData.directness_description}
                onChange={(e) =>
                  handleInputChange('directness_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <Select
                label="Emotionality"
                options={emotionalityOptions}
                value={formData.emotionality}
                onChange={(e) =>
                  handleInputChange('emotionality', e.target.value)
                }
              />
              <Textarea
                placeholder="Optional description"
                value={formData.emotionality_description}
                onChange={(e) =>
                  handleInputChange('emotionality_description', e.target.value)
                }
                rows={2}
              />
            </div>
          </div>
        )}

        {currentStep === 7 && (
          <div className="space-y-6">
            <h2 className="font-display text-2xl text-charcoal mb-6">
              Discussion Tendencies
            </h2>

            <div className="space-y-4">
              <Select
                label="Conflict Approach"
                options={conflictApproachOptions}
                value={formData.conflict_approach}
                onChange={(e) =>
                  handleInputChange('conflict_approach', e.target.value)
                }
              />
              <Textarea
                placeholder="Optional description"
                value={formData.conflict_approach_description}
                onChange={(e) =>
                  handleInputChange(
                    'conflict_approach_description',
                    e.target.value
                  )
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <Select
                label="Consensus Style"
                options={consensusOptions}
                value={formData.consensus}
                onChange={(e) => handleInputChange('consensus', e.target.value)}
              />
              <Textarea
                placeholder="Optional description"
                value={formData.consensus_description}
                onChange={(e) =>
                  handleInputChange('consensus_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <Select
                label="Focus"
                options={focusOptions}
                value={formData.focus}
                onChange={(e) => handleInputChange('focus', e.target.value)}
              />
              <Textarea
                placeholder="Optional description"
                value={formData.focus_description}
                onChange={(e) =>
                  handleInputChange('focus_description', e.target.value)
                }
                rows={2}
              />
            </div>

            <div className="space-y-4">
              <Textarea
                label="Strengths"
                placeholder="Describe the persona's strengths in discussions"
                value={formData.strengths}
                onChange={(e) =>
                  handleInputChange('strengths', e.target.value)
                }
                rows={3}
              />
            </div>

            <div className="space-y-4">
              <Textarea
                label="Blind Spots"
                placeholder="Describe the persona's blind spots or weaknesses"
                value={formData.blind_spots}
                onChange={(e) =>
                  handleInputChange('blind_spots', e.target.value)
                }
                rows={3}
              />
            </div>

            <div className="space-y-4">
              <Textarea
                label="Trigger Points"
                placeholder="Describe what tends to trigger strong reactions"
                value={formData.trigger_points}
                onChange={(e) =>
                  handleInputChange('trigger_points', e.target.value)
                }
                rows={3}
              />
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-terracotta/10 border border-terracotta rounded">
            <p className="font-sans text-sm text-terracotta">{error}</p>
          </div>
        )}
      </div>

      {/* Navigation buttons */}
      <div className="mt-6 flex items-center justify-between">
        <Button
          variant="secondary"
          onClick={prevStep}
          disabled={currentStep === 1 || isSubmitting}
        >
          Previous
        </Button>

        <div className="flex gap-3">
          {currentStep < 7 ? (
            <Button onClick={nextStep} disabled={!validateStep()}>
              Next
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              loading={isSubmitting}
              disabled={!validateStep()}
            >
              Create Persona
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

export default PersonaForm
