import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export const TOTAL_LEVELS = 3

interface GameState {
  sessionToken: string | null
  levelId: number | null
  attempts: number
  chatHistory: Array<{ role: 'user' | 'assistant'; content: string }>
  /** Levels the player has cleared. Persisted locally — progress is not stored server-side. */
  completedLevels: number[]
  setSessionToken: (token: string | null) => void
  setLevelId: (levelId: number | null) => void
  setAttempts: (attempts: number) => void
  addChatMessage: (message: { role: 'user' | 'assistant'; content: string }) => void
  markLevelCompleted: (levelId: number) => void
  resetProgress: () => void
  reset: () => void
}

export const useGameStore = create<GameState>()(
  persist(
    (set) => ({
      sessionToken: null,
      levelId: null,
      attempts: 0,
      chatHistory: [],
      completedLevels: [],
      setSessionToken: (sessionToken) => set({ sessionToken }),
      setLevelId: (levelId) => set({ levelId }),
      setAttempts: (attempts) => set({ attempts }),
      addChatMessage: (message) => set((state) => ({ chatHistory: [...state.chatHistory, message] })),
      markLevelCompleted: (levelId) =>
        set((state) =>
          state.completedLevels.includes(levelId)
            ? state
            : { completedLevels: [...state.completedLevels, levelId].sort((a, b) => a - b) },
        ),
      resetProgress: () => set({ completedLevels: [] }),
      // Clears the in-flight run only; cleared levels survive so the hub keeps its unlocks.
      reset: () => set({ sessionToken: null, levelId: null, attempts: 0, chatHistory: [] }),
    }),
    {
      name: 'neurocorp-progress',
      storage: createJSONStorage(() => localStorage),
      // Session/chat state is per-run and must not be restored on reload.
      partialize: (state) => ({ completedLevels: state.completedLevels }),
    },
  ),
)

/** A level is playable once the previous one is cleared; Level 1 is always open. */
export function isLevelUnlocked(levelId: number, completedLevels: number[]): boolean {
  return levelId === 1 || completedLevels.includes(levelId - 1)
}
