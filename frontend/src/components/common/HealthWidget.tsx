'use client';

import React, { useEffect, useState } from 'react';
import { healthService } from '@/services/api/health';
import { ApiRootInfo, HealthStatus } from '@/types/health';
import { env } from '@/config/env';

export function HealthWidget() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [rootInfo, setRootInfo] = useState<ApiRootInfo | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);

  const fetchStatus = async () => {
    setIsLoading(true);
    setError(null);
    const start = performance.now();

    try {
      const [h, r] = await Promise.all([
        healthService.checkHealth(),
        healthService.getRootInfo(),
      ]);
      setLatencyMs(Math.round(performance.now() - start));
      setHealth(h);
      setRootInfo(r);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
      setHealth(null);
      setRootInfo(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let isCancelled = false;
    const start = performance.now();

    Promise.all([healthService.checkHealth(), healthService.getRootInfo()])
      .then(([h, r]) => {
        if (isCancelled) return;
        setLatencyMs(Math.round(performance.now() - start));
        setHealth(h);
        setRootInfo(r);
        setIsLoading(false);
      })
      .catch((err: unknown) => {
        if (isCancelled) return;
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        setIsLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto rounded-2xl border border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-900/60 p-6 shadow-sm dark:shadow-xl backdrop-blur-sm transition-colors duration-200">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <div
            className={`w-3 h-3 rounded-full transition-all ${
              isLoading
                ? 'bg-amber-400 animate-pulse'
                : health?.status === 'ok'
                ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'
                : 'bg-rose-500'
            }`}
          />
          <h2 className="text-sm font-semibold text-slate-800 dark:text-slate-100">
            Backend API Health
          </h2>
        </div>

        <button
          onClick={fetchStatus}
          disabled={isLoading}
          className="text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Checking...' : 'Check Status'}
        </button>
      </div>

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/50 border border-slate-200/80 dark:border-slate-800/80">
          <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Target Endpoint</div>
          <div className="mt-1 font-mono text-xs text-slate-800 dark:text-slate-200 truncate">{env.apiUrl}</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/50 border border-slate-200/80 dark:border-slate-800/80">
          <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Connection State</div>
          <div className="mt-1 font-mono text-xs text-slate-800 dark:text-slate-200">
            {health?.status ? (
              <span className="text-emerald-600 dark:text-emerald-400 uppercase font-semibold">
                {health.status}
              </span>
            ) : error ? (
              <span className="text-rose-600 dark:text-rose-400 font-semibold">DISCONNECTED</span>
            ) : (
              'CONNECTING...'
            )}
            {latencyMs !== null && health && (
              <span className="text-slate-400 dark:text-slate-500 text-[10px] ml-1.5 font-normal">
                ({latencyMs}ms)
              </span>
            )}
          </div>
        </div>

        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/50 border border-slate-200/80 dark:border-slate-800/80">
          <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Storage Backend</div>
          <div className="mt-1 font-mono text-xs text-slate-800 dark:text-slate-200 capitalize">
            {health?.storage_type || '—'}
          </div>
        </div>
      </div>

      {rootInfo && (
        <div className="mt-4 p-3 rounded-xl bg-slate-50/80 dark:bg-slate-950/30 border border-slate-200/60 dark:border-slate-800/50 text-xs text-slate-600 dark:text-slate-400 flex flex-wrap items-center justify-between gap-2">
          <span>{rootInfo.message} • v{rootInfo.version}</span>
          <span className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono text-[10px]">
            {rootInfo.environment}
          </span>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800/40 text-xs text-rose-700 dark:text-rose-300">
          <span className="font-semibold">Connection offline: </span>
          {error}. Ensure the FastAPI backend is running on <code className="bg-rose-100 dark:bg-rose-900/40 px-1 py-0.5 rounded font-mono text-[11px]">{env.apiUrl}</code>.
        </div>
      )}
    </div>
  );
}
