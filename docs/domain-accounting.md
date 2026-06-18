# Domain & Accounting — the crown jewel

This is the most important file in the repo. If the math here is wrong, the demo is dead. Every formula is owner's-rep accounting under **percentage-of-completion (POC)**. Implemented in `intelligence/domain`, proven with Hypothesis.

## Money rules (absolute)

- **`Decimal` only. No `float` ever touches a dollar.** Construct from strings/ints, never from floats.
- Set the context once at process start: `getcontext().rounding = ROUND_HALF_EVEN` (banker's rounding), `prec = 28`.
- Quantize to cents (`Decimal("0.01")`) **only at output/storage boundaries**, never mid-calculation.
- Domain owns a small `Money` value object (amount + currency) with guarded arithmetic (no USD + EUR). No Pydantic in the domain.
- Persisted as `NUMERIC(19, 4)`.

## The entities (plain dataclasses, Decimal-typed)

A **Project (job)** carries:

| Field | Meaning |
|---|---|
| `billing_model` | `FIXED_FEE` \| `PERCENT_OF_COST` \| `TIME_AND_MATERIALS` |
| `contract_fee` | total fee owed to SLS (the revenue SLS earns) |
| `budgeted_cost` | SLS's original estimated cost to deliver |
| `cost_to_date` | actual cost incurred so far |
| `estimated_cost_to_complete` (ETC) | remaining cost to finish |
| `billed_to_date` | invoiced to the owner |
| `collected_to_date` | cash received |
| `change_orders` | approved + unapproved fee/cost adjustments |
| `retainage_pct` | % withheld until completion (0 if none) |

## Core formulas

**Estimate at completion (EAC)** — the honest total cost:
```
EAC = cost_to_date + estimated_cost_to_complete
```

**Percent complete (cost-to-cost)**, clamped to [0, 1]:
```
POC = cost_to_date / EAC          (0 if EAC == 0)
```

**Effective fee** (after approved change orders), by billing model:
```
FIXED_FEE          → fee = contract_fee + approved_fee_change_orders
PERCENT_OF_COST    → fee = rate × construction_cost (moves with the job)
TIME_AND_MATERIALS → fee = billable_hours × rate (revenue == work performed)
```

**Revenue recognized to date:**
```
FIXED_FEE / PERCENT_OF_COST → recognized = POC × fee     (≤ fee)
TIME_AND_MATERIALS          → recognized = billable work performed to date
```

**WIP (the owner's-rep heart)** — recognized vs billed:
```
WIP = recognized − billed_to_date
  WIP > 0  → UNDERBILLED  (asset: costs/profit earned but not yet invoiced)
  WIP < 0  → OVERBILLED   (liability: invoiced ahead of work — deferred revenue)
```

**Projected margin at completion** vs original — erosion is the warning signal:
```
projected_margin = (fee − EAC) / fee
original_margin  = (contract_fee − budgeted_cost) / contract_fee
erosion          = original_margin − projected_margin   (> 0 = margin slipping)
```

**Cash / receivables:**
```
retainage_held       = billed_to_date × retainage_pct
collectible_billed   = billed_to_date − retainage_held
accounts_receivable  = collectible_billed − collected_to_date   (≥ 0)
AR is bucketed by invoice age: current / 31–60 / 61–90 / 90+
```

## Reconciliation invariants (Hypothesis proves these)

These are exactly what a senior accountant will try to break. The property tests make them true for all valid inputs.

1. **Portfolio ties out:** `portfolio.recognized == Σ project.recognized` (and same for billed, cost, WIP, AR).
2. **WIP identity:** `recognized == billed + WIP` for every project (the pipeline must preserve this).
3. **Over/under partition:** `WIP > 0 ⇒ underbilled_asset == WIP`; `WIP < 0 ⇒ overbilled_liability == −WIP`; never both.
4. **POC bounds:** `0 ≤ POC ≤ 1`.
5. **No phantom revenue:** `recognized ≤ fee` (absent change orders increasing fee).
6. **Receivables sane:** `0 ≤ AR`, `retainage_held ≤ billed`, `Σ aging_buckets == AR`.
7. **Money conservation:** allocating/splitting a total across projects loses or creates **zero** pennies.
8. **Determinism:** same inputs → byte-identical Decimal outputs (no float nondeterminism).

## Seeded problems (so the narrative has something true to say)

- **DFW (healthcare)** — cost burning hot vs progress: EAC rising, POC ahead of billing → margin-at-completion erosion warning.
- **Omaha (medical)** — margin erosion + **unapproved** change orders (cost recognized, fee not yet) → unrecovered-CO warning.
- **UT (higher ed)** — aged A/R: large 90+ bucket, collections lagging → cash-gap warning.
- One **healthy** project as the control.
