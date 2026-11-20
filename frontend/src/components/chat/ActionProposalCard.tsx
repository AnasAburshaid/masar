'use client';

import React, { useState } from 'react';
import { ActionProposal } from '@/types/action';

interface ActionProposalCardProps {
  proposal: ActionProposal;
  onApprove: (proposalId: number) => Promise<void>;
  onReject: (proposalId: number) => Promise<void>;
}

export const ActionProposalCard: React.FC<ActionProposalCardProps> = ({
  proposal,
  onApprove,
  onReject,
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showParameters, setShowParameters] = useState(false);

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

  const getStatusBadge = () => {
    switch (proposal.status) {
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
            Pending Approval
          </span>
        );
      case 'executed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30">
            ✓ Executed
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/30">
            ✕ Execution Failed
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-500/10 text-slate-600 dark:text-slate-400 border border-slate-500/30">
            Declined
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
            {proposal.status}
          </span>
        );
    }
  };

  const formatToolName = (tool: string) => {
    return tool.replace(/_/g, ' ').toUpperCase();
  };

  return (
    <div className="w-full my-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-hidden transition-all">
      {/* Card Header */}
      <div className="px-4 py-3 bg-slate-50/70 dark:bg-slate-800/40 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5 truncate">
          <span className="text-base">⚡</span>
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white truncate">
              {proposal.title}
            </h4>
            <span className="text-[10px] text-slate-500 dark:text-slate-400">
              AI Proposed Action Plan • {proposal.actions.length} operation{proposal.actions.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
        <div>{getStatusBadge()}</div>
      </div>

      {/* Warning Callout for Destructive Actions */}
      {proposal.has_destructive_actions && (
        <div className="px-4 py-2 bg-amber-500/10 border-b border-amber-500/20 text-amber-800 dark:text-amber-300 text-[11px] flex items-center gap-2">
          <span>⚠️</span>
          <span>
            <strong>Attention:</strong> This proposal includes destructive operations (e.g. deletion of roadmaps, sections, or topics).
          </span>
        </div>
      )}

      {/* Action Steps List */}
      <div className="p-4 space-y-2.5">
        <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400 mb-2">
          Planned Operations:
        </div>
        {proposal.actions.map((act, idx) => {
          const result = proposal.results.find((r) => r.action_index === idx);
          return (
            <div
              key={idx}
              className={`p-2.5 rounded-xl border text-xs transition-colors ${
                act.is_destructive
                  ? 'border-rose-200 dark:border-rose-900/50 bg-rose-50/30 dark:bg-rose-950/20'
                  : 'border-slate-200 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-950/30'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
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
                    {formatToolName(act.tool)}
                  </span>
                  <span className="font-medium text-slate-800 dark:text-slate-200 text-xs">
                    {act.description || act.tool}
                  </span>
                </div>

                {/* Execution outcome indicator */}
                {result && (
                  <span
                    className={`text-[11px] font-semibold flex items-center gap-1 ${
                      result.status === 'success'
                        ? 'text-emerald-600 dark:text-emerald-400'
                        : 'text-rose-600 dark:text-rose-400'
                    }`}
                  >
                    {result.status === 'success' ? '✓ Success' : `✕ ${result.error || 'Failed'}`}
                  </span>
                )}
              </div>

              {/* Parameters Preview */}
              {showParameters && (
                <div className="mt-2 pl-7">
                  <pre className="p-2 rounded-lg bg-slate-100 dark:bg-slate-900 text-[10px] font-mono text-slate-700 dark:text-slate-300 overflow-x-auto">
                    {JSON.stringify(act.parameters, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          );
        })}

        {/* Toggle parameters view */}
        <div className="pt-1 flex justify-end">
          <button
            type="button"
            onClick={() => setShowParameters(!showParameters)}
            className="text-[11px] text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
          >
            {showParameters ? 'Hide parameters ▲' : 'Show parameters ▼'}
          </button>
        </div>
      </div>

      {/* Card Footer / Approval Actions */}
      {proposal.status === 'pending' && (
        <div className="px-4 py-3 bg-slate-50/70 dark:bg-slate-800/40 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3">
          <p className="text-[11px] text-slate-500 dark:text-slate-400">
            Review proposed actions before executing.
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={isProcessing}
              onClick={handleReject}
              className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold disabled:opacity-50 transition-colors"
            >
              Reject
            </button>
            <button
              type="button"
              disabled={isProcessing}
              onClick={handleApprove}
              className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs disabled:opacity-50 transition-all flex items-center gap-1.5"
            >
              {isProcessing ? (
                <>
                  <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Executing...</span>
                </>
              ) : (
                <span>Approve & Execute</span>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
