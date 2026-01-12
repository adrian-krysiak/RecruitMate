import { axiosClient } from "../api/axiosClient";
import { type MatchRequest, type MatchResponse } from "../types/api";
import { API_ENDPOINTS } from "../constants";

export const analyzeMatch = async (
  payload: MatchRequest
): Promise<MatchResponse> => {
  const response = await axiosClient.post<MatchResponse>(
    API_ENDPOINTS.MATCH,
    payload
  );
  return response.data;
};
