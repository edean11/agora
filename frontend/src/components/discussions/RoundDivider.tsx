interface RoundDividerProps {
  round: number
}

function RoundDivider({ round }: RoundDividerProps) {
  return (
    <div className="flex items-center gap-4 py-6">
      <div className="flex-1 h-px bg-gold opacity-30 origin-center animate-expand-line" />
      <span className="font-sans text-sm text-charcoal-light uppercase tracking-wide animate-fade-in" style={{ animationDelay: '200ms' }}>
        Round {round}
      </span>
      <div className="flex-1 h-px bg-gold opacity-30 origin-center animate-expand-line" />
    </div>
  )
}

export default RoundDivider
