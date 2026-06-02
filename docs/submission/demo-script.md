# Demo Video Script (≤ 5:00)

**Format:** MP4 or MOV, max 5 minutes. **Working demo beats slides.**
**Golden rule:** *record this last — after everything works.* Re-confirm the Loomi token and `docker compose up` are healthy < 1h before recording.

**Arc:** problem → solution → live demo (the loop) → close.

| # | Time | On screen | Say (narration) |
|---|---|---|---|
| 1 | 0:00–0:30 | Title slide / your face | "Lean marketing teams have opportunities sitting in their data they never work — because finding them, building a campaign, sending, and measuring spans too many tools. Orbit is a closed-loop campaign agent that does that loop with you, not for you." |
| 2 | 0:30–1:10 | Architecture diagram (`architecture.png`) | "Orbit orchestrates two Bloomreach MCP surfaces. Loomi Connect MCP — read-only — is how it discovers opportunities. A custom write-MCP executes. And there are two hard human-approval gates: the agent recommends, the human executes." |
| 3 | 1:10–2:20 | Hermes UI (:8787). Type the goal. Show EQL tool calls running. | "I give it a plain goal — 'find me a revenue opportunity.' Watch it call Loomi Connect's `execute_analytics_eql` against live data… it finds ~15,900 lapsed one-time buyers across three markets, 12% repeat rate, ~$1,000 average order. Real query, real numbers." |
| 4 | 2:20–3:10 | The campaign brief it outputs; highlight the authored email copy + the "AWAITING APPROVAL" line | "It computes an RFM tier — honestly, a heuristic, not ML — picks a 20% offer for these high-value customers, and **writes the actual email copy**. Then it stops. **Gate 1** — nothing is sent until I approve." |
| 5 | 3:10–4:10 | Approve in chat → show `set_customer_property` → `read_customer_attributes` (verify) → `trigger_scenario` → `read_customer_events` (status: sent). Optionally show the email. | "I approve. Now the write-MCP takes over: it sets the personalization properties, verifies they landed, fires the scenario, and reads back the delivery status. And for a brand-new campaign type, it hands me importable scenario JSON to paste into Bloomreach — that paste is **Gate 2**." |
| 6 | 4:10–4:40 | The iteration proposal (monitor → next move) | "It monitors results and proposes the next iteration — sharper subject for non-openers, a bigger offer for high-value silent customers — and stops again for approval. That's the closed loop." |
| 7 | 4:40–5:00 | Diagram / one-line recap | "Two MCPs, one loop, a human at every campaign-facing action. Sandbox data only, full transparency on what's simulated. That's Orbit." |

## Tips
- **Pre-stage the data**: seed the demo recipient (with consent) *before* recording so the send isn't suppressed.
- Disclose on camera: RFM is a heuristic; the offer code is a demo placeholder; the email may land in spam (unverified sandbox Mailgun domain). Honesty scores on the Responsible-AI criterion.
- If a live Loomi query is slow (rate-limited ~1 req/10s), narrate over it — don't cut to a blank screen.
- Keep cursor movements slow and deliberate; zoom the terminal/tool-call cards so they're readable.
