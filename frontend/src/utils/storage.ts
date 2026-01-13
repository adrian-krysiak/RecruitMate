import { STORAGE_KEYS, SESSION_KEYS } from "../constants";

export class StorageService {
  // --- LocalStorage Methods ---
  static setItem<T>(key: string, value: T): void {
    try {
      const serializedValue = JSON.stringify(value);
      localStorage.setItem(key, serializedValue);
    } catch (error) {
      // Silently fail in production
    }
  }

  static getItem<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  }

  static getString(key: string): string | null {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  }

  static setString(key: string, value: string): void {
    try {
      localStorage.setItem(key, value);
    } catch {
      // Silently fail in production
    }
  }

  static removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch {
      // Silently fail in production
    }
  }

  static clear(): void {
    try {
      localStorage.clear();
    } catch {
      // Silently fail in production
    }
  }

  // --- SessionStorage Methods (for temporary/sensitive data) ---
  static setSessionItem<T>(key: string, value: T): void {
    try {
      const serializedValue = JSON.stringify(value);
      sessionStorage.setItem(key, serializedValue);
    } catch {
      // Silently fail in production
    }
  }

  static getSessionItem<T>(key: string): T | null {
    try {
      const item = sessionStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  }

  static getSessionString(key: string): string | null {
    try {
      return sessionStorage.getItem(key);
    } catch {
      return null;
    }
  }

  static setSessionString(key: string, value: string): void {
    try {
      sessionStorage.setItem(key, value);
    } catch {
      // Silently fail in production
    }
  }

  static removeSessionItem(key: string): void {
    try {
      sessionStorage.removeItem(key);
    } catch {
      // Silently fail in production
    }
  }

  static clearSession(): void {
    try {
      sessionStorage.clear();
    } catch {
      // Silently fail in production
    }
  }

  // --- Auth-specific helpers ---
  static clearAuthData(): void {
    this.removeItem(STORAGE_KEYS.TOKEN);
    this.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    this.removeItem(STORAGE_KEYS.USER);
  }

  // --- Scanner data helpers (uses sessionStorage) ---
  static clearScannerData(): void {
    this.removeSessionItem(SESSION_KEYS.SCANNER_CV_TEXT);
    this.removeSessionItem(SESSION_KEYS.SCANNER_JOB_DESC);
    this.removeSessionItem(SESSION_KEYS.SCANNER_RESULT);
  }

  // --- Full logout cleanup ---
  static clearAllUserData(): void {
    this.clearAuthData();
    this.clearScannerData();
  }
}
