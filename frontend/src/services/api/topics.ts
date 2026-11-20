import { apiClient } from './client';
import { Topic, TopicCreatePayload, TopicUpdatePayload } from '@/types/journey';

export const topicService = {
  /**
   * List all topics for a section (GET /sections/{sectionId}/topics).
   */
  async listTopics(sectionId: number): Promise<Topic[]> {
    return apiClient.get<Topic[]>(`/sections/${sectionId}/topics`);
  },

  /**
   * Get a topic by ID (GET /topics/{id}).
   */
  async getTopic(topicId: number): Promise<Topic> {
    return apiClient.get<Topic>(`/topics/${topicId}`);
  },

  /**
   * Create a new topic in a section (POST /topics).
   */
  async createTopic(payload: TopicCreatePayload): Promise<Topic> {
    return apiClient.post<Topic>('/topics', payload);
  },

  /**
   * Update topic title or completion status (PUT /topics/{id}).
   */
  async updateTopic(topicId: number, payload: TopicUpdatePayload): Promise<Topic> {
    return apiClient.put<Topic>(`/topics/${topicId}`, payload);
  },

  /**
   * Mark a topic as completed (PATCH /topics/{id}/complete).
   */
  async markCompleted(topicId: number): Promise<Topic> {
    return apiClient.patch<Topic>(`/topics/${topicId}/complete`);
  },

  /**
   * Mark a topic as pending (PATCH /topics/{id}/pending).
   */
  async markPending(topicId: number): Promise<Topic> {
    return apiClient.patch<Topic>(`/topics/${topicId}/pending`);
  },

  /**
   * Delete a topic (DELETE /topics/{id}).
   */
  async deleteTopic(topicId: number): Promise<void> {
    return apiClient.delete<void>(`/topics/${topicId}`);
  },
};
