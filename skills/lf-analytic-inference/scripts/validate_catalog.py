#!/usr/bin/env python3
"""Validate an analytic-inference catalog without mutating it."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from manage_consumer_state import (
    StateError,
    _validate_lifecycle_event,
    assert_no_symlink_components,
    contained_path,
    load_json,
    require_event_derived_snapshot,
    require_segment,
    resolve_consumer_root,
    state_root_for,
    validate_registry,
)
from state_xml import StateXmlError, load_state


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


def load_live(path: Path, kind: str) -> dict[str, Any]:
    try:
        return load_state(path, kind)
    except (OSError, StateXmlError) as exc:
        diagnostic = exc.diagnostic if isinstance(exc, StateXmlError) else str(exc)
        raise StateError(f"STATE_XML_READ:{kind}:{diagnostic}") from exc


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
        "consumer_state_required": True,
        "package_catalog": False,
        "initial_consumer_catalog": "absent-or-empty",
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
        else:
            try:
                require_segment(index[key], f"index:{key}:PATH_SEGMENT")
            except StateError as exc:
                errors.append(exc.diagnostic)
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
        else:
            try:
                require_segment(inference_id, f"{where}:inference_id:PATH_SEGMENT")
            except StateError as exc:
                errors.append(exc.diagnostic)
            if inference_id in ids:
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
    try:
        return contained_path(root, locator, f"{where}:LOCATOR_CONTAINMENT", must_exist=True)
    except StateError as exc:
        errors.append(exc.diagnostic)
        return None


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
    parser.add_argument("--technology", action="append", default=[], help="validate only a registry technology or alias")
    parser.add_argument("--policy", type=Path, default=Path(__file__).resolve().parents[1] / "references" / "policy-v1.json")
    args = parser.parse_args()
    errors: list[str] = []
    try:
        consumer_root, resolution_source = resolve_consumer_root()
        state_root = state_root_for(consumer_root)
        policy = load_json(args.policy)
        registry_path = state_root / "registry.xml"
        assert_no_symlink_components(consumer_root, state_root)
        if not registry_path.exists() and not registry_path.is_symlink():
            output = {
                "consumer_root": str(consumer_root),
                "consumer_root_resolution_source": resolution_source,
                "diagnostics": [],
                "loaded_locators": [],
                "mutation_applied": False,
                "record_count": 0,
                "registry_state": "absent",
                "state_root": str(state_root),
                "status": "insufficient",
            }
            print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
            return 0
        assert_no_symlink_components(consumer_root, registry_path)
        registry = load_live(registry_path, "registry")
        registry_entries = validate_registry(registry)
    except (OSError, json.JSONDecodeError, StateError) as exc:
        diagnostic = exc.diagnostic if isinstance(exc, StateError) else f"INPUT:{exc}"
        print(json.dumps({"status": "blocked", "diagnostics": [diagnostic], "mutation_applied": False}, sort_keys=True, separators=(",", ":")))
        return 2
    values = validate_policy(policy, errors)
    requested = set(args.technology)
    for item in sorted(requested):
        try:
            require_segment(item, f"TECHNOLOGY_FILTER:{item}")
        except StateError as exc:
            errors.append(exc.diagnostic)
    selected_registry_entries = []
    for entry in registry_entries:
        names = {entry["technology"], *entry["aliases"]}
        if not requested or requested & names:
            selected_registry_entries.append(entry)
    unresolved = requested - {name for entry in registry_entries for name in [entry["technology"], *entry["aliases"]]}
    errors.extend(f"REGISTRY_TECHNOLOGY_UNRESOLVED:{item}" for item in sorted(unresolved))
    status_counts = {status: 0 for status in sorted(STATUS)}
    records: dict[str, dict[str, Any]] = {}
    loaded: list[str] = []
    catalog_ids: list[str] = []
    active_occupancy = 0
    active_limits: dict[str, Any] = {}
    catalog_occupancy: dict[str, int] = {}
    expected_record_count = 0
    for registry_position, registry_entry in enumerate(selected_registry_entries):
        index_path = resolve_locator(state_root, registry_entry["locator"], f"registry.entries[{registry_position}]", errors)
        if index_path is None:
            continue
        try:
            index = load_live(index_path, "catalog")
        except (OSError, StateError) as exc:
            errors.append(f"registry.entries[{registry_position}]:INDEX_READ:{exc}")
            continue
        entries = validate_index(index, errors)
        if isinstance(index, dict):
            for key in ("technology", "catalog_id", "aliases"):
                expected = registry_entry["technology" if key == "technology" else key]
                if index.get(key) != expected:
                    errors.append(f"registry.entries[{registry_position}]:INDEX_PARITY:{key}")
            active_limit = index.get("active_limit")
            active_limits[registry_entry["technology"]] = active_limit
            catalog_ids.append(index.get("catalog_id"))
            if values is not None and is_int(active_limit) and active_limit != values["catalog_limit"]:
                errors.append("index:active_limit:POLICY_MISMATCH")
        expected_record_count += len(entries)
        loaded.append(registry_entry["locator"])
        this_catalog_occupancy = 0
        for entry_position, entry in enumerate(entries):
            if isinstance(entry, dict) and entry.get("status") in status_counts:
                status_counts[entry["status"]] += 1
                if entry["status"] in {"active", "protected"}:
                    this_catalog_occupancy += 1
            expected_locator = f"catalogs/{registry_entry['technology']}/records/{entry.get('inference_id')}/rev-{entry.get('revision')}.xml"
            if entry.get("locator") != expected_locator:
                errors.append(f"index.entries[{entry_position}]:LOCATOR_LAYOUT")
            path = resolve_locator(state_root, entry.get("locator"), f"index.entries[{entry_position}]", errors)
            if path is None:
                continue
            try:
                record = load_live(path, "record")
            except (OSError, StateError) as exc:
                errors.append(f"index.entries[{entry_position}]:RECORD_READ:{exc}")
                continue
            validate_record(record, f"record:{entry.get('inference_id')}", errors)
            inference_id = record.get("inference_id") if isinstance(record, dict) else None
            if isinstance(inference_id, str):
                if inference_id in records:
                    errors.append(f"record:DUPLICATE_ID:{inference_id}")
                records[inference_id] = record
            for key in ("inference_id", "revision", "status"):
                if isinstance(record, dict) and entry.get(key) != record.get(key):
                    errors.append(f"index.entries[{entry_position}]:PARITY:{key}")
            loaded.append(entry.get("locator", ""))
            inference_id = entry.get("inference_id")
            events_dir = state_root / "events" / str(inference_id)
            try:
                assert_no_symlink_components(consumer_root, events_dir)
                if not events_dir.is_dir() or events_dir.is_symlink():
                    raise StateError(f"EVENTS_DIRECTORY_REQUIRED:{inference_id}")
                current_events: list[dict[str, Any]] = []
                for event_path in sorted(events_dir.iterdir()):
                    if event_path.is_symlink() or not event_path.is_file() or event_path.suffix != ".xml":
                        raise StateError(f"EVENT_TARGET_INVALID:{event_path.name}")
                    event = load_live(event_path, "event")
                    if event_path.name != f"{event.get('event_id')}.xml":
                        raise StateError(f"EVENT_LOCATOR_ID_MISMATCH:{event_path.name}")
                    event_entry = {**entry, "revision": event.get("inference_revision")}
                    _validate_lifecycle_event(event, event_entry)
                    if event.get("inference_revision") == entry.get("revision"):
                        current_events.append(event)
                    loaded.append(str(event_path.relative_to(state_root)))
                if values is not None and isinstance(record, dict):
                    require_event_derived_snapshot(
                        record,
                        current_events,
                        entry,
                        values,
                        f"SNAPSHOT_EVENT_DERIVATION_MISMATCH:{inference_id}",
                    )
            except (OSError, StateError) as exc:
                errors.append(exc.diagnostic if isinstance(exc, StateError) else f"EVENT_READ:{exc}")
        catalog_occupancy[registry_entry["technology"]] = this_catalog_occupancy
    active_occupancy = status_counts["active"] + status_counts["protected"]
    exceeds_index_limit = any(
        is_int(active_limits.get(technology)) and occupancy > active_limits[technology]
        for technology, occupancy in catalog_occupancy.items()
    )
    exceeds_policy_limit = any(
        values is not None and occupancy > values["catalog_limit"]
        for occupancy in catalog_occupancy.values()
    )
    if exceeds_index_limit or exceeds_policy_limit:
        errors.append("catalog:ACTIVE_OCCUPANCY_EXCEEDS_LIMIT")
    if len(records) != expected_record_count:
        errors.append("catalog:INDEX_RECORD_PARITY")
    validate_lineage(records, errors)
    output = {
        "active_limits": active_limits,
        "active_occupancy": active_occupancy,
        "catalog_ids": catalog_ids,
        "catalog_occupancy": catalog_occupancy,
        "catalog_state": "empty" if expected_record_count == 0 else "loaded",
        "consumer_root": str(consumer_root),
        "consumer_root_resolution_source": resolution_source,
        "diagnostics": sorted(set(errors)),
        "loaded_locators": loaded,
        "mutation_applied": False,
        "policy_digest": policy.get("approved_candidate_digest_sha256") if isinstance(policy, dict) else None,
        "policy_id": policy.get("policy_id") if isinstance(policy, dict) else None,
        "record_count": len(records),
        "registry_state": "empty" if not registry_entries else "loaded",
        "state_root": str(state_root),
        "status": "blocked" if errors else ("insufficient" if not registry_entries or not selected_registry_entries or expected_record_count == 0 else "valid"),
        "status_counts": status_counts,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
