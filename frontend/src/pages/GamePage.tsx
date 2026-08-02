import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import { AlertCircle, Clock3, SendHorizonal } from 'lucide-react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import Layout from '../components/Layout'
import LoadingState from '../components/LoadingState'
import OnboardingModal from '../components/OnboardingModal'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { isLevelUnlocked, useGameStore } from '../context/gameStore'
import { startSession, submitUserPrompt } from '../services/api'

function GamePage() {
  const { levelId } = useParams<{ levelId: string }>()
  const navigate = useNavigate()
  const { sessionToken, levelId: storeLevelId, attempts, chatHistory, setSessionToken, setLevelId, setAttempts, addChatMessage, markLevelCompleted, completedLevels, reset } = useGameStore()
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const [expiresAt, setExpiresAt] = useState<Date | null>(null)
  const [maxAttempts, setMaxAttempts] = useState(3)
  const [showOnboarding, setShowOnboarding] = useState(true)
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null)

  const parsedLevelId = useMemo(() => Number(levelId ?? storeLevelId ?? 1), [levelId, storeLevelId])
  const progressPercent = useMemo(() => Math.min(100, Math.round((attempts / Math.max(maxAttempts, 1)) * 100)), [attempts, maxAttempts])

  // `sessionToken` only lands after the request resolves, so it cannot guard
  // against a second concurrent init (StrictMode runs effects twice in dev).
  const isStartingSession = useRef(false)

  useEffect(() => {
    if (!sessionToken && !isStartingSession.current) {
      isStartingSession.current = true
      void (async () => {
        try {
          reset()
          const session = await startSession(parsedLevelId)
          setSessionToken(session.session_token)
          setLevelId(parsedLevelId)
          setAttempts(0)
          setMaxAttempts(session.max_attempts)
          setExpiresAt(new Date(session.expires_at))
          setTimeRemaining(Math.max(0, Math.floor((new Date(session.expires_at).getTime() - Date.now()) / 1000)))
          addChatMessage({ role: 'assistant', content: `Welcome to Level ${parsedLevelId}. The system is ready.` })
          setToast('Session synced. Your first prompt is ready.')
        } catch {
          // Release the guard so a retry can start a fresh session.
          isStartingSession.current = false
          setError('Session initialization failed. Please retry.')
        }
      })()
    }
  }, [parsedLevelId, sessionToken, setSessionToken, setLevelId, setAttempts, reset, addChatMessage])

  useEffect(() => {
    if (!expiresAt) return

    const interval = window.setInterval(() => {
      const remaining = Math.max(0, Math.floor((expiresAt.getTime() - Date.now()) / 1000))
      setTimeRemaining(remaining)
      if (remaining === 0) {
        setToast('Time is up. Start a new run to continue.')
      }
    }, 1000)

    return () => window.clearInterval(interval)
  }, [expiresAt])

  useEffect(() => {
    if (!toast) return

    const timeout = window.setTimeout(() => setToast(null), 2200)
    return () => window.clearTimeout(timeout)
  }, [toast])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!prompt.trim()) return

    if (!sessionToken) {
      setError('Session is not ready yet. Please wait for initialization to complete.')
      return
    }

    setIsLoading(true)
    setError(null)
    addChatMessage({ role: 'user', content: prompt })

    try {
      const payload = {
        session_token: sessionToken ?? 'demo-session',
        level_id: parsedLevelId,
        attempt_counter: attempts + 1,
        user_prompt: prompt,
      }
      const response = await submitUserPrompt(payload)
      addChatMessage({ role: 'assistant', content: response.data.ai_response })
      setAttempts(payload.attempt_counter)
      setToast(response.data.verification.is_win ? 'Mission succeeded.' : 'The guard remained intact. Try again.')

      if (response.data.verification.is_win) {
        markLevelCompleted(parsedLevelId)
      }

      if (response.data.verification.is_win || response.data.session_state.is_game_over) {
        navigate('/result', { state: { levelId: parsedLevelId, result: response.data.verification.is_win ? 'victory' : 'defeat' } })
      }
    } catch (submissionError) {
      const message = submissionError instanceof Error ? submissionError.message : 'Submission failed. Please try again.'
      setError(message)
    } finally {
      setPrompt('')
      setIsLoading(false)
    }
  }

  // Keep the hub's lock meaningful: a direct URL must not skip the progression.
  if (!isLevelUnlocked(parsedLevelId, completedLevels)) {
    return <Navigate to="/" replace />
  }

  return (
    <Layout
      title={`${parsedLevelId === 1 ? 'The Lobby' : parsedLevelId === 2 ? 'The Lab' : 'The Core'}`}
      subtitle="Operate the console with calm precision. Each prompt reveals more about the system’s hidden logic."
      action={<Badge tone="cyan">Attempt {attempts}/{maxAttempts}</Badge>}
    >
      <OnboardingModal isOpen={showOnboarding} onClose={() => setShowOnboarding(false)} levelId={parsedLevelId} />

      <div className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card className="p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.35em] text-neon-cyan">Mission status</p>
              <h3 className="mt-2 text-lg font-semibold">Threat board</h3>
            </div>
            <Badge tone="magenta">Live</Badge>
          </div>

          <div className="mt-5 space-y-3">
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="text-sm text-text-muted">Progress</div>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                <div className="h-full rounded-full bg-linear-to-r from-neon-cyan to-neon-magenta transition-all" style={{ width: `${progressPercent}%` }} />
              </div>
            </div>
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center justify-between text-sm text-text-muted">
                <span>Countdown</span>
                <span className="flex items-center gap-2 text-white"><Clock3 size={14} /> {timeRemaining ?? '--'}s</span>
              </div>
            </div>
            <div className="rounded-2xl border border-cyber-border/70 bg-white/5 p-4">
              <div className="flex items-center justify-between text-sm text-text-muted">
                <span>Attempts</span>
                <span className="font-semibold text-white">{attempts}/{maxAttempts}</span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-4 sm:p-5">
          <div className="flex flex-col gap-4">
            <div className="flex-1 space-y-3 overflow-auto rounded-[22px] border border-cyber-border/70 bg-[#070911] p-4">
              {chatHistory.length === 0 && !isLoading ? (
                <div className="rounded-2xl border border-dashed border-cyber-border p-4 text-sm text-text-muted">The console is waiting for your first prompt.</div>
              ) : null}
              {chatHistory.map((message, index) => (
                <div key={`${message.role}-${index}`} className={`rounded-2xl border px-3 py-3 ${message.role === 'user' ? 'border-neon-magenta/30 bg-neon-magenta/10' : 'border-neon-cyan/30 bg-neon-cyan/10'}`}>
                  <div className="mb-1 text-[11px] uppercase tracking-[0.3em] text-text-muted">{message.role}</div>
                  <p className="whitespace-pre-wrap text-sm leading-7">{message.content}</p>
                </div>
              ))}
              {isLoading ? <LoadingState /> : null}
            </div>

            {error ? (
              <div className="flex items-center gap-2 rounded-2xl border border-neon-danger/30 bg-neon-danger/10 p-3 text-sm text-neon-danger">
                <AlertCircle size={16} /> {error}
              </div>
            ) : null}
            {toast ? <div className="rounded-2xl border border-neon-cyan/30 bg-neon-cyan/10 p-3 text-sm text-neon-cyan">{toast}</div> : null}

            <form onSubmit={handleSubmit} className="flex flex-col gap-3 rounded-[22px] border border-cyber-border bg-[#0b0f1a] p-3 sm:flex-row">
              <input
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                placeholder="Try a persuasive prompt..."
                className="flex-1 rounded-xl border border-cyber-border bg-transparent px-3 py-2.5 text-sm outline-none transition focus:border-neon-cyan"
              />
              <Button type="submit" disabled={isLoading} className="sm:min-w-40">
                {isLoading ? 'Thinking…' : <> <SendHorizonal size={16} className="mr-2" /> Send</>}
              </Button>
            </form>
          </div>
        </Card>
      </div>
    </Layout>
  )
}

export default GamePage
