#!/usr/bin/env python3
"""Validate an agent_session_evidence XML manifest without reading payloads."""

from __future__ import annotations

import hashlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


STATES = {"complete", "partial", "pointer-only", "unavailable", "unsupported"}
LOCATOR_KINDS = {"runtime-pointer", "local-file", "export", "unavailable"}
PORTABILITIES = {"same-profile", "same-machine", "portable", "none"}
STORAGE_MODES = {"pointer-only", "pointer-plus-sanitized-snapshot", "sanitized-snapshot-only", "unavailable"}
METRIC_KINDS = {"per-turn-delta", "cumulative", "account-window", "estimated", "unknown"}
DIMENSIONS = {"transcript", "tool_io", "errors", "reasoning_summary", "token_usage"}
ID_TYPES = {
    "run_id": "loki-run-id", "agent_run_id": "agent-run-id",
    "handoff_id": "handoff-id", "agent_name": "agent-name",
}

ROOT_CHILDREN = ("identity", "runtime", "locator", "snapshot", "evidence_completeness", "usage", "security", "integrity", "completion_record", "evidence_policy")
COMPLETION_LISTS = {
    "changed_files": "file", "read_files": "file", "validations": "validation",
    "material_attempts": "attempt", "known_errors": "error", "decisions": "decision",
    "residual_risks": "risk",
}


def value(node: ET.Element | None) -> str:
    return (node.text or "").strip() if node is not None else ""


def canonical_checksum(root: ET.Element) -> str:
    """Hash the ElementTree serialization with the self-referential value blank."""
    integrity = root.find("integrity/canonical_content_checksum")
    if integrity is None:
        return ""
    old = integrity.text
    integrity.text = ""
    serialized = ET.tostring(root, encoding="utf-8", short_empty_elements=True)
    integrity.text = old
    return hashlib.sha256(serialized).hexdigest()


def child_names(node: ET.Element | None) -> list[str]:
    return [child.tag for child in node] if node is not None else []


