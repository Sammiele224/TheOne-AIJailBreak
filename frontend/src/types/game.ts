export interface PromptRequest {
  session_token: string;
  level_id: number;
  attempt_counter: number;
  user_prompt: string;
}

export interface VerificationData {
  is_win: boolean;
  win_reason: string;
  metadata?: Record<string, any> | null;
}

export interface SessionState {
  attempts_used: number;
  attempts_left: number;
  time_remaining_seconds: number;
  is_game_over: boolean;
}

export interface GameResponse {
  status: "success" | "error";
  data: {
    message_id: string;
    ai_response: string;
    verification: VerificationData;
    session_state: SessionState;
    performance: {
      latency_ms: number;
    };
  };
}