# A/B Split Scenario — Wiring Reference (2026-06-01)

## Flow shape
trigger → ab-split → [Variant A: send-email] / [Variant B: send-email]

## Connector indices (verified from skill + live export)
| Edge | source node | source connector_index | dest node | dest connector_index |
|---|---|---|---|---|
| trigger → ab-split | on-event-trigger | 0 | ab-split | 0 |
| ab-split → email A | ab-split | 1 | send-email (A) | 0 |
| ab-split → email B | ab-split | 2 | send-email (B) | 0 |

ab-split variants array order matches connector_index order: variants[0] → index 1, variants[1] → index 2.

## Example ab-split node
```json
{
  "id": 2,
  "type": "ab-split",
  "version": 1,
  "x": 520,
  "y": 300,
  "variants": [
    {"name": "Variant A", "percentage": 50, "id": "variant_a"},
    {"name": "Variant B", "percentage": 50, "id": "variant_b"}
  ]
}
```

## Example connections block
```json
"connections": [
  {"source": {"node_id": 1, "connector_index": 0}, "destination": {"node_id": 2, "connector_index": 0}},
  {"source": {"node_id": 2, "connector_index": 1}, "destination": {"node_id": 3, "connector_index": 0}},
  {"source": {"node_id": 2, "connector_index": 2}, "destination": {"node_id": 4, "connector_index": 0}}
]
```
Node 1 = trigger, 2 = ab-split, 3 = email A, 4 = email B.

## Campaign context (women's apparel win-back, 2026-06-01)
- Trigger event: orbit_winback_ab_triggered
- Variant A: Discount-led, offer_code WB20A, discount_tier 20
- Variant B: FOMO-led, offer_code WB20B, discount_tier 20
- KPI: 7-day purchase conversion (>5%), 48h open rate as early signal
- Cohort: 15,255 one-time women's apparel buyers, silent 60d, AOV ~$1,042
