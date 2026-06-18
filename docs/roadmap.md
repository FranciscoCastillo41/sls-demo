# Roadmap & status

Build order is deliberate: **correctness before paint.** The math is bulletproof before anything gets a UI.

## Status

- [x] **0 — Repo & git foundation.** Monorepo skeleton, `.gitignore`, Biome, Lefthook, commitlint/commitizen, Taskfile, docker-compose skeleton, CI (quality + gated python/web), repo-scoped SSH signing, lean `docs/`. GitHub remote + Rulesets.
- [ ] **1 — mock-netsuite.** FastAPI service: NetSuite-shaped records (`job`/`vendorbill`/`invoice`/`customerpayment`/`timebill`), seed data with the four baked-in projects (DFW hot, Omaha CO erosion, UT aged AR, one healthy), SSE stream of postings.
- [ ] **2 — Domain core + Hypothesis.** `Money` value object; rev-rec, WIP, over/under-billing, EAC, projected margin-at-completion, retainage, AR aging — per billing model. Property tests for every invariant in `domain-accounting.md`. *This is the gate; nothing downstream until it's green.*
- [ ] **3 — intelligence API.** Application use cases + infrastructure NetSuiteClient adapter (points at mock today) + FastAPI interface + OpenAPI. Reconciling portfolio P&L endpoint.
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
