function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-marble-light border-b border-marble-dark z-10">
      <div className="h-full flex items-center px-6">
        <h1 className="font-display text-2xl tracking-wider text-charcoal-dark flex items-center gap-3">
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            className="text-gold"
            aria-hidden="true"
          >
            {/* Simple laurel wreath - left side */}
            <path
              d="M8 12c-1-2-2-4-2-6 0 0 1 1 2 2 1-1 2-2 2-2 0 2-1 4-2 6z"
              fill="currentColor"
            />
            {/* Right side */}
            <path
              d="M16 12c1-2 2-4 2-6 0 0-1 1-2 2-1-1-2-2-2-2 0 2 1 4 2 6z"
              fill="currentColor"
            />
            {/* Bottom leaves */}
            <path
              d="M8 12c-1 2-2 4-2 6 0 0 1-1 2-2 1 1 2 2 2 2 0-2-1-4-2-6z"
              fill="currentColor"
            />
            <path
              d="M16 12c1 2 2 4 2 6 0 0-1-1-2-2-1 1-2 2-2 2 0-2 1-4 2-6z"
              fill="currentColor"
            />
          </svg>
          <span className="relative">
            AGORA
            <span className="absolute -bottom-1 left-0 right-0 h-0.5 bg-gold"></span>
          </span>
        </h1>
      </div>
    </header>
  )
}

export default Header
