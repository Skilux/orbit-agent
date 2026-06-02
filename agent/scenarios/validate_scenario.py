#!/usr/bin/env python3
"""Validate an Orbit scenario JSON against the author-scenario skill rules.

Checks the Bloomreach clipboard format the agent must produce:
  - wrapper shape (scenarioId / appVersion / copiedData{nodes,connections})
  - node integrity (unique int ids, known types, x/y)
  - connection integrity (destination connector_index == 0, no dangling edges)
  - source connector_index matches the VERIFIED per-type rule (the #1 import bug)
  - constant project-bound IDs (channel_extension_id, consent_category=other)
  - email node design.data contract (jinja_html present)

Usage: python validate_scenario.py <file.json> [<file.json> ...]
Exit 0 if all files pass (errors==0); non-zero otherwise.
"""
import json
import sys

# Verified source output connector indices (from the skill / real BR export).
# A set of allowed indices per source node type. Triggers emit 0; most else 1.
SOURCE_CONNECTOR_RULES = {
    "on-event-trigger": {0},
    "on-date-attribute-trigger": {0},
    "repeated-trigger": {0},
    "send-email-action": {1},
    "wait-action": {1},
    "condition": {1, 2},
    "limit": {1},
    # ab-split / ab-split-contextual: 1..N (one per variant) — handled dynamically
}
TRIGGER_TYPES = {"on-event-trigger", "on-date-attribute-trigger", "repeated-trigger"}
KNOWN_TYPES = set(SOURCE_CONNECTOR_RULES) | {
    "segmentation-fork", "ab-split", "ab-split-contextual",
}
CHANNEL_EXT_ID = "6a1720ff1a26b57a6b5c97f6"


def validate(path):
    errors, warnings = [], []
    try:
        with open(path) as f:
            doc = json.load(f)
    except Exception as e:
        return [f"NOT VALID JSON: {e}"], []

    # ── wrapper ──
    for k in ("scenarioId", "appVersion", "copiedData"):
        if k not in doc:
            errors.append(f"missing top-level key '{k}'")
    cd = doc.get("copiedData", {})
    if not isinstance(cd, dict):
        return errors + ["copiedData is not an object"], warnings
    nodes = cd.get("nodes")
    conns = cd.get("connections", [])
    if not isinstance(nodes, list) or not nodes:
        return errors + ["copiedData.nodes missing or empty"], warnings
    if not isinstance(conns, list):
        errors.append("copiedData.connections is not a list")
        conns = []

    # ── nodes ──
    ids, types_by_id, variant_count = set(), {}, {}
    for i, n in enumerate(nodes):
        nid = n.get("id")
        if not isinstance(nid, int):
            errors.append(f"node[{i}] id missing or not an integer: {nid!r}")
        elif nid in ids:
            errors.append(f"duplicate node id {nid}")
        else:
            ids.add(nid)
        t = n.get("type")
        types_by_id[nid] = t
        if t not in KNOWN_TYPES:
            warnings.append(f"node {nid}: unknown type '{t}' (not in palette)")
        if "x" not in n or "y" not in n:
            warnings.append(f"node {nid}: missing x/y (cosmetic)")
        if t in ("ab-split", "ab-split-contextual"):
            variant_count[nid] = len(n.get("variants", []) or [])
        # email node contract
        if t == "send-email-action":
            if n.get("consent_category") != "other":
                errors.append(f"node {nid}: consent_category != 'other' ({n.get('consent_category')!r})")
            data = (n.get("design") or {}).get("data") or {}
            prov = data.get("provider") or {}
            if prov.get("channel_extension_id") != CHANNEL_EXT_ID:
                errors.append(f"node {nid}: provider.channel_extension_id wrong/missing ({prov.get('channel_extension_id')!r})")
            if not (data.get("jinja_html") or "").strip():
                errors.append(f"node {nid}: email design.data.jinja_html empty/missing")

    # ── connections ──
    referenced = set()
    for j, c in enumerate(conns):
        src, dst = c.get("source", {}), c.get("destination", {})
        sid, sidx = src.get("node_id"), src.get("connector_index")
        did, didx = dst.get("node_id"), dst.get("connector_index")
        for label, nid in (("source", sid), ("destination", did)):
            if nid not in ids:
                errors.append(f"connection[{j}] {label}.node_id {nid} not in nodes (dangling edge)")
            else:
                referenced.add(nid)
        if didx != 0:
            errors.append(f"connection[{j}] destination.connector_index must be 0, got {didx}")
        st = types_by_id.get(sid)
        if st in SOURCE_CONNECTOR_RULES:
            if sidx not in SOURCE_CONNECTOR_RULES[st]:
                errors.append(
                    f"connection[{j}] source node {sid} ({st}): connector_index {sidx} "
                    f"invalid — expected one of {sorted(SOURCE_CONNECTOR_RULES[st])} "
                    f"(wrong index => BR silently drops the edge)")
        elif st in ("ab-split", "ab-split-contextual"):
            vc = variant_count.get(sid, 0)
            if not (1 <= (sidx or -1) <= vc):
                errors.append(f"connection[{j}] source node {sid} ({st}): connector_index {sidx} outside variant range 1..{vc}")

    # orphan nodes (no edges) — warn, triggers excepted
    for nid in ids:
        if nid not in referenced and types_by_id.get(nid) not in TRIGGER_TYPES:
            warnings.append(f"node {nid} ({types_by_id.get(nid)}): no connections (orphan?)")

    return errors, warnings


def main():
    paths = sys.argv[1:]
    if not paths:
        print("usage: validate_scenario.py <file.json> ...")
        return 2
    total_err = 0
    for p in paths:
        errors, warnings = validate(p)
        total_err += len(errors)
        status = "PASS ✅" if not errors else f"FAIL ❌ ({len(errors)} errors)"
        print(f"\n=== {p} — {status} ===")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  warn:  {w}")
    print(f"\nTotal errors across {len(paths)} file(s): {total_err}")
    return 0 if total_err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
