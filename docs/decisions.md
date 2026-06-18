# Decisions (ADR-lite)

Each entry: the choice, and the *why*. Verified against mid-2026 practice.

## Architecture

- **Polyglot, 3 services** (FastAPI domain/API + Next.js UI), not a TS monolith. Keeps money math in one well-tested Python core, gives clean boundaries, and makes the core productizable later.
- **Domain core is pure** (plain dataclasses + `Money`), Pydantic only at the boundary. Mixing Pydantic into the domain collapses the architectural boundary.
- **Mock NetSuite is a separate, disposable service.** Makes the "swap one URL for live NetSuite" seam real.

## Python

- **uv over Poetry.** Faster, now the greenfield default. *Deliberate deviation from the user's global CLAUDE.md Poetry standard — do not "correct" it.*
- **Pyright (strict) over mypy.** Faster, ~98% spec conformance, native Pydantic v2. `ty` (Astral) is not production-ready yet — revisit at its 1.0.
- **`Decimal` for money**, banker's rounding, `NUMERIC(19,4)`. Floats for money is the classic credibility-killer.
- **Hypothesis** for reconciliation invariants — proves the math for all inputs, not just examples.

## TypeScript / UI

- **Next.js 16** (not 15 — 15 EOLs Oct 2026), React 19.2, Turbopack + React Compiler defaults.
- **Recharts v3, not Tremor.** `@tremor/react` npm package is effectively abandoned (last release Nov 2024; Vercel pivoted it to copy-paste blocks).
- **Biome + minimal ESLint hybrid**, not Biome alone. Biome lacks `eslint-plugin-next` and `react-hooks` rules.
- **SSE via `queryClient.setQueryData`**, not TanStack's experimental `streamedQuery` — stability for a financial app.
- **Orval + Zod** client from OpenAPI — runtime response validation so bad data fails loud.

## Persistence

- **Postgres everywhere** (mock + intelligence), via docker-compose `db` with separate databases (`mock_netsuite`, `intelligence`). Money is `NUMERIC(19,4)`.
- **Async SQLAlchemy 2.0 + asyncpg** — honors "never block the event loop"; `Mapped[]` typed models.
- **Mock seeds via `create_all` + idempotent seed; intelligence will use Alembic migrations.** Migrations matter where the schema evolves (the durable product); the mock's schema is frozen and its DB is ephemeral, so migrations there would be ceremony.
- **Integration tests run against a real Postgres** (testcontainers), never SQLite — test the engine you ship.
- **mock-netsuite stays flat** (concern-per-module), no hexagonal layers: it has no business domain to protect. Full Clean Architecture is reserved for `intelligence`, where the domain lives. Architecture depth matches component value.

## Process

- **Trunk-based + squash-merge + linear history**, not Git Flow. Git Flow fights continuous integration; overkill for a small team.
- **SSH commit signing**, repo-scoped — simplest modern setup, doesn't touch other projects.
- **Release Please** for versioning — more automated than Changesets, more controlled than semantic-release, native polyglot monorepo support.

## Deliberately NOT done (gold-plating = junior signal on a demo)

Kubernetes, microservice meshes, event sourcing, heavy monorepo tools (Turborepo/Nx), multi-version CI matrices. Right altitude beats maximal tooling.
