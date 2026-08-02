import { BrowserRouter, Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import HubPage from './pages/HubPage'
import GamePage from './pages/GamePage'
import NotFoundPage from './pages/NotFoundPage'
import ResultPage from './pages/ResultPage'

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HubPage />} />
          <Route path="/level/:levelId" element={<GamePage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
