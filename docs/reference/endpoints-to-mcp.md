# Orbit — Engagement REST Endpoints to Wrap in the Custom MCP

**Server name:** `engagement-mcp` (writes + real-time reads — "write-mcp" is a misnomer)
**Decision:** Real email is delivered by a **pre-built scenario** in the Engagement UI, triggered by an event the agent fires. **`send_transactional_email` is NOT wrapped** — redundant with the scenario path and removes the CSM-enablement dependency.

All endpoints below are **validated live** against `crispy-ferret` (see `BR-API.md`).

---

## Connection (shared by all tools)

| Setting | Value |
|---|---|
| API base (`BR_BASE`) | `https://uqa.api.exponea.dev` *(API host — NOT app host `uqa.app.exponea.dev`)* |
| Project (`BR_PROJECT`) | `crispy-ferret` → `abe73626-5469-11f1-8a97-6e3fd3d5a22f` |
| Auth | HTTP **Basic** — `Authorization: Basic base64(BR_KEY:BR_SECRET)` |
| Credential source | Private API group → Engagement → Settings → Access Management → API |
| Path split | **writes → `track/v2`** · **reads → `data/v2`** (same auth) |

**Async-write lag:** tracked properties/events take ~10–20s to materialize. Read-after-write can return `404 Customer does not exist` and succeed on retry. All read tools must tolerate this (retry/backoff).

**Never log `BR_KEY` / `BR_SECRET`.** Load from `.env` (git-ignored); ship `.env.example` only.

---

## Tools to wrap (4)

### 1. `set_customer_property` — WRITE
The personalization channel: agent writes its decided offer/state; the scenario email template renders it.

- **Method / path:** `POST {BR_BASE}/track/v2/projects/{BR_PROJECT}/customers`
- **Input schema:**
  - `customer_id` (string, required) → maps to `customer_ids.registered`
  - `properties` (object, required) — e.g. `{ "offer_code": "WB20", "discount_tier": 20, "recovery_initiated": true }`
- **Request body:**
  ```json
  {"customer_ids":{"registered":"<customer_id>"},"properties":{ ... }}
  ```
- **Success:** `{"success":true,"errors":[]}` (HTTP 200). Creates the customer if absent.
- **Why:** Injects the agent's *decision* (the personalized offer) into the customer profile so the scenario can render it. Load-bearing for "personalized," not for delivery.

### 2. `trigger_scenario` — WRITE (the campaign-facing action)
Fires the event the pre-built win-back scenario listens for. **This is the human-approved action.**

- **Method / path:** `POST {BR_BASE}/track/v2/projects/{BR_PROJECT}/customers/events`
- **Input schema:**
  - `customer_id` (string, required) → `customer_ids.registered`
  - `event_type` (string, required) — e.g. `orbit_winback_triggered`
  - `properties` (object, optional) — event context, e.g. `{ "source": "orbit", "offer_code": "WB20" }`
- **Request body:**
  ```json
  {"customer_ids":{"registered":"<customer_id>"},"event_type":"<event_type>","properties":{ ... }}
  ```
- **Success:** `{"success":true,"errors":[]}` (HTTP 200).
- **Why:** Launches the real campaign. Scenario (hand-built in UI, triggered by `event_type`) sends the email through Bloomreach's own delivery. No REST endpoint creates scenarios — pre-build in UI.

### 3. `read_customer_events` — READ (monitoring, closes the loop)
Step 5: did the scenario fire? any opens/clicks? Drives the iteration proposal.

- **Method / path:** `POST {BR_BASE}/data/v2/projects/{BR_PROJECT}/customers/events`
- **Input schema:**
  - `customer_id` (string, required) → `customer_ids.registered`
  - `event_types` (string[], required) — e.g. `["orbit_winback_triggered","email_open","email_click"]`
- **Request body:**
  ```json
  {"customer_ids":{"registered":"<customer_id>"},"event_types":[ ... ]}
  ```
- **Success:** `{"success":true,"data":[{"properties":{...},"timestamp":<epoch>,"type":"<event>"}]}` (HTTP 200).
- **Why:** Near-real-time event read (Loomi analytics lags via warehouse). Powers monitoring + iteration without a second OAuth surface and dodges Loomi's 1-req/sec limit.

### 4. `read_customer_attributes` — READ (verify write landed) — *optional but recommended*
Confirms property writes materialized; clean "see, the offer is set" demo beat. Handles the async lag.

