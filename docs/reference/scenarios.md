# Orbit — Scenarios & Use Cases

**Single source of truth** for *what the agent does* and *what data/tools it touches*. Merges the former `DEMO-SCENARIOS.md`, `USE-CASES.md`, `agentic-design.md`, and `orbit-idea.md`.

Companions: `PRD.md` (master spec) · `winback-scenario.md` (operational runbook) · `endpoints-to-mcp.md` (tool wrapping spec) · `BUILD-STEPS.md` (execution plan).

---

## 1. The shift — why this is an agent, not a script

The hackathon scores **understand → decide → act**. v1 (the validated plumbing) only *acts*. The intelligence must move upstream — into deciding **what** campaign to run, not just running a pre-decided one.

| v1 (rule) | v2 (agentic) |
|---|---|
| Human says "win back 30d lapsed" | Human gives a loose goal ("find me a revenue opportunity") |
| Agent runs a fixed playbook | Agent **discovers** the cohort worth chasing, with a $ number |
| Pre-written email template | Agent **authors** the offer + the email copy from the data |
| Fixed "iterate" step | Agent **designs** the next move from real results |

Three new agent responsibilities:

1. **DISCOVER** — explore real data (Loomi EQL aggregates, schemas) → opportunity grounded in numbers.
2. **DECIDE + AUTHOR** — invent the campaign: audience, offer size, angle, email copy. The Planner sets customer properties (`email_headline`, `email_body`) that the email shell renders — agent reasoning flows straight into the real email through validated infrastructure.
3. **LEARN** — read results, design a data-grounded iteration.

### Ambition levels (Level 2 chosen)

- **Level 1** — Adaptive offer (human picks audience, agent decides offer + copy).
- **Level 2 ⭐ CHOSEN** — Opportunity finder (human gives loose goal; agent explores, diagnoses, proposes whole campaign incl. copy; human approves; runs; iterates).
- **Level 3** — Autonomous strategist (open-ended, ranks multiple opportunities). Too risky for the build window.

---

## 2. The discoverable insight (the anchor)

Validated live on `crispy-ferret` sandbox (2026-05-31):

- Lapsed one-time buyers ≈ **15,891** (US 7,276 / UK 6,060 / DE 2,555).
- Repeat-purchase rate ≈ **12%**. AOV ≈ **$1,000**.
- Category split (item counts, `purchase_item.category_level_2`): Women 10,320 / Men 4,820 / Shoes 631 / Jewelery 343.
- Found in one EQL query. **Pre-seed only the recipients, never the pattern.**
- No ML models on sandbox → **RFM proxy** (recency + frequency + AOV from EQL) is the honest substitute.

---

## 3. Three demo modes (one backend, three surfaces)

Narrative arc for the 5–6 min video: **one agent, three surfaces** — chat (intelligence) → cron (automation) → Kanban (scale). ~90s each. All three equal weight.

All modes run on the two least-privilege Hermes configs:
- **Planner** — Loomi MCP (read-only EQL), authors copy, stops at Gate 1.
- **Executor** — custom `bloomreach` MCP (4 write/read tools), builds + ships.

### Mode 1 — Chat (reactive / ad-hoc) 🗣️  [HERO #1]

**Prompt:** "Revenue's soft this month. Find me a revenue opportunity in the data and prep a campaign."

**Flow:**
1. Planner runs serialized EQL → discovers lapsed one-time buyers.
2. Computes RFM proxy.
3. Decides offer + **authors email copy** (headline + body).
4. Emits brief → **stops at Gate 1**.
5. Human confirms → Executor `set_customer_property` → `read_customer_attributes` (verify) → `trigger_scenario` → wait 60s → `read_customer_events` (confirm sent) → **real email lands**.

**Judge takeaway:** understand → decide → act from one vague sentence.
**Build cost:** ~zero (core loop). **Demo:** ~90s.

### Mode 2 — Scheduled cron (proactive / repetitive) ⏰  [HERO #2]

**Trigger:** Hermes cron, daily 09:00 — "Lapsed-buyer morning sweep."

**Decision: AUTO-SEND UNDER CAP.**
- Human gives **standing approval** of the playbook + sets a daily cap once.
- Agent auto-executes win-back up to the cap.
- **Escalates anything over the cap to Gate 1.**
- MUST be disclosed in the responsible-design note: approval is at the policy level (human approved the rule + cap), not silent autonomy.

**Flow each run:**
1. EQL: count customers crossing lapse threshold in last 24h (first purchase, no repeat, 30d silent).
2. Compare to yesterday → "142 newly lapsed."
3. Queue into win-back, **cap at N**, auto-send within cap.
4. Write digest: "142 new lapsed (Women 91 / Men 38 / Shoes 13). Sent N, escalated {142-N} for approval."

