import Link from 'next/link';
import { HealthWidget } from '@/components/common/HealthWidget';

export default function HomePage() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
      <div className="max-w-4xl w-full text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Frontend Phase Initialized • Next.js & FastAPI
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-100">
          Track Your Developer Learning <br className="hidden sm:inline" />
          <span className="text-emerald-400">Step by Structured Step</span>
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Masar is a developer learning platform engineered with clean architecture. Organize learning journeys, track sections and topics, record notes, and measure genuine progress.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <Link
            href="/register"
            className="px-5 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm transition-colors shadow-lg shadow-emerald-500/10"
          >
            Create an account
          </Link>
          <Link
            href="/login"
            className="px-5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm border border-slate-700 transition-colors"
          >
            Sign in
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-5 py-2.5 rounded-lg bg-transparent hover:bg-slate-800/60 text-slate-400 hover:text-slate-200 font-medium text-sm border border-slate-800 transition-colors"
          >
            FastAPI Docs ↗
          </a>
        </div>
      </div>

      <div className="w-full mt-12 sm:mt-16">
        <HealthWidget />
      </div>

      <div className="max-w-5xl w-full mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800/80">
          <div className="text-xs font-mono text-emerald-400 font-semibold">01 • ARCHITECTURE</div>
          <h3 className="mt-2 text-base font-semibold text-slate-200">Layered Clean Architecture</h3>
          <p className="mt-2 text-xs text-slate-400 leading-relaxed">
            Strict separation of domain models, application use cases, repository interfaces, and presentation layers.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800/80">
          <div className="text-xs font-mono text-emerald-400 font-semibold">02 • SECURITY</div>
          <h3 className="mt-2 text-base font-semibold text-slate-200">JWT & Data Ownership</h3>
          <p className="mt-2 text-xs text-slate-400 leading-relaxed">
            Stateless signed tokens, PBKDF2 password hashing, and strict cascading authorization guarding journeys and topics.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800/80">
          <div className="text-xs font-mono text-emerald-400 font-semibold">03 • INTEGRATION</div>
          <h3 className="mt-2 text-base font-semibold text-slate-200">Type-Safe API Client</h3>
          <p className="mt-2 text-xs text-slate-400 leading-relaxed">
            Centralized error handling, automatic Bearer injection, and configurable environment-based endpoints.
          </p>
        </div>
      </div>
    </div>
  );
}
