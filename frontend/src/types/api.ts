export interface MatchResponse {
  final_score: number;
  sbert_score: number;
  tfidf_score: number;
  common_keywords: string[];
  details: MatchDetail[];
}

export interface MatchDetail {
  requirement_chunk: string;
  best_match_cv_chunk: string;
  score: number;
  status: MatchStatus;
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