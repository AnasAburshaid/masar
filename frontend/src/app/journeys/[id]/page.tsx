'use client';

import React, { useEffect, useState, useCallback, use, Suspense } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { journeyService } from '@/services/api/journeys';
import { sectionService } from '@/services/api/sections';
import { topicService } from '@/services/api/topics';
import { noteService } from '@/services/api/notes';
import { progressService } from '@/services/api/progress';
import { Journey, Section, Topic, Note } from '@/types/journey';
import { JourneyProgress } from '@/types/progress';
import { ApiError } from '@/services/api/errors';

interface JourneyDetailPageProps {
  params: Promise<{ id: string }>;
}

function JourneyDetailContent({ journeyId }: { journeyId: number }) {
  const router = useRouter();

  // Core data states
  const [journey, setJourney] = useState<Journey | null>(null);
  const [sections, setSections] = useState<Section[]>([]);
  const [topicsBySection, setTopicsBySection] = useState<Record<number, Topic[]>>({});
  const [progress, setProgress] = useState<JourneyProgress | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  // Section Modal & Form states
  const [isSectionModalOpen, setIsSectionModalOpen] = useState(false);
  const [editingSection, setEditingSection] = useState<Section | null>(null);
  const [sectionTitleInput, setSectionTitleInput] = useState('');

  // Topic Modal & Form states
  const [targetSectionIdForTopic, setTargetSectionIdForTopic] = useState<number | null>(null);
  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);
  const [topicTitleInput, setTopicTitleInput] = useState('');

  // Notes Drawer states
  const [selectedTopicForNotes, setSelectedTopicForNotes] = useState<Topic | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoadingNotes, setIsLoadingNotes] = useState(false);
  const [newNoteContent, setNewNoteContent] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [editingNoteContent, setEditingNoteContent] = useState('');

  // Submitting indicator
  const [isActionLoading, setIsActionLoading] = useState(false);

  // Load journey and all sections & topics
  const loadFullData = useCallback(async () => {
    setIsLoading(true);
    setErrorBanner(null);
    try {
      const [j, s, p] = await Promise.all([
        journeyService.getJourney(journeyId),
        sectionService.listSections(journeyId),
        progressService.getJourneyProgress(journeyId).catch(() => null),
      ]);
      setJourney(j);
      setSections(s);
      setProgress(p);

      // Load topics for each section in parallel
      const topicsMap: Record<number, Topic[]> = {};
      await Promise.all(
        s.map(async (sec) => {
          const tList = await topicService.listTopics(sec.id);
          topicsMap[sec.id] = tList;
        })
      );
      setTopicsBySection(topicsMap);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setErrorBanner(err.userMessage);
      } else {
        setErrorBanner('Failed to load journey details.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [journeyId]);

  useEffect(() => {
    let isCancelled = false;

    const fetchData = async () => {
      try {
        const [j, s, p] = await Promise.all([
          journeyService.getJourney(journeyId),
          sectionService.listSections(journeyId),
          progressService.getJourneyProgress(journeyId).catch(() => null),
        ]);
        if (isCancelled) return;
        setJourney(j);
        setSections(s);
        setProgress(p);

        const topicsMap: Record<number, Topic[]> = {};
        await Promise.all(
          s.map(async (sec) => {
            const tList = await topicService.listTopics(sec.id);
            topicsMap[sec.id] = tList;
          })
        );
        if (isCancelled) return;
        setTopicsBySection(topicsMap);
      } catch (err: unknown) {
        if (!isCancelled) {
          if (err instanceof ApiError) {
            setErrorBanner(err.userMessage);
          } else {
            setErrorBanner('Failed to load journey details.');
          }
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isCancelled = true;
    };
  }, [journeyId]);

  // Section Handlers
  const handleSaveSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sectionTitleInput.trim()) return;

    setIsActionLoading(true);
    try {
      if (editingSection) {
        await sectionService.updateSection(editingSection.id, { title: sectionTitleInput.trim() });
      } else {
        await sectionService.createSection({
          journey_id: journeyId,
          title: sectionTitleInput.trim(),
        });
      }
      setIsSectionModalOpen(false);
      setEditingSection(null);
      setSectionTitleInput('');
      await loadFullData();
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Section operation failed.');
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleDeleteSection = async (sectionId: number) => {
    if (!confirm('Are you sure you want to delete this section and all its topics?')) return;
    try {
      await sectionService.deleteSection(sectionId);
      await loadFullData();
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to delete section.');
    }
  };

  // Topic Handlers
  const handleSaveTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicTitleInput.trim()) return;

    setIsActionLoading(true);
    try {
      if (editingTopic) {
        await topicService.updateTopic(editingTopic.id, { title: topicTitleInput.trim() });
      } else if (targetSectionIdForTopic) {
        await topicService.createTopic({
          section_id: targetSectionIdForTopic,
          title: topicTitleInput.trim(),
        });
      }
      setTargetSectionIdForTopic(null);
      setEditingTopic(null);
      setTopicTitleInput('');
      await loadFullData();
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Topic operation failed.');
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleToggleTopicCompletion = async (topic: Topic) => {
    try {
      if (topic.is_completed) {
        await topicService.markPending(topic.id);
      } else {
        await topicService.markCompleted(topic.id);
      }
      await loadFullData();
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to update topic status.');
    }
  };

  const handleDeleteTopic = async (topicId: number) => {
    if (!confirm('Delete this topic and all its notes?')) return;
    try {
      await topicService.deleteTopic(topicId);
      if (selectedTopicForNotes?.id === topicId) {
        setSelectedTopicForNotes(null);
      }
      await loadFullData();
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to delete topic.');
    }
  };

  // Note Handlers
  const openNotesDrawer = async (topic: Topic) => {
    setSelectedTopicForNotes(topic);
    setNewNoteContent('');
    setEditingNoteId(null);
    await loadNotesForTopic(topic.id);
  };

  const loadNotesForTopic = async (topicId: number) => {
    setIsLoadingNotes(true);
    try {
      const data = await noteService.listNotes(topicId);
      setNotes(data);
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to load topic notes.');
    } finally {
      setIsLoadingNotes(false);
    }
  };

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTopicForNotes || !newNoteContent.trim()) return;

    setIsActionLoading(true);
    try {
      await noteService.createNote({
        topic_id: selectedTopicForNotes.id,
        content: newNoteContent.trim(),
      });
      setNewNoteContent('');
      await loadNotesForTopic(selectedTopicForNotes.id);
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to add note.');
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleUpdateNote = async (noteId: number) => {
    if (!editingNoteContent.trim() || !selectedTopicForNotes) return;
    try {
      await noteService.updateNote(noteId, { content: editingNoteContent.trim() });
      setEditingNoteId(null);
      await loadNotesForTopic(selectedTopicForNotes.id);
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to update note.');
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    if (!confirm('Delete this note?') || !selectedTopicForNotes) return;
    try {
      await noteService.deleteNote(noteId);
      await loadNotesForTopic(selectedTopicForNotes.id);
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to delete note.');
    }
  };

  const handleDeleteJourney = async () => {
    if (!confirm('Are you sure you want to delete this entire journey? This action cannot be undone.')) return;
    try {
      await journeyService.deleteJourney(journeyId);
      router.push('/journeys');
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to delete journey.');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="w-8 h-8 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin" />
      </div>
    );
  }

  if (!journey) {
    return (
      <div className="text-center py-16 space-y-4">
        <h2 className="text-base font-bold text-rose-600 dark:text-rose-400">Journey Not Found</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">The journey you requested does not exist or you do not have permission to view it.</p>
        <Link href="/journeys" className="inline-block px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs font-semibold text-slate-800 dark:text-slate-200">
          Back to Journeys
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Breadcrumb & Action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200/90 dark:border-slate-800/80">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-1">
            <Link href="/journeys" className="hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors font-medium">
              Journeys
            </Link>
            <span>/</span>
            <span className="text-slate-700 dark:text-slate-300 font-medium">Journey #{journey.id}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">{journey.title}</h1>
          <p className="mt-1 text-xs sm:text-sm text-slate-500 dark:text-slate-400 max-w-2xl">
            {journey.description || 'No description provided.'}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setSectionTitleInput('');
              setEditingSection(null);
              setIsSectionModalOpen(true);
            }}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
            </svg>
            <span>Add Section</span>
          </button>
          <button
            onClick={handleDeleteJourney}
            className="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-rose-50 dark:hover:bg-rose-950/20 text-slate-600 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 border border-slate-200 dark:border-slate-700 hover:border-rose-200 dark:hover:border-rose-900 text-xs font-semibold transition-colors cursor-pointer"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Real-Time Journey Progress Bar */}
      {progress && progress.total_topics > 0 && (
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200/90 dark:border-slate-800/80 shadow-xs space-y-2.5">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-500 dark:text-slate-400 font-medium">
              Roadmap Progress:{' '}
              <strong className="text-slate-900 dark:text-slate-100">{progress.completed_topics}</strong> of{' '}
              <strong className="text-slate-900 dark:text-slate-100">{progress.total_topics}</strong> topics completed
            </span>
            <span className={`font-bold ${progress.is_complete ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-800 dark:text-slate-200'}`}>
              {progress.percentage}% {progress.is_complete && '✓ Mastered'}
            </span>
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className={`h-2 rounded-full transition-all duration-700 ${
                progress.is_complete ? 'bg-emerald-500' : 'bg-gradient-to-r from-emerald-600 to-teal-400'
              }`}
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
        </div>
      )}

      {errorBanner && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/50 text-xs text-rose-700 dark:text-rose-300">
          {errorBanner}
        </div>
      )}

      {/* Sections and Topics list */}
      {sections.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-950/40 p-12 text-center">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">No sections in this journey yet</h3>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            Break down this learning journey into key sections (e.g., &quot;Fundamentals&quot;, &quot;Intermediate Patterns&quot;, &quot;Projects&quot;).
          </p>
          <div className="mt-5">
            <button
              onClick={() => {
                setSectionTitleInput('');
                setEditingSection(null);
                setIsSectionModalOpen(true);
              }}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-xs transition-colors cursor-pointer"
            >
              + Create First Section
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {sections.map((sec) => {
            const secTopics = topicsBySection[sec.id] || [];
            const completedCount = secTopics.filter((t) => t.is_completed).length;

            return (
              <div
                key={sec.id}
                className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/60 overflow-hidden shadow-xs"
              >
                {/* Section Header */}
                <div className="p-4 sm:p-5 bg-slate-50/80 dark:bg-slate-950/70 border-b border-slate-200/90 dark:border-slate-800/80 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    <div>
                      <h2 className="text-sm sm:text-base font-bold text-slate-900 dark:text-slate-100">{sec.title}</h2>
                      <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono font-medium">
                        {completedCount} of {secTopics.length} topics completed
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => {
                        setTargetSectionIdForTopic(sec.id);
                        setEditingTopic(null);
                        setTopicTitleInput('');
                      }}
                      className="px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold border border-slate-200 dark:border-slate-700 shadow-xs transition-colors cursor-pointer"
                    >
                      + Topic
                    </button>
                    <button
                      onClick={() => {
                        setEditingSection(sec);
                        setSectionTitleInput(sec.title);
                        setIsSectionModalOpen(true);
                      }}
                      title="Rename section"
                      className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleDeleteSection(sec.id)}
                      title="Delete section"
                      className="p-1.5 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/20 rounded-lg transition-colors cursor-pointer"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Topics List */}
                <div className="p-4 sm:p-5">
                  {secTopics.length === 0 ? (
                    <div className="text-center py-6 text-xs text-slate-500">
                      No topics added yet. Click &quot;+ Topic&quot; to add your first topic to this section.
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {secTopics.map((topic) => (
                        <div
                          key={topic.id}
                          className={`flex items-center justify-between p-3.5 rounded-xl border transition-all ${
                            topic.is_completed
                              ? 'bg-emerald-50/70 dark:bg-emerald-950/20 border-emerald-200/70 dark:border-emerald-900/30 text-emerald-950 dark:text-slate-300'
                              : 'bg-slate-50/60 dark:bg-slate-950/40 border-slate-200/80 dark:border-slate-800 text-slate-800 dark:text-slate-100 hover:border-slate-300 dark:hover:border-slate-700'
                          }`}
                        >
                          <div className="flex items-center gap-3 min-w-0 flex-1">
                            <input
                              type="checkbox"
                              checked={topic.is_completed}
                              onChange={() => handleToggleTopicCompletion(topic)}
                              className="w-4 h-4 rounded text-emerald-600 bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 focus:ring-emerald-500 cursor-pointer"
                            />
                            <span
                              className={`text-xs sm:text-sm font-medium truncate ${
                                topic.is_completed ? 'line-through text-slate-400 dark:text-slate-500' : ''
                              }`}
                            >
                              {topic.title}
                            </span>
                          </div>

                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => openNotesDrawer(topic)}
                              className="px-2.5 py-1 rounded-lg bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 border border-slate-200 dark:border-slate-700 shadow-xs transition-colors flex items-center gap-1 cursor-pointer"
                            >
                              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                              <span>Notes</span>
                            </button>
                            <button
                              onClick={() => {
                                setEditingTopic(topic);
                                setTopicTitleInput(topic.title);
                              }}
                              className="p-1 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg cursor-pointer"
                              title="Rename topic"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                            </button>
                            <button
                              onClick={() => handleDeleteTopic(topic.id)}
                              className="p-1 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 rounded-lg cursor-pointer"
                              title="Delete topic"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add / Edit Section Modal */}
      {isSectionModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-black/70 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              {editingSection ? 'Rename Section' : 'Create New Section'}
            </h3>
            <form onSubmit={handleSaveSection} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Section Title</label>
                <input
                  type="text"
                  required
                  value={sectionTitleInput}
                  onChange={(e) => setSectionTitleInput(e.target.value)}
                  placeholder="e.g. Asynchronous Programming with asyncio"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/70 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => {
                    setIsSectionModalOpen(false);
                    setEditingSection(null);
                  }}
                  className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isActionLoading}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs disabled:opacity-50 cursor-pointer"
                >
                  {isActionLoading ? 'Saving...' : editingSection ? 'Save Title' : 'Add Section'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add / Edit Topic Modal */}
      {(targetSectionIdForTopic || editingTopic) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-black/70 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              {editingTopic ? 'Rename Topic' : 'Add New Topic'}
            </h3>
            <form onSubmit={handleSaveTopic} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Topic Title</label>
                <input
                  type="text"
                  required
                  value={topicTitleInput}
                  onChange={(e) => setTopicTitleInput(e.target.value)}
                  placeholder="e.g. Coroutines, Tasks, and Event Loops"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/70 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => {
                    setTargetSectionIdForTopic(null);
                    setEditingTopic(null);
                  }}
                  className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isActionLoading}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs disabled:opacity-50 cursor-pointer"
                >
                  {isActionLoading ? 'Saving...' : editingTopic ? 'Update Topic' : 'Add Topic'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Notes Slide-over Drawer */}
      {selectedTopicForNotes && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-slate-900/60 dark:bg-black/70 backdrop-blur-xs">
          <div className="w-full max-w-lg h-full bg-white dark:bg-slate-950 border-l border-slate-200 dark:border-slate-800 p-6 flex flex-col justify-between shadow-2xl">
            <div className="space-y-4 flex-1 flex flex-col min-h-0">
              <div className="flex items-start justify-between pb-3 border-b border-slate-200/90 dark:border-slate-800">
                <div>
                  <span className="text-[10px] uppercase font-mono text-emerald-600 dark:text-emerald-400 font-bold">
                    Topic Notes
                  </span>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white line-clamp-1">
                    {selectedTopicForNotes.title}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedTopicForNotes(null)}
                  className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-white rounded-lg cursor-pointer"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Notes List */}
              <div className="flex-1 overflow-y-auto space-y-3 pr-1 min-h-0">
                {isLoadingNotes ? (
                  <div className="text-center py-10 text-xs text-slate-400">Loading notes...</div>
                ) : notes.length === 0 ? (
                  <div className="text-center py-10 text-xs text-slate-500 border border-dashed border-slate-200 dark:border-slate-800 rounded-xl p-6">
                    No notes recorded yet. Write key concepts, code snippets, or takeaways below.
                  </div>
                ) : (
                  notes.map((n) => (
                    <div
                      key={n.id}
                      className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800/80 space-y-2 text-xs shadow-xs"
                    >
                      {editingNoteId === n.id ? (
                        <div className="space-y-2">
                          <textarea
                            rows={3}
                            value={editingNoteContent}
                            onChange={(e) => setEditingNoteContent(e.target.value)}
                            className="w-full p-2.5 rounded-xl bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-xs"
                          />
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => setEditingNoteId(null)}
                              className="px-2.5 py-1 rounded-lg bg-slate-200 dark:bg-slate-800 text-[11px] font-semibold text-slate-700 dark:text-slate-300 cursor-pointer"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handleUpdateNote(n.id)}
                              className="px-3 py-1 rounded-lg bg-emerald-600 text-[11px] font-semibold text-white cursor-pointer"
                            >
                              Save
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <p className="text-slate-800 dark:text-slate-200 whitespace-pre-wrap leading-relaxed">{n.content}</p>
                          <div className="flex items-center justify-between text-[10px] text-slate-400 dark:text-slate-500 pt-1.5 border-t border-slate-200/80 dark:border-slate-800/60">
                            <span>Note #{n.id}</span>
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => {
                                  setEditingNoteId(n.id);
                                  setEditingNoteContent(n.content);
                                }}
                                className="text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 font-medium cursor-pointer"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleDeleteNote(n.id)}
                                className="text-rose-600 hover:text-rose-700 dark:text-rose-400 dark:hover:text-rose-300 font-medium cursor-pointer"
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        </>
                      )}
                    </div>
                  ))
                )}
              </div>

              {/* Add Note Input */}
              <form onSubmit={handleCreateNote} className="pt-3 border-t border-slate-200/90 dark:border-slate-800 space-y-2">
                <textarea
                  rows={3}
                  required
                  value={newNoteContent}
                  onChange={(e) => setNewNoteContent(e.target.value)}
                  placeholder="Record an observation, concept, or code snippet..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-400 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
                />
                <button
                  type="submit"
                  disabled={isActionLoading || !newNoteContent.trim()}
                  className="w-full py-2.5 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs transition-colors disabled:opacity-50 cursor-pointer"
                >
                  {isActionLoading ? 'Saving Note...' : 'Add Note'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function JourneyDetailPageInner({ params }: JourneyDetailPageProps) {
  const unwrappedParams = use(params);
  const journeyId = parseInt(unwrappedParams.id, 10);

  return (
    <ProtectedRoute>
      <AppLayout>
        <JourneyDetailContent journeyId={journeyId} />
      </AppLayout>
    </ProtectedRoute>
  );
}

export default function JourneyDetailPage({ params }: JourneyDetailPageProps) {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[var(--bg-page)] flex items-center justify-center">
          <div className="w-8 h-8 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin" />
        </div>
      }
    >
      <JourneyDetailPageInner params={params} />
    </Suspense>
  );
}
