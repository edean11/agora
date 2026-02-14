import { type ReactNode, type HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  children: ReactNode
}

function Card({ hover = false, children, className = '', ...props }: CardProps) {
  const baseStyles =
    'bg-marble-light rounded-lg shadow-sm border border-marble-dark/30 p-4 sm:p-6'
  const hoverStyles = hover
    ? 'transition-all duration-200 hover:scale-[1.02] hover:shadow-lg hover:shadow-charcoal/10'
    : ''

  return (
    <div className={`${baseStyles} ${hoverStyles} ${className}`} {...props}>
      {children}
    </div>
  )
}

export default Card
