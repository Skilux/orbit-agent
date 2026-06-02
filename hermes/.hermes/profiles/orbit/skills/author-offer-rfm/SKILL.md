---
name: author-offer-rfm
description: "Compute an RFM proxy from EQL aggregates and map it to an offer tier and email copy."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [orbit, bloomreach, campaign]
    related_skills: []
---

# Author the Offer — RFM Proxy (Loop Step 3)

**Honest substitute:** the sandbox has **0 prediction models** (0 predictions, 0 segmentations). Do **not** pitch an "ML churn score." Instead the agent computes a lightweight **RFM proxy** (Recency + Frequency + monetary AOV) from EQL aggregates, then maps it to an offer tier. Transparent and needs no model.

**Tool:** `mcp__loomi-mcp__execute_analytics_eql` for the inputs; the tiering is pure LLM reasoning (no tool).

## The three signals (all from EQL, cohort-level)
| Signal | EQL it comes from | Cohort value (live 2026-05-31) |
|---|---|---|
| **R**ecency | `count event purchase in last 30 days = 0` (lapsed) | all 30d+ silent |
| **F**requency | `count event purchase = 1` | exactly one order ever |
| **M**onetary (AOV) | `select average event purchase.total_price by customer.country customers matching (...)` | DE $1,002 / UK $1,062 / USA $965 |

For a richer per-segment read, break AOV by category_level_2 the same way (see `discover-opportunity.md`).

## Map to an offer tier
The agent reasons over R/F/M to pick `discount_tier` + `offer_code`. A defensible default mapping:

| Tier reasoning | `discount_tier` | `offer_code` example |
|---|---|---|
| High AOV (>$1,000) + long silence → high-value silent, worth a bigger pull | 20 | `WB20` |
| Mid AOV, single purchase → standard win-back | 15 | `WB15` |
| Lower AOV / recently-ish lapsed → light nudge | 10 | `WB10` |

The agent should **state its reasoning** ("AOV ~$1,062 in UK and 30d+ silent → tier 20") so the human can sanity-check at the approval gate.

## Output of this step (the personalization contract)
The agent authors and will write (next step) these customer properties:
`first_name`, `email`, `email_headline`, `email_body`, `offer_code`, `discount_tier`.
`email_headline` / `email_body` are the agent-written copy, grounded in the customer's history (category they bought, AOV, time lapsed).

## A/B test extension
When the human asks for an A/B test, split on **framing**, not just discount level — same
`discount_tier` across variants lets you isolate the copy signal cleanly. Proven pattern:

| Variant | Frame | offer_code suffix |
|---|---|---|
| A | Discount-led ("here's 20% off") | WB20A |
| B | FOMO-led ("new arrivals moving fast — your 20% is waiting") | WB20B |

50/50 split. Primary KPI: 7-day purchase conversion. Secondary: 48h open rate (faster
signal, declare winner first). The scenario uses an `ab-split` node — see `author-scenario`.

## Gotcha
There is no voucher pool on the sandbox (0 pools), so `offer_code` is a **static string the agent invents**, not a redeemable code from a ledger. Fine for the demo — disclose it. Keep `discount_tier` numeric (the template renders it directly).
