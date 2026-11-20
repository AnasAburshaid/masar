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
  const [token, setToken] = useState<string | null>(() => {
    if (typeof window !== 'undefined') {
      return sessionStorage.getItem(STORAGE_KEY);
    }
    return null;
  });
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return Boolean(sessionStorage.getItem(STORAGE_KEY));
    }
    return false;
  });

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

  // Load and validate user profile when token exists or changes
  useEffect(() => {
    let isCancelled = false;

    if (!token) {
      return;
    }

    authService
      .getCurrentUser(token)
      .then((profile) => {
        if (!isCancelled) {
          setUser(profile);
          setIsLoading(false);
        }
      })
      .catch(() => {
        if (!isCancelled) {
          if (typeof window !== 'undefined') {
            sessionStorage.removeItem(STORAGE_KEY);
          }
          setToken(null);
          setUser(null);
          setIsLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [token]);

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
