import { type InputHTMLAttributes, forwardRef } from 'react'

interface SliderProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
  showValue?: boolean
}

const Slider = forwardRef<HTMLInputElement, SliderProps>(
  (
    {
      label,
      showValue = true,
      min = 0,
      max = 100,
      value,
      className = '',
      ...props
    },
    ref
  ) => {
    return (
      <div className="w-full">
        {(label || showValue) && (
          <div className="flex items-center justify-between mb-2">
            {label && (
              <label className="block font-display text-sm font-medium text-charcoal">
                {label}
              </label>
            )}
            {showValue && (
              <span className="font-sans text-sm text-charcoal-light tabular-nums">
                {value}
              </span>
            )}
          </div>
        )}
        <input
          ref={ref}
          type="range"
          min={min}
          max={max}
          value={value}
          className={`w-full h-2 bg-charcoal-light/20 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-gold focus:ring-offset-2
            [&::-webkit-slider-thumb]:appearance-none
            [&::-webkit-slider-thumb]:w-4
            [&::-webkit-slider-thumb]:h-4
            [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-gold
            [&::-webkit-slider-thumb]:cursor-pointer
            [&::-webkit-slider-thumb]:transition-all
            [&::-webkit-slider-thumb]:duration-200
            [&::-webkit-slider-thumb]:hover:bg-gold-light
            [&::-webkit-slider-thumb]:hover:scale-110
            [&::-moz-range-thumb]:w-4
            [&::-moz-range-thumb]:h-4
            [&::-moz-range-thumb]:rounded-full
            [&::-moz-range-thumb]:bg-gold
            [&::-moz-range-thumb]:border-0
            [&::-moz-range-thumb]:cursor-pointer
            [&::-moz-range-thumb]:transition-all
            [&::-moz-range-thumb]:duration-200
            [&::-moz-range-thumb]:hover:bg-gold-light
            [&::-moz-range-thumb]:hover:scale-110
            ${className}`}
          {...props}
        />
      </div>
    )
  }
)

Slider.displayName = 'Slider'

export default Slider
