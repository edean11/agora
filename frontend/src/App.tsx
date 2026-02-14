import { BrowserRouter, Routes, Route } from 'react-router-dom'
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

function App() {
  return (
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
  )
}

export default App
