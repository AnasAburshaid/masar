'use client';

import { useEffect, useState } from 'react';
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
    <div className="w-full max-w-2xl mx-auto rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div
            className={`w-3 h-3 rounded-full ${
              isLoading
                ? 'bg-amber-400 animate-pulse'
                : health?.status === 'ok'
                ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]'
                : 'bg-rose-500'
            }`}
          />
          <h2 className="text-base font-semibold text-slate-100">Backend Communication Status</h2>
        </div>

        <button
          onClick={fetchStatus}
          disabled={isLoading}
          className="text-xs font-medium px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Checking...' : 'Check connection'}
        </button>
      </div>

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
        <div className="p-3 rounded-lg bg-slate-950/50 border border-slate-800/80">
          <div className="text-xs text-slate-400">Target API URL</div>
          <div className="mt-1 font-mono text-xs text-slate-200 truncate">{env.apiUrl}</div>
        </div>

        <div className="p-3 rounded-lg bg-slate-950/50 border border-slate-800/80">
          <div className="text-xs text-slate-400">Health Endpoint</div>
          <div className="mt-1 font-mono text-xs text-slate-200">
            {health?.status ? (
              <span className="text-emerald-400 uppercase font-semibold">{health.status}</span>
            ) : error ? (
              <span className="text-rose-400">DISCONNECTED</span>
            ) : (
              'CONNECTING...'
            )}
            {latencyMs !== null && health && (
              <span className="text-slate-500 text-[10px] ml-1.5">({latencyMs}ms)</span>
            )}
          </div>
        </div>

        <div className="p-3 rounded-lg bg-slate-950/50 border border-slate-800/80">
          <div className="text-xs text-slate-400">Persistence Mode</div>
          <div className="mt-1 font-mono text-xs text-slate-200 capitalize">
            {health?.storage_type || '—'}
          </div>
        </div>
      </div>

      {rootInfo && (
        <div className="mt-4 p-3.5 rounded-lg bg-slate-950/30 border border-slate-800/50 text-xs text-slate-400 flex flex-wrap items-center justify-between gap-2">
          <span>{rootInfo.message} • Masar API v{rootInfo.version}</span>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
            env: {rootInfo.environment}
          </span>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-rose-950/30 border border-rose-800/40 text-xs text-rose-300">
          <span className="font-semibold">Connection failed: </span>
          {error}. Ensure the FastAPI backend server is running on <code className="bg-rose-900/40 px-1 py-0.5 rounded">{env.apiUrl}</code>.
        </div>
      )}
    </div>
  );
}
