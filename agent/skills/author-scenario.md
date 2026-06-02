# Author a Scenario (programmatic JSON build)

**Goal:** the agent builds a Bloomreach scenario as a JSON object, a human pastes it into the Engagement UI (paste = the approval gate). No API deploys scenarios — the agent produces the artifact; the human imports + activates.

**Reference:** `scenarios/examples/orbit_winback.json` — a real BR clipboard export containing one of every node type. Pattern-match it. This skill is the rules; that file is the ground truth.

---

## The wrapper (BR clipboard format — produce exactly this shape)
```json
{
  "scenarioId": "<any id or reuse>",
  "appVersion": "v1.310.0-0-g8cfbd920",
  "copiedData": { "nodes": [ ... ], "connections": [ ... ] }
}
```
- `copiedData.nodes` — array of node objects (each has unique integer `id`, `type`, `x`, `y`, + type-specific config).
- `copiedData.connections` — array of edges wiring the nodes into a flow.

## Connections — how to wire a flow
```json
{ "source": {"node_id": 2, "connector_index": 1},
  "destination": {"node_id": 3, "connector_index": 0} }
```
- One edge = a source node's OUTPUT port → a destination node's INPUT port.
- **The destination `connector_index` is ALWAYS `0`** (input port).
- **The source `connector_index` is the node's OUTPUT port — and these are VERIFIED from a real working branched export (2026-05-31). Get them wrong and BR SILENTLY DROPS the edge on import:**

| Source node type | Output `connector_index` value(s) |
|---|---|
| `on-event-trigger` | `0` |
| `send-email-action` | `1` |
| `wait-action` | `1` |
| `condition` | `1` (one branch) and `2` (other branch) |
| `ab-split` / `ab-split-contextual` | `1`, `2`, … (one per variant, in `variants[]` order) |

