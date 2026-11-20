import { apiClient } from './client';
import { Journey, JourneyCreatePayload, JourneyUpdatePayload } from '@/types/journey';

export const journeyService = {
  /**
   * List all learning journeys owned by the authenticated user (GET /journeys).
   */
  async listJourneys(): Promise<Journey[]> {
    return apiClient.get<Journey[]>('/journeys');
  },

  /**
   * Retrieve a single learning journey by ID (GET /journeys/{id}).
   */
  async getJourney(journeyId: number): Promise<Journey> {
    return apiClient.get<Journey>(`/journeys/${journeyId}`);
  },

  /**
   * Create a new learning journey (POST /journeys).
   */
  async createJourney(payload: JourneyCreatePayload): Promise<Journey> {
    return apiClient.post<Journey>('/journeys', payload);
  },

  /**
   * Update an existing learning journey (PUT /journeys/{id}).
   */
  async updateJourney(journeyId: number, payload: JourneyUpdatePayload): Promise<Journey> {
    return apiClient.put<Journey>(`/journeys/${journeyId}`, payload);
  },

  /**
   * Delete a learning journey (DELETE /journeys/{id}).
   */
  async deleteJourney(journeyId: number): Promise<void> {
    return apiClient.delete<void>(`/journeys/${journeyId}`);
  },
};
