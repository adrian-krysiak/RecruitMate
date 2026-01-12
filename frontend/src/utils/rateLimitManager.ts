/**
 * Rate Limiting utility for handling API rate limit responses
 * Provides retry logic and user feedback for rate-limited requests
 */

export interface RateLimitInfo {
  remaining: number;
  limit: number;
  resetTime: number; // Unix timestamp
  retryAfter: number; // Seconds
}

export class RateLimitManager {
  private static readonly RATE_LIMIT_HEADERS = {
    LIMIT: "x-ratelimit-limit",
    REMAINING: "x-ratelimit-remaining",
    RESET: "x-ratelimit-reset",
    RETRY_AFTER: "retry-after",
  } as const;

  /**
   * Extract rate limit info from response headers
   */
  static extractRateLimitInfo(
    headers: Record<string, string | number | undefined>
  ): RateLimitInfo | null {
    const limit = parseInt(
      String(headers[this.RATE_LIMIT_HEADERS.LIMIT] || "0")
    );
    const remaining = parseInt(
      String(headers[this.RATE_LIMIT_HEADERS.REMAINING] || "0")
    );
    const resetTime = parseInt(
      String(headers[this.RATE_LIMIT_HEADERS.RESET] || "0")
    );
    const retryAfter = parseInt(
      String(headers[this.RATE_LIMIT_HEADERS.RETRY_AFTER] || "60")
    );

    if (!limit) return null;

    return { remaining, limit, resetTime, retryAfter };
  }

  /**
   * Check if request is rate limited (429 status)
   */
  static isRateLimited(status: number): boolean {
    return status === 429;
  }

  /**
   * Get human-readable wait message
   */
  static getWaitMessage(rateLimitInfo: RateLimitInfo): string {
    const retryInSeconds = Math.ceil(rateLimitInfo.retryAfter);
    const minutes = Math.ceil(retryInSeconds / 60);

    if (retryInSeconds < 60) {
      return `Rate limited. Please wait ${retryInSeconds} seconds.`;
    }
    return `Rate limited. Please wait ${minutes} minutes.`;
  }

  /**
   * Get time until rate limit reset (in seconds)
   */
  static getTimeUntilReset(resetTime: number): number {
    const now = Date.now() / 1000;
    return Math.max(0, Math.ceil(resetTime - now));
  }

  /**
   * Check if should retry based on rate limit
   */
  static shouldRetry(retryAttempt: number, maxRetries: number = 3): boolean {
    return retryAttempt < maxRetries;
  }

  /**
   * Calculate exponential backoff with jitter
   */
  static getBackoffDelay(
    retryAttempt: number,
    baseDelay: number = 1000
  ): number {
    const exponentialDelay = baseDelay * Math.pow(2, retryAttempt);
    const jitter = Math.random() * 0.1 * exponentialDelay;
    return Math.min(exponentialDelay + jitter, 30000); // Max 30 seconds
  }
}
