---
name: execute-campaign
description: "Write/trigger/verify sequence to ship a campaign via the custom bloomreach MCP."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [orbit, bloomreach, campaign]
    related_skills: []
---

# Execute the Campaign (Loop Step 4)

**Surface:** custom `bloomreach` MCP only (the Executor). Runs **after** the human approves the brief (gate 1).
**Sequence:** write properties → wait → fire trigger → (scenario sends). Order and waits matter.

## Prerequisites (both or the send silently fails)
1. Scenario `orbit_winback` is **RUNNING** (not Draft). Draft ignores every event, no error.
2. Target customer has **consent** category `other` (see `check-consent.md`). No consent → `status: suppressed`.

## Step 1 — write copy + offer
**`mcp__bloomreach__set_customer_property`** — write the full personalization contract for the customer:
`first_name`, `email`, `email_headline`, `email_body`, `offer_code`, `discount_tier`.
The template renders `{{ customer.email_headline }}` / `{{ customer.email_body | safe }}` / `{{ customer.offer_code }}` / `{{ customer.discount_tier }}` — so every variable the template references **must** be written here.

Optionally call **`mcp__bloomreach__read_customer_attributes`** to verify the write landed (may 404/stale for a few seconds — wait + retry).

## Step 2 — wait ~15s
Property writes ingest asynchronously (~3–30s). Firing the trigger before the write lands renders an email with missing/old values. Wait ~15s after step 1.

## Step 3 — fire the trigger
**`mcp__bloomreach__trigger_scenario`** — fires event `orbit_winback_triggered` for the customer (props can include `source`, `offer_code`).
This launches `orbit_winback`: `on-event-trigger` (30s delay) → `send-email-action` (Mailgun) → checks consent → renders template → INBOX.

## Step 4 — let it run
The trigger node has a **30s delay**, plus send latency. A `campaign` event appears **~90s** after firing. Don't conclude failure earlier. Then go to `monitor-and-iterate.md`.

## Order summary
```
set_customer_property (copy+offer)  →  wait ~15s  →  trigger_scenario(orbit_winback_triggered)  →  ~90s  →  campaign event
```

## Gotcha
Every variable the email template references must be set in step 1 — a missing `email_body` renders blank, not an error. And the recipient `email` property is what Mailgun sends to; if it's wrong/missing the send can't address. Sandbox emails may land in **spam** (unverified Mailgun domain) — acceptable for the demo, disclose it.
