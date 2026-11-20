'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { useAuth } from '@/context/AuthContext';
import { journeyService } from '@/services/api/journeys';
import { progressService } from '@/services/api/progress';
import { Journey } from '@/types/journey';
import { JourneyProgress, DashboardStats } from '@/types/progress';
import { ApiError } from '@/services/api/errors';

function DashboardContent() {
  const { user } = useAuth();

  const [journeys, setJourneys] = useState<Journey[]>([]);
  const [journeyProgressMap, setJourneyProgressMap] = useState<Record<number, JourneyProgress>>({});
  const [stats, setStats] = useState<DashboardStats>({
    totalJourneys: 0,
    completedJourneys: 0,
    inProgressJourneys: 0,
    notStartedJourneys: 0,
    totalTopics: 0,
    completedTopics: 0,
    inProgressTopics: 0,
    overallPercentage: 0,
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);
  const [expandedJourneyId, setExpandedJourneyId] = useState<number | null>(null);

  const fetchDashboardData = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) {
      setIsRefreshing(true);
    }
    setErrorBanner(null);

    try {
      // 1. Fetch all user journeys
      const userJourneys = await journeyService.listJourneys();
      setJourneys(userJourneys);

      // 2. Fetch progress for each journey in parallel
      const progressPromises = userJourneys.map(async (j) => {
        try {
          const prog = await progressService.getJourneyProgress(j.id);
          return { id: j.id, progress: prog };
        } catch {
          // Fallback if individual progress fetch fails
          const fallback: JourneyProgress = {
            journey_id: j.id,
            title: j.title,
            completed_topics: 0,
            total_topics: 0,
            percentage: 0,
            is_complete: false,
            sections: [],
          };
          return { id: j.id, progress: fallback };
        }
      });

      const progressResults = await Promise.all(progressPromises);
      const progressMap: Record<number, JourneyProgress> = {};
      const progressList: JourneyProgress[] = [];

      for (const res of progressResults) {
        progressMap[res.id] = res.progress;
        progressList.push(res.progress);
      }

      setJourneyProgressMap(progressMap);

      // 3. Compute aggregated statistics
      const calculatedStats = progressService.calculateDashboardStats(progressList);
      setStats(calculatedStats);
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorBanner(err.message);
      } else {
        setErrorBanner('Failed to load dashboard progress. Please check your network connection.');
      }
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    (async () => {
      if (isMounted) {
        await fetchDashboardData(false);
      }
    })();
    return () => {
      isMounted = false;
    };
  }, [fetchDashboardData]);

  const toggleExpandJourney = (id: number) => {
    setExpandedJourneyId((prev) => (prev === id ? null : id));
  };

  const username = user?.email ? user.email.split('@')[0] : 'Engineer';

  return (
    <div className="space-y-8">
      {/* Welcome & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-medium uppercase tracking-wider text-emerald-400">
              Live Progress Dashboard
            </span>
          </div>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-100">
            Welcome back, {username}!
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-slate-400">
            Monitor your engineering milestones, topic mastery, and learning journey velocity.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => fetchDashboardData(true)}
            disabled={isRefreshing || isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 disabled:opacity-50 transition-colors"
            title="Refresh learning statistics"
          >
            <svg
              className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-emerald-400' : 'text-slate-400'}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
          >
            API Docs ↗
          </a>

          <Link
            href="/journeys"
            className="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-colors"
          >
            Manage Journeys
          </Link>
        </div>
      </div>

      {/* Error Banner */}
      {errorBanner && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/80 flex items-start justify-between gap-3 text-rose-200">
          <div className="flex items-center gap-2 text-xs">
            <svg className="w-4 h-4 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{errorBanner}</span>
          </div>
          <button
            onClick={() => fetchDashboardData(true)}
            className="text-xs font-semibold underline text-rose-300 hover:text-rose-100"
          >
            Retry
          </button>
        </div>
      )}

      {/* Skeleton Loading State */}
      {isLoading ? (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 animate-pulse h-28" />
            ))}
          </div>
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 animate-pulse h-64" />
        </div>
      ) : (
        <>
          {/* 4 Main KPI Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Overall Mastery Percentage */}
            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800/90 shadow-sm relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-colors pointer-events-none" />
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Overall Mastery</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {stats.overallPercentage}%
                </span>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-slate-100 font-mono tracking-tight">
                {stats.overallPercentage}%
              </div>
              <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-emerald-600 to-teal-400 h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${stats.overallPercentage}%` }}
                />
              </div>
              <div className="mt-2 text-[11px] text-slate-500">
                {stats.completedTopics} of {stats.totalTopics} topics completed
              </div>
            </div>

            {/* Total Journeys */}
            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800/90 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Learning Journeys</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                  Total
                </span>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-slate-100 font-mono tracking-tight">
                {stats.totalJourneys}
              </div>
              <div className="mt-3 text-[11px] text-slate-400 flex items-center gap-2">
                <span className="text-emerald-400 font-medium">{stats.completedJourneys} completed</span>
                <span>·</span>
                <span className="text-amber-400 font-medium">{stats.inProgressJourneys} in progress</span>
              </div>
            </div>

            {/* Topics Mastered */}
            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800/90 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Topics Mastered</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
              </div>
              <div className="mt-2 text-3xl font-extrabold text-emerald-400 font-mono tracking-tight">
                {stats.completedTopics}
              </div>
              <div className="mt-3 text-[11px] text-slate-500">
                {stats.totalTopics > 0
                  ? `${Math.round((stats.completedTopics / stats.totalTopics) * 100)}% completion rate`
                  : 'No topics added yet'}
              </div>
            </div>

            {/* Topics in Progress */}
            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800/90 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Topics Pending</span>
                <span className="w-2 h-2 rounded-full bg-amber-400" />
              </div>
              <div className="mt-2 text-3xl font-extrabold text-amber-400 font-mono tracking-tight">
                {stats.inProgressTopics}
              </div>
              <div className="mt-3 text-[11px] text-slate-500">
                Awaiting study and completion
              </div>
            </div>
          </div>

          {/* Visual Milestone Distribution Card */}
          {stats.totalJourneys > 0 && (
            <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800/80 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-slate-200">Roadmap Progress Distribution</h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Categorization of learning journeys by active completion state.
                  </p>
                </div>
                <div className="flex items-center gap-4 text-xs font-mono">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    <span className="text-slate-300">Completed ({stats.completedJourneys})</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                    <span className="text-slate-300">In Progress ({stats.inProgressJourneys})</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-600" />
                    <span className="text-slate-300">Not Started ({stats.notStartedJourneys})</span>
                  </div>
                </div>
              </div>

              {/* Proportional Segmented Meter */}
              <div className="w-full h-3 rounded-full bg-slate-800 flex overflow-hidden p-0.5 gap-0.5">
                {stats.completedJourneys > 0 && (
                  <div
                    className="bg-emerald-500 rounded-sm transition-all duration-500"
                    style={{ width: `${(stats.completedJourneys / stats.totalJourneys) * 100}%` }}
                    title={`${stats.completedJourneys} Completed`}
                  />
                )}
                {stats.inProgressJourneys > 0 && (
                  <div
                    className="bg-amber-400 rounded-sm transition-all duration-500"
                    style={{ width: `${(stats.inProgressJourneys / stats.totalJourneys) * 100}%` }}
                    title={`${stats.inProgressJourneys} In Progress`}
                  />
                )}
                {stats.notStartedJourneys > 0 && (
                  <div
                    className="bg-slate-600 rounded-sm transition-all duration-500"
                    style={{ width: `${(stats.notStartedJourneys / stats.totalJourneys) * 100}%` }}
                    title={`${stats.notStartedJourneys} Not Started`}
                  />
                )}
              </div>
            </div>
          )}

          {/* Individual Journeys Progress Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-slate-200">Your Learning Roadmaps</h2>
                <p className="text-xs text-slate-400">
                  Individual completion breakdown per journey and section.
                </p>
              </div>
              <Link
                href="/journeys"
                className="text-xs font-medium text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
              >
                <span>View all journeys</span>
                <span aria-hidden="true">→</span>
              </Link>
            </div>

            {/* Empty State */}
            {journeys.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950/40 p-8 sm:p-12 text-center">
                <div className="mx-auto w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 mb-3">
                  <svg className="w-6 h-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <h3 className="text-sm font-semibold text-slate-200">No learning journeys created yet</h3>
                <p className="mt-1 text-xs text-slate-400 max-w-sm mx-auto">
                  Create your first learning journey to start tracking sections, topics, notes, and visual progress metrics.
                </p>
                <div className="mt-5 flex items-center justify-center gap-3">
                  <Link
                    href="/journeys"
                    className="px-4 py-2 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors"
                  >
                    + Create First Journey
                  </Link>
                  <a
                    href="http://localhost:8000/docs"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                  >
                    Explore API Specs
                  </a>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {journeys.map((journey) => {
                  const prog = journeyProgressMap[journey.id] || {
                    journey_id: journey.id,
                    title: journey.title,
                    completed_topics: 0,
                    total_topics: 0,
                    percentage: 0,
                    is_complete: false,
                    sections: [],
                  };

                  const isExpanded = expandedJourneyId === journey.id;
                  const isFinished = prog.is_complete && prog.total_topics > 0;
                  const isStarted = prog.completed_topics > 0 && !isFinished;

                  return (
                    <div
                      key={journey.id}
                      className="rounded-xl border border-slate-800/80 bg-slate-900/60 hover:border-slate-700/80 transition-all p-5 shadow-sm"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                        <div className="space-y-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60">
                              #{journey.id}
                            </span>
                            <h3 className="text-sm font-semibold text-slate-100 truncate">
                              {journey.title}
                            </h3>
                            {isFinished ? (
                              <span className="inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                                <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                Completed
                              </span>
                            ) : isStarted ? (
                              <span className="inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
                                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                                In Progress
                              </span>
                            ) : (
                              <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                                Not Started
                              </span>
                            )}
                          </div>
                          {journey.description && (
                            <p className="text-xs text-slate-400 line-clamp-1">{journey.description}</p>
                          )}
                        </div>

                        <div className="flex items-center gap-3 shrink-0">
                          <button
                            onClick={() => toggleExpandJourney(journey.id)}
                            className="px-2.5 py-1 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 transition-colors flex items-center gap-1"
                          >
                            <span>{isExpanded ? 'Hide Breakdown' : 'Sections'}</span>
                            <svg
                              className={`w-3.5 h-3.5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </button>

                          <Link
                            href={`/journeys/${journey.id}`}
                            className="px-3 py-1 rounded-lg text-xs font-medium bg-emerald-600/90 hover:bg-emerald-500 text-white transition-colors flex items-center gap-1"
                          >
                            <span>Open Journey</span>
                            <span aria-hidden="true">→</span>
                          </Link>
                        </div>
                      </div>

                      {/* Progress Bar & Indicators */}
                      <div className="mt-4 pt-3 border-t border-slate-800/60">
                        <div className="flex items-center justify-between text-xs mb-1.5 font-mono">
                          <span className="text-slate-400 text-[11px]">
                            {prog.completed_topics} / {prog.total_topics} topics completed
                          </span>
                          <span className={`font-semibold ${isFinished ? 'text-emerald-400' : 'text-slate-200'}`}>
                            {prog.percentage}%
                          </span>
                        </div>
                        <div className="w-full bg-slate-800/90 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-2 rounded-full transition-all duration-500 ${
                              isFinished
                                ? 'bg-emerald-500'
                                : 'bg-gradient-to-r from-emerald-600 to-teal-400'
                            }`}
                            style={{ width: `${prog.percentage}%` }}
                          />
                        </div>
                      </div>

                      {/* Expandable Section Breakdown */}
                      {isExpanded && (
                        <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-3 bg-slate-950/40 -mx-5 -mb-5 p-5 rounded-b-xl">
                          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                            Section Breakdown ({prog.sections?.length || 0})
                          </h4>

                          {prog.sections && prog.sections.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                              {prog.sections.map((sec) => (
                                <div
                                  key={sec.section_id}
                                  className="p-3 rounded-lg bg-slate-900/80 border border-slate-800/80 text-xs"
                                >
                                  <div className="flex items-center justify-between mb-1.5">
                                    <span className="font-medium text-slate-200 truncate">{sec.title}</span>
                                    <span className="font-mono text-[11px] text-slate-400 shrink-0 ml-2">
                                      {sec.completed_topics}/{sec.total_topics} ({sec.percentage}%)
                                    </span>
                                  </div>
                                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                    <div
                                      className={`h-1.5 rounded-full transition-all ${
                                        sec.is_complete ? 'bg-emerald-500' : 'bg-emerald-600/70'
                                      }`}
                                      style={{ width: `${sec.percentage}%` }}
                                    />
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-xs text-slate-500 italic">
                              No sections added to this journey yet.
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </>
      )}
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
