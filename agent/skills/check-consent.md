# Check Consent (Pre-Flight Before Any Send)

**Why it matters:** the `orbit_winback` email node checks consent. A customer **without** consent in category `other` → the send is silently **SUPPRESSED** (a `campaign` event with `status: suppressed`, *not* an error). Miss this and you'll think you sent an email that never left.

## 1. Read the project's consent setup — Loomi
**`mcp__loomi-mcp__get_consent_settings({ project_id })`**
When: confirm which consent category the scenario requires. The `orbit_winback` email node uses category **`other`**.
(Costs a rate-limit slot — space ~12–14s.)

## 2. Confirm a specific customer has consent before firing
Two ways:
- **EQL aggregate** (Planner) — count how many in your cohort already consent:
  ```
  select count customers matching (has consent other) by customer.country
  ```
- **Per-customer** (Executor) — `mcp__bloomreach__read_customer_events` and look for a `consent` event with `action: accept`, `category: other`. Or read the `campaign` event after a test fire and check `status`.

## 3. Grant consent (seeding only — normally done in seed.ts, not per-send)
Consent is set by firing a `consent` event with `action: accept`, `category: other`, `valid_until: unlimited`. In the demo, seeded recipients already have it. Granting is a **one-time** step per customer, part of seeding — not part of the per-send flow.

## Gotcha
Suppression is silent. Always treat "no consent" as the default failure mode when an email doesn't arrive: check the `campaign` event's `status` (`suppressed` + a "...has not given consent..." message) before blaming the scenario or Mailgun.
