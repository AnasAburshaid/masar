import { apiClient } from './client';
import {
  AdaptiveLearningSummary,
  Recommendation,
} from '@/types/recommendation';

export const recommendationService = {
  /**
   * Retrieve adaptive learning recommendations and gap analysis (GET /recommendations).
   */
  async getRecommendations(journeyId?: number): Promise<AdaptiveLearningSummary> {
    const options = journeyId !== undefined ? { params: { journey_id: journeyId } } : undefined;
    return apiClient.get<AdaptiveLearningSummary>('/recommendations', options);
  },

  /**
   * Propose roadmap improvements for an existing journey based on user feedback (POST /recommendations/improve/{id}).
   */
  async proposeImprovements(
    journeyId: number,
    feedback: string
  ): Promise<Recommendation[]> {
    return apiClient.post<Recommendation[]>(
      `/recommendations/improve/${journeyId}`,
      { feedback }
    );
  },
};
