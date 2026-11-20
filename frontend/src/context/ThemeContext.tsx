'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

export type Theme = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const THEME_STORAGE_KEY = 'masar_theme_preference';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('system');
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>('dark');

  const applyThemeToDocument = useCallback((effectiveTheme: ResolvedTheme) => {
    if (typeof document === 'undefined') return;
    const root = document.documentElement;
    if (effectiveTheme === 'dark') {
      root.classList.add('dark');
      root.style.colorScheme = 'dark';
      root.setAttribute('data-theme', 'dark');
    } else {
      root.classList.remove('dark');
      root.style.colorScheme = 'light';
      root.setAttribute('data-theme', 'light');
    }
  }, []);

  const resolveTheme = useCallback((targetTheme: Theme): ResolvedTheme => {
    if (targetTheme === 'system') {
      if (typeof window !== 'undefined' && window.matchMedia) {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      return 'dark';
    }
    return targetTheme;
  }, []);

  const setTheme = useCallback(
    (newTheme: Theme) => {
      setThemeState(newTheme);
      try {
        localStorage.setItem(THEME_STORAGE_KEY, newTheme);
      } catch {
        // Storage might be disabled
      }
      const effective = resolveTheme(newTheme);
      setResolvedTheme(effective);
      applyThemeToDocument(effective);
    },
    [applyThemeToDocument, resolveTheme]
  );

  const toggleTheme = useCallback(() => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  }, [resolvedTheme, setTheme]);

  useEffect(() => {
    let saved: Theme | null = null;
    try {
      saved = localStorage.getItem(THEME_STORAGE_KEY) as Theme | null;
    } catch {
      // Storage might be disabled
    }

    const initialTheme: Theme = saved && ['light', 'dark', 'system'].includes(saved) ? saved : 'system';
    const effective = resolveTheme(initialTheme);

    // Apply to document immediately
    applyThemeToDocument(effective);

    // Queue state update to avoid cascading re-render warnings
    queueMicrotask(() => {
      setThemeState(initialTheme);
      setResolvedTheme(effective);
    });

    // Media query listener for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemChange = (e: MediaQueryListEvent) => {
      setThemeState((currentTheme) => {
        if (currentTheme === 'system') {
          const newEffective: ResolvedTheme = e.matches ? 'dark' : 'light';
          setResolvedTheme(newEffective);
          applyThemeToDocument(newEffective);
        }
        return currentTheme;
      });
    };

    mediaQuery.addEventListener('change', handleSystemChange);
    return () => mediaQuery.removeEventListener('change', handleSystemChange);
  }, [applyThemeToDocument, resolveTheme]);

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
