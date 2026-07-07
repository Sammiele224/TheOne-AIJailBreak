import type { PromptRequest, GameResponse } from "../types/game";

const API_BASE_URL = "http://localhost:8000/api/v1/game";

export async function submitUserPrompt(payload: PromptRequest): Promise<GameResponse> {
  const response = await fetch(`${API_BASE_URL}/submit-prompt`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  // Assign to a variable first to avoid the ESLint "redundant return-await" error:
  const data: GameResponse = await response.json();
  return data;
}