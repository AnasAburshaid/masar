/**
 * Centralized environment and runtime configuration for the Masar frontend.
 */

export const env = {
  /**
   * The base URL for the FastAPI backend service.
   * Defaults to 'http://localhost:8000' if not provided via environment variable.
   */
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',

  /**
   * Application metadata.
   */
  appName: 'Masar',
  appDescription: 'Developer Learning Tracker',
} as const;

export default env;
