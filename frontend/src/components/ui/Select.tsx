import { type SelectHTMLAttributes, forwardRef } from 'react'

interface SelectOption {
  value: string
  label: string
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: SelectOption[]
  error?: string
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, error, className = '', ...props }, ref) => {
    const selectStyles = error
      ? 'border-terracotta focus:ring-terracotta focus:border-terracotta'
      : 'border-charcoal-light focus:ring-gold focus:border-gold'

    return (
      <div className="w-full">
        {label && (
          <label className="block font-display text-sm font-medium text-charcoal mb-1.5">
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={`w-full px-4 py-2 bg-parchment border rounded transition-all duration-200 focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed ${selectStyles} ${className}`}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && (
          <p className="mt-1.5 text-sm text-terracotta font-sans">{error}</p>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'

export default Select
