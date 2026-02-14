import { type HTMLAttributes } from 'react'

function ColumnDivider({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`flex items-center justify-center my-4 ${className}`}
      {...props}
    >
      <div className="flex-1 h-px bg-marble-dark" />
      <svg
        width="32"
        height="48"
        viewBox="0 0 32 48"
        fill="none"
        className="mx-4 text-gold"
        aria-hidden="true"
      >
        {/* Ionic column capital */}
        <rect x="4" y="0" width="24" height="2" fill="currentColor" />
        <path
          d="M4 2 L6 6 L26 6 L28 2"
          fill="currentColor"
          opacity="0.7"
        />

        {/* Column shaft */}
        <rect x="10" y="6" width="12" height="36" fill="currentColor" opacity="0.5" />

        {/* Base */}
        <path
          d="M6 42 L4 46 L28 46 L26 42"
          fill="currentColor"
          opacity="0.7"
        />
        <rect x="4" y="46" width="24" height="2" fill="currentColor" />
      </svg>
      <div className="flex-1 h-px bg-marble-dark" />
    </div>
  )
}

export default ColumnDivider
