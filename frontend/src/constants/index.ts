// API Configuration
export const API_CONFIG = {
  TIMEOUT: 10000,
  BASE_URL: "/api",
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login/",
    REGISTER: "/auth/register/",
    LOGOUT: "/auth/logout/",
    REFRESH: "/auth/token/refresh/",
  },
  MATCH: "/match",
} as const;

// LocalStorage Keys
export const STORAGE_KEYS = {
  TOKEN: "token",
  REFRESH_TOKEN: "refresh_token",
  USER: "user",
  THEME: "theme",
  SCANNER_INPUT_MODE: "guestScannerInputMode",
} as const;

// Theme Configuration
export const THEME = {
  LIGHT: "light",
  DARK: "dark",
} as const;

// Match Analysis
export const MATCH_CONFIG = {
  DEFAULT_ALPHA: 0.7,
  MIN_CV_LENGTH: 50,
  MIN_JOB_DESC_LENGTH: 50,
  MIN_PASSWORD_LENGTH: 8,
} as const;

// Score Thresholds
export const SCORE_THRESHOLDS = {
  GOOD: 0.7,
  MEDIUM: 0.4,
  WEAK: 0.0,
} as const;

// HTTP Status Codes
export const HTTP_STATUS = {
  UNAUTHORIZED: 401,
  UNPROCESSABLE_ENTITY: 422,
} as const;

// File Upload Configuration
export const FILE_UPLOAD = {
  ACCEPTED_FORMATS: ".pdf,.docx,.txt",
  ACCEPTED_MIME_TYPES: [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
  ],
} as const;
