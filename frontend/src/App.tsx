import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider, QueryCache, MutationCache } from '@tanstack/react-query'
import { useMemo } from 'react'
import ErrorBoundary from './components/ErrorBoundary'
import { ToastProvider } from './components/ui/Toast'
import { useToast } from './hooks/useToast'
import AppShell from './components/layout/AppShell'
import Home from './pages/Home'
import Discussions from './pages/Discussions'
import DiscussionNew from './pages/DiscussionNew'
import DiscussionView from './pages/DiscussionView'
import Personas from './pages/Personas'
import PersonaDetail from './pages/PersonaDetail'
import PersonaCreate from './pages/PersonaCreate'
import AgentAsk from './pages/AgentAsk'
import AgentMemory from './pages/AgentMemory'

function AppContent() {
  const { showToast } = useToast()

  // Create QueryClient with global error handler using QueryCache and MutationCache
  const queryClient = useMemo(
    () =>
      new QueryClient({
        queryCache: new QueryCache({
          onError: (error) => {
            const message = error instanceof Error ? error.message : 'An error occurred'
            showToast(message, 'error')
          },
        }),
        mutationCache: new MutationCache({
          onError: (error) => {
            const message = error instanceof Error ? error.message : 'An error occurred'
            showToast(message, 'error')
          },
        }),
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
          },
          mutations: {
            retry: 0,
          },
        },
      }),
    [showToast]
  )

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppShell>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/discussions" element={<Discussions />} />
            <Route path="/discussions/new" element={<DiscussionNew />} />
            <Route path="/discussions/:id" element={<DiscussionView />} />
            <Route path="/personas" element={<Personas />} />
            <Route path="/personas/:id" element={<PersonaDetail />} />
            <Route path="/personas/create" element={<PersonaCreate />} />
            <Route path="/agents/:id/ask" element={<AgentAsk />} />
            <Route path="/agents/:id/memory" element={<AgentMemory />} />
          </Routes>
        </AppShell>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App
