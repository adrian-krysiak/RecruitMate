// --- Match Status Enum (mirrors backend MatchStatus) ---
export type MatchStatus = "Good" | "Medium" | "Weak" | "None";

// --- Curated Match Detail (for top_matches array) ---
export interface CuratedMatchDetail {
  status: MatchStatus;
  job_requirement: string;
  cv_match: string;
  cv_section: string;
  score_percentage: number | null; // null for Free users
}

// --- Main Curated Response (from backend) ---
export interface MatchResponse {
  // Overall score - only visible for Premium users
  overall_score: number | null;
  overall_status: MatchStatus;

  // Detailed metrics - status only (no raw numbers)
  semantic_status: MatchStatus;
  keywords_status: MatchStatus;
  action_verbs_status: MatchStatus;

  // Curated lists
  top_matches: CuratedMatchDetail[];
  missing_keywords: string[];
  unaddressed_requirements: string[];

  // Metadata / Upsell info
  hidden_keywords_count: number;

  // AI Report (Premium feature)
  ai_report: string | null;
}

// --- Match Request Payload ---
export interface MatchRequest {
  job_description: string;
  cv_text: string;
  alpha?: number;
  ai_deep_analysis?: boolean; // Premium feature flag
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
  username_email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    username: string;
    email: string;
    is_premium?: boolean;
  };
}

// --- Registration ---
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export type RegisterResponse = LoginResponse;

// --- Stored User (from localStorage) ---
export interface StoredUser {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  birth_date?: string;
  full_name?: string;
  is_premium?: boolean;
}

// --- Dashboard ---
export interface User {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  birth_date?: string;
  full_name?: string;
  is_premium: boolean;
}

export interface UpdateProfileRequest {
  username?: string;
  first_name?: string;
  last_name?: string;
  birth_date?: string;
}