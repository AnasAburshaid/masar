import { apiClient } from './client';
import { ApiRootInfo, HealthStatus } from '@/types/health';

/**
 * Health and system information API service.
 */
export const healthService = {
  /**
   * Check backend health and persistence status (GET /health).
   */
  async checkHealth(): Promise<HealthStatus> {
    return apiClient.get<HealthStatus>('/health');
  },

  /**
   * Fetch root API metadata and documentation links (GET /).
   */
  async getRootInfo(): Promise<ApiRootInfo> {
    return apiClient.get<ApiRootInfo>('/');
  },
};
