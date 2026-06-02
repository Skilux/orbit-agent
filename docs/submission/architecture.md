# Architecture

One clear diagram of how Orbit connects to **Loomi Connect MCP** (and the custom write-MCP), with both human-approval gates.

> **To export PNG/PDF for the submission portal:**
> - Paste the Mermaid block below into <https://mermaid.live> → Export PNG/SVG, **or**
> - `cd docs/submission && npx -y @mermaid-js/mermaid-cli -i architecture.md -o architecture.png`

```mermaid
flowchart TB
    H(["👤 Marketer"]):::human

    subgraph RUNTIME["Orbit runtime — one command: docker compose up"]
        UI["Hermes Web UI<br/>(:8787 — chat, tasks, kanban)"]:::ui
        AG["Hermes Agent Runtime<br/>profile: orbit · closed-loop planner<br/>8 skills · understand → decide → act"]:::agent
    end

    LOOMI[["🔵 Loomi Connect MCP<br/>REMOTE · read-only · OAuth 2.1 PKCE<br/>5 of 81 tools:<br/>execute_analytics_eql · get_event_schema<br/>get_customer_property_schema<br/>list_scenarios · get_consent_settings"]]:::loomi
    BR[["🟠 bloomreach-mcp (custom, in-repo)<br/>HTTP :8000 · write path · 4 tools:<br/>set_customer_property · read_customer_attributes<br/>trigger_scenario · read_customer_events"]]:::write
    ENG[("Bloomreach Engagement<br/>REST track/data v2")]:::eng
    MAIL["📧 Scenario → Mailgun → inbox"]:::mail

    H -->|"1 · plain-language goal"| UI
    UI <--> AG

    AG -->|"2 · DISCOVER (read-only)"| LOOMI
    LOOMI -->|"cohort + metrics<br/>(PII-masked aggregates)"| AG

    AG -->|"3 · campaign brief + authored copy"| UI
    UI -->|"✋ GATE 1 — human approves brief"| AG

    AG -->|"4 · SHIP (only after approval)"| BR
    BR -->|REST| ENG
    ENG --> MAIL
    BR -->|"5 · delivery status"| AG

    AG -->|"6 · authored scenario JSON (new campaign type)"| UI
    UI -->|"✋ GATE 2 — human pastes + activates in Bloomreach UI"| ENG

    AG -.->|"monitor results → propose next iteration (loop)"| UI

    classDef human fill:#fde68a,stroke:#b45309,color:#111
    classDef ui fill:#bfdbfe,stroke:#1e40af,color:#111
    classDef agent fill:#ddd6fe,stroke:#5b21b6,color:#111
    classDef loomi fill:#bbf7d0,stroke:#15803d,color:#111
    classDef write fill:#fecaca,stroke:#b91c1c,color:#111
    classDef eng fill:#e2e8f0,stroke:#475569,color:#111
    classDef mail fill:#fef9c3,stroke:#a16207,color:#111
```

## Legend

| Box | What it is |
|---|---|
| **Marketer** | The human. Gives a goal; approves at both gates. The agent recommends, the human executes. |
| **Hermes Web UI (:8787)** | Chat + scheduled tasks + kanban. The demo surface (the agent can also run on Slack/Teams/Telegram/email). |
| **Hermes Agent Runtime** | The closed-loop planner (Hermes "orbit" profile). Orchestrates both MCPs; carries the 8 Orbit skills. |
| **🔵 Loomi Connect MCP** | Remote, **read-only**, OAuth. The discovery/context surface — 5 focused tools of 81. *This is the central integration.* |
| **🟠 bloomreach-mcp** | Custom in-repo write-MCP (Python/FastMCP). The execution surface — wraps Engagement REST; only acts after Gate 1. |
| **Bloomreach Engagement** | The CRM/automation platform. Scenarios send the email; humans activate new scenarios (Gate 2). |
| **✋ Gate 1 / Gate 2** | The two mandatory human-approval points. Gate 1 = approve the brief before any write/send. Gate 2 = human pastes + activates a new scenario JSON. |

## Flow (numbered on the diagram)

1. Marketer gives a plain-language goal in the UI.
2. Agent **discovers** via Loomi Connect MCP (read-only EQL + schemas + consent) → gets a real cohort + metrics on PII-masked aggregates.
3. Agent authors a **campaign brief + email copy** and presents it.
4. **Gate 1** — human approves; only then the agent **ships** via the custom write-MCP (set properties → verify → trigger scenario).
5. Agent reads back **delivery status**.
6. For a new campaign type, the agent hands over importable **scenario JSON**; **Gate 2** — the human pastes + activates it in Bloomreach. Then the agent monitors results and proposes the next iteration — closing the loop.
