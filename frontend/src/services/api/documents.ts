import { apiClient } from './client';
import {
  DocumentDetail,
  DocumentItem,
  DocumentSummarizeResponse,
} from '@/types/document';

export const documentService = {
  /**
   * Upload a learning resource file (PDF, TXT, MD up to 10MB) (POST /documents/upload).
   */
  async uploadDocument(file: File): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<DocumentItem>('/documents/upload', formData);
  },

  /**
   * List all documents uploaded by the authenticated user (GET /documents).
   */
  async listDocuments(): Promise<DocumentItem[]> {
    return apiClient.get<DocumentItem[]>('/documents');
  },

  /**
   * Retrieve document details and extracted content (GET /documents/{id}).
   */
  async getDocument(documentId: number): Promise<DocumentDetail> {
    return apiClient.get<DocumentDetail>(`/documents/${documentId}`);
  },

  /**
   * Delete an uploaded document (DELETE /documents/{id}).
   */
  async deleteDocument(documentId: number): Promise<void> {
    return apiClient.delete<void>(`/documents/${documentId}`);
  },

  /**
   * Generate or retrieve an AI technical summary (POST /documents/{id}/summarize).
   */
  async summarizeDocument(documentId: number): Promise<DocumentSummarizeResponse> {
    return apiClient.post<DocumentSummarizeResponse>(`/documents/${documentId}/summarize`);
  },
};
