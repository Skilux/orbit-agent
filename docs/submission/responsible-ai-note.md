# Responsible AI Note

Orbit keeps a human in control of every campaign-facing action. The agent *recommends*; the human *executes*: it stops at **two mandatory approval gates** — first when it presents a campaign brief (nothing is written or sent until the marketer approves), and again when a new campaign type requires a human to paste and activate the agent-authored scenario in the Bloomreach UI. All work runs on **sandbox/synthetic data only** — no production data, and no PII leaves Bloomreach; discovery runs on **PII-masked aggregates**, so the agent never sees individual customers' emails while analyzing. We are transparent about what is modeled vs. real: audience tiering is a **rule-based RFM heuristic, not an ML model**, so its segmentation logic is fully inspectable and free of opaque model bias, and the offer code is a static placeholder rather than a live voucher pool. By design the agent has **read-only** access to Loomi Connect and can act only through a separate, human-gated write path — limiting misuse — and no credentials are committed to the repo.

## Guardrails at a glance

| Concern | How Orbit handles it |
|---|---|
| **Human oversight** | Two mandatory gates. Gate 1: approve the brief before any write/send. Gate 2: human pastes + activates new scenario JSON in Bloomreach (no API auto-deploys campaigns). |
| **Least privilege** | Loomi Connect is read-only; only the custom write-MCP can act, and only after approval. Discovery cannot write; execution cannot read Loomi. |
| **Privacy** | Sandbox/synthetic data only; no PII leaves Bloomreach. Discovery uses PII-masked aggregates — no individual identities surfaced during analysis. |
| **Bias** | Tiering is a simple, inspectable RFM rule rather than a trained model — segmentation logic is auditable, with no opaque model bias. |
| **Transparency** | RFM tiering is a disclosed heuristic, not ML; the static offer code and any simulated steps are stated plainly. The agent never declares a send it didn't verify — it reads back the event status. |
| **Misuse** | The agent cannot act on its own: a read-only discovery path is separated from a human-gated write path, so no campaign reaches a customer without explicit human approval. |
| **Secrets** | `.env` is gitignored; config uses `${VAR}` interpolation — no keys or tokens committed. |
