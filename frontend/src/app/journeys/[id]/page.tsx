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

  // Load notes for selected topic
  const loadNotesForTopic = async (topicId: number) => {
    setIsLoadingNotes(true);
    try {
      const nList = await noteService.listNotes(topicId);
      setNotes(nList);
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to load notes.');
    } finally {
      setIsLoadingNotes(false);
    }
  };

  const openNotesDrawer = (topic: Topic) => {
    setSelectedTopicForNotes(topic);
    setNewNoteContent('');
    setEditingNoteId(null);
    loadNotesForTopic(topic.id);
  };

  // Section Handlers
  const handleSaveSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sectionTitleInput.trim()) return;

    setIsActionLoading(true);
    try {
      if (editingSection) {
        await sectionService.updateSection(editingSection.id, { title: sectionTitleInput.trim() });
      } else {
        await sectionService.createSection({ journey_id: journeyId, title: sectionTitleInput.trim() });
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
    setIsActionLoading(true);
    try {
      await sectionService.deleteSection(sectionId);
      await loadFullData();
    } catch (err: unknown) {
      setErrorBanner(err instanceof ApiError ? err.userMessage : 'Failed to delete section.');
    } finally {
      setIsActionLoading(false);
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
    if (!confirm('Are you sure you want to delete this entire journey? This action is permanent.')) return;
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
        <h2 className="text-base font-semibold text-rose-400">Journey Not Found</h2>
        <p className="text-xs text-slate-400">The journey you requested does not exist or you do not have permission to view it.</p>
        <Link href="/journeys" className="inline-block px-4 py-2 rounded-lg bg-slate-800 text-xs text-slate-200">
          Back to Journeys
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Breadcrumb & Action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
            <Link href="/journeys" className="hover:text-emerald-400 transition-colors">
              Journeys
            </Link>
            <span>/</span>
            <span className="text-slate-300">Journey #{journey.id}</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">{journey.title}</h1>
          <p className="mt-1 text-xs sm:text-sm text-slate-400 max-w-2xl">
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
            className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium shadow-sm transition-colors flex items-center gap-1.5"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Add Section</span>
          </button>
          <button
            onClick={handleDeleteJourney}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-700 hover:border-rose-500/30 text-xs font-medium transition-colors"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Journey Progress Bar */}
      {progress && progress.total_topics > 0 && (
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">
              Journey Progress:{' '}
              <strong className="text-slate-200">{progress.completed_topics}</strong> of{' '}
              <strong className="text-slate-200">{progress.total_topics}</strong> topics completed
            </span>
            <span className={`font-semibold ${progress.is_complete ? 'text-emerald-400' : 'text-slate-200'}`}>
              {progress.percentage}% {progress.is_complete && '✓ Mastered'}
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                progress.is_complete ? 'bg-emerald-500' : 'bg-gradient-to-r from-emerald-600 to-teal-400'
              }`}
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
        </div>
      )}

      {errorBanner && (
        <div className="p-3.5 rounded-lg bg-rose-950/40 border border-rose-800/50 text-xs text-rose-300">
          {errorBanner}
        </div>
      )}

      {/* Sections and Topics list */}
      {sections.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950/40 p-12 text-center">
          <h3 className="text-sm font-semibold text-slate-200">No sections in this journey yet</h3>
          <p className="mt-1 text-xs text-slate-400 max-w-sm mx-auto">
            Break down this learning journey into key sections (e.g., &quot;Fundamentals&quot;, &quot;Intermediate Patterns&quot;, &quot;Projects&quot;).
          </p>
          <div className="mt-4">
            <button
              onClick={() => {
                setSectionTitleInput('');
                setEditingSection(null);
                setIsSectionModalOpen(true);
              }}
              className="px-4 py-2 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors"
            >
              + Create first section
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
                className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-sm"
              >
                {/* Section Header */}
                <div className="p-4 sm:p-5 bg-slate-950/70 border-b border-slate-800/80 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-emerald-500" />
                    <div>
                      <h2 className="text-sm sm:text-base font-semibold text-slate-100">{sec.title}</h2>
                      <span className="text-[11px] text-slate-400 font-mono">
                        {completedCount} of {secTopics.length} topics completed
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        setTargetSectionIdForTopic(sec.id);
                        setEditingTopic(null);
                        setTopicTitleInput('');
                      }}
                      className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
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
                      className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition-colors"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleDeleteSection(sec.id)}
                      title="Delete section"
                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors"
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
                          className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                            topic.is_completed
                              ? 'bg-emerald-950/20 border-emerald-900/30 text-slate-300'
                              : 'bg-slate-950/40 border-slate-800 text-slate-100 hover:border-slate-700'
                          }`}
                        >
                          <div className="flex items-center gap-3 min-w-0 flex-1">
                            <input
                              type="checkbox"
                              checked={topic.is_completed}
                              onChange={() => handleToggleTopicCompletion(topic)}
                              className="w-4 h-4 rounded text-emerald-600 bg-slate-900 border-slate-700 focus:ring-emerald-500 cursor-pointer"
                            />
                            <span
                              className={`text-xs sm:text-sm font-medium truncate ${
                                topic.is_completed ? 'line-through text-slate-400' : ''
                              }`}
                            >
                              {topic.title}
                            </span>
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => openNotesDrawer(topic)}
                              className="px-2.5 py-1 rounded bg-slate-800/80 hover:bg-slate-800 text-[11px] font-medium text-emerald-400 hover:text-emerald-300 border border-slate-700 transition-colors flex items-center gap-1"
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
                              className="p-1 text-slate-400 hover:text-slate-200 rounded"
                              title="Rename topic"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                            </button>
                            <button
                              onClick={() => handleDeleteTopic(topic.id)}
                              className="p-1 text-slate-400 hover:text-rose-400 rounded"
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-base font-bold text-slate-100">
              {editingSection ? 'Rename Section' : 'Create New Section'}
            </h3>
            <form onSubmit={handleSaveSection} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Section Title</label>
                <input
                  type="text"
                  required
                  value={sectionTitleInput}
                  onChange={(e) => setSectionTitleInput(e.target.value)}
                  placeholder="e.g. Asynchronous Programming with asyncio"
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setIsSectionModalOpen(false);
                    setEditingSection(null);
                  }}
                  className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isActionLoading}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium shadow-sm disabled:opacity-50"
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h3 className="text-base font-bold text-slate-100">
              {editingTopic ? 'Rename Topic' : 'Add New Topic'}
            </h3>
            <form onSubmit={handleSaveTopic} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Topic Title</label>
                <input
                  type="text"
                  required
                  value={topicTitleInput}
                  onChange={(e) => setTopicTitleInput(e.target.value)}
                  placeholder="e.g. Coroutines, Tasks, and Event Loops"
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setTargetSectionIdForTopic(null);
                    setEditingTopic(null);
                  }}
                  className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isActionLoading}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium shadow-sm disabled:opacity-50"
                >
                  {isActionLoading ? 'Saving...' : editingTopic ? 'Update Topic' : 'Add Topic'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Notes Slide-over Drawer / Modal */}
      {selectedTopicForNotes && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-xs">
          <div className="w-full max-w-lg h-full bg-slate-950 border-l border-slate-800 p-6 flex flex-col justify-between shadow-2xl">
            <div className="space-y-4 flex-1 flex flex-col min-h-0">
              <div className="flex items-start justify-between pb-3 border-b border-slate-800">
                <div>
                  <span className="text-[10px] uppercase font-mono text-emerald-400 font-semibold">
                    Topic Notes
                  </span>
                  <h3 className="text-base font-bold text-slate-100 line-clamp-1">
                    {selectedTopicForNotes.title}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedTopicForNotes(null)}
                  className="p-1 text-slate-400 hover:text-white rounded"
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
                  <div className="text-center py-10 text-xs text-slate-500 border border-dashed border-slate-800 rounded-lg p-6">
                    No notes recorded yet. Write key concepts, code snippets, or takeaways below.
                  </div>
                ) : (
                  notes.map((n) => (
                    <div
                      key={n.id}
                      className="p-3.5 rounded-lg bg-slate-900 border border-slate-800/80 space-y-2 text-xs"
                    >
                      {editingNoteId === n.id ? (
                        <div className="space-y-2">
                          <textarea
                            rows={3}
                            value={editingNoteContent}
                            onChange={(e) => setEditingNoteContent(e.target.value)}
                            className="w-full p-2 rounded bg-slate-950 border border-slate-700 text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                          />
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => setEditingNoteId(null)}
                              className="px-2.5 py-1 rounded bg-slate-800 text-[11px] text-slate-300"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handleUpdateNote(n.id)}
                              className="px-3 py-1 rounded bg-emerald-600 text-[11px] text-white"
                            >
                              Save
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <p className="text-slate-200 whitespace-pre-wrap leading-relaxed">{n.content}</p>
                          <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                            <span>Note #{n.id}</span>
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => {
                                  setEditingNoteId(n.id);
                                  setEditingNoteContent(n.content);
                                }}
                                className="text-slate-400 hover:text-slate-200"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleDeleteNote(n.id)}
                                className="text-rose-400 hover:text-rose-300"
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
              <form onSubmit={handleCreateNote} className="pt-3 border-t border-slate-800 space-y-2">
                <textarea
                  rows={3}
                  required
                  value={newNoteContent}
                  onChange={(e) => setNewNoteContent(e.target.value)}
                  placeholder="Record an observation, concept, or code snippet..."
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
                <button
                  type="submit"
                  disabled={isActionLoading || !newNoteContent.trim()}
                  className="w-full py-2 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium shadow-sm transition-colors disabled:opacity-50"
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
        <div className="min-h-screen bg-slate-950 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin" />
        </div>
      }
    >
      <JourneyDetailPageInner params={params} />
    </Suspense>
  );
}
