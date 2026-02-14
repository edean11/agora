import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchPersonas } from '../api/personas'
import PersonaCard from '../components/personas/PersonaCard'
import Button from '../components/ui/Button'
import Skeleton from '../components/ui/Skeleton'
import Card from '../components/ui/Card'
import { useToast } from '../hooks/useToast'
import { useEffect } from 'react'

function Personas() {
  const navigate = useNavigate()
  const { showToast } = useToast()

  const { data: personas, isLoading, error } = useQuery({
    queryKey: ['personas'],
    queryFn: fetchPersonas,
  })

  useEffect(() => {
    if (error) {
      showToast('Unable to load personas', 'error')
    }
  }, [error, showToast])

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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Card key={i}>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Skeleton variant="circle" className="h-12 w-12" />
                  <Skeleton variant="title" className="flex-1" />
                </div>
                <Skeleton variant="text" className="w-full" />
                <Skeleton variant="text" className="w-3/4" />
                <div className="flex gap-2">
                  <Skeleton variant="text" className="w-16 h-6" />
                  <Skeleton variant="text" className="w-16 h-6" />
                </div>
              </div>
            </Card>
          ))}
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
              No personas found. Create your first!
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
