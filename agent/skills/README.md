# Orbit Skills — Index

Reference skills teaching the Orbit marketing agent how to work with live Bloomreach data on project `crispy-ferret`. Each file is short, copy-paste-accurate, and validated live (2026-05-31).

## The two tool surfaces
- **Loomi MCP** (`mcp__loomi-mcp__*`) — hosted, **read-only**. Discovery + schemas + consent. The Planner uses this. Load via ToolSearch.
- **Custom `bloomreach` MCP** (`mcp__bloomreach__*`) — **write/monitor**. The Executor uses this. `set_customer_property`, `trigger_scenario`, `read_customer_events`, `read_customer_attributes`.

Least privilege: Planner can't write; Executor can't read Loomi.

## Skills
| File | Loop step | What it teaches |
|---|---|---|
| `eql-cheatsheet.md` | all reads | EQL syntax, recency idiom, breakdown/funnel forms, common parse errors |
| `discover-opportunity.md` | 2. Discover | The exact validated queries that surface the lapsed-buyer cohort + sizing |
| `read-customer-data.md` | 2. Discover | Schemas + per-customer attribute/event reads |
| `check-consent.md` | 4. Execute (pre-flight) | Why consent matters, how to confirm before sending |
| `author-offer-rfm.md` | 3. Decide+Author | RFM proxy from EQL → offer tier (no ML model exists) |
| `execute-campaign.md` | 4. Execute | The write+send sequence with order/async/prereqs |
| `monitor-and-iterate.md` | 5–6. Learn | Read campaign results, interpret status, propose iteration |
| `author-scenario.md` | build | Programmatically build a scenario JSON (clipboard format) for a human to paste into BR |

## Golden rules (these override convenience)
1. **Loomi rate limit: 1 request / 10 seconds** (measured tighter — leave ~12–14s + backoff on `Too many requests`). A *failed* call still burns the slot. Per-customer Loomi loops are impossible. Budget discovery to ~5–8 calls.
2. **Consent gate.** A customer must have accepted consent (category `other`) or the send is silently **SUPPRESSED** — not an error. Confirm before firing.
3. **Scenario must be RUNNING.** `orbit_winback` in Draft silently ignores every trigger event.
4. **PII masking.** Loomi `list_customers` returns `registered: ******`. Discover on **aggregates**; you cannot enumerate real emails. Execute on seeded known recipients.
5. **Everything is async (~3–30s).** Writes, events, and sends lag. Read-after-write may 404 → wait + retry. The trigger node adds a 30s delay (~90s before a `campaign` event appears).
6. **Discovery objects are EMPTY** — 0 predictions, 0 segmentations, 0 catalogs, 0 voucher pools. Discover via ad-hoc EQL, never pre-built segments. No ML churn model: use the RFM proxy.

## Reference IDs
| Thing | ID |
|---|---|
| Project `crispy-ferret` | `abe73626-5469-11f1-8a97-6e3fd3d5a22f` |
| Cloud org | `1e01c518-2d5e-4566-9091-3d100f95b03b` |
| Scenario `orbit_winback` | `6a1c6288edee51fad10d64aa` |
| Trigger event | `orbit_winback_triggered` |

Scale: 123,165 customers · 1.17M events · 30 event types · countries USA / UK / Germany.
