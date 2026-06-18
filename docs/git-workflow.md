# Git workflow — flawless from commit #1

## Branching (trunk-based)

- `main` is always deployable and protected.
- Work on short-lived branches: `feat/<slug>`, `fix/<slug>`, `chore/<slug>`, `docs/<slug>`. Live ≤ 1–2 days; longer work hides behind a feature flag.
- **Squash-merge only.** `main` keeps a linear history — one clean Conventional Commit per PR.

## Commits (Conventional Commits, enforced)

- Format: `type(scope): subject`. Types: `feat fix docs chore refactor perf test ci build`.
- Scopes: `mock-netsuite intelligence owner-app domain ci docs repo`.
- Breaking: `type(scope)!: ...` or a `BREAKING CHANGE:` footer.
- Write commits with `pnpm commit` (commitizen prompt). `commitlint` rejects bad messages via the `commit-msg` hook.

## Hooks (Lefthook)

`pre-commit` runs in parallel, glob-scoped: Ruff on staged `*.py`, Biome on staged JS/TS, auto-stages fixes. `commit-msg` runs commitlint. Installed by `task setup` / `pnpm install` (`prepare` script).

## Signing

SSH commit signing is configured **locally in this repo** (not globally — it won't disturb other projects). Every commit is signed → GitHub "Verified". Key: `~/.ssh/id_ed25519.pub`.

## CI (GitHub Actions)

- `ci.yml`: a `changes` job (path filter) gates `python` and `web` jobs so Python edits don't run JS jobs. A `quality` job runs Biome repo-wide on every push.
- `pr-title.yml`: enforces the PR title is a valid Conventional Commit (it becomes the squash subject).
- Caching: `astral-sh/setup-uv` (uv) + `actions/setup-node` `cache: pnpm`. Lockfiles enforced with `--locked` / `--frozen-lockfile`.

## Branch protection (GitHub Rulesets on `main`)

Require PR, required status checks (`quality`, and `python`/`web` when relevant), linear history, signed commits, block force-push and deletion. Squash-merge is the only enabled merge method.

## Releases (added with the first service)

`release-please` opens a release PR from the Conventional Commit history (native Python + Node monorepo support); merging it tags and writes the changelog. Configured when the first releasable service lands.

## First-time setup recap

1. `pnpm install` (installs hooks via `prepare`).
2. Branch: `git switch -c feat/<slug>`.
3. Code → `pnpm commit` → push → open PR.
4. CI green + review → **squash-merge**.
