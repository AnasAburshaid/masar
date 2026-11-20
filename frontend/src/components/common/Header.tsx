import Link from 'next/link';

export function Header() {
  return (
    <header className="w-full border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold text-lg group-hover:bg-emerald-500/20 group-hover:border-emerald-500/50 transition-colors">
              M
            </div>
            <div>
              <span className="text-lg font-semibold tracking-tight text-slate-100 group-hover:text-white transition-colors">
                Masar
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs text-slate-400 border-l border-slate-700 pl-2">
                Learning Tracker
              </span>
            </div>
          </Link>
        </div>

        <nav className="flex items-center gap-4">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs sm:text-sm text-slate-300 hover:text-emerald-400 transition-colors"
          >
            API Docs
          </a>
          <Link
            href="/login"
            className="text-xs sm:text-sm font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-md hover:bg-slate-800 transition-colors"
          >
            Sign in
          </Link>
          <Link
            href="/register"
            className="text-xs sm:text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-1.5 rounded-md shadow-sm transition-colors"
          >
            Get started
          </Link>
        </nav>
      </div>
    </header>
  );
}
