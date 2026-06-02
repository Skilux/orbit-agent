# Orbit — Usage

How to drive the closed loop once Orbit is running. For install/config, see
**[SETUP.md](SETUP.md)**.

## The closed loop

Orbit runs a **goal → context → plan → execute → monitor → iterate** loop with a
**human-approval gate** before any campaign-facing action. The agent *recommends*;
you *execute*.

1. **Connect Loomi (one-time).** Authorize the `loomi` MCP via the browser OAuth
   flow in the Hermes UI (see [SETUP § Connecting Loomi](SETUP.md#connecting-loomi-read-only)).
   The token caches locally and is never committed. Re-auth if it expires (~1 h).
2. **Open the UI** at <http://localhost:8787> and start a chat.
3. **Goal input (you).** Give a plain-language goal, e.g.
   > *"Find a revenue opportunity in lapsed one-time buyers and propose a win-back campaign."*
4. **Discovery (agent, read-only).** The agent runs EQL / schema / consent reads
   against Loomi. It self-throttles to ~1 call / 10 s, so latency is expected and
   normal — cards trickle in.
5. **🚦 Gate 1 — approve the brief.** The agent presents a campaign brief +
   authored email copy. **Nothing is written or sent until you approve.**
6. **Execution (agent, write-MCP).** On approval it sets customer properties,
   verifies the write (read-back), fires `trigger_scenario` to send, then reads
   delivery status.
7. **🚦 Gate 2 — paste & activate (new campaign types only).** For a brand-new
   campaign the agent hands you an importable **scenario JSON**. You paste/import
   it into the Bloomreach Engagement UI and activate it — **that paste is the
   second approval gate**. Examples and generated scenarios live in
   [`../agent/scenarios/`](../agent/scenarios/).
8. **Monitor & iterate.** The agent reads campaign events and proposes the next
   iteration, closing the loop.

## Simulated vs. live

Per the hackathon rules — **sandbox / synthetic data only; no production PII**.

- **Live:** EQL discovery against the real sandbox · the write-MCP writing to
  Engagement · the actual email send via a pre-built scenario.
- **Simulated / disclosed:** audience tiering is a rule-based **RFM heuristic**
  (no ML); the demo offer code is a **static placeholder** (no live voucher pool);
  sends go to a **single seeded recipient**; the sandbox Mailgun sender domain is
  unverified, so mail may land in **spam**.

See [`reference/scenarios.md`](reference/scenarios.md) and
[`submission/responsible-ai-note.md`](submission/responsible-ai-note.md) for the
full disclosure.

## FAQ / Troubleshooting

**Discovery does nothing / Loomi errors out.**
Your Loomi OAuth token is missing or expired (~1 h lifetime). Re-authorize. Tokens
cache in `hermes/.hermes/profiles/orbit/mcp-tokens/` (gitignored), so a fresh clone
always needs a first login.

**Discovery is slow / results trickle in.**
Expected. Loomi enforces ~1 request / 10 s; the agent serializes reads. Latency =
working, not stuck.

**The email landed in spam (or didn't arrive).**
The sandbox Mailgun sender domain is unverified — spam placement is expected and
disclosed. Confirm the send via **event status** (`enqueued → delivered → opened`)
with `read_customer_events`, not by checking the inbox.

**`trigger_scenario` returned 200 but nothing sent.**
The event only activates a scenario that **already exists** in the Bloomreach UI
with a matching event-trigger node — build/import it first (Gate 2). Also, writes
are async: 200 means *queued*; wait 1–2 s and read back to confirm.

**A property I set reads back empty.**
Writes are async — add a 1–2 s delay before `read_customer_attributes`. Note the
email template renders a missing variable as blank (not an error), so set every
variable it references.

**The LLM endpoint is unreachable.**
Check `OPENAI_BASE_URL` is reachable from where Hermes runs (inside the container
in Docker mode) and that `OPENAI_API_KEY` is valid — or reconfigure with
`hermes model`.

**The agent can't reach bloomreach-mcp.**
`BLOOMREACH_MCP_URL` differs by mode: local `http://localhost:8000/mcp`, Docker
`http://bloomreach-mcp:8000/mcp` (compose sets this automatically — don't override
it in `.env` for Docker). Confirm the MCP is up: `curl http://localhost:8000/health`.

**Docker: WebUI says the gateway isn't running / permission errors.**
On macOS set real `UID`/`GID` in `.env` (`id -u` / `id -g`). The runtime home lives
on a named volume by design (macOS bind-mounts don't enforce file locking).

**Where do I get Bloomreach credentials?**
Engagement → *Project settings* (token); *Access Management → API* (key + secret).
You need an existing (invite/CSM-gated) sandbox. Sandbox/synthetic data only.

**Where do scenario JSONs come from / go?**
The agent authors them; examples and generated ones live in
[`../agent/scenarios/`](../agent/scenarios/). You import/paste them into the
Bloomreach Engagement UI to activate (Gate 2).
