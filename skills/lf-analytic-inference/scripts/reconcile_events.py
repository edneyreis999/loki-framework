#!/usr/bin/env python3
"""Reconcile immutable inference events into an eligibility-only snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


EVENT_KEYS = {"schema_version", "event_id", "sequence", "source", "inference_id", "inference_revision", "stage", "outcome", "reason", "agent_capability", "cost"}
SOURCE_KEYS = {"analysis_ref", "run_id", "handoff_id", "evidence_refs"}
COST_KEYS = {"context", "tools"}
STAGES = {"selected", "investigated", "validated", "rejected", "material-finding", "task-helped", "false-positive", "repeated-evidence", "stale"}
STAGE_COMPONENT = {
    "selected": "selected_count",
    "investigated": "investigated_count",
    "validated": "validated_count",
    "rejected": "rejected_count",
    "material-finding": "material_findings_count",
    "task-helped": "tasks_helped_count",
    "false-positive": "false_positive_count",
    "repeated-evidence": "repeated_evidence_count",
    "stale": "stale_count",
}
WEIGHT_COMPONENT = {
    "selected": "selected_count",
    "investigated": "investigated_count",
    "validated": "validated_count",
    "material_finding": "material_findings_count",
    "task_helped": "tasks_helped_count",
    "false_positive": "false_positive_count",
    "repeated_evidence": "repeated_evidence_count",
    "stale": "stale_count",
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_policy(policy: Any) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not isinstance(policy, dict):
        return None, ["POLICY_OBJECT"]
    required = {"schema_version", "policy_id", "status", "approved_candidate_digest_sha256", "approved_candidate", "semantics"}
    if set(policy) != required:
        errors.append("POLICY_KEYS")
    if policy.get("schema_version") != "1":
        errors.append("POLICY_SCHEMA_VERSION")
    if policy.get("policy_id") != "analytic-inference-policy-v1":
        errors.append("POLICY_ID")
    if policy.get("status") != "active":
        errors.append("POLICY_STATUS_ACTIVE")
    candidate = policy.get("approved_candidate")
    if not isinstance(candidate, dict):
        return None, errors + ["POLICY_CANDIDATE"]
    required_candidate = {"candidate_id", "policy_source", "schema_version", "status", "values"}
    if set(candidate) != required_candidate:
        return None, errors + ["POLICY_CANDIDATE_KEYS"]
    expected_identity = {
        "candidate_id": "analytic-inference-policy-v1-candidate-001",
        "policy_source": "PC-BALANCED",
        "schema_version": "1",
        "status": "proposed",
    }
    for key, expected in expected_identity.items():
        if candidate.get(key) != expected:
            errors.append(f"POLICY_CANDIDATE_IDENTITY:{key}")
    digest = hashlib.sha256(canonical(candidate)).hexdigest()
    if digest != policy.get("approved_candidate_digest_sha256"):
        errors.append("POLICY_DIGEST_MISMATCH")
    values = candidate.get("values")
    required_values = {"catalog_limit", "cost_budget", "fan_out_limit", "handoff_timeout_ticks", "promotion_min", "purge_review_max", "removals_per_cycle", "reorganization_max", "score_weights"}
    if not isinstance(values, dict) or set(values) != required_values:
        return None, errors + ["POLICY_VALUE_KEYS"]
    for key in ("catalog_limit", "cost_budget", "fan_out_limit", "handoff_timeout_ticks", "removals_per_cycle"):
        if not is_int(values.get(key)) or values[key] < 0:
            errors.append(f"POLICY_BOUND:{key}")
    for key in ("promotion_min", "purge_review_max", "reorganization_max"):
        if not is_int(values.get(key)):
            errors.append(f"POLICY_INTEGER:{key}")
    weights = values.get("score_weights")
    if not isinstance(weights, dict) or set(weights) != set(WEIGHT_COMPONENT):
        errors.append("POLICY_WEIGHT_KEYS")
    elif not all(is_int(value) for value in weights.values()):
        errors.append("POLICY_WEIGHT_INTEGER")
    elif weights["selected"] != 0:
        errors.append("POLICY_SELECTED_WEIGHT")
    semantics = policy.get("semantics")
    expected_semantics = {
        "approved_candidate_status_is_identity_bound": True,
        "thresholds_are_inclusive": True,
        "score_is_eligibility_only": True,
        "automatic_mutation": False,
        "purge_requires_independent_just_in_time_approval": True,
        "consumer_state_required": True,
        "package_catalog": False,
        "initial_consumer_catalog": "absent-or-empty",
    }
    if not isinstance(semantics, dict) or set(semantics) != set(expected_semantics):
        errors.append("POLICY_SEMANTICS_KEYS")
    else:
        for key, expected in expected_semantics.items():
            if semantics.get(key) != expected:
                errors.append(f"POLICY_SEMANTICS_WEAKENED:{key}")
    return values, errors


def validate_cost(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0) or value in {"unknown", "unsupported"}


def validate_event(event: Any, position: int) -> list[str]:
    prefix = f"EVENT[{position}]"
    errors: list[str] = []
    if not isinstance(event, dict):
        return [f"{prefix}:OBJECT"]
    required = EVENT_KEYS - {"sequence"}
    missing = required - event.keys()
    unknown = event.keys() - EVENT_KEYS
    errors.extend(f"{prefix}:REQUIRED:{key}" for key in sorted(missing))
    errors.extend(f"{prefix}:UNKNOWN:{key}" for key in sorted(unknown))
    if event.get("schema_version") != 1:
        errors.append(f"{prefix}:SCHEMA_VERSION")
    for key in ("event_id", "inference_id", "reason", "agent_capability"):
        if not isinstance(event.get(key), str) or not event[key]:
            errors.append(f"{prefix}:{key}:NON_EMPTY_STRING")
    if not is_int(event.get("inference_revision")) or event["inference_revision"] < 1:
        errors.append(f"{prefix}:INFERENCE_REVISION")
    if "sequence" in event and (not is_int(event["sequence"]) or event["sequence"] < 0):
        errors.append(f"{prefix}:SEQUENCE")
    if event.get("stage") not in STAGES:
        errors.append(f"{prefix}:STAGE")
    source = event.get("source")
    if not isinstance(source, dict) or set(source) != SOURCE_KEYS:
        errors.append(f"{prefix}:SOURCE_KEYS")
    else:
        for key in ("analysis_ref", "run_id", "handoff_id"):
            if not isinstance(source[key], str) or not source[key]:
                errors.append(f"{prefix}:SOURCE:{key}")
        refs = source["evidence_refs"]
        if not isinstance(refs, list) or not all(isinstance(item, str) and item for item in refs) or len(refs) != len(set(refs)):
            errors.append(f"{prefix}:SOURCE:EVIDENCE_REFS")
    cost = event.get("cost")
    if not isinstance(cost, dict) or set(cost) != COST_KEYS:
        errors.append(f"{prefix}:COST_KEYS")
    elif not all(validate_cost(cost[key]) for key in COST_KEYS):
        errors.append(f"{prefix}:COST_VALUE")
    return errors


def blocked(diagnostics: list[str], policy: Any = None) -> int:
    output = {
        "diagnostics": sorted(set(diagnostics)),
        "eligibility": None,
        "mutation_applied": False,
        "policy_digest": policy.get("approved_candidate_digest_sha256") if isinstance(policy, dict) else None,
        "policy_id": policy.get("policy_id") if isinstance(policy, dict) else None,
        "status": "blocked",
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path, help="JSON array or object with an events array")
    parser.add_argument("--policy", type=Path, default=Path(__file__).resolve().parents[1] / "references" / "policy-v1.json")
    parser.add_argument("--protected", action="store_true", help="classify the inference as protected")
    args = parser.parse_args()
    try:
        document = load_json(args.events)
        policy = load_json(args.policy)
    except (OSError, json.JSONDecodeError) as exc:
        return blocked([f"INPUT:{exc}"])
    values, policy_errors = validate_policy(policy)
    if policy_errors or values is None:
        return blocked(policy_errors, policy)
    events = document.get("events") if isinstance(document, dict) else document
    if not isinstance(events, list):
        return blocked(["EVENTS_ARRAY"], policy)
    errors: list[str] = []
    for position, event in enumerate(events):
        errors.extend(validate_event(event, position))
    if errors:
        return blocked(errors, policy)
    has_sequence = ["sequence" in event for event in events]
    if any(has_sequence) and not all(has_sequence):
        return blocked(["AMBIGUOUS_EVENT_ORDER"], policy)
    identity: dict[str, bytes] = {}
    unique: dict[str, dict[str, Any]] = {}
    replayed: list[str] = []
    for event in events:
        event_id = event["event_id"]
        payload = canonical(event)
        if event_id in identity:
            if identity[event_id] != payload:
                return blocked([f"EVENT_ID_PAYLOAD_CONFLICT:{event_id}"], policy)
            replayed.append(event_id)
            continue
        identity[event_id] = payload
        unique[event_id] = event
    inference_ids = {event["inference_id"] for event in unique.values()}
    revisions = {event["inference_revision"] for event in unique.values()}
    if len(inference_ids) > 1:
        return blocked(["MULTIPLE_INFERENCE_IDS"], policy)
    if len(revisions) > 1:
        return blocked(["MULTIPLE_INFERENCE_REVISIONS"], policy)
    order = sorted(unique.values(), key=(lambda item: (item["sequence"], item["event_id"])) if all(has_sequence) else (lambda item: item["event_id"]))
    components = {key: 0 for key in sorted(set(STAGE_COMPONENT.values()))}
    for event in order:
        components[STAGE_COMPONENT[event["stage"]]] += 1
    weights = values["score_weights"]
    score = sum(components[component] * weights[weight] for weight, component in WEIGHT_COMPONENT.items())
    eligibility = {
        "promotion": score >= values["promotion_min"],
        "purge_review": (not args.protected) and score <= values["purge_review_max"],
        "reorganization": score <= values["reorganization_max"],
    }
    as_of = order[-1]["event_id"] if order else None
    freshness = "stale" if components["stale_count"] else "current"
    output = {
        "applied_event_ids": [event["event_id"] for event in order],
        "diagnostics": ["EVENT_REPLAY"] if replayed else [],
        "eligibility": eligibility,
        "inference_id": next(iter(inference_ids), None),
        "inference_revision": next(iter(revisions), None),
        "mutation_applied": False,
        "policy_digest": policy["approved_candidate_digest_sha256"],
        "policy_id": policy["policy_id"],
        "replayed_event_ids": replayed,
        "snapshot": {
            "algorithm_version": policy["policy_id"],
            "as_of_event": as_of,
            "components": components,
            "denominators": {"unique_events": len(order)},
            "freshness": freshness,
            "score": score,
        },
        "status": "valid",
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
