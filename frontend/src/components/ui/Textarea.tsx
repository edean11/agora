import { type TextareaHTMLAttributes, forwardRef, useEffect, useRef } from 'react'

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  autoResize?: boolean
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, autoResize = false, className = '', ...props }, ref) => {
    const internalRef = useRef<HTMLTextAreaElement | null>(null)
    const textareaStyles = error
      ? 'border-terracotta focus:ring-terracotta focus:border-terracotta'
      : 'border-charcoal-light focus:ring-gold focus:border-gold'

    useEffect(() => {
      if (!autoResize) return

      const textarea = internalRef.current
      if (!textarea) return

      const handleResize = () => {
        textarea.style.height = 'auto'
        textarea.style.height = `${textarea.scrollHeight}px`
      }

      textarea.addEventListener('input', handleResize)
      handleResize() // Initial resize

      return () => {
        textarea.removeEventListener('input', handleResize)
      }
    }, [autoResize])

    const handleRef = (node: HTMLTextAreaElement | null) => {
      internalRef.current = node
      if (typeof ref === 'function') {
        ref(node)
      } else if (ref) {
        ref.current = node
      }
    }

    return (
      <div className="w-full">
        {label && (
          <label className="block font-display text-sm font-medium text-charcoal mb-1.5">
            {label}
          </label>
        )}
        <textarea
          ref={handleRef}
          className={`w-full px-4 py-2 bg-parchment border rounded transition-all duration-200 focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed resize-none ${textareaStyles} ${className}`}
          rows={props.rows ?? 4}
          {...props}
        />
        {error && (
          <p className="mt-1.5 text-sm text-terracotta font-sans">{error}</p>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'

export default Textarea
