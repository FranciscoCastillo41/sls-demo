# sls-demo

A financial-intelligence layer on top of NetSuite for an owner's-rep construction firm — **the month-end close, automated.** Detailed NetSuite data goes in; an owner-readable story comes out: a portfolio P&L that reconciles, early-warning flags, an auto-written close memo, and ask-the-numbers Q&A.

> ⚠️ All data in this project is **synthetic** and for demonstration only.

## Why it exists

NetSuite runs the business but its reporting is accountant-shaped, not owner-shaped. This app is the translation layer — the part a senior accountant produces by hand each month — built so the numbers reconcile and hold up to scrutiny.

## Architecture

```
mock-netsuite   →   intelligence        →   owner-app
(stand-in feed,     (domain core + API,     (Next.js dashboard,
 NetSuite shapes)    the durable product)    live via SSE)
```

The mock feed is disposable. Going live against real NetSuite is one adapter + one URL — the domain core never knows the difference. Details in [`docs/architecture.md`](docs/architecture.md).

## Quick start

```bash
task setup   # install pnpm + uv toolchains and git hooks
task up      # bring up the full stack via Docker Compose
```

## Development

| Command | What |
|---|---|
| `task` | List all tasks |
| `task lint` / `task fmt` | Biome across the repo |
| `pnpm commit` | Guided Conventional Commit |

Standards live in [`docs/`](docs/) — start with [`CLAUDE.md`](CLAUDE.md). We follow **Clean Code (Robert C. Martin) religiously** and never let a float touch a dollar.

## License

Private / unpublished.
