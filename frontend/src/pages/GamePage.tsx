import { useParams } from 'react-router-dom'

function GamePage() {
  const { levelId } = useParams<{ levelId: string }>()

  return (
    <div className="min-h-full flex flex-col p-4">
      <header className="text-text-muted font-mono text-sm mb-4">LEVEL {levelId}</header>
      <div className="flex-1 rounded-lg border border-cyber-border bg-cyber-panel p-4">
        {/* Chat console mounts here */}
      </div>
    </div>
  )
}

export default GamePage
