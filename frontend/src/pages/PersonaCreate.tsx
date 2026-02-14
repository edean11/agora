import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Spinner from '../components/ui/Spinner'
import PersonaForm from '../components/personas/PersonaForm'
import { generatePersonas, createFromPerson, type PersonaDisambiguation } from '../api/personas'
import type { PersonaFull } from '../api/types'

type Tab = 'manual' | 'generate' | 'from-person'

interface Candidate {
  name: string
  description: string
}

function PersonaCreate() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<Tab>('manual')

  // Generate flow state
  const [generateCount, setGenerateCount] = useState(1)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState('')

  // From-person flow state
  const [personName, setPersonName] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [fromPersonError, setFromPersonError] = useState('')
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [selectedCandidate, setSelectedCandidate] = useState<number | null>(null)

  const handleGenerate = async () => {
    setIsGenerating(true)
    setGenerateError('')

    try {
      const result = await generatePersonas(generateCount)
      // Redirect to gallery to see the generated personas
      navigate('/personas', {
        state: { message: `Successfully generated ${result.length} persona(s)` },
      })
    } catch (err) {
      setGenerateError(
        err instanceof Error ? err.message : 'Failed to generate personas'
      )
      setIsGenerating(false)
    }
  }

  const handleFindPerson = async () => {
    if (!personName.trim()) {
      setFromPersonError('Please enter a person name')
      return
    }

    setIsSearching(true)
    setFromPersonError('')
    setCandidates([])
    setSelectedCandidate(null)

    try {
      const result = await createFromPerson(personName)

      // Check if result is disambiguation or full persona
      if ('candidates' in result) {
        // Disambiguation case
        const disambiguation = result as PersonaDisambiguation
        setCandidates(disambiguation.candidates)
      } else {
        // Unambiguous case - redirect to persona detail
        const persona = result as PersonaFull
        navigate(`/personas/${persona.id}`)
      }
    } catch (err) {
      setFromPersonError(
        err instanceof Error ? err.message : 'Failed to find person'
      )
    } finally {
      setIsSearching(false)
    }
  }

  const handleSelectCandidate = async () => {
    if (selectedCandidate === null) {
      setFromPersonError('Please select a candidate')
      return
    }

    setIsSearching(true)
    setFromPersonError('')

    try {
      const result = await createFromPerson(personName, selectedCandidate)

      // Should be a full persona now
      if ('candidates' in result) {
        throw new Error('Unexpected disambiguation response')
      }

      const persona = result as PersonaFull
      navigate(`/personas/${persona.id}`)
    } catch (err) {
      setFromPersonError(
        err instanceof Error ? err.message : 'Failed to create persona'
      )
      setIsSearching(false)
    }
  }

  return (
    <div className="p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="font-display text-4xl text-charcoal mb-2">
          Create Persona
        </h1>
        <p className="font-sans text-charcoal-light mb-8">
          Create a new AI persona using one of three methods
        </p>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-charcoal-light/20 mb-8">
          <button
            onClick={() => setActiveTab('manual')}
            className={`font-display px-6 py-3 border-b-2 transition-all duration-200 ${
              activeTab === 'manual'
                ? 'border-gold text-charcoal font-medium'
                : 'border-transparent text-charcoal-light hover:text-charcoal'
            }`}
          >
            Create Custom
          </button>
          <button
            onClick={() => setActiveTab('generate')}
            className={`font-display px-6 py-3 border-b-2 transition-all duration-200 ${
              activeTab === 'generate'
                ? 'border-gold text-charcoal font-medium'
                : 'border-transparent text-charcoal-light hover:text-charcoal'
            }`}
          >
            Generate
          </button>
          <button
            onClick={() => setActiveTab('from-person')}
            className={`font-display px-6 py-3 border-b-2 transition-all duration-200 ${
              activeTab === 'from-person'
                ? 'border-gold text-charcoal font-medium'
                : 'border-transparent text-charcoal-light hover:text-charcoal'
            }`}
          >
            From Person
          </button>
        </div>

        {/* Tab content */}
        {activeTab === 'manual' && <PersonaForm />}

        {activeTab === 'generate' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-parchment/50 border border-charcoal-light/20 rounded-lg p-8">
              <h2 className="font-display text-2xl text-charcoal mb-4">
                Auto-Generate Personas
              </h2>
              <p className="font-sans text-charcoal-light mb-6">
                Generate random personas with AI-generated personalities,
                backgrounds, and traits.
              </p>

              {isGenerating ? (
                <Spinner
                  size="lg"
                  text="Generating personas... This may take a while."
                />
              ) : (
                <>
                  <div className="mb-6">
                    <Input
                      label="Number of personas to generate"
                      type="number"
                      min={1}
                      max={5}
                      value={generateCount}
                      onChange={(e) =>
                        setGenerateCount(
                          Math.min(
                            5,
                            Math.max(1, parseInt(e.target.value) || 1)
                          )
                        )
                      }
                    />
                    <p className="font-sans text-xs text-charcoal-light mt-2">
                      Maximum 5 personas at a time
                    </p>
                  </div>

                  {generateError && (
                    <div className="mb-6 p-4 bg-terracotta/10 border border-terracotta rounded">
                      <p className="font-sans text-sm text-terracotta">
                        {generateError}
                      </p>
                    </div>
                  )}

                  <Button onClick={handleGenerate} size="lg">
                    Generate {generateCount} Persona{generateCount > 1 ? 's' : ''}
                  </Button>
                </>
              )}
            </div>
          </div>
        )}

        {activeTab === 'from-person' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-parchment/50 border border-charcoal-light/20 rounded-lg p-8">
              <h2 className="font-display text-2xl text-charcoal mb-4">
                Create from Historical Person
              </h2>
              <p className="font-sans text-charcoal-light mb-6">
                Create a persona based on a famous historical figure. The AI
                will research and generate appropriate personality traits.
              </p>

              {isSearching ? (
                <Spinner
                  size="lg"
                  text="Searching and analyzing... This may take a while."
                />
              ) : candidates.length > 0 ? (
                <>
                  <h3 className="font-display text-lg text-charcoal mb-4">
                    Multiple matches found. Please select one:
                  </h3>

                  <div className="space-y-3 mb-6">
                    {candidates.map((candidate, index) => (
                      <label
                        key={index}
                        className={`block p-4 border-2 rounded cursor-pointer transition-all duration-200 ${
                          selectedCandidate === index
                            ? 'border-gold bg-gold/10'
                            : 'border-charcoal-light/20 hover:border-gold/50'
                        }`}
                      >
                        <input
                          type="radio"
                          name="candidate"
                          value={index}
                          checked={selectedCandidate === index}
                          onChange={() => setSelectedCandidate(index)}
                          className="mr-3"
                        />
                        <span className="font-display font-medium text-charcoal">
                          {candidate.name}
                        </span>
                        <p className="font-sans text-sm text-charcoal-light mt-1 ml-6">
                          {candidate.description}
                        </p>
                      </label>
                    ))}
                  </div>

                  {fromPersonError && (
                    <div className="mb-6 p-4 bg-terracotta/10 border border-terracotta rounded">
                      <p className="font-sans text-sm text-terracotta">
                        {fromPersonError}
                      </p>
                    </div>
                  )}

                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      onClick={() => {
                        setCandidates([])
                        setSelectedCandidate(null)
                        setPersonName('')
                      }}
                    >
                      Start Over
                    </Button>
                    <Button
                      onClick={handleSelectCandidate}
                      disabled={selectedCandidate === null}
                    >
                      Create Persona
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <div className="mb-6">
                    <Input
                      label="Person name"
                      value={personName}
                      onChange={(e) => setPersonName(e.target.value)}
                      placeholder="e.g., Albert Einstein, Marie Curie"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleFindPerson()
                        }
                      }}
                    />
                  </div>

                  {fromPersonError && (
                    <div className="mb-6 p-4 bg-terracotta/10 border border-terracotta rounded">
                      <p className="font-sans text-sm text-terracotta">
                        {fromPersonError}
                      </p>
                    </div>
                  )}

                  <Button
                    onClick={handleFindPerson}
                    disabled={!personName.trim()}
                    size="lg"
                  >
                    Find Person
                  </Button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PersonaCreate
