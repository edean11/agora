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
    <div className="border-t border-marble-dark bg-parchment px-4 sm:px-6 py-3 sm:py-4">
      <div className="max-w-4xl mx-auto space-y-3">
        {/* Input field */}
        <div className="flex items-center gap-2 sm:gap-3">
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
            className="flex-1 px-3 sm:px-4 py-2 min-h-[44px] bg-parchment border border-charcoal-light rounded transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gold focus:border-gold disabled:opacity-50 disabled:cursor-not-allowed font-sans text-sm sm:text-base"
          />
          <Button
            onClick={handleSend}
            disabled={disabled || isFinished || !message.trim()}
            size="sm"
          >
            Send
          </Button>
        </div>

        {/* Action buttons */}
        {!isFinished && (
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
            <Button
              onClick={() => onContinue(5)}
              disabled={disabled}
              variant="secondary"
              size="sm"
              className="w-full sm:w-auto"
            >
              Continue (5 rounds)
            </Button>
            <Button
              onClick={onEndDiscussion}
              disabled={disabled}
              variant="danger"
              size="sm"
              className="w-full sm:w-auto"
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
