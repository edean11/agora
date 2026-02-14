interface RoundDividerProps {
  round: number
}

function RoundDivider({ round }: RoundDividerProps) {
  return (
    <div className="flex items-center gap-4 py-6 animate-fade-in">
      <div className="flex-1 h-px bg-gold opacity-30" />
      <span className="font-sans text-sm text-charcoal-light uppercase tracking-wide">
        Round {round}
      </span>
      <div className="flex-1 h-px bg-gold opacity-30" />
    </div>
  )
}

export default RoundDivider
