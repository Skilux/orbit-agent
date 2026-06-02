# Responsible AI Note

**Paste-ready (honest, a few sentences):**

> Orbit keeps a human in control of every campaign-facing action. The agent *recommends*; the human *executes*: it stops at **two mandatory approval gates** — first when it presents a campaign brief (nothing is written or sent until the marketer approves), and again when a new campaign type requires a human to paste and activate the agent-authored scenario in the Bloomreach UI. All work runs on **sandbox/synthetic data only** — no production data, and no PII leaves Bloomreach; discovery runs on **PII-masked aggregates**, so the agent never sees individual customers' emails while analyzing. We're transparent about what's modeled vs. real: the audience tiering is a **rule-based RFM heuristic, not an ML model**, the demo offer code is a static placeholder (no live voucher pool), and the demo sends to a single seeded recipient (the sandbox's email domain is unverified, so the message may land in spam). By design the agent has **read-only** access to Loomi Connect and can only act through a separate, human-gated write path — and no credentials are committed to the repo.

---

## Guardrails at a glance

| Concern | How Orbit handles it |
|---|---|
| **Human oversight** | Two mandatory gates. Gate 1: approve the brief before any write/send. Gate 2: human pastes + activates new scenario JSON in Bloomreach (no API auto-deploys campaigns). |
| **Least privilege** | Loomi Connect is read-only; only the custom write-MCP can act, and only after approval. Discovery cannot write; execution cannot read Loomi. |
| **Privacy** | Sandbox/synthetic data only; no PII leaves Bloomreach. Discovery uses PII-masked aggregates — no individual identities surfaced during analysis. |
| **Honesty about AI** | RFM tiering is a transparent heuristic, not ML (the sandbox has no models). Disclosed in-product. |
| **No overclaiming** | The agent never declares a send it didn't verify (it reads back the event status). Simulated parts (static offer code, single seeded recipient, spam placement) are disclosed. |
| **Secrets** | `.env` is gitignored; config uses `${VAR}` interpolation — no keys or tokens committed. |
