import { apiClient } from './client';
import { ActionApprovalResponse, ActionProposal } from '@/types/action';

export const actionService = {
  /**
   * List all action proposals for a conversation (GET /conversations/{id}/proposals).
   */
  async listProposals(conversationId: number): Promise<ActionProposal[]> {
    return apiClient.get<ActionProposal[]>(`/conversations/${conversationId}/proposals`);
  },

  /**
   * Retrieve a specific action proposal by ID (GET /conversations/{id}/proposals/{proposalId}).
   */
  async getProposal(conversationId: number, proposalId: number): Promise<ActionProposal> {
    return apiClient.get<ActionProposal>(`/conversations/${conversationId}/proposals/${proposalId}`);
  },

  /**
   * Approve a proposal and trigger execution of its planned actions
   * (POST /conversations/{id}/proposals/{proposalId}/approve).
   */
  async approveProposal(
    conversationId: number,
    proposalId: number
  ): Promise<ActionApprovalResponse> {
    return apiClient.post<ActionApprovalResponse>(
      `/conversations/${conversationId}/proposals/${proposalId}/approve`,
      {}
    );
  },

  /**
   * Reject a proposal (POST /conversations/{id}/proposals/{proposalId}/reject).
   */
  async rejectProposal(conversationId: number, proposalId: number): Promise<ActionProposal> {
    return apiClient.post<ActionProposal>(
      `/conversations/${conversationId}/proposals/${proposalId}/reject`,
      {}
    );
  },
};
