import { apiClient } from './client';
import {
  Conversation,
  ConversationDetail,
  CreateConversationPayload,
  SendMessagePayload,
  SendMessageResponse,
  UpdateConversationPayload,
} from '@/types/conversation';

export const conversationService = {
  /**
   * List all conversations for the authenticated user (GET /conversations).
   */
  async listConversations(): Promise<Conversation[]> {
    return apiClient.get<Conversation[]>('/conversations');
  },

  /**
   * Retrieve a conversation along with its full message history (GET /conversations/{id}).
   */
  async getConversation(conversationId: number): Promise<ConversationDetail> {
    return apiClient.get<ConversationDetail>(`/conversations/${conversationId}`);
  },

  /**
   * Create a new conversation thread (POST /conversations).
   */
  async createConversation(payload: CreateConversationPayload = {}): Promise<Conversation> {
    return apiClient.post<Conversation>('/conversations', payload);
  },

  /**
   * Update the title of an existing conversation (PUT /conversations/{id}).
   */
  async updateConversation(
    conversationId: number,
    payload: UpdateConversationPayload
  ): Promise<Conversation> {
    return apiClient.put<Conversation>(`/conversations/${conversationId}`, payload);
  },

  /**
   * Delete a conversation thread and its messages (DELETE /conversations/{id}).
   */
  async deleteConversation(conversationId: number): Promise<void> {
    return apiClient.delete<void>(`/conversations/${conversationId}`);
  },

  /**
   * Send a user message and receive the AI assistant's response (POST /conversations/{id}/messages).
   */
  async sendMessage(
    conversationId: number,
    payload: SendMessagePayload
  ): Promise<SendMessageResponse> {
    return apiClient.post<SendMessageResponse>(`/conversations/${conversationId}/messages`, payload);
  },
};
