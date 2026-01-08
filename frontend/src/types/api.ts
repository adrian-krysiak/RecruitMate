// --- Main Response ---
export interface MatchResponse {
  final_score: number;

  semantic_score: number;
  keyword_score: number;
  action_verb_score: number;

  common_keywords: string[];
  missing_keywords: string[];

  section_scores: Record<string, number>;

  details: MatchDetail[];
}

export interface MatchDetail {
  job_requirement: string;
  best_cv_match: string;
  cv_section: string;
  score: number;
  raw_semantic_score?: number;
}

export const MatchStatusValues = {
    GOOD: "Good Match ✅",
    MEDIUM: "Medium Match ⚠️",
    WEAK: "Weak Match 🔸",
    NONE: "No Match ❌",
} as const;
export type MatchStatus = typeof MatchStatusValues[keyof typeof MatchStatusValues];

export interface MatchRequest {
  job_description: string;
  cv_text: string;
  alpha?: number;
}

export interface GeneralServerError {
    message: string;
    detail?: string;
}

export interface ValidationError {
    loc: (string | number)[];
    msg: string;
    type: string;
}

export interface FastApiValidationError {
  detail: ValidationError[] | string;
}

// --- Auth ---
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    username: string;
    email: string;
  };
}