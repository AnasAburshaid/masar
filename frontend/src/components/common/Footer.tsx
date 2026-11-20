import React from 'react';

export function Footer() {
  return (
    <footer className="w-full border-t border-slate-200 dark:border-slate-800/80 bg-slate-50/80 dark:bg-slate-950/60 py-8 text-xs text-slate-500 dark:text-slate-400 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="flex items-center gap-2">
          <span>Masar — Developer Learning Tracker.</span>
          <span className="hidden md:inline text-slate-400 dark:text-slate-600">•</span>
          <span className="hidden md:inline">Engineered with Clean Architecture & Modern UX.</span>
        </p>
        <div className="flex items-center gap-4 text-xs">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
          >
            FastAPI OpenAPI
          </a>
          <span className="text-slate-300 dark:text-slate-700">•</span>
          <a
            href="http://localhost:8000/health"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
          >
            Health Status
          </a>
        </div>
      </div>
    </footer>
  );
}
