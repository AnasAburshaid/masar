'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { journeyService } from '@/services/api/journeys';
import { Journey } from '@/types/journey';
import { ApiError } from '@/services/api/errors';

function JourneysContent() {
  const [journeys, setJourneys] = useState<Journey[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Modal states
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingJourney, setEditingJourney] = useState<Journey | null>(null);
  const [deletingJourney, setDeletingJourney] = useState<Journey | null>(null);

  // Form states
  const [formTitle, setFormTitle] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const loadJourneys = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await journeyService.listJourneys();
      setJourneys(data);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setErrorMessage(err.userMessage);
      } else {
        setErrorMessage('Failed to load journeys.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let isCancelled = false;

    journeyService.listJourneys().then(
      (data) => {
        if (!isCancelled) {
          setJourneys(data);
          setIsLoading(false);
        }
      },
      (err: unknown) => {
        if (!isCancelled) {
          if (err instanceof ApiError) {
            setErrorMessage(err.userMessage);
          } else {
            setErrorMessage('Failed to load journeys.');
          }
          setIsLoading(false);
        }
      }
    );

    return () => {
      isCancelled = true;
    };
  }, []);

  const openCreateModal = () => {
    setFormTitle('');
    setFormDescription('');
    setFormError(null);
    setIsCreateOpen(true);
  };

  const openEditModal = (journey: Journey) => {
    setEditingJourney(journey);
    setFormTitle(journey.title);
    setFormDescription(journey.description || '');
    setFormError(null);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formTitle.trim()) {
      setFormError('Journey title is required.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);
    try {
      await journeyService.createJourney({
        title: formTitle.trim(),
        description: formDescription.trim(),
      });
      setIsCreateOpen(false);
      await loadJourneys();
    } catch (err: unknown) {
      setFormError(err instanceof ApiError ? err.userMessage : 'Failed to create journey.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingJourney) return;
    if (!formTitle.trim()) {
      setFormError('Journey title is required.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);
    try {
      await journeyService.updateJourney(editingJourney.id, {
        title: formTitle.trim(),
        description: formDescription.trim(),
      });
      setEditingJourney(null);
      await loadJourneys();
    } catch (err: unknown) {
      setFormError(err instanceof ApiError ? err.userMessage : 'Failed to update journey.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deletingJourney) return;
    setIsSubmitting(true);
    try {
      await journeyService.deleteJourney(deletingJourney.id);
      setDeletingJourney(null);
      await loadJourneys();
    } catch (err: unknown) {
      setErrorMessage(err instanceof ApiError ? err.userMessage : 'Failed to delete journey.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">Learning Journeys</h1>
          <p className="mt-1 text-xs sm:text-sm text-slate-400">
            Organize your technical learning paths into structured sections, topics, and notes.
          </p>
        </div>

        <button
          onClick={openCreateModal}
          className="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs sm:text-sm shadow-sm transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Create Journey</span>
        </button>
      </div>

      {/* Global Error Banner */}
      {errorMessage && (
        <div className="p-3.5 rounded-lg bg-rose-950/40 border border-rose-800/50 text-xs text-rose-300">
          {errorMessage}
        </div>
      )}

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin" />
        </div>
      ) : journeys.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950/40 p-12 text-center">
          <div className="mx-auto w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 mb-3">
            <svg className="w-6 h-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </div>
          <h2 className="text-sm font-semibold text-slate-200">No learning journeys yet</h2>
          <p className="mt-1 text-xs text-slate-400 max-w-sm mx-auto">
            Create your first learning journey to begin structuring your skills and track your progress.
          </p>
          <div className="mt-5">
            <button
              onClick={openCreateModal}
              className="px-4 py-2 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors"
            >
              + Create your first journey
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {journeys.map((journey) => (
            <div
              key={journey.id}
              className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 flex flex-col justify-between hover:border-slate-700 transition-colors shadow-sm group"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <Link
                    href={`/journeys/${journey.id}`}
                    className="text-base font-semibold text-slate-100 hover:text-emerald-400 transition-colors line-clamp-1"
                  >
                    {journey.title}
                  </Link>
                  <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 shrink-0">
                    ID #{journey.id}
                  </span>
                </div>

                <p className="mt-2 text-xs text-slate-400 line-clamp-2 leading-relaxed">
                  {journey.description || 'No description provided.'}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800/70 flex items-center justify-between text-xs">
                <Link
                  href={`/journeys/${journey.id}`}
                  className="font-medium text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition-colors"
                >
                  <span>Explore journey</span>
                  <span>→</span>
                </Link>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => openEditModal(journey)}
                    className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition-colors"
                    title="Edit journey"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setDeletingJourney(journey)}
                    className="p-1 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors"
                    title="Delete journey"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create / Edit Journey Modal */}
      {(isCreateOpen || editingJourney) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h2 className="text-lg font-bold text-slate-100">
              {editingJourney ? 'Edit Learning Journey' : 'Create Learning Journey'}
            </h2>
            <p className="mt-1 text-xs text-slate-400">
              Define the title and goal of your learning path.
            </p>

            {formError && (
              <div className="mt-4 p-3 rounded-lg bg-rose-950/40 border border-rose-800/50 text-xs text-rose-300">
                {formError}
              </div>
            )}

            <form onSubmit={editingJourney ? handleUpdate : handleCreate} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Journey Title</label>
                <input
                  type="text"
                  required
                  value={formTitle}
                  onChange={(e) => setFormTitle(e.target.value)}
                  placeholder="e.g. Full-Stack Python & FastAPI"
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description</label>
                <textarea
                  rows={3}
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  placeholder="What will you master in this journey?"
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setIsCreateOpen(false);
                    setEditingJourney(null);
                  }}
                  className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium shadow-sm transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? 'Saving...' : editingJourney ? 'Save Changes' : 'Create Journey'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deletingJourney && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="w-full max-w-sm rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h2 className="text-base font-bold text-rose-400">Delete Learning Journey</h2>
            <p className="mt-2 text-xs text-slate-300">
              Are you sure you want to delete <span className="font-semibold text-white">&quot;{deletingJourney.title}&quot;</span>? This will permanently delete all associated sections, topics, and notes.
            </p>

            <div className="mt-6 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setDeletingJourney(null)}
                className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDelete}
                disabled={isSubmitting}
                className="px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium shadow-sm transition-colors disabled:opacity-50"
              >
                {isSubmitting ? 'Deleting...' : 'Confirm Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function JourneysPage() {
  return (
    <ProtectedRoute>
      <AppLayout>
        <JourneysContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
