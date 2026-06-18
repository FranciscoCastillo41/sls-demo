# Conventions

## Repository layout

```
sls-demo/
├── apps/owner-app/          # Next.js 16 UI (pnpm workspace member)
├── services/
│   ├── mock-netsuite/       # FastAPI — disposable NetSuite stand-in (uv project)
│   └── intelligence/        # FastAPI — the product (uv project)
├── docs/                    # lean context, one concern per file
├── .github/workflows/       # CI
├── biome.json · lefthook.yml · commitlint.config.js · Taskfile.yml · docker-compose.yml
```

## Python (services)

- **uv** per service: `uv init --package` → src layout, `py.typed` present.
- Pydantic v2 **only at the interface boundary**. Domain = plain dataclasses + `Money`.
- Lint/format: **Ruff** (`ruff check` + `ruff format`). Types: **Pyright strict**.
- Tests: **pytest + Hypothesis**; `@settings(max_examples=500)` for money invariants.
- Config: **pydantic-settings**, `SecretStr` for secrets, validated at startup (fail fast).
- Money: `Decimal` only; global `ROUND_HALF_EVEN`; quantize at boundaries only.

## TypeScript (owner-app)

- **Next.js 16** App Router / RSC, **TS strict**, **pnpm**.
- Lint/format: **Biome** (format + bulk lint) + a **minimal ESLint flat config** for `eslint-plugin-next` and `eslint-plugin-react-hooks` only (Biome can't cover those).
- UI: Tailwind v4 (CSS-first `@theme`, no `tailwind.config.js`), shadcn/ui (+ Sonner). Charts: **Recharts v3**.
- Server state: TanStack Query. Live: **SSE** via `queryClient.setQueryData` (not experimental `streamedQuery`).
- API client: **Orval + Zod** generated from the intelligence OpenAPI spec; generated client is committed and regenerated in CI. Spec is the single source of truth.
- Tests: Vitest + Testing Library (units/hooks), Playwright (async RSC, SSE flows, critical paths).
- Note: Next 16 uses `proxy.ts` (not `middleware.ts`); `params`/`searchParams`/`cookies()`/`headers()` are async.

## Environment variables

No `.env` is committed (the sandbox blocks it too). Create `.env` from this reference:

```
# intelligence
ENVIRONMENT=development
NETSUITE_BASE_URL=http://localhost:8001
ANTHROPIC_API_KEY=            # optional; deterministic fallback if empty
ANTHROPIC_MODEL=claude-opus-4-8
# owner-app
INTELLIGENCE_BASE_URL=http://localhost:8000
```

## Definition of Done (every change)

1. Follows `clean-code.md`.
2. Money is `Decimal`; new math has Hypothesis coverage.
3. `task lint` clean; Pyright/TS strict clean.
4. Tests pass locally; CI green.
5. Conventional Commit; PR squash-merged to `main`.
