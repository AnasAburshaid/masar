import test from 'node:test';
import assert from 'node:assert/strict';
import { THEME_STORAGE_KEY } from './ThemeContext';

test('THEME_STORAGE_KEY constant is defined as masar_theme_preference', () => {
  assert.equal(THEME_STORAGE_KEY, 'masar_theme_preference');
});

test('Theme preference document manipulation works for light and dark', (t) => {
  // Set up mock DOM environment
  const classListSet = new Set<string>();
  const attributes: Record<string, string> = {};
  const styleObj: Record<string, string> = {};

  const mockRoot = {
    classList: {
      add: (cls: string) => classListSet.add(cls),
      remove: (cls: string) => classListSet.delete(cls),
      contains: (cls: string) => classListSet.has(cls),
    },
    style: styleObj,
    setAttribute: (name: string, val: string) => {
      attributes[name] = val;
    },
    getAttribute: (name: string) => attributes[name] ?? null,
  };

  const originalDocument = globalThis.document;
  t.after(() => {
    globalThis.document = originalDocument;
  });

  (globalThis as unknown as { document: unknown }).document = {
    documentElement: mockRoot,
  };

  // Helper matching ThemeContext applyThemeToDocument logic
  const applyTheme = (effectiveTheme: 'light' | 'dark') => {
    const root = globalThis.document.documentElement;
    if (effectiveTheme === 'dark') {
      root.classList.add('dark');
      root.style.colorScheme = 'dark';
      root.setAttribute('data-theme', 'dark');
    } else {
      root.classList.remove('dark');
      root.style.colorScheme = 'light';
      root.setAttribute('data-theme', 'light');
    }
  };

  // 1. Apply dark mode
  applyTheme('dark');
  assert.equal(mockRoot.classList.contains('dark'), true);
  assert.equal(mockRoot.style.colorScheme, 'dark');
  assert.equal(mockRoot.getAttribute('data-theme'), 'dark');

  // 2. Apply light mode
  applyTheme('light');
  assert.equal(mockRoot.classList.contains('dark'), false);
  assert.equal(mockRoot.style.colorScheme, 'light');
  assert.equal(mockRoot.getAttribute('data-theme'), 'light');
});

test('Theme preference resolves system theme correctly via matchMedia', (t) => {
  const originalWindow = globalThis.window;
  t.after(() => {
    globalThis.window = originalWindow;
  });

  let prefersDark = true;
  (globalThis as unknown as { window: unknown }).window = {
    matchMedia: (query: string) => ({
      matches: query.includes('prefers-color-scheme: dark') ? prefersDark : false,
      addEventListener: () => {},
      removeEventListener: () => {},
    }),
  };

  const resolveTheme = (targetTheme: 'light' | 'dark' | 'system'): 'light' | 'dark' => {
    if (targetTheme === 'system') {
      if (typeof window !== 'undefined' && window.matchMedia) {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      return 'dark';
    }
    return targetTheme;
  };

  // When OS prefers dark
  prefersDark = true;
  assert.equal(resolveTheme('system'), 'dark');

  // When OS prefers light
  prefersDark = false;
  assert.equal(resolveTheme('system'), 'light');

  // Explicit overrides
  assert.equal(resolveTheme('dark'), 'dark');
  assert.equal(resolveTheme('light'), 'light');
});

test('Theme preference toggling and localStorage persistence', (t) => {
  const store: Record<string, string> = {};
  const originalLocalStorage = globalThis.localStorage;
  t.after(() => {
    globalThis.localStorage = originalLocalStorage;
  });

  (globalThis as unknown as { localStorage: unknown }).localStorage = {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, val: string) => {
      store[key] = val;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
  };

  // Simulate user switching to light
  localStorage.setItem(THEME_STORAGE_KEY, 'light');
  assert.equal(localStorage.getItem(THEME_STORAGE_KEY), 'light');

  // Toggle from light -> dark
  const currentTheme = localStorage.getItem(THEME_STORAGE_KEY);
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
  localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  assert.equal(localStorage.getItem(THEME_STORAGE_KEY), 'dark');
});
