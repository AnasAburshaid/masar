import { apiClient } from './client';
import { AuthToken, LoginCredentials, RegisterCredentials, User } from '@/types/auth';

/**
 * Authentication service interacting with FastAPI backend endpoints.
 */
export const authService = {
  /**
   * Register a new user account (POST /auth/register).
   */
  async register(credentials: RegisterCredentials): Promise<User> {
    return apiClient.post<User>('/auth/register', credentials);
  },

  /**
   * Authenticate with email & password to obtain a JWT token (POST /auth/login).
   */
  async login(credentials: LoginCredentials): Promise<AuthToken> {
    return apiClient.post<AuthToken>('/auth/login', credentials);
  },

  /**
   * Fetch currently authenticated user profile (GET /auth/me).
   */
  async getCurrentUser(token?: string): Promise<User> {
    return apiClient.get<User>('/auth/me', { token });
  },
};
