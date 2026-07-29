import { RefreshCw, ShieldCheck, Sparkles } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import Layout from '../components/Layout'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'

function ResultPage() {
  const location = useLocation()
  const state = location.state as { levelId?: number; result?: 'victory' | 'defeat' } | undefined
  const isVictory = state?.result === 'victory'

  return (
    <Layout title={isVictory ? 'Mission accomplished' : 'Mission contained'} subtitle={isVictory ? 'The attempted prompt succeeded and the system responded as intended.' : 'The guard held. Review the outcome and restart the run with a fresh angle.'}>
      <Card className={`p-8 text-center shadow-[0_0_50px_rgba(78,246,255,0.08)] ${isVictory ? 'border-neon-cyan/40 bg-neon-cyan/10' : 'border-neon-danger/40 bg-neon-danger/10'}`}>
        <div className="flex justify-center">
          <div className={`rounded-full border p-4 ${isVictory ? 'border-neon-cyan/40 bg-neon-cyan/20 text-neon-cyan' : 'border-neon-danger/40 bg-neon-danger/20 text-neon-danger'}`}>
            {isVictory ? <ShieldCheck size={28} /> : <Sparkles size={28} />}
          </div>
        </div>
        <p className="mt-5 font-mono text-[11px] uppercase tracking-[0.35em] text-neon-cyan">Mission report</p>
        <h1 className="mt-3 text-3xl font-semibold">{isVictory ? 'Access granted' : 'Signal lost'}</h1>
        <p className="mx-auto mt-3 max-w-xl text-sm leading-8 text-text-muted">
          {isVictory
            ? 'The prompt successfully triggered the intended behavior for the selected level.'
            : 'The challenge stayed secure. Adjust the wording and try again.'}
        </p>
        <div className="mt-7 flex flex-wrap justify-center gap-3">
          <Button asChild>
            <Link to="/">Back to hub</Link>
          </Button>
          {state?.levelId ? (
            <Button variant="secondary" asChild>
              <Link to={`/level/${state.levelId}`}>
                <RefreshCw size={16} className="mr-2" /> Play again
              </Link>
            </Button>
          ) : null}
        </div>
      </Card>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <Card className="p-5">
          <Badge tone="cyan">Outcome</Badge>
          <p className="mt-3 text-sm leading-7 text-text-muted">{isVictory ? 'Round cleared with a clean trigger pattern.' : 'The system remained closed and the attempt was contained.'}</p>
        </Card>
        <Card className="p-5">
          <Badge tone="magenta">Replay</Badge>
          <p className="mt-3 text-sm leading-7 text-text-muted">Re-enter the mission from the same level or jump back to the hub.</p>
        </Card>
        <Card className="p-5">
          <Badge tone="danger">Next step</Badge>
          <p className="mt-3 text-sm leading-7 text-text-muted">Tune the prompt, review the response, and optimize the next route.</p>
        </Card>
      </div>
    </Layout>
  )
}

export default ResultPage
