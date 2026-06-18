# Clean Code — followed religiously

Robert C. Martin's *Clean Code* is the standard for this repo, not a suggestion. Every PR is held to it. Reviewers (human or Claude) reject violations.

## Names

- Intention-revealing. `recognized_revenue`, not `rev` or `r`.
- No disinformation, no noise words (`data`, `info`, `manager` without meaning).
- Searchable over magic: no bare numbers/strings — name every constant (`ROUNDING = ROUND_HALF_EVEN`, `RETAINAGE_DEFAULT = Decimal("0.10")`).
- Class names are nouns; method names are verbs. Pick one word per concept (don't mix `fetch`/`get`/`retrieve`).

## Functions

- **Small.** Do one thing, at one level of abstraction. If you can extract a function with a meaningful name, do it.
- **Few arguments** (0–2 ideal, 3 max). No boolean flag arguments — split the function.
- **No side effects.** A function named `compute_wip` computes; it does not also write or log surprises.
- **Command/Query Separation:** a function either does something or answers something, never both.
- Prefer exceptions to error codes. Don't return `null`; don't pass `null`.

## Comments

- Code explains *how*; comments (sparingly) explain *why*. The best comment is a good name.
- No commented-out code (git remembers). No redundant/obvious comments.

## Structure

- One reason to change per module (SRP). Dependencies point inward (see `architecture.md`).
- Domain layer stays pure — no framework imports leaking in.
- Keep related things vertically close; declare variables near use.

## Errors & boundaries

- Fail fast and loud on invalid money/state. Validate at boundaries (Pydantic/Zod); trust types inside the domain.
- Wrap third parties (NetSuite, Claude) behind a thin adapter interface we own.

## Tests (first-class — same bar as production code)

- **F.I.R.S.T.**: Fast, Independent, Repeatable, Self-validating, Timely.
- One logical assertion per test; descriptive test names that read as specs.
- The domain's invariants are property-based (Hypothesis), not just examples.
- No untested money math. Ever.

## The Boy Scout Rule

Leave every file cleaner than you found it.
