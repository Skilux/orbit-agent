# Demo Video Script — Orbit (≤ 5:00)

**Format:** MP4/MOV, max 5 min. **The presenter surface is the slide deck** `demo/concept-1-orbital.html` (8 slides), with **4 screen-recording clips** dropped into video slots on slides 4–7. You record the deck (voiceover + slide transitions) and the 4 clips separately, then edit together.

**The story (one line):** *thin tools + rich agent knowledge = leverage.* Orbit **reads** with Loomi Connect, **operates** existing infra through a deliberately thin write-MCP, and **creates** whole new campaigns from the agent's own skills.

**Two things to produce:**
1. **The deck** — drive `demo/concept-1-orbital.html` (arrow keys), voiceover per slide.
2. **The 4 clips** — screen-record the agent in the Hermes UI using the 3 prompts (Part 2), then trim into `assets/clip-discover.mp4`, `clip-gate1.mp4`, `clip-operate.mp4`, `clip-create.mp4`.

---

## Slide-by-slide plan (deck = `demo/concept-1-orbital.html`, 8 slides)

> VO lines in full are in the **"Text to say"** section at the bottom (mapped slide-by-slide). Clips are captured per **Part 2**.

| # | Slide (on screen) | Video slot | Voiceover (who) | Clip: what it must capture |
|---|---|---|---|---|
| 1 | **Title** — Orbit, tagline, Track 6, Team Rohlik | — | S1 intro | — |
| 2 | **The challenge** — manual discovery, fragmented loop + **Orbit's thesis** | — | S1 problem · S2 thesis | — |
| 3 | **System architecture** — 2 MCP surfaces, 2 trust levels, both gates | — | S2 architecture | — (the slide's native diagram animates) |
| 4 | **Step 1 · READ — Discover** — Loomi 5 tools, cohort 15,274 | `clip-discover.mp4` | S1 discover | From **P1**: Loomi tool-call cards stacking in the chat (event schema → EQL → consent → scenarios). ~15–25s, trimmed. |
| 5 | **Gate 1 — agent stops & asks** + Responsible-AI note | `clip-gate1.mp4` | S2 brief · S1 RAI | Same **P1** turn, the *brief* part: scroll the Campaign Brief to `>>> AWAITING HUMAN APPROVAL`. ~10–15s. |
| 6 | **Step 2 · ACT — Operate** — 4-tool sequence | `clip-operate.mp4` | S1 operate | From **P2**: the 4 write-MCP cards firing → `enqueued → opened`. ~15–20s. |
| 7 | **Step 3 · CREATE — Author** — what it builds + **Gate 2** | `clip-create.mp4` | S2 create · S1 Gate 2 | From **P3**: authored scenario JSON (the branch) → rendered HTML → terminal `validate_scenario.py` → `PASS ✅`. ~20–30s. |
| 8 | **The three verbs** — recap, stat counters, RAI line | — | S2 recap · S1 sign-off | — (let the counters animate to 88% / 15,274 / $774K / gates) |

**Capture note:** clips 4 & 5 come from the **same P1 turn** (discovery → brief). Record the whole P1 turn once, then cut it into two clips — the Loomi-cards portion → `clip-discover`, the brief portion → `clip-gate1`.

---

## Part 1 — Prerequisites (do these BEFORE you hit record)

### A. Stack is healthy
- [ ] `docker compose up --build` running; <http://localhost:8787> loads.
- [ ] Gateway pill is **green** in the WebUI.
- [ ] `bloomreach-mcp` reachable (port 8000) and its 4 tools show in the agent's tool list.

### B. Loomi Connect token is fresh
- [ ] Re-mint the Loomi OAuth token **< 1 hour** before recording (it's the read path; if it's expired the discovery beat dies). One-time browser login.

### C. Recipient is seeded (for the real send, Prompt 2)
- [ ] `orbit-seed-1@email.com` exists in the sandbox **with email consent** and is **not suppressed**. (Already done + verified `delivered`/`opened` in rehearsal — just re-confirm it didn't get suppressed since.)

### D. Stage the workspace so authoring is *honest* (Prompt 3)  ⚠️ important
The agent must build cart-recovery **from the win-back example**, not copy a prebuilt cart-recovery file. Before recording, move the pre-existing cart-recovery / other generated artifacts out of the agent's reach:

```bash
# from repo root — temporarily stash everything EXCEPT the winback example.
# Stash MIRRORS the dir structure (top-level + generated/ have same-named copies),
# so restore is unambiguous.
mkdir -p .demo-stash/scenarios .demo-stash/generated .demo-stash/templates
mv agent/scenarios/generated/orbit_cartrecovery.json   .demo-stash/generated/  2>/dev/null
mv agent/scenarios/generated/orbit_vip_reengage.json   .demo-stash/generated/  2>/dev/null
mv agent/scenarios/orbit_cartrecovery.json             .demo-stash/scenarios/  2>/dev/null
mv agent/scenarios/orbit_vip_reengage.json             .demo-stash/scenarios/  2>/dev/null
mv agent/scenarios/orbit_newbrands.json                .demo-stash/scenarios/  2>/dev/null
mv agent/templates/cartrecovery-email.html             .demo-stash/templates/  2>/dev/null
mv agent/templates/newbrands-email.html                .demo-stash/templates/  2>/dev/null
```

After recording, restore (see bottom of file) — they're part of the repo deliverable, don't lose them.

**What MUST remain in the workspace** (these are the example the agent learns from):
- [ ] `agent/scenarios/examples/orbit_winback.json` — the scenario reference (one of every node type).
- [ ] `agent/templates/winback-shell.html` — the HTML shell example.
- [ ] `agent/skills/author-scenario.md`, `author-offer-rfm.md`, `eql-cheatsheet.md` — the rules.
- [ ] `agent/scenarios/validate_scenario.py` — the honesty check you'll run on camera (or right after).

If the container is already running, the stash takes effect immediately (workspace is bind-mounted `./agent:/workspace/agent`). No rebuild needed.

### E. Dry-run the whole thing once, un-recorded
Run Prompts 1→2→3 start to finish once. Confirm: Loomi cards appear, the send returns `delivered`/`opened`, and the authored cart-recovery JSON **passes** `validate_scenario.py`. Only then record.

---

## Part 2 — Capturing the agent (the 4 clips for slides 4–7)

> **Slides 1, 2, 3, 8 are deck-only** — voiceover over the slide, no screen recording.
> **Slides 4–7 each hold a clip** you capture by screen-recording the Hermes UI with the 3 prompts below.
> The **Say** lines here are presenter notes / what the clip should convey; the final polished narration lives in **"Text to say"** (mapped slide-by-slide). Move the cursor slowly; zoom tool-call cards so they're readable.

### Beat 1 · Slide 1 — Meet Orbit  *(deck-only — voiceover, no clip)*
- **Show:** the title slide.
- **Say:** see VO Slide 1 in "Text to say."

### Beat 2 · Slide 3 — Architecture  *(deck-only — the slide's native diagram animates; no clip)*
- **Show:** the architecture slide (or `architecture.png`).
- **Say:**
  > "Quick look under the hood — because *how* it's built is the point.
  >
  > **What we connected.** Orbit talks to Bloomreach through two MCP surfaces. On the read side, the **Loomi Connect MCP** — remote, OAuth, read-only — and we use five of its eighty-plus tools for discovery: event schema, EQL analytics, consent, scenarios. On the write side, **we built our own Engagement MCP** — a small Python FastMCP server wrapping the Bloomreach Engagement REST API, just four endpoints: set a customer property, read attributes, read events, and trigger a scenario.
  >
  > **Why we split read and write.** Discovery should be free and safe, so the read path is strictly read-only. Anything that touches a customer goes through *our* MCP, where we control it — and behind a human approval gate. Two surfaces, two trust levels, by design.
  >
  > **Why the write-MCP is deliberately thin.** We could have stuffed logic into the tools — we did the opposite. The four endpoints stay dumb; all the intelligence lives in **Orbit's skills** — its knowledge of the Bloomreach scenario schema, the connector graph, EQL, and email templating. That keeps the tools portable and model-agnostic, and it's *why* Orbit can author a whole campaign instead of just calling an API.
  >
  > **Why Hermes.** It all runs on the **Hermes agent harness** with a web UI — so this same teammate can run on Slack, Teams, Telegram or email, on a schedule or on demand. Plug-and-play for any team, and the whole thing comes up with one `docker compose up`."
- **If too long to land smoothly:** keep the four **bold headers** as one sentence each and drop the parentheticals.

### Beat 3 · Slide 4 — DISCOVER  → records **`clip-discover.mp4`**
- **Show:** the Hermes chat; let the Loomi tool-call cards stack up; zoom each as it lands. *(This is the Loomi-cards portion of the P1 turn.)*
- **Type — Prompt 1** (pinned cohort + asks for the brief in one go, so it lands deterministically):
  > I run marketing for our store. We keep acquiring customers but revenue is flat and I don't know why. Dig into our data and find the root cause. When you measure the lapsed segment, define it once as: customers who purchased exactly once ever AND have not purchased in the last 60 days — use that exact definition consistently everywhere. Give me the root cause, the size and dollar value of the opportunity, and then go straight to a full campaign brief — RFM tier, offer, and the authored email copy — ready for my approval. Do not send anything.
- **Say:**
  > "I'll just talk to it like a colleague. Now watch how many ways Orbit interrogates **Loomi Connect** to diagnose this: it reads the **event schema** to learn our data model, runs **EQL** across the purchase funnel, checks **consent**, and lists our existing **scenarios**. This is real diagnosis — not one canned query."
- **Expect (verified 2026-06-02 — ~2–3 min on Loomi's rate limit):** ~20 serialized Loomi calls (`get_event_schema`, `execute_analytics_eql` …). Diagnosis: **88% one-and-done**, **15,274 lapsed one-time buyers** (DE 2,457 · UK 5,819 · USA 6,998), **AOV ~$1,013**, ~$774K at a 5% win-back — then it flows **straight into the brief in the SAME turn** (next beat).
- **If it stalls:** narrate the reasoning in the partial output; Loomi rate-limiting means cards arrive deliberately — latency reads as "working." Trim the long waits in post.

### Beat 4 · Slide 5 — Brief + Gate 1  → records **`clip-gate1.mp4`** (same P1 turn — no new prompt)
- **Show:** the structured **Campaign Brief** that follows the diagnosis in the *same* response; highlight the **cohort size (15,274)**, the **RFM decision (`WB20`, 20%)**, the **authored email copy**, the **disclosures**, and **`>>> AWAITING HUMAN APPROVAL`** at the bottom.
- **Say:**
  > "And it doesn't just diagnose — it writes the actual plan. Same 15,274 lapsed buyers, an RFM tier — honestly a transparent heuristic, not a black-box model — a real offer, and the email copy, written for *this* cohort. Then it **stops. This is Gate one** — Orbit recommends, but nothing touches a customer until I approve and hand it a recipient."
- **Expect:** full brief in the SOUL format — `WB20` / 20% tier with margin reasoning, headline + body HTML, honest disclosures (PII-masked, heuristic-not-ML, static offer code), then `AWAITING HUMAN APPROVAL` and a stop. Gate holds. *(P1 produces the brief in the same turn as the diagnosis — no separate "yes, build it" prompt needed.)*

### Beat 5 · Slide 6 — OPERATE (thin write-MCP, real send)  → records **`clip-operate.mp4`**
- **Show:** zoom the **4 write-MCP cards** in sequence; show the `read_customer_events` result.
- **Type — Prompt 2 (approve + send):**
  > Approved — run the win-back. Ship it to orbit-seed-1@email.com.
- **Say:**
  > "Approved. Now — and only now — Orbit touches the write side through that thin Engagement MCP: it sets the personalization, **verifies** it landed, fires the win-back scenario, and reads the result straight back — **delivered, and opened.** A real campaign, from a plain-language goal, with a human in the middle."
- **Expect (verified 2026-06-02):** `set_customer_property` → `read_customer_attributes` (verify) → `trigger_scenario` (`orbit_winback_triggered`) → `read_customer_events` → campaign event **`enqueued` then `opened`**. No `suppressed`/error. *(Timing wrinkle: the new send's delivery event may not surface in the ~90s read window, so the agent reports the most-recent visible `enqueued/opened` pair — its timestamp can lag the moment you hit send. Harmless; the proof is the clean status.)*
- **Show status, not spam:** prove the send via the clean event status (`enqueued → opened`), not the inbox — simpler to film and avoids the unverified-sender-domain look. (Note: during the smoke run the agent *speculated* the subject renders raw, but it can't see email content — only event status — and the subject uses the same Jinja + properties as the body, with `default()` fallbacks, so it resolves to "Danila, we saved 20% off…". Eyeball it once on your dry-run to be sure; nothing to fix in advance.)

### Beat 6 · Slide 7 — CREATE (author a new campaign from an example) ★ the payoff  → records **`clip-create.mp4`**
- **Show:** as the agent works — (1) the **authored scenario JSON**, point at the branch (trigger → send → wait → condition → follow-up); (2) **open the rendered HTML** the agent produced in a browser tab; (3) **run the validator** in a terminal.
- **Type — Prompt 3 (hero):**
  > We've got nothing for abandoned carts — that whole revenue stream is leaking. Look at our existing win-back scenario as a reference for the format, then build me a complete cart-recovery campaign from scratch: work out the audience, design the email, and author the full multi-step scenario — send, wait two days, follow up if they haven't opened — plus a preview-ready HTML I can open. I want to import it straight into Bloomreach.
- **Say:**
  > "Now the part I love. We have **no** cart-recovery campaign at all — that whole revenue stream is leaking. So Orbit studies our existing win-back scenario as a template, and from one sentence it **authors a brand-new campaign from scratch** — the audience logic, a full multi-step flow: send, wait two days, branch on whether they opened, follow up — *and* it designs the email itself. Remember that thin little MCP? **This** is where the power actually lives — in Orbit's *skills*. It knows the Bloomreach scenario schema, the connector graph, the email templates."
- **The honesty proof (do on camera if you can):**
  ```bash
  python agent/scenarios/validate_scenario.py <the-file-the-agent-wrote>.json
  ```
  > "And it imports clean — we validate every scenario Orbit writes. I paste it into Bloomreach and activate — that's **Gate two.**"
- **Expect:** agent reads `examples/orbit_winback.json` + the `author-scenario` skill, then emits a **new** scenario JSON in BR clipboard shape (correct connector indices, constant `channel_extension_id`, `consent_category: "other"`) + an email HTML based on `winback-shell.html` with fresh cart-recovery copy. Validator prints `PASS ✅ ... Total errors: 0`.
- **If the live build is slow/imperfect:** keep narrating; if the JSON has a flaw, *show the validator catching it* — the guardrail working is still a win. Do **not** swap in a prebuilt file on camera; the whole point is that it authored this one.

### Beat 7 · Slide 8 — Close  *(deck-only — let the stat counters animate; no clip)*
- **Show:** the recap slide (three verbs + counters: 88% / 15,274 / $774K / gates).
- **Say:** see VO Slide 8 in "Text to say."

---

## Prompts (copy-paste) — 3 prompts, one continuous chat
1. **(diagnose → brief)** *I run marketing for our store. We keep acquiring customers but revenue is flat and I don't know why. Dig into our data and find the root cause. When you measure the lapsed segment, define it once as: customers who purchased exactly once ever AND have not purchased in the last 60 days — use that exact definition consistently everywhere. Give me the root cause, the size and dollar value of the opportunity, and then go straight to a full campaign brief — RFM tier, offer, and the authored email copy — ready for my approval. Do not send anything.*
2. **(approve + send)** *Approved — run the win-back. Ship it to orbit-seed-1@email.com.*
3. **(hero — author from scratch)** *We've got nothing for abandoned carts — that whole revenue stream is leaking. Look at our existing win-back scenario as a reference for the format, then build me a complete cart-recovery campaign from scratch: work out the audience, design the email, and author the full multi-step scenario — send, wait two days, follow up if they haven't opened — plus a preview-ready HTML I can open. I want to import it straight into Bloomreach.*
4. *(only if time)* *How is the win-back performing? If it's underperforming, propose the next iteration.*

## Recording tips
- **Architecture (Slide 3) earns the credibility** — it's what tells judges this is real engineering, not a wrapper. Land the four "why" points in VO.
- **Loomi is the judged criterion** — in `clip-discover`, let the tool-call cards (event schema, EQL, consent, scenarios) be readable; the VO names them.
- **Authoring is the emotional peak** — give `clip-create` (Slide 7) room; the thin-MCP→rich-skills contrast is what makes it memorable.
- **Latency is your friend** in `clip-discover` (Loomi rate-limits ~1/10s): the stacking cards read as "working." Trim the long waits when you cut the clip.
- **Show status, not spam** in `clip-operate`: capture the `enqueued → opened` event status, not the inbox.
- **Don't fake `clip-create`.** No prebuilt swap on camera. The validator catching a flaw is an acceptable, honest outcome; copying a file is not.
- Record each clip at **1920×1080**; slow cursor; zoom tool-call cards. Capture P1 once and split it into `clip-discover` + `clip-gate1`.
- Drop the finished clips into `demo/assets/` as `clip-discover.mp4`, `clip-gate1.mp4`, `clip-operate.mp4`, `clip-create.mp4` (the deck's video slots already point there).

## Honesty line (say once — scores on Responsible-AI)
"Everything's on sandbox data — no real customers. Discovery runs on PII-masked aggregates, the RFM tier is a transparent heuristic not an ML model, the offer code is a demo placeholder, and the agent only acts after I approve."

## After recording — restore the workspace
```bash
# restore mirrors the stash structure
mv .demo-stash/generated/*  agent/scenarios/generated/ 2>/dev/null
mv .demo-stash/scenarios/*  agent/scenarios/           2>/dev/null
mv .demo-stash/templates/*  agent/templates/           2>/dev/null
# verify nothing is left behind before removing the stash
find .demo-stash -type f && rm -rf .demo-stash
```

---

## Text to say (voiceover script — for TTS)

> **Scene:** The Sound Stage Booth.
>
> **Sample Context:** Hackathon demo voice-over. Dynamic pacing — starts intrigued, ends punchy. Tone is polished, persuasive, and inviting. Two voices trading off: Speaker 1 is the narrator/marketer, Speaker 2 is the builder explaining the "how."
>
> *(Lines map in order to the 8 deck slides — Slide 1 → Slide 8 (a few slides get two lines). Speaker 1 = narrator/marketer, Speaker 2 = builder. Format is exactly `Speaker N: text` so a TTS model parses the speakers. Slide guide: 1 title · 2 challenge+thesis · 3 architecture · 4 discover · 5 gate 1 · 6 operate · 7 create · 8 close.)*

Speaker 1: Hey — Rohlik team here to show you something. Meet Orbit, your marketing team's next AI teammate. Orbit is an AI agent built on the Hermes agent and plugged straight into Bloomreach stack — through the Loomi Connect MCP for reading, and a custom Engagement MCP for acting. The idea is plug-and-play: a powerful harness tuned specifically to work hand-in-hand with Bloomreach. Let me show you what it does — and how it's built.

Speaker 1: But here's the problem every lean marketing team lies with. The data is rich — but finding a real revenue opportunity means hours of analysis, checks, and scenario auditing, before a single brief is even written. And the loop — discover, build, send, measure, iterate — is fragmented: every step lives in a different tool, owned by a different person, and insights expire at every handoff. Orbit's thesis is simple: thin tools plus rich agent knowledge equals leverage. The agent is the intelligence — powered by MCP tools and skills.

Speaker 2: Quick look under the hood — because how it's built is the point. What we connected: Orbit talks to Bloomreach through two MCP surfaces. On the read side, the Loomi Connect MCP — remote, read-only — and we use it for discovery and analytics. On the write side, we built our own Engagement MCP — a small Python FastMCP server wrapping the Bloomreach Engagement REST API, just four endpoints. And here's the key: we didn't just wire it up to the tools — we gave it what an agent actually needs: context. MCP tools are the instruments; the intelligence lives in Orbit's skills — its knowledge of the Bloomreach scenario schema, the connector graph, EQL, and email templating. That keeps the tools portable and model-agnostic, and it's why Orbit can author a whole campaign instead of just calling an API. And why Hermes? It all runs on the Hermes agent harness with a web UI — so this same teammate can run on Slack, Teams, or Telegram, on a schedule or on demand. Preconfigured tools, skills, the full advantage of a self-improving AI agent. Plug-and-play for any team and platform — and the whole thing comes up with one command.

Speaker 1: So I'll just talk to it like a colleague. Now watch how many ways Orbit interrogates Loomi Connect to diagnose this: it reads the event schema to learn our data model, runs EQL across the purchase funnel, checks consent, and lists our existing scenarios. This is real diagnosis — not one canned query.

Speaker 2: And it doesn't just diagnose — it writes the actual plan. Here's the verdict: eighty-eight percent of customers buy once and never come back. Orbit sizes it — about fifteen thousand lapsed high-value buyers, a thousand-dollar average order — picks an offer tier off a transparent heuristic, not a black-box model, and writes the email copy for this exact cohort. Then it stops. This is Gate one — Orbit recommends, but nothing touches a customer until a human approves.

Speaker 1: Approved. And now — only now — Orbit touches the write side, through that thin Engagement MCP. It sets the personalization, verifies it landed, fires the win-back, and reads the result straight back: delivered, and opened. A real campaign, from a plain-language goal, with a human in the middle.

Speaker 2: Now the part we love. We have no cart-recovery campaign at all — that whole revenue stream is leaking. So Orbit studies our existing win-back as a reference, and from a single sentence it authors a brand-new campaign from scratch: the audience, a full multi-step flow — send, wait two days, branch on whether they opened, follow up — and it designs the email itself. Remember that deliberately thin MCP? This is where the power actually lives — in Orbit's skills.

Speaker 1: And it imports clean — we validate every scenario Orbit writes. Paste it into Bloomreach, activate — that's Gate two.

Speaker 2: So that's Orbit: it reads with Loomi Connect, operates through a thin custom MCP, and creates entire campaigns from its own skills — with a human at every customer-facing step. It even monitors results and proposes the next iteration, closing the loop.

Speaker 1: Sandbox data only, fully transparent about what's simulated. Your marketing team's next teammate. That's Orbit.
