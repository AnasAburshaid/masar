'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { AuthState, LoginCredentials, RegisterCredentials, User } from '@/types/auth';
import { authService } from '@/services/api/auth';
import { apiClient } from '@/services/api/client';

interface AuthContextValue extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<User>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const STORAGE_KEY = 'masar_session_token';

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Synchronize token provider with API client
  useEffect(() => {
    apiClient.setTokenProvider(() => token);
  }, [token]);

  const logout = useCallback(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(STORAGE_KEY);
    }
    setToken(null);
    setUser(null);
  }, []);

  const fetchProfile = useCallback(async (activeToken: string) => {
    try {
      const profile = await authService.getCurrentUser(activeToken);
      setUser(profile);
    } catch {
      // Token is invalid or expired
      logout();
    }
  }, [logout]);

  // Initialize session on client mount
  useEffect(() => {
    let isCancelled = false;

    const initAuth = async () => {
      try {
        const savedToken = typeof window !== 'undefined' ? sessionStorage.getItem(STORAGE_KEY) : null;
        if (!savedToken) {
          if (!isCancelled) {
            setIsLoading(false);
          }
          return;
        }

        setToken(savedToken);
        const profile = await authService.getCurrentUser(savedToken);
        if (!isCancelled) {
          setUser(profile);
        }
      } catch {
        if (!isCancelled) {
          if (typeof window !== 'undefined') {
            sessionStorage.removeItem(STORAGE_KEY);
          }
          setToken(null);
          setUser(null);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    initAuth();

    return () => {
      isCancelled = true;
    };
  }, []);

  const login = async (credentials: LoginCredentials): Promise<void> => {
    const authResult = await authService.login(credentials);
    const accessToken = authResult.access_token;

    if (typeof window !== 'undefined') {
      sessionStorage.setItem(STORAGE_KEY, accessToken);
    }

    setToken(accessToken);
    await fetchProfile(accessToken);
  };

  const register = async (credentials: RegisterCredentials): Promise<User> => {
    return authService.register(credentials);
  };

  const refreshUser = async (): Promise<void> => {
    if (token) {
      await fetchProfile(token);
    }
  };

  const value: AuthContextValue = {
    user,
    token,
    isAuthenticated: Boolean(token && user),
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
