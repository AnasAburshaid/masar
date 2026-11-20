'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { useAuth } from '@/context/AuthContext';
import { documentService } from '@/services/api/documents';
import { ApiError } from '@/services/api/errors';
import { profileService } from '@/services/api/profile';
import { DocumentItem } from '@/types/document';
import {
  LearningProfile,
  ProfileCategory,
  ProfileItem,
  SkillLevel,
} from '@/types/profile';

const CATEGORIES: { label: string; value: ProfileCategory }[] = [
  { label: 'All Categories', value: 'skill' },
  { label: 'Skills', value: 'skill' },
  { label: 'Technologies', value: 'technology' },
  { label: 'Languages', value: 'language' },
  { label: 'Experience', value: 'experience' },
  { label: 'Projects', value: 'project' },
  { label: 'Knowledge', value: 'knowledge' },
  { label: 'Goals', value: 'goal' },
];

const SKILL_LEVELS: { label: string; value: SkillLevel }[] = [
  { label: 'Beginner', value: 'beginner' },
  { label: 'Intermediate', value: 'intermediate' },
  { label: 'Advanced', value: 'advanced' },
  { label: 'Expert', value: 'expert' },
];

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<LearningProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Filter state
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Bio state
  const [isEditingBio, setIsEditingBio] = useState(false);
  const [bioInput, setBioInput] = useState('');
  const [isSavingBio, setIsSavingBio] = useState(false);

  // Add Item Modal
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newItemName, setNewItemName] = useState('');
  const [newItemCategory, setNewItemCategory] = useState<ProfileCategory>('skill');
  const [newItemLevel, setNewItemLevel] = useState<SkillLevel | ''>('intermediate');
  const [isSavingItem, setIsSavingItem] = useState(false);

  // Extract from Document Modal
  const [isExtractModalOpen, setIsExtractModalOpen] = useState(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);

  // Action status tracker
  const [actionInProgressId, setActionInProgressId] = useState<number | null>(null);

  const refreshProfile = useCallback(async () => {
    try {
      const data = await profileService.getProfile();
      setProfile(data);
      setBioInput(data.bio || '');
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMsg(err.detail || err.message);
      } else if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('Failed to refresh profile.');
      }
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    profileService.getProfile().then(
      (data) => {
        if (isMounted) {
          setProfile(data);
          setBioInput(data.bio || '');
          setIsLoading(false);
        }
      },
      (err: unknown) => {
        if (isMounted) {
          if (err instanceof ApiError) {
            setErrorMsg(err.detail || err.message);
          } else if (err instanceof Error) {
            setErrorMsg(err.message);
          } else {
            setErrorMsg('Failed to load profile.');
          }
          setIsLoading(false);
        }
      }
    );

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSaveBio = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSavingBio(true);
      setErrorMsg(null);
      const updated = await profileService.updateBio(bioInput);
      setProfile(updated);
      setIsEditingBio(false);
      setSuccessMsg('Bio updated successfully.');
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMsg(err.detail || err.message);
      } else {
        setErrorMsg('Failed to update bio.');
      }
    } finally {
      setIsSavingBio(false);
    }
  };

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemName.trim()) return;

    try {
      setIsSavingItem(true);
      setErrorMsg(null);
      await profileService.addItem({
        name: newItemName.trim(),
        category: newItemCategory,
        level: newItemLevel ? newItemLevel : null,
        is_confirmed: true,
      });
      setIsAddModalOpen(false);
      setNewItemName('');
      setSuccessMsg(`Added '${newItemName.trim()}' to your profile.`);
      setTimeout(() => setSuccessMsg(null), 3000);
      await refreshProfile();
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMsg(err.detail || err.message);
      } else {
        setErrorMsg('Failed to add profile item.');
      }
    } finally {
      setIsSavingItem(false);
    }
  };

  const handleConfirmItem = async (item: ProfileItem) => {
    try {
      setActionInProgressId(item.id);
      setErrorMsg(null);
      await profileService.confirmItem(item.id);
      setSuccessMsg(`Confirmed '${item.name}' as verified knowledge!`);
      setTimeout(() => setSuccessMsg(null), 3000);
      await refreshProfile();
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMsg(err.detail || err.message);
      } else {
        setErrorMsg('Failed to confirm item.');
      }
    } finally {
      setActionInProgressId(null);
    }
  };

  const handleDeleteItem = async (item: ProfileItem) => {
    if (!confirm(`Are you sure you want to remove '${item.name}'?`)) return;

    try {
      setActionInProgressId(item.id);
      setErrorMsg(null);
      await profileService.deleteItem(item.id);
      setSuccessMsg(`Removed '${item.name}'.`);
      setTimeout(() => setSuccessMsg(null), 3000);
      await refreshProfile();
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMsg(err.detail || err.message);
      } else {
        setErrorMsg('Failed to delete item.');
      }
    } finally {
      setActionInProgressId(null);
    }
  };

  const handleOpenExtractModal = async () => {
    setIsExtractModalOpen(true);
    try {
      setIsLoadingDocs(true);
      const docs = await documentService.listDocuments();
      setDocuments(docs);
      if (docs.length > 0) {
        setSelectedDocId(docs[0].id);
      }
    } catch {
      setErrorMsg('Failed to load documents for extraction.');
    } finally {
      setIsLoadingDocs(false);
    }
  };

  const handleExtractFromDocument = async () => {
    if (!selectedDocId) return;

    try {
      setIsExtracting(true);
      setErrorMsg(null);
      const res = await profileService.extractFromDocument(selectedDocId);
      setIsExtractModalOpen(false);
      setSuccessMsg(
        `Extracted ${res.extracted_items.length} new items from document! Review and confirm them below.`
      );
      setTimeout(() => setSuccessMsg(null), 4000);
      await refreshProfile();
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMsg(err.detail || err.message);
      } else {
        setErrorMsg('Failed to extract skills from document.');
      }
    } finally {
      setIsExtracting(false);
    }
  };

  const confirmedList = profile?.confirmed_items || [];
  const inferredList = profile?.inferred_items || [];

  const filteredConfirmed =
    selectedCategory === 'all'
      ? confirmedList
      : confirmedList.filter((item) => item.category === selectedCategory);

  const getLevelBadge = (level?: SkillLevel | null) => {
    if (!level) return null;
    const colors: Record<SkillLevel, string> = {
      beginner:
        'bg-blue-100 text-blue-800 dark:bg-blue-950/50 dark:text-blue-300 border-blue-200 dark:border-blue-800',
      intermediate:
        'bg-teal-100 text-teal-800 dark:bg-teal-950/50 dark:text-teal-300 border-teal-200 dark:border-teal-800',
      advanced:
        'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/50 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800',
      expert:
        'bg-purple-100 text-purple-800 dark:bg-purple-950/50 dark:text-purple-300 border-purple-200 dark:border-purple-800',
    };

    return (
      <span
        className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border ${colors[level]}`}
      >
        {level.charAt(0).toUpperCase() + level.slice(1)}
      </span>
    );
  };

  const getCategoryBadge = (category: ProfileCategory) => {
    return (
      <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
        {category}
      </span>
    );
  };

  return (
    <ProtectedRoute>
      <AppLayout>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
          {/* Header Banner */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  Personal Learning Knowledge Profile
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                  AI Context Ready
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                Your verified skills, background, and goals automatically inform your AI Mentor&apos;s adaptive guidance.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleOpenExtractModal}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors shadow-sm"
              >
                <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                <span>Extract from Document</span>
              </button>

              <button
                onClick={() => setIsAddModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-600/20 transition-all"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>Add Skill / Goal</span>
              </button>
            </div>
          </div>

          {/* Feedback messages */}
          {errorMsg && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300 text-sm flex items-center justify-between">
              <span>{errorMsg}</span>
              <button onClick={() => setErrorMsg(null)} className="font-bold ml-4">✕</button>
            </div>
          )}

          {successMsg && (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 dark:bg-emerald-950/40 dark:border-emerald-900 dark:text-emerald-300 text-sm flex items-center justify-between">
              <span>{successMsg}</span>
              <button onClick={() => setSuccessMsg(null)} className="font-bold ml-4">✕</button>
            </div>
          )}

          {/* User Bio Card */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white font-bold text-sm shadow-sm">
                  {user?.email?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div>
                  <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                    {user?.email || 'Learner Profile'}
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Professional Summary & Background
                  </p>
                </div>
              </div>

              {!isEditingBio && (
                <button
                  onClick={() => setIsEditingBio(true)}
                  className="text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:underline"
                >
                  Edit Bio
                </button>
              )}
            </div>

            {isEditingBio ? (
              <form onSubmit={handleSaveBio} className="space-y-3">
                <textarea
                  value={bioInput}
                  onChange={(e) => setBioInput(e.target.value)}
                  placeholder="e.g. Senior Backend Engineer with 5+ years experience in Python and microservices architecture..."
                  rows={3}
                  maxLength={1000}
                  className="w-full text-sm p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setIsEditingBio(false);
                      setBioInput(profile?.bio || '');
                    }}
                    className="px-3 py-1.5 text-xs font-medium rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSavingBio}
                    className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50"
                  >
                    {isSavingBio ? 'Saving...' : 'Save Bio'}
                  </button>
                </div>
              </form>
            ) : (
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed italic">
                {profile?.bio
                  ? `“${profile.bio}”`
                  : 'No professional bio provided yet. Add a short summary to help the AI mentor contextualize your learning pace.'}
              </p>
            )}
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Total Items</span>
              <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                {profile?.total_items || 0}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">Verified Skills</span>
              <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                {confirmedList.length}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-medium text-amber-600 dark:text-amber-400">Pending Review</span>
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">
                {inferredList.length}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-medium text-indigo-600 dark:text-indigo-400">Active Goals</span>
              <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">
                {confirmedList.filter((i) => i.category === 'goal').length}
              </p>
            </div>
          </div>

          {/* Inferred Items Pending Review Banner */}
          {inferredList.length > 0 && (
            <div className="p-6 rounded-2xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-800/60 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="w-3 h-3 rounded-full bg-amber-500 animate-pulse" />
                  <h3 className="text-sm font-bold text-amber-900 dark:text-amber-300">
                    AI-Inferred Items Pending Your Approval ({inferredList.length})
                  </h3>
                </div>
                <span className="text-xs text-amber-700 dark:text-amber-400">
                  Human-in-the-loop: Only verified items are permanently locked in your profile.
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {inferredList.map((item) => (
                  <div
                    key={item.id}
                    className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-900/60 flex items-center justify-between gap-3 shadow-sm"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-slate-900 dark:text-white">
                          {item.name}
                        </span>
                        {getCategoryBadge(item.category)}
                        {getLevelBadge(item.level)}
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">
                        Source: {item.source_type} {item.source_id ? `#${item.source_id}` : ''}
                      </p>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      <button
                        onClick={() => handleConfirmItem(item)}
                        disabled={actionInProgressId === item.id}
                        className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50 transition-colors shadow-sm"
                        title="Confirm and verify this item"
                      >
                        ✓ Confirm
                      </button>
                      <button
                        onClick={() => handleDeleteItem(item)}
                        disabled={actionInProgressId === item.id}
                        className="p-1 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
                        title="Reject / Dismiss"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Confirmed Knowledge Base */}
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  Confirmed Knowledge & Goals
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Items verified by you and actively injected into your AI mentor&apos;s system prompt.
                </p>
              </div>

              {/* Category Filter Pills */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
                <button
                  onClick={() => setSelectedCategory('all')}
                  className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                    selectedCategory === 'all'
                      ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
                  }`}
                >
                  All ({confirmedList.length})
                </button>
                {CATEGORIES.slice(1).map((cat) => {
                  const count = confirmedList.filter((i) => i.category === cat.value).length;
                  return (
                    <button
                      key={cat.value}
                      onClick={() => setSelectedCategory(cat.value)}
                      className={`px-3 py-1 text-xs font-medium rounded-full whitespace-nowrap transition-colors ${
                        selectedCategory === cat.value
                          ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
                      }`}
                    >
                      {cat.label} ({count})
                    </button>
                  );
                })}
              </div>
            </div>

            {isLoading ? (
              <div className="p-12 text-center text-slate-400">Loading your knowledge profile...</div>
            ) : filteredConfirmed.length === 0 ? (
              <div className="p-12 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                  No verified items found in this category.
                </p>
                <button
                  onClick={() => setIsAddModalOpen(true)}
                  className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline"
                >
                  + Add your first item
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {filteredConfirmed.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col justify-between space-y-3"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        {getCategoryBadge(item.category)}
                        {getLevelBadge(item.level)}
                      </div>
                      <h4 className="font-semibold text-slate-900 dark:text-white text-base">
                        {item.name}
                      </h4>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800/80 text-[11px] text-slate-400">
                      <span>Source: {item.source_type}</span>
                      <button
                        onClick={() => handleDeleteItem(item)}
                        disabled={actionInProgressId === item.id}
                        className="text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 transition-colors"
                        title="Delete item"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Add Item Modal */}
          {isAddModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
              <div className="w-full max-w-md p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Add Knowledge or Goal
                  </h3>
                  <button
                    onClick={() => setIsAddModalOpen(false)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    ✕
                  </button>
                </div>

                <form onSubmit={handleAddItem} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                      Item Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={newItemName}
                      onChange={(e) => setNewItemName(e.target.value)}
                      placeholder="e.g. Python, Docker, Next.js, System Design"
                      className="w-full text-sm p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                      Category *
                    </label>
                    <select
                      value={newItemCategory}
                      onChange={(e) => setNewItemCategory(e.target.value as ProfileCategory)}
                      className="w-full text-sm p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                      {CATEGORIES.slice(1).map((cat) => (
                        <option key={cat.value} value={cat.value}>
                          {cat.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                      Proficiency Level (Optional)
                    </label>
                    <select
                      value={newItemLevel}
                      onChange={(e) => setNewItemLevel(e.target.value as SkillLevel | '')}
                      className="w-full text-sm p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                      <option value="">None / Not Applicable</option>
                      {SKILL_LEVELS.map((lvl) => (
                        <option key={lvl.value} value={lvl.value}>
                          {lvl.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex justify-end gap-2 pt-2">
                    <button
                      type="button"
                      onClick={() => setIsAddModalOpen(false)}
                      className="px-3.5 py-2 text-xs font-medium rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isSavingItem || !newItemName.trim()}
                      className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50 shadow-sm"
                    >
                      {isSavingItem ? 'Saving...' : 'Add to Profile'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Extract From Document Modal */}
          {isExtractModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
              <div className="w-full max-w-md p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Extract Profile from Document
                  </h3>
                  <button
                    onClick={() => setIsExtractModalOpen(false)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    ✕
                  </button>
                </div>

                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Select an uploaded resume or syllabus. AI will extract skills, technologies, and goals, placing them in your profile awaiting your confirmation.
                </p>

                {isLoadingDocs ? (
                  <div className="py-6 text-center text-xs text-slate-400">Loading documents...</div>
                ) : documents.length === 0 ? (
                  <div className="py-6 text-center text-xs text-slate-400 space-y-2">
                    <p>No documents uploaded yet.</p>
                    <p className="text-slate-500">
                      Upload a document in AI Chat or the Document Manager first.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
                      Select Document
                    </label>
                    <select
                      value={selectedDocId || ''}
                      onChange={(e) => setSelectedDocId(Number(e.target.value))}
                      className="w-full text-sm p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                      {documents.map((doc) => (
                        <option key={doc.id} value={doc.id}>
                          {doc.filename} ({doc.file_type})
                        </option>
                      ))}
                    </select>

                    <div className="flex justify-end gap-2 pt-4">
                      <button
                        type="button"
                        onClick={() => setIsExtractModalOpen(false)}
                        className="px-3.5 py-2 text-xs font-medium rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={handleExtractFromDocument}
                        disabled={isExtracting || !selectedDocId}
                        className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50 shadow-sm"
                      >
                        {isExtracting ? 'Analyzing...' : 'Extract Skills'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}
