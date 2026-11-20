/**
 * API client and response types.
 */

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
  token?: string | null;
}

export interface ApiErrorResponse {
  detail?: string | Array<{ loc?: string[]; msg?: string; type?: string }>;
  message?: string;
  error?: string;
}