- **Method / path:** `POST {BR_BASE}/data/v2/projects/{BR_PROJECT}/customers/attributes`
- **Input schema:**
  - `customer_id` (string, required) → `customer_ids.registered`
  - `properties` (string[], required) — property names to read, e.g. `["offer_code","recovery_initiated"]`
- **Request body:**
  ```json
  {"customer_ids":{"registered":"<customer_id>"},"attributes":[{"type":"property","property":"<name>"}]}
  ```
  (one `attributes` entry per requested property)
- **Success (after ingestion):** `{"results":[{"success":true,"value":<v>}],"success":true}` (HTTP 200).
- **Before ingestion:** `{"errors":{"_global":["Customer does not exist"]},"success":false}` (HTTP 404 → retry).
- **Why:** Verifies tool #1 landed; gives the Executor a `verify=true` read-back option against the 10–20s lag.

---

## NOT wrapped

| Endpoint | Reason |
|---|---|
| `send_transactional_email` (`POST email/v2/.../sync`) | **Dropped by decision.** Scenario delivers the real email. Removes CSM-enablement dependency. |

---

## Supporting (used by the seed script — NOT an MCP tool)

| Use | Endpoint |
|---|---|
| Batch-seed synthetic customers + events (own known-email recipients, to work around PII masking) | `POST {BR_BASE}/track/v2/projects/{BR_PROJECT}/batch` |

```json
{"commands":[
  {"name":"customers","data":{"customer_ids":{"registered":"orbit-seed-1@rohlik.cz"},"properties":{"first_name":"Seed","last_purchase_days":45}}},
  {"name":"customers/events","data":{"customer_ids":{"registered":"orbit-seed-1@rohlik.cz"},"event_type":"purchase","properties":{"total_price":42.5}}}
]}
```
Lives in `seed.ts`, not the MCP server.

---

## Failure codes

| Code | Meaning |
|---|---|
| 200 `success:true` | OK |
| 404 `Customer does not exist` | Async ingestion lag (retry) **or** wrong project token / id |
| 401 | Bad auth — wrong host, key/secret swapped, or shell mangling (`-u "$BR_KEY:$BR_SECRET"` inline) |
| 403 | API group missing that permission scope |

---

## Tools once proposed (2) — NOT BUILT / deferred — see `scenarios.md` (Appendix C)

**Decision (2026-05-31):** neither tool below is built. They are **replaced** by (a) **saved EQL queries** the Planner runs for cohort sizing + results, and (b) the demo **targeting a single known recipient** (so no count→members export is needed). The 4 tools above are the complete v1 custom MCP. Kept here for context / future scope only.

### 5. `read_campaign_performance` — READ (the Learn step) — NOT BUILT
Aggregates cohort-level results in ONE call so the Planner doesn't loop per-customer (blocked by Loomi's 1-req/10s limit).

- **Approach:** EQL/report aggregate over `campaign` events (`action_type` = opened/clicked) + `orbit_winback_triggered` + downstream `purchase`, filtered by a cohort tag/property.
- **Input:** `cohort_tag` (or property filter), `since` (timestamp/window).
- **Returns:** `{sent, opened, clicked, converted, rates}`.
- **Why:** powers Step 6 iteration. Per-customer `read_customer_events` can't scale to a cohort at the rate limit.

### 6. `query_cohort_ids` — READ (count → members) — NOT BUILT
Bridges the biggest gap: EQL returns *counts*, `list_customers` masks emails — the agent finds 15,891 lapsed buyers but can't get the recipient list.

- **Approach:** wrap Engagement customer export (`data/v2/.../customers/export` or segment export) with the EQL-equivalent predicate; return registered IDs.
- **Input:** behavioral predicate (e.g. `purchases_lifetime=1 AND purchase_in_last_30d=0`), `limit`.
- **Returns:** list of `registered` IDs.
- **Demo fallback:** `seed.ts` creates a known-email cohort matching the discovered pattern; agent acts on those. Build the full export tool only if time allows.

---

## Build summary

**4 MCP tools built ✅ — this is the complete v1 custom MCP.** The 2 once-proposed extras (`read_campaign_performance`, `query_cohort_ids`) are **NOT built** — replaced by saved EQL queries the Planner runs + a single known demo recipient.
**2 prefixes:** `track/v2` (writes), `data/v2` (reads).
**1 auth:** HTTP Basic from env (wired into the Executor's Hermes config only — the Planner never sees it).
**0 external dependencies:** no CSM gate, no Loomi for the write/monitor path.

