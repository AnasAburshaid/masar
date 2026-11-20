'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ActionProposal, ProposedAction } from '@/types/action';

interface ActionProposalCardProps {
  proposal: ActionProposal;
  onApprove: (proposalId: number) => Promise<void>;
  onReject: (proposalId: number) => Promise<void>;
  onRequestEdit?: (suggestion: string) => void;
}

interface ParsedSection {
  title: string;
  actionIndex: number;
  topics: ParsedTopic[];
}

interface ParsedTopic {
  title: string;
  actionIndex: number;
  notes: string[];
}

interface ParsedJourneyProposal {
  journeyTitle: string;
  journeyDescription: string;
  sections: ParsedSection[];
  totalTopics: number;
  totalNotes: number;
  createdJourneyId?: number;
}

function parseJourneyPlan(actions: ProposedAction[], proposal: ActionProposal): ParsedJourneyProposal | null {
  const journeyAction = actions.find((a) => a.tool === 'create_journey');
  if (!journeyAction) return null;

  const journeyTitle = (journeyAction.parameters.title as string) || 'New Learning Journey';
  const journeyDescription = (journeyAction.parameters.description as string) || '';

  const sections: ParsedSection[] = [];
  let currentSection: ParsedSection | null = null;
  let currentTopic: ParsedTopic | null = null;
  let totalTopics = 0;
  let totalNotes = 0;

  actions.forEach((act, idx) => {
    if (act.tool === 'create_section') {
      currentSection = {
        title: (act.parameters.title as string) || `Section ${sections.length + 1}`,
        actionIndex: idx,
        topics: [],
      };
      sections.push(currentSection);
      currentTopic = null;
    } else if (act.tool === 'create_topic') {
      totalTopics++;
      currentTopic = {
        title: (act.parameters.title as string) || 'Untitled Topic',
        actionIndex: idx,
        notes: [],
      };
      if (currentSection) {
        currentSection.topics.push(currentTopic);
      } else {
        // Fallback section if topics defined before sections
        const defaultSec: ParsedSection = {
          title: 'Core Curriculum',
          actionIndex: idx,
          topics: [currentTopic],
        };
        sections.push(defaultSec);
        currentSection = defaultSec;
      }
    } else if (act.tool === 'create_note') {
      totalNotes++;
      const noteContent = (act.parameters.content as string) || '';
      if (currentTopic) {
        currentTopic.notes.push(noteContent);
      }
    }
  });

  // Extract created journey ID if executed successfully
  let createdJourneyId: number | undefined;
  if (proposal.status === 'executed' && proposal.results.length > 0) {
    const journeyResult = proposal.results.find((r) => r.tool === 'create_journey' && r.status === 'success');
    if (journeyResult?.data && typeof journeyResult.data.id === 'number') {
      createdJourneyId = journeyResult.data.id;
    }
  }

  return {
    journeyTitle,
    journeyDescription,
    sections,
    totalTopics,
    totalNotes,
    createdJourneyId,
  };
}

