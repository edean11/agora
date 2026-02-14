import { type ReactNode, useState } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import HealthBanner from '../ui/HealthBanner'

interface AppShellProps {
  children: ReactNode
}

function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-parchment">
      <Header onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
      <HealthBanner />
      <div className="flex pt-16">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 lg:ml-60 overflow-y-auto animate-fade-in-page">
          {children}
        </main>
      </div>
    </div>
  )
}

export default AppShell
