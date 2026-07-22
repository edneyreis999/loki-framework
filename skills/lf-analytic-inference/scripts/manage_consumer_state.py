#!/usr/bin/env python3
"""Inspect and manage approved root-bound analytic-inference lifecycle state."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import stat
import sys
import tempfile
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
from typing import Any

from state_xml import StateXmlError, canonical_state, load_state


STATE_PARTS = (".loki", "analytic-inference", "v2")
SEGMENT = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
REGISTRY_KEYS = {"schema_version", "state_layout", "entries"}
REGISTRY_ENTRY_KEYS = {"technology", "aliases", "catalog_id", "locator"}
CATALOG_KEYS = {"schema_version", "catalog_id", "technology", "aliases", "active_limit", "entries"}
CATALOG_ENTRY_KEYS = {"inference_id", "revision", "status", "summary", "technologies", "surfaces", "objectives", "signals", "locator"}
RECORD_KEYS = {"schema_version", "inference_id", "revision", "status", "statement", "applicability", "investigation", "provenance", "lineage", "snapshot"}
EVENT_KEYS = {"schema_version", "event_id", "sequence", "source", "inference_id", "inference_revision", "stage", "outcome", "reason", "agent_capability", "cost"}
LIFECYCLE_REQUEST_KEYS = {"schema_version", "operation_id", "operation", "technology", "catalog_id", "policy_id", "policy_digest_sha256", "index_entry", "record", "events"}
APPROVAL_KEYS = {"schema_version", "approval_type", "status", "consumed", "issued_after_dry_run", "operation_id", "operation", "consumer_root", "policy_id", "policy_digest_sha256", "target_manifest_digest_sha256", "targets", "source_locator"}
STAGES = {"selected", "investigated", "validated", "rejected", "material-finding", "task-helped", "false-positive", "repeated-evidence", "stale"}
STAGE_COMPONENT = {
    "selected": "selected_count", "investigated": "investigated_count", "validated": "validated_count",
    "rejected": "rejected_count", "material-finding": "material_findings_count", "task-helped": "tasks_helped_count",
    "false-positive": "false_positive_count", "repeated-evidence": "repeated_evidence_count", "stale": "stale_count",
}
WEIGHT_COMPONENT = {
    "selected": "selected_count", "investigated": "investigated_count", "validated": "validated_count",
    "material_finding": "material_findings_count", "task_helped": "tasks_helped_count",
    "false_positive": "false_positive_count", "repeated_evidence": "repeated_evidence_count", "stale": "stale_count",
}
POLICY_PATH = Path(__file__).resolve().parents[1] / "references" / "policy-v1.json"


class StateError(Exception):
    """A fail-closed state or containment error."""

    def __init__(self, diagnostic: str):
        super().__init__(diagnostic)
        self.diagnostic = diagnostic


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def compact(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(compact(value)).hexdigest()


def digest_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def load_live_state(path: Path, kind: str) -> dict[str, Any]:
    """Load live state only through the strict canonical XML codec."""
    try:
        return load_state(path, kind)
    except (OSError, StateXmlError) as exc:
        diagnostic = exc.diagnostic if isinstance(exc, StateXmlError) else str(exc)
        raise StateError(f"STATE_XML_READ:{kind}:{diagnostic}") from exc


def live_payload(value: dict[str, Any], kind: str) -> bytes:
    """Encode live state only through the strict canonical XML codec."""
    try:
        return canonical_state(value, kind)
    except StateXmlError as exc:
        raise StateError(f"STATE_XML_ENCODE:{kind}:{exc.diagnostic}") from exc


def _canonical_existing_directory(path: Path, diagnostic: str) -> Path:
    try:
        if path.is_symlink() or not path.is_dir():
            raise StateError(diagnostic)
        return path.resolve(strict=True)
    except OSError as exc:
        raise StateError(f"{diagnostic}:{exc}") from exc


def resolve_consumer_root() -> tuple[Path, str]:
    """Resolve the consumer boundary from the command's canonical cwd."""
    return _canonical_existing_directory(Path.cwd(), "CONSUMER_ROOT_INVALID"), "canonical-pwd"


def state_root_for(consumer_root: Path) -> Path:
    return consumer_root.joinpath(*STATE_PARTS)


def reject_legacy_state_layout(consumer_root: Path) -> None:
    """Fail closed when the removed JSON v1 layout is present."""
    legacy_root = consumer_root / ".loki" / "analytic-inference" / "v1"
    if legacy_root.exists() or legacy_root.is_symlink():
        raise StateError("LEGACY_STATE_LAYOUT_UNSUPPORTED")


def require_segment(value: Any, diagnostic: str) -> str:
    if not isinstance(value, str) or SEGMENT.fullmatch(value) is None:
        raise StateError(diagnostic)
    return value


def _relative_parts(locator: Any, diagnostic: str) -> tuple[str, ...]:
    if not isinstance(locator, str) or not locator:
        raise StateError(diagnostic)
    path = Path(locator)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise StateError(diagnostic)
    return path.parts


def assert_no_symlink_components(root: Path, target: Path, *, include_target: bool = True) -> None:
    try:
        relative = target.relative_to(root)
    except ValueError as exc:
        raise StateError("ROOT_CONTAINMENT") from exc
    current = root
    parts = relative.parts if include_target else relative.parts[:-1]
    for part in parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise StateError(f"LSTAT_FAILED:{current}:{exc}") from exc
        if stat.S_ISLNK(mode):
            raise StateError(f"SYMLINK_COMPONENT:{current}")


def contained_path(state_root: Path, locator: Any, diagnostic: str, *, must_exist: bool) -> Path:
    parts = _relative_parts(locator, diagnostic)
    target = state_root.joinpath(*parts)
    assert_no_symlink_components(state_root.parent.parent.parent, target)
    try:
        resolved_parent = target.parent.resolve(strict=True)
        resolved = resolved_parent / target.name
        resolved.relative_to(state_root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise StateError(diagnostic) from exc
    if must_exist:
        try:
            mode = target.lstat().st_mode
        except OSError as exc:
            raise StateError(f"LOCATOR_MISSING:{locator}") from exc
        if not stat.S_ISREG(mode):
            raise StateError(f"LOCATOR_NOT_REGULAR:{locator}")
    return target


def contained_write_path(state_root: Path, locator: Any, diagnostic: str) -> Path:
    """Resolve an existing or future target without following a missing parent."""
    parts = _relative_parts(locator, diagnostic)
    target = state_root.joinpath(*parts)
    try:
        canonical_root = state_root.resolve(strict=True)
        target.relative_to(state_root)
    except (OSError, ValueError) as exc:
        raise StateError(diagnostic) from exc
    assert_no_symlink_components(state_root.parent.parent.parent, target)
    current = target.parent
    while not current.exists() and current != state_root:
        current = current.parent
    try:
        current.resolve(strict=True).relative_to(canonical_root)
    except (OSError, ValueError) as exc:
        raise StateError(diagnostic) from exc
    return target


def validate_registry(registry: Any) -> list[dict[str, Any]]:
    if not isinstance(registry, dict) or set(registry) != REGISTRY_KEYS:
        raise StateError("REGISTRY_KEYS")
    if registry.get("schema_version") != 2:
        raise StateError("REGISTRY_SCHEMA_VERSION")
    if registry.get("state_layout") != "analytic-inference-consumer-v2":
        raise StateError("REGISTRY_STATE_LAYOUT")
    entries = registry.get("entries")
    if not isinstance(entries, list):
        raise StateError("REGISTRY_ENTRIES_ARRAY")
    technologies: set[str] = set()
    names: set[str] = set()
    catalog_ids: set[str] = set()
    locators: set[str] = set()
    last_technology: str | None = None
    for position, entry in enumerate(entries):
        prefix = f"REGISTRY_ENTRY[{position}]"
        if not isinstance(entry, dict) or set(entry) != REGISTRY_ENTRY_KEYS:
            raise StateError(f"{prefix}:KEYS")
        technology = require_segment(entry.get("technology"), f"{prefix}:TECHNOLOGY")
        catalog_id = require_segment(entry.get("catalog_id"), f"{prefix}:CATALOG_ID")
        aliases = entry.get("aliases")
        if not isinstance(aliases, list):
            raise StateError(f"{prefix}:ALIASES_ARRAY")
        normalized_aliases = [require_segment(alias, f"{prefix}:ALIAS") for alias in aliases]
        if normalized_aliases != sorted(normalized_aliases) or len(normalized_aliases) != len(set(normalized_aliases)):
            raise StateError(f"{prefix}:ALIASES_ORDER_OR_DUPLICATE")
        locator = entry.get("locator")
        expected_locator = f"catalogs/{technology}/index.xml"
        if locator != expected_locator:
            raise StateError(f"{prefix}:LOCATOR_LAYOUT")
        if last_technology is not None and technology <= last_technology:
            raise StateError("REGISTRY_ORDER_OR_DUPLICATE")
        last_technology = technology
        if technology in technologies or catalog_id in catalog_ids or locator in locators:
            raise StateError(f"{prefix}:IDENTITY_DUPLICATE")
        technologies.add(technology)
        catalog_ids.add(catalog_id)
        locators.add(locator)
        for name in [technology, *normalized_aliases]:
            if name in names:
                raise StateError(f"{prefix}:NAME_DUPLICATE:{name}")
            names.add(name)
    return entries


def registry_document(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "state_layout": "analytic-inference-consumer-v2",
        "entries": sorted(entries, key=lambda item: item["technology"]),
    }


def catalog_document(technology: str, catalog_id: str, aliases: list[str], active_limit: int) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "catalog_id": catalog_id,
        "technology": technology,
        "aliases": aliases,
        "active_limit": active_limit,
        "entries": [],
    }


