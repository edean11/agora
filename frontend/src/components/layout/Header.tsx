interface HeaderProps {
  onMenuToggle: () => void
}

function Header({ onMenuToggle }: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-marble-light border-b border-marble-dark z-10">
      <div className="h-full flex items-center px-4 sm:px-6">
        {/* Hamburger Menu Button - visible on mobile/tablet */}
        <button
          onClick={onMenuToggle}
          className="lg:hidden mr-3 p-2 hover:bg-marble rounded transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
          aria-label="Toggle menu"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            className="text-charcoal"
          >
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>

        <h1 className="font-display text-xl sm:text-2xl tracking-wider text-charcoal-dark flex items-center gap-2 sm:gap-3">
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            className="text-gold w-5 h-5 sm:w-6 sm:h-6"
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