def closed_shape_errors(root: ET.Element) -> list[str]:
    """Reject unknown manifest children and attributes before semantic checks."""
    errors: list[str] = []
    def exact(node: ET.Element | None, names: tuple[str, ...], path: str) -> None:
        if child_names(node) != list(names):
            errors.append(f"{path} has unknown, missing, or reordered children")
    def attrs(node: ET.Element | None, allowed: set[str], path: str) -> None:
        if node is not None and set(node.attrib) - allowed:
            errors.append(f"{path} has unknown attributes")

    attrs(root, {"schema_version"}, "root")
    exact(root, ROOT_CHILDREN, "root")
    identity = root.find("identity")
    exact(identity, tuple(ID_TYPES), "identity")
    for name in ID_TYPES: attrs(identity.find(name) if identity is not None else None, {"type"}, f"identity/{name}")
    runtime = root.find("runtime")
    exact(runtime, ("adapter", "adapter_version", "root_session_id", "parent_thread_id", "thread_id", "runtime_agent_id", "terminal_status", "parent_reference"), "runtime")
    for name in ("root_session_id", "parent_thread_id", "thread_id", "runtime_agent_id"):
        attrs(runtime.find(name) if runtime is not None else None, {"type"}, f"runtime/{name}")
    exact(runtime.find("parent_reference") if runtime is not None else None, ("type", "value"), "runtime/parent_reference")
    for path, names in (("locator", ("kind", "value", "portability", "unavailable_reason")),
                        ("snapshot", ("storage_mode", "payload_path", "captured_at", "payload_checksum", "checksum_absence_reason")),
                        ("usage", ("status", "metric_kind", "source", "source_scope", "measured_at", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens", "unavailable_reason")),
                        ("security", ("snapshot_classification", "structural_redaction_result", "secret_pii_hardening", "retention_metadata", "purge_policy")),
                        ("integrity", ("canonical_content_checksum", "result", "verification_notes")),
                        ("evidence_policy", ("mode", "gap_handling", "capture_owner", "retrospective_dispatch"))):
        exact(root.find(path), names, path)
    attrs(root.find("snapshot/payload_checksum"), {"algorithm"}, "snapshot/payload_checksum")
    attrs(root.find("integrity/canonical_content_checksum"), {"algorithm"}, "integrity/canonical_content_checksum")
    completeness = root.find("evidence_completeness")
    if completeness is not None:
        if child_names(completeness) != ["dimension"] * 5 + ["overall_status"]:
            errors.append("evidence_completeness has unknown, missing, or reordered children")
        for dimension in completeness.findall("dimension"):
            attrs(dimension, {"name"}, "evidence_completeness/dimension")
            expected = ("status", "missing_reason", "provenance") if dimension.get("name") == "reasoning_summary" else ("status", "missing_reason")
            exact(dimension, expected, "evidence_completeness/dimension")
    completion = root.find("completion_record")
    completion_names = ("agent_run_id", "handoff_id", "terminal_status", "summary", *COMPLETION_LISTS, "next_destination")
    exact(completion, completion_names, "completion_record")
    for name in ("agent_run_id", "handoff_id"):
        attrs(completion.find(name) if completion is not None else None, {"type"}, f"completion_record/{name}")
    if completion is not None:
        for container, child in COMPLETION_LISTS.items():
            node = completion.find(container)
            if node is not None and (any(item.tag != child for item in node) or any(item.attrib for item in node)):
                errors.append(f"completion_record/{container} has unknown children or attributes")
    for node in root.iter():
        allowed = {"schema_version"} if node is root else set()
        if node.tag in {"run_id", "agent_run_id", "handoff_id", "agent_name", "root_session_id", "parent_thread_id", "thread_id", "runtime_agent_id"}: allowed = {"type"}
        if node.tag in {"payload_checksum", "canonical_content_checksum"}: allowed = {"algorithm"}
        if node.tag == "dimension": allowed = {"name"}
        if set(node.attrib) - allowed:
            errors.append(f"{node.tag} has unknown attributes")
    return errors


def validate(root: ET.Element) -> list[str]:
    errors = closed_shape_errors(root)
    def require(path: str) -> ET.Element | None:
        node = root.find(path)
        if node is None or not value(node):
            errors.append(f"missing {path}")
        return node

    if root.tag != "agent_session_evidence" or root.get("schema_version") != "1":
        errors.append("root must be agent_session_evidence schema_version=1")

    identity_values: dict[str, str] = {}
    for name, expected_type in ID_TYPES.items():
        node = require(f"identity/{name}")
        if node is not None and node.get("type") != expected_type:
            errors.append(f"identity/{name} has wrong type")
        identity_values[name] = value(node)
    if len(set(identity_values.values())) != len(identity_values) or "" in identity_values.values():
        errors.append("identity values must be non-empty and non-interchangeable")

    runtime_ids = [value(root.find(f"runtime/{name}")) for name in
                   ("root_session_id", "parent_thread_id", "thread_id", "runtime_agent_id")]
    if any(item and item in identity_values.values() for item in runtime_ids):
        errors.append("runtime locators must not reuse identity values")
    for name, expected_type in (("root_session_id", "runtime-root-session-id"),
                                ("parent_thread_id", "runtime-parent-thread-id"),
                                ("thread_id", "runtime-thread-id"),
                                ("runtime_agent_id", "runtime-agent-id")):
        node = require(f"runtime/{name}")
        if node is not None and node.get("type") != expected_type:
            errors.append(f"runtime/{name} has wrong type")
    if not value(root.find("runtime/adapter")) or not value(root.find("runtime/terminal_status")):
        errors.append("runtime adapter and terminal_status are required")

    locator_kind = value(root.find("locator/kind"))
    locator_value = value(root.find("locator/value"))
    portability = value(root.find("locator/portability"))
    locator_reason = value(root.find("locator/unavailable_reason"))
    if locator_kind not in LOCATOR_KINDS or portability not in PORTABILITIES:
        errors.append("invalid locator kind or portability")
    if locator_kind == "unavailable":
        if locator_value or not locator_reason or portability != "none":
            errors.append("unavailable locator needs no value, a reason, and portability none")
    elif not locator_value:
        errors.append("usable locator needs a value")

    overall = value(root.find("evidence_completeness/overall_status"))
    if overall not in STATES:
        errors.append("invalid overall evidence status")
    dimensions = {node.get("name", ""): node for node in root.findall("evidence_completeness/dimension")}
    if set(dimensions) != DIMENSIONS:
        errors.append("exactly the five required dimensions are required")
    statuses: list[str] = []
    for name, node in dimensions.items():
        status = value(node.find("status"))
        reason = value(node.find("missing_reason"))
        statuses.append(status)
        if status not in STATES:
            errors.append(f"invalid {name} status")
        if status != "complete" and not reason:
            errors.append(f"{name} needs a missing reason")
        if status == "complete" and reason:
            errors.append(f"complete {name} cannot have a missing reason")
        if name == "reasoning_summary":
            combined = " ".join(value(n).lower() for n in node.iter())
            if "chain-of-thought" in combined or "private cot" in combined or "full cot" in combined:
                errors.append("private/full chain-of-thought is forbidden")
    if overall == "complete" and (any(status != "complete" for status in statuses) or locator_kind == "unavailable"):
        errors.append("complete requires every dimension complete and a usable locator")

    policy = root.find("evidence_policy")
    if policy is None or {name: value(policy.find(name)) for name in ("mode", "gap_handling", "capture_owner", "retrospective_dispatch")} != {
        "mode": "evidence-first", "gap_handling": "preserve-gap", "capture_owner": "collector-only", "retrospective_dispatch": "explicit-only",
    }:
        errors.append("evidence policy must be the closed evidence-first policy")

    mode = value(root.find("snapshot/storage_mode"))
    payload = value(root.find("snapshot/payload_path"))
    payload_sum = value(root.find("snapshot/payload_checksum"))
    absence = value(root.find("snapshot/checksum_absence_reason"))
    if mode not in STORAGE_MODES:
        errors.append("invalid snapshot storage mode")
    if mode in {"pointer-plus-sanitized-snapshot", "sanitized-snapshot-only"}:
        if not payload or len(payload_sum) != 64 or any(ch not in "0123456789abcdef" for ch in payload_sum.lower()):
            errors.append("persisted sanitized snapshot needs path and sha-256")
    elif payload or payload_sum or not absence:
        errors.append("non-persisted snapshot needs no payload/checksum and an absence reason")

    usage = root.find("usage")
    usage_status = value(usage.find("status")) if usage is not None else ""
    if usage_status not in STATES:
        errors.append("invalid usage status")
    metrics = [value(usage.find(name)) if usage is not None else "" for name in
               ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")]
    if usage_status == "complete":
        if (value(usage.find("metric_kind")) not in METRIC_KINDS or not value(usage.find("source"))
                or not value(usage.find("source_scope")) or not value(usage.find("measured_at"))):
            errors.append("complete usage needs kind, source, scope, and time")
        try:
            numbers = [int(item) for item in metrics]
            if any(number < 0 for number in numbers) or numbers[4] != numbers[0] + numbers[2]:
                errors.append("usage token counters are incoherent")
        except ValueError:
            errors.append("complete usage counters must be integers")
    elif any(metrics) or not value(usage.find("unavailable_reason")):
        errors.append("degraded usage must omit counters and state a reason")

    security = root.find("security")
    forbidden = " ".join(value(n).lower() for n in root.iter())
    if any(term in forbidden for term in ("private chain-of-thought", "full chain-of-thought", "private_cot", "full_cot")):
        errors.append("private/full chain-of-thought is forbidden")
    if security is None or value(security.find("snapshot_classification")) != "sanitized" or not value(security.find("structural_redaction_result")):
        errors.append("sanitized classification and structural redaction result are required")

    checksum = value(root.find("integrity/canonical_content_checksum"))
    if len(checksum) != 64 or checksum != canonical_checksum(root):
        errors.append("canonical content checksum mismatch")
    if value(root.find("integrity/result")) not in {"verified", "unverified", "mismatch"}:
        errors.append("invalid integrity result")
    if overall == "complete" and value(root.find("integrity/result")) != "verified":
        errors.append("complete requires verified integrity")

    for name, expected_type, identity_name in (("agent_run_id", "agent-run-id", "agent_run_id"), ("handoff_id", "handoff-id", "handoff_id")):
        node = root.find(f"completion_record/{name}")
        if node is None or node.get("type") != expected_type or value(node) != identity_values[identity_name]:
            errors.append(f"completion record {name} does not correlate")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate-session-evidence.py <path>", file=sys.stderr)
        return 2
    try:
        root = ET.parse(Path(sys.argv[1])).getroot()
    except (OSError, ET.ParseError) as exc:
        print(f"unable to read or parse evidence: {exc}", file=sys.stderr)
        return 2
    errors = validate(root)
    if errors:
        print("invalid evidence: " + "; ".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
