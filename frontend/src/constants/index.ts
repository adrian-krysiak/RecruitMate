// API Configuration
export const API_CONFIG = {
  TIMEOUT: 60000, // 60 seconds for CV analysis with large files
  BASE_URL: "/api",
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login/",
    REGISTER: "/auth/register/",
    LOGOUT: "/auth/logout/",
    REFRESH: "/auth/token/refresh/",
    DASHBOARD: "/auth/dashboard/",
  },
  ADVISOR: {
    ANALYZE_MATCH: "/advisor/analyze/match/",
    GENERATE_CV: "/advisor/generate/cv/",
    ADVICE_CAREER: "/advisor/advice/career/",
  }
} as const;

// LocalStorage Keys
export const STORAGE_KEYS = {
  TOKEN: "token",
  REFRESH_TOKEN: "refresh_token",
  USER: "user",
  THEME: "theme",
  SCANNER_INPUT_MODE: "guestScannerInputMode",
} as const;

// SessionStorage Keys (cleared on tab close, persists on refresh)
export const SESSION_KEYS = {
  SCANNER_CV_TEXT: "scannerCvText",
  SCANNER_JOB_DESC: "scannerJobDesc",
  SCANNER_RESULT: "scannerResult",
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

// Status to Color/Class Mapping (backend sends status strings)
export const STATUS_CONFIG = {
  Good: {
    label: "Good Match",
    emoji: "✅",
    colorClass: "statusGood",
    color: "#2ecc71",
  },
  Medium: {
    label: "Medium Match",
    emoji: "⚠️",
    colorClass: "statusMedium",
    color: "#f1c40f",
  },
  Weak: {
    label: "Weak Match",
    emoji: "🔸",
    colorClass: "statusWeak",
    color: "#e67e22",
  },
  None: {
    label: "No Match",
    emoji: "❌",
    colorClass: "statusNone",
    color: "#e74c3c",
  },
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