def _ensure_directory_chain(consumer_root: Path, target: Path) -> None:
    assert_no_symlink_components(consumer_root, target)
    current = consumer_root
    for part in target.relative_to(consumer_root).parts:
        current = current / part
        try:
            current.mkdir()
        except FileExistsError:
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise StateError(f"DIRECTORY_COLLISION:{current}")


def _assert_root_identity(consumer_root: Path, expected_identity: tuple[int, int]) -> None:
    try:
        observed = (consumer_root.stat().st_dev, consumer_root.stat().st_ino)
        resolved = consumer_root.resolve(strict=True)
    except OSError as exc:
        raise StateError(f"ROOT_DRIFT:{exc}") from exc
    if observed != expected_identity or resolved != consumer_root:
        raise StateError("ROOT_DRIFT")


def _atomic_publish(
    path: Path,
    payload: bytes,
    staging: Path,
    consumer_root: Path,
    root_identity: tuple[int, int],
    kind: str,
) -> bool:
    _assert_root_identity(consumer_root, root_identity)
    if path.exists() or path.is_symlink():
        assert_no_symlink_components(staging.parent.parent, path)
        try:
            load_live_state(path, kind)
            observed = path.read_bytes()
        except (OSError, StateError) as exc:
            raise StateError(f"COLLISION_READ:{path}:{exc}") from exc
        if observed == payload:
            return False
        raise StateError(f"DIVERGENT_COLLISION:{path}")
    fd, temporary_name = tempfile.mkstemp(prefix="publish-", suffix=".xml", dir=staging)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        assert_no_symlink_components(staging.parent.parent, path, include_target=False)
        _assert_root_identity(consumer_root, root_identity)
        if path.exists() or path.is_symlink():
            raise StateError(f"TARGET_DRIFT:{path}")
        os.replace(temporary_name, path)
        return True
    finally:
        try:
            Path(temporary_name).unlink()
        except FileNotFoundError:
            pass


def _bootstrap_locked(
    consumer_root: Path,
    technology: str,
    catalog_id: str,
    aliases: list[str],
    active_limit: int,
    *,
    fail_before_registry: bool = False,
) -> dict[str, Any]:
    """Apply bootstrap while the caller holds the consumer writer lock."""
    technology = require_segment(technology, "TECHNOLOGY_ID")
    catalog_id = require_segment(catalog_id, "CATALOG_ID")
    aliases = sorted(require_segment(alias, "ALIAS_ID") for alias in aliases)
    if len(aliases) != len(set(aliases)) or technology in aliases:
        raise StateError("ALIAS_DUPLICATE")
    if isinstance(active_limit, bool) or not isinstance(active_limit, int) or active_limit < 0:
        raise StateError("ACTIVE_LIMIT")
    if active_limit != 3:
        raise StateError("ACTIVE_LIMIT_POLICY_MISMATCH")
    original_identity = (consumer_root.stat().st_dev, consumer_root.stat().st_ino)
    state_root = state_root_for(consumer_root)
    _ensure_directory_chain(consumer_root, state_root)
    assert_no_symlink_components(consumer_root, state_root)
    registry_path = state_root / "registry.xml"
    existing_entries: list[dict[str, Any]] = []
    if registry_path.exists() or registry_path.is_symlink():
        assert_no_symlink_components(consumer_root, registry_path)
        try:
            existing_entries = validate_registry(load_live_state(registry_path, "registry"))
        except (OSError, StateError) as exc:
            raise StateError(f"REGISTRY_READ:{exc}") from exc
    desired_entry = {
        "technology": technology,
        "aliases": aliases,
        "catalog_id": catalog_id,
        "locator": f"catalogs/{technology}/index.xml",
    }
    same_technology = [entry for entry in existing_entries if entry["technology"] == technology]
    if same_technology and same_technology[0] != desired_entry:
        raise StateError("DIVERGENT_REGISTRY_IDENTITY")
    if not same_technology:
        if existing_entries:
            raise StateError("STATE_ALREADY_LOADED")
        candidate_entries = [*existing_entries, desired_entry]
    else:
        candidate_entries = existing_entries
    desired_registry = registry_document(candidate_entries)
    validate_registry(desired_registry)
    desired_catalog = catalog_document(technology, catalog_id, aliases, active_limit)
    catalog_path = state_root / desired_entry["locator"]
    _ensure_directory_chain(consumer_root, catalog_path.parent)
    staging = Path(tempfile.mkdtemp(prefix=".bootstrap-", dir=consumer_root / ".loki"))
    published: list[str] = []
    try:
        if _atomic_publish(catalog_path, live_payload(desired_catalog, "catalog"), staging, consumer_root, original_identity, "catalog"):
            published.append(desired_entry["locator"])
        if fail_before_registry:
            return {
                "consumer_root": str(consumer_root),
                "diagnostics": ["INJECTED_FAILURE_BEFORE_REGISTRY"],
                "mutation_applied": bool(published),
                "published": [],
                "registry_state": "absent" if not registry_path.exists() else ("empty" if not existing_entries else "loaded"),
                "staging_residue": published,
                "state_root": str(state_root),
                "status": "blocked",
                "technology": technology,
            }
        _assert_root_identity(consumer_root, original_identity)
        registry_payload = live_payload(desired_registry, "registry")
        if registry_path.exists():
            load_live_state(registry_path, "registry")
            observed = registry_path.read_bytes()
            if observed != registry_payload:
                fd, temporary_name = tempfile.mkstemp(prefix="registry-", suffix=".xml", dir=staging)
                try:
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(registry_payload)
                        stream.flush()
                        os.fsync(stream.fileno())
                    assert_no_symlink_components(consumer_root, registry_path)
                    _assert_root_identity(consumer_root, original_identity)
                    load_live_state(registry_path, "registry")
                    if registry_path.read_bytes() != observed:
                        raise StateError("REGISTRY_DRIFT")
                    os.replace(temporary_name, registry_path)
                    published.append("registry.xml")
                finally:
                    try:
                        Path(temporary_name).unlink()
                    except FileNotFoundError:
                        pass
        elif _atomic_publish(registry_path, registry_payload, staging, consumer_root, original_identity, "registry"):
            published.append("registry.xml")
    finally:
        try:
            staging.rmdir()
        except OSError:
            pass
    return {
        "consumer_root": str(consumer_root),
        "state_root": str(state_root),
        "registry_state": "loaded",
        "technology": technology,
        "published": published,
        "mutation_applied": bool(published),
        "status": "success",
    }


