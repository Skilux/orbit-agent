# MCP Usage Explanation

**Summary (paste-ready):**

> Orbit orchestrates **two MCP surfaces** in one closed loop. It uses **Loomi Connect MCP** (remote, read-only, OAuth) for all discovery and context — a deliberately focused **5 of 81 tools** so the agent reasons with a sharp toolset — and a **custom in-repo write-MCP** (4 tools, Python/FastMCP) for execution, because Loomi is read-only and Bloomreach has no first-class agent write-layer. Loomi *understands* the data; the custom MCP *acts* on it — with a mandatory human approval in between.

---

## Loomi Connect MCP — context & discovery (read-only, OAuth 2.1 PKCE)

The agent enables **5 of the 81 available tools** — depth over breadth. Each, and exactly how it's used in the loop:

| Tool | How Orbit uses it |
|---|---|
| **`execute_analytics_eql`** | The workhorse. Runs serialized EQL aggregate queries against the live sandbox (~123k customers / 1.17M events) to **discover a revenue opportunity**. Live result from a real run: **~15,905 lapsed one-time buyers** (Germany 2,557 · UK 6,062 · USA 7,286), **~12% repeat-purchase rate**, **~$1,010 AOV**, category mix dominated by women's apparel. Loomi enforces ~1 request / 10s, so the agent **serializes ~5–8 queries** and never loops per-customer. |
| **`get_event_schema`** | Discovers which event types exist and their properties, so the agent writes valid EQL and knows what's trackable. |
| **`get_customer_property_schema`** | Discovers the customer attributes available for targeting and personalization. |
| **`list_scenarios`** | Lists existing automation scenarios (name/status), so the agent knows whether to **reuse** one (e.g. `orbit_winback`) or **author a new** scenario. |
| **`get_consent_settings`** | Reads the project's GDPR/consent configuration so the agent respects consent **before any send** — a send without consent is silently *suppressed*, not failed. |

This is the judged surface: real EQL discovery against live data drives every downstream decision.

## Custom `bloomreach-mcp` — execution (the write path)

Loomi is read-only, and Bloomreach Engagement has no agent-callable write surface — so Orbit ships a **custom Python/FastMCP server** (`mcp/bloomreach-engagement-mcp/`) that wraps exactly the Engagement REST endpoints (track/data v2) the loop needs:

| Tool | How Orbit uses it |
|---|---|
| **`set_customer_property`** | Writes personalization properties (`email_headline`, `email_body`, `offer_code`, `discount_tier`, `first_name`, `email`) to a customer profile. |
| **`read_customer_attributes`** | Verifies the write landed before triggering — never fire on a half-written profile. |
| **`trigger_scenario`** | Fires a tracked event (e.g. `orbit_winback_triggered`) that activates a pre-built Bloomreach scenario → sends the email. |
| **`read_customer_events`** | Reads the resulting campaign event to confirm delivery status (`sent` / `delivered` / `suppressed`). |

## Cross-MCP orchestration (Track 6)

The two surfaces form one loop: **Loomi (read/understand) → human approval → custom MCP (write/act) → Loomi/custom MCP (monitor)**. The agent discovers via Loomi, decides an offer, authors copy and a scenario, **stops for human approval (Gate 1)**, then executes via the custom MCP, and for new campaign types hands the human an importable scenario JSON to paste and activate (**Gate 2**). Understanding and acting are deliberately separated across two MCPs with a human in between — that separation *is* the safety model.
