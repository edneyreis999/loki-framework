#!/usr/bin/env python3
"""Validate an analytic-inference catalog without mutating it."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


INDEX_KEYS = {"schema_version", "catalog_id", "technology", "aliases", "active_limit", "entries"}
ENTRY_KEYS = {"inference_id", "revision", "status", "summary", "technologies", "surfaces", "objectives", "signals", "locator"}
RECORD_KEYS = {"schema_version", "inference_id", "revision", "status", "statement", "applicability", "investigation", "provenance", "lineage", "snapshot"}
STATUS = {"active", "protected", "redirect", "tombstone"}
FRESHNESS = {"current", "stale", "unknown", "unsupported"}
COMPONENTS = {
    "selected_count", "investigated_count", "validated_count", "rejected_count",
    "material_findings_count", "tasks_helped_count", "false_positive_count",
    "repeated_evidence_count", "stale_count",
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def exact_keys(value: Any, expected: set[str], where: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{where}:TYPE_OBJECT")
        return False
    missing = sorted(expected - value.keys())
    unknown = sorted(value.keys() - expected)
    errors.extend(f"{where}:REQUIRED:{key}" for key in missing)
    errors.extend(f"{where}:UNKNOWN:{key}" for key in unknown)
    return not missing and not unknown


def string_array(value: Any, where: str, errors: list[str]) -> bool:
    valid = isinstance(value, list) and all(isinstance(item, str) and item for item in value)
    if not valid:
        errors.append(f"{where}:STRING_ARRAY")
        return False
    if len(value) != len(set(value)):
        errors.append(f"{where}:DUPLICATE")
        return False
    return True


def validate_policy(policy: Any, errors: list[str]) -> dict[str, Any] | None:
    keys = {"schema_version", "policy_id", "status", "approved_candidate_digest_sha256", "approved_candidate", "semantics"}
    if not exact_keys(policy, keys, "policy", errors):
        return None
    if policy.get("schema_version") != "1":
        errors.append("policy:SCHEMA_VERSION")
    if policy.get("policy_id") != "analytic-inference-policy-v1":
        errors.append("policy:POLICY_ID")
    if policy.get("status") != "active":
        errors.append("policy:STATUS_ACTIVE")
    candidate = policy.get("approved_candidate")
    if not isinstance(candidate, dict):
        errors.append("policy:APPROVED_CANDIDATE")
        return None
    candidate_keys = {"candidate_id", "policy_source", "schema_version", "status", "values"}
    if not exact_keys(candidate, candidate_keys, "policy.approved_candidate", errors):
        return None
    candidate_identity = {
        "candidate_id": "analytic-inference-policy-v1-candidate-001",
        "policy_source": "PC-BALANCED",
        "schema_version": "1",
        "status": "proposed",
    }
    for key, expected in candidate_identity.items():
        if candidate.get(key) != expected:
            errors.append(f"policy.approved_candidate:{key}:IDENTITY")
    digest = hashlib.sha256(canonical(candidate)).hexdigest()
    if digest != policy.get("approved_candidate_digest_sha256"):
        errors.append("policy:DIGEST_MISMATCH")
    values = candidate.get("values")
    value_keys = {
        "catalog_limit", "cost_budget", "fan_out_limit", "handoff_timeout_ticks",
        "promotion_min", "purge_review_max", "removals_per_cycle",
        "reorganization_max", "score_weights",
    }
    if not exact_keys(values, value_keys, "policy.values", errors):
        return None
    for key in ("catalog_limit", "cost_budget", "fan_out_limit", "handoff_timeout_ticks", "removals_per_cycle"):
        if not is_int(values.get(key)) or values[key] < 0:
            errors.append(f"policy.values:{key}:NON_NEGATIVE_INTEGER")
    for key in ("promotion_min", "purge_review_max", "reorganization_max"):
        if not is_int(values.get(key)):
            errors.append(f"policy.values:{key}:INTEGER")
    weights = values.get("score_weights")
    weight_keys = {"false_positive", "investigated", "material_finding", "repeated_evidence", "selected", "stale", "task_helped", "validated"}
    if exact_keys(weights, weight_keys, "policy.values.score_weights", errors):
        for key in sorted(weight_keys):
            if not is_int(weights[key]):
                errors.append(f"policy.values.score_weights:{key}:INTEGER")
        if weights.get("selected") != 0:
            errors.append("policy.values.score_weights:selected:MUST_BE_ZERO")
    semantics = policy.get("semantics")
    expected_semantics = {
        "approved_candidate_status_is_identity_bound": True,
        "thresholds_are_inclusive": True,
        "score_is_eligibility_only": True,
        "automatic_mutation": False,
        "purge_requires_independent_just_in_time_approval": True,
        "consumer_overlay_v1": False,
        "initial_catalog": "empty",
    }
    if not exact_keys(semantics, set(expected_semantics), "policy.semantics", errors):
        return None
    for key, expected in expected_semantics.items():
        if semantics.get(key) != expected:
            errors.append(f"policy.semantics:{key}:WEAKENED")
    return values


def validate_index(index: Any, errors: list[str]) -> list[dict[str, Any]]:
    if not exact_keys(index, INDEX_KEYS, "index", errors):
        return []
    if index.get("schema_version") != 1:
        errors.append("index:SCHEMA_VERSION")
    for key in ("catalog_id", "technology"):
        if not isinstance(index.get(key), str) or not index[key]:
            errors.append(f"index:{key}:NON_EMPTY_STRING")
    string_array(index.get("aliases"), "index.aliases", errors)
    if not is_int(index.get("active_limit")) or index["active_limit"] < 0:
        errors.append("index:active_limit:NON_NEGATIVE_INTEGER")
    entries = index.get("entries")
    if not isinstance(entries, list):
        errors.append("index:entries:ARRAY")
        return []
    ids: set[str] = set()
    locators: set[str] = set()
    last_id: str | None = None
    for position, entry in enumerate(entries):
        where = f"index.entries[{position}]"
        if not exact_keys(entry, ENTRY_KEYS, where, errors):
            continue
        inference_id = entry.get("inference_id")
        if not isinstance(inference_id, str) or not inference_id:
            errors.append(f"{where}:inference_id:NON_EMPTY_STRING")
        elif inference_id in ids:
            errors.append(f"{where}:DUPLICATE_ID:{inference_id}")
        else:
            ids.add(inference_id)
        if last_id is not None and isinstance(inference_id, str) and inference_id < last_id:
            errors.append(f"{where}:ORDER")
        if isinstance(inference_id, str):
            last_id = inference_id
        if not is_int(entry.get("revision")) or entry["revision"] < 1:
            errors.append(f"{where}:revision:POSITIVE_INTEGER")
        if entry.get("status") not in STATUS:
            errors.append(f"{where}:status:ENUM")
        if not isinstance(entry.get("summary"), str):
            errors.append(f"{where}:summary:STRING")
        for key in ("technologies", "surfaces", "objectives", "signals"):
            string_array(entry.get(key), f"{where}.{key}", errors)
        locator = entry.get("locator")
        if not isinstance(locator, str) or not locator:
            errors.append(f"{where}:locator:NON_EMPTY_STRING")
        elif locator in locators:
            errors.append(f"{where}:DUPLICATE_LOCATOR:{locator}")
        else:
            locators.add(locator)
    return entries


def validate_record(record: Any, where: str, errors: list[str]) -> None:
    if not exact_keys(record, RECORD_KEYS, where, errors):
        return
    if record.get("schema_version") != 1:
        errors.append(f"{where}:schema_version")
    if not isinstance(record.get("inference_id"), str) or not record["inference_id"]:
        errors.append(f"{where}:inference_id")
    if not is_int(record.get("revision")) or record["revision"] < 1:
        errors.append(f"{where}:revision")
    if record.get("status") not in STATUS:
        errors.append(f"{where}:status")
    if not isinstance(record.get("statement"), str) or not record["statement"]:
        errors.append(f"{where}:statement")
    app_keys = {"technologies", "versions", "surfaces", "objectives", "signals", "exclusions"}
    if exact_keys(record.get("applicability"), app_keys, f"{where}.applicability", errors):
        for key in sorted(app_keys):
            string_array(record["applicability"].get(key), f"{where}.applicability.{key}", errors)
    inv_keys = {"demand_relation", "confirm_or_reject_evidence", "potential_impact", "cost", "stop_condition", "suggested_capabilities"}
    if exact_keys(record.get("investigation"), inv_keys, f"{where}.investigation", errors):
        for key in ("demand_relation", "potential_impact", "stop_condition"):
            if not isinstance(record["investigation"].get(key), str):
                errors.append(f"{where}.investigation:{key}:STRING")
        for key in ("confirm_or_reject_evidence", "suggested_capabilities"):
            string_array(record["investigation"].get(key), f"{where}.investigation.{key}", errors)
        if record["investigation"].get("cost") not in {"low", "medium", "high", "unknown", "unsupported"}:
            errors.append(f"{where}.investigation:cost:ENUM")
    prov_keys = {"source_refs", "accepted_evidence_refs", "freshness"}
    if exact_keys(record.get("provenance"), prov_keys, f"{where}.provenance", errors):
        string_array(record["provenance"].get("source_refs"), f"{where}.provenance.source_refs", errors)
        string_array(record["provenance"].get("accepted_evidence_refs"), f"{where}.provenance.accepted_evidence_refs", errors)
        if record["provenance"].get("freshness") not in FRESHNESS:
            errors.append(f"{where}.provenance:freshness:ENUM")
    lineage_keys = {"supersedes", "merged_from", "redirect_to", "tombstone"}
    if exact_keys(record.get("lineage"), lineage_keys, f"{where}.lineage", errors):
        string_array(record["lineage"].get("supersedes"), f"{where}.lineage.supersedes", errors)
        string_array(record["lineage"].get("merged_from"), f"{where}.lineage.merged_from", errors)
        redirect = record["lineage"].get("redirect_to")
        if redirect is not None and (not isinstance(redirect, str) or not redirect):
            errors.append(f"{where}.lineage:redirect_to")
        if record["lineage"].get("tombstone") is not None and not isinstance(record["lineage"]["tombstone"], dict):
            errors.append(f"{where}.lineage:tombstone")
    snapshot_keys = {"algorithm_version", "components", "score", "as_of_event", "freshness", "denominators"}
    snapshot = record.get("snapshot")
    if exact_keys(snapshot, snapshot_keys, f"{where}.snapshot", errors):
        if not isinstance(snapshot.get("algorithm_version"), str) or not snapshot["algorithm_version"]:
            errors.append(f"{where}.snapshot:algorithm_version")
        if exact_keys(snapshot.get("components"), COMPONENTS, f"{where}.snapshot.components", errors):
            for key in sorted(COMPONENTS):
                if not is_int(snapshot["components"].get(key)) or snapshot["components"][key] < 0:
                    errors.append(f"{where}.snapshot.components:{key}:NON_NEGATIVE_INTEGER")
        if not is_int(snapshot.get("score")):
            errors.append(f"{where}.snapshot:score:INTEGER")
        if snapshot.get("as_of_event") is not None and (not isinstance(snapshot["as_of_event"], str) or not snapshot["as_of_event"]):
            errors.append(f"{where}.snapshot:as_of_event")
        if snapshot.get("freshness") not in FRESHNESS:
            errors.append(f"{where}.snapshot:freshness:ENUM")
        if not isinstance(snapshot.get("denominators"), dict):
            errors.append(f"{where}.snapshot:denominators:OBJECT")


def resolve_locator(root: Path, locator: Any, where: str, errors: list[str]) -> Path | None:
    if not isinstance(locator, str) or not locator:
        return None
    candidate = Path(locator)
    if candidate.is_absolute():
        errors.append(f"{where}:LOCATOR_ABSOLUTE")
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{where}:LOCATOR_ESCAPE")
        return None
    if not resolved.is_file():
        errors.append(f"{where}:LOCATOR_MISSING")
        return None
    return resolved


def validate_lineage(records: dict[str, dict[str, Any]], errors: list[str]) -> None:
    ancestry: dict[str, set[str]] = {key: set() for key in records}
    redirects: dict[str, set[str]] = {key: set() for key in records}
    for inference_id, record in records.items():
        lineage = record.get("lineage")
        if not isinstance(lineage, dict):
            continue
        parent_refs = list(lineage.get("supersedes", [])) + list(lineage.get("merged_from", []))
        redirect = lineage.get("redirect_to")
        for target in parent_refs:
            if target not in records:
                errors.append(f"record:{inference_id}:LINEAGE_UNRESOLVED:{target}")
            elif target == inference_id:
                errors.append(f"record:{inference_id}:LINEAGE_SELF")
            else:
                ancestry[inference_id].add(target)
        if redirect is not None:
            if redirect not in records:
                errors.append(f"record:{inference_id}:LINEAGE_UNRESOLVED:{redirect}")
            elif redirect == inference_id:
                errors.append(f"record:{inference_id}:LINEAGE_SELF")
            else:
                redirects[inference_id].add(redirect)

    def check_cycle(graph: dict[str, set[str]], kind: str) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                errors.append(f"lineage:{kind}_CYCLE:{node}")
                return
            if node in visited:
                return
            visiting.add(node)
            for target in sorted(graph[node]):
                visit(target)
            visiting.remove(node)
            visited.add(node)

        for node in sorted(graph):
            visit(node)

    check_cycle(ancestry, "ANCESTRY")
    check_cycle(redirects, "REDIRECT")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path, help="catalog index JSON path")
    parser.add_argument("--policy", type=Path, default=Path(__file__).resolve().parents[1] / "references" / "policy-v1.json")
    args = parser.parse_args()
    errors: list[str] = []
    try:
        index = load_json(args.catalog)
        policy = load_json(args.policy)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "diagnostics": [f"INPUT:{exc}"]}, sort_keys=True, separators=(",", ":")))
        return 1
    values = validate_policy(policy, errors)
    entries = validate_index(index, errors)
    status_counts = {status: 0 for status in sorted(STATUS)}
    for entry in entries:
        if isinstance(entry, dict) and entry.get("status") in status_counts:
            status_counts[entry["status"]] += 1
    active_occupancy = status_counts["active"] + status_counts["protected"]
    active_limit = index.get("active_limit") if isinstance(index, dict) else None
    if values is not None and isinstance(index, dict) and is_int(index.get("active_limit")) and index["active_limit"] != values["catalog_limit"]:
        errors.append("index:active_limit:POLICY_MISMATCH")
    exceeds_index_limit = is_int(active_limit) and active_occupancy > active_limit
    exceeds_policy_limit = values is not None and active_occupancy > values["catalog_limit"]
    if exceeds_index_limit or exceeds_policy_limit:
        errors.append("catalog:ACTIVE_OCCUPANCY_EXCEEDS_LIMIT")
    records: dict[str, dict[str, Any]] = {}
    loaded: list[str] = []
    root = args.catalog.resolve().parent
    for position, entry in enumerate(entries):
        path = resolve_locator(root, entry.get("locator"), f"index.entries[{position}]", errors)
        if path is None:
            continue
        try:
            record = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"index.entries[{position}]:RECORD_READ:{exc}")
            continue
        validate_record(record, f"record:{entry.get('inference_id')}", errors)
        inference_id = record.get("inference_id") if isinstance(record, dict) else None
        if isinstance(inference_id, str):
            if inference_id in records:
                errors.append(f"record:DUPLICATE_ID:{inference_id}")
            records[inference_id] = record
        for key in ("inference_id", "revision", "status"):
            if isinstance(record, dict) and entry.get(key) != record.get(key):
                errors.append(f"index.entries[{position}]:PARITY:{key}")
        loaded.append(entry.get("locator", ""))
    if len(records) != len(entries):
        errors.append("catalog:INDEX_RECORD_PARITY")
    validate_lineage(records, errors)
    output = {
        "active_limit": active_limit,
        "active_occupancy": active_occupancy,
        "catalog_id": index.get("catalog_id") if isinstance(index, dict) else None,
        "diagnostics": sorted(set(errors)),
        "loaded_locators": loaded,
        "mutation_applied": False,
        "policy_digest": policy.get("approved_candidate_digest_sha256") if isinstance(policy, dict) else None,
        "policy_id": policy.get("policy_id") if isinstance(policy, dict) else None,
        "record_count": len(records),
        "status": "blocked" if errors else "valid",
        "status_counts": status_counts,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
