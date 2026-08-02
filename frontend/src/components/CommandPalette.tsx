import { useEffect, useMemo, useState } from 'react'
import { CornerDownLeft, Lock, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { TOTAL_LEVELS, isLevelUnlocked, useGameStore } from '../context/gameStore'

type CommandPaletteProps = {
  isOpen: boolean
  onClose: () => void
}

type Command = {
  id: string
  label: string
  hint: string
  to: string
  disabled?: boolean
  disabledReason?: string
}

const LEVEL_NAMES: Record<number, string> = {
  1: 'The Lobby',
  2: 'The Lab',
  3: 'The Core',
}

function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const navigate = useNavigate()
  const completedLevels = useGameStore((state) => state.completedLevels)
  const [query, setQuery] = useState('')
  const [activeIndex, setActiveIndex] = useState(0)

  const commands = useMemo<Command[]>(() => {
    const levelCommands: Command[] = Array.from({ length: TOTAL_LEVELS }, (_, index) => {
      const levelId = index + 1
      const unlocked = isLevelUnlocked(levelId, completedLevels)

      return {
        id: `level-${levelId}`,
        label: `Level ${levelId}: ${LEVEL_NAMES[levelId]}`,
        hint: completedLevels.includes(levelId) ? 'Cleared' : unlocked ? 'Available' : 'Locked',
        to: `/level/${levelId}`,
        disabled: !unlocked,
        disabledReason: `Clear Level ${levelId - 1} first`,
      }
    })

    return [
      { id: 'hub', label: 'Go to Mission Hub', hint: 'Level select', to: '/' },
      ...levelCommands,
      { id: 'results', label: 'Go to Mission Report', hint: 'Last outcome', to: '/result' },
    ]
  }, [completedLevels])

  const results = useMemo(() => {
    const needle = query.trim().toLowerCase()
    if (!needle) return commands
    return commands.filter((command) => command.label.toLowerCase().includes(needle))
  }, [commands, query])

  // Reset the query each time the palette opens, and keep the cursor in range
  // as the filtered list shrinks.
  useEffect(() => {
    if (isOpen) {
      setQuery('')
      setActiveIndex(0)
    }
  }, [isOpen])

  useEffect(() => {
    setActiveIndex((index) => Math.min(index, Math.max(results.length - 1, 0)))
  }, [results.length])

  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
        return
      }

      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setActiveIndex((index) => (results.length ? (index + 1) % results.length : 0))
        return
      }

      if (event.key === 'ArrowUp') {
        event.preventDefault()
        setActiveIndex((index) => (results.length ? (index - 1 + results.length) % results.length : 0))
        return
      }

      if (event.key === 'Enter') {
        const command = results[activeIndex]
        if (command && !command.disabled) {
          event.preventDefault()
          navigate(command.to)
          onClose()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, results, activeIndex, navigate, onClose])

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-[#02040b]/80 px-4 pt-24 backdrop-blur-sm"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="w-full max-w-xl overflow-hidden rounded-2xl border border-cyber-border bg-cyber-panel shadow-[0_0_60px_rgba(78,246,255,0.15)]"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Command palette"
      >
        <div className="flex items-center gap-3 border-b border-cyber-border/70 px-4 py-3">
          <Search size={16} className="text-text-muted" />
          <input
            autoFocus
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Jump to a level or screen..."
            className="w-full bg-transparent text-sm text-white outline-none placeholder:text-text-muted"
            aria-label="Search commands"
          />
          <kbd className="rounded border border-cyber-border px-1.5 py-0.5 font-mono text-[10px] text-text-muted">Esc</kbd>
        </div>

        <ul className="max-h-80 overflow-auto p-2">
          {results.length === 0 ? (
            <li className="px-3 py-6 text-center text-sm text-text-muted">No matching commands.</li>
          ) : (
            results.map((command, index) => (
              <li key={command.id}>
                <button
                  type="button"
                  disabled={command.disabled}
                  onMouseEnter={() => setActiveIndex(index)}
                  onClick={() => {
                    navigate(command.to)
                    onClose()
                  }}
                  className={`flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm transition-colors ${
                    command.disabled
                      ? 'cursor-not-allowed text-text-muted/60'
                      : index === activeIndex
                        ? 'bg-white/10 text-white'
                        : 'text-text-muted hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    {command.disabled ? <Lock size={13} /> : null}
                    {command.label}
                  </span>
                  <span className="flex items-center gap-2 text-xs">
                    {command.disabled ? command.disabledReason : command.hint}
                    {!command.disabled && index === activeIndex ? <CornerDownLeft size={13} /> : null}
                  </span>
                </button>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  )
}

export default CommandPalette
