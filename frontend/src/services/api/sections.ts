import { apiClient } from './client';
import { Section, SectionCreatePayload, SectionUpdatePayload } from '@/types/journey';

export const sectionService = {
  /**
   * List all sections belonging to a journey (GET /journeys/{journeyId}/sections).
   */
  async listSections(journeyId: number): Promise<Section[]> {
    return apiClient.get<Section[]>(`/journeys/${journeyId}/sections`);
  },

  /**
   * Get a section by ID (GET /sections/{id}).
   */
  async getSection(sectionId: number): Promise<Section> {
    return apiClient.get<Section>(`/sections/${sectionId}`);
  },

  /**
   * Create a new section within a journey (POST /sections).
   */
  async createSection(payload: SectionCreatePayload): Promise<Section> {
    return apiClient.post<Section>('/sections', payload);
  },

  /**
   * Update/rename a section (PUT /sections/{id}).
   */
  async updateSection(sectionId: number, payload: SectionUpdatePayload): Promise<Section> {
    return apiClient.put<Section>(`/sections/${sectionId}`, payload);
  },

  /**
   * Delete a section (DELETE /sections/{id}).
   */
  async deleteSection(sectionId: number): Promise<void> {
    return apiClient.delete<void>(`/sections/${sectionId}`);
  },
};
