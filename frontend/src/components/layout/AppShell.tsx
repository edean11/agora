import { type ReactNode } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import HealthBanner from '../ui/HealthBanner'

interface AppShellProps {
  children: ReactNode
}

function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-parchment">
      <Header />
      <HealthBanner />
      <div className="flex pt-16">
        <Sidebar />
        <main className="flex-1 ml-60 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

export default AppShell
