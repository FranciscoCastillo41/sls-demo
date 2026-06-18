# intelligence

The product. A pure, framework-free domain core (owner's-rep accounting:
rev-rec, WIP, over/under-billing, projected margin-at-completion, retainage,
A/R aging) with the API, persistence, and narrative layers built around it.

Money is `Decimal`; the domain imports no framework. See
`../../docs/architecture.md` and `../../docs/domain-accounting.md`.

## Test

```bash
uv run pytest
```
