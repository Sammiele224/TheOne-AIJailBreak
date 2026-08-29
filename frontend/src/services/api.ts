import type { PromptRequest, GameResponse } from '../types/game'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1/game'
const API_KEY = import.meta.env.VITE_API_KEY ?? ''

function buildHeaders() {
  return {
    'Content-Type': 'application/json',
    ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
  }
}

export async function startSession(levelId: number): Promise<{ session_token: string; expires_at: string; max_attempts: number }> {
  const response = await fetch(`${API_BASE_URL}/start-game`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({ level_id: levelId }),
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`API Error: ${response.status} ${detail || response.statusText}`)
  }

  return response.json()
}

export async function submitUserPrompt(payload: PromptRequest): Promise<GameResponse> {
  const response = await fetch(`${API_BASE_URL}/submit-prompt`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`API Error: ${response.status} ${detail || response.statusText}`)
  }

  return response.json() as Promise<GameResponse>
}