**Build cost:** low — "delta since yesterday" EQL + cap/escalation logic + Hermes scheduled trigger. **Demo:** pre-record one fire + show cron entry + digest.

### Mode 3 — Kanban (parallel / multitasking) 📋  [HERO #3]

**Board:** "Q3 Reactivation Sprint." Human drops cards; agent works each like a teammate, moving `To Do → In Progress → Needs Approval (Gate) → Done`.

| Card | Agent task |
|------|-----------|
| A | Win-back lapsed **Women's** buyers (10,320) — discover, author copy, prep |
| B | Win-back lapsed **Men's** buyers (4,820) — different offer/tone |
| C | Draft **cart-abandoner** scenario JSON (new campaign type → Gate 2 import) |
| D | Build **performance EQL** — opens/clicks/conversions dashboard query |

**Judge takeaway:** agent juggles a backlog across segments, parks at approval, multitasks like a real team.
**Build cost:** med — category-split EQL (validated filter) + Hermes Kanban wiring + cart-abandoner scenario authoring. **Demo:** ~90s showing 2–3 cards flow.

---

## 4. Cross-cutting use cases (bolt onto any mode)

### UC-4 — Pre-Send Safety Audit 🛡️

**Where it runs:** Bolts onto Gate 1 in all 3 modes (or chat standalone: "Safe to send win-back this week?"). Agent does due diligence *before* any send.

**Why it matters:** Lights up 4 Loomi categories no other mode touches. Pure responsible-AI story — agent refuses to act blindly. Hits **MCP Depth** + **Execution Quality** + **Agent Behavior** at once.

**Checks (8+ tools across 5 categories):**

| Check | Loomi tools | Agent conclusion |
|-------|-------------|------------------|
| Campaign collision | `list_email_campaigns`, `get_campaign_calendar` | "Another send hits this audience Thu — dedupe / wait" |
| Frequency rules | `get_frequency_policies` | "Project caps 2 emails/wk — within policy" |
| Consent | `get_consent_settings` | "Marketing consent required on `email` — filtering non-consented" |
| Voucher stock | `list_voucher_pools`, `list_voucher_codes` | Pools empty 05-31 → "no codes in stock, flat 15% not a code" (honest reasoning, tool still exercised) |
| Scenario transparency | `list_scenarios`, `list_scenario_nodes`, `get_scenario_node` | Reads node graph → at gate explains "fires 30s delay → Mailgun email" |

**Build cost:** low — all read-only EQL/REST, serialized. **Demo:** ~30s pre-Gate panel ("Safety audit: ✅ no collisions, ✅ frequency OK, ⚠️ no voucher codes — using flat %").

### UC-5 — Catalog-Aware Personalized Offer 🛍️

**Pitch:** "10% off" → "3 new arrivals in Women's, picked for you." Lights up entire **Catalog** category (zero coverage today).

**Flow:**
1. Read lapsed buyer last-purchased category — `list_customer_events`, `get_customer_properties`.
2. Find product catalog — `list_catalogs`, `get_catalog_configuration`.
3. Pull real products in that category — `list_catalog_items`, `get_catalog_item`.
4. Planner injects specific SKUs into authored copy → Executor ships.

**Wow factor:** Generic discount → concrete personalized product picks. Makes agent-authored copy visibly data-driven.

**⚠️ Data risk:** v2 catalog object may be empty (like predictions/segmentations were 05-31). Category split came from *event* data, not necessarily populated catalog. **Verify `list_catalogs` on `crispy-ferret` first.**

**Fallback UC-5b — Project Opportunity Scan:** if catalog empty, `whoami` → `list_projects_with_overview` → `get_project_overview` → `list_trends` / `list_funnels` / `list_reports`. Low-risk exec-summary opener, always returns data, lights up Navigation + Analytics categories.

**Build cost:** low (UC-5) / trivial (UC-5b). **Demo:** ~20s inside Mode 1 ("agent picked these 3 SKUs from catalog → pasted into email body").

---

## 5. Tool-coverage tally (MCP Usage submission artifact)

- **Before UC-4/5:** ~5 Loomi tools, ~2 categories (mostly EQL).
- **After UC-4 + UC-5:** **~15+ distinct tools across 8 categories** — Navigation, Customer reads, Analytics, Campaigns introspection, Frequency, Consent, Vouchers, Catalog.

Concrete line for the **MCP Usage Explanation** submission artifact.

---

## 6. Demo narrative (6-min video script)

> Type a vague goal → watch the agent reason over real numbers → surfaces *"~16k first-time buyers never came back — that's ~$X left on the table"* → proposes a campaign **and shows the email copy it wrote** → safety audit panel (UC-4) confirms no collisions → human approves (gate 1) → sends a real email → returns: *"opens are low on this cohort, here's a sharper subject line"* → human approves the iteration.

