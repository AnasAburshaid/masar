export function Footer() {
  return (
    <footer className="w-full border-t border-slate-800/80 bg-slate-950/60 py-8 text-center text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p>Masar — Developer Learning Tracker. Professional architecture & clean design.</p>
        <div className="flex items-center gap-4">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-slate-400 transition-colors"
          >
            FastAPI OpenAPI
          </a>
          <span>•</span>
          <a
            href="http://localhost:8000/health"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-slate-400 transition-colors"
          >
            Backend Health
          </a>
        </div>
      </div>
    </footer>
  );
}
