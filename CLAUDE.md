# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this directory is

This is the **Orbit** repo — a hackathon project for the **Loomi Connect AI
Hackathon** (Bloomreach). It is now a code repo: an agentic application that
orchestrates Bloomreach **MCP surfaces** (Loomi read-only + a custom write-MCP)
into a closed-loop campaign workflow, with a human-approval gate before any
campaign-facing action.

## Layout

- `docs/submission/` — hackathon deliverables (project summary, architecture, MCP usage, responsible-AI note, demo script). `docs/reference/` — supporting docs: **`docs/reference/scenarios.md`** (use cases, demo modes, full Loomi tool inventory), Bloomreach API, endpoint→MCP mapping.
- `personal/` — **untracked, local only.** Internal planning + progress notes (the master-spec PRD, build-steps log, win-back runbook, hackathon context, Slack notes) and raw demo footage. Not part of the shipped repo.
- `demo/` — interactive demo one-pager (`concept-1-orbital.html`) + screen-capture clips + voiceover audio.
- `agent/` — the agent's playbook: `prompts/`, `skills/`, `scenarios/`, `templates/`.
- `mcp/bloomreach-engagement-mcp/` — custom Bloomreach Engagement MCP server (Python/FastMCP), the write path. `mcp/openapi-specs/` holds the BR OpenAPI reference.
- `hermes/ui/` — vendored Hermes web UI + agent runtime (MIT). `hermes/.hermes/` — Orbit's Hermes config (profile, SOUL, Orbit skills, MCP registrations).
- `docker-compose.yml` — one-command bring-up. `NOTICE` — third-party attribution.

## Build / run

```bash
cp .env.example .env        # fill credentials; set OPENAI_API_KEY/OPENAI_BASE_URL to a reachable endpoint
docker compose up --build   # bloomreach-mcp (:8000) + hermes-webui (:8787)
```

The MCP server is Python/FastMCP (`mcp/bloomreach-engagement-mcp/`); run its
tests/dev per that subdir's README. No repo-wide test suite yet.

> The legacy live working dir `orbit/` is gitignored (it held a running gateway,
> dead `node_modules`, and old Paperclip data). Delete it once the running Hermes
> gateway is stopped. Reversible cleanup lives in `.trash/` (also gitignored).

## The Orbit concept (big picture)

Orbit is a **closed-loop campaign agent** for lean marketing teams (Track 6 — Cross-MCP Orchestration). The defining architecture is a 6-step loop with three human touchpoints:

1. **Goal input** (human) → 2. **Context gathering** (Marketing + Analytics MCPs) → 3. **Campaign planning** (human approves) → 4. **Execution** (Marketing MCP, inside Bloomreach) → 5. **Performance monitoring** (Analytics MCP) → 6. **Iteration proposal** (human approves) → loop back.

The differentiator vs. a scripted bot: the agent must *understand → decide → act*, with meaningful orchestration across MCPs — not just chained API calls.

## Hard constraints (from hackathon rules — these override convenience)

- **Sandbox/synthetic data only.** Never use production customer data; no PII leaves Bloomreach environments.
- **Human approval is mandatory** before any campaign-facing action. The agent recommends; the human executes.
- **Be transparent about what is simulated vs. actually executed** — mocking parts of the workflow is allowed, but must be disclosed.
- Never commit credentials or API keys anywhere (repo, Slack, screenshots, demo video).

## Key dates

- Build window: open since May 26, 2026.
- **Final submission deadline: Jun 2, 2026, 4:00 PM PST.**
- Demo Day: Jun 4, 2026.

## Required submission artifacts (track these as deliverables)

Project Summary (≤500 words, non-technical), 5–6 min demo video, architecture overview (must show UI, agent runtime, MCPs, data flow, output, **human approval step**), team details, MCP usage explanation, responsible-design note, and a **code repo + README with setup instructions**.

## Note for future Claude instances

Until source code exists, "the codebase" is these planning docs. When implementation starts, update this file with the real build/run/test commands and the chosen agent-runtime architecture (UI, agent loop, MCP client wiring, mock vs. live boundary).
