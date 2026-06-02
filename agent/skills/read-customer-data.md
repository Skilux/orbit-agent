# Read Customer Data (Schemas + Per-Customer)

Use schema reads to learn what's available; use per-customer reads to verify writes and monitor a single profile.

## Schemas — Loomi (read-only)
**`mcp__loomi-mcp__get_event_schema({ project_id })`**
When: you need exact event types + property names before writing EQL.
Returns all 30 event types. Key facts confirmed live:
- `purchase` props: `currency, payment_method, product_ids, product_list, purchase_id, purchase_source_type, purchase_status, total_price` — **no category here.**
- `purchase_item` props: `brand, category_level_1, category_level_2, category_level_3, price, product_id, quantity, size, title` — categories live here.
- `campaign` props (monitoring): `action_type, campaign_name, status, subject, recipient, consent_category, error, message_id, sent_timestamp` — `status` is what you check after a send.
- Custom: `orbit_winback_triggered` (props `source`, `offer_code`) — the event that launches the scenario.

**`mcp__loomi-mcp__get_customer_property_schema({ project_id })`**
When: you need the customer attribute names (e.g. confirm `first_name`, `email`, and the agent-written `email_headline`/`email_body`/`offer_code`/`discount_tier` exist).
Costs a rate-limit slot — fold it into the discovery budget.

## Per-customer — custom `bloomreach` MCP (Executor)
**`mcp__bloomreach__read_customer_attributes`**
When: verify a `set_customer_property` write actually landed before triggering.
Read-after-write may **404 / show stale values** for ~3–30s → wait and retry.

**`mcp__bloomreach__read_customer_events`**
When: monitor one customer's `campaign` / `orbit_winback_triggered` / open / click events after a send. See `monitor-and-iterate.md`.

## Gotcha
PII masking: Loomi `list_customers` returns `registered: ******`, so you **cannot enumerate real emails** to build a target list. Discover on aggregates (Loomi EQL); operate per-customer only on **seeded known recipients** whose email you already have.
