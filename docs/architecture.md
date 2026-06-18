# Architecture

Three separable services. Clean Architecture inside each; clean boundaries between them.

```
┌──────────────┐     HTTP / SSE      ┌──────────────────┐     HTTP / SSE     ┌────────────┐
│ mock-netsuite│ ──── records ────▶  │   intelligence   │ ──── metrics ───▶  │ owner-app  │
│  (FastAPI)   │   NetSuite shapes   │    (FastAPI)      │   + narrative      │ (Next.js)  │
│ DISPOSABLE   │                     │  THE PRODUCT      │                    │ PRESENT.   │
└──────────────┘                     └──────────────────┘                    └────────────┘
```

## mock-netsuite (disposable)

Stands in for NetSuite. Emits records in **true NetSuite shapes** (`internalId`, `tranDate`, `entity`, record types `job`, `vendorbill`, `invoice`, `customerpayment`, `timebill`) and streams new postings over SSE on a loop. Seeded with problems baked in (see `domain-accounting.md`). Thrown away when real NetSuite arrives.

## intelligence (the product — the crown jewel)

The durable thing you'd later productize. Clean Architecture layers:

```
intelligence/src/intelligence/
├── domain/          # PURE. plain dataclasses + Money value object. zero framework imports.
│                    #   rev-rec, WIP, over/under-billing, projected margin-at-completion.
├── application/     # use cases orchestrating the domain over a feed (input/output DTOs)
├── infrastructure/  # NetSuiteClient adapter (mock today, real SuiteAnalytics later) +
│                    #   the Claude narrative adapter (with deterministic fallback)
└── interface/       # FastAPI routers, Pydantic request/response schemas, OpenAPI, config
```

**Dependency rule:** dependencies point inward. `domain` knows nothing of FastAPI, Pydantic, HTTP, or NetSuite. `infrastructure` implements interfaces (Protocols) declared by the domain/application layers.

## owner-app (presentation only)

Next.js 16 dashboard. No business logic — it renders what `intelligence` computes. Talks to the API via a **typed client generated from the OpenAPI spec** (Orval + Zod). Live updates via SSE consumed through the stable `queryClient.setQueryData` pattern.

## The NetSuite seam (the pitch, made true)

Today `intelligence/infrastructure` points its `NetSuiteClient` at `mock-netsuite`. Going live = implement the same client interface against SuiteAnalytics Connect / SuiteTalk REST and change one base URL. **The domain core and the UI do not change.** That is what makes "this goes live the day NetSuite does" a fact, not a slogan.

## Data flow per request

1. `intelligence` pulls raw records from the NetSuite client (mock/real).
2. Records map to **domain entities** (plain, Decimal-typed).
3. The domain computes the portfolio: revenue recognized, WIP, over/under-billing, margin-at-completion, warnings.
4. `interface` serializes domain results to Pydantic response models → OpenAPI → typed UI client.
5. Narrative endpoints feed the computed figures to Claude (or the deterministic fallback) for the close memo and Q&A.
