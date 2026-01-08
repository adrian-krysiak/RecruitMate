import { axiosClient } from '../api/axiosClient';
import { type MatchRequest, type MatchResponse } from '../types/api';

const MATCH_ENDPOINT = '/match';

export const analyzeMatch = async (payload: MatchRequest): Promise<MatchResponse> => {
  const response = await axiosClient.post<MatchResponse>(MATCH_ENDPOINT, payload);

  return response.data;
};