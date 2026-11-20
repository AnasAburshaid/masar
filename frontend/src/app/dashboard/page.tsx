'use client';

import React from 'react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { useAuth } from '@/context/AuthContext';

function DashboardContent() {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-800/80">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">
            Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}!
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-slate-400">
            Track your technical learning paths and milestone progress.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
          >
            API Docs ↗
          </a>
          <button
            onClick={() => alert('Learning Journey management is coming in Issue #41!')}
            className="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-colors"
          >
            + New Journey
          </button>
        </div>
      </div>

      {/* Learning Statistics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
          <div className="text-xs font-medium text-slate-400">Total Journeys</div>
          <div className="mt-2 text-3xl font-extrabold text-slate-100">0</div>
          <div className="mt-1 text-[11px] text-slate-500">Active learning roadmaps</div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
          <div className="text-xs font-medium text-slate-400">Topics in Progress</div>
          <div className="mt-2 text-3xl font-extrabold text-amber-400">0</div>
          <div className="mt-1 text-[11px] text-slate-500">Topics currently learning</div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
          <div className="text-xs font-medium text-slate-400">Completed Topics</div>
          <div className="mt-2 text-3xl font-extrabold text-emerald-400">0</div>
          <div className="mt-1 text-[11px] text-slate-500">Mastered topics</div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
          <div className="text-xs font-medium text-slate-400">Overall Completion</div>
          <div className="mt-2 text-3xl font-extrabold text-slate-100">0%</div>
          <div className="mt-1 text-[11px] text-slate-500">Progress across all journeys</div>
        </div>
      </div>

      {/* Main Learning Journeys Container */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-200">Your Learning Journeys</h2>
          <span className="text-xs text-slate-500">Filtered by owner #{user?.id}</span>
        </div>

        {/* Empty State */}
        <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950/40 p-8 sm:p-12 text-center">
          <div className="mx-auto w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 mb-3">
            <svg className="w-6 h-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 className="text-sm font-semibold text-slate-200">No learning journeys created yet</h3>
          <p className="mt-1 text-xs text-slate-400 max-w-sm mx-auto">
            Journeys help you divide ambitious goals (e.g., &quot;Full-Stack Rust&quot;, &quot;Distributed Systems&quot;) into structured sections and actionable topics.
          </p>
          <div className="mt-5 flex items-center justify-center gap-3">
            <button
              onClick={() => alert('Learning Journey management is coming in Issue #41!')}
              className="px-4 py-2 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors"
            >
              Get started with a journey
            </button>
            <Link
              href="/"
              className="px-4 py-2 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            >
              View system status
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <AppLayout>
        <DashboardContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