Unmistakably an agent, not a script.

---

## 7. Dependencies (blocker order)

1. **Step A** — wire two Hermes configs (Planner read-only, Executor write-only). BLOCKS ALL.
2. **Step B** — run Mode 1 end-to-end in Hermes. Proves the loop.
3. UC-4 safety audit panel (read-only, low risk — bolt onto Gate 1).
4. Verify `list_catalogs` populated → ship UC-5; else fall back to UC-5b.
5. Mode 2 cron skill (delta EQL + cap/escalation).
6. Mode 3 Kanban wiring + segment EQL + cart-abandoner JSON.

---

## 8. Responsible-design note must cover

- Sandbox-only data; no PII outside Bloomreach.
- Gate 1 (terminal confirm) + Gate 2 (scenario import for new types).
- Mode 2 standing-approval + cap framing (policy-level human approval).
- RFM heuristic (no ML); single seeded demo recipient; spam placement (unverified Mailgun domain).
- UC-4 audit findings disclosed (e.g. "voucher pool empty — flat % offer used instead of code").

---

# Appendix A — Loomi MCP verified tool inventory

**75+ tools across 14 categories**, confirmed live on `loomi-mcp-alpha.bloomreach.com/mcp` (2026-05-31). Auth = OAuth (drop trailing slash from URL or callback fails).

## Navigation & bootstrap
| Tool | Purpose |
|---|---|
| `whoami` | Returns auth identity — perfect demo opener |
| `list_cloud_organizations` | Discover orgs the bearer can see |
| `list_workspaces` | Workspaces inside an org |
| `list_projects` | All projects across an org (returns the project UUID needed by every other tool) |
| `list_projects_with_overview` | Same + KPI snapshot per project (single round-trip) |
| `get_cloud_organization_details` | Org-level admin metadata |
| `get_project_overview` | Customer/event counts, active-campaign counts, quota |

## Customer reads
| Tool | Purpose |
|---|---|
| `list_customers` | Paginated search across identifier fields (email, cookie). NOT property search. |
| `get_customer_properties` | Full property dump + expression-derived attributes for one customer |
| `list_customer_events` | Per-customer event history, filterable by type and `days_back` |
| `get_customer_schema` | Identifier fields config (hard/soft, transforms) |
| `get_customer_property_schema` | All property definitions in the project |

## Segments & filters
| Tool | Purpose |
|---|---|
| `list_segmentations` / `get_segmentations` | Named segmentations + full definition |
| `list_customers_in_segment` | Paginated customer IDs inside a specific named segment |
| `list_event_segmentations` / `get_event_segmentation` | Event-based partitioning |
| `list_customer_filters` / `get_customer_filter` | Reusable filter conditions |
| `list_autosegments` / `get_autosegment` | ML-discovered segments |

> Sandbox 05-31: empty.

## Predictions
| Tool | Purpose |
|---|---|
| `list_predictions` / `get_prediction` | Discover churn / LTV / propensity prediction jobs |
| `get_customer_prediction_score` | Per-customer score + last update timestamp |

> Sandbox 05-31: empty → driving RFM proxy fallback.

## Analytics (the Planner's reasoning workhorse)
| Tool | Purpose |
|---|---|
| **`execute_analytics_eql`** | Ad-hoc EQL queries — reports & funnels |
| `execute_analytics` | Same intent via JSON definition |
| `list_aggregates` / `get_aggregate` | Customer-history aggregates |
| `list_running_aggregates` / `get_running_aggregate` | Streaming aggregates |
| `list_expressions` / `get_expression` | Derived attribute formulas |
| `list_funnels` / `get_funnel` | Saved funnel definitions |
| `list_trends` / `get_trend` | Time-series analyses |
| `list_reports` / `get_report` | Multi-metric report definitions |
| `list_dashboards` / `get_dashboard` | Dashboard layouts |

## Campaigns & scenarios (introspection)
| Tool | Purpose |
|---|---|
| `list_email_campaigns` / `get_email_campaign` | Existing email campaigns — spam-overlap check |
| `list_sms_campaigns` / `get_sms_campaign` | SMS variants + action payloads |
| `list_scenarios` / `get_scenario` | Multi-step automation flows |
| `list_scenario_nodes` / `get_scenario_node` | Read a scenario's exact node graph — Gate-1 transparency |
| `list_banners` / `get_banner` | Web layer banners |
| `list_in_app_messages` / `get_in_app_message` | Mobile in-app messages |
| `list_experiments` / `get_experiment` | A/B test definitions |
| `list_recommendations` / `get_recommendation` | Recommendation engines |
| `list_surveys` / `get_survey` | Survey definitions |
| `get_campaign_calendar` | Scheduled sends within a date window |

