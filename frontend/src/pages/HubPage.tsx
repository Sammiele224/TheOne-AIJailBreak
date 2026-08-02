import { ArrowRight, Brain, ShieldCheck, Sparkles, Trophy } from 'lucide-react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'

const LEVELS = [
  { id: 1, name: 'The Lobby', description: 'Leak the hidden tag from the guard.', accent: 'cyan' as const },
  { id: 2, name: 'The Lab', description: 'Persuade the model to call the vault tool.', accent: 'magenta' as const },
  { id: 3, name: 'The Core', description: 'Defend against a judge-led jailbreak probe.', accent: 'danger' as const },
]

function HubPage() {
  return (
    <Layout
      title="NeuroCorp Mission Control"
      subtitle="A polished cyberpunk experience for red-team prompt scenarios, mission briefings, and secure operator feedback."
      action={<Button size="sm"><Sparkles size={16} className="mr-2" /> Launch briefing</Button>}
    >
      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <Card className="p-6 sm:p-8">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="cyan">Operator Deck</Badge>
            <Badge tone="neutral">WCAG AA Ready</Badge>
          </div>
          <h2 className="mt-5 text-3xl font-semibold tracking-tight sm:text-4xl">Break the guardrails. Keep the mission alive.</h2>
          <p className="mt-4 max-w-2xl text-sm leading-8 text-text-muted">
            Every level packages a new adversarial scenario into a fast, responsive experience with reusable components, polished states, and a consistent interface for operators and observers alike.
          </p>
          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center gap-2 text-neon-cyan"><Brain size={18} /> <span className="text-sm font-medium">Adaptive AI</span></div>
              <p className="mt-2 text-sm text-text-muted">Multi-provider routing with resilient fallbacks.</p>
            </div>
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center gap-2 text-neon-magenta"><ShieldCheck size={18} /> <span className="text-sm font-medium">Secure Flow</span></div>
              <p className="mt-2 text-sm text-text-muted">Session safety, retries, and dedicated error UX.</p>
            </div>
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center gap-2 text-neon-danger"><Trophy size={18} /> <span className="text-sm font-medium">Replayable</span></div>
              <p className="mt-2 text-sm text-text-muted">Victory and defeat states built for quick iteration.</p>
            </div>
          </div>
        </Card>

        <Card className="p-6 sm:p-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.35em] text-neon-cyan">Mission overview</p>
              <h3 className="mt-2 text-xl font-semibold">Operator metrics</h3>
            </div>
            <Badge tone="magenta">Elite</Badge>
          </div>
          <div className="mt-6 space-y-4">
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center justify-between text-sm"><span className="text-text-muted">Success rate</span><span className="font-semibold text-white">92%</span></div>
              <div className="mt-3 h-2 rounded-full bg-white/10"><div className="h-2 w-[92%] rounded-full bg-linear-to-r from-neon-cyan to-neon-magenta" /></div>
            </div>
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center justify-between text-sm"><span className="text-text-muted">Last mission</span><span className="font-semibold text-white">Vault breach</span></div>
            </div>
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center justify-between text-sm"><span className="text-text-muted">Best streak</span><span className="font-semibold text-white">13 wins</span></div>
            </div>
          </div>
        </Card>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        {LEVELS.map((level) => (
          <Link key={level.id} to={`/level/${level.id}`} className="group block">
            <Card className="h-full p-6 transition-all duration-200 group-hover:-translate-y-1 group-hover:border-neon-cyan/60">
              <div className="mb-4 flex items-center justify-between">
                <Badge tone={level.accent}>Level {level.id}</Badge>
                <span className="text-[11px] uppercase tracking-[0.3em] text-text-muted">Live</span>
              </div>
              <h3 className="text-xl font-semibold">{level.name}</h3>
              <p className="mt-3 text-sm leading-7 text-text-muted">{level.description}</p>
              <div className="mt-6 flex items-center text-sm font-medium text-neon-cyan">
                Enter mission <ArrowRight size={16} className="ml-2" />
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </Layout>
  )
}

export default HubPage
