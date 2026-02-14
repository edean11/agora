import AgentAvatar from './AgentAvatar'

interface ThinkingIndicatorProps {
  agentName: string
}

function ThinkingIndicator({ agentName }: ThinkingIndicatorProps) {
  return (
    <div className="flex items-start gap-3 animate-fade-in">
      <AgentAvatar name={agentName} />
      <div className="flex-1 pt-2">
        <p className="font-sans text-sm text-charcoal-light italic">
          {agentName} is thinking
          <span className="inline-flex gap-0.5 ml-1">
            <span className="animate-pulse-dot" style={{ animationDelay: '0ms' }}>
              .
            </span>
            <span className="animate-pulse-dot" style={{ animationDelay: '200ms' }}>
              .
            </span>
            <span className="animate-pulse-dot" style={{ animationDelay: '400ms' }}>
              .
            </span>
          </span>
        </p>
      </div>
    </div>
  )
}

export default ThinkingIndicator
