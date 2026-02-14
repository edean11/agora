import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchPersonas } from '../api/personas'
import PersonaCard from '../components/personas/PersonaCard'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'
import Card from '../components/ui/Card'

function Personas() {
  const navigate = useNavigate()

  const { data: personas, isLoading } = useQuery({
    queryKey: ['personas'],
    queryFn: fetchPersonas,
  })

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl text-charcoal">Personas</h1>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            onClick={() => navigate('/personas/create')}
          >
            Generate New
          </Button>
          <Button
            variant="secondary"
            onClick={() => navigate('/personas/create')}
          >
            Create Custom
          </Button>
          <Button onClick={() => navigate('/personas/create')}>
            Create from Person
          </Button>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="py-12">
          <Spinner size="lg" text="Loading personas..." />
        </div>
      ) : personas && personas.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {personas.map((persona) => (
            <PersonaCard key={persona.id} persona={persona} />
          ))}
        </div>
      ) : (
        <Card>
          <div className="text-center py-12 space-y-4">
            <p className="font-sans text-lg text-charcoal-light">
              No personas yet
            </p>
            <p className="font-sans text-sm text-charcoal-light">
              Create your first persona to get started
            </p>
            <div className="pt-4">
              <Button onClick={() => navigate('/personas/create')}>
                Create Persona
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default Personas
