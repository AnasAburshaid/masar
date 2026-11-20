import type { ApiErrorResponse } from '@/types/api';

/**
 * Standardized API Error representation across the Masar frontend.
 */
export class ApiError extends Error {
  public readonly status: number;
  public readonly detail?: string;
  public readonly validationErrors?: Array<{ loc?: string[]; msg?: string; type?: string }>;
  public readonly isNetworkError: boolean;
  public readonly rawResponse?: unknown;

  constructor(options: {
    message: string;
    status?: number;
    detail?: string;
    validationErrors?: Array<{ loc?: string[]; msg?: string; type?: string }>;
    isNetworkError?: boolean;
    rawResponse?: unknown;
  }) {
    super(options.message);
    this.name = 'ApiError';
    this.status = options.status ?? 0;
    this.detail = options.detail;
    this.validationErrors = options.validationErrors;
    this.isNetworkError = options.isNetworkError ?? false;
    this.rawResponse = options.rawResponse;

    // Maintain proper prototype chain
    Object.setPrototypeOf(this, ApiError.prototype);
  }

  /**
   * Helper to check if the error was due to an authentication failure (HTTP 401).
   */
  public get isUnauthorized(): boolean {
    return this.status === 401;
  }

  /**
   * Helper to check if the error was due to an authorization failure (HTTP 403).
   */
  public get isForbidden(): boolean {
    return this.status === 403;
  }

  /**
   * Helper to check if the resource was not found (HTTP 404).
   */
  public get isNotFound(): boolean {
    return this.status === 404;
  }

  /**
   * Helper to check if the error was due to request validation (HTTP 422).
   */
  public get isValidationError(): boolean {
    return this.status === 422;
  }

  /**
   * Extract user-friendly display message from error.
   */
  public get userMessage(): string {
    if (this.isNetworkError) {
      return 'Unable to connect to the Masar backend server. Please check your network connection or verify that the API server is running.';
    }

    if (this.detail) {
      return this.detail;
    }

    if (this.validationErrors && this.validationErrors.length > 0) {
      return this.validationErrors
        .map((e) => e.msg || 'Invalid field')
        .join(', ');
    }

    return this.message || 'An unexpected error occurred while communicating with the server.';
  }

  /**
   * Parse a failed Response into an ApiError.
   */
  public static async fromResponse(response: Response): Promise<ApiError> {
    let parsedBody: ApiErrorResponse | null = null;
    let fallbackText = '';

    try {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        parsedBody = (await response.json()) as ApiErrorResponse;
      } else {
        fallbackText = await response.text();
      }
    } catch {
      // Body could not be read or parsed
    }

    let detail: string | undefined;
    let validationErrors: Array<{ loc?: string[]; msg?: string; type?: string }> | undefined;

    if (parsedBody) {
      if (typeof parsedBody.detail === 'string') {
        detail = parsedBody.detail;
      } else if (Array.isArray(parsedBody.detail)) {
        validationErrors = parsedBody.detail;
      } else if (parsedBody.message) {
        detail = parsedBody.message;
      } else if (parsedBody.error) {
        detail = parsedBody.error;
      }
    } else if (fallbackText) {
      detail = fallbackText;
    }

    const message = detail || `Request failed with HTTP status ${response.status}`;

    return new ApiError({
      message,
      status: response.status,
      detail,
      validationErrors,
      isNetworkError: false,
      rawResponse: parsedBody || fallbackText,
    });
  }

  /**
   * Create an ApiError representing a network or connection failure.
   */
  public static networkError(error: unknown): ApiError {
    const rawMessage = error instanceof Error ? error.message : String(error);
    return new ApiError({
      message: `Network Error: ${rawMessage}`,
      status: 0,
      isNetworkError: true,
      rawResponse: error,
    });
  }
}