export const ActionProposalCard: React.FC<ActionProposalCardProps> = ({
  proposal,
  onApprove,
  onReject,
  onRequestEdit,
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<number, boolean>>({ 0: true });

  const toggleSection = (idx: number) => {
    setExpandedSections((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const handleApprove = async () => {
    try {
      setIsProcessing(true);
      await onApprove(proposal.id);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    try {
      setIsProcessing(true);
      await onReject(proposal.id);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEditRequest = () => {
    if (onRequestEdit) {
      onRequestEdit(`I would like to refine the "${proposal.title}" plan: `);
    }
  };

  const journeyPlan = parseJourneyPlan(proposal.actions, proposal);

  const getStatusBadge = () => {
    switch (proposal.status) {
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            Pending Approval
          </span>
        );
      case 'executed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30">
            ✓ Executed Successfully
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-700 dark:text-rose-400 border border-rose-500/30">
            ✕ Execution Failed
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-500/15 text-slate-600 dark:text-slate-400 border border-slate-500/30">
            Declined
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
            {proposal.status}
          </span>
        );
    }
  };

  return (
    <div className="w-full my-4 rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-md overflow-hidden transition-all">
      {/* Header Bar */}
      <div className="px-5 py-4 bg-gradient-to-r from-slate-50 to-slate-100/60 dark:from-slate-900/90 dark:to-slate-800/50 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 truncate">
          <div className="w-8 h-8 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-sm font-bold shadow-xs">
            ⚡
          </div>
          <div className="truncate">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate">
              {proposal.title}
            </h4>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">
              AI Action Proposal • {proposal.actions.length} operation{proposal.actions.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
        <div>{getStatusBadge()}</div>
      </div>

      {/* Destructive Warning Callout */}
      {proposal.has_destructive_actions && (
        <div className="px-5 py-2.5 bg-amber-500/10 border-b border-amber-500/20 text-amber-800 dark:text-amber-300 text-xs flex items-center gap-2.5">
          <span className="text-base">⚠️</span>
          <span>
            <strong>Warning:</strong> This proposal includes destructive operations (e.g. deletion of existing roadmaps or topics). Please review carefully before approving.
          </span>
        </div>
      )}

      {/* Plan Preview Body */}
      <div className="p-5">
        {journeyPlan ? (
          /* Structured Learning Roadmap Tree View */
          <div className="space-y-4">
            {/* Journey Meta Card */}
            <div className="p-4 rounded-xl bg-emerald-50/40 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-800/40">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                    Proposed Learning Journey
                  </div>
                  <h3 className="text-base font-extrabold text-slate-900 dark:text-white mt-0.5">
                    {journeyPlan.journeyTitle}
                  </h3>
                  {journeyPlan.journeyDescription && (
                    <p className="text-xs text-slate-600 dark:text-slate-300 mt-1.5 leading-relaxed">
                      {journeyPlan.journeyDescription}
                    </p>
                  )}
                </div>
              </div>

              {/* Metrics Pill Bar */}
              <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-emerald-200/40 dark:border-emerald-800/40 text-[11px] text-slate-600 dark:text-slate-300">
                <span className="font-semibold text-emerald-700 dark:text-emerald-300">
                  📑 {journeyPlan.sections.length} Section{journeyPlan.sections.length !== 1 ? 's' : ''}
                </span>
                <span>•</span>
                <span className="font-semibold text-emerald-700 dark:text-emerald-300">
                  📌 {journeyPlan.totalTopics} Topic{journeyPlan.totalTopics !== 1 ? 's' : ''}
                </span>
                {journeyPlan.totalNotes > 0 && (
                  <>
                    <span>•</span>
                    <span className="font-semibold text-emerald-700 dark:text-emerald-300">
                      📝 {journeyPlan.totalNotes} Exercise/Note{journeyPlan.totalNotes !== 1 ? 's' : ''}
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Sections & Topics Accordion */}
            <div className="space-y-2.5">
              <div className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Curriculum Breakdown:
              </div>
              {journeyPlan.sections.map((section, sIdx) => {
                const isExpanded = Boolean(expandedSections[sIdx]);
                return (
                  <div
                    key={sIdx}
                    className="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 overflow-hidden"
                  >
                    <button
                      type="button"
                      onClick={() => toggleSection(sIdx)}
                      className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-slate-100/60 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="w-5 h-5 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-bold flex items-center justify-center">
                          {sIdx + 1}
                        </span>
                        <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                          {section.title}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          ({section.topics.length} topic{section.topics.length !== 1 ? 's' : ''})
                        </span>
                      </div>
                      <span className="text-xs text-slate-400">
                        {isExpanded ? '▲' : '▼'}
                      </span>
                    </button>

                    {isExpanded && (
                      <div className="px-4 pb-3.5 pt-1 space-y-2 border-t border-slate-200/60 dark:border-slate-800/60 bg-white dark:bg-slate-900">
                        {section.topics.map((topic, tIdx) => (
                          <div
                            key={tIdx}
                            className="p-2.5 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-950/20 text-xs"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-slate-800 dark:text-slate-200">
                                {topic.title}
                              </span>
                              <span className="text-[10px] text-slate-400">
                                Step {tIdx + 1}
                              </span>
                            </div>
                            {topic.notes.map((note, nIdx) => (
                              <div
                                key={nIdx}
                                className="mt-2 pl-3 py-1 border-l-2 border-teal-500 bg-teal-500/5 rounded-r text-[11px] text-slate-600 dark:text-slate-300"
                              >
                                <span className="font-semibold text-teal-600 dark:text-teal-400 mr-1">
                                  Task:
                                </span>
                                {note}
                              </div>
                            ))}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          /* General Action Operations List (Updates, Deletes, Toggles) */
          <div className="space-y-2.5">
            <div className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Operations to Execute:
            </div>
            {proposal.actions.map((act, idx) => {
              const result = proposal.results.find((r) => r.action_index === idx);
              return (
                <div
                  key={idx}
                  className={`p-3 rounded-xl border text-xs transition-colors ${
                    act.is_destructive
                      ? 'border-rose-200 dark:border-rose-900/50 bg-rose-50/30 dark:bg-rose-950/20'
                      : 'border-slate-200 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-950/30'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center text-[10px] font-mono text-slate-600 dark:text-slate-400">
                        {idx + 1}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] font-mono font-bold ${
                          act.is_destructive
                            ? 'bg-rose-100 dark:bg-rose-900/60 text-rose-700 dark:text-rose-300'
                            : 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300'
                        }`}
                      >
                        {act.tool.replace(/_/g, ' ').toUpperCase()}
                      </span>
                      <span className="font-medium text-slate-800 dark:text-slate-200">
                        {act.description || act.tool}
                      </span>
                    </div>

                    {result && (
                      <span
                        className={`text-[11px] font-semibold ${
                          result.status === 'success'
                            ? 'text-emerald-600 dark:text-emerald-400'
                            : 'text-rose-600 dark:text-rose-400'
                        }`}
                      >
                        {result.status === 'success' ? '✓ Done' : `✕ Failed`}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Technical Parameters Toggle */}
        <div className="mt-4 pt-2 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            {proposal.actions.length} automated service step{proposal.actions.length !== 1 ? 's' : ''}
          </span>
          <button
            type="button"
            onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
            className="text-[11px] text-slate-500 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
          >
            {showTechnicalDetails ? 'Hide technical schemas ▲' : 'View technical schemas ▼'}
          </button>
        </div>

        {showTechnicalDetails && (
          <div className="mt-2 p-3 rounded-xl bg-slate-900 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-48">
            <pre>{JSON.stringify(proposal.actions, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* Footer Controls */}
      <div className="px-5 py-3.5 bg-slate-50/80 dark:bg-slate-800/40 border-t border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3">
        {proposal.status === 'pending' ? (
          <>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Review carefully before execution. No changes are applied automatically.
            </p>
            <div className="flex items-center gap-2.5">
              <button
                type="button"
                disabled={isProcessing}
                onClick={handleReject}
                className="px-3.5 py-1.5 rounded-xl border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold disabled:opacity-50 transition-colors"
              >
                Reject Plan
              </button>
              {onRequestEdit && (
                <button
                  type="button"
                  disabled={isProcessing}
                  onClick={handleEditRequest}
                  className="px-3.5 py-1.5 rounded-xl border border-emerald-300 dark:border-emerald-700 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 text-xs font-semibold disabled:opacity-50 transition-colors"
                >
                  Refine with AI ✎
                </button>
              )}
              <button
                type="button"
                disabled={isProcessing}
                onClick={handleApprove}
                className="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs disabled:opacity-50 transition-all flex items-center gap-1.5"
              >
                {isProcessing ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Executing Plan...</span>
                  </>
                ) : (
                  <span>Approve & Create Roadmap →</span>
                )}
              </button>
            </div>
          </>
        ) : proposal.status === 'executed' ? (
          <div className="w-full flex items-center justify-between">
            <span className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1.5">
              <span>✓</span>
              <span>All changes applied to your learning dashboard.</span>
            </span>
            {journeyPlan?.createdJourneyId && (
              <Link
                href={`/journeys/${journeyPlan.createdJourneyId}`}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs transition-all"
              >
                <span>Open Journey Canvas →</span>
              </Link>
            )}
          </div>
        ) : (
          <div className="w-full text-right text-xs text-slate-400">
            Status: <span className="font-semibold capitalize">{proposal.status}</span>
          </div>
        )}
      </div>
    </div>
  );
};
