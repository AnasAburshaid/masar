import { apiClient } from './client';
import {
  LearningProfile,
  ProfileExtractionResponse,
  ProfileItem,
  ProfileItemCreatePayload,
  ProfileItemUpdatePayload,
} from '@/types/profile';

export const profileService = {
  /**
   * Retrieve current user's complete learning profile (GET /profile).
   */
  async getProfile(): Promise<LearningProfile> {
    return apiClient.get<LearningProfile>('/profile');
  },

  /**
   * Update user's professional bio (PUT /profile/bio).
   */
  async updateBio(bio: string): Promise<LearningProfile> {
    return apiClient.put<LearningProfile>('/profile/bio', { bio });
  },

  /**
   * Add a new profile item (POST /profile/items).
   */
  async addItem(payload: ProfileItemCreatePayload): Promise<ProfileItem> {
    return apiClient.post<ProfileItem>('/profile/items', payload);
  },

  /**
   * Update an existing profile item (PUT /profile/items/{item_id}).
   */
  async updateItem(
    itemId: number,
    payload: ProfileItemUpdatePayload
  ): Promise<ProfileItem> {
    return apiClient.put<ProfileItem>(`/profile/items/${itemId}`, payload);
  },

  /**
   * Confirm an AI-inferred profile item (POST /profile/items/{item_id}/confirm).
   */
  async confirmItem(itemId: number): Promise<ProfileItem> {
    return apiClient.post<ProfileItem>(`/profile/items/${itemId}/confirm`);
  },

  /**
   * Remove a profile item (DELETE /profile/items/{item_id}).
   */
  async deleteItem(itemId: number): Promise<void> {
    return apiClient.delete<void>(`/profile/items/${itemId}`);
  },

  /**
   * Extract skills and knowledge from an uploaded document (POST /profile/extract/document/{doc_id}).
   */
  async extractFromDocument(
    documentId: number
  ): Promise<ProfileExtractionResponse> {
    return apiClient.post<ProfileExtractionResponse>(
      `/profile/extract/document/${documentId}`
    );
  },
};
