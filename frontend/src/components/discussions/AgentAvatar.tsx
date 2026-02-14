interface AgentAvatarProps {
  name: string
  isUser?: boolean
}

const AVATAR_COLORS = [
  'bg-olive',
  'bg-gold',
  'bg-terracotta',
  'bg-burgundy',
  'bg-charcoal-light',
]

function hashString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    hash = hash & hash
  }
  return Math.abs(hash)
}

function AgentAvatar({ name, isUser = false }: AgentAvatarProps) {
  const colorIndex = hashString(name) % AVATAR_COLORS.length
  const bgColor = isUser ? 'bg-charcoal' : AVATAR_COLORS[colorIndex]
  const initial = isUser ? 'U' : name.charAt(0).toUpperCase()

  return (
    <div
      className={`flex items-center justify-center w-10 h-10 rounded-full ${bgColor} text-parchment font-display font-semibold text-lg flex-shrink-0`}
    >
      {initial}
    </div>
  )
}

export default AgentAvatar
