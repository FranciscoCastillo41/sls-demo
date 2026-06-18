# CLAUDE.md — sls-demo

Read this first. It's the lean entry point; deeper context lives in `docs/` (load only the file you need).

## What this is

A financial-intelligence layer that sits **on top of NetSuite** for **SLS Consultants** (Dallas owner's-rep / construction-management firm). NetSuite holds the detailed data; this app does the thing NetSuite is bad at: turning it into an **owner-readable month-end story** — a portfolio P&L that reconciles, early-warning flags, an auto-written close memo, and ask-the-numbers Q&A.

The whole demo's credibility rests on one thing: **the accounting math reconciles and a senior accountant cannot break it.** Correctness before polish, always.

> Data is synthetic and labeled as such. Never imply it is SLS's real numbers.

## Architecture (one line)

`mock-netsuite` (disposable, NetSuite-shaped feed) → `intelligence` (the product: pure domain core + API) → `owner-app` (Next.js UI). The seam is real: swapping to live NetSuite is one adapter + one URL. See `docs/architecture.md`.

## Non-negotiables

- **Clean Code (Robert C. Martin), religiously.** See `docs/clean-code.md`. This is enforced, not aspirational.
- **Money is `Decimal`, end to end. No float ever touches a dollar.** Rules in `docs/domain-accounting.md`.
- **The domain layer is pure** — plain dataclasses + a `Money` value object, zero framework imports (no Pydantic/FastAPI/SQLAlchemy). Pydantic lives only at the API boundary.
- **Reconciliation is proven, not spot-checked** — Hypothesis property tests assert the invariants.

## Stack (mid-2026, verified)

Python 3.12 · FastAPI · **uv** · Pydantic v2 (boundary only) · Ruff · **Pyright strict** · pytest + **Hypothesis**
**Next.js 16** · React 19.2 · TS strict · **pnpm** · Tailwind v4 · shadcn/ui · **Recharts v3** · TanStack Query + **SSE** · **Orval+Zod** client
Biome (format + bulk lint) + minimal ESLint (next/react-hooks) · Docker Compose · Taskfile · Lefthook · GitHub Actions

## Commands

- `task` — list everything · `task setup` — install toolchains + hooks · `task up` — full stack
- `task lint` / `task fmt` — Biome across the repo
- Commit via `pnpm commit` (Conventional Commits, enforced). See `docs/git-workflow.md`.

## docs/ index

- `architecture.md` — services, boundaries, the NetSuite seam
- `domain-accounting.md` — **the crown jewel**: rev-rec / WIP / over-under-billing / margin-at-completion formulas, Decimal rules, invariants
- `clean-code.md` — the Clean Code rules we hold to religiously
- `conventions.md` — coding standards, testing, types, env vars
- `git-workflow.md` — trunk-based, Conventional Commits, signing, CI, releases
- `decisions.md` — ADR-lite: what we chose and why
- `roadmap.md` — build order + current status
