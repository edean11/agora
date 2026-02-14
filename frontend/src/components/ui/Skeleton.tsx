interface SkeletonProps {
  variant?: 'text' | 'title' | 'card' | 'circle'
  className?: string
}

function Skeleton({ variant = 'text', className = '' }: SkeletonProps) {
  const variantStyles = {
    text: 'h-4 w-32 rounded',
    title: 'h-6 w-48 rounded',
    card: 'h-48 w-full rounded-lg',
    circle: 'h-12 w-12 rounded-full',
  }

  return (
    <div
      className={`bg-marble-light animate-skeleton-pulse ${variantStyles[variant]} ${className}`}
    />
  )
}

export default Skeleton
