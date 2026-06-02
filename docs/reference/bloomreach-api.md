# Bloomreach Engagement REST API — Tested & Working

What we've **verified live** against the `crispy-ferret` sandbox for Orbit's write-back layer. The Loomi MCP is read-only; everything here is the REST write/read path the custom write-MCP wraps.

Credentials live in `.env` (git-ignored). Shape in `.env.example`.

---

## Connection

| Setting | Value |
|---|---|
| API base | `https://uqa.api.exponea.dev` *(API host — NOT the app host `uqa.app.exponea.dev`)* |
| Project token | `BR_PROJECT` (crispy-ferret) |
| Auth | HTTP **Basic** — `Authorization: Basic base64(BR_KEY:BR_SECRET)`. In curl: `-u "$BR_KEY:$BR_SECRET"` |
| Credential source | Private API group → Engagement → Settings → Access Management → API |

**Path split:** **writes → `track/v2`**, **reads → `data/v2`**. Different prefixes, same auth.

**Writes are async.** A tracked property/event takes ~10–20s to materialize in the customer profile. Read-immediately-after-write can return `404 Customer does not exist`; it succeeds on retry. Any monitoring / read-after-write logic must tolerate this lag.

---

## ✅ Tested & working

### 1. Set customer property — `set_customer_property`
```bash
curl -sS -X POST "$BR_BASE/track/v2/projects/$BR_PROJECT/customers" \
  -u "$BR_KEY:$BR_SECRET" -H "Content-Type: application/json" \
  -d '{"customer_ids":{"registered":"orbit-test@email.com"},"properties":{"recovery_initiated":true}}'
```
Response: `{"success":true,"errors":[]}` — HTTP 200
Creates the customer if absent. Hard ID `registered` works.

### 2. Read customer attributes (verify a write landed)
```bash
curl -sS -X POST "$BR_BASE/data/v2/projects/$BR_PROJECT/customers/attributes" \
  -u "$BR_KEY:$BR_SECRET" -H "Content-Type: application/json" \
  -d '{"customer_ids":{"registered":"orbit-test@email.com"},"attributes":[{"type":"property","property":"recovery_initiated"}]}'
```
Response (after ingestion): `{"results":[{"success":true,"value":true}],"success":true}` — HTTP 200
Before ingestion completes: `{"errors":{"_global":["Customer does not exist"]},"success":false}` — HTTP 404 (retry).

### 3. Track custom event — `trigger_scenario` (event-driven)
```bash
curl -sS -X POST "$BR_BASE/track/v2/projects/$BR_PROJECT/customers/events" \
  -u "$BR_KEY:$BR_SECRET" -H "Content-Type: application/json" \
  -d '{"customer_ids":{"registered":"orbit-test@email.com"},"event_type":"orbit_winback_triggered","properties":{"source":"validation"}}'
```
Response: `{"success":true,"errors":[]}` — HTTP 200
Pattern: hand-build a scenario in Engagement triggered by this `event_type`; the agent fires the event to launch it. (No REST endpoint creates/edits scenarios — pre-build in UI.)

### 4. Read customer events — monitoring + journey inference
```bash
curl -sS -X POST "$BR_BASE/data/v2/projects/$BR_PROJECT/customers/events" \
  -u "$BR_KEY:$BR_SECRET" -H "Content-Type: application/json" \
  -d '{"customer_ids":{"registered":"orbit-test@email.com"},"event_types":["orbit_winback_triggered"]}'
```
Response: `{"success":true,"data":[{"properties":{"source":"validation"},"timestamp":1780228246.37,"type":"orbit_winback_triggered"}]}` — HTTP 200
Powers Step 5 monitoring and the journey-state inference workaround (no real-time scenario telemetry exists).

### 5. Batch tracking — efficient synthetic seeding
```bash
curl -sS -X POST "$BR_BASE/track/v2/projects/$BR_PROJECT/batch" \
  -u "$BR_KEY:$BR_SECRET" -H "Content-Type: application/json" \
  -d '{"commands":[
        {"name":"customers","data":{"customer_ids":{"registered":"orbit-seed-1@email.com"},"properties":{"first_name":"Seed","churn_risk":"high"}}},
        {"name":"customers/events","data":{"customer_ids":{"registered":"orbit-seed-1@email.com"},"event_type":"purchase","properties":{"total_price":42.5}}}
      ]}'
```
Response: `{"results":[{"success":true},{"success":true}],"success":true}` — HTTP 200
Multiple `commands` per call (mix `customers` + `customers/events`). This is the path to seed the demo dataset (Steps 5–6 need data — none is seeded by Bloomreach). Custom event types/properties are accepted schema-on-write.

---

## ⏳ Not yet tested

### Transactional email — `send_transactional_email`
```
POST $BR_BASE/email/v2/projects/$BR_PROJECT/sync
```
**Disabled by default** — must be enabled by Bloomreach CSM/support per project (request in `#bloomreach-sandbox-support` for `crispy-ferret`). Body is heavier (integration id + recipient + content) — document once enabled. Mailgun is already pre-integrated on the Engagement side, so delivery exists; only the transactional *API* is gated.

---

## Failure codes seen / expected
| Code | Meaning |
|---|---|
| 200 `success:true` | OK |
| 404 `Customer does not exist` | Async ingestion lag (retry) **or** wrong project token / id |
| 401 | Bad auth — wrong host, non-private key, key/secret swapped, **or** shell mangling: don't stuff `-u` into an unquoted variable; pass `-u "$BR_KEY:$BR_SECRET"` inline |
| 403 | API group missing that permission scope |

---

## Maps to the write-MCP
| MCP tool | Endpoint | Status |
|---|---|---|
| `set_customer_property` | `track/v2/.../customers` | ✅ |
| `trigger_scenario` | `track/v2/.../customers/events` | ✅ |
| `send_transactional_email` | `email/v2/.../sync` | ⏳ pending enablement |

Supporting (validated, not MCP tools but used by the agent/seeder):
| Use | Endpoint | Status |
|---|---|---|
| Read customer events (monitor/infer) | `data/v2/.../customers/events` | ✅ |
| Read customer attributes (verify) | `data/v2/.../customers/attributes` | ✅ |
| Batch seed customers + events | `track/v2/.../batch` | ✅ |

Reads for context/monitoring (segments, predictions, analytics) come from the **Loomi MCP** (OAuth, read-only) — see `slack.md` / `loomi-connect-architecture` memory.
