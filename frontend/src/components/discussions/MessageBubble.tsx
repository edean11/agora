import AgentAvatar from './AgentAvatar'
import type { TranscriptEntry } from '../../api/types'

interface MessageBubbleProps {
  message: TranscriptEntry
  isUser?: boolean
}

function MessageBubble({ message, isUser = false }: MessageBubbleProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  return (
    <div
      className={`flex items-start gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <AgentAvatar name={message.speaker} isUser={isUser} />
      <div className={`flex-1 space-y-1 ${isUser ? 'text-right' : ''}`}>
        <div className="flex items-baseline gap-2">
          <span
            className={`font-display font-semibold text-charcoal ${isUser ? 'order-2' : ''}`}
          >
            {message.speaker}
          </span>
          <span
            className={`font-sans text-xs text-charcoal-light ${isUser ? 'order-1' : ''}`}
          >
            {formatTime(message.timestamp)}
          </span>
        </div>
        <div
          className={`inline-block px-4 py-2 rounded-lg ${
            isUser
              ? 'bg-gold bg-opacity-20 text-charcoal'
              : 'bg-marble text-charcoal'
          }`}
        >
          <p className="font-sans text-base whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
