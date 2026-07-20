import { Link } from 'react-router-dom'

const LEVELS = [
  { id: 1, name: 'The Lobby' },
  { id: 2, name: 'The Lab' },
  { id: 3, name: 'The Core' },
]

function HubPage() {
  return (
    <div className="min-h-full flex flex-col items-center justify-center gap-8 px-4">
      <h1 className="font-mono text-4xl text-neon-cyan tracking-widest">NEUROCORP HEIST</h1>
      <div className="flex flex-col sm:flex-row gap-4">
        {LEVELS.map((level) => (
          <Link
            key={level.id}
            to={`/level/${level.id}`}
            className="rounded-lg border border-cyber-border bg-cyber-panel px-6 py-4 text-center hover:border-neon-cyan transition-colors"
          >
            <div className="text-text-muted text-sm">Level {level.id}</div>
            <div className="font-mono text-lg">{level.name}</div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default HubPage
