import { env } from '@/config/env';
import type { RequestOptions } from '@/types/api';
import { ApiError } from './errors';

/**
 * Reusable HTTP client for communicating with the Masar FastAPI backend.
 */
export class ApiClient {
  private readonly baseUrl: string;
  private tokenProvider: (() => string | null) | null = null;

  constructor(baseUrl: string = env.apiUrl) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  /**
   * Set a dynamic token provider for authenticated requests.
   */
  public setTokenProvider(provider: () => string | null): void {
    this.tokenProvider = provider;
  }

  /**
   * Resolve an absolute or relative path to a full URL with query parameters.
   */
  private buildUrl(path: string, params?: Record<string, string | number | boolean | undefined>): string {
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    const url = new URL(`${this.baseUrl}${cleanPath}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    return url.toString();
  }

  /**
   * Execute an HTTP request with centralized error handling and authentication headers.
   */
  public async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { params, token, headers, ...restOptions } = options;
    const url = this.buildUrl(path, params);

    const requestHeaders = new Headers(headers);

    if (!requestHeaders.has('Content-Type') && !(restOptions.body instanceof FormData)) {
      requestHeaders.set('Content-Type', 'application/json');
    }

    if (!requestHeaders.has('Accept')) {
      requestHeaders.set('Accept', 'application/json');
    }

    // Attach Bearer token if provided or retrieved from token provider
    const authToken = token !== undefined ? token : this.tokenProvider?.();
    if (authToken && !requestHeaders.has('Authorization')) {
      requestHeaders.set('Authorization', `Bearer ${authToken}`);
    }

    let response: Response;
    try {
      response = await fetch(url, {
        ...restOptions,
        headers: requestHeaders,
      });
    } catch (networkErr) {
      throw ApiError.networkError(networkErr);
    }

    if (!response.ok) {
      throw await ApiError.fromResponse(response);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as unknown as T;
    }

    try {
      return (await response.json()) as T;
    } catch {
      return undefined as unknown as T;
    }
  }

  public get<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, { ...options, method: 'GET' });
  }

  public post<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  }

  public put<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: 'PUT',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  }

  public patch<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: 'PATCH',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  }

  public delete<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, { ...options, method: 'DELETE' });
  }
}

/**
 * Default singleton instance configured with environment settings.
 */
export const apiClient = new ApiClient();
