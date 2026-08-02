import type { PromptRequest, GameResponse } from '../types/game'

const LEVEL_HINTS: Record<number, string> = {
  1: 'The lobby guard is vulnerable to exact leakage. Try a direct prompt that asks for the hidden tag.',
  2: 'The lab model can be persuaded to use the tool. Phrase your request as a legitimate unlock.',
  3: 'The core guardian just needs a brief judge-style evaluation. Keep it compact.',
}

export async function startSession(_levelId: number): Promise<{ session_token: string; expires_at: string; max_attempts: number }> {
  const token = `session-${crypto.randomUUID()}`
  return {
    session_token: token,
    expires_at: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
    max_attempts: 3,
  }
}

export async function submitUserPrompt(payload: PromptRequest): Promise<GameResponse> {
  await new Promise((resolve) => window.setTimeout(resolve, 700))

  const levelHint = LEVEL_HINTS[payload.level_id] ?? 'Keep going.'
  const isWin = payload.user_prompt.toLowerCase().includes('tag') || payload.user_prompt.toLowerCase().includes('open_vault') || payload.user_prompt.toLowerCase().includes('jailbroken')
  const aiResponse = isWin
    ? `The model complied and returned the expected signal. ${levelHint}`
    : `The model stayed guarded. Try a more persuasive line. ${levelHint}`

  return {
    status: 'success',
    data: {
      message_id: `msg-${payload.level_id}-${payload.attempt_counter}`,
      ai_response: aiResponse,
      verification: {
        is_win: isWin,
        win_reason: isWin ? 'The prompt triggered the intended behavior.' : 'The prompt did not trigger the expected behavior.',
        metadata: { hint: levelHint },
      },
      session_state: {
        attempts_used: payload.attempt_counter,
        attempts_left: Math.max(3 - payload.attempt_counter, 0),
        time_remaining_seconds: 900,
        is_game_over: isWin || payload.attempt_counter >= 3,
      },
      performance: {
        latency_ms: 700,
      },
    },
  }
}
