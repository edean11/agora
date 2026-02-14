import { useNavigate } from 'react-router-dom'
import Card from '../ui/Card'
import type { PersonaSummary } from '../../api/types'

interface PersonaCardProps {
  persona: PersonaSummary
}

function PersonaCard({ persona }: PersonaCardProps) {
  const navigate = useNavigate()

  const bigFiveTraits = [
    { label: 'O', level: persona.openness || 'Medium' },
    { label: 'C', level: persona.conscientiousness || 'Medium' },
    { label: 'E', level: persona.extraversion || 'Medium' },
    { label: 'A', level: persona.agreeableness || 'Medium' },
    { label: 'N', level: persona.neuroticism || 'Medium' },
  ]

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

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  return (
    <Card
      hover
      onClick={() => navigate(`/personas/${persona.id}`)}
      className="cursor-pointer"
    >
      <div className="space-y-4">
        {/* Name and Age */}
        <div className="space-y-1">
          <h3 className="font-display text-xl text-charcoal">{persona.name}</h3>
          <p className="font-sans text-sm text-charcoal-light">Age {persona.age}</p>
        </div>

        {/* Background snippet */}
        <p className="font-sans text-sm text-charcoal-light leading-relaxed">
          {truncateText(persona.background_brief, 100)}
        </p>

        {/* Big Five mini-visualization */}
        <div className="space-y-2 pt-2 border-t border-marble-dark/30">
          <p className="font-sans text-xs uppercase tracking-wide text-charcoal-light">
            Big Five Traits
          </p>
          <div className="grid grid-cols-5 gap-2">
            {bigFiveTraits.map((trait) => (
              <div key={trait.label} className="space-y-1">
                <div className="text-center">
                  <span className="font-sans text-xs font-medium text-charcoal">
                    {trait.label}
                  </span>
                </div>
                <div className="h-1.5 bg-marble-dark/30 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-olive rounded-full transition-all duration-300"
                    style={{ width: getLevelWidth(trait.level) }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  )
}

export default PersonaCard
