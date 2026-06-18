# Roadmap & status

Build order is deliberate: **correctness before paint.** The math is bulletproof before anything gets a UI.

## Status

- [x] **0 — Repo & git foundation.** Monorepo skeleton, `.gitignore`, Biome, Lefthook, commitlint/commitizen, Taskfile, docker-compose skeleton, CI (quality + gated python/web), repo-scoped SSH signing, lean `docs/`. GitHub remote + Rulesets.
- [x] **1 — mock-netsuite.** FastAPI service on Postgres (async SQLAlchemy 2.0 + asyncpg): NetSuite-shaped records (`job`/`vendorbill`/`invoice`/`customerpayment`/`changeorder`), seed data with the four baked-in projects (DFW hot, Omaha CO erosion, UT aged AR, PHX healthy), SSE stream of postings. Money `NUMERIC(19,4)`. Tested against a real Postgres via testcontainers. Dockerfile + compose `db` service + Release Please wired.
- [x] **2 — Domain core + Hypothesis.** Pure, framework-free `intelligence.domain`: `Money` value object (Decimal, banker's rounding, currency-guarded, float-rejecting); rev-rec, WIP, over/under-billing, EAC, projected margin-at-completion, retainage, AR aging — per billing model. Hypothesis property proofs for every invariant in `domain-accounting.md` (recognized==billed+WIP, partition, POC bounds, recognized≤fee, portfolio ties out, aging==AR, determinism). Recognized revenue quantized to cents at the boundary.
- [x] **3 — intelligence API.** Full Clean Architecture: application (`ProjectSource` port + `build_portfolio` use case), infrastructure (async `NetSuiteClient` over httpx, mapping NetSuite records → domain incl. FIFO oldest-first receivables + retainage, `NetSuiteProjectSource` adapter), interface (FastAPI app, `PortfolioReport` schemas, decimal-context setup, graceful 502 on upstream failure). Reconciling `/portfolio` endpoint. Tested unit + end-to-end through `MockTransport`. *Deferred (real-NetSuite hardening): retry/backoff + shared pooled client; period-snapshot Postgres persistence; T&M revenue needs timebill records the source doesn't emit yet.*
- [ ] **4 — Early-warning engine.** Margin erosion, cash gaps, aged pay-apps, unrecovered change orders — forward-looking flags.
- [ ] **5 — owner-app.** Next.js 16 dashboard; Orval+Zod client; live via SSE; KPI cards, project table, warnings panel.
- [ ] **6 — Narrative + ask-the-numbers.** Claude close-memo + Q&A over the live computed figures. Deterministic fallback first; `ANTHROPIC_API_KEY` wired in last.

## When each ships

- Add the `python` CI specifics + `release-please` with **step 1**.
- Add the `web` CI specifics with **step 5**.

## Guardrails

- Data is synthetic and labeled as such in the UI.
- No float touches a dollar. No untested money math.
- Clean Code, religiously (`clean-code.md`).
