# Scenarios — Agent-Authored Campaign Artifacts

**Premise:** Bloomreach scenarios and email templates are just **JSON + HTML files**. An LLM agent can author new ones by pattern-matching real examples; a human then **uploads/imports them into Bloomreach** (that import = the human-approval gate). The agent builds the artifact; the human deploys it.

This reframes the earlier "agent can't build campaigns" limit: the agent **can** design new campaign *types* (offer + copy + a new trigger + a new template). It just doesn't auto-deploy them — no Bloomreach API creates scenarios, so a human imports.

## Folder layout
```
scenarios/
  examples/
    orbit_winback.json   ← GOLD example (real, harvested live 2026-05-31)
  generated/             ← agent writes new campaign artifacts here (create as needed)
templates/
  winback-shell.html     ← the email HTML shell (the design.data.jinja_html target)
```

## How an agent authors a new scenario
1. Read `examples/orbit_winback.json` to learn the structure.
2. Author a new email HTML (start from `templates/winback-shell.html`), filling brand chrome and `{{ customer.* }}` placeholders.
3. Produce a new scenario JSON: change `name`, the trigger `event.type` (e.g. `orbit_cartrecovery_triggered`), `subject`, `preheader`, and embed the new HTML in `design.data.jinja_html`.
4. **Keep these project-bound IDs constant:** `provider.channel_extension_id` (Mailgun) and `consent_category`.
5. Human imports the JSON + activates the scenario in the Engagement UI.

## What's free vs. fixed (from the real example)
| Field | Agent authors? |
|---|---|
| `name`, trigger `event.type`, `delay_seconds` | ✅ free |
| `design.data.jinja_html` (the email HTML) | ✅ free — this is the bulk of the work, same as authoring any template |
| `subject`, `preheader`, `sender_email`, `sender_name` | ✅ free |
| `provider.channel_extension_id` (Mailgun) | ❌ keep constant — project-bound |
| `consent_category` (`other`) | ❌ keep constant — or sends are suppressed |
| `_id`, node ids, timestamps, `cached_email_hash` | regenerate / omit on import |

## Import format — CONFIRMED
The real BR clipboard export (`examples/orbit_winback.json`) is the importable format:
```
{ scenarioId, appVersion, copiedData: { nodes[], connections[] } }
```
It includes the `connections` edge array (with `source`/`destination` + `connector_index`) and a valid example of **all 10 node types**. The agent produces this shape; a human pastes it into the Engagement UI and activates. Full schema + rules: `skills/author-scenario.md`.

## Confidence
- **HTML templates: HIGH** — proven; the agent authored `winback-shell.html` and we sent a real email from it.
- **Scenario JSON: HIGH** — we have a real, valid clipboard export of every node type + the connections format. Remaining care items are mechanical: keep project-bound IDs constant (`channel_extension_id`, `consent_category`), wire connections correctly, embed the shell HTML, and avoid `segmentation-fork` until a real segment exists.

## Finding from the harvest
The currently **deployed** `orbit_winback` scenario still embeds the ORIGINAL hardcoded HTML (`We've missed you, {{ first_name }}` + a fixed body) — **not** the new shell. To make the email agent-authored, paste `templates/winback-shell.html` into the scenario's email node (replacing the current HTML) so `email_headline` / `email_body` render.
