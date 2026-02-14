import { NavLink } from 'react-router-dom'

function Sidebar() {
  const linkClassName = ({ isActive }: { isActive: boolean }) =>
    `block px-4 py-2 text-charcoal transition-colors ${
      isActive
        ? 'bg-gold-light/10 border-l-2 border-gold'
        : 'hover:bg-gold-light/10 border-l-2 border-transparent'
    }`

  return (
    <aside className="fixed top-16 left-0 bottom-0 w-60 bg-marble border-r border-marble-dark overflow-y-auto">
      <nav className="p-4 space-y-6">
        {/* Discussions Section */}
        <div>
          <h2 className="font-display text-sm uppercase tracking-wider text-charcoal-light mb-2 px-4">
            Discussions
          </h2>
          <div className="space-y-1">
            <NavLink to="/discussions" className={linkClassName}>
              All Discussions
            </NavLink>
            <NavLink to="/discussions/new" className={linkClassName}>
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
            <NavLink to="/personas" className={linkClassName}>
              Gallery
            </NavLink>
            <NavLink to="/personas/create" className={linkClassName}>
              Create Persona
            </NavLink>
          </div>
        </div>
      </nav>
    </aside>
  )
}

export default Sidebar