## Catalog
| Tool | Purpose |
|---|---|
| `list_catalogs` / `get_catalog` | v2 catalogs available in the project |
| `list_catalog_items` / `get_catalog_item` | Product records (Elasticsearch-backed) |
| `get_catalog_configuration` | Field schema (attribute definitions, mappings) |
| `list_catalog_jobs` / `get_catalog_usages` | Ingest job history + cross-references |

> Sandbox 05-31: empty — verify before committing to UC-5.

## Project config
| Tool | Purpose |
|---|---|
| `list_project_variables` | Global Jinja substitutions (`project_variable.brand_name`) |
| `get_consent_settings` | GDPR consent categories per channel |
| `get_frequency_policies` | Rate-limit policies — agent reads these to obey project rules |
| `list_project_users` | Users with project access |
| `list_api_triggers` / `get_api_trigger` | External event triggers that fire scenarios |
| `get_mapping` | Standard e-commerce event vocabulary (purchase, add_to_cart, etc.) |

## Vouchers
| Tool | Purpose |
|---|---|
| `list_voucher_pools` / `get_voucher_pool` | Pools + counts (`total`, `available`) |
| `list_voucher_codes` | Individual codes with status (`available`/`assigned`/`redeemed`) |

> Sandbox 05-31: empty → UC-4 reasons around it ("flat % not a code").

## Initiatives, schema, feedback
| Tool | Purpose |
|---|---|
| `list_initiatives` / `get_initiative` / `get_initiative_items` | Group related campaigns + analyses |
| `get_event_schema` | All event type definitions + property schemas |
| `submit_llm_feedback` | Agent reports gaps where a tool was needed but missing |

---

# Appendix B — Conversations MCP

`https://uqa.api.exponea.dev/cocoaas/public/api/clarity-search/v1/mcp/...` — clarity-search (ClarityCommerce / product search), no auth, tenant ID in URL.

| Tool | Purpose |
|---|---|
| `search_products` | NL + structured-filter search on the "First" catalog (apparel domain) |
| `get_product` | Fetch by item/product ID with all variants |
| `search_productCollections` | Multi-intent parallel search (max 5) |
| `seeker_products` | Vague/discovery queries ("gift for my wife") |

> Not on the critical path for win-back. Possible UC-5 flourish if catalog is populated.

---

# Appendix C — Custom `bloomreach` MCP — final scope

4 tools wrapping Engagement REST. Reads stay in Loomi where possible.

| Tool | Endpoint | Status |
|---|---|---|
| `set_customer_property` | `POST track/v2/.../customers` | ✅ validated |
| `trigger_scenario` (event ingest) | `POST track/v2/.../customers/events` | ✅ validated |
| `read_customer_events` | `POST data/v2/.../customers/events` | ✅ validated |
| `read_customer_attributes` | `POST data/v2/.../customers/attributes` | ✅ validated |

`send_transactional_email` **dropped** — the scenario delivers the email. `read_campaign_performance` / `query_cohort_ids` **NOT built** — replaced by saved EQL the Planner runs + single seeded demo recipient. See `endpoints-to-mcp.md` for the wrapping spec.

---

# Appendix D — Deferred use cases

| UC | Idea | Tools available? | Verdict |
|---|---|---|---|
| UC2 | Cart abandonment | Yes — reuses 80% of UC1 infra | Stretch only, after primary loop lands |
| UC3 | Anomaly → A/B | Yes — `list_trends`, `list_experiments`, `execute_analytics_eql` | Demo arc weaker than win-back; deferred |
| UC4 (orig — onboarding) | Onboarding nudge | Yes — `list_customers` + `list_customer_events` by created date | Pacing kills 6-min video; deferred |
| UC6 | Catalog-aware re-engagement | Yes — catalog + Conversations MCP | Folded into **UC-5** above |
| UC7 | Cross-channel SMS | Introspection yes (`get_sms_campaign`); SMS *sends* gated | Cut — gated API risk |

---

# Appendix E — Verified constraints (carried into every scenario)

1. **Loomi rate limit: 1 req / 10s** (measured). Planner serializes with ~11s spacing + backoff. Budget discovery to ~5–8 EQL calls.
2. **PII masking** — `list_customers` returns `registered: ******`. Discover on aggregates; execute on seeded recipients.
3. **Empty discovery objects** — 0 predictions, 0 segmentations, 0 catalogs, 0 voucher pools on `crispy-ferret`.
4. **EQL recency idiom** — `count event purchase in last 30 days = 0` works; "more than N days ago" throws a parse error.
5. **Consent + Running scenario** required or send is silently suppressed.
6. **Async lag ~3–30s** everywhere; trigger node adds 30s.