- ⚠️ Triggers use `0`; almost everything else's first/only output is `1`, NOT `0`. This is the #1 import bug — a wrong source index is dropped without error, orphaning everything downstream.
- For `condition`, confirm which of `1`/`2` is the Yes vs No branch against the UI (the index↔branch mapping follows connection order in the editor; don't assume Yes=1).
- **Convergence is ALLOWED:** multiple edges may point into the same destination node (e.g. three emails → one wait, all with destination `connector_index: 0`). Verified working.
- Every `node_id` referenced MUST exist in `nodes`. No dangling edges.

---

## KEEP CONSTANT — project-bound IDs (do not invent these)
| Field | Value | Where |
|---|---|---|
| `provider.channel_extension_id` | `6a1720ff1a26b57a6b5c97f6` | email node → `design.data.provider` |
| `consent_category` | `"other"` | email node top-level |
| `segmentation_id` | (none exist yet — leave `null` / avoid `segmentation-fork` until a segment is built) | segmentation-fork node |

Invent freely: `event.type`, all copy (`subject`/`preheader`/`jinja_html`), `sender_email`/`sender_name`, delays, variant %, condition filters, node `id`s, `x`/`y`.

---

## Node palette (config the agent fills)
| `type` | Purpose | Key fields |
|---|---|---|
| `on-event-trigger` | start on a tracked event | `event.type`, `event.filter`, `delay_seconds` |
| `on-date-attribute-trigger` | start on a date attribute | `trigger_period`, `timezone`, `times` |
| `repeated-trigger` | recurring start | `repeat`, `times`, `timezone`, `from_date`/`to_date` |
| `send-email-action` | send email | top: `consent_category`, `frequency_policy`; `design.data`: see below |
| `segmentation-fork` | branch by segment | `segmentation_id`, `segments[]` (needs a real segment) |
| `ab-split` | random split | `variants[]` = `[{name,percentage,id}]` (sum 100) |
| `ab-split-contextual` | AI personalization | `variants[]`, `optimization_target`, `bandit_definition` (copy from example) |
| `condition` | branch by customer filter | `customer_filter.{filters,formula}`, `evaluate_jinja` |
| `wait-action` | delay | `count`, `units` (`hours`/`days`), `count_template`, `optimize` |
| `limit` | cap recipients | `steps[].limit` |

### Email node `design.data` contract
```json
{
  "subject": "<jinja subject>",
  "preheader": "<jinja preheader>",
  "jinja_html": "<FULL email HTML — use templates/winback-shell.html so {{customer.email_headline}}/{{email_body}} render>",
  "sender_email": "orbit-seed-1@rohlik.cz",
  "sender_name": "Pacific Apparel",
  "provider": { "type": "channel_extension", "channel_extension_id": "6a1720ff1a26b57a6b5c97f6" },
  "reply_to": null, "file_ids": [], "translations": {}
}
```
Top-level email node also needs: `"type":"send-email-action"`, `"consent_category":"other"`, `"frequency_policy":"unlimited-policy"`, `"transfer_identity":true`, `"version":1`, unique `id`, `x`, `y`.

---

## Recipe — build a new campaign
1. Pick the trigger (usually `on-event-trigger` with a new `event.type`, e.g. `orbit_cartrecovery_triggered`).
2. Author the email HTML (start from `templates/winback-shell.html`); set `subject`/`preheader`.
3. Choose flow nodes from the palette (condition? wait? A/B?).
4. Give each node a unique integer `id`; lay out `x`/`y` (cosmetic).
5. Wire `connections` (mind `connector_index` on branches).
6. Keep the project-bound IDs constant.
7. Output the full wrapper JSON → human pastes into BR → activates.

## Minimal worked example (trigger → email)
```json
{"scenarioId":"orbit_demo","appVersion":"v1.310.0-0-g8cfbd920","copiedData":{
 "nodes":[
  {"id":1,"type":"on-event-trigger","version":1,"delay_seconds":0,"event":{"type":"orbit_winback_triggered","filter":[]},"x":300,"y":300},
  {"id":2,"type":"send-email-action","version":1,"consent_category":"other","frequency_policy":"unlimited-policy","transfer_identity":true,"recipient_email":"","recipient_name":"",
   "design":{"type":"raw","data":{"subject":"…","preheader":"…","jinja_html":"<…shell…>","sender_email":"orbit-seed-1@rohlik.cz","sender_name":"Pacific Apparel","provider":{"type":"channel_extension","channel_extension_id":"6a1720ff1a26b57a6b5c97f6"},"file_ids":[],"translations":{}}},
   "x":520,"y":300}
 ],
 "connections":[{"source":{"node_id":1,"connector_index":0},"destination":{"node_id":2,"connector_index":0}}]
}}
```

## Branching example (trigger → condition → [branch1: email] / [branch2: wait → email])
Real, verified indices: trigger out **0**; condition out **1** and **2**; wait out **1**.
Wire: trigger→condition; condition branch1→emailA; condition branch2→wait; wait→emailB.
```json
"connections":[
 {"source":{"node_id":1,"connector_index":0},"destination":{"node_id":2,"connector_index":0}},
 {"source":{"node_id":2,"connector_index":1},"destination":{"node_id":3,"connector_index":0}},
 {"source":{"node_id":2,"connector_index":2},"destination":{"node_id":4,"connector_index":0}},
 {"source":{"node_id":4,"connector_index":1},"destination":{"node_id":5,"connector_index":0}}
]
```
(node 1 = trigger, 2 = condition, 3 = email on branch 1, 4 = wait, 5 = email after wait)
Reference: `scenarios/generated/orbit_cartrecovery.json` is a real working branched export — copy its connector indices.

---

## Gotchas
- **Use the shell HTML.** The example's embedded HTML is the OLD hardcoded copy (no `email_headline`/`email_body`). Embed `templates/winback-shell.html` so agent-authored copy renders.
- **Don't use `segmentation-fork`** until a real segmentation exists (sandbox has 0; `segmentation_id` would be null → broken branch). Use `condition` with a `customer_filter` instead.
- **Leave the `condition` filter EMPTY for a human to fill.** Set `customer_filter` to `{"filters": [], "formula": ""}` and `name` the node clearly (e.g. "VIP churn-risk? — set filter"). Do NOT invent `property`/`event` field names or operator strings — those are project-specific schema you can't verify, and guessing them produces a filter that imports but doesn't match real data. The branch structure + connections still import correctly; the human just fills the filter in the UI before activating. This keeps the whole JSON paste-and-go except the one field only a human can get right.
- **Unique node ids**; every connection references an existing id; no orphan branches.
- **Escape the HTML** properly as a JSON string (it's one long escaped value in `jinja_html`).
- The human still **activates** the scenario after pasting (Running, not Draft) and consent still applies — see `execute-campaign.md` / `check-consent.md`.
