'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { ThemeToggle } from '@/components/common/ThemeToggle';

export function Header() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <header className="w-full border-b border-slate-200/90 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/75 backdrop-blur-md sticky top-0 z-50 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 dark:from-emerald-500 dark:to-teal-300 flex items-center justify-center text-white font-bold text-lg shadow-sm shadow-emerald-500/20 group-hover:scale-105 transition-transform">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2.5}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                Masar
              </span>
              <span className="hidden sm:inline-block text-[11px] font-medium tracking-wide text-slate-500 dark:text-slate-400 uppercase">
                Learning Engine
              </span>
            </div>
          </Link>
        </div>

        <nav className="flex items-center gap-2 sm:gap-3">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center gap-1 text-xs font-medium text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200 px-2.5 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800/60 transition-colors"
          >
            <span>API Docs</span>
            <span className="text-[10px]" aria-hidden="true">↗</span>
          </a>

          {/* Theme switcher */}
          <ThemeToggle />

          <div className="h-4 w-px bg-slate-200 dark:bg-slate-800 mx-1 hidden sm:block" />

          {isAuthenticated ? (
            <>
              <Link
                href="/dashboard"
                className="text-xs font-medium text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors"
              >
                Dashboard
              </Link>
              <Link
                href="/journeys"
                className="text-xs font-medium text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors"
              >
                Journeys
              </Link>
              <Link
                href="/profile"
                className="text-xs font-medium text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors"
              >
                Knowledge Profile
              </Link>
              <Link
                href="/chat"
                className="text-xs font-medium text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors flex items-center gap-1.5"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span>AI Chat</span>
              </Link>
              <button
                onClick={logout}
                title={user?.email ? `Signed in as ${user.email}` : 'Sign out'}
                className="text-xs font-medium text-slate-500 hover:text-rose-600 dark:text-slate-400 dark:hover:text-rose-400 px-2.5 py-1.5 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="text-xs font-medium text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Sign in
              </Link>
              <Link
                href="/register"
                className="text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-1.5 rounded-lg shadow-sm shadow-emerald-600/20 hover:shadow-emerald-600/30 transition-all"
              >
                Get Started
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
