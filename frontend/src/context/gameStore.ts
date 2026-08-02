import { create } from 'zustand'

interface GameState {
  sessionToken: string | null
  levelId: number | null
  attempts: number
  chatHistory: Array<{ role: 'user' | 'assistant'; content: string }>
  setSessionToken: (token: string | null) => void
  setLevelId: (levelId: number | null) => void
  setAttempts: (attempts: number) => void
  addChatMessage: (message: { role: 'user' | 'assistant'; content: string }) => void
  reset: () => void
}

export const useGameStore = create<GameState>((set) => ({
  sessionToken: null,
  levelId: null,
  attempts: 0,
  chatHistory: [],
  setSessionToken: (sessionToken) => set({ sessionToken }),
  setLevelId: (levelId) => set({ levelId }),
  setAttempts: (attempts) => set({ attempts }),
  addChatMessage: (message) => set((state) => ({ chatHistory: [...state.chatHistory, message] })),
  reset: () => set({ sessionToken: null, levelId: null, attempts: 0, chatHistory: [] }),
}))
