# AGENTS.md — Frontend Layer (`frontend/`)

## 1. Role and Purpose

The **Frontend Layer** provides the modern, responsive web application for Masar. Built with Next.js 16 (App Router with Turbopack), React 19, and Tailwind CSS v4, it delivers an intuitive user experience for tracking learning journeys, managing roadmap hierarchies (sections and topics), writing contextual notes, toggling topic mastery, and visualizing progress metrics in both Light and Dark themes.

---

## 2. Directory and Package Organization

```
frontend/
├── src/
│   ├── app/                    # Next.js 16 App Router pages and route handlers
│   │   ├── page.tsx            # Landing page (hero, value pillars, backend health widget)
│   │   ├── layout.tsx          # RootLayout (Geist fonts, ThemeProvider, AuthProvider)
│   │   ├── globals.css         # Tailwind v4 import, @variant dark override, CSS tokens
│   │   ├── login/page.tsx      # Sign-in page with SaaS split-screen layout
│   │   ├── register/page.tsx   # Sign-up page with live validation & auto-login
│   │   ├── dashboard/page.tsx  # Progress dashboard, KPI grid, roadmap distribution meter
│   │   ├── profile/page.tsx    # Knowledge profile (verified skills, AI-inferred items review, bio editor)
│   │   ├── journeys/
│   │   │   ├── page.tsx        # Journeys list, creation modal, edit/delete dialogs
│   │   │   └── [id]/page.tsx   # Journey Canvas (sections, topics, notes drawer, live progress)
│   │   └── chat/page.tsx       # AI Conversation Hub (multi-turn chat, prompt cards, sidebar history)
│   ├── components/             # Reusable UI components
│   │   ├── common/             # Header, Footer, HealthWidget, ThemeToggle
│   │   ├── layout/             # AppLayout (responsive sidebar, user profile card)
│   │   ├── auth/               # ProtectedRoute (session guard and redirection)
│   │   └── chat/               # MarkdownRenderer, ActionProposalCard & DocumentManagerModal
│   ├── context/                # Global React context providers
│   │   ├── AuthContext.tsx     # Session state, JWT token storage, login/logout actions
│   │   └── ThemeContext.tsx    # Light/Dark/System theme management with persistence
│   ├── services/api/           # Type-safe API client layer
│   │   ├── client.ts           # ApiClient fetch wrapper (Bearer token injection, error mapping)
│   │   ├── errors.ts           # ApiError class with status code helpers
│   │   ├── auth.ts             # Auth endpoints (/auth/login, /auth/register, /auth/me)
│   │   ├── journeys.ts         # /journeys CRUD
│   │   ├── sections.ts         # /sections CRUD
│   │   ├── topics.ts           # /topics CRUD and status toggles (/complete, /pending)
│   │   ├── notes.ts            # /notes CRUD
│   │   ├── conversations.ts    # /conversations CRUD and message submission
│   │   ├── documents.ts        # /documents CRUD, uploads, and AI summarization
│   │   ├── profile.ts          # /profile (getProfile, updateBio, addItem, confirmItem, deleteItem, extract)
│   │   ├── actions.ts          # /conversations/{id}/proposals (list, get, approve, reject)
│   │   ├── progress.ts         # /journeys/{id}/progress & dashboard metrics aggregator
│   │   └── health.ts           # /health and root status
│   ├── types/                  # TypeScript interfaces (matching backend Pydantic schemas)
│   │   ├── action.ts
│   │   ├── auth.ts
│   │   ├── conversation.ts
│   │   ├── document.ts
│   │   ├── health.ts
│   │   ├── journey.ts
│   │   ├── profile.ts
│   │   └── progress.ts
│   └── config/env.ts           # Centralized environment variables (NEXT_PUBLIC_API_URL)
├── package.json                # Project dependencies and npm scripts
├── tsconfig.json               # TypeScript compiler configuration
└── AGENTS.md                   # This specification file
```

---

## 3. Architectural Rules & Constraints

1. **Backend as Single Source of Truth:**
   - The frontend must never invent independent business rules or override backend progress calculations.
   - Validation rules, ownership checks, and status transitions are governed by the FastAPI backend.
2. **Strict Inward Dependency (Services First):**
   - UI pages and components must **never** make direct `fetch()` calls. All backend communications must go through the typed API service layer in `src/services/api/`.
3. **Strict Typing & Type Parity:**
   - All API payloads, query parameters, and responses must use explicit TypeScript interfaces located in `src/types/` that mirror backend Pydantic schemas.
4. **Dual-Theme Integrity (Light & Dark Mode):**
   - All components must provide high-contrast, visually pleasing styling for both Light and Dark modes.
   - Never hardcode static dark colors (`bg-slate-950`, `text-slate-100`) without corresponding light mode variants or CSS token variables.
5. **React 19 & Turbopack Concurrency Rules:**
   - **No synchronous `setState` in `useEffect`:** Avoid triggering `react-hooks/set-state-in-effect`. Use async IIFEs, promise callbacks, or `queueMicrotask` when initializing state in effects.
   - **Dynamic Route Params:** In Next.js 15/16 App Router, `params` is a Promise (`params: Promise<{ id: string }>`). Unwrapping via `use(params)` must be enclosed within a `<Suspense>` boundary to enable partial prerendering.
6. **Zero Bloat & Minimal Dependencies:**
   - Avoid bloated UI component libraries. Use utility-first Tailwind CSS v4 and native accessible HTML/React primitives.

---

## 4. Implementation Approach & Design Patterns

- **Typed HTTP Client Pattern (`ApiClient`):**
  - Centralizes request URL construction, Bearer token attachment from `sessionStorage`, HTTP method execution, and error transformation into structured `ApiError` objects.
- **Client-Side Auth Guard (`ProtectedRoute`):**
  - Wraps authenticated routes (`/dashboard`, `/journeys`, etc.) to prevent unauthenticated access and cascading renders during session verification.
- **Micro-Interactions & Optimistic Feedback:**
  - Topic completion status toggles provide immediate visual feedback while asynchronously synchronizing state with the backend.
- **Mobile-First Responsive Layout:**
  - Uses Tailwind breakpoints (`sm:`, `md:`, `lg:`) to deliver optimal layouts from mobile drawer navigation to full split-screen desktop experiences.

---

## 5. Tools & Technologies

- **Next.js 16.4+:** React framework with App Router, Turbopack, and Partial Prerendering.
- **React 19.3+:** Modern component runtime with `use()`, `Suspense`, and strict concurrency guards.
- **Tailwind CSS v4:** Zero-configuration CSS engine with custom selector variant `@variant dark (&:where(.dark, .dark *, [data-theme="dark"], [data-theme="dark"] *));`.
- **Node.js Test Runner (`tsx --test`):** Automated unit tests for API services and progress aggregators.
- **ESLint 9:** Code quality enforcement using `eslint-config-next`.

---

## 6. Maintenance & Evolution Mandate

Whenever new pages, components, or API integrations are introduced:
- Create corresponding type definitions under `src/types/`.
- Add typed service methods under `src/services/api/`.
- Verify responsive layout and both Light/Dark themes.
- Run `npm test`, `npm run lint`, and `npm run build` before submitting PRs.
- **Update this `AGENTS.md` file** whenever UI patterns, libraries, or routing paradigms evolve.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
