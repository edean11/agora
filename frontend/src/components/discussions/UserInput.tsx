import { useState, type KeyboardEvent } from 'react'
import Button from '../ui/Button'

interface UserInputProps {
  disabled: boolean
  isFinished: boolean
  onSendMessage: (content: string) => void
  onContinue: (rounds: number) => void
  onEndDiscussion: () => void
}

function UserInput({
  disabled,
  isFinished,
  onSendMessage,
  onContinue,
  onEndDiscussion,
}: UserInputProps) {
  const [message, setMessage] = useState('')

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled && message.trim()) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="border-t border-marble-dark bg-parchment px-6 py-4">
      <div className="max-w-4xl mx-auto space-y-3">
        {/* Input field */}
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={disabled || isFinished}
            placeholder={
              isFinished
                ? 'Discussion has ended'
                : disabled
                  ? 'Waiting for agents...'
                  : 'Type your message...'
            }
            className="flex-1 px-4 py-2 bg-parchment border border-charcoal-light rounded transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gold focus:border-gold disabled:opacity-50 disabled:cursor-not-allowed font-sans"
          />
          <Button
            onClick={handleSend}
            disabled={disabled || isFinished || !message.trim()}
            size="md"
          >
            Send
          </Button>
        </div>

        {/* Action buttons */}
        {!isFinished && (
          <div className="flex items-center gap-3">
            <Button
              onClick={() => onContinue(5)}
              disabled={disabled}
              variant="secondary"
              size="sm"
            >
              Continue (5 rounds)
            </Button>
            <Button
              onClick={onEndDiscussion}
              disabled={disabled}
              variant="danger"
              size="sm"
            >
              End Discussion
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

export default UserInput
