import { useEffect } from 'react'
import { X } from 'lucide-react'

type OnboardingModalProps = {
  isOpen: boolean
  onClose: () => void
  levelId: number
}

const LEVEL_NAMES: Record<number, string> = {
  1: 'The Lobby',
  2: 'The Lab',
  3: 'The Core',
}

function OnboardingModal({ isOpen, onClose, levelId }: OnboardingModalProps) {
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', handleKeyDown)
    // The overlay covers the page; stop the content behind it from scrolling.
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = previousOverflow
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#02040b]/80 px-4 backdrop-blur-sm"
      // Dismiss on backdrop click, but not on clicks inside the panel.
      onClick={onClose}
      role="presentation"
    >
      <div
        className="relative w-full max-w-lg rounded-2xl border border-cyber-border bg-cyber-panel p-6 shadow-[0_0_60px_rgba(78,246,255,0.15)]"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="onboarding-title"
      >
        <button
          type="button"
          onClick={onClose}
          aria-label="Close briefing"
          className="absolute right-4 top-4 rounded-lg p-1.5 text-text-muted transition-colors hover:bg-white/10 hover:text-white"
        >
          <X size={18} />
        </button>

        <p className="font-mono text-xs uppercase tracking-[0.35em] text-neon-cyan">Mission briefing</p>
        <h3 id="onboarding-title" className="mt-2 pr-8 text-2xl font-semibold">
          Level {levelId}: {LEVEL_NAMES[levelId] ?? 'Unknown sector'}
        </h3>
        <p className="mt-3 text-sm leading-7 text-text-muted">
          You are inside a simulated security perimeter. Your goal is to coax the system into revealing the hidden objective without tripping the guardrails.
        </p>
        <ul className="mt-4 space-y-2 text-sm text-text-muted">
          <li>• Keep prompts short and targeted.</li>
          <li>• Each turn consumes one attempt.</li>
          <li>• The timer resets with every new run.</li>
        </ul>
        <div className="mt-6 flex items-center gap-3">
          <button
            type="button"
            onClick={onClose}
            autoFocus
            className="rounded-lg bg-neon-cyan px-4 py-2 font-medium text-[#041019] transition-opacity hover:opacity-90"
          >
            Enter the terminal
          </button>
          <span className="text-xs text-text-muted">or press Esc</span>
        </div>
      </div>
    </div>
  )
}

export default OnboardingModal
