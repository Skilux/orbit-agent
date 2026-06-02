# EQL Cheatsheet

**Tool:** `mcp__loomi-mcp__execute_analytics_eql({ project_id, query })`
**When:** every Loomi read that isn't a schema/consent lookup. EQL is the workhorse.
**Rate limit:** 1 req / 10s — space calls ~12–14s. A failed call still burns the slot. See README golden rule #1.

## The shape of a query
```
select <metric> [by <breakdown> [grouping top N]] [customers matching (<filter>)]
```
- A `select` with **no `by`** parses as a non-executable "metric" → always add a breakdown (even `by customer.country`).
- Standalone expressions like `count event purchase` are not executable — wrap in `select ... by ...`.

## Metrics
- `count customers` — distinct customers
- `count event purchase` — number of events of a type
- `count event purchase_item` — items (a single order spans multiple item rows)
- `average event purchase.total_price` / `sum event purchase.total_price` — works even though `total_price` is stored as a string

## Breakdowns
- `by customer.country` — customer property
- `by event purchase_item.category_level_2 grouping top 10` — event property; **use `grouping top N`** (`by X top N` without `grouping` is a parse error)
- Order inside `by`: attribute → `grouping` → `format` → `with null`. `format` before `grouping` errors.
- Multiple dims: `by row X by column Y` (cross-tab). **Never separate dims/metrics with a comma** — comma is a parse error.

## The recency idiom (memorize this)
```
count event purchase in last 30 days = 0     ✅ works
count event purchase more than 30 days ago    ❌ parse error
```
Lapsed = "purchased once ever, none in the last 30 days":
```
count event purchase = 1 and count event purchase in last 30 days = 0
```

## customers matching (cohort filters)
- **Report-level** (applies to all metrics) goes **after** the `by` clause:
  `select count event purchase_item by event purchase_item.category_level_2 grouping top 10 customers matching (count event purchase = 1 and count event purchase in last 30 days = 0)`
- **Metric-level** (one metric only) goes **before** that metric's `by`:
  `select count customers matching (count event purchase >= 2) by customer.country`
- Supports full boolean logic (`and`, `or`, `not`, `xor`) and rich ops: `has value`, `has no value`, `starts with`, `between X and Y`, `has consent <category>`.

## Funnels
```
funnel session_start followed by purchase in last 30 days within 7 days end
```
- Must end with `end`. `in last` MUST come before `within`. Inline form inside `customers matching` uses `funnel(A followed by B)` with **no** `end`.

## Common parse errors (all hit live)
| You wrote | Error | Fix |
|---|---|---|
| `count customers customers matching (...)` | "Unexpected token matching" | one `customers`: `count customers matching (...)` |
| `... by customer.country, count ...` | "Unexpected token ," | metrics/dims are space-separated, no commas |
| `count event purchase more than 30 days ago` | parse error | use `in last 30 days = 0` |
| `by customer.country top 10` | parse error | `by customer.country grouping top 10` |
| top-level `where .field is null` | parse error | null checks unsupported; use `has no value` in `customers matching` |

## Gotcha
The `where` clause only accepts `and`-joined conditions — `or`/`not`/multiple `where` all error at the backend. Put boolean logic in `customers matching` instead.
