import { type InputHTMLAttributes, forwardRef } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', ...props }, ref) => {
    const inputStyles = error
      ? 'border-terracotta focus:ring-terracotta focus:border-terracotta'
      : 'border-charcoal-light focus:ring-gold focus:border-gold'

    return (
      <div className="w-full">
        {label && (
          <label className="block font-display text-sm font-medium text-charcoal mb-1.5">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`w-full px-4 py-2 bg-parchment border rounded transition-all duration-200 focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed ${inputStyles} ${className}`}
          {...props}
        />
        {error && (
          <p className="mt-1.5 text-sm text-terracotta font-sans">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
