# Orbit — Submission Artifacts

Everything the Loomi Connect AI Hackathon portal asks for. Deadline: **June 2, 11:59 PM PST**.

| Portal field | Required | File | Status |
|---|---|---|---|
| **Demo Video** (≤5 min, MP4/MOV) | ✅ | record using [`demo-script.md`](demo-script.md) | ⬜ to record (do last) |
| **Architecture Diagram** (PNG/JPG/PDF) | ✅ | [`architecture.md`](architecture.md) → export `architecture.png` | ✅ source ready |
| **Project Summary** (2–4 sentences) | ✅ | [`project-summary.md`](project-summary.md) | ✅ paste-ready |
| **MCP Usage Explanation** | ✅ | [`mcp-usage.md`](mcp-usage.md) | ✅ paste-ready |
| **Responsible AI Note** | ✅ | [`responsible-ai-note.md`](responsible-ai-note.md) | ✅ paste-ready |
| **GitHub Repo** | optional | repo root + [`../../README.md`](../../README.md) | ✅ public/setup ready |
| **Presentation Deck** | optional | [`../../demo/orbit-deck.pdf`](../../demo/orbit-deck.pdf) (8-page PDF) · per-slide PNGs in [`../../demo/deck/`](../../demo/deck/) | ✅ ready |
| **Team Details** | (form) | [`team.md`](team.md) | ⬜ fill in |

## Before you submit
1. **Fill `team.md`** (name, Slack handle, team lead).
2. **Export the diagram** to PNG: paste [`architecture.md`](architecture.md)'s Mermaid into <https://mermaid.live>, or run
   `cd docs/submission && npx -y @mermaid-js/mermaid-cli -i architecture.md -o architecture.png`.
3. **Record the video last**, after a clean `docker compose up` and a fresh Loomi token. Follow [`demo-script.md`](demo-script.md).
4. Paste Project Summary / MCP Usage / Responsible AI text straight from the files above.

## One-line pitch
Orbit is a closed-loop campaign agent that orchestrates Loomi Connect MCP (discovery) and a custom write-MCP (execution) into a goal→plan→execute→monitor→iterate loop, with a human approving every campaign-facing action.