def inspect(consumer_root: Path) -> dict[str, Any]:
    state_root = state_root_for(consumer_root)
    registry_path = state_root / "registry.xml"
    assert_no_symlink_components(consumer_root, state_root)
    if not registry_path.exists() and not registry_path.is_symlink():
        return {
            "consumer_root": str(consumer_root),
            "diagnostics": [],
            "loaded_locators": [],
            "mutation_applied": False,
            "operation": "inspect",
            "registry_state": "absent",
            "state_root": str(state_root),
            "status": "insufficient",
        }
    assert_no_symlink_components(consumer_root, registry_path)
    entries = validate_registry(load_live_state(registry_path, "registry"))
    return {
        "consumer_root": str(consumer_root),
        "diagnostics": [],
        "loaded_locators": ["registry.xml"],
        "mutation_applied": False,
        "operation": "inspect",
        "registry_state": "empty" if not entries else "loaded",
        "state_root": str(state_root),
        "status": "insufficient" if not entries else "success",
    }


def _exact_object(value: Any, keys: set[str], diagnostic: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise StateError(diagnostic)
    return value


def _string_array(value: Any, diagnostic: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise StateError(diagnostic)
    if value != sorted(value) or len(value) != len(set(value)):
        raise StateError(f"{diagnostic}:ORDER_OR_DUPLICATE")
    return value


def _policy_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_policy_object(raw: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    policy = _exact_object(
        raw,
        {"schema_version", "policy_id", "status", "approved_candidate_digest_sha256", "approved_candidate", "semantics"},
        "POLICY_KEYS",
    )
    if policy["schema_version"] != "1" or policy["policy_id"] != "analytic-inference-policy-v1" or policy["status"] != "active":
        raise StateError("POLICY_IDENTITY")
    candidate = _exact_object(policy.get("approved_candidate"), {"candidate_id", "policy_source", "schema_version", "status", "values"}, "POLICY_CANDIDATE_KEYS")
    if candidate.get("candidate_id") != "analytic-inference-policy-v1-candidate-001" or candidate.get("policy_source") != "PC-BALANCED" or candidate.get("schema_version") != "1" or candidate.get("status") != "proposed":
        raise StateError("POLICY_CANDIDATE_IDENTITY")
    if digest_value(candidate) != policy["approved_candidate_digest_sha256"]:
        raise StateError("POLICY_DIGEST_MISMATCH")
    value_keys = {"candidate_ceiling", "catalog_retrieval_page_size", "concurrent_handoff_limit", "handoff_timeout_ticks", "max_delegated_investigations_per_round", "max_investigation_rounds", "minimum_candidate_floor", "persistent_catalog_limit", "promotion_min", "purge_review_max", "removals_per_cycle", "reorganization_max", "score_weights"}
    values = _exact_object(candidate.get("values"), value_keys, "POLICY_VALUE_KEYS")
    if values["candidate_ceiling"] is not None:
        raise StateError("POLICY_CANDIDATE_CEILING")
    positive_keys = {"catalog_retrieval_page_size", "concurrent_handoff_limit", "handoff_timeout_ticks", "max_delegated_investigations_per_round", "max_investigation_rounds", "minimum_candidate_floor", "persistent_catalog_limit", "removals_per_cycle"}
    if any(not _policy_int(values[key]) or values[key] <= 0 for key in positive_keys):
        raise StateError("POLICY_POSITIVE_INTEGER")
    if values["concurrent_handoff_limit"] > values["max_delegated_investigations_per_round"]:
        raise StateError("POLICY_CONCURRENCY_EXCEEDS_ROUND_CAPACITY")
    if any(not _policy_int(values[key]) for key in ("promotion_min", "purge_review_max", "reorganization_max")):
        raise StateError("POLICY_THRESHOLD_INTEGER")
    weights = _exact_object(values["score_weights"], set(WEIGHT_COMPONENT), "POLICY_WEIGHT_KEYS")
    if any(not _policy_int(weight) for weight in weights.values()) or weights["selected"] != 0:
        raise StateError("POLICY_WEIGHTS")
    expected = {
        "automatic_mutation": False,
        "consumer_state_required": True,
        "package_catalog": False,
        "purge_requires_independent_just_in_time_approval": True,
        "score_is_eligibility_only": True,
        "thresholds_are_inclusive": True,
        "candidate_floor_is_non_terminal": True,
        "cost_is_telemetry_only": True,
        "retrieval_page_size_is_not_total_limit": True,
        "persistent_catalog_limit_is_storage_only": True,
        "semantic_saturation_ends_generation": True,
        "approved_candidate_status_is_identity_bound": True,
        "initial_consumer_catalog": "absent-or-empty",
    }
    semantics = policy.get("semantics")
    if not isinstance(semantics, dict) or set(semantics) != set(expected) or any(semantics.get(key) != value for key, value in expected.items()):
        raise StateError("POLICY_SEMANTICS_WEAKENED")
    return policy, values


def load_policy(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    return validate_policy_object(load_json(path))


def strict_policy_self_test(path: Path) -> None:
    policy = load_json(path)
    validate_policy_object(policy)
    invalid = json.loads(json.dumps(policy))
    invalid["approved_candidate"]["values"]["candidate_ceiling"] = 1
    invalid["approved_candidate_digest_sha256"] = digest_value(invalid["approved_candidate"])
    try:
        validate_policy_object(invalid)
    except StateError as exc:
        if exc.diagnostic != "POLICY_CANDIDATE_CEILING":
            raise StateError(f"POLICY_SELF_TEST_WRONG_DIAGNOSTIC:{exc.diagnostic}") from exc
    else:
        raise StateError("POLICY_SELF_TEST_ACCEPTED_NON_NULL_CEILING")


def classify_eligibility(score: int, protected: bool, values: dict[str, Any]) -> dict[str, bool]:
    return {
        "promotion": score >= values["promotion_min"],
        "reorganization": score <= values["reorganization_max"],
        "purge_review": (not protected) and score <= values["purge_review_max"],
    }


def _load_catalog(consumer_root: Path, technology: str, catalog_id: str) -> tuple[Path, dict[str, Any]]:
    state_root = state_root_for(consumer_root)
    registry_path = state_root / "registry.xml"
    if not registry_path.exists() and not registry_path.is_symlink():
        raise StateError("REGISTRY_ABSENT")
    registry = validate_registry(load_live_state(contained_path(state_root, "registry.xml", "REGISTRY_LOCATOR", must_exist=True), "registry"))
    matches = [item for item in registry if technology in [item["technology"], *item["aliases"]]]
    if len(matches) != 1:
        raise StateError("TECHNOLOGY_REGISTRY_MATCH")
    registry_entry = matches[0]
    if registry_entry["technology"] != technology or registry_entry["catalog_id"] != catalog_id:
        raise StateError("CATALOG_IDENTITY_MISMATCH")
    catalog_path = contained_path(state_root, registry_entry["locator"], "CATALOG_LOCATOR", must_exist=True)
    catalog = _exact_object(load_live_state(catalog_path, "catalog"), CATALOG_KEYS, "CATALOG_KEYS")
    if catalog.get("schema_version") != 1 or catalog.get("technology") != technology or catalog.get("catalog_id") != catalog_id:
        raise StateError("CATALOG_IDENTITY_MISMATCH")
    if catalog.get("active_limit") != 3:
        raise StateError("ACTIVE_LIMIT_POLICY_MISMATCH")
    if not isinstance(catalog.get("entries"), list):
        raise StateError("CATALOG_ENTRIES")
    return catalog_path, catalog


def _validate_catalog_entry(entry: Any, technology: str, record: dict[str, Any]) -> dict[str, Any]:
    entry = _exact_object(entry, CATALOG_ENTRY_KEYS, "INDEX_ENTRY_KEYS")
    inference_id = require_segment(entry.get("inference_id"), "INFERENCE_ID")
    revision = entry.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise StateError("INFERENCE_REVISION")
    if entry.get("status") not in {"active", "protected", "redirect", "tombstone"}:
        raise StateError("INDEX_ENTRY_STATUS")
    for key in ("technologies", "surfaces", "objectives", "signals"):
        _string_array(entry.get(key), f"INDEX_ENTRY_{key.upper()}")
    if technology not in entry["technologies"]:
        raise StateError("INDEX_ENTRY_TECHNOLOGY")
    expected_locator = f"catalogs/{technology}/records/{inference_id}/rev-{revision}.xml"
    if entry.get("locator") != expected_locator:
        raise StateError("INDEX_ENTRY_LOCATOR")
    if record.get("inference_id") != inference_id or record.get("revision") != revision or record.get("status") != entry.get("status"):
        raise StateError("INDEX_RECORD_PARITY")
    return entry


def _validate_record(record: Any) -> dict[str, Any]:
    record = _exact_object(record, RECORD_KEYS, "RECORD_KEYS")
    if record.get("schema_version") != 1:
        raise StateError("RECORD_SCHEMA_VERSION")
    require_segment(record.get("inference_id"), "RECORD_INFERENCE_ID")
    if isinstance(record.get("revision"), bool) or not isinstance(record.get("revision"), int) or record["revision"] < 1:
        raise StateError("RECORD_REVISION")
    if not isinstance(record.get("statement"), str) or not record["statement"]:
        raise StateError("RECORD_STATEMENT")
    applicability = _exact_object(record.get("applicability"), {"technologies", "versions", "surfaces", "objectives", "signals", "exclusions"}, "RECORD_APPLICABILITY_KEYS")
    for key in sorted(applicability):
        _string_array(applicability[key], f"RECORD_APPLICABILITY_{key.upper()}")
    investigation = _exact_object(record.get("investigation"), {"demand_relation", "confirm_or_reject_evidence", "potential_impact", "cost", "stop_condition", "suggested_capabilities"}, "RECORD_INVESTIGATION_KEYS")
    for key in ("demand_relation", "potential_impact", "stop_condition"):
        if not isinstance(investigation.get(key), str):
            raise StateError(f"RECORD_INVESTIGATION_{key.upper()}")
    for key in ("confirm_or_reject_evidence", "suggested_capabilities"):
        _string_array(investigation.get(key), f"RECORD_INVESTIGATION_{key.upper()}")
    provenance = _exact_object(record.get("provenance"), {"source_refs", "accepted_evidence_refs", "freshness"}, "RECORD_PROVENANCE_KEYS")
    for key in ("source_refs", "accepted_evidence_refs"):
        _string_array(provenance.get(key), f"RECORD_PROVENANCE_{key.upper()}")
    lineage = _exact_object(record.get("lineage"), {"supersedes", "merged_from", "redirect_to", "tombstone"}, "RECORD_LINEAGE_KEYS")
    for key in ("supersedes", "merged_from"):
        _string_array(lineage.get(key), f"RECORD_LINEAGE_{key.upper()}")
    snapshot = record.get("snapshot")
    snapshot = _exact_object(snapshot, {"algorithm_version", "components", "score", "as_of_event", "freshness", "denominators"}, "RECORD_SNAPSHOT_KEYS")
    if isinstance(snapshot.get("score"), bool) or not isinstance(snapshot.get("score"), int):
        raise StateError("RECORD_SNAPSHOT_SCORE")
    if set(snapshot.get("components", {})) != set(STAGE_COMPONENT.values()) or not all(isinstance(value, int) and not isinstance(value, bool) and value >= 0 for value in snapshot["components"].values()):
        raise StateError("RECORD_SNAPSHOT_COMPONENTS")
    if not isinstance(snapshot.get("denominators"), dict):
        raise StateError("RECORD_SNAPSHOT_DENOMINATORS")
    return record


def _validate_lifecycle_event(event: Any, entry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise StateError("LIFECYCLE_EVENT_OBJECT")
    required = EVENT_KEYS - {"sequence"}
    if not required.issubset(event) or not set(event).issubset(EVENT_KEYS):
        raise StateError("LIFECYCLE_EVENT_KEYS")
    if event.get("schema_version") != 1:
        raise StateError("LIFECYCLE_EVENT_SCHEMA_VERSION")
    event_id = require_segment(event.get("event_id"), "LIFECYCLE_EVENT_ID")
    revision = event.get("inference_revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise StateError("LIFECYCLE_EVENT_INFERENCE_REVISION")
    if event.get("inference_id") != entry["inference_id"] or event.get("inference_revision") != entry["revision"]:
        raise StateError("EVENT_RECORD_PARITY")
    if "sequence" in event and (isinstance(event["sequence"], bool) or not isinstance(event["sequence"], int) or event["sequence"] < 0):
        raise StateError("LIFECYCLE_EVENT_SEQUENCE")
    if event.get("stage") not in STAGES:
        raise StateError("LIFECYCLE_EVENT_STAGE")
    if "outcome" not in event:
        raise StateError("LIFECYCLE_EVENT_OUTCOME")
    for key in ("reason", "agent_capability"):
        if not isinstance(event.get(key), str) or not event[key]:
            raise StateError(f"LIFECYCLE_EVENT_{key.upper()}")
    source = event.get("source")
    if not isinstance(source, dict) or set(source) != {"analysis_ref", "run_id", "handoff_id", "evidence_refs"}:
        raise StateError("LIFECYCLE_EVENT_SOURCE")
    evidence_refs = source.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not all(isinstance(item, str) and item for item in evidence_refs) or len(evidence_refs) != len(set(evidence_refs)):
        raise StateError("LIFECYCLE_EVENT_EVIDENCE_REFS")
    for key in ("analysis_ref", "run_id", "handoff_id"):
        if not isinstance(source.get(key), str) or not source[key]:
            raise StateError(f"LIFECYCLE_EVENT_SOURCE_{key.upper()}")
    cost = event.get("cost")
    if not isinstance(cost, dict) or set(cost) != {"context", "tools"}:
        raise StateError("LIFECYCLE_EVENT_COST")
    for value in cost.values():
        numeric = isinstance(value, (int, float, Decimal)) and not isinstance(value, bool)
        finite = value.is_finite() if isinstance(value, Decimal) else (math.isfinite(value) if numeric else False)
        if not ((numeric and finite and value >= 0) or value in {"unknown", "unsupported"}):
            raise StateError("LIFECYCLE_EVENT_COST_VALUE")
    return event


def reduce_events(events: list[dict[str, Any]], entry: dict[str, Any], values: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    validated = [_validate_lifecycle_event(event, entry) for event in events]
    has_sequence = ["sequence" in event for event in validated]
    if any(has_sequence) and not all(has_sequence):
        raise StateError("AMBIGUOUS_EVENT_ORDER")
    identities: dict[str, bytes] = {}
    unique: dict[str, dict[str, Any]] = {}
    replayed: list[str] = []
    for event in validated:
        payload = live_payload(event, "event")
        event_id = event["event_id"]
        if event_id in identities:
            if identities[event_id] != payload:
                raise StateError(f"EVENT_ID_PAYLOAD_CONFLICT:{event_id}")
            replayed.append(event_id)
            continue
        identities[event_id] = payload
        unique[event_id] = event
    order = sorted(unique.values(), key=(lambda item: (item["sequence"], item["event_id"])) if validated and all(has_sequence) else (lambda item: item["event_id"]))
    components = {key: 0 for key in sorted(set(STAGE_COMPONENT.values()))}
    for event in order:
        components[STAGE_COMPONENT[event["stage"]]] += 1
    score = sum(components[component] * values["score_weights"][weight] for weight, component in WEIGHT_COMPONENT.items())
    snapshot = {
        "algorithm_version": "analytic-inference-policy-v1",
        "components": components,
        "score": score,
        "as_of_event": order[-1]["event_id"] if order else None,
        "freshness": "stale" if components["stale_count"] else "current",
        "denominators": {"unique_events": len(order)},
    }
    return order, snapshot, replayed


def require_event_derived_snapshot(record: dict[str, Any], events: list[dict[str, Any]], entry: dict[str, Any], values: dict[str, Any], diagnostic: str) -> tuple[list[dict[str, Any]], list[str]]:
    ordered, snapshot, replayed = reduce_events(events, entry, values)
    if record["snapshot"] != snapshot:
        raise StateError(diagnostic)
    return ordered, replayed


def _validate_lifecycle_request(request: Any, policy: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    request = _exact_object(request, LIFECYCLE_REQUEST_KEYS, "LIFECYCLE_REQUEST_KEYS")
    if request.get("schema_version") != 2:
        raise StateError("LIFECYCLE_SCHEMA_VERSION")
    require_segment(request.get("operation_id"), "OPERATION_ID")
    operation = request.get("operation")
    if operation not in {"promotion", "reorganization"}:
        raise StateError("LIFECYCLE_OPERATION")
    technology = require_segment(request.get("technology"), "TECHNOLOGY_ID")
    require_segment(request.get("catalog_id"), "CATALOG_ID")
    if request.get("policy_id") != policy["policy_id"] or request.get("policy_digest_sha256") != policy["approved_candidate_digest_sha256"]:
        raise StateError("POLICY_BINDING_MISMATCH")
    record = _validate_record(request.get("record"))
    entry = _validate_catalog_entry(request.get("index_entry"), technology, record)
    status = entry["status"]
    lineage = record["lineage"]
    if operation == "promotion" and status not in {"active", "protected"}:
        raise StateError("PROMOTION_STATUS")
    if operation == "reorganization":
        if status not in {"redirect", "tombstone"}:
            raise StateError("REORGANIZATION_STATUS")
        if status == "redirect" and lineage["redirect_to"] is None:
            raise StateError("REORGANIZATION_REDIRECT_REQUIRED")
        if status == "tombstone" and not isinstance(lineage["tombstone"], dict):
            raise StateError("REORGANIZATION_TOMBSTONE_REQUIRED")
    events = request.get("events")
    if not isinstance(events, list) or not events:
        raise StateError("LIFECYCLE_EVENTS_REQUIRED")
    _, _ = require_event_derived_snapshot(record, events, entry, values, "SNAPSHOT_EVENT_DERIVATION_MISMATCH")
    eligibility = classify_eligibility(record["snapshot"]["score"], status == "protected", values)
    if operation == "promotion" and not eligibility["promotion"]:
        raise StateError("PROMOTION_NOT_ELIGIBLE")
    if operation == "reorganization" and not eligibility["reorganization"]:
        raise StateError("REORGANIZATION_NOT_ELIGIBLE")
    return request


def _before_hash(path: Path) -> str | None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file():
            raise StateError(f"TARGET_NOT_REGULAR:{path}")
        return digest_file(path)
    return None


def _validate_proposed_lineage(state_root: Path, technology: str, proposed_entries: list[dict[str, Any]], proposed_record: dict[str, Any]) -> None:
    records: dict[str, dict[str, Any]] = {}
    proposed_id = proposed_record["inference_id"]
    for entry in proposed_entries:
        inference_id = entry["inference_id"]
        if inference_id == proposed_id:
            records[inference_id] = proposed_record
        else:
            record_path = contained_path(state_root, entry["locator"], "LINEAGE_RECORD_LOCATOR", must_exist=True)
            existing_record = _validate_record(load_live_state(record_path, "record"))
            _validate_catalog_entry(entry, technology, existing_record)
            records[inference_id] = existing_record
    ancestry: dict[str, set[str]] = {item: set() for item in records}
    redirects: dict[str, set[str]] = {item: set() for item in records}
    for inference_id, record in records.items():
        lineage = record["lineage"]
        for parent in [*lineage["supersedes"], *lineage["merged_from"]]:
            if parent not in records:
                raise StateError(f"LINEAGE_UNRESOLVED:{parent}")
            if parent == inference_id:
                raise StateError(f"LINEAGE_SELF:{inference_id}")
            ancestry[inference_id].add(parent)
        redirect = lineage["redirect_to"]
        if redirect is not None:
            if redirect not in records:
                raise StateError(f"LINEAGE_UNRESOLVED:{redirect}")
            if redirect == inference_id:
                raise StateError(f"LINEAGE_SELF:{inference_id}")
            redirects[inference_id].add(redirect)

    def reject_cycle(graph: dict[str, set[str]], kind: str) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise StateError(f"LINEAGE_{kind}_CYCLE:{node}")
            if node in visited:
                return
            visiting.add(node)
            for target in sorted(graph[node]):
                visit(target)
            visiting.remove(node)
            visited.add(node)

        for node in sorted(graph):
            visit(node)

    reject_cycle(ancestry, "ANCESTRY")
    reject_cycle(redirects, "REDIRECT")


def _state_target_path(consumer_root: Path, locator: str) -> Path:
    parts = _relative_parts(locator, "LIFECYCLE_TARGET")
    state_root = state_root_for(consumer_root)
    target = state_root.joinpath(*parts)
    assert_no_symlink_components(consumer_root, target)
    current = target.parent
    while not current.exists() and current != consumer_root:
        current = current.parent
    try:
        current.resolve(strict=True).relative_to(consumer_root)
    except (OSError, ValueError) as exc:
        raise StateError("LIFECYCLE_TARGET") from exc
    return target


def _lifecycle_base(consumer_root: Path, technology: str, catalog_id: str, values: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], str | None]:
    state_root = state_root_for(consumer_root)
    registry_path = state_root / "registry.xml"
    if registry_path.exists() or registry_path.is_symlink():
        registry_entries = validate_registry(load_live_state(contained_path(state_root, "registry.xml", "REGISTRY_LOCATOR", must_exist=True), "registry"))
    else:
        assert_no_symlink_components(consumer_root, state_root)
        registry_entries = []
    matches = [item for item in registry_entries if technology in [item["technology"], *item["aliases"]]]
    if len(matches) > 1:
        raise StateError("TECHNOLOGY_REGISTRY_MATCH")
    if matches:
        registry_entry = matches[0]
        if registry_entry["technology"] != technology or registry_entry["catalog_id"] != catalog_id:
            raise StateError("CATALOG_IDENTITY_MISMATCH")
        catalog_path = contained_path(state_root, registry_entry["locator"], "CATALOG_LOCATOR", must_exist=True)
        catalog = _exact_object(load_live_state(catalog_path, "catalog"), CATALOG_KEYS, "CATALOG_KEYS")
        catalog_before = digest_file(catalog_path)
    else:
        registry_entry = {"technology": technology, "aliases": [], "catalog_id": catalog_id, "locator": f"catalogs/{technology}/index.xml"}
        registry_entries = [*registry_entries, registry_entry]
        catalog = catalog_document(technology, catalog_id, [], values["persistent_catalog_limit"])
        catalog_before = None
    registry_entries = sorted(registry_entries, key=lambda item: item["technology"])
    validate_registry(registry_document(registry_entries))
    if catalog.get("schema_version") != 1 or catalog.get("technology") != technology or catalog.get("catalog_id") != catalog_id:
        raise StateError("CATALOG_IDENTITY_MISMATCH")
    if catalog.get("active_limit") != values["persistent_catalog_limit"]:
        raise StateError("ACTIVE_LIMIT_POLICY_MISMATCH")
    if not isinstance(catalog.get("entries"), list):
        raise StateError("CATALOG_ENTRIES")
    return registry_entries, catalog, catalog_before


def lifecycle_proposal(consumer_root: Path, source: str, request_path: Path, policy_path: Path) -> dict[str, Any]:
    policy, values = load_policy(policy_path)
    request = _validate_lifecycle_request(load_json(request_path), policy, values)
    technology = request["technology"]
    registry_entries, catalog, catalog_before = _lifecycle_base(consumer_root, technology, request["catalog_id"], values)
    entry = request["index_entry"]
    record = request["record"]
    entries = catalog["entries"]
    _load_validated_catalog_records(state_root_for(consumer_root), technology, catalog, values)
    prior = [item for item in entries if item["inference_id"] == entry["inference_id"]]
    if prior and prior[0]["revision"] > entry["revision"]:
        raise StateError("REVISION_REGRESSION")
    proposed_entries = sorted([item for item in entries if item["inference_id"] != entry["inference_id"]] + [entry], key=lambda item: item["inference_id"])
    active_occupancy = sum(item.get("status") in {"active", "protected"} for item in proposed_entries)
    if active_occupancy > values["persistent_catalog_limit"] or active_occupancy > catalog["active_limit"]:
        raise StateError("CATALOG_ACTIVE_LIMIT_EXCEEDED")
    state_root = state_root_for(consumer_root)
    _validate_proposed_lineage(state_root, technology, proposed_entries, record)
    proposed_catalog = {**catalog, "entries": proposed_entries}
    payloads: list[tuple[str, str, bytes]] = [("record", entry["locator"], live_payload(record, "record"))]
    ordered_events, _, replayed = reduce_events(request["events"], entry, values)
    for event in ordered_events:
        locator = f"events/{entry['inference_id']}/{event['event_id']}.xml"
        payloads.append(("event", locator, live_payload(event, "event")))
    targets: list[dict[str, Any]] = []
    immutable_observed = True
    for kind, locator, payload in payloads:
        path = _state_target_path(consumer_root, locator)
        before = _before_hash(path)
        after = hashlib.sha256(payload).hexdigest()
        if before is not None and before != after:
            raise StateError(f"DIVERGENT_IMMUTABLE_COLLISION:{locator}")
        immutable_observed = immutable_observed and before == after
        targets.append({"artifact_kind": kind, "locator": locator, "before_sha256": None, "payload_sha256": after})
    catalog_locator = f"catalogs/{technology}/index.xml"
    targets.append({
        "artifact_kind": "technology-index",
        "locator": catalog_locator,
        "before_sha256": catalog_before,
        "payload_sha256": hashlib.sha256(live_payload(proposed_catalog, "catalog")).hexdigest(),
    })
    registry_payload = live_payload(registry_document(registry_entries), "registry")
    registry_path = state_root / "registry.xml"
    registry_before = _before_hash(registry_path)
    desired_registry_hash = hashlib.sha256(registry_payload).hexdigest()
    if registry_before != desired_registry_hash:
        targets.append({"artifact_kind": "registry", "locator": "registry.xml", "before_sha256": registry_before, "payload_sha256": desired_registry_hash})
    commit_point = "registry.xml" if targets[-1]["artifact_kind"] == "registry" else catalog_locator
    if commit_point == "registry.xml" and targets[-2]["artifact_kind"] == "technology-index" and targets[-2]["before_sha256"] == targets[-2]["payload_sha256"]:
        targets[-2]["before_sha256"] = None
    catalog_applied = catalog_before == hashlib.sha256(live_payload(proposed_catalog, "catalog")).hexdigest()
    registry_applied = registry_before == desired_registry_hash
    already_applied = immutable_observed and catalog_applied and registry_applied
    manifest = {
        "schema_version": 2,
        "operation_id": request["operation_id"],
        "operation": request["operation"],
        "consumer_root": str(consumer_root),
        "consumer_root_resolution_source": source,
        "state_root": str(state_root),
        "technology": technology,
        "catalog_id": request["catalog_id"],
        "inference_id": entry["inference_id"],
        "revision": entry["revision"],
        "policy_id": policy["policy_id"],
        "policy_digest_sha256": policy["approved_candidate_digest_sha256"],
        "replayed_event_ids": replayed,
        "publication_order": [target["locator"] for target in targets],
        "commit_point": commit_point,
        "targets": targets,
    }
    return {
        "consumer_root": str(consumer_root),
        "consumer_root_resolution_source": source,
        "diagnostics": [],
        "already_applied": already_applied,
        "mutation_applied": False,
        "proposal": manifest,
        "status": "proposal",
        "target_manifest_digest_sha256": digest_value(manifest),
    }


def _validate_approval(approval: Any, proposal: dict[str, Any]) -> None:
    approval = _exact_object(approval, APPROVAL_KEYS, "APPROVAL_KEYS")
    manifest = proposal["proposal"]
    expected = {
        "schema_version": 2,
        "approval_type": "analytic-inference-lifecycle-mutation",
        "status": "approved",
        "consumed": False,
        "issued_after_dry_run": True,
        "operation_id": manifest["operation_id"],
        "operation": manifest["operation"],
        "consumer_root": manifest["consumer_root"],
        "policy_id": manifest["policy_id"],
        "policy_digest_sha256": manifest["policy_digest_sha256"],
        "target_manifest_digest_sha256": proposal["target_manifest_digest_sha256"],
        "targets": manifest["targets"],
    }
    for key, value in expected.items():
        if approval.get(key) != value:
            raise StateError(f"APPROVAL_BINDING_MISMATCH:{key}")
    if not isinstance(approval.get("source_locator"), str) or not approval["source_locator"]:
        raise StateError("APPROVAL_SOURCE_LOCATOR")


@contextmanager
def exclusive_writer(lock_root: Path, operation_id: str):
    """Take a non-writing, consumer-root-wide advisory lock or fail closed."""
    del operation_id
    descriptor = os.open(lock_root, os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        os.close(descriptor)
        raise StateError("CONCURRENT_WRITER") from exc
    try:
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def bootstrap(
    consumer_root: Path,
    technology: str,
    catalog_id: str,
    aliases: list[str],
    active_limit: int,
    *,
    fail_before_registry: bool = False,
) -> dict[str, Any]:
    """Serialize the complete bootstrap validation and mutation transaction."""
    with exclusive_writer(consumer_root, f"bootstrap:{technology}"):
        return _bootstrap_locked(
            consumer_root,
            technology,
            catalog_id,
            aliases,
            active_limit,
            fail_before_registry=fail_before_registry,
        )


def _replace_index(path: Path, payload: bytes, before_sha256: str, staging: Path, consumer_root: Path, root_identity: tuple[int, int]) -> None:
    _assert_root_identity(consumer_root, root_identity)
    assert_no_symlink_components(consumer_root, path)
    if digest_file(path) != before_sha256:
        raise StateError("INDEX_DRIFT")
    fd, temporary_name = tempfile.mkstemp(prefix="index-", suffix=".xml", dir=staging)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _assert_root_identity(consumer_root, root_identity)
        if digest_file(path) != before_sha256:
            raise StateError("INDEX_DRIFT")
        os.replace(temporary_name, path)
    finally:
        try:
            Path(temporary_name).unlink()
        except FileNotFoundError:
            pass


def apply_lifecycle(
    consumer_root: Path,
    source: str,
    request_path: Path,
    approval_path: Path,
    policy_path: Path,
    *,
    fail_before_commit: bool = False,
    fail_after_commit: bool = False,
) -> dict[str, Any]:
    initial = lifecycle_proposal(consumer_root, source, request_path, policy_path)
    if initial["already_applied"]:
        return {"approval_consumed": False, "approval_required": False, "consumer_root": str(consumer_root), "diagnostics": ["EXACT_REPLAY_NOOP"], "mutation_applied": False, "published": [], "residues": [], "status": "success", "target_manifest_digest_sha256": initial["target_manifest_digest_sha256"]}
    _validate_approval(load_json(approval_path), initial)
    state_root = state_root_for(consumer_root)
    operation_id = initial["proposal"]["operation_id"]
    residues: list[str] = []
    published: list[str] = []
    with exclusive_writer(consumer_root, operation_id):
        proposal = lifecycle_proposal(consumer_root, source, request_path, policy_path)
        if proposal["target_manifest_digest_sha256"] != initial["target_manifest_digest_sha256"]:
            raise StateError("PROPOSAL_DRIFT")
        if proposal["already_applied"]:
            return {"approval_consumed": False, "approval_required": False, "consumer_root": str(consumer_root), "diagnostics": ["EXACT_REPLAY_NOOP"], "mutation_applied": False, "published": [], "residues": [], "status": "success", "target_manifest_digest_sha256": proposal["target_manifest_digest_sha256"]}
        _validate_approval(load_json(approval_path), proposal)
        request = load_json(request_path)
        _, values = load_policy(policy_path)
        registry_entries, catalog, _ = _lifecycle_base(consumer_root, request["technology"], request["catalog_id"], values)
        entry = request["index_entry"]
        proposed_catalog = {
            **catalog,
            "entries": sorted([item for item in catalog["entries"] if item["inference_id"] != entry["inference_id"]] + [entry], key=lambda item: item["inference_id"]),
        }
        original_identity = (consumer_root.stat().st_dev, consumer_root.stat().st_ino)
        _ensure_directory_chain(consumer_root, consumer_root / ".loki")
        staging = Path(tempfile.mkdtemp(prefix=".lifecycle-", dir=consumer_root / ".loki"))
        try:
            payload_by_locator = {entry["locator"]: live_payload(request["record"], "record")}
            ordered_events, _, _ = reduce_events(request["events"], entry, values)
            for event in ordered_events:
                locator = f"events/{entry['inference_id']}/{event['event_id']}.xml"
                payload_by_locator[locator] = live_payload(event, "event")
            payload_by_locator[f"catalogs/{request['technology']}/index.xml"] = live_payload(proposed_catalog, "catalog")
            payload_by_locator["registry.xml"] = live_payload(registry_document(registry_entries), "registry")

            def publish(target: dict[str, Any]) -> None:
                path = state_root / target["locator"]
                _ensure_directory_chain(consumer_root, path.parent)
                payload = payload_by_locator[target["locator"]]
                if target["before_sha256"] == target["payload_sha256"]:
                    return
                if target["before_sha256"] is None:
                    artifact_kind = target["artifact_kind"]
                    kind = {"technology-index": "catalog"}.get(artifact_kind, artifact_kind)
                    changed = _atomic_publish(path, payload, staging, consumer_root, original_identity, kind)
                else:
                    _replace_index(path, payload, target["before_sha256"], staging, consumer_root, original_identity)
                    changed = True
                if changed:
                    published.append(target["locator"])

            commit_point = proposal["proposal"]["commit_point"]
            non_commit = [target for target in proposal["proposal"]["targets"] if target["locator"] != commit_point]
            commit_target = [target for target in proposal["proposal"]["targets"] if target["locator"] == commit_point]
            if len(commit_target) != 1:
                raise StateError("COMMIT_POINT_TARGET")
            for target in non_commit:
                publish(target)
            if fail_before_commit:
                residues = sorted(published)
                return {
                    "approval_consumed": False,
                    "commit_point_published": False,
                    "diagnostics": ["INJECTED_FAILURE_BEFORE_COMMIT"],
                    "mutation_applied": bool(published),
                    "published": [],
                    "residues": residues,
                    "status": "blocked",
                }
            publish(commit_target[0])
            if fail_after_commit:
                residues = sorted(published)
                return {
                    "approval_consumed": True,
                    "commit_point_published": True,
                    "diagnostics": ["INJECTED_FAILURE_AFTER_COMMIT", "AUDIT_REQUIRED_NO_ROLLBACK_CLAIMED"],
                    "mutation_applied": True,
                    "published": published,
                    "residues": residues,
                    "status": "blocked",
                }
        except (StateError, StateXmlError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            residues.extend(published)
            try:
                residues.extend(str(path.relative_to(consumer_root)) for path in staging.iterdir())
            except OSError:
                residues.append(str(staging.relative_to(consumer_root)))
            diagnostic = exc.diagnostic if isinstance(exc, StateError) else f"MUTATION_FAILURE:{exc}"
            return {
                "approval_consumed": bool(published and published[-1] == proposal["proposal"]["commit_point"]),
                "commit_point_published": bool(published and published[-1] == proposal["proposal"]["commit_point"]),
                "diagnostics": [diagnostic, "PARTIAL_FAILURE_NO_ROLLBACK_CLAIMED"],
                "mutation_applied": bool(published),
                "published": published,
                "residues": sorted(set(residues)),
                "status": "blocked",
            }
        finally:
            try:
                staging.rmdir()
            except OSError:
                residues.extend(str(path.relative_to(consumer_root)) for path in staging.iterdir())
    return {
        "approval_consumed": bool(published),
        "commit_point_published": bool(published and published[-1] == initial["proposal"]["commit_point"]),
        "consumer_root": str(consumer_root),
        "diagnostics": [],
        "mutation_applied": bool(published),
        "published": published,
        "residues": sorted(set(residues)),
        "status": "success",
        "target_manifest_digest_sha256": initial["target_manifest_digest_sha256"],
    }


def _load_validated_catalog_records(state_root: Path, technology: str, catalog: dict[str, Any], values: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    records: dict[str, dict[str, Any]] = {}
    events_by_id: dict[str, list[dict[str, Any]]] = {}
    _validate_catalog_structure(catalog, technology, values)
    seen: set[str] = set()
    previous: str | None = None
    for raw_entry in catalog["entries"]:
        raw_entry = _exact_object(raw_entry, CATALOG_ENTRY_KEYS, "CATALOG_ENTRY_KEYS")
        inference_id = require_segment(raw_entry.get("inference_id"), "CATALOG_INFERENCE_ID")
        if not isinstance(inference_id, str) or inference_id in seen or (previous is not None and inference_id <= previous):
            raise StateError("CATALOG_ENTRY_ORDER_OR_DUPLICATE")
        revision = raw_entry.get("revision")
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise StateError("CATALOG_ENTRY_REVISION")
        expected_locator = f"catalogs/{technology}/records/{inference_id}/rev-{revision}.xml"
        if raw_entry.get("locator") != expected_locator:
            raise StateError("CATALOG_ENTRY_LOCATOR")
        record_path = contained_path(state_root, raw_entry.get("locator"), "CATALOG_RECORD_LOCATOR", must_exist=True)
        record = _validate_record(load_live_state(record_path, "record"))
        entry = _validate_catalog_entry(raw_entry, technology, record)
        events_dir = state_root / f"events/{inference_id}"
        assert_no_symlink_components(state_root.parent.parent.parent, events_dir)
        if not events_dir.exists() or events_dir.is_symlink() or not events_dir.is_dir():
            raise StateError(f"EVENTS_DIRECTORY_REQUIRED:{inference_id}")
        events: list[dict[str, Any]] = []
        for event_path in sorted(events_dir.iterdir()):
            if event_path.is_symlink() or not event_path.is_file() or event_path.suffix != ".xml":
                raise StateError(f"EVENT_TARGET_INVALID:{event_path.name}")
            event = load_live_state(event_path, "event")
            if event_path.name != f"{event.get('event_id')}.xml":
                raise StateError(f"EVENT_LOCATOR_ID_MISMATCH:{event_path.name}")
            event_entry = {**entry, "revision": event.get("inference_revision")}
            _validate_lifecycle_event(event, event_entry)
            events.append(event)
        current_events = [event for event in events if event.get("inference_revision") == entry["revision"]]
        ordered, _ = require_event_derived_snapshot(record, current_events, entry, values, f"SNAPSHOT_EVENT_DERIVATION_MISMATCH:{inference_id}")
        seen.add(inference_id)
        previous = inference_id
        records[inference_id] = record
        events_by_id[inference_id] = sorted(events, key=lambda item: item["event_id"])
    return records, events_by_id


def _validate_catalog_structure(catalog: dict[str, Any], technology: str, values: dict[str, Any]) -> None:
    previous: str | None = None
    seen: set[str] = set()
    for raw_entry in catalog["entries"]:
        raw_entry = _exact_object(raw_entry, CATALOG_ENTRY_KEYS, "CATALOG_ENTRY_KEYS")
        inference_id = require_segment(raw_entry.get("inference_id"), "CATALOG_INFERENCE_ID")
        if inference_id in seen or (previous is not None and inference_id <= previous):
            raise StateError("CATALOG_ENTRY_ORDER_OR_DUPLICATE")
        revision = raw_entry.get("revision")
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise StateError("CATALOG_ENTRY_REVISION")
        if raw_entry.get("locator") != f"catalogs/{technology}/records/{inference_id}/rev-{revision}.xml":
            raise StateError("CATALOG_ENTRY_LOCATOR")
        seen.add(inference_id)
        previous = inference_id
    active = sum(entry.get("status") in {"active", "protected"} for entry in catalog["entries"])
    if catalog["active_limit"] != values["persistent_catalog_limit"] or active > catalog["active_limit"]:
        raise StateError("CATALOG_ACTIVE_LIMIT")


def _directory_digest(path: Path) -> str:
    listing = []
    for child in sorted(path.iterdir()):
        if child.is_symlink():
            raise StateError(f"DIRECTORY_SYMLINK:{child}")
        listing.append({"name": child.name, "kind": "directory" if child.is_dir() else "file", "sha256": digest_file(child) if child.is_file() else None})
    return digest_value(listing)


def purge_dry_run(consumer_root: Path, source: str, request_path: Path, policy_path: Path) -> dict[str, Any]:
    request = _exact_object(
        load_json(request_path),
        {"schema_version", "operation_id", "technology", "catalog_id", "inference_ids", "policy_id", "policy_digest_sha256"},
        "PURGE_REQUEST_KEYS",
    )
    if request.get("schema_version") != 1:
        raise StateError("PURGE_SCHEMA_VERSION")
    require_segment(request.get("operation_id"), "OPERATION_ID")
    technology = require_segment(request.get("technology"), "TECHNOLOGY_ID")
    catalog_id = require_segment(request.get("catalog_id"), "CATALOG_ID")
    inference_ids = _string_array(request.get("inference_ids"), "PURGE_INFERENCE_IDS")
    policy, values = load_policy(policy_path)
    if request.get("policy_id") != policy["policy_id"] or request.get("policy_digest_sha256") != policy["approved_candidate_digest_sha256"]:
        raise StateError("POLICY_BINDING_MISMATCH")
    if not inference_ids or len(inference_ids) > values["removals_per_cycle"]:
        raise StateError("PURGE_REMOVALS_PER_CYCLE")
    catalog_path, catalog = _load_catalog(consumer_root, technology, catalog_id)
    state_root = state_root_for(consumer_root)
    records, events_by_id = _load_validated_catalog_records(state_root, technology, catalog, values)
    by_id = {item.get("inference_id"): item for item in catalog["entries"] if isinstance(item, dict)}
    targets: list[dict[str, Any]] = []
    revisions: dict[str, int] = {}
    for inference_id in inference_ids:
        require_segment(inference_id, "PURGE_INFERENCE_ID")
        entry = by_id.get(inference_id)
        if not isinstance(entry, dict):
            raise StateError(f"PURGE_INFERENCE_NOT_FOUND:{inference_id}")
        record_path = contained_path(state_root, entry.get("locator"), "PURGE_RECORD_LOCATOR", must_exist=True)
        record = records[inference_id]
        score = record["snapshot"]["score"]
        protected = entry.get("status") == "protected" or record.get("status") == "protected"
        eligibility = classify_eligibility(score, protected, values)
        if protected:
            raise StateError(f"PROTECTED_RECORD:{inference_id}")
        if not eligibility["purge_review"]:
            raise StateError(f"PURGE_NOT_ELIGIBLE:{inference_id}")
        revisions[inference_id] = entry["revision"]
        record_dir = record_path.parent
        if record_dir.is_symlink() or not record_dir.is_dir():
            raise StateError(f"PURGE_RECORDS_NOT_DIRECTORY:{inference_id}")
        record_revisions: list[int] = []
        for revision_path in sorted(record_dir.iterdir()):
            match = re.fullmatch(r"rev-([1-9][0-9]*)\.xml", revision_path.name)
            if revision_path.is_symlink() or not revision_path.is_file() or match is None:
                raise StateError(f"PURGE_RECORD_REVISION_INVALID:{revision_path.name}")
            revision_record = _validate_record(load_live_state(revision_path, "record"))
            if revision_record["inference_id"] != inference_id or revision_record["revision"] != int(match.group(1)):
                raise StateError(f"PURGE_RECORD_REVISION_PARITY:{revision_path.name}")
            record_revisions.append(revision_record["revision"])
            locator = str(revision_path.relative_to(state_root))
            before_hash = digest_file(revision_path)
            targets.append({"artifact_kind": "record", "locator": locator, "selector": "document", "before_sha256": before_hash})
            targets.append({"artifact_kind": "snapshot", "locator": locator, "selector": "record.snapshot", "before_sha256": before_hash})
        if entry["revision"] not in record_revisions:
            raise StateError(f"PURGE_CURRENT_REVISION_MISSING:{inference_id}")
        events_dir = state_root / f"events/{inference_id}"
        assert_no_symlink_components(consumer_root, events_dir)
        for event in events_by_id[inference_id]:
            event_path = contained_path(state_root, f"events/{inference_id}/{event['event_id']}.xml", "PURGE_EVENT_LOCATOR", must_exist=True)
            targets.append({"artifact_kind": "event", "locator": str(event_path.relative_to(state_root)), "selector": "document", "before_sha256": digest_file(event_path)})
        targets.append({"artifact_kind": "known-empty-directory", "locator": str(events_dir.relative_to(state_root)), "selector": "empty-after-approved-file-deletes", "before_sha256": _directory_digest(events_dir)})
        targets.append({"artifact_kind": "known-empty-directory", "locator": str(record_dir.relative_to(state_root)), "selector": "empty-after-approved-file-deletes", "before_sha256": _directory_digest(record_dir)})
        targets.append({"artifact_kind": "index-entry", "locator": str(catalog_path.relative_to(state_root)), "selector": f"catalog.entries[inference_id={inference_id}]", "before_sha256": digest_file(catalog_path)})
        for survivor_id, survivor in records.items():
            if survivor_id in inference_ids:
                continue
            lineage = survivor["lineage"]
            if inference_id in [*lineage["supersedes"], *lineage["merged_from"]] or lineage["redirect_to"] == inference_id:
                raise StateError(f"PURGE_SURVIVING_LINEAGE_REFERENCE:{survivor_id}:{inference_id}")
    targets.sort(key=lambda item: (item["locator"], item["artifact_kind"], item["selector"]))
    manifest = {
        "schema_version": 1,
        "operation_id": request["operation_id"],
        "operation": "purge",
        "consumer_root": str(consumer_root),
        "consumer_root_resolution_source": source,
        "state_root": str(state_root),
        "technology": technology,
        "catalog_id": catalog_id,
        "inference_ids": inference_ids,
        "inference_revisions": revisions,
        "policy_id": policy["policy_id"],
        "policy_digest_sha256": policy["approved_candidate_digest_sha256"],
        "targets": targets,
    }
    return {
        "approval_effect": "none",
        "diagnostics": ["PHYSICAL_PURGE_UNAVAILABLE_DRY_RUN_ONLY"],
        "dry_run_manifest": manifest,
        "dry_run_manifest_digest_sha256": digest_value(manifest),
        "mutation_applied": False,
        "physical_purge_available": False,
        "status": "valid-dry-run",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("inspect", "bootstrap", "propose-lifecycle", "apply-lifecycle", "purge-dry-run"))
    parser.add_argument("--approved-mutation", action="store_true")
    parser.add_argument("--technology")
    parser.add_argument("--catalog-id")
    parser.add_argument("--alias", action="append", default=[])
    parser.add_argument("--active-limit", type=int, default=3)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--policy", type=Path, default=POLICY_PATH)
    parser.add_argument("--strict-policy-self-test", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--fail-before-registry", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--fail-before-commit", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--fail-after-commit", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    consumer_root: Path | None = None
    source: str | None = None
    try:
        if args.strict_policy_self_test:
            strict_policy_self_test(args.policy)
        consumer_root, source = resolve_consumer_root()
        reject_legacy_state_layout(consumer_root)
        if args.operation == "inspect":
            output = inspect(consumer_root)
        elif args.operation == "bootstrap":
            if not args.approved_mutation:
                raise StateError("APPROVED_MUTATION_REQUIRED")
            if args.technology is None or args.catalog_id is None:
                raise StateError("BOOTSTRAP_IDENTITY_REQUIRED")
            output = bootstrap(consumer_root, args.technology, args.catalog_id, args.alias, args.active_limit, fail_before_registry=args.fail_before_registry)
        elif args.operation == "propose-lifecycle":
            if args.request is None:
                raise StateError("LIFECYCLE_REQUEST_REQUIRED")
            output = lifecycle_proposal(consumer_root, source, args.request, args.policy)
        elif args.operation == "apply-lifecycle":
            if args.request is None or args.approval is None:
                raise StateError("LIFECYCLE_REQUEST_AND_APPROVAL_REQUIRED")
            output = apply_lifecycle(
                consumer_root,
                source,
                args.request,
                args.approval,
                args.policy,
                fail_before_commit=args.fail_before_commit,
                fail_after_commit=args.fail_after_commit,
            )
        elif args.operation == "purge-dry-run":
            if args.request is None:
                raise StateError("PURGE_REQUEST_REQUIRED")
            output = purge_dry_run(consumer_root, source, args.request, args.policy)
        output.setdefault("consumer_root_resolution_source", source)
        print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 2 if output.get("status") == "blocked" else 0
    except (StateError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        diagnostic = exc.diagnostic if isinstance(exc, StateError) else f"INPUT:{exc}"
        output: dict[str, Any] = {
            "diagnostics": [diagnostic],
            "mutation_applied": False,
            "operation": args.operation,
            "status": "blocked",
        }
        if args.operation == "inspect":
            output.update({
                "consumer_root": str(consumer_root) if consumer_root is not None else None,
                "consumer_root_resolution_source": source,
                "loaded_locators": [],
                "registry_state": "blocked",
                "state_root": str(state_root_for(consumer_root)) if consumer_root is not None else None,
            })
        print(json.dumps(output, sort_keys=True, separators=(",", ":")))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
