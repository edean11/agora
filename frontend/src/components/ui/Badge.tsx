import { type ReactNode, type HTMLAttributes } from 'react'

type BadgeVariant =
  | 'active'
  | 'completed'
  | 'paused'
  | 'observation'
  | 'own_statement'
  | 'reflection'
  | 'user_interaction'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant: BadgeVariant
  children: ReactNode
}

function Badge({ variant, children, className = '', ...props }: BadgeProps) {
  const baseStyles =
    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-sans font-medium'

  const variantStyles = {
    // Status badges
    active: 'bg-olive text-parchment',
    completed: 'bg-gold text-charcoal',
    paused: 'bg-terracotta text-parchment',
    // Type badges
    observation: 'bg-olive text-parchment',
    own_statement: 'bg-gold text-charcoal',
    reflection: 'bg-terracotta text-parchment',
    user_interaction: 'bg-charcoal text-parchment',
  }

  return (
    <span
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  )
}

export default Badge
