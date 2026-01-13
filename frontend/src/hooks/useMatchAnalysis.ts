import { useState, useCallback, useRef, useEffect } from "react";
import { type AxiosError } from "axios";
import { type MatchRequest, type MatchResponse } from "../types/api";
import { analyzeMatch } from "../services/matchService";
import { MATCH_CONFIG, SESSION_KEYS } from "../constants";
import { StorageService } from "../utils/storage";
import { toError } from "../utils/errorHandler";

export const useMatchAnalysis = () => {
  // Load persisted result from sessionStorage
  const [result, setResult] = useState<MatchResponse | null>(() => {
    return StorageService.getSessionItem<MatchResponse>(SESSION_KEYS.SCANNER_RESULT);
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AxiosError | Error | null>(null);

  // AbortController ref for request cancellation
  const abortControllerRef = useRef<AbortController | null>(null);

  // Persist result to sessionStorage when it changes
  useEffect(() => {
    if (result) {
      StorageService.setSessionItem(SESSION_KEYS.SCANNER_RESULT, result);
    } else {
      StorageService.removeSessionItem(SESSION_KEYS.SCANNER_RESULT);
    }
  }, [result]);

  const performAnalysis = useCallback(
    async (jobDesc: string, cvText: string) => {
      // Cancel any in-flight request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new AbortController for this request
      abortControllerRef.current = new AbortController();

      setLoading(true);
      setError(null);
      setResult(null);

      try {
        const payload: MatchRequest = {
          job_description: jobDesc,
          cv_text: cvText,
          alpha: MATCH_CONFIG.DEFAULT_ALPHA,
        };

        const data = await analyzeMatch(payload, abortControllerRef.current.signal);
        setResult(data);
      } catch (err) {
        // Ignore abort errors
        if (err instanceof Error && err.name === 'CanceledError') {
          return;
        }
        setError(toError(err));
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setResult(null);
    setError(null);
    StorageService.removeSessionItem(SESSION_KEYS.SCANNER_RESULT);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { result, loading, error, performAnalysis, reset };
};
