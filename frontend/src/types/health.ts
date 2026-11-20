/**
 * Backend health check and root information types.
 */

export interface HealthStatus {
  status: 'ok' | 'degraded' | 'error';
  environment: string;
  storage_type: string;
}

export interface ApiRootInfo {
  message: string;
  app_name: string;
  version: string;
  environment: string;
  docs_url: string;
  health_url: string;
}
