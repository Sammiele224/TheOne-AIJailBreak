import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HubPage from './pages/HubPage'
import GamePage from './pages/GamePage'
import ResultPage from './pages/ResultPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HubPage />} />
        <Route path="/level/:levelId" element={<GamePage />} />
        <Route path="/result" element={<ResultPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
