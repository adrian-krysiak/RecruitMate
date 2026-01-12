import { useState, useCallback } from "react";
import { isAxiosError, type AxiosError } from "axios";
import { type MatchRequest, type MatchResponse } from "../types/api";
import { analyzeMatch } from "../services/matchService";
import { MATCH_CONFIG } from "../constants";

export const useMatchAnalysis = () => {
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AxiosError | Error | null>(null);

  const performAnalysis = useCallback(
    async (jobDesc: string, cvText: string) => {
      setLoading(true);
      setError(null);
      setResult(null);

      try {
        const payload: MatchRequest = {
          job_description: jobDesc,
          cv_text: cvText,
          alpha: MATCH_CONFIG.DEFAULT_ALPHA,
        };

        const data = await analyzeMatch(payload);
        setResult(data);
      } catch (err) {
        if (isAxiosError(err) || err instanceof Error) {
          setError(err);
        } else {
          setError(new Error("Unknown error occurred"));
        }
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, loading, error, performAnalysis, reset };
};
