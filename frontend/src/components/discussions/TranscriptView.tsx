import { useEffect, useRef, type ReactElement } from 'react'
import MessageBubble from './MessageBubble'
import ThinkingIndicator from './ThinkingIndicator'
import RoundDivider from './RoundDivider'
import type { TranscriptEntry } from '../../api/types'

interface TranscriptViewProps {
  messages: TranscriptEntry[]
  thinkingAgent: string | null
  rounds: { round: number; index: number }[]
}

function TranscriptView({
  messages,
  thinkingAgent,
  rounds,
}: TranscriptViewProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinkingAgent])

  const renderContent = () => {
    const elements: ReactElement[] = []
    let messageIndex = 0

    // Merge messages and round dividers
    for (let i = 0; i < rounds.length; i++) {
      const { round, index } = rounds[i]

      // Add messages before this round divider
      while (messageIndex < index && messageIndex < messages.length) {
        const message = messages[messageIndex]
        const isUser = message.speaker.toLowerCase() === 'user'
        elements.push(
          <MessageBubble
            key={`message-${messageIndex}`}
            message={message}
            isUser={isUser}
          />
        )
        messageIndex++
      }

      // Add round divider
      elements.push(<RoundDivider key={`round-${round}`} round={round} />)
    }

    // Add remaining messages
    while (messageIndex < messages.length) {
      const message = messages[messageIndex]
      const isUser = message.speaker.toLowerCase() === 'user'
      elements.push(
        <MessageBubble
          key={`message-${messageIndex}`}
          message={message}
          isUser={isUser}
        />
      )
      messageIndex++
    }

    return elements
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4">
      <div className="max-w-4xl mx-auto">
        {renderContent()}
        {thinkingAgent && <ThinkingIndicator agentName={thinkingAgent} />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

export default TranscriptView
