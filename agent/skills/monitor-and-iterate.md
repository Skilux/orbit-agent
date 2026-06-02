# Monitor + Iterate (Loop Steps 5–6)

**When:** after a send (wait ~90s — trigger has a 30s delay + send latency). Read results, interpret, then propose a data-grounded next move and pause for human approval (gate 2).

## Read results — per customer (Executor)
**`mcp__bloomreach__read_customer_events`** for the recipient(s). Look for `campaign` events and the engagement events that follow.
Key fields on the `campaign` event (from the schema):
- `status` — the verdict (see table below)
- `action_type` / `type` — channel (email)
- `subject`, `recipient`, `consent_category`, `error`, `sent_timestamp`

## Read results — cohort aggregate (Planner, Loomi)
For a one-shot cohort read instead of per-customer loops, aggregate over `campaign` events with EQL:
```
select count event campaign by event campaign.status grouping top 10
```
(Narrow with `customers matching (...)` to your cohort, or by `campaign_name`.) Respect the 1-req/10s limit. This dodges the impossible per-customer Loomi loop.

## Interpret `status`
| `status` | Meaning | Action |
|---|---|---|
| `sent` / `delivered` | ✅ Email went out | Done. Check opens/clicks next. |
| `suppressed` (+ "...has not given consent...") | Consent missing | Grant consent for that customer, re-fire. |
| (no `campaign` event at all) | Scenario didn't run | Confirm scenario **Running** + trigger name matches + wait longer (async). |
| `error` populated | Delivery failure | Read `error`; usually domain/Mailgun. |

Engagement signals after delivery: open / click events on the customer timeline (and `campaign` action sub-events). Low opens → subject-line problem; opens but no clicks → offer/copy problem.

## Propose an iteration (data-grounded)
Tie the next move to what the numbers say, e.g.:
- **Low open rate on the cohort** → sharper subject line for non-openers (re-author `email_headline`, re-send to non-openers).
- **Opens but no conversions on high-AOV silent customers** → bump `discount_tier` for that slice (e.g. 15 → 20) and re-author `email_body`.
- **Suppressed share high** → consent coverage gap; flag for seeding, not creative.

Present the proposal + the supporting numbers, **pause for human approval (gate 2)**, then loop back to `execute-campaign.md`.

## Gotcha
Don't read too early — a missing `campaign` event within the first ~90s means "still in the 30s delay node + async lag," not "failed." Re-read after waiting. And interpret `suppressed` as a consent problem, not a send failure.
