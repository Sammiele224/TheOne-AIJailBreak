import { Link } from 'react-router-dom'
import Button from '../components/ui/Button'

function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="max-w-xl rounded-[30px] border border-cyber-border/70 bg-cyber-panel/80 p-8 text-center shadow-[0_0_60px_rgba(78,246,255,0.12)]">
        <p className="font-mono text-sm uppercase tracking-[0.35em] text-neon-cyan">404</p>
        <h1 className="mt-3 text-4xl font-semibold">The route is not available.</h1>
        <p className="mt-3 text-sm leading-7 text-text-muted">The mission map doesn’t contain that endpoint. Return to the hub and continue the operation.</p>
        <div className="mt-6 flex justify-center gap-3">
          <Button asChild>
            <Link to="/">Return home</Link>
          </Button>
          <Button variant="secondary" asChild>
            <Link to="/level/1">Start Level 1</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage
