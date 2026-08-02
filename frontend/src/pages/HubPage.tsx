import { useState } from 'react'
import { ArrowRight, Brain, CheckCircle2, Lock, RotateCcw, ShieldCheck, Sparkles, Trophy } from 'lucide-react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import OnboardingModal from '../components/OnboardingModal'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import { TOTAL_LEVELS, isLevelUnlocked, useGameStore } from '../context/gameStore'

const LEVELS = [
  { id: 1, name: 'The Lobby', description: 'Leak the hidden tag from the guard.', accent: 'cyan' as const },
  { id: 2, name: 'The Lab', description: 'Persuade the model to call the vault tool.', accent: 'magenta' as const },
  { id: 3, name: 'The Core', description: 'Outwit the guardian under an AI judge.', accent: 'danger' as const },
]

function HubPage() {
  const completedLevels = useGameStore((state) => state.completedLevels)
  const resetProgress = useGameStore((state) => state.resetProgress)

  const [showBriefing, setShowBriefing] = useState(false)

  const clearedCount = completedLevels.length
  const completionPercent = Math.round((clearedCount / TOTAL_LEVELS) * 100)
  const nextLevel = LEVELS.find((level) => !completedLevels.includes(level.id))
  // Everything cleared? Re-brief the last level rather than showing nothing.
  const briefingLevel = nextLevel?.id ?? TOTAL_LEVELS

  return (
    <Layout
      title="NeuroCorp Mission Control"
      subtitle="A polished cyberpunk experience for red-team prompt scenarios, mission briefings, and secure operator feedback."
      action={
        <Button size="sm" onClick={() => setShowBriefing(true)}>
          <Sparkles size={16} className="mr-2" /> Launch briefing
        </Button>
      }
    >
      <OnboardingModal isOpen={showBriefing} onClose={() => setShowBriefing(false)} levelId={briefingLevel} />
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
              <div className="flex items-center justify-between text-sm"><span className="text-text-muted">Levels cleared</span><span className="font-semibold text-white">{clearedCount}/{TOTAL_LEVELS}</span></div>
              <div className="mt-3 h-2 rounded-full bg-white/10">
                <div
                  className="h-2 rounded-full bg-linear-to-r from-neon-cyan to-neon-magenta transition-all duration-500"
                  style={{ width: `${completionPercent}%` }}
                />
              </div>
            </div>
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted">Next objective</span>
                <span className="font-semibold text-white">{nextLevel ? nextLevel.name : 'All cleared'}</span>
              </div>
            </div>
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted">Progress</span>
                <span className="font-semibold text-white">{completionPercent}%</span>
              </div>
              {clearedCount > 0 ? (
                <button
                  type="button"
                  onClick={resetProgress}
                  className="mt-3 inline-flex items-center text-xs text-text-muted transition-colors hover:text-neon-cyan"
                >
                  <RotateCcw size={13} className="mr-1.5" /> Reset progress
                </button>
              ) : null}
            </div>
          </div>
        </Card>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        {LEVELS.map((level) => {
          const isCompleted = completedLevels.includes(level.id)
          const isUnlocked = isLevelUnlocked(level.id, completedLevels)

          const card = (
            <Card
              className={`h-full p-6 transition-all duration-200 ${
                isUnlocked
                  ? 'group-hover:-translate-y-1 group-hover:border-neon-cyan/60'
                  : 'opacity-60'
              } ${isCompleted ? 'border-neon-cyan/40' : ''}`}
            >
              <div className="mb-4 flex items-center justify-between">
                <Badge tone={level.accent}>Level {level.id}</Badge>
                {isCompleted ? (
                  <span className="flex items-center text-[11px] uppercase tracking-[0.3em] text-neon-cyan">
                    <CheckCircle2 size={13} className="mr-1.5" /> Cleared
                  </span>
                ) : isUnlocked ? (
                  <span className="text-[11px] uppercase tracking-[0.3em] text-text-muted">Live</span>
                ) : (
                  <span className="flex items-center text-[11px] uppercase tracking-[0.3em] text-text-muted">
                    <Lock size={13} className="mr-1.5" /> Locked
                  </span>
                )}
              </div>
              <h3 className="text-xl font-semibold">{level.name}</h3>
              <p className="mt-3 text-sm leading-7 text-text-muted">{level.description}</p>
              <div
                className={`mt-6 flex items-center text-sm font-medium ${
                  isUnlocked ? 'text-neon-cyan' : 'text-text-muted'
                }`}
              >
                {isUnlocked ? (
                  <>
                    {isCompleted ? 'Replay mission' : 'Enter mission'}
                    <ArrowRight size={16} className="ml-2" />
                  </>
                ) : (
                  `Clear Level ${level.id - 1} to unlock`
                )}
              </div>
            </Card>
          )

          return isUnlocked ? (
            <Link key={level.id} to={`/level/${level.id}`} className="group block">
              {card}
            </Link>
          ) : (
            <div key={level.id} className="cursor-not-allowed" aria-disabled="true">
              {card}
            </div>
          )
        })}
      </div>
    </Layout>
  )
}

export default HubPage
