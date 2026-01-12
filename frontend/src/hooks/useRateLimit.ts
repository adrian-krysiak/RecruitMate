import { useState, useEffect } from "react";
import { type RateLimitInfo } from "../utils/rateLimitManager";
import { subscribeToRateLimit } from "../api/axiosClient";

/**
 * Hook to monitor rate limit status
 * Returns current rate limit info if user is being rate limited
 */
export function useRateLimit(): RateLimitInfo | null {
  const [rateLimit, setRateLimit] = useState<RateLimitInfo | null>(null);

  useEffect(() => {
    const unsubscribe = subscribeToRateLimit((info) => {
      setRateLimit(info);
    });

    return unsubscribe;
  }, []);

  return rateLimit;
}
