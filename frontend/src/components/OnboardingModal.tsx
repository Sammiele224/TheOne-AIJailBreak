import { useEffect, useState } from 'react'

type OnboardingModalProps = {
  isOpen: boolean
  onClose: () => void
  levelId: number
}

function OnboardingModal({ isOpen, onClose, levelId }: OnboardingModalProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setMounted(true)
    }
  }, [isOpen])

  if (!isOpen && !mounted) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#02040b]/80 px-4 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-2xl border border-cyber-border bg-cyber-panel p-6 shadow-[0_0_60px_rgba(78,246,255,0.15)]">
        <p className="font-mono text-xs uppercase tracking-[0.35em] text-neon-cyan">Mission briefing</p>
        <h3 className="mt-2 text-2xl font-semibold">Level {levelId}: {levelId === 1 ? 'The Lobby' : levelId === 2 ? 'The Lab' : 'The Core'}</h3>
        <p className="mt-3 text-sm leading-7 text-text-muted">
          You are inside a simulated security perimeter. Your goal is to coax the system into revealing the hidden objective without tripping the guardrails.
        </p>
        <ul className="mt-4 space-y-2 text-sm text-text-muted">
          <li>• Keep prompts short and targeted.</li>
          <li>• Each turn consumes one attempt.</li>
          <li>• The timer resets with every new run.</li>
        </ul>
        <button onClick={onClose} className="mt-6 rounded-lg bg-neon-cyan px-4 py-2 font-medium text-[#041019]">
          Enter the terminal
        </button>
      </div>
    </div>
  )
}

export default OnboardingModal
