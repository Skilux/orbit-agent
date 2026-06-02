---
name: eql-cheatsheet
description: "EQL syntax, recency idiom, and gotchas for Loomi analytics queries on Bloomreach."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [orbit, bloomreach, campaign]
    related_skills: []
---

# EQL Cheatsheet

**Tool:** `mcp__loomi-mcp__execute_analytics_eql({ project_id, query })`
**When:** every Loomi read that isn't a schema/consent lookup. EQL is the workhorse.
**Rate limit:** 1 req / 10s — space calls ~12–14s. A failed call still burns the slot. See README golden rule #1.

**Project ID (stable, do not hunt for it):** `abe73626-5469-11f1-8a97-6e3fd3d5a22f`
Do NOT waste calls trying `list_cloud_organizations`, `list_projects`, or reading `.env` files — those navigation tools are not available in this toolset. The project_id above is the only Bloomreach project; use it directly.

## Rate-limit survival (practical, from live sessions)
The 1 req/10s limit is enforced globally — a failed call STILL burns the slot.
When you hit "Too many requests", wait **at least 15–20s** before retrying (not 10 — the
clock starts at the previous call, and tool-call overhead adds latency you can't rely on).
Two back-to-back failures with identical args triggers a tool-loop warning; always
introduce a different spacing strategy rather than retry identically a third time.
Pattern that worked: fire call → get rate-limit error → wait 15s → retry → success.

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

Named lapsed cohort idioms:

Lapsed one-time buyer (bought exactly once, nothing in last 30 days):
```
count event purchase = 1 and count event purchase in last 30 days = 0
```
→ Live count (2026-05-31): DE 2,555 · UK 6,060 · USA 7,276 = ~15,891 total

Lapsed all buyers (bought at least once, nothing in last 30 days — "stopped shopping"):
```
count event purchase >= 1 and count event purchase in last 30 days = 0
```
→ Live count (2026-06-01): DE 2,935 · UK 6,842 · USA 8,247 = ~18,024 total

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
