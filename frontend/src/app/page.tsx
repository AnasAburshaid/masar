'use client';

import React from 'react';
import Link from 'next/link';
import { HealthWidget } from '@/components/common/HealthWidget';
import { useAuth } from '@/context/AuthContext';

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 py-12 sm:py-20 transition-colors duration-200">
      <div className="max-w-4xl w-full text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20 shadow-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Developer Learning Tracker • Full-Stack Platform</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
          Master Engineering Domains <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-300 bg-clip-text text-transparent">
            One Structured Step at a Time
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Masar transforms scattered bookmarks and unorganized notes into actionable learning journeys. Track sections, check off topics, record insights, and measure real progress.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
          {isAuthenticated ? (
            <Link
              href="/dashboard"
              className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition-all shadow-sm shadow-emerald-600/30 hover:scale-[1.02]"
            >
              Open Dashboard →
            </Link>
          ) : (
            <>
              <Link
                href="/register"
                className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition-all shadow-sm shadow-emerald-600/30 hover:scale-[1.02]"
              >
                Start Learning Now
              </Link>
              <Link
                href="/login"
                className="px-6 py-3 rounded-xl bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-100 font-semibold text-sm border border-slate-200 dark:border-slate-700 transition-all shadow-xs"
              >
                Sign In
              </Link>
            </>
          )}

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-5 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 font-medium text-sm hover:bg-slate-100 dark:hover:bg-slate-800/60 transition-colors"
          >
            FastAPI Docs ↗
          </a>
        </div>
      </div>

      {/* Backend API Health Status Indicator */}
      <div className="w-full mt-14 sm:mt-18">
        <HealthWidget />
      </div>

      {/* Core Architectural Pillars */}
      <div className="max-w-5xl w-full mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/50 border border-slate-200/90 dark:border-slate-800/80 shadow-xs hover:shadow-md transition-all">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-4">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">Clean Layered Design</h3>
          <p className="mt-2 text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            Strict domain models, decoupled service abstractions, repository interfaces, and presentation boundaries.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/50 border border-slate-200/90 dark:border-slate-800/80 shadow-xs hover:shadow-md transition-all">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">Stateless JWT Auth</h3>
          <p className="mt-2 text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            PBKDF2 salted password hashing, signed access tokens, and strict cascading data ownership rules.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/50 border border-slate-200/90 dark:border-slate-800/80 shadow-xs hover:shadow-md transition-all">
          <div className="w-10 h-10 rounded-xl bg-teal-50 dark:bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center mb-4">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">Milestone Analytics</h3>
          <p className="mt-2 text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            Real-time percentage calculations, section breakdowns, and genuine completion tracking.
          </p>
        </div>
      </div>
    </div>
  );
}
