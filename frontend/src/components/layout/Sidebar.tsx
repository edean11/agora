import { NavLink } from 'react-router-dom'
import { useEffect } from 'react'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

function Sidebar({ isOpen, onClose }: SidebarProps) {
  const linkClassName = ({ isActive }: { isActive: boolean }) =>
    `block px-4 py-3 text-charcoal transition-all duration-200 min-h-[44px] flex items-center ${
      isActive
        ? 'bg-gold-light/10 border-l-4 border-gold'
        : 'hover:bg-gold-light/10 border-l-4 border-transparent'
    }`

  // Close sidebar on navigation (mobile)
  const handleLinkClick = () => {
    if (window.innerWidth < 1024) {
      onClose()
    }
  }

  // Close sidebar on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  // Prevent body scroll when mobile sidebar is open
  useEffect(() => {
    if (isOpen && window.innerWidth < 1024) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  return (
    <>
      {/* Backdrop - mobile/tablet only */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-charcoal/50 z-20 lg:hidden animate-fade-in-page"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-16 left-0 bottom-0 w-60 bg-marble border-r border-marble-dark overflow-y-auto z-30
          transition-transform duration-300 ease-in-out
          lg:translate-x-0
          ${isOpen ? 'translate-x-0 shadow-xl' : '-translate-x-full'}
        `}
      >
        <nav className="p-4 space-y-6">
          {/* Discussions Section */}
          <div>
            <h2 className="font-display text-sm uppercase tracking-wider text-charcoal-light mb-2 px-4">
              Discussions
            </h2>
            <div className="space-y-1">
              <NavLink
                to="/discussions"
                className={linkClassName}
                onClick={handleLinkClick}
              >
                All Discussions
              </NavLink>
              <NavLink
                to="/discussions/new"
                className={linkClassName}
                onClick={handleLinkClick}
              >
                New Discussion
              </NavLink>
            </div>
          </div>

          {/* Decorative Divider */}
          <div className="border-t border-marble-dark mx-4"></div>

          {/* Personas Section */}
          <div>
            <h2 className="font-display text-sm uppercase tracking-wider text-charcoal-light mb-2 px-4">
              Personas
            </h2>
            <div className="space-y-1">
              <NavLink
                to="/personas"
                className={linkClassName}
                onClick={handleLinkClick}
              >
                Gallery
              </NavLink>
              <NavLink
                to="/personas/create"
                className={linkClassName}
                onClick={handleLinkClick}
              >
                Create Persona
              </NavLink>
            </div>
          </div>
        </nav>
      </aside>
    </>
  )
}

export default Sidebar
