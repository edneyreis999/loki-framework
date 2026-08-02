#!/usr/bin/env python3
"""Validate current-only loki-manual-qa records and real persisted run trees."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from copy import deepcopy
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "scripts/fixtures/manual-qa"
FIXTURE_FILES = ("record-cases.json", "transition-cases.json", "tree-cases.json")
HEX = r"[0-9a-f]{64}"
RUN_RE = re.compile(rf"loki-run-v2:{HEX}\Z")
EXEC_RE = re.compile(rf"loki-execution-v2:{HEX}\Z")
DIGEST_RE = re.compile(rf"sha256:{HEX}\Z")
STEP_RE = re.compile(r"MQ-(?:0[1-9]|[1-9][0-9]+)\Z")
AGENT_RUN_RE = re.compile(rf"agent-run-v1:{HEX}\Z")
HANDOFF_ID_RE = re.compile(rf"handoff-v1:{HEX}\Z")
REPORT_RE = re.compile(rf"manual-qa-report-v1:{HEX}\Z")
TRANSACTION_ID_RE = re.compile(rf"manual-qa-transaction-v1:{HEX}\Z")
DECLARATION = "all-applicable-manual-tests-tested-and-approved"
ASSESSOR_IDENTITY = "loki-manual-qa:semantic-assessor-v1"
ASSESSMENT_OWNER = "loki-manual-qa-orchestrator"
ATTESTATION_REVIEWER_IDENTITY = "manual-qa-attestation-auditor"
EVALUATOR_POLICY_ID = "manual-qa-semantic-policy-v1"
EVALUATOR_POLICY_DIGEST = "sha256:" + hashlib.sha256(
    b"manual-qa-semantic-policy-v1:completed-all;reject-ambiguous-negated-future-partial"
).hexdigest()
MANUAL_WRITE_TRACE: list[str] = []
EVIDENCE_DIMENSIONS = ("transcript", "tool_io", "errors", "reasoning_summary", "token_usage")
EVIDENCE_STATES = {"complete", "partial", "pointer-only", "unavailable", "unsupported"}
GUIDE_FIELDS = ("environment", "prerequisites", "initial_state", "actions", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit")


class ContractError(ValueError):
    pass


def require(code: str, condition: bool) -> None:
    if not condition:
        raise ContractError(code)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == unicodedata.normalize("NFC", value)


def closed(code: str, value: Any, keys: set[str]) -> dict[str, Any]:
    require(code, isinstance(value, dict) and set(value) == keys)
    return value


def digest(value: Any, *, omit: str | None = None) -> str:
    material = deepcopy(value)
    if omit is not None:
        material.pop(omit, None)
    raw = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def bytes_digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def xml_child(parent: ET.Element, tag: str, code: str) -> ET.Element:
    matches = [child for child in parent if child.tag == tag]
    require(code, len(matches) == 1)
    return matches[0]


def xml_closed(parent: ET.Element, tags: tuple[str, ...], code: str) -> None:
    require(code, [child.tag for child in parent] == list(tags))


def xml_text(parent: ET.Element, tag: str, code: str) -> str:
    value = xml_child(parent, tag, code).text or ""
    require(code, nonempty(value))
    return value


def evidence_canonical_checksum(root: ET.Element) -> str:
    clone = ET.fromstring(ET.tostring(root, encoding="utf-8"))
    checksum = clone.find("./integrity/canonical_content_checksum")
    require("EVIDENCE_CHECKSUM_FIELD_MISSING", checksum is not None)
    checksum.text = ""
    return "sha256:" + hashlib.sha256(ET.tostring(clone, encoding="utf-8")).hexdigest()


def validate_agent_session_evidence_bytes(raw: bytes, *, run_id: str, decision: str) -> dict[str, str]:
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ContractError("EVIDENCE_XML_INVALID") from exc
    require("EVIDENCE_ROOT_INVALID", root.tag == "agent_session_evidence" and root.attrib == {"schema_version": "1"})
    xml_closed(root, ("identity", "runtime", "locator", "snapshot", "evidence_completeness", "usage", "security", "integrity", "completion_record", "evidence_policy"), "EVIDENCE_ROOT_SHAPE_INVALID")
    identity = xml_child(root, "identity", "EVIDENCE_IDENTITY_MISSING")
    xml_closed(identity, ("run_id", "agent_run_id", "handoff_id", "agent_name"), "EVIDENCE_IDENTITY_SHAPE_INVALID")
    identity_values = {child.tag: child.text or "" for child in identity}
    identity_types = {child.tag: child.attrib.get("type") for child in identity}
    require("EVIDENCE_IDENTITY_TYPES_INVALID", identity_types == {"run_id": "loki-run-id", "agent_run_id": "agent-run-id", "handoff_id": "handoff-id", "agent_name": "agent-name"})
    require("EVIDENCE_RUN_ID_MISMATCH", identity_values["run_id"] == run_id and RUN_RE.fullmatch(run_id) is not None)
    require("EVIDENCE_AGENT_RUN_ID_INVALID", AGENT_RUN_RE.fullmatch(identity_values["agent_run_id"]) is not None)
    require("EVIDENCE_HANDOFF_ID_INVALID", HANDOFF_ID_RE.fullmatch(identity_values["handoff_id"]) is not None and identity_values["handoff_id"] != identity_values["agent_run_id"])
    require("EVIDENCE_AGENT_IDENTITY_INVALID", identity_values["agent_name"] == ATTESTATION_REVIEWER_IDENTITY)
    runtime = xml_child(root, "runtime", "EVIDENCE_RUNTIME_MISSING")
    xml_closed(runtime, ("adapter", "adapter_version", "root_session_id", "parent_thread_id", "thread_id", "runtime_agent_id", "terminal_status", "parent_reference"), "EVIDENCE_RUNTIME_SHAPE_INVALID")
    require("EVIDENCE_RUNTIME_TERMINAL_INVALID", xml_text(runtime, "terminal_status", "EVIDENCE_RUNTIME_TERMINAL_INVALID") == "completed")
    for tag, expected_type in (("root_session_id", "runtime-root-session-id"), ("parent_thread_id", "runtime-parent-thread-id"), ("thread_id", "runtime-thread-id"), ("runtime_agent_id", "runtime-agent-id")):
        node = xml_child(runtime, tag, "EVIDENCE_RUNTIME_LOCATOR_INVALID")
        require("EVIDENCE_RUNTIME_LOCATOR_INVALID", node.attrib == {"type": expected_type} and nonempty(node.text))
    parent = xml_child(runtime, "parent_reference", "EVIDENCE_PARENTAGE_MISSING")
    xml_closed(parent, ("type", "value"), "EVIDENCE_PARENTAGE_SHAPE_INVALID")
    require("EVIDENCE_PARENTAGE_INVALID", xml_text(parent, "type", "EVIDENCE_PARENTAGE_INVALID") == "runtime-parent-thread-id" and xml_text(parent, "value", "EVIDENCE_PARENTAGE_INVALID") == xml_text(runtime, "parent_thread_id", "EVIDENCE_PARENTAGE_INVALID"))
    locator = xml_child(root, "locator", "EVIDENCE_LOCATOR_MISSING")
    xml_closed(locator, ("kind", "value", "portability", "unavailable_reason"), "EVIDENCE_LOCATOR_SHAPE_INVALID")
    require("EVIDENCE_LOCATOR_INVALID", xml_text(locator, "kind", "EVIDENCE_LOCATOR_INVALID") == "runtime-pointer" and xml_text(locator, "portability", "EVIDENCE_LOCATOR_INVALID") == "same-profile" and xml_text(locator, "value", "EVIDENCE_LOCATOR_INVALID") == xml_text(runtime, "thread_id", "EVIDENCE_LOCATOR_INVALID"))
    snapshot = xml_child(root, "snapshot", "EVIDENCE_SNAPSHOT_MISSING")
    xml_closed(snapshot, ("storage_mode", "payload_path", "captured_at", "payload_checksum", "checksum_absence_reason"), "EVIDENCE_SNAPSHOT_SHAPE_INVALID")
    require("EVIDENCE_SNAPSHOT_INVALID", xml_text(snapshot, "storage_mode", "EVIDENCE_SNAPSHOT_INVALID") == "pointer-only" and xml_text(snapshot, "payload_path", "EVIDENCE_SNAPSHOT_INVALID") == "null" and xml_text(snapshot, "captured_at", "EVIDENCE_SNAPSHOT_INVALID") == "null" and xml_text(snapshot, "payload_checksum", "EVIDENCE_SNAPSHOT_INVALID") == "null" and xml_child(snapshot, "payload_checksum", "EVIDENCE_SNAPSHOT_INVALID").attrib == {"algorithm": "sha-256"} and xml_text(snapshot, "checksum_absence_reason", "EVIDENCE_SNAPSHOT_INVALID") != "null")
    completeness = xml_child(root, "evidence_completeness", "EVIDENCE_COMPLETENESS_MISSING")
    require("EVIDENCE_COMPLETENESS_SHAPE_INVALID", [child.tag for child in completeness] == ["dimension"] * 5 + ["overall_status"])
    dimensions = completeness.findall("dimension")
    require("EVIDENCE_DIMENSION_PARTITION_INVALID", [node.attrib for node in dimensions] == [{"name": name} for name in EVIDENCE_DIMENSIONS])
    for node in dimensions:
        xml_closed(node, ("status", "missing_reason") + (("provenance",) if node.attrib["name"] == "reasoning_summary" else ()), "EVIDENCE_DIMENSION_SHAPE_INVALID")
        status = xml_text(node, "status", "EVIDENCE_DIMENSION_STATUS_INVALID")
        require("EVIDENCE_DIMENSION_STATUS_INVALID", status in EVIDENCE_STATES and status != "complete")
        require("EVIDENCE_DIMENSION_REASON_INVALID", xml_text(node, "missing_reason", "EVIDENCE_DIMENSION_REASON_INVALID") != "null")
    require("EVIDENCE_OVERALL_STATUS_INVALID", xml_text(completeness, "overall_status", "EVIDENCE_OVERALL_STATUS_INVALID") == "pointer-only")
    usage = xml_child(root, "usage", "EVIDENCE_USAGE_MISSING")
    xml_closed(usage, ("status", "metric_kind", "source", "source_scope", "measured_at", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens", "unavailable_reason"), "EVIDENCE_USAGE_SHAPE_INVALID")
    require("EVIDENCE_USAGE_INVALID", xml_text(usage, "status", "EVIDENCE_USAGE_INVALID") == "unavailable" and all(xml_text(usage, tag, "EVIDENCE_USAGE_INVALID") == "null" for tag in ("metric_kind", "source", "source_scope", "measured_at", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")) and xml_text(usage, "unavailable_reason", "EVIDENCE_USAGE_INVALID") != "null")
    security = xml_child(root, "security", "EVIDENCE_SECURITY_MISSING")
    xml_closed(security, ("snapshot_classification", "structural_redaction_result", "secret_pii_hardening", "retention_metadata", "purge_policy"), "EVIDENCE_SECURITY_SHAPE_INVALID")
    require("EVIDENCE_SECURITY_INVALID", xml_text(security, "snapshot_classification", "EVIDENCE_SECURITY_INVALID") == "sanitized" and xml_text(security, "structural_redaction_result", "EVIDENCE_SECURITY_INVALID") == "not-applicable-pointer-only" and all(xml_text(security, tag, "EVIDENCE_SECURITY_INVALID") != "null" for tag in ("secret_pii_hardening", "retention_metadata", "purge_policy")))
    integrity = xml_child(root, "integrity", "EVIDENCE_INTEGRITY_MISSING")
    xml_closed(integrity, ("canonical_content_checksum", "result", "verification_notes"), "EVIDENCE_INTEGRITY_SHAPE_INVALID")
    checksum_node = xml_child(integrity, "canonical_content_checksum", "EVIDENCE_INTEGRITY_INVALID")
    require("EVIDENCE_INTEGRITY_INVALID", checksum_node.attrib == {"algorithm": "sha-256"} and checksum_node.text == evidence_canonical_checksum(root) and xml_text(integrity, "result", "EVIDENCE_INTEGRITY_INVALID") == "verified")
    completion = xml_child(root, "completion_record", "EVIDENCE_COMPLETION_MISSING")
    xml_closed(completion, ("agent_run_id", "handoff_id", "terminal_status", "summary", "changed_files", "read_files", "validations", "material_attempts", "known_errors", "decisions", "residual_risks", "next_destination"), "EVIDENCE_COMPLETION_SHAPE_INVALID")
    require("EVIDENCE_COMPLETION_IDENTITY_MISMATCH", xml_text(completion, "agent_run_id", "EVIDENCE_COMPLETION_IDENTITY_MISMATCH") == identity_values["agent_run_id"] and xml_text(completion, "handoff_id", "EVIDENCE_COMPLETION_IDENTITY_MISMATCH") == identity_values["handoff_id"])
    require("EVIDENCE_COMPLETION_TERMINAL_INVALID", xml_text(completion, "terminal_status", "EVIDENCE_COMPLETION_TERMINAL_INVALID") == "completed")
    require("EVIDENCE_COMPLETION_DECISION_MISMATCH", [node.text for node in xml_child(completion, "decisions", "EVIDENCE_COMPLETION_DECISION_MISMATCH")] == [decision])
    require("EVIDENCE_COMPLETION_DESTINATION_INVALID", xml_text(completion, "next_destination", "EVIDENCE_COMPLETION_DESTINATION_INVALID") == "loki-manual-qa orchestrator")
    require("EVIDENCE_COMPLETION_CHANGED_FILES_INVALID", [node.text for node in xml_child(completion, "changed_files", "EVIDENCE_COMPLETION_CHANGED_FILES_INVALID")] == ["none"])
    policy = xml_child(root, "evidence_policy", "EVIDENCE_POLICY_MISSING")
    xml_closed(policy, ("mode", "gap_handling", "capture_owner", "retrospective_dispatch"), "EVIDENCE_POLICY_SHAPE_INVALID")
    require("EVIDENCE_POLICY_INVALID", {child.tag: child.text for child in policy} == {"mode": "evidence-first", "gap_handling": "preserve-gap", "capture_owner": "collector-only", "retrospective_dispatch": "explicit-only"})
    return identity_values


def validate_manual_qa_command_ownership(package_root: Path) -> list[str]:
    skills_root = package_root / "skills"
    require("MANUAL_QA_COMMAND_SCAN_ROOT_MISSING", skills_root.is_dir())
    legacy = re.compile(r"manual_steps|playtest\s+question|pending-human-validation", re.IGNORECASE)
    action = re.compile(r"(?:deriv\w*|present\w*|render\w*|collect\w*|colet\w*|promot\w*|reconcil\w*|accept\w*)[^\n]{0,100}manual[- ]qa|manual[- ]qa[^\n]{0,100}(?:deriv\w*|present\w*|render\w*|collect\w*|colet\w*|promot\w*|reconcil\w*|accept\w*)", re.IGNORECASE)
    allowed = re.compile(r"\b(?:do not|never|nao|não|only|alone|unico|único|reserve\w*|reject\w*|block\w*|prohibit\w*|forbid\w*|handoff|ready-for-manual-qa|manual-qa-not-required|manual-qa-not-evaluated)\b", re.IGNORECASE)
    scanned: list[str] = []
    for bundle in sorted(skills_root.glob("loki-*")):
        if not bundle.is_dir() or bundle.name == "loki-manual-qa":
            continue
        for path in sorted(bundle.rglob("*.md")):
            scanned.append(path.relative_to(package_root).as_posix())
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                require(f"MANUAL_QA_FOREIGN_LEGACY_CONTRACT:{path.relative_to(package_root)}:{lineno}", legacy.search(line) is None)
                if action.search(line):
                    require(f"MANUAL_QA_FOREIGN_OWNER:{path.relative_to(package_root)}:{lineno}", allowed.search(line) is not None)
    require("MANUAL_QA_COMMAND_SCAN_EMPTY", bool(scanned))
    return scanned


def validate_digest(value: Any, code: str) -> None:
    require(code, isinstance(value, str) and DIGEST_RE.fullmatch(value) is not None)


def validate_ids(value: dict[str, Any]) -> None:
    require("RUN_ID_INVALID", isinstance(value.get("run_id"), str) and RUN_RE.fullmatch(value["run_id"]) is not None)
    require("EXECUTION_ID_INVALID", isinstance(value.get("execution_id"), str) and EXEC_RE.fullmatch(value["execution_id"]) is not None)


def validate_locator(value: Any, code: str, *, fragment: bool = False) -> None:
    require(code, nonempty(value) and "\\" not in value)
    path, marker, suffix = value.partition("#")
    require(code, (not marker or fragment) and (not marker or bool(suffix)))
    pure = PurePosixPath(path)
    require(code, not pure.is_absolute() and ".." not in pure.parts and "." not in pure.parts and len(pure.parts) >= 2)
    require(code, pure.parts[0] == "planos")


def validate_timestamp(value: Any, code: str) -> None:
    require(code, isinstance(value, str) and value.endswith("Z"))
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ContractError(code) from exc
    require(code, parsed.utcoffset() is not None and parsed.utcoffset().total_seconds() == 0)


HANDOFF_KEYS = {"schema_version", "status", "run_id", "execution_id", "plan_directory", "automatic_evidence_refs", "manual_qa_result_ref", "manual_qa_attestation_ref", "task_refs", "acceptance_criterion_refs", "gate_refs", "changed_target_refs", "reason"}
SOURCE_KEYS = {"schema_version", "source_kind", "source_ref", "source_digest", "source_order", "applicability", "not_applicable_reason", "task_refs", "acceptance_criterion_refs", "gate_refs", "changed_surface_refs", "observable_fact_refs", "observable_fact_digests", "observable_fact_statements", "guide_fact_bindings", "environment", "prerequisites", "initial_state", "actions", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit", "runtime_qa_proposal_ref", "runtime_qa_proposal_digest"}
CATALOG_KEYS = {"schema_version", "run_id", "execution_id", "plan_directory", "state_ref", "state_digest", "handoff_ref", "handoff_digest", "candidate_refs", "candidate_digests", "sources", "applicable_source_refs", "not_applicable_source_refs", "coverage_digest", "catalog_digest"}
PROPOSAL_KEYS = {"schema_version", "run_id", "execution_id", "caller", "agent", "allowed_writes", "candidate_ref", "candidate_digest", "source_kind", "applicability", "not_applicable_reason", "environment", "prerequisites", "initial_state", "actions", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit", "evidence_refs", "completion_record"}
STEP_KEYS = {"schema_version", "id", "source_kind", "source_ref", "source_order", "title", "environment", "prerequisites", "initial_state", "actions", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit"}
DASHBOARD_KEYS = {"schema_version", "run_id", "execution_id", "plan_directory", "state_ref", "state_digest", "handoff_ref", "handoff_digest", "implementation_result_ref", "implementation_result_digest", "implementation_dashboard_ref", "implementation_dashboard_digest", "implementation_consistency_ref", "implementation_consistency_digest", "demand_ref", "demand_digest", "analysis_ref", "analysis_digest", "source_catalog_ref", "source_catalog_digest", "applicable_source_refs", "not_applicable_source_refs", "steps", "applicable_steps_digest", "dashboard_digest"}
ATTESTATION_KEYS = {"schema_version", "run_id", "execution_id", "applicable_steps_digest", "demand_digest", "analysis_digest", "human_statement", "declaration", "attestation_review_ref", "attestation_review_digest", "recorded_at"}
ASSESSMENT_KEYS = {"schema_version", "run_id", "execution_id", "human_statement", "statement_digest", "dashboard_ref", "dashboard_digest", "applicable_steps_digest", "assessor_identity", "assessment_owner", "evaluator_policy_id", "evaluator_policy_digest", "decision", "rationale", "signals", "assessment_digest"}
ASSESSMENT_SIGNAL_KEYS = {"explicit_completed_all", "ambiguous", "negated", "future_intent", "partial_scope"}
ATTESTATION_REVIEW_KEYS = {"schema_version", "run_id", "execution_id", "reviewer_identity", "independent_agent_run_evidence_ref", "independent_agent_run_evidence_digest", "statement_digest", "dashboard_ref", "dashboard_digest", "applicable_steps_digest", "evaluator_policy_id", "evaluator_policy_digest", "assessment_ref", "assessment_digest", "signals", "decision", "rationale", "confidence", "completion_record", "review_digest"}
REPORT_KEYS = {"schema_version", "report_id", "run_id", "execution_id", "status", "kind", "summary", "impact", "next_action", "recorded_at", "resolution_ref", "resolution_digest", "resolved_at", "revalidation_refs", "revalidation_digests"}
INTERACTION_KEYS = {"schema_version", "run_id", "execution_id", "status", "attestation_ref", "attestation_digest", "report_ref", "report_digest", "interaction_digest"}
TRANSACTION_KEYS = {"schema_version", "transaction_id", "run_id", "execution_id", "batch_kind", "transition_intent_digest", "predecessor_transaction_id", "predecessor_transaction_digest", "phase", "next_target_index", "owner", "target_refs", "before_digests", "intended_after_digests", "published_refs", "published_digests", "residue_refs", "residue_digests", "attestation_ref", "attestation_digest", "transaction_digest"}
TERMINAL_PROJECTION_KEYS = {"source_catalog_ref", "source_catalog_digest", "transaction_ref", "transaction_id", "covered_task_refs", "covered_acceptance_criterion_refs", "covered_gate_refs", "covered_changed_surface_refs", "promoted_task_refs", "promoted_acceptance_criterion_refs", "promoted_gate_refs", "canonical_asset_refs", "canonical_asset_digests", "validator_refs", "validator_digests", "audit_refs", "audit_digests", "final_plan_status", "blockers", "resume"}
RESULT_KEYS = {"schema_version", "run_id", "execution_id", "status", "state_ref", "state_digest", "handoff_ref", "handoff_digest", "dashboard_ref", "dashboard_digest", "interaction_ref", "interaction_digest", "attestation_ref", "attestation_digest", "report_ref", "report_digest", "applicable_steps_digest", "demand_revalidation_digest", "automatic_gate_refs", "automatic_gate_digests", "reconciled_handoff_ref", "next_action", "result_digest"} | TERMINAL_PROJECTION_KEYS
CONSISTENCY_KEYS = ({"schema_version", "run_id", "execution_id", "state_ref", "state_digest", "handoff_ref", "handoff_digest", "dashboard_ref", "dashboard_digest", "interaction_ref", "interaction_digest", "attestation_ref", "attestation_digest", "report_ref", "report_digest", "result_ref", "result_digest", "applicable_steps_digest", "demand_revalidation_digest", "automatic_gate_refs", "automatic_gate_digests", "reconciled_handoff_ref", "consistency_digest"} | TERMINAL_PROJECTION_KEYS)


def validate_handoff(value: Any) -> dict[str, Any]:
    p = closed("HANDOFF_SHAPE_INVALID", value, HANDOFF_KEYS)
    require("HANDOFF_SCHEMA_CURRENT_ONLY", type(p["schema_version"]) is int and p["schema_version"] == 2)
    require("HANDOFF_NOT_ELIGIBLE", p["status"] == "ready-for-manual-qa" and p["reason"] is None)
    validate_ids(p)
    validate_locator(p["plan_directory"] + "/_", "PLAN_DIRECTORY_INVALID")
    expected_result = f'{p["plan_directory"]}/builds/manual-qa/result.json'
    expected_attestation = f'{p["plan_directory"]}/interaction/manual-qa/{p["run_id"]}/attestation.json'
    require("HANDOFF_RESULT_ANCHOR_INVALID", p["manual_qa_result_ref"] == expected_result)
    require("HANDOFF_ATTESTATION_ANCHOR_INVALID", p["manual_qa_attestation_ref"] == expected_attestation)
    require("AUTOMATIC_EVIDENCE_INVALID", isinstance(p["automatic_evidence_refs"], list) and bool(p["automatic_evidence_refs"]) and len(p["automatic_evidence_refs"]) == len(set(p["automatic_evidence_refs"])))
    for key in ("automatic_evidence_refs", "task_refs", "acceptance_criterion_refs", "gate_refs"):
        require("HANDOFF_REF_ARRAY_INVALID", isinstance(p[key], list) and bool(p[key]) and len(p[key]) == len(set(p[key])))
        for ref in p[key]: validate_locator(ref, "HANDOFF_REF_INVALID", fragment=True)
    require("HANDOFF_CHANGED_TARGETS_INVALID", isinstance(p["changed_target_refs"], list) and bool(p["changed_target_refs"]) and len(p["changed_target_refs"]) == len(set(p["changed_target_refs"])))
    for ref in p["changed_target_refs"]:
        require("HANDOFF_CHANGED_TARGET_REF_INVALID", nonempty(ref) and "#" not in ref and "\\" not in ref and not PurePosixPath(ref).is_absolute() and ".." not in PurePosixPath(ref).parts)
    return p


def validate_step(value: Any, *, expected_id: str | None = None, expected_order: int | None = None) -> dict[str, Any]:
    p = closed("STEP_SHAPE_INVALID", value, STEP_KEYS)
    require("STEP_SCHEMA_CURRENT_ONLY", type(p["schema_version"]) is int and p["schema_version"] == 1)
    require("STEP_ID_INVALID", isinstance(p["id"], str) and STEP_RE.fullmatch(p["id"]) is not None)
    require("STEP_SOURCE_KIND_INVALID", p["source_kind"] in {"acceptance-criterion", "human-gate", "changed-surface"})
    if p["source_kind"] == "changed-surface":
        require("STEP_SOURCE_REF_INVALID", nonempty(p["source_ref"]) and not PurePosixPath(p["source_ref"]).is_absolute() and ".." not in PurePosixPath(p["source_ref"]).parts)
    else:
        validate_locator(p["source_ref"], "STEP_SOURCE_REF_INVALID", fragment=True)
    require("STEP_SOURCE_ORDER_INVALID", type(p["source_order"]) is int and p["source_order"] >= 0)
    for key in ("title", "environment", "prerequisites", "initial_state", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit"):
        require("STEP_TEXT_INVALID", nonempty(p[key]))
    require("STEP_ACTIONS_INVALID", isinstance(p["actions"], list) and bool(p["actions"]) and all(nonempty(item) for item in p["actions"]))
    if expected_id is not None:
        require("STEP_ID_ORDER_MISMATCH", p["id"] == expected_id)
    if expected_order is not None:
        require("STEP_SOURCE_ORDER_MISMATCH", p["source_order"] == expected_order)
    return p


PLACEHOLDER_RE = re.compile(r"\b(?:todo|tbd|placeholder|lorem ipsum|fill (?:this|me)|coming soon)\b|<[^>]+>", re.IGNORECASE)


def validate_guide(
    p: dict[str, Any], prefix: str, candidate_ref: str, candidate_digest: str, *, require_fact_bindings: bool = False
) -> None:
    guide_keys = ("environment", "prerequisites", "initial_state", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit")
    values = [p[key] for key in guide_keys] + list(p.get("actions", []))
    require(f"{prefix}_GUIDE_INCOMPLETE", all(nonempty(value) for value in values) and bool(p.get("actions")))
    require(f"{prefix}_GUIDE_TOO_SHORT", all(len(value.strip()) >= 24 for value in values))
    require(f"{prefix}_GUIDE_PLACEHOLDER", not any(PLACEHOLDER_RE.search(value) for value in values))
    require(f"{prefix}_GUIDE_UNBOUND", sum(candidate_ref in value for value in values) >= 2)
    require(f"{prefix}_GUIDE_SOURCE_FACT_UNBOUND", any(candidate_digest in value for value in values))
    if not require_fact_bindings:
        return
    fact_refs = p.get("observable_fact_refs")
    fact_digests = p.get("observable_fact_digests")
    fact_statements = p.get("observable_fact_statements")
    require(
        f"{prefix}_OBSERVABLE_FACT_BINDING_INVALID",
        isinstance(fact_refs, list)
        and isinstance(fact_digests, list)
        and isinstance(fact_statements, list)
        and bool(fact_refs)
        and len(fact_refs) == len(fact_digests) == len(fact_statements)
        and len(fact_refs) == len(set(fact_refs)),
    )
    for fact_ref, fact_digest, fact_statement in zip(fact_refs, fact_digests, fact_statements):
        require(f"{prefix}_OBSERVABLE_FACT_REF_INVALID", nonempty(fact_ref))
        validate_digest(fact_digest, f"{prefix}_OBSERVABLE_FACT_DIGEST_INVALID")
        require(f"{prefix}_OBSERVABLE_FACT_STATEMENT_INVALID", nonempty(fact_statement))
        require(
            f"{prefix}_GUIDE_OBSERVABLE_FACT_UNBOUND",
            any(fact_ref in value and fact_digest in value and fact_statement in value for value in values),
        )
    bindings = closed(f"{prefix}_GUIDE_FACT_BINDINGS_SHAPE_INVALID", p.get("guide_fact_bindings"), set(GUIDE_FIELDS))
    fact_rows = {(ref, item_digest): statement for ref, item_digest, statement in zip(fact_refs, fact_digests, fact_statements)}
    for field in GUIDE_FIELDS:
        binding = closed(f"{prefix}_GUIDE_FIELD_BINDING_SHAPE_INVALID", bindings[field], {"fact_ref", "fact_digest"})
        pair = (binding["fact_ref"], binding["fact_digest"])
        require(f"{prefix}_GUIDE_FIELD_BINDING_UNKNOWN", pair in fact_rows)
        material = " ".join(p[field]) if isinstance(p[field], list) else p[field]
        require(f"{prefix}_GUIDE_FIELD_FACT_UNBOUND:{field}", binding["fact_ref"] in material and binding["fact_digest"] in material and fact_rows[pair] in material)


def guide_signature(
    p: dict[str, Any], *, normalization_values: list[str] | None = None
) -> str:
    values = [p[key] for key in ("environment", "prerequisites", "initial_state", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit")] + p["actions"]
    material = " ".join(values).casefold()
    for value in sorted(
        {p["source_ref"], *(normalization_values or [])}, key=len, reverse=True
    ):
        material = material.replace(value.casefold(), " <normalized-fact> ")
    material = re.sub(r"(?:planos|src)/[^\s,.;:]+", " <normalized-ref> ", material)
    material = re.sub(r"sha256:[0-9a-f]{64}", " <normalized-digest> ", material)
    material = re.sub(r"\bmq-\d+\b|\bac-\d+\b", " <normalized-id> ", material)
    return re.sub(r"\s+", " ", material).strip()


def guide_similarity(left: str, right: str) -> float:
    left_tokens = set(re.findall(r"[a-z0-9-]{4,}", left))
    right_tokens = set(re.findall(r"[a-z0-9-]{4,}", right))
    if not left_tokens or not right_tokens:
        return 1.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def validate_source(value: Any, *, expected_order: int | None = None) -> dict[str, Any]:
    p = closed("SOURCE_SHAPE_INVALID", value, SOURCE_KEYS)
    require("SOURCE_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    require("SOURCE_KIND_INVALID", p["source_kind"] in {"acceptance-criterion", "human-gate", "changed-surface"})
    require("SOURCE_REF_INVALID", nonempty(p["source_ref"]))
    validate_digest(p["source_digest"], "SOURCE_DIGEST_INVALID")
    require("SOURCE_ORDER_INVALID", type(p["source_order"]) is int and p["source_order"] >= 0)
    if expected_order is not None: require("SOURCE_ORDER_MISMATCH", p["source_order"] == expected_order)
    require("SOURCE_APPLICABILITY_INVALID", p["applicability"] in {"applicable", "not-applicable"})
    require("SOURCE_REASON_INVALID", (p["applicability"] == "applicable" and p["not_applicable_reason"] is None) or (p["applicability"] == "not-applicable" and nonempty(p["not_applicable_reason"])))
    require("SOURCE_HUMAN_GATE_NOT_APPLICABLE", p["source_kind"] != "human-gate" or p["applicability"] == "applicable")
    coverage = {"acceptance-criterion": "acceptance_criterion_refs", "human-gate": "gate_refs", "changed-surface": "changed_surface_refs"}[p["source_kind"]]
    for key in ("task_refs", "acceptance_criterion_refs", "gate_refs", "changed_surface_refs"):
        require("SOURCE_COVERAGE_ARRAY_INVALID", isinstance(p[key], list) and len(p[key]) == len(set(p[key])))
    require("SOURCE_KIND_COVERAGE_INVALID", p["source_ref"] in p[coverage])
    validate_locator(p["runtime_qa_proposal_ref"], "SOURCE_PROPOSAL_REF_INVALID", fragment=True)
    validate_digest(p["runtime_qa_proposal_digest"], "SOURCE_PROPOSAL_DIGEST_INVALID")
    require("SOURCE_ACTIONS_INVALID", isinstance(p["actions"], list))
    validate_guide(p, "SOURCE", p["source_ref"], p["source_digest"], require_fact_bindings=p["applicability"] == "applicable")
    return p


def catalog_coverage_material(p: dict[str, Any]) -> dict[str, Any]:
    return {"candidate_refs": p["candidate_refs"], "candidate_digests": p["candidate_digests"], "source_refs": [row["source_ref"] for row in p["sources"]], "applicable_source_refs": p["applicable_source_refs"], "not_applicable_source_refs": p["not_applicable_source_refs"]}


def validate_catalog(value: Any) -> dict[str, Any]:
    p = closed("CATALOG_SHAPE_INVALID", value, CATALOG_KEYS)
    require("CATALOG_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    validate_ids(p); validate_locator(p["plan_directory"] + "/_", "CATALOG_PLAN_INVALID")
    for key in ("state_ref", "handoff_ref"): validate_locator(p[key], "CATALOG_REF_INVALID", fragment=True)
    for key in ("state_digest", "handoff_digest", "coverage_digest", "catalog_digest"): validate_digest(p[key], "CATALOG_DIGEST_INVALID")
    require("CATALOG_CANDIDATES_INVALID", isinstance(p["candidate_refs"], list) and bool(p["candidate_refs"]) and len(p["candidate_refs"]) == len(set(p["candidate_refs"])) and len(p["candidate_refs"]) == len(p["candidate_digests"]))
    require("CATALOG_SOURCES_INVALID", isinstance(p["sources"], list) and len(p["sources"]) == len(p["candidate_refs"]))
    for index, source in enumerate(p["sources"]): validate_source(source, expected_order=index)
    normalization_values = p["candidate_refs"] + [
        source["expected_result"] for source in p["sources"]
    ]
    signatures = [
        guide_signature(source, normalization_values=normalization_values)
        for source in p["sources"]
    ]
    require("CATALOG_MATERIALLY_REPEATED_GUIDE", len(signatures) == len(set(signatures)))
    require(
        "CATALOG_NEAR_DUPLICATE_GUIDE",
        all(
            guide_similarity(signatures[left], signatures[right]) < 0.92
            for left in range(len(signatures))
            for right in range(left + 1, len(signatures))
        ),
    )
    require("CATALOG_SOURCE_REF_MISMATCH", [row["source_ref"] for row in p["sources"]] == p["candidate_refs"])
    require("CATALOG_SOURCE_DIGEST_MISMATCH", [row["source_digest"] for row in p["sources"]] == p["candidate_digests"])
    applicable = [row["source_ref"] for row in p["sources"] if row["applicability"] == "applicable"]
    not_applicable = [row["source_ref"] for row in p["sources"] if row["applicability"] == "not-applicable"]
    require("CATALOG_APPLICABILITY_MISMATCH", p["applicable_source_refs"] == applicable and p["not_applicable_source_refs"] == not_applicable and bool(applicable))
    require("CATALOG_COVERAGE_DIGEST_MISMATCH", p["coverage_digest"] == digest(catalog_coverage_material(p)))
    require("CATALOG_DIGEST_MISMATCH", p["catalog_digest"] == digest(p, omit="catalog_digest"))
    return p


def validate_proposal(value: Any) -> dict[str, Any]:
    p = closed("PROPOSAL_SHAPE_INVALID", value, PROPOSAL_KEYS); validate_ids(p)
    require("PROPOSAL_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    require("PROPOSAL_DISPATCH_INVALID", p["caller"] == "loki-manual-qa" and p["agent"] == "runtime-qa" and p["allowed_writes"] == [])
    require("PROPOSAL_CANDIDATE_REF_INVALID", nonempty(p["candidate_ref"]))
    validate_digest(p["candidate_digest"], "PROPOSAL_CANDIDATE_DIGEST_INVALID")
    require("PROPOSAL_SOURCE_KIND_INVALID", p["source_kind"] in {"acceptance-criterion", "human-gate", "changed-surface"})
    require("PROPOSAL_APPLICABILITY_INVALID", p["applicability"] in {"applicable", "not-applicable"})
    require("PROPOSAL_REASON_INVALID", (p["applicability"] == "applicable" and p["not_applicable_reason"] is None) or (p["applicability"] == "not-applicable" and nonempty(p["not_applicable_reason"])))
    require("PROPOSAL_HUMAN_GATE_NOT_APPLICABLE", p["source_kind"] != "human-gate" or p["applicability"] == "applicable")
    require("PROPOSAL_EVIDENCE_REFS_INVALID", isinstance(p["evidence_refs"], list) and bool(p["evidence_refs"]) and len(p["evidence_refs"]) == len(set(p["evidence_refs"])))
    for ref in p["evidence_refs"]: validate_locator(ref, "PROPOSAL_EVIDENCE_REF_INVALID", fragment=True)
    require("PROPOSAL_ACTIONS_INVALID", isinstance(p["actions"], list))
    validate_guide(p, "PROPOSAL", p["candidate_ref"], p["candidate_digest"])
    completion = closed("PROPOSAL_COMPLETION_SHAPE_INVALID", p["completion_record"], {"status", "validators", "gates", "risks", "next_destination"})
    require("PROPOSAL_COMPLETION_INVALID", completion["status"] == "completed" and isinstance(completion["validators"], list) and bool(completion["validators"]) and completion["gates"] == [] and isinstance(completion["risks"], list) and completion["next_destination"] == "loki-manual-qa orchestrator")
    return p


def validate_transaction(value: Any) -> dict[str, Any]:
    p = closed("TRANSACTION_SHAPE_INVALID", value, TRANSACTION_KEYS)
    require("TRANSACTION_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1); validate_ids(p)
    require("TRANSACTION_ID_INVALID", isinstance(p["transaction_id"], str) and TRANSACTION_ID_RE.fullmatch(p["transaction_id"]) is not None)
    validate_digest(p["transition_intent_digest"], "TRANSACTION_INTENT_DIGEST_INVALID")
    require("TRANSACTION_INTENT_DIGEST_MISMATCH", p["transition_intent_digest"] == digest({"schema_version": 1, "batch_kind": p["batch_kind"], "target_refs": p["target_refs"]}))
    require("TRANSACTION_ID_MISMATCH", p["transaction_id"] == transaction_identity(p["run_id"], p["execution_id"], p["batch_kind"], p["transition_intent_digest"], p["predecessor_transaction_id"]))
    require("TRANSACTION_BATCH_KIND_INVALID", p["batch_kind"] in {"initial", "issue", "terminal", "terminal-reject"})
    predecessor_absent = p["predecessor_transaction_id"] is None and p["predecessor_transaction_digest"] is None
    predecessor_present = isinstance(p["predecessor_transaction_id"], str) and TRANSACTION_ID_RE.fullmatch(p["predecessor_transaction_id"]) is not None and isinstance(p["predecessor_transaction_digest"], str) and DIGEST_RE.fullmatch(p["predecessor_transaction_digest"]) is not None
    require("TRANSACTION_PREDECESSOR_PAIR_INVALID", predecessor_absent or predecessor_present)
    require("TRANSACTION_PREDECESSOR_INVALID", predecessor_absent if p["batch_kind"] == "initial" else predecessor_present)
    if predecessor_present:
        require("TRANSACTION_PREDECESSOR_SELF_REFERENCE", p["predecessor_transaction_id"] != p["transaction_id"])
    phases_by_batch = {
        "initial": {"journal-created", "manual-publishing", "committed", "recovery-required"},
        "issue": {"journal-created", "manual-publishing", "committed", "recovery-required"},
        "terminal": {"journal-created", "assessment-published", "review-published", "attested", "gates-promoted", "canonical-promoted", "consistency-published", "committed", "recovery-required"},
        "terminal-reject": {"journal-created", "assessment-published", "review-published", "committed", "recovery-required"},
    }
    require("TRANSACTION_PHASE_INVALID", p["phase"] in phases_by_batch[p["batch_kind"]])
    require("TRANSACTION_OWNER_INVALID", p["owner"] == "loki-manual-qa-orchestrator")
    for refs_key, digests_key in (("target_refs", "before_digests"), ("target_refs", "intended_after_digests"), ("published_refs", "published_digests"), ("residue_refs", "residue_digests")):
        require("TRANSACTION_PAIR_INVALID", isinstance(p[refs_key], list) and isinstance(p[digests_key], list) and len(p[refs_key]) == len(p[digests_key]) and len(p[refs_key]) == len(set(p[refs_key])))
        for item in p[digests_key]: validate_digest(item, "TRANSACTION_DIGEST_INVALID")
    require("TRANSACTION_TARGETS_EMPTY", bool(p["target_refs"]))
    require("TRANSACTION_CURSOR_INVALID", type(p["next_target_index"]) is int and p["next_target_index"] == len(p["published_refs"]) and 0 <= p["next_target_index"] <= len(p["target_refs"]))
    require("TRANSACTION_PUBLISHED_NOT_PREFIX", p["published_refs"] == p["target_refs"][:p["next_target_index"]])
    require("TRANSACTION_ATTESTATION_PAIR_INVALID", (p["attestation_ref"] is None) == (p["attestation_digest"] is None))
    if p["attestation_ref"] is not None:
        validate_locator(p["attestation_ref"], "TRANSACTION_ATTESTATION_REF_INVALID", fragment=True); validate_digest(p["attestation_digest"], "TRANSACTION_ATTESTATION_DIGEST_INVALID")
    if p["batch_kind"] in {"initial", "issue", "terminal-reject"}:
        require("TRANSACTION_ATTESTATION_PHASE_INVALID", p["attestation_ref"] is None)
    elif p["phase"] in {"journal-created", "assessment-published", "review-published"}:
        require("TRANSACTION_ATTESTATION_PHASE_INVALID", p["attestation_ref"] is None)
    elif p["phase"] != "recovery-required":
        require("TRANSACTION_ATTESTATION_PHASE_INVALID", p["attestation_ref"] is not None)
    if p["phase"] == "journal-created":
        require("TRANSACTION_PHASE_CURSOR_INVALID", p["next_target_index"] == 0)
    if p["batch_kind"] in {"terminal", "terminal-reject"} and p["phase"] == "assessment-published":
        require("TRANSACTION_PHASE_CURSOR_INVALID", p["next_target_index"] == 1)
    if p["batch_kind"] in {"terminal", "terminal-reject"} and p["phase"] == "review-published":
        require("TRANSACTION_PHASE_CURSOR_INVALID", p["next_target_index"] == 2)
    if p["batch_kind"] == "terminal" and p["phase"] == "attested":
        require("TRANSACTION_PHASE_CURSOR_INVALID", p["next_target_index"] == 3)
    tasks_indexes = [index for index, ref in enumerate(p["target_refs"]) if ref.endswith("/tasks.md")]
    if p["batch_kind"] == "terminal" and tasks_indexes:
        tasks_index = tasks_indexes[0]
        if p["phase"] == "gates-promoted":
            require("TRANSACTION_PHASE_CURSOR_INVALID", p["next_target_index"] == tasks_index)
        if p["phase"] == "canonical-promoted":
            require("TRANSACTION_PHASE_CURSOR_INVALID", tasks_index + 4 <= p["next_target_index"] < len(p["target_refs"]))
    if p["phase"] in {"consistency-published", "committed"}:
        require("TRANSACTION_PHASE_CURSOR_INVALID", p["next_target_index"] == len(p["target_refs"]))
    if p["phase"] == "committed": require("TRANSACTION_COMMITTED_RESIDUE", p["residue_refs"] == [] and p["published_refs"] == p["target_refs"])
    if p["phase"] == "recovery-required":
        require("TRANSACTION_RECOVERY_WITHOUT_RESIDUE", bool(p["residue_refs"]) or p["next_target_index"] == 0)
        require("TRANSACTION_RECOVERY_RESIDUE_NOT_PREFIX", p["residue_refs"] == p["published_refs"] and p["residue_digests"] == p["published_digests"])
    require("TRANSACTION_DIGEST_MISMATCH", p["transaction_digest"] == digest(p, omit="transaction_digest"))
    return p


def transaction_identity(run_id: str, execution_id: str, batch_kind: str, transition_intent_digest: str, predecessor_transaction_id: str | None) -> str:
    value = digest({"schema_version": 1, "run_id": run_id, "execution_id": execution_id, "batch_kind": batch_kind, "transition_intent_digest": transition_intent_digest, "predecessor_transaction_id": predecessor_transaction_id})
    return "manual-qa-transaction-v1:" + value.split(":", 1)[1]


def bind_transaction_identity(transaction: dict[str, Any]) -> None:
    transaction["transition_intent_digest"] = digest({"schema_version": 1, "batch_kind": transaction["batch_kind"], "target_refs": transaction["target_refs"]})
    transaction["transaction_id"] = transaction_identity(transaction["run_id"], transaction["execution_id"], transaction["batch_kind"], transaction["transition_intent_digest"], transaction["predecessor_transaction_id"])


def validate_semantic_assessment(value: Any) -> dict[str, Any]:
    p = closed("ASSESSMENT_SHAPE_INVALID", value, ASSESSMENT_KEYS)
    require("ASSESSMENT_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1); validate_ids(p)
    require("ASSESSMENT_STATEMENT_INVALID", nonempty(p["human_statement"]))
    require("ASSESSMENT_STATEMENT_DIGEST_MISMATCH", p["statement_digest"] == bytes_digest(p["human_statement"].encode("utf-8")))
    validate_locator(p["dashboard_ref"], "ASSESSMENT_DASHBOARD_REF_INVALID")
    for key in ("dashboard_digest", "applicable_steps_digest", "assessment_digest"): validate_digest(p[key], "ASSESSMENT_DIGEST_INVALID")
    require("ASSESSMENT_ACTOR_INVALID", p["assessor_identity"] == ASSESSOR_IDENTITY and p["assessment_owner"] == ASSESSMENT_OWNER)
    require("ASSESSMENT_POLICY_INVALID", p["evaluator_policy_id"] == EVALUATOR_POLICY_ID and p["evaluator_policy_digest"] == EVALUATOR_POLICY_DIGEST)
    signals = closed("ASSESSMENT_SIGNALS_SHAPE_INVALID", p["signals"], ASSESSMENT_SIGNAL_KEYS)
    require("ASSESSMENT_SIGNALS_TYPE_INVALID", all(type(value) is bool for value in signals.values()))
    expected = "approve" if signals["explicit_completed_all"] and not any(signals[key] for key in ("ambiguous", "negated", "future_intent", "partial_scope")) else "reject"
    require("ASSESSMENT_DECISION_NOT_DERIVED", p["decision"] == expected)
    require("ASSESSMENT_RATIONALE_INVALID", nonempty(p["rationale"]))
    require("ASSESSMENT_DIGEST_MISMATCH", p["assessment_digest"] == digest(p, omit="assessment_digest"))
    return p


def validate_attestation_review(value: Any) -> dict[str, Any]:
    p = closed("ATTESTATION_REVIEW_SHAPE_INVALID", value, ATTESTATION_REVIEW_KEYS)
    require("ATTESTATION_REVIEW_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    validate_ids(p)
    require("ATTESTATION_REVIEWER_IDENTITY_INVALID", p["reviewer_identity"] == ATTESTATION_REVIEWER_IDENTITY and p["reviewer_identity"] not in {ASSESSOR_IDENTITY, ASSESSMENT_OWNER})
    for key in ("independent_agent_run_evidence_ref", "dashboard_ref", "assessment_ref"):
        validate_locator(p[key], "ATTESTATION_REVIEW_REF_INVALID", fragment=True)
    for key in ("independent_agent_run_evidence_digest", "statement_digest", "dashboard_digest", "applicable_steps_digest", "evaluator_policy_digest", "assessment_digest", "review_digest"):
        validate_digest(p[key], "ATTESTATION_REVIEW_DIGEST_INVALID")
    require("ATTESTATION_REVIEW_POLICY_INVALID", p["evaluator_policy_id"] == EVALUATOR_POLICY_ID and p["evaluator_policy_digest"] == EVALUATOR_POLICY_DIGEST)
    signals = closed("ATTESTATION_REVIEW_SIGNALS_SHAPE_INVALID", p["signals"], ASSESSMENT_SIGNAL_KEYS)
    require("ATTESTATION_REVIEW_SIGNALS_TYPE_INVALID", all(type(item) is bool for item in signals.values()))
    expected = "approve" if signals["explicit_completed_all"] and not any(signals[key] for key in ("ambiguous", "negated", "future_intent", "partial_scope")) else "reject"
    require("ATTESTATION_REVIEW_DECISION_NOT_DERIVED", p["decision"] == expected)
    require("ATTESTATION_REVIEW_RATIONALE_INVALID", nonempty(p["rationale"]))
    require("ATTESTATION_REVIEW_CONFIDENCE_INVALID", p["confidence"] in {"low", "medium", "high"})
    completion = closed("ATTESTATION_REVIEW_COMPLETION_SHAPE_INVALID", p["completion_record"], {"status", "validators", "gates", "risks", "success_destination", "failure_destination"})
    require("ATTESTATION_REVIEW_COMPLETION_INVALID", completion["status"] == "completed" and isinstance(completion["validators"], list) and bool(completion["validators"]) and completion["gates"] == [] and isinstance(completion["risks"], list) and completion["success_destination"] == "loki-manual-qa orchestrator" and nonempty(completion["failure_destination"]))
    require("ATTESTATION_REVIEW_DIGEST_MISMATCH", p["review_digest"] == digest(p, omit="review_digest"))
    return p


def canonical_transaction_targets(reader: Any, plan: str, state: dict[str, Any], handoff: dict[str, Any], candidates: list[dict[str, Any]] | None = None, *, terminal: bool = False) -> list[str]:
    proposal_refs = [f"{plan}/builds/manual-qa/proposals/{index}.json" for index, _ in enumerate(candidates or [])]
    catalog_ref = f"{plan}/builds/manual-qa/source-catalog.json"
    dashboard_ref = f"{plan}/builds/manual-qa/dashboard.json"
    run_dir = PurePosixPath(handoff["manual_qa_attestation_ref"]).parent
    interaction_ref = str(run_dir / "interaction.json")
    presentation_ref = str(run_dir / "dashboard-presentation.json")
    if terminal:
        human_gate_refs = [ref for ref in handoff["gate_refs"] if reader.read_json(ref)["kind"] == "human-validation"]
        targets = [str(run_dir / "semantic-assessment.json"), str(run_dir / "attestation-review.json"), handoff["manual_qa_attestation_ref"]] + human_gate_refs + [f"{plan}/tasks.md", state["result_ref"], state["dashboard_ref"], state["consistency_packet_ref"]] + proposal_refs + [catalog_ref, dashboard_ref, interaction_ref, handoff["manual_qa_result_ref"], f"{plan}/builds/manual-qa/consistency.json"]
    else:
        targets = proposal_refs + [catalog_ref, dashboard_ref, presentation_ref, interaction_ref, handoff["manual_qa_result_ref"]]
    require("TRANSACTION_CANONICAL_TARGET_DUPLICATE", len(targets) == len(set(targets)))
    return targets


def resume_transaction_checkpoint(value: Any) -> int:
    """Validate the persisted prefix and return the only legal resume cursor."""
    return validate_transaction(value)["next_target_index"]


def terminal_phase_for_cursor(transaction: dict[str, Any]) -> str | None:
    """Return the named terminal boundary reached by the exact cursor."""
    cursor = transaction["next_target_index"]
    targets = transaction["target_refs"]
    tasks_index = next(index for index, ref in enumerate(targets) if ref.endswith("/tasks.md"))
    first_manual_view = tasks_index + 4
    boundaries = {
        0: "journal-created",
        1: "assessment-published",
        2: "review-published",
        3: "attested",
        tasks_index: "gates-promoted",
        first_manual_view: "canonical-promoted",
        len(targets): "consistency-published",
    }
    return boundaries.get(cursor)


def normal_phase_for_cursor(transaction: dict[str, Any]) -> str | None:
    if transaction["batch_kind"] == "terminal":
        return terminal_phase_for_cursor(transaction)
    cursor = transaction["next_target_index"]
    if transaction["batch_kind"] in {"initial", "issue"}:
        if cursor == 0:
            return "manual-publishing"
        if cursor == len(transaction["target_refs"]):
            return "committed"
        return "manual-publishing"
    if transaction["batch_kind"] == "terminal-reject":
        return {0: "journal-created", 1: "assessment-published", 2: "review-published", len(transaction["target_refs"]): "committed"}.get(cursor)
    return None


def persist_transaction(root: Path, transaction_ref: str, transaction: dict[str, Any]) -> None:
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest")
    write_json(root, transaction_ref, transaction)
    validate_transaction(transaction)


def resume_transaction(
    root: Path, transaction_ref: str, intended_bytes_by_ref: dict[str, bytes]
) -> dict[str, Any]:
    """Resume the exact persisted batch state machine or prove replay is a no-op."""
    transaction = validate_transaction(
        json.loads((root / transaction_ref).read_text(encoding="utf-8"))
    )
    current_published = [
        frozen_target_digest(root, ref) for ref in transaction["published_refs"]
    ]
    require(
        "TRANSACTION_RESUME_PUBLISHED_DRIFT",
        current_published == transaction["published_digests"],
    )
    if transaction["phase"] == "committed":
        require(
            "TRANSACTION_COMMITTED_INTENDED_MISSING",
            set(intended_bytes_by_ref) == set(transaction["target_refs"]),
        )
        rederived_digests = [
            bytes_digest(intended_bytes_by_ref[ref]) for ref in transaction["target_refs"]
        ]
        require(
            "TRANSACTION_COMMITTED_REPLAY_DRIFT",
            transaction["published_refs"] == transaction["target_refs"]
            and current_published == transaction["intended_after_digests"]
            and rederived_digests == transaction["intended_after_digests"],
        )
        return {"status": "no-op", "transaction": transaction}
    if transaction["phase"] == "recovery-required":
        require(
            "TRANSACTION_RESUME_RESIDUE_INVALID",
            transaction["residue_refs"] == transaction["published_refs"]
            and transaction["residue_digests"] == transaction["published_digests"],
        )
    named_boundary = normal_phase_for_cursor(transaction)
    allowed_normal_phases = {named_boundary}
    if transaction["batch_kind"] in {"initial", "issue"} and transaction["next_target_index"] == 0:
        allowed_normal_phases.add("journal-created")
    require(
        "TRANSACTION_RESUME_PHASE_INVALID",
        transaction["phase"] == "recovery-required"
        or transaction["phase"] in allowed_normal_phases,
    )
    if transaction["batch_kind"] == "terminal":
        require(
            "TRANSACTION_RESUME_PHASE_INVALID",
            transaction["phase"] == "recovery-required" or named_boundary is not None,
        )
        attestation_ref = transaction["target_refs"][2]
        if transaction["next_target_index"] >= 3:
            attestation_digest = frozen_target_digest(root, attestation_ref)
            require("TRANSACTION_RESUME_ATTESTATION_MISSING", attestation_digest != "sha256:" + "0" * 64)
            transaction.update(attestation_ref=attestation_ref, attestation_digest=attestation_digest)
        else:
            transaction.update(attestation_ref=None, attestation_digest=None)
    remaining_refs = transaction["target_refs"][transaction["next_target_index"] :]
    for ref in remaining_refs:
        require("TRANSACTION_RESUME_INTENDED_MISSING", ref in intended_bytes_by_ref)
        index = transaction["next_target_index"]
        rederived_digest = bytes_digest(intended_bytes_by_ref[ref])
        require(
            "TRANSACTION_RESUME_INTENDED_DRIFT",
            transaction["intended_after_digests"][index]
            in {transaction["before_digests"][index], rederived_digest},
        )
        current_digest = frozen_target_digest(root, ref)
        if current_digest == transaction["intended_after_digests"][index] == rederived_digest:
            transaction["published_refs"].append(ref)
            transaction["published_digests"].append(current_digest)
            transaction["next_target_index"] += 1
            transaction["residue_refs"] = list(transaction["published_refs"])
            transaction["residue_digests"] = list(transaction["published_digests"])
            transaction["phase"] = "recovery-required"
            persist_transaction(root, transaction_ref, transaction)
            if transaction["batch_kind"] == "terminal":
                if transaction["next_target_index"] >= 3:
                    transaction.update(attestation_ref=transaction["target_refs"][2], attestation_digest=frozen_target_digest(root, transaction["target_refs"][2]))
                boundary = terminal_phase_for_cursor(transaction)
                if boundary is not None:
                    transaction["phase"] = boundary
                    persist_transaction(root, transaction_ref, transaction)
            elif transaction["batch_kind"] == "terminal-reject":
                boundary = normal_phase_for_cursor(transaction)
                if boundary in {"assessment-published", "review-published"}:
                    transaction["phase"] = boundary
                    persist_transaction(root, transaction_ref, transaction)
            continue
        if transaction["phase"] != "recovery-required":
            transaction.update(
                phase="recovery-required",
                residue_refs=list(transaction["published_refs"]),
                residue_digests=list(transaction["published_digests"]),
            )
            persist_transaction(root, transaction_ref, transaction)
        publish_bytes_target(
            root,
            transaction_ref,
            transaction,
            ref,
            intended_bytes_by_ref[ref],
        )
        if transaction["batch_kind"] == "terminal":
            if transaction["next_target_index"] >= 3:
                transaction.update(
                    attestation_ref=transaction["target_refs"][2],
                    attestation_digest=frozen_target_digest(root, transaction["target_refs"][2]),
                )
            boundary = terminal_phase_for_cursor(transaction)
            if boundary is not None:
                transaction["phase"] = boundary
                persist_transaction(root, transaction_ref, transaction)
        elif transaction["batch_kind"] == "terminal-reject":
            boundary = normal_phase_for_cursor(transaction)
            if boundary in {"assessment-published", "review-published"}:
                transaction["phase"] = boundary
                persist_transaction(root, transaction_ref, transaction)
    if transaction["batch_kind"] == "terminal":
        transaction["phase"] = "consistency-published"
        persist_transaction(root, transaction_ref, transaction)
    transaction.update(phase="committed", residue_refs=[], residue_digests=[])
    persist_transaction(root, transaction_ref, transaction)
    return {"status": "committed", "transaction": transaction}


def issue_transaction_targets(plan: str, handoff: dict[str, Any], *, resolved: bool, candidates: list[dict[str, Any]] | None = None) -> list[str]:
    run_dir = PurePosixPath(handoff["manual_qa_attestation_ref"]).parent
    refs: list[str] = []
    if resolved:
        require("RESOLVED_ISSUE_CANDIDATES_MISSING", isinstance(candidates, list) and bool(candidates))
        refs.extend(f"{plan}/builds/manual-qa/proposals/{index}.json" for index, _ in enumerate(candidates))
        refs.extend([f"{plan}/builds/manual-qa/source-catalog.json", f"{plan}/builds/manual-qa/dashboard.json", str(run_dir / "dashboard-presentation.json")])
    refs.extend([str(run_dir / "report.json"), str(run_dir / "interaction.json"), handoff["manual_qa_result_ref"]])
    require("TRANSACTION_CANONICAL_TARGET_DUPLICATE", len(refs) == len(set(refs)))
    return refs


def rejected_transaction_targets(plan: str, handoff: dict[str, Any]) -> list[str]:
    run_dir = PurePosixPath(handoff["manual_qa_attestation_ref"]).parent
    return [
        str(run_dir / "semantic-assessment.json"),
        str(run_dir / "attestation-review.json"),
        str(run_dir / "interaction.json"),
        handoff["manual_qa_result_ref"],
    ]


def current_target_digest(reader: Any, state: dict[str, Any], ref: str) -> str:
    try: return bytes_digest(reader.read_bytes(ref))
    except (ContractError, ValueError) as exc:
        if str(exc).startswith("REF_MISSING:"): return "sha256:" + "0" * 64
        raise


def validate_dashboard(value: Any) -> dict[str, Any]:
    p = closed("DASHBOARD_SHAPE_INVALID", value, DASHBOARD_KEYS)
    require("DASHBOARD_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    validate_ids(p)
    validate_locator(p["plan_directory"] + "/_", "PLAN_DIRECTORY_INVALID")
    for key in ("state_ref", "handoff_ref", "implementation_result_ref", "implementation_dashboard_ref", "implementation_consistency_ref", "demand_ref", "analysis_ref", "source_catalog_ref"):
        validate_locator(p[key], "DASHBOARD_REF_INVALID", fragment=True)
    for key in DASHBOARD_KEYS & {name for name in DASHBOARD_KEYS if name.endswith("_digest")}:
        validate_digest(p[key], "DASHBOARD_DIGEST_INVALID")
    require("DASHBOARD_STEPS_EMPTY", isinstance(p["steps"], list) and bool(p["steps"]))
    last_order = -1
    for index, step in enumerate(p["steps"]):
        validated = validate_step(step, expected_id=f"MQ-{index + 1:02d}")
        require("STEP_SOURCE_ORDER_NOT_INCREASING", validated["source_order"] > last_order); last_order = validated["source_order"]
    require("DASHBOARD_SOURCE_ARRAYS_INVALID", isinstance(p["applicable_source_refs"], list) and bool(p["applicable_source_refs"]) and isinstance(p["not_applicable_source_refs"], list))
    require("DASHBOARD_STEP_SOURCE_MISMATCH", [row["source_ref"] for row in p["steps"]] == p["applicable_source_refs"])
    require("APPLICABLE_STEPS_DIGEST_MISMATCH", p["applicable_steps_digest"] == digest(p["steps"]))
    require("DASHBOARD_DIGEST_MISMATCH", p["dashboard_digest"] == digest(p, omit="dashboard_digest"))
    return p


def validate_attestation(value: Any) -> dict[str, Any]:
    p = closed("ATTESTATION_SHAPE_INVALID", value, ATTESTATION_KEYS)
    require("ATTESTATION_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    validate_ids(p)
    for key in ("applicable_steps_digest", "demand_digest", "analysis_digest"):
        validate_digest(p[key], "ATTESTATION_DIGEST_INVALID")
    require("ATTESTATION_HUMAN_STATEMENT_MISSING", nonempty(p["human_statement"]))
    require("ATTESTATION_DECLARATION_NOT_NORMALIZED", p["declaration"] == DECLARATION)
    validate_locator(p["attestation_review_ref"], "ATTESTATION_REVIEW_REF_INVALID", fragment=True)
    validate_digest(p["attestation_review_digest"], "ATTESTATION_REVIEW_DIGEST_INVALID")
    validate_timestamp(p["recorded_at"], "ATTESTATION_TIME_INVALID")
    return p


def report_identity_material(p: dict[str, Any]) -> dict[str, Any]:
    return {key: p[key] for key in ("schema_version", "run_id", "execution_id", "kind", "summary", "impact", "next_action", "recorded_at")}


def validate_report(value: Any) -> dict[str, Any]:
    p = closed("REPORT_SHAPE_INVALID", value, REPORT_KEYS)
    require("REPORT_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    validate_ids(p)
    require("REPORT_ID_INVALID", isinstance(p["report_id"], str) and REPORT_RE.fullmatch(p["report_id"]) is not None)
    require("REPORT_ID_MISMATCH", p["report_id"] == "manual-qa-report-v1:" + digest(report_identity_material(p)).split(":", 1)[1])
    require("REPORT_STATUS_INVALID", p["status"] in {"open", "resolved"})
    require("REPORT_KIND_INVALID", p["kind"] in {"failure", "blocker"})
    require("REPORT_SUMMARY_INVALID", nonempty(p["summary"]) and len(p["summary"]) <= 280)
    require("REPORT_TEXT_INVALID", nonempty(p["impact"]) and nonempty(p["next_action"]))
    validate_timestamp(p["recorded_at"], "REPORT_TIME_INVALID")
    if p["status"] == "open":
        require("OPEN_REPORT_HAS_RESOLUTION", p["resolution_ref"] is None and p["resolution_digest"] is None and p["resolved_at"] is None and p["revalidation_refs"] == [] and p["revalidation_digests"] == [])
    else:
        validate_locator(p["resolution_ref"], "REPORT_RESOLUTION_REF_INVALID", fragment=True)
        validate_digest(p["resolution_digest"], "REPORT_RESOLUTION_DIGEST_INVALID")
        validate_timestamp(p["resolved_at"], "REPORT_RESOLUTION_TIME_INVALID")
        require("REPORT_REVALIDATION_INVALID", isinstance(p["revalidation_refs"], list) and bool(p["revalidation_refs"]) and len(p["revalidation_refs"]) == len(p["revalidation_digests"]))
        for ref, item_digest in zip(p["revalidation_refs"], p["revalidation_digests"]):
            validate_locator(ref, "REPORT_REVALIDATION_INVALID", fragment=True)
            validate_digest(item_digest, "REPORT_REVALIDATION_INVALID")
    return p


def validate_interaction(value: Any) -> dict[str, Any]:
    p = closed("INTERACTION_SHAPE_INVALID", value, INTERACTION_KEYS)
    require("INTERACTION_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    validate_ids(p)
    require("INTERACTION_STATUS_INVALID", p["status"] in {"in-progress", "awaiting-attestation", "paused", "issue-open", "issue-resolved", "attested", "stopped"})
    validate_pairs(p, "attestation", "INTERACTION_ATTESTATION_PAIR_INVALID")
    validate_pairs(p, "report", "INTERACTION_REPORT_PAIR_INVALID")
    has_attestation, has_report = p["attestation_ref"] is not None, p["report_ref"] is not None
    expected = {
        "in-progress": not has_attestation and not has_report,
        "awaiting-attestation": not has_attestation and not has_report,
        "paused": not has_attestation,
        "issue-open": not has_attestation and has_report,
        "issue-resolved": not has_attestation and has_report,
        "attested": has_attestation,
        "stopped": not has_attestation,
    }
    require("INTERACTION_STATUS_CONTENT_MISMATCH", expected[p["status"]])
    require("INTERACTION_DIGEST_MISMATCH", p["interaction_digest"] == digest(p, omit="interaction_digest"))
    return p


def validate_pairs(p: dict[str, Any], prefix: str, code: str) -> None:
    ref, item_digest = p[f"{prefix}_ref"], p[f"{prefix}_digest"]
    require(code, (ref is None) == (item_digest is None))
    if ref is not None:
        validate_locator(ref, code, fragment=True)
        validate_digest(item_digest, code)


def validate_result(value: Any) -> dict[str, Any]:
    p = closed("RESULT_SHAPE_INVALID", value, RESULT_KEYS)
    require("RESULT_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    validate_ids(p)
    require("RESULT_STATUS_INVALID", p["status"] in {"in-progress", "pending-input", "blocked", "stopped", "completed"})
    for key in ("state_ref", "handoff_ref", "dashboard_ref", "interaction_ref"):
        validate_locator(p[key], "RESULT_REF_INVALID", fragment=True)
    for prefix in ("attestation", "report"):
        validate_pairs(p, prefix, "RESULT_FRAGMENT_PAIR_INVALID")
    for key in ("state_digest", "handoff_digest", "dashboard_digest", "interaction_digest", "applicable_steps_digest", "demand_revalidation_digest", "result_digest"):
        validate_digest(p[key], "RESULT_DIGEST_INVALID")
    require("RESULT_AUTOMATIC_GATES_INVALID", isinstance(p["automatic_gate_refs"], list) and bool(p["automatic_gate_refs"]) and len(p["automatic_gate_refs"]) == len(p["automatic_gate_digests"]))
    require("RESULT_NEXT_ACTION_INVALID", nonempty(p["next_action"]))
    validate_terminal_projection(p, completed=p["status"] == "completed")
    if p["status"] == "completed":
        require("RESULT_HANDOFF_NOT_RECONCILED", p["reconciled_handoff_ref"] == p["handoff_ref"] and p["attestation_ref"] is not None)
    else:
        require("RESULT_PREMATURE_RECONCILIATION", p["reconciled_handoff_ref"] is None)
    require("RESULT_DIGEST_MISMATCH", p["result_digest"] == digest(p, omit="result_digest"))
    return p


def validate_consistency(value: Any) -> dict[str, Any]:
    p = closed("CONSISTENCY_SHAPE_INVALID", value, CONSISTENCY_KEYS)
    require("CONSISTENCY_SCHEMA_CURRENT_ONLY", p["schema_version"] == 1)
    validate_ids(p)
    for key in ("state_ref", "handoff_ref", "dashboard_ref", "interaction_ref", "result_ref", "attestation_ref"):
        validate_locator(p[key], "CONSISTENCY_REF_INVALID", fragment=True)
    validate_pairs(p, "report", "CONSISTENCY_REPORT_PAIR_INVALID")
    for key in ("state_digest", "handoff_digest", "dashboard_digest", "interaction_digest", "attestation_digest", "result_digest", "applicable_steps_digest", "demand_revalidation_digest", "consistency_digest"):
        validate_digest(p[key], "CONSISTENCY_DIGEST_INVALID")
    require("CONSISTENCY_AUTOMATIC_GATES_INVALID", isinstance(p["automatic_gate_refs"], list) and bool(p["automatic_gate_refs"]) and len(p["automatic_gate_refs"]) == len(p["automatic_gate_digests"]))
    require("CONSISTENCY_RECONCILIATION_INVALID", p["reconciled_handoff_ref"] == p["handoff_ref"])
    validate_terminal_projection(p, completed=True)
    require("CONSISTENCY_DIGEST_MISMATCH", p["consistency_digest"] == digest(p, omit="consistency_digest"))
    return p


def validate_terminal_projection(p: dict[str, Any], *, completed: bool) -> None:
    for key in ("source_catalog_ref", "transaction_ref"): validate_locator(p[key], "TERMINAL_PROJECTION_REF_INVALID", fragment=True)
    validate_digest(p["source_catalog_digest"], "TERMINAL_PROJECTION_DIGEST_INVALID")
    require("TERMINAL_PROJECTION_TRANSACTION_ID_INVALID", isinstance(p["transaction_id"], str) and TRANSACTION_ID_RE.fullmatch(p["transaction_id"]) is not None)
    list_keys = ("covered_task_refs", "covered_acceptance_criterion_refs", "covered_gate_refs", "covered_changed_surface_refs", "promoted_task_refs", "promoted_acceptance_criterion_refs", "promoted_gate_refs", "canonical_asset_refs", "canonical_asset_digests", "validator_refs", "validator_digests", "audit_refs", "audit_digests", "blockers")
    for key in list_keys:
        require("TERMINAL_PROJECTION_LIST_INVALID", isinstance(p[key], list))
        if key.endswith("_refs"):
            require("TERMINAL_PROJECTION_REF_DUPLICATE", len(p[key]) == len(set(p[key])))
    for refs_key, digests_key in (("canonical_asset_refs", "canonical_asset_digests"), ("validator_refs", "validator_digests"), ("audit_refs", "audit_digests")):
        require("TERMINAL_PROJECTION_PAIR_INVALID", len(p[refs_key]) == len(p[digests_key]))
        for item in p[digests_key]: validate_digest(item, "TERMINAL_PROJECTION_DIGEST_INVALID")
    require("TERMINAL_PROJECTION_STATUS_INVALID", p["final_plan_status"] in {"awaiting-manual-qa", "completed"})
    require("TERMINAL_PROJECTION_RESUME_INVALID", nonempty(p["resume"]))
    require("TERMINAL_PROJECTION_COVERAGE_EMPTY", bool(p["covered_task_refs"]) and bool(p["covered_acceptance_criterion_refs"]) and bool(p["covered_gate_refs"]) and bool(p["covered_changed_surface_refs"]))
    for key in ("covered_task_refs", "covered_acceptance_criterion_refs", "covered_gate_refs", "promoted_gate_refs", "canonical_asset_refs", "validator_refs", "audit_refs"):
        for ref in p[key]: validate_locator(ref, "TERMINAL_PROJECTION_REF_INVALID", fragment=True)
    for ref in p["covered_changed_surface_refs"]:
        require("TERMINAL_PROJECTION_CHANGED_SURFACE_INVALID", nonempty(ref) and not PurePosixPath(ref).is_absolute() and ".." not in PurePosixPath(ref).parts)
    require("TERMINAL_PROJECTION_CANONICAL_ASSETS_INVALID", len(p["canonical_asset_refs"]) == 4 and p["canonical_asset_refs"][0].endswith("/tasks.md"))
    require("TERMINAL_PROJECTION_VALIDATORS_EMPTY", bool(p["validator_refs"]))
    require("TERMINAL_PROJECTION_AUDITS_EMPTY", bool(p["audit_refs"]))
    require("TERMINAL_PROJECTION_FALSE_TECHNICAL_PROMOTION", p["promoted_task_refs"] == [] and p["promoted_acceptance_criterion_refs"] == [])
    if completed:
        require("TERMINAL_PROJECTION_NOT_COMPLETED", p["final_plan_status"] == "completed" and p["blockers"] == [])
        require("TERMINAL_PROJECTION_HUMAN_PROMOTION_EMPTY", bool(p["promoted_gate_refs"]))
        require("TERMINAL_PROJECTION_PROMOTION_INCOMPLETE", p["promoted_gate_refs"] == p["covered_gate_refs"])
    else:
        require("TERMINAL_PROJECTION_PREMATURE_PROMOTION", p["final_plan_status"] == "awaiting-manual-qa" and p["promoted_task_refs"] == [] and p["promoted_acceptance_criterion_refs"] == [] and p["promoted_gate_refs"] == [])


def load_upstream() -> Any:
    path = ROOT / "scripts/validate-implement-feature-contracts.py"
    spec = importlib.util.spec_from_file_location("loki_validate_implement_feature", path)
    require("UPSTREAM_VALIDATOR_LOAD_FAILED", spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def enumerate_candidates(reader: Any, handoff: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    task_contracts = {ref: reader.read_markdown_json(ref)["task_contract"] for ref in handoff["task_refs"]}
    ac_rows: dict[str, tuple[str, dict[str, Any]]] = {}
    for task_ref, task in task_contracts.items():
        for ac in task["task_validation"]["acceptance_criteria"]: ac_rows[f'{task_ref}#{ac["id"]}'] = (task_ref, ac)
    require("CANDIDATE_AC_COVERAGE_INVALID", list(ac_rows) == handoff["acceptance_criterion_refs"])
    for ref in handoff["acceptance_criterion_refs"]:
        task_ref, ac = ac_rows[ref]
        ac_digest = digest(ac)
        candidates.append({"source_kind": "acceptance-criterion", "source_ref": ref, "source_digest": ac_digest, "task_refs": [task_ref], "acceptance_criterion_refs": [ref], "gate_refs": [], "changed_surface_refs": [], "observable_fact_refs": [ref], "observable_fact_digests": [ac_digest], "observable_fact_statements": [ac["statement"]], "statement": ac["statement"]})
    observable_by_task: dict[str, list[tuple[str, str, str]]] = {
        task_ref: [
            (ac_ref, ac["statement"], digest(ac))
            for ac_ref, (owner_ref, ac) in ac_rows.items()
            if owner_ref == task_ref
        ]
        for task_ref in task_contracts
    }
    for ref in handoff["gate_refs"]:
        gate = reader.read_json(ref)
        if gate["kind"] != "human-validation": continue
        immutable_gate_source = {key: gate[key] for key in ("schema_version", "gate_id", "task_ref", "kind", "statement")}
        observable_by_task.setdefault(gate["task_ref"], []).append(
            (ref, gate["statement"], digest(immutable_gate_source))
        )
        gate_digest = digest(immutable_gate_source)
        candidates.append({"source_kind": "human-gate", "source_ref": ref, "source_digest": gate_digest, "task_refs": [gate["task_ref"]], "acceptance_criterion_refs": [], "gate_refs": [ref], "changed_surface_refs": [], "observable_fact_refs": [ref], "observable_fact_digests": [gate_digest], "observable_fact_statements": [gate["statement"]], "statement": gate["statement"]})
    target_owner = {target: task_ref for task_ref, task in task_contracts.items() for target in task["target_files"]}
    for ref in handoff["changed_target_refs"]:
        require("CANDIDATE_CHANGED_TARGET_UNOWNED", ref in target_owner)
        owner_ref = target_owner[ref]
        observable_facts = observable_by_task.get(owner_ref, [])
        surface_digest = bytes_digest(reader.read_bytes(ref))
        statement = (
            "Validate the changed surface against persisted observable facts: "
            + "; ".join(
                f"{fact_ref} ({fact_digest}) states {fact_statement}"
                for fact_ref, fact_statement, fact_digest in observable_facts
            )
            if observable_facts
            else "No persisted acceptance criterion or human gate provides an observable fact for this changed surface."
        )
        candidates.append({"source_kind": "changed-surface", "source_ref": ref, "source_digest": surface_digest, "task_refs": [owner_ref], "acceptance_criterion_refs": [fact_ref for fact_ref, _, _ in observable_facts if "#" in fact_ref], "gate_refs": [fact_ref for fact_ref, _, _ in observable_facts if "#" not in fact_ref and fact_ref.endswith(".json")], "changed_surface_refs": [ref], "observable_fact_refs": [fact_ref for fact_ref, _, _ in observable_facts], "observable_fact_digests": [fact_digest for _, _, fact_digest in observable_facts], "observable_fact_statements": [fact_statement for _, fact_statement, _ in observable_facts], "statement": statement, "default_applicable": bool(observable_facts)})
    require("CANDIDATE_SET_EMPTY", bool(candidates))
    return candidates


def steps_from_catalog(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for source in catalog["sources"]:
        if source["applicability"] != "applicable": continue
        steps.append({"schema_version": 1, "id": f"MQ-{len(steps) + 1:02d}", "source_kind": source["source_kind"], "source_ref": source["source_ref"], "source_order": source["source_order"], "title": source["expected_result"], "environment": source["environment"], "prerequisites": source["prerequisites"], "initial_state": source["initial_state"], "actions": source["actions"], "expected_result": source["expected_result"], "success_signal": source["success_signal"], "failure_signal": source["failure_signal"], "cleanup": source["cleanup"], "automation_limit": source["automation_limit"]})
    return steps


def read_context(project_root: Path, plan_directory: str) -> tuple[Any, Any, dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    upstream = load_upstream()
    tasks_ref = f"{plan_directory}/tasks.md"
    invocation_ref = f"{plan_directory}/execution-input.json"
    upstream.validate_real_run(project_root, tasks_ref, invocation_ref)
    reader = upstream.RealRunReader(project_root)
    tasks = reader.read_markdown_json(tasks_ref)
    state = tasks["loki_run_state"]
    invocation = reader.read_json(invocation_ref)
    handoff = validate_handoff(state["manual_qa_handoff"])
    require("HANDOFF_STATE_IDENTITY_MISMATCH", (handoff["run_id"], handoff["execution_id"], handoff["plan_directory"]) == (state["run_id"], state["execution_id"], plan_directory))
    candidates = enumerate_candidates(reader, handoff)
    return upstream, reader, state, invocation, handoff, candidates


def validate_tree(project_root: Path, plan_directory: str) -> dict[str, Any]:
    upstream, reader, state, invocation, handoff, candidates = read_context(project_root, plan_directory)
    identity = invocation["command_identity"]
    state_ref = f"{plan_directory}/tasks.md#loki_run_state"
    handoff_ref = f"{plan_directory}/tasks.md#loki_run_state.manual_qa_handoff"
    catalog_ref = f"{plan_directory}/builds/manual-qa/source-catalog.json"
    dashboard_ref = f"{plan_directory}/builds/manual-qa/dashboard.json"
    interaction_ref = str(PurePosixPath(handoff["manual_qa_attestation_ref"]).parent / "interaction.json")
    result_ref = handoff["manual_qa_result_ref"]
    consistency_ref = f"{plan_directory}/builds/manual-qa/consistency.json"
    transaction_ref = f"{plan_directory}/builds/manual-qa/transaction.json"

    catalog = validate_catalog(reader.read_json(catalog_ref))
    require("CATALOG_TREE_IDENTITY_MISMATCH", (catalog["run_id"], catalog["execution_id"], catalog["plan_directory"], catalog["state_digest"], catalog["handoff_digest"]) == (state["run_id"], state["execution_id"], plan_directory, state["state_digest"], digest(handoff)))
    require("CATALOG_TREE_CANDIDATE_MISMATCH", catalog["candidate_refs"] == [row["source_ref"] for row in candidates] and catalog["candidate_digests"] == [row["source_digest"] for row in candidates])
    for source, candidate in zip(catalog["sources"], candidates):
        for key in ("source_kind", "source_ref", "source_digest", "task_refs", "acceptance_criterion_refs", "gate_refs", "changed_surface_refs", "observable_fact_refs", "observable_fact_digests", "observable_fact_statements"): require(f"CATALOG_TREE_SOURCE_MISMATCH:{key}", source[key] == candidate[key])
        require("CATALOG_PROPOSAL_BYTES_MISMATCH", source["runtime_qa_proposal_digest"] == bytes_digest(reader.read_bytes(source["runtime_qa_proposal_ref"])))
        proposal = validate_proposal(reader.read_json(source["runtime_qa_proposal_ref"]))
        proposal_source_pairs = {"candidate_ref": "source_ref", "candidate_digest": "source_digest", "source_kind": "source_kind", "applicability": "applicability", "not_applicable_reason": "not_applicable_reason", "environment": "environment", "prerequisites": "prerequisites", "initial_state": "initial_state", "actions": "actions", "expected_result": "expected_result", "success_signal": "success_signal", "failure_signal": "failure_signal", "cleanup": "cleanup", "automation_limit": "automation_limit"}
        for proposal_key, source_key in proposal_source_pairs.items(): require(f"CATALOG_PROPOSAL_CORRELATION_MISMATCH:{proposal_key}", proposal[proposal_key] == source[source_key])
        require("CATALOG_PROPOSAL_EVIDENCE_MISMATCH", proposal["evidence_refs"] == source["task_refs"])
        guide_material = " ".join(
            [proposal[key] for key in ("environment", "prerequisites", "initial_state", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit")]
            + proposal["actions"]
        )
        require("CATALOG_GUIDE_SOURCE_FACT_MISSING", all(ref in guide_material and item_digest in guide_material and statement in guide_material for ref, item_digest, statement in zip(candidate["observable_fact_refs"], candidate["observable_fact_digests"], candidate["observable_fact_statements"])))
    steps = steps_from_catalog(catalog)

    dashboard = validate_dashboard(reader.read_json(dashboard_ref))
    expected_dashboard = {
        "schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "plan_directory": plan_directory,
        "state_ref": state_ref, "state_digest": state["state_digest"], "handoff_ref": handoff_ref, "handoff_digest": digest(handoff),
        "implementation_result_ref": state["result_ref"], "implementation_result_digest": bytes_digest(reader.read_bytes(state["result_ref"])),
        "implementation_dashboard_ref": state["dashboard_ref"], "implementation_dashboard_digest": bytes_digest(reader.read_bytes(state["dashboard_ref"])),
        "implementation_consistency_ref": state["consistency_packet_ref"], "implementation_consistency_digest": bytes_digest(reader.read_bytes(state["consistency_packet_ref"])),
        "demand_ref": invocation["demand_ref"], "demand_digest": bytes_digest(reader.read_bytes(invocation["demand_ref"])),
        "analysis_ref": invocation["analysis_ref"], "analysis_digest": bytes_digest(reader.read_bytes(invocation["analysis_ref"])),
        "source_catalog_ref": catalog_ref, "source_catalog_digest": bytes_digest(reader.read_bytes(catalog_ref)), "applicable_source_refs": catalog["applicable_source_refs"], "not_applicable_source_refs": catalog["not_applicable_source_refs"], "steps": steps, "applicable_steps_digest": digest(steps), "dashboard_digest": "",
    }
    expected_dashboard["dashboard_digest"] = digest(expected_dashboard, omit="dashboard_digest")
    require("DASHBOARD_TREE_PARITY_MISMATCH", dashboard == expected_dashboard)

    interaction = validate_interaction(reader.read_json(interaction_ref))
    require("INTERACTION_TREE_IDENTITY_MISMATCH", (interaction["run_id"], interaction["execution_id"]) == (state["run_id"], state["execution_id"]))
    attestation = validate_attestation(reader.read_json(interaction["attestation_ref"])) if interaction["attestation_ref"] is not None else None
    report = validate_report(reader.read_json(interaction["report_ref"])) if interaction["report_ref"] is not None else None
    if attestation is not None:
        require("ATTESTATION_TREE_PARITY_MISMATCH", interaction["attestation_ref"] == handoff["manual_qa_attestation_ref"] and interaction["attestation_digest"] == bytes_digest(reader.read_bytes(interaction["attestation_ref"])) and attestation["applicable_steps_digest"] == digest(steps) and attestation["demand_digest"] == identity["demand_digest"] and attestation["analysis_digest"] == identity["analysis_digest"])
        assessment_ref = str(PurePosixPath(interaction["attestation_ref"]).parent / "semantic-assessment.json")
        assessment = validate_semantic_assessment(reader.read_json(assessment_ref))
        review = validate_attestation_review(reader.read_json(attestation["attestation_review_ref"]))
        review_evidence_bytes = reader.read_bytes(review["independent_agent_run_evidence_ref"])
        validate_agent_session_evidence_bytes(review_evidence_bytes, run_id=state["run_id"], decision=review["decision"])
        presentation_ref = str(PurePosixPath(interaction["attestation_ref"]).parent / "dashboard-presentation.json")
        presentation = validate_dashboard(reader.read_json(presentation_ref))
        require("ASSESSMENT_TREE_CORRELATION_MISMATCH", assessment["human_statement"] == attestation["human_statement"] and assessment["statement_digest"] == bytes_digest(attestation["human_statement"].encode("utf-8")) and assessment["dashboard_ref"] == presentation_ref and assessment["dashboard_digest"] == bytes_digest(reader.read_bytes(presentation_ref)) and assessment["applicable_steps_digest"] == presentation["applicable_steps_digest"] and assessment["decision"] == "approve")
        require("ATTESTATION_REVIEW_TREE_CORRELATION_MISMATCH", attestation["attestation_review_digest"] == bytes_digest(reader.read_bytes(attestation["attestation_review_ref"])) and review["assessment_ref"] == assessment_ref and review["assessment_digest"] == bytes_digest(reader.read_bytes(assessment_ref)) and review["statement_digest"] == assessment["statement_digest"] and review["dashboard_ref"] == assessment["dashboard_ref"] and review["dashboard_digest"] == assessment["dashboard_digest"] and review["applicable_steps_digest"] == assessment["applicable_steps_digest"] and review["evaluator_policy_id"] == assessment["evaluator_policy_id"] and review["evaluator_policy_digest"] == assessment["evaluator_policy_digest"] and review["signals"] == assessment["signals"] and review["decision"] == assessment["decision"] == "approve" and review["independent_agent_run_evidence_digest"] == bytes_digest(review_evidence_bytes))
    if report is not None:
        require("REPORT_TREE_BYTES_MISMATCH", interaction["report_digest"] == bytes_digest(reader.read_bytes(interaction["report_ref"])))
    if report is not None and report["status"] == "resolved":
        require("REPORT_RESOLUTION_BYTES_MISMATCH", report["resolution_digest"] == bytes_digest(reader.read_bytes(report["resolution_ref"])))
        require("REPORT_REVALIDATION_BYTES_MISMATCH", report["revalidation_digests"] == [bytes_digest(reader.read_bytes(ref)) for ref in report["revalidation_refs"]])
        technical_ref = f"{plan_directory}/builds/manual-qa/technical-revalidation.json"
        require("REPORT_REVALIDATION_PROJECTION_MISMATCH", report["revalidation_refs"] == [technical_ref, *handoff["automatic_evidence_refs"]])
        technical = closed("TECHNICAL_REVALIDATION_SHAPE_INVALID", reader.read_json(technical_ref), {"schema_version", "status", "run_id", "execution_id", "resolution_ref", "resolution_digest", "projection_refs", "projection_digests"})
        require("TECHNICAL_REVALIDATION_IDENTITY_INVALID", technical["schema_version"] == 1 and technical["status"] == "fresh" and (technical["run_id"], technical["execution_id"]) == (state["run_id"], state["execution_id"]))
        require("TECHNICAL_REVALIDATION_RESOLUTION_MISMATCH", technical["resolution_ref"] == report["resolution_ref"] and technical["resolution_digest"] == report["resolution_digest"])
        expected_projection_refs = [state["result_ref"], state["dashboard_ref"], state["consistency_packet_ref"], *handoff["automatic_evidence_refs"]]
        require("TECHNICAL_REVALIDATION_PROJECTION_MISMATCH", technical["projection_refs"] == expected_projection_refs and technical["projection_digests"] == [bytes_digest(reader.read_bytes(ref)) for ref in expected_projection_refs])
        presentation_ref = str(PurePosixPath(handoff["manual_qa_attestation_ref"]).parent / "dashboard-presentation.json")
        require("RESOLVED_ISSUE_STALE_PRESENTATION", bytes_digest(reader.read_bytes(presentation_ref)) == bytes_digest(reader.read_bytes(dashboard_ref)))

    result = validate_result(reader.read_json(result_ref))
    transaction = validate_transaction(reader.read_json(transaction_ref))
    if transaction["batch_kind"] == "terminal-reject":
        expected_transaction_targets = rejected_transaction_targets(plan_directory, handoff)
        rejected_assessment_ref = expected_transaction_targets[0]
        rejected_assessment = validate_semantic_assessment(reader.read_json(rejected_assessment_ref))
        rejected_review = validate_attestation_review(reader.read_json(expected_transaction_targets[1]))
        rejected_evidence_bytes = reader.read_bytes(rejected_review["independent_agent_run_evidence_ref"])
        validate_agent_session_evidence_bytes(rejected_evidence_bytes, run_id=state["run_id"], decision="reject")
        require("REJECTED_ASSESSMENT_DECISION_INVALID", rejected_assessment["decision"] == rejected_review["decision"] == "reject" and rejected_review["assessment_ref"] == rejected_assessment_ref and rejected_review["assessment_digest"] == bytes_digest(reader.read_bytes(rejected_assessment_ref)) and rejected_review["independent_agent_run_evidence_digest"] == bytes_digest(rejected_evidence_bytes) and attestation is None and result["status"] == "pending-input")
        expected_batch_kind = "terminal-reject"
    else:
        expected_transaction_targets = issue_transaction_targets(plan_directory, handoff, resolved=report["status"] == "resolved", candidates=candidates if report["status"] == "resolved" else None) if report is not None else canonical_transaction_targets(reader, plan_directory, state, handoff, candidates, terminal=result["status"] == "completed")
        expected_batch_kind = "issue" if report is not None else ("terminal" if result["status"] == "completed" else "initial")
    require("TRANSACTION_BATCH_KIND_MISMATCH", transaction["batch_kind"] == expected_batch_kind)
    require("TRANSACTION_TARGET_SET_MISMATCH", transaction["target_refs"] == expected_transaction_targets)
    require("TRANSACTION_BEFORE_TARGET_SET_MISMATCH", len(transaction["before_digests"]) == len(expected_transaction_targets))
    require("TRANSACTION_INTENDED_TARGET_SET_MISMATCH", len(transaction["intended_after_digests"]) == len(expected_transaction_targets))
    current_target_digests = [current_target_digest(reader, state, ref) for ref in transaction["target_refs"]]
    if transaction["phase"] == "committed": require("TRANSACTION_TARGET_BYTES_MISMATCH", transaction["intended_after_digests"] == current_target_digests and transaction["published_digests"] == current_target_digests)
    for ref, item_digest in zip(transaction["published_refs"], transaction["published_digests"]):
        current = current_target_digest(reader, state, ref); require("TRANSACTION_PUBLISHED_BYTES_MISMATCH", item_digest == current)
    for ref, item_digest in zip(transaction["residue_refs"], transaction["residue_digests"]):
        current = current_target_digest(reader, state, ref); require("TRANSACTION_RESIDUE_BYTES_MISMATCH", item_digest == current)
    automatic_digests = [bytes_digest(reader.read_bytes(ref)) for ref in handoff["automatic_evidence_refs"]]
    attestation_ref = handoff["manual_qa_attestation_ref"] if attestation is not None else None
    attestation_digest = bytes_digest(reader.read_bytes(attestation_ref)) if attestation_ref is not None else None
    report_ref = interaction["report_ref"]
    report_digest = bytes_digest(reader.read_bytes(report_ref)) if report_ref is not None else None
    expected_common = {
        "schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"],
        "state_ref": state_ref, "state_digest": state["state_digest"], "handoff_ref": handoff_ref, "handoff_digest": digest(handoff),
        "dashboard_ref": dashboard_ref, "dashboard_digest": bytes_digest(reader.read_bytes(dashboard_ref)),
        "interaction_ref": interaction_ref, "interaction_digest": bytes_digest(reader.read_bytes(interaction_ref)),
        "attestation_ref": attestation_ref, "attestation_digest": attestation_digest, "report_ref": report_ref, "report_digest": report_digest,
        "applicable_steps_digest": digest(steps), "demand_revalidation_digest": bytes_digest(reader.read_bytes(invocation["demand_ref"])),
        "automatic_gate_refs": handoff["automatic_evidence_refs"], "automatic_gate_digests": automatic_digests,
    }
    for key, value in expected_common.items():
        require(f"RESULT_TREE_PARITY_MISMATCH:{key}", result[key] == value)
    report_status = report["status"] if report else None
    allowed_pair = (interaction["status"], report_status, result["status"]) in {("in-progress", None, "in-progress"), ("awaiting-attestation", None, "pending-input"), ("paused", None, "in-progress"), ("paused", "resolved", "in-progress"), ("issue-open", "open", "blocked"), ("issue-resolved", "resolved", "in-progress"), ("attested", None, "in-progress"), ("attested", "resolved", "in-progress"), ("attested", None, "completed"), ("attested", "resolved", "completed"), ("stopped", None, "stopped"), ("stopped", "resolved", "stopped")}
    require("TRANSITION_PAIR_INVALID", allowed_pair)
    require("RESULT_CATALOG_TRANSACTION_MISMATCH", result["source_catalog_ref"] == catalog_ref and result["source_catalog_digest"] == bytes_digest(reader.read_bytes(catalog_ref)) and result["transaction_ref"] == transaction_ref and result["transaction_id"] == transaction["transaction_id"])
    human_gate_refs = [ref for ref in handoff["gate_refs"] if reader.read_json(ref)["kind"] == "human-validation"]
    require("RESULT_COVERAGE_MISMATCH", result["covered_task_refs"] == handoff["task_refs"] and result["covered_acceptance_criterion_refs"] == handoff["acceptance_criterion_refs"] and result["covered_gate_refs"] == human_gate_refs and result["covered_changed_surface_refs"] == handoff["changed_target_refs"])
    if result["status"] == "completed":
        require("RESULT_COMPLETED_WITHOUT_ATTESTATION", interaction["status"] == "attested" and attestation is not None and (report is None or report["status"] == "resolved"))
        require("RESULT_RECONCILIATION_MISMATCH", result["reconciled_handoff_ref"] == handoff_ref)
        require("TRANSACTION_NOT_COMMITTED", transaction["phase"] == "committed" and transaction["residue_refs"] == [])
        require("CANONICAL_PLAN_NOT_COMPLETED", state["status"] == "completed")
        require("CANONICAL_ASSET_BYTES_MISMATCH", result["canonical_asset_digests"] == [state["state_digest"] if ref == state_ref else bytes_digest(reader.read_bytes(ref)) for ref in result["canonical_asset_refs"]])
        consistency = validate_consistency(reader.read_json(consistency_ref))
        expected_consistency = {key: result[key] for key in CONSISTENCY_KEYS if key in result and key not in {"result_digest"}}
        expected_consistency.update({"result_ref": result_ref, "result_digest": bytes_digest(reader.read_bytes(result_ref)), "consistency_digest": ""})
        expected_consistency["consistency_digest"] = digest(expected_consistency, omit="consistency_digest")
        require("CONSISTENCY_TREE_PARITY_MISMATCH", consistency == expected_consistency)
    return {"schema_version": 1, "status": "passed", "run_id": state["run_id"], "execution_id": state["execution_id"], "steps": len(steps), "files_read": len(reader._bytes), "tree_digest": digest({ref: bytes_digest(data) for ref, data in sorted(reader._bytes.items())})}


def write_json(root: Path, ref: str, value: Any) -> None:
    path = root / ref
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    MANUAL_WRITE_TRACE.append(ref)


def frozen_target_digest(root: Path, ref: str) -> str:
    path = root / ref.partition("#")[0]
    return bytes_digest(path.read_bytes()) if path.is_file() else "sha256:" + "0" * 64


def publish_json_target(root: Path, transaction_ref: str, transaction: dict[str, Any], ref: str, value: Any) -> None:
    index = transaction["next_target_index"]
    require("TRANSACTION_PUBLICATION_ORDER_INVALID", index < len(transaction["target_refs"]) and transaction["target_refs"][index] == ref)
    require("TRANSACTION_BEFORE_WRITE_DRIFT", frozen_target_digest(root, ref) == transaction["before_digests"][index])
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    intended = bytes_digest(encoded)
    transaction["intended_after_digests"][index] = intended
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)
    write_json(root, ref, value)
    require("TRANSACTION_PUBLICATION_BYTES_MISMATCH", bytes_digest((root / ref).read_bytes()) == intended)
    transaction["published_refs"].append(ref); transaction["published_digests"].append(intended); transaction["next_target_index"] += 1
    transaction["residue_refs"] = list(transaction["published_refs"])
    transaction["residue_digests"] = list(transaction["published_digests"])
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)


def publish_bytes_target(root: Path, transaction_ref: str, transaction: dict[str, Any], ref: str, encoded: bytes, *, intended_digest: str | None = None) -> None:
    index = transaction["next_target_index"]
    require("TRANSACTION_PUBLICATION_ORDER_INVALID", index < len(transaction["target_refs"]) and transaction["target_refs"][index] == ref)
    require("TRANSACTION_BEFORE_WRITE_DRIFT", frozen_target_digest(root, ref) == transaction["before_digests"][index])
    intended = intended_digest or bytes_digest(encoded); transaction["intended_after_digests"][index] = intended
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)
    path = root / ref.partition("#")[0]; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(encoded); MANUAL_WRITE_TRACE.append(ref)
    if intended_digest is None: require("TRANSACTION_PUBLICATION_BYTES_MISMATCH", bytes_digest(path.read_bytes()) == intended)
    transaction["published_refs"].append(ref); transaction["published_digests"].append(intended); transaction["next_target_index"] += 1
    transaction["residue_refs"] = list(transaction["published_refs"])
    transaction["residue_digests"] = list(transaction["published_digests"])
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)


def proposal_source(plan: str, run_id: str, execution_id: str, candidate: dict[str, Any], order: int, applicable: bool = True) -> tuple[str, dict[str, Any], dict[str, Any]]:
    ref = f"{plan}/builds/manual-qa/proposals/{order}.json"
    subject = candidate["statement"]
    kind_instruction = {
        "acceptance-criterion": "trace the persisted criterion through the complete user-visible scenario",
        "human-gate": "perform the named human-validation gate with its declared environment",
        "changed-surface": "inspect the changed surface directly and exercise its affected behavior",
    }[candidate["source_kind"]]
    fact_actions = [
        f"Bind observable fact {fact_ref} at {fact_digest} exactly: {fact_statement}"
        for fact_ref, fact_digest, fact_statement in zip(candidate["observable_fact_refs"], candidate["observable_fact_digests"], candidate["observable_fact_statements"])
    ]
    fact_ref, fact_digest, fact_statement = next(zip(candidate["observable_fact_refs"], candidate["observable_fact_digests"], candidate["observable_fact_statements"]), (candidate["source_ref"], candidate["source_digest"], candidate["statement"]))
    binding = f"Observable fact {fact_ref} at {fact_digest} states: {fact_statement}"
    environment_detail = {
        "acceptance-criterion": "Open the real-run fixture shell with the feature output panel and its byte-verification control visible",
        "human-gate": "Open the real-run fixture shell at the changed behavior view with the approval indicator visible",
        "changed-surface": f"Open the fixture consumer that loads the exact changed file {candidate['source_ref']} and exposes its affected output panel",
    }[candidate["source_kind"]]
    proposal = {"schema_version": 1, "run_id": run_id, "execution_id": execution_id, "caller": "loki-manual-qa", "agent": "runtime-qa", "allowed_writes": [], "candidate_ref": candidate["source_ref"], "candidate_digest": candidate["source_digest"], "source_kind": candidate["source_kind"], "applicability": "applicable" if applicable else "not-applicable", "not_applicable_reason": None if applicable else f"Current evidence proves {candidate['source_ref']} has no human-observable behavior.", "environment": f"{environment_detail}. {binding}", "prerequisites": f"Load candidate {candidate['source_ref']} at exact source digest {candidate['source_digest']}; confirm the fixture starts before interaction. {binding}", "initial_state": f"The feature output is idle, the approval indicator is unset, and no byte-verification action has run. {binding}", "actions": [f"From the fixture start view for {candidate['source_ref']}, {kind_instruction}. {binding}", *fact_actions, f"Compare the displayed output and indicator with the persisted statement for {candidate['source_ref']}. {binding}"], "expected_result": f"The output panel visibly demonstrates the persisted expectation without fallback or stale state. {binding}", "success_signal": f"The expected output and approval indicator are simultaneously visible after the action. {binding}", "failure_signal": f"The output is absent, stale, contradicted, incomplete, or the approval indicator remains unset. {binding}", "cleanup": f"Reset the fixture output and approval indicator to their idle state, then reload the exact candidate. {binding}", "automation_limit": f"Automatic byte checks cannot establish the displayed output and approval indicator perceived by the human. {binding}", "evidence_refs": candidate["task_refs"], "completion_record": {"status": "completed", "validators": ["proposal-schema-and-source-correlation"], "gates": [], "risks": [], "next_destination": "loki-manual-qa orchestrator"}}
    proposal_bytes = (json.dumps(proposal, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    guide_fact_bindings = ({field: {"fact_ref": fact_ref, "fact_digest": fact_digest} for field in GUIDE_FIELDS} if candidate["observable_fact_refs"] else {})
    source = {"schema_version": 1, "source_kind": candidate["source_kind"], "source_ref": candidate["source_ref"], "source_digest": candidate["source_digest"], "source_order": order, "applicability": proposal["applicability"], "not_applicable_reason": proposal["not_applicable_reason"], "task_refs": candidate["task_refs"], "acceptance_criterion_refs": candidate["acceptance_criterion_refs"], "gate_refs": candidate["gate_refs"], "changed_surface_refs": candidate["changed_surface_refs"], "observable_fact_refs": candidate["observable_fact_refs"], "observable_fact_digests": candidate["observable_fact_digests"], "observable_fact_statements": candidate["observable_fact_statements"], "guide_fact_bindings": guide_fact_bindings, "environment": proposal["environment"], "prerequisites": proposal["prerequisites"], "initial_state": proposal["initial_state"], "actions": proposal["actions"], "expected_result": proposal["expected_result"], "success_signal": proposal["success_signal"], "failure_signal": proposal["failure_signal"], "cleanup": proposal["cleanup"], "automation_limit": proposal["automation_limit"], "runtime_qa_proposal_ref": ref, "runtime_qa_proposal_digest": bytes_digest(proposal_bytes)}
    return ref, proposal, source


def make_catalog(plan: str, state: dict[str, Any], handoff: dict[str, Any], candidates: list[dict[str, Any]], not_applicable_orders: set[int] | None = None) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    excluded = not_applicable_orders or set()
    prepared = [proposal_source(plan, state["run_id"], state["execution_id"], candidate, index, index not in excluded and candidate.get("default_applicable", True)) for index, candidate in enumerate(candidates)]
    sources = [item[2] for item in prepared]
    catalog = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "plan_directory": plan, "state_ref": f"{plan}/tasks.md#loki_run_state", "state_digest": state["state_digest"], "handoff_ref": f"{plan}/tasks.md#loki_run_state.manual_qa_handoff", "handoff_digest": digest(handoff), "candidate_refs": [row["source_ref"] for row in sources], "candidate_digests": [row["source_digest"] for row in sources], "sources": sources, "applicable_source_refs": [row["source_ref"] for row in sources if row["applicability"] == "applicable"], "not_applicable_source_refs": [row["source_ref"] for row in sources if row["applicability"] == "not-applicable"], "coverage_digest": "", "catalog_digest": ""}
    catalog["coverage_digest"] = digest(catalog_coverage_material(catalog)); catalog["catalog_digest"] = digest(catalog, omit="catalog_digest")
    return catalog, [(item[0], item[1]) for item in prepared]


def promote_upstream(root: Path, plan: str, attestation_ref: str, transaction_ref: str, transaction: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    upstream = load_upstream(); reader = upstream.RealRunReader(root); tasks_ref = f"{plan}/tasks.md"; tasks_doc = reader.read_markdown_json(tasks_ref); state = tasks_doc["loki_run_state"]
    immutable_task_bytes = {
        ref: reader.read_bytes(ref) for ref in state["manual_qa_handoff"]["task_refs"]
    }
    immutable_acceptance_material = {
        ref: digest(row)
        for task_ref in state["manual_qa_handoff"]["task_refs"]
        for row in reader.read_markdown_json(task_ref)["task_contract"]["task_validation"]["acceptance_criteria"]
        for ref in [f"{task_ref}#{row['id']}"]
    }
    promote_candidates = enumerate_candidates(reader, state["manual_qa_handoff"])
    target_refs = canonical_transaction_targets(reader, plan, state, state["manual_qa_handoff"], promote_candidates, terminal=True)
    before: list[str] = []
    for ref in target_refs:
        before.append(current_target_digest(reader, state, ref))
    attestation_digest = bytes_digest((root / attestation_ref).read_bytes())
    for gate_ref in state["gate_refs"]:
        gate = reader.read_json(gate_ref)
        if gate["kind"] == "human-validation": gate.update(status="passed", attestation_ref=attestation_ref, attestation_digest=attestation_digest); publish_json_target(root, transaction_ref, transaction, gate_ref, gate)
    transaction["phase"] = "gates-promoted"; transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)
    gate_digests = [bytes_digest((root / ref).read_bytes()) for ref in state["gate_refs"]]
    state.update(status="completed", gate_digests=gate_digests, next_action="none"); state["state_digest"] = upstream.digest_without(state, "state_digest")
    markdown_value = {"loki_run_plan": tasks_doc["loki_run_plan"], "loki_run_state": state}; encoded_json = json.dumps(markdown_value, indent=2, sort_keys=True, ensure_ascii=False)
    original_tasks_text = (root / tasks_ref).read_text(encoding="utf-8")
    replacement_block = f"```json\n{encoded_json}\n```"
    tasks_text, substitutions = re.subn(
        r"```json\n.*?\n```", replacement_block, original_tasks_text, count=1, flags=re.DOTALL
    )
    require("TASKS_JSON_BLOCK_MISSING", substitutions == 1)
    original_outer = re.sub(r"```json\n.*?\n```", "<LOKI_RUN_STATE>", original_tasks_text, count=1, flags=re.DOTALL)
    final_outer = re.sub(r"```json\n.*?\n```", "<LOKI_RUN_STATE>", tasks_text, count=1, flags=re.DOTALL)
    require("TASKS_NON_STATE_BYTES_CHANGED", original_outer == final_outer)
    publish_bytes_target(root, transaction_ref, transaction, tasks_ref, tasks_text.encode("utf-8"))
    result = json.loads((root / state["result_ref"]).read_text()); result.update(status="completed", state_digest=state["state_digest"], gate_digests=gate_digests, next_action="none"); result["result_digest"] = upstream.digest_without(result, "result_digest"); publish_json_target(root, transaction_ref, transaction, state["result_ref"], result)
    dashboard = json.loads((root / state["dashboard_ref"]).read_text()); dashboard.update(status="completed", gate_digests=gate_digests, next_action="none"); dashboard["dashboard_digest"] = upstream.digest_without(dashboard, "dashboard_digest"); publish_json_target(root, transaction_ref, transaction, state["dashboard_ref"], dashboard)
    consistency = json.loads((root / state["consistency_packet_ref"]).read_text()); consistency.update(status="completed", state_digest=state["state_digest"], tasks_md_digest=bytes_digest((root / tasks_ref).read_bytes()), result_digest=bytes_digest((root / state["result_ref"]).read_bytes()), dashboard_digest=bytes_digest((root / state["dashboard_ref"]).read_bytes()), gate_digests=gate_digests); publish_json_target(root, transaction_ref, transaction, state["consistency_packet_ref"], consistency)
    transaction["phase"] = "canonical-promoted"; transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)
    final_reader = upstream.RealRunReader(root); final_state = final_reader.read_markdown_json(tasks_ref)["loki_run_state"]
    require("TASK_CONTRACT_BYTES_CHANGED", all(final_reader.read_bytes(ref) == value for ref, value in immutable_task_bytes.items()))
    final_acceptance_material = {
        ref: digest(row)
        for task_ref in final_state["manual_qa_handoff"]["task_refs"]
        for row in final_reader.read_markdown_json(task_ref)["task_contract"]["task_validation"]["acceptance_criteria"]
        for ref in [f"{task_ref}#{row['id']}"]
    }
    require("AC_CONTRACT_CHANGED", final_acceptance_material == immutable_acceptance_material)
    intended: list[str] = []
    for ref in target_refs: intended.append(current_target_digest(final_reader, final_state, ref))
    return target_refs, before, intended


def build_initial_fixture(root: Path, *, interaction_status: str = "awaiting-attestation", result_status: str = "pending-input", not_applicable_orders: set[int] | None = None) -> str:
    upstream = load_upstream(); tasks_ref, _ = upstream.build_real_run_fixture(root); plan = str(PurePosixPath(tasks_ref).parent)
    tasks_path = root / tasks_ref
    original_tasks = tasks_path.read_text(encoding="utf-8")
    rich_tasks = original_tasks.replace(
        "# Run plan\n\n",
        "---\ntitle: Rich manual-QA fixture\nowner: upstream-plan\n---\n\n# Run plan\n\nOperator prose before the Loki state must remain byte-for-byte stable.\n\n",
        1,
    ) + "\n## Durable operator notes\n\nThis section is outside LokiRunState and must survive promotion unchanged.\n"
    tasks_path.write_text(rich_tasks, encoding="utf-8")
    fixture_payload = json.loads(re.search(r"```json\n(.*?)\n```", rich_tasks, flags=re.DOTALL).group(1))
    fixture_consistency_ref = fixture_payload["loki_run_state"]["consistency_packet_ref"]
    fixture_consistency_path = root / fixture_consistency_ref
    fixture_consistency = json.loads(fixture_consistency_path.read_text(encoding="utf-8"))
    fixture_consistency["tasks_md_digest"] = bytes_digest(tasks_path.read_bytes())
    fixture_consistency_path.write_bytes((json.dumps(fixture_consistency, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    _, reader, state, invocation, handoff, candidates = read_context(root, plan)
    MANUAL_WRITE_TRACE.clear()
    state_ref, handoff_ref = f"{tasks_ref}#loki_run_state", f"{tasks_ref}#loki_run_state.manual_qa_handoff"
    catalog_ref, dashboard_ref = f"{plan}/builds/manual-qa/source-catalog.json", f"{plan}/builds/manual-qa/dashboard.json"
    interaction_ref = str(PurePosixPath(handoff["manual_qa_attestation_ref"]).parent / "interaction.json"); transaction_ref = f"{plan}/builds/manual-qa/transaction.json"
    # The journal is deliberately the first write owned by manual QA.
    target_refs = canonical_transaction_targets(reader, plan, state, handoff, candidates)
    current_digests = [current_target_digest(reader, state, ref) for ref in target_refs]
    transaction = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "batch_kind": "initial", "predecessor_transaction_id": None, "predecessor_transaction_digest": None, "phase": "manual-publishing", "next_target_index": 0, "owner": "loki-manual-qa-orchestrator", "target_refs": target_refs, "before_digests": list(current_digests), "intended_after_digests": list(current_digests), "published_refs": [], "published_digests": [], "residue_refs": [], "residue_digests": [], "attestation_ref": None, "attestation_digest": None, "transaction_digest": ""}; bind_transaction_identity(transaction); transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)
    require("TRANSACTION_NOT_FIRST_MANUAL_WRITE", MANUAL_WRITE_TRACE == [transaction_ref])
    catalog, proposals = make_catalog(plan, state, handoff, candidates, not_applicable_orders)
    for proposal_ref, proposal in proposals: publish_json_target(root, transaction_ref, transaction, proposal_ref, proposal)
    publish_json_target(root, transaction_ref, transaction, catalog_ref, catalog); steps = steps_from_catalog(catalog)
    dashboard = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "plan_directory": plan, "state_ref": state_ref, "state_digest": state["state_digest"], "handoff_ref": handoff_ref, "handoff_digest": digest(handoff), "implementation_result_ref": state["result_ref"], "implementation_result_digest": bytes_digest(reader.read_bytes(state["result_ref"])), "implementation_dashboard_ref": state["dashboard_ref"], "implementation_dashboard_digest": bytes_digest(reader.read_bytes(state["dashboard_ref"])), "implementation_consistency_ref": state["consistency_packet_ref"], "implementation_consistency_digest": bytes_digest(reader.read_bytes(state["consistency_packet_ref"])), "demand_ref": invocation["demand_ref"], "demand_digest": bytes_digest(reader.read_bytes(invocation["demand_ref"])), "analysis_ref": invocation["analysis_ref"], "analysis_digest": bytes_digest(reader.read_bytes(invocation["analysis_ref"])), "source_catalog_ref": catalog_ref, "source_catalog_digest": bytes_digest((root / catalog_ref).read_bytes()), "applicable_source_refs": catalog["applicable_source_refs"], "not_applicable_source_refs": catalog["not_applicable_source_refs"], "steps": steps, "applicable_steps_digest": digest(steps), "dashboard_digest": ""}; dashboard["dashboard_digest"] = digest(dashboard, omit="dashboard_digest"); publish_json_target(root, transaction_ref, transaction, dashboard_ref, dashboard)
    presentation_ref = str(PurePosixPath(handoff["manual_qa_attestation_ref"]).parent / "dashboard-presentation.json")
    publish_json_target(root, transaction_ref, transaction, presentation_ref, dashboard)
    interaction = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "status": interaction_status, "attestation_ref": None, "attestation_digest": None, "report_ref": None, "report_digest": None, "interaction_digest": ""}; interaction["interaction_digest"] = digest(interaction, omit="interaction_digest"); publish_json_target(root, transaction_ref, transaction, interaction_ref, interaction)
    human_gate_refs = [ref for ref in handoff["gate_refs"] if reader.read_json(ref)["kind"] == "human-validation"]
    terminal = reader.read_json(handoff["automatic_evidence_refs"][0]); canonical_refs = [tasks_ref, state["result_ref"], state["dashboard_ref"], state["consistency_packet_ref"]]; canonical_digests = [bytes_digest(reader.read_bytes(tasks_ref)), bytes_digest(reader.read_bytes(state["result_ref"])), bytes_digest(reader.read_bytes(state["dashboard_ref"])), bytes_digest(reader.read_bytes(state["consistency_packet_ref"]))]
    projection = {"source_catalog_ref": catalog_ref, "source_catalog_digest": bytes_digest((root / catalog_ref).read_bytes()), "transaction_ref": transaction_ref, "transaction_id": transaction["transaction_id"], "covered_task_refs": handoff["task_refs"], "covered_acceptance_criterion_refs": handoff["acceptance_criterion_refs"], "covered_gate_refs": human_gate_refs, "covered_changed_surface_refs": handoff["changed_target_refs"], "promoted_task_refs": [], "promoted_acceptance_criterion_refs": [], "promoted_gate_refs": [], "canonical_asset_refs": canonical_refs, "canonical_asset_digests": canonical_digests, "validator_refs": terminal["validator_refs"], "validator_digests": [bytes_digest(reader.read_bytes(ref)) for ref in terminal["validator_refs"]], "audit_refs": terminal["audit_checkpoint_refs"], "audit_digests": [bytes_digest(reader.read_bytes(ref)) for ref in terminal["audit_checkpoint_refs"]], "final_plan_status": "awaiting-manual-qa", "blockers": [], "resume": "Resume from the validated catalog-published transaction and current interaction."}
    result = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "status": result_status, "state_ref": state_ref, "state_digest": state["state_digest"], "handoff_ref": handoff_ref, "handoff_digest": digest(handoff), "dashboard_ref": dashboard_ref, "dashboard_digest": bytes_digest((root / dashboard_ref).read_bytes()), "interaction_ref": interaction_ref, "interaction_digest": bytes_digest((root / interaction_ref).read_bytes()), "attestation_ref": None, "attestation_digest": None, "report_ref": None, "report_digest": None, "applicable_steps_digest": digest(steps), "demand_revalidation_digest": bytes_digest(reader.read_bytes(invocation["demand_ref"])), "automatic_gate_refs": handoff["automatic_evidence_refs"], "automatic_gate_digests": [bytes_digest(reader.read_bytes(ref)) for ref in handoff["automatic_evidence_refs"]], "reconciled_handoff_ref": None, "next_action": "await aggregate human testing statement" if result_status == "pending-input" else "resume", **projection, "result_digest": ""}; result["result_digest"] = digest(result, omit="result_digest"); publish_json_target(root, transaction_ref, transaction, handoff["manual_qa_result_ref"], result)
    final_reader = upstream.RealRunReader(root)
    published_digests = [current_target_digest(final_reader, state, ref) for ref in target_refs]
    transaction.update(next_target_index=len(target_refs), intended_after_digests=published_digests, published_refs=target_refs, published_digests=published_digests, residue_refs=[], residue_digests=[])
    transaction["phase"] = "committed"
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)
    return plan


def precreate_external_resolution_fixture(root: Path, plan: str) -> str:
    """Model bytes produced by an external technical owner, outside manual-QA trace."""
    upstream = load_upstream()
    reader = upstream.RealRunReader(root)
    state = reader.read_markdown_json(f"{plan}/tasks.md")["loki_run_state"]
    resolution_ref = f"{plan}/builds/manual-qa/resolution.json"
    resolution = {"schema_version": 1, "status": "corrected", "run_id": state["run_id"], "execution_id": state["execution_id"]}
    path = root / resolution_ref
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(resolution, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    projection_ref = f"{plan}/builds/manual-qa/technical-revalidation.json"
    projection_refs = [state["result_ref"], state["dashboard_ref"], state["consistency_packet_ref"], *state["manual_qa_handoff"]["automatic_evidence_refs"]]
    projection = {"schema_version": 1, "status": "fresh", "run_id": state["run_id"], "execution_id": state["execution_id"], "resolution_ref": resolution_ref, "resolution_digest": bytes_digest(path.read_bytes()), "projection_refs": projection_refs, "projection_digests": [bytes_digest(reader.read_bytes(ref)) for ref in projection_refs]}
    projection_path = root / projection_ref
    projection_path.write_bytes((json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return resolution_ref


def publish_issue_view(root: Path, plan: str, *, kind: str, resolved: bool) -> None:
    upstream, reader, state, invocation, handoff, candidates = read_context(root, plan)
    run_dir = PurePosixPath(handoff["manual_qa_attestation_ref"]).parent; report_ref = str(run_dir / "report.json"); interaction_ref = str(run_dir / "interaction.json"); result_ref = handoff["manual_qa_result_ref"]
    resolution_ref = f"{plan}/builds/manual-qa/resolution.json"
    if resolved:
        require("EXTERNAL_RESOLUTION_MISSING", (root / resolution_ref).is_file())
    transaction_ref = f"{plan}/builds/manual-qa/transaction.json"; targets = issue_transaction_targets(plan, handoff, resolved=resolved, candidates=candidates if resolved else None)
    before = [current_target_digest(reader, state, ref) for ref in targets]
    predecessor = validate_transaction(reader.read_json(transaction_ref))
    transaction = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "batch_kind": "issue", "predecessor_transaction_id": predecessor["transaction_id"], "predecessor_transaction_digest": bytes_digest(reader.read_bytes(transaction_ref)), "phase": "manual-publishing", "next_target_index": 0, "owner": "loki-manual-qa-orchestrator", "target_refs": targets, "before_digests": list(before), "intended_after_digests": list(before), "published_refs": [], "published_digests": [], "residue_refs": [], "residue_digests": [], "attestation_ref": None, "attestation_digest": None, "transaction_digest": ""}
    bind_transaction_identity(transaction); transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)
    if resolved:
        catalog, proposals = make_catalog(plan, state, handoff, candidates)
        for proposal_ref, proposal in proposals:
            publish_json_target(root, transaction_ref, transaction, proposal_ref, proposal)
        catalog_ref = f"{plan}/builds/manual-qa/source-catalog.json"
        publish_json_target(root, transaction_ref, transaction, catalog_ref, catalog)
        steps = steps_from_catalog(catalog)
        dashboard_ref = f"{plan}/builds/manual-qa/dashboard.json"
        dashboard = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "plan_directory": plan, "state_ref": f"{plan}/tasks.md#loki_run_state", "state_digest": state["state_digest"], "handoff_ref": f"{plan}/tasks.md#loki_run_state.manual_qa_handoff", "handoff_digest": digest(handoff), "implementation_result_ref": state["result_ref"], "implementation_result_digest": bytes_digest(reader.read_bytes(state["result_ref"])), "implementation_dashboard_ref": state["dashboard_ref"], "implementation_dashboard_digest": bytes_digest(reader.read_bytes(state["dashboard_ref"])), "implementation_consistency_ref": state["consistency_packet_ref"], "implementation_consistency_digest": bytes_digest(reader.read_bytes(state["consistency_packet_ref"])), "demand_ref": invocation["demand_ref"], "demand_digest": bytes_digest(reader.read_bytes(invocation["demand_ref"])), "analysis_ref": invocation["analysis_ref"], "analysis_digest": bytes_digest(reader.read_bytes(invocation["analysis_ref"])), "source_catalog_ref": catalog_ref, "source_catalog_digest": bytes_digest((root / catalog_ref).read_bytes()), "applicable_source_refs": catalog["applicable_source_refs"], "not_applicable_source_refs": catalog["not_applicable_source_refs"], "steps": steps, "applicable_steps_digest": digest(steps), "dashboard_digest": ""}
        dashboard["dashboard_digest"] = digest(dashboard, omit="dashboard_digest")
        publish_json_target(root, transaction_ref, transaction, dashboard_ref, dashboard)
        publish_json_target(root, transaction_ref, transaction, str(run_dir / "dashboard-presentation.json"), dashboard)
    terminal_refs = ([f"{plan}/builds/manual-qa/technical-revalidation.json", *handoff["automatic_evidence_refs"]] if resolved else [])
    report = {"schema_version": 1, "report_id": "", "run_id": state["run_id"], "execution_id": state["execution_id"], "status": "resolved" if resolved else "open", "kind": kind, "summary": f"Manual QA reported a {kind}.", "impact": "The current aggregate manual result cannot complete.", "next_action": "Resolve and republish the terminal technical projection.", "recorded_at": "2026-08-01T11:00:00Z", "resolution_ref": resolution_ref if resolved else None, "resolution_digest": bytes_digest((root / resolution_ref).read_bytes()) if resolved else None, "resolved_at": "2026-08-01T11:30:00Z" if resolved else None, "revalidation_refs": terminal_refs, "revalidation_digests": [bytes_digest((root / ref).read_bytes()) for ref in terminal_refs]}; report["report_id"] = "manual-qa-report-v1:" + digest(report_identity_material(report)).split(":", 1)[1]; publish_json_target(root, transaction_ref, transaction, report_ref, report)
    interaction = reader.read_json(interaction_ref); interaction.update(status="issue-resolved" if resolved else "issue-open", report_ref=report_ref, report_digest=bytes_digest((root / report_ref).read_bytes())); interaction["interaction_digest"] = digest(interaction, omit="interaction_digest"); publish_json_target(root, transaction_ref, transaction, interaction_ref, interaction)
    result = reader.read_json(result_ref); result.update(status="in-progress" if resolved else "blocked", interaction_digest=bytes_digest((root / interaction_ref).read_bytes()), report_ref=report_ref, report_digest=bytes_digest((root / report_ref).read_bytes()), transaction_id=transaction["transaction_id"], next_action="rederive complete dashboard" if resolved else "resolve reported issue", blockers=[] if resolved else [report["summary"]]); result["result_digest"] = digest(result, omit="result_digest"); publish_json_target(root, transaction_ref, transaction, result_ref, result)
    final_reader = upstream.RealRunReader(root); after = [current_target_digest(final_reader, state, ref) for ref in targets]
    transaction.update(next_target_index=len(targets), intended_after_digests=after, published_refs=targets, published_digests=after, residue_refs=[], residue_digests=[])
    transaction["phase"] = "committed"
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)


def tree_snapshot(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): bytes_digest(path.read_bytes()) for path in sorted(root.rglob("*")) if path.is_file()}


def handle_help(root: Path, plan: str, mq_id: str) -> dict[str, Any]:
    before = tree_snapshot(root); validate_tree(root, plan)
    dashboard = json.loads((root / plan / "builds/manual-qa/dashboard.json").read_text(encoding="utf-8"))
    matches = [step for step in dashboard["steps"] if step["id"] == mq_id]
    require("HELP_STEP_NOT_FOUND", len(matches) == 1)
    after = tree_snapshot(root); require("HELP_MUTATED_BYTES", before == after)
    return {"schema_version": 1, "status": "read-only-help", "step": matches[0], "bytes_before": before, "bytes_after": after}


def make_attestation_auditor_evidence(run_id: str, execution_id: str, decision: str, assessment_ref: str, dashboard_ref: str) -> bytes:
    agent_run_id = "agent-run-v1:" + hashlib.sha256(f"{run_id}:{execution_id}:{decision}:attestation-auditor".encode()).hexdigest()
    handoff_id = "handoff-v1:" + hashlib.sha256(f"{run_id}:{execution_id}:{assessment_ref}".encode()).hexdigest()
    thread_id = "manual-qa-attestation-thread:" + hashlib.sha256(agent_run_id.encode()).hexdigest()
    raw = f'''<agent_session_evidence schema_version="1">
  <identity><run_id type="loki-run-id">{run_id}</run_id><agent_run_id type="agent-run-id">{agent_run_id}</agent_run_id><handoff_id type="handoff-id">{handoff_id}</handoff_id><agent_name type="agent-name">{ATTESTATION_REVIEWER_IDENTITY}</agent_name></identity>
  <runtime><adapter>fixture-collector</adapter><adapter_version>schema-1</adapter_version><root_session_id type="runtime-root-session-id">manual-qa-root</root_session_id><parent_thread_id type="runtime-parent-thread-id">manual-qa-orchestrator-thread</parent_thread_id><thread_id type="runtime-thread-id">{thread_id}</thread_id><runtime_agent_id type="runtime-agent-id">{ATTESTATION_REVIEWER_IDENTITY}:{agent_run_id}</runtime_agent_id><terminal_status>completed</terminal_status><parent_reference><type>runtime-parent-thread-id</type><value>manual-qa-orchestrator-thread</value></parent_reference></runtime>
  <locator><kind>runtime-pointer</kind><value>{thread_id}</value><portability>same-profile</portability><unavailable_reason>null</unavailable_reason></locator>
  <snapshot><storage_mode>pointer-only</storage_mode><payload_path>null</payload_path><captured_at>null</captured_at><payload_checksum algorithm="sha-256">null</payload_checksum><checksum_absence_reason>Collector retained only the typed runtime pointer; no payload was persisted.</checksum_absence_reason></snapshot>
  <evidence_completeness>
    <dimension name="transcript"><status>pointer-only</status><missing_reason>No sanitized transcript snapshot was persisted.</missing_reason></dimension>
    <dimension name="tool_io"><status>unsupported</status><missing_reason>The read-only reviewer used no auditable tool-I/O export.</missing_reason></dimension>
    <dimension name="errors"><status>pointer-only</status><missing_reason>Terminal runtime pointer exists without an error payload snapshot.</missing_reason></dimension>
    <dimension name="reasoning_summary"><status>unavailable</status><missing_reason>Private reasoning is unavailable and forbidden from persistence.</missing_reason><provenance>none-private-reasoning-excluded</provenance></dimension>
    <dimension name="token_usage"><status>unavailable</status><missing_reason>No verified run-scoped adapter counter was available.</missing_reason></dimension>
    <overall_status>pointer-only</overall_status>
  </evidence_completeness>
  <usage><status>unavailable</status><metric_kind>null</metric_kind><source>null</source><source_scope>null</source_scope><measured_at>null</measured_at><input_tokens>null</input_tokens><cached_input_tokens>null</cached_input_tokens><output_tokens>null</output_tokens><reasoning_output_tokens>null</reasoning_output_tokens><total_tokens>null</total_tokens><unavailable_reason>No verified run-scoped adapter counter was available.</unavailable_reason></usage>
  <security><snapshot_classification>sanitized</snapshot_classification><structural_redaction_result>not-applicable-pointer-only</structural_redaction_result><secret_pii_hardening>deferred-no-payload</secret_pii_hardening><retention_metadata>runtime-pointer-only</retention_metadata><purge_policy>adapter-owned-pointer-lifecycle</purge_policy></security>
  <integrity><canonical_content_checksum algorithm="sha-256"></canonical_content_checksum><result>verified</result><verification_notes>Canonical XML content checksum verified; no payload checksum exists for pointer-only evidence.</verification_notes></integrity>
  <completion_record><agent_run_id type="agent-run-id">{agent_run_id}</agent_run_id><handoff_id type="handoff-id">{handoff_id}</handoff_id><terminal_status>completed</terminal_status><summary>Independent aggregate attestation statement review completed.</summary><changed_files><file>none</file></changed_files><read_files><file>{assessment_ref}</file><file>{dashboard_ref}</file></read_files><validations><validation>manual_qa_attestation_review-v1</validation></validations><material_attempts><attempt>one independent semantic review</attempt></material_attempts><known_errors><error>none</error></known_errors><decisions><decision>{decision}</decision></decisions><residual_risks><risk>pointer-only runtime evidence has no sanitized payload snapshot</risk></residual_risks><next_destination>loki-manual-qa orchestrator</next_destination></completion_record>
  <evidence_policy><mode>evidence-first</mode><gap_handling>preserve-gap</gap_handling><capture_owner>collector-only</capture_owner><retrospective_dispatch>explicit-only</retrospective_dispatch></evidence_policy>
</agent_session_evidence>'''
    root = ET.fromstring(raw)
    checksum = root.find("./integrity/canonical_content_checksum")
    require("EVIDENCE_CHECKSUM_FIELD_MISSING", checksum is not None)
    checksum.text = evidence_canonical_checksum(root)
    encoded = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
    validate_agent_session_evidence_bytes(encoded, run_id=run_id, decision=decision)
    return encoded


def _apply_pinned_assessment_fixture(
    root: Path,
    plan: str,
    human_statement: str,
    signals: dict[str, bool],
    rationale: str,
) -> dict[str, Any]:
    """Test setup only: persist a preclassified, pinned assessment record."""
    require("INTAKE_STATEMENT_INVALID", nonempty(human_statement))
    require("INTAKE_RATIONALE_INVALID", nonempty(rationale))
    signals = closed("INTAKE_ASSESSOR_SIGNALS_INVALID", signals, ASSESSMENT_SIGNAL_KEYS)
    require("INTAKE_ASSESSOR_SIGNALS_INVALID", all(type(value) is bool for value in signals.values()))
    _, reader, state, invocation, handoff, candidates = read_context(root, plan)
    validate_tree(root, plan)
    attestation_path = root / handoff["manual_qa_attestation_ref"]
    require("INTAKE_ATTESTATION_ALREADY_EXISTS", not attestation_path.exists())
    interaction_ref = str(
        PurePosixPath(handoff["manual_qa_attestation_ref"]).parent
        / "interaction.json"
    )
    interaction = validate_interaction(reader.read_json(interaction_ref))
    require(
        "INTAKE_INTERACTION_NOT_PRESENTED",
        interaction["status"] == "awaiting-attestation"
        and interaction["attestation_ref"] is None,
    )
    presentation_ref = str(
        PurePosixPath(handoff["manual_qa_attestation_ref"]).parent
        / "dashboard-presentation.json"
    )
    dashboard = validate_dashboard(reader.read_json(presentation_ref))
    require(
        "INTAKE_DASHBOARD_PRESENTATION_STALE",
        dashboard["applicable_steps_digest"]
        == reader.read_json(f"{plan}/builds/manual-qa/dashboard.json")[
            "applicable_steps_digest"
        ],
    )
    decision = "approve" if signals["explicit_completed_all"] and not any(signals[key] for key in ("ambiguous", "negated", "future_intent", "partial_scope")) else "reject"
    assessment_ref = str(PurePosixPath(handoff["manual_qa_attestation_ref"]).parent / "semantic-assessment.json")
    assessment = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "human_statement": human_statement, "statement_digest": bytes_digest(human_statement.encode("utf-8")), "dashboard_ref": presentation_ref, "dashboard_digest": bytes_digest(reader.read_bytes(presentation_ref)), "applicable_steps_digest": dashboard["applicable_steps_digest"], "assessor_identity": ASSESSOR_IDENTITY, "assessment_owner": ASSESSMENT_OWNER, "evaluator_policy_id": EVALUATOR_POLICY_ID, "evaluator_policy_digest": EVALUATOR_POLICY_DIGEST, "decision": decision, "rationale": rationale, "signals": signals, "assessment_digest": ""}
    assessment["assessment_digest"] = digest(assessment, omit="assessment_digest")
    validate_semantic_assessment(assessment)
    review_ref = str(PurePosixPath(handoff["manual_qa_attestation_ref"]).parent / "attestation-review.json")
    agent_run_evidence_ref = str(PurePosixPath(handoff["manual_qa_attestation_ref"]).parent / "agent-runs/manual-qa-attestation-auditor.xml")
    agent_run_evidence_path = root / agent_run_evidence_ref
    agent_run_evidence_path.parent.mkdir(parents=True, exist_ok=True)
    agent_run_evidence_path.write_bytes(make_attestation_auditor_evidence(state["run_id"], state["execution_id"], decision, assessment_ref, presentation_ref))
    review = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "reviewer_identity": ATTESTATION_REVIEWER_IDENTITY, "independent_agent_run_evidence_ref": agent_run_evidence_ref, "independent_agent_run_evidence_digest": bytes_digest(agent_run_evidence_path.read_bytes()), "statement_digest": assessment["statement_digest"], "dashboard_ref": assessment["dashboard_ref"], "dashboard_digest": assessment["dashboard_digest"], "applicable_steps_digest": assessment["applicable_steps_digest"], "evaluator_policy_id": assessment["evaluator_policy_id"], "evaluator_policy_digest": assessment["evaluator_policy_digest"], "assessment_ref": assessment_ref, "assessment_digest": bytes_digest((json.dumps(assessment, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")), "signals": deepcopy(signals), "decision": decision, "rationale": f"Independent attestation review: {rationale}", "confidence": "high", "completion_record": {"status": "completed", "validators": ["manual_qa_attestation_review-v1-closed-schema-and-correlation"], "gates": [], "risks": [], "success_destination": "loki-manual-qa orchestrator", "failure_destination": "loki-manual-qa terminal failure response"}, "review_digest": ""}
    review["review_digest"] = digest(review, omit="review_digest")
    validate_attestation_review(review)
    terminal_targets = (
        canonical_transaction_targets(
            reader, plan, state, handoff, candidates, terminal=True
        )
        if decision == "approve"
        else rejected_transaction_targets(plan, handoff)
    )
    before = [current_target_digest(reader, state, ref) for ref in terminal_targets]
    transaction_ref = f"{plan}/builds/manual-qa/transaction.json"
    predecessor = validate_transaction(reader.read_json(transaction_ref))
    transaction = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "batch_kind": "terminal" if decision == "approve" else "terminal-reject", "predecessor_transaction_id": predecessor["transaction_id"], "predecessor_transaction_digest": bytes_digest(reader.read_bytes(transaction_ref)), "phase": "journal-created", "next_target_index": 0, "owner": ASSESSMENT_OWNER, "target_refs": terminal_targets, "before_digests": list(before), "intended_after_digests": list(before), "published_refs": [], "published_digests": [], "residue_refs": [], "residue_digests": [], "attestation_ref": None, "attestation_digest": None, "transaction_digest": ""}
    bind_transaction_identity(transaction)
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest")
    MANUAL_WRITE_TRACE.clear()
    write_json(root, transaction_ref, transaction)
    require("TRANSACTION_NOT_FIRST_TERMINAL_WRITE", MANUAL_WRITE_TRACE == [transaction_ref])
    publish_json_target(root, transaction_ref, transaction, assessment_ref, assessment)
    transaction["phase"] = "assessment-published"
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest")
    write_json(root, transaction_ref, transaction)
    publish_json_target(root, transaction_ref, transaction, review_ref, review)
    transaction["phase"] = "review-published"
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest")
    write_json(root, transaction_ref, transaction)
    if decision == "reject":
        interaction = reader.read_json(interaction_ref)
        publish_json_target(root, transaction_ref, transaction, interaction_ref, interaction)
        result_ref = handoff["manual_qa_result_ref"]
        result = reader.read_json(result_ref)
        result.update(
            transaction_id=transaction["transaction_id"],
            next_action="submit a new human_statement for a new terminal batch",
        )
        result["result_digest"] = digest(result, omit="result_digest")
        publish_json_target(root, transaction_ref, transaction, result_ref, result)
        transaction.update(phase="committed", residue_refs=[], residue_digests=[])
        transaction["transaction_digest"] = digest(transaction, omit="transaction_digest")
        write_json(root, transaction_ref, transaction)
        validate_transaction(transaction)
        return {"schema_version": 1, "status": "rejected", "attestation_ref": None, "assessment_ref": assessment_ref, "assessment_digest": bytes_digest((root / assessment_ref).read_bytes()), "transaction_ref": transaction_ref, "transaction_id": transaction["transaction_id"]}
    require("ATTESTATION_REVIEW_DECISION_MISMATCH", assessment["decision"] == review["decision"] == "approve")
    attestation = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "applicable_steps_digest": dashboard["applicable_steps_digest"], "demand_digest": invocation["command_identity"]["demand_digest"], "analysis_digest": invocation["command_identity"]["analysis_digest"], "human_statement": human_statement, "declaration": DECLARATION, "attestation_review_ref": review_ref, "attestation_review_digest": bytes_digest((root / review_ref).read_bytes()), "recorded_at": "2026-08-01T12:00:00Z"}
    publish_json_target(root, transaction_ref, transaction, handoff["manual_qa_attestation_ref"], attestation)
    validate_attestation(attestation)
    transaction.update(phase="attested", attestation_ref=handoff["manual_qa_attestation_ref"], attestation_digest=bytes_digest(attestation_path.read_bytes()))
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest")
    write_json(root, transaction_ref, transaction)
    validate_transaction(transaction)
    return {"schema_version": 1, "status": "created", "attestation_ref": handoff["manual_qa_attestation_ref"], "attestation_digest": bytes_digest(attestation_path.read_bytes()), "assessment_ref": assessment_ref, "assessment_digest": bytes_digest((root / assessment_ref).read_bytes()), "review_ref": review_ref, "review_digest": bytes_digest((root / review_ref).read_bytes()), "transaction_ref": transaction_ref, "transaction_id": transaction["transaction_id"]}


def build_manual_fixture(root: Path, plan_directory: str | None = None, *, apply_acceptance: bool = True) -> str:
    plan_directory = plan_directory or build_initial_fixture(root)
    upstream = load_upstream()
    tasks_ref = f"{plan_directory}/tasks.md"
    if apply_acceptance:
        outcome = _apply_pinned_assessment_fixture(
            root,
            plan_directory,
            "Já testei todos os itens aplicáveis e aprovo o resultado.",
            {"explicit_completed_all": True, "ambiguous": False, "negated": False, "future_intent": False, "partial_scope": False},
            "Pinned fixture assessment marks the aggregate statement complete.",
        )
        require("TERMINAL_FIXTURE_ATTESTATION_REJECTED", outcome["status"] == "created")
    _, reader, state, invocation, handoff, candidates = read_context(root, plan_directory)
    state_ref = f"{tasks_ref}#loki_run_state"
    handoff_ref = f"{tasks_ref}#loki_run_state.manual_qa_handoff"
    catalog_ref = f"{plan_directory}/builds/manual-qa/source-catalog.json"
    dashboard_ref = f"{plan_directory}/builds/manual-qa/dashboard.json"
    interaction_ref = str(PurePosixPath(handoff["manual_qa_attestation_ref"]).parent / "interaction.json")
    result_ref = handoff["manual_qa_result_ref"]
    consistency_ref = f"{plan_directory}/builds/manual-qa/consistency.json"
    transaction_ref = f"{plan_directory}/builds/manual-qa/transaction.json"
    transaction = validate_transaction(reader.read_json(transaction_ref))
    target_refs, _, _ = promote_upstream(
        root,
        plan_directory,
        handoff["manual_qa_attestation_ref"],
        transaction_ref,
        transaction,
    )
    _, reader, state, invocation, handoff, candidates = read_context(root, plan_directory)
    catalog, proposals = make_catalog(plan_directory, state, handoff, candidates); steps = steps_from_catalog(catalog)
    for proposal_ref, proposal in proposals: publish_json_target(root, transaction_ref, transaction, proposal_ref, proposal)
    publish_json_target(root, transaction_ref, transaction, catalog_ref, catalog)
    dashboard = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "plan_directory": plan_directory, "state_ref": state_ref, "state_digest": state["state_digest"], "handoff_ref": handoff_ref, "handoff_digest": digest(handoff), "implementation_result_ref": state["result_ref"], "implementation_result_digest": bytes_digest(reader.read_bytes(state["result_ref"])), "implementation_dashboard_ref": state["dashboard_ref"], "implementation_dashboard_digest": bytes_digest(reader.read_bytes(state["dashboard_ref"])), "implementation_consistency_ref": state["consistency_packet_ref"], "implementation_consistency_digest": bytes_digest(reader.read_bytes(state["consistency_packet_ref"])), "demand_ref": invocation["demand_ref"], "demand_digest": bytes_digest(reader.read_bytes(invocation["demand_ref"])), "analysis_ref": invocation["analysis_ref"], "analysis_digest": bytes_digest(reader.read_bytes(invocation["analysis_ref"])), "source_catalog_ref": catalog_ref, "source_catalog_digest": bytes_digest((root / catalog_ref).read_bytes()), "applicable_source_refs": catalog["applicable_source_refs"], "not_applicable_source_refs": catalog["not_applicable_source_refs"], "steps": steps, "applicable_steps_digest": digest(steps), "dashboard_digest": ""}
    dashboard["dashboard_digest"] = digest(dashboard, omit="dashboard_digest"); publish_json_target(root, transaction_ref, transaction, dashboard_ref, dashboard)
    interaction = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "status": "attested", "attestation_ref": handoff["manual_qa_attestation_ref"], "attestation_digest": bytes_digest((root / handoff["manual_qa_attestation_ref"]).read_bytes()), "report_ref": None, "report_digest": None, "interaction_digest": ""}
    interaction["interaction_digest"] = digest(interaction, omit="interaction_digest")
    publish_json_target(root, transaction_ref, transaction, interaction_ref, interaction)
    automatic_digests = [bytes_digest((root / ref).read_bytes()) for ref in handoff["automatic_evidence_refs"]]
    terminal = reader.read_json(handoff["automatic_evidence_refs"][0]); human_gate_refs = [ref for ref in handoff["gate_refs"] if reader.read_json(ref)["kind"] == "human-validation"]
    canonical_refs = [tasks_ref, state["result_ref"], state["dashboard_ref"], state["consistency_packet_ref"]]
    canonical_digests = [bytes_digest(reader.read_bytes(tasks_ref)), bytes_digest(reader.read_bytes(state["result_ref"])), bytes_digest(reader.read_bytes(state["dashboard_ref"])), bytes_digest(reader.read_bytes(state["consistency_packet_ref"]))]
    terminal_projection = {"source_catalog_ref": catalog_ref, "source_catalog_digest": bytes_digest((root / catalog_ref).read_bytes()), "transaction_ref": transaction_ref, "transaction_id": transaction["transaction_id"], "covered_task_refs": handoff["task_refs"], "covered_acceptance_criterion_refs": handoff["acceptance_criterion_refs"], "covered_gate_refs": human_gate_refs, "covered_changed_surface_refs": handoff["changed_target_refs"], "promoted_task_refs": [], "promoted_acceptance_criterion_refs": [], "promoted_gate_refs": human_gate_refs, "canonical_asset_refs": canonical_refs, "canonical_asset_digests": canonical_digests, "validator_refs": terminal["validator_refs"], "validator_digests": [bytes_digest(reader.read_bytes(ref)) for ref in terminal["validator_refs"]], "audit_refs": terminal["audit_checkpoint_refs"], "audit_digests": [bytes_digest(reader.read_bytes(ref)) for ref in terminal["audit_checkpoint_refs"]], "final_plan_status": "completed", "blockers": [], "resume": "Validated committed terminal replay is a no-op."}
    result = {"schema_version": 1, "run_id": state["run_id"], "execution_id": state["execution_id"], "status": "completed", "state_ref": state_ref, "state_digest": state["state_digest"], "handoff_ref": handoff_ref, "handoff_digest": digest(handoff), "dashboard_ref": dashboard_ref, "dashboard_digest": bytes_digest((root / dashboard_ref).read_bytes()), "interaction_ref": interaction_ref, "interaction_digest": bytes_digest((root / interaction_ref).read_bytes()), "attestation_ref": handoff["manual_qa_attestation_ref"], "attestation_digest": bytes_digest((root / handoff["manual_qa_attestation_ref"]).read_bytes()), "report_ref": None, "report_digest": None, "applicable_steps_digest": digest(steps), "demand_revalidation_digest": bytes_digest((root / invocation["demand_ref"]).read_bytes()), "automatic_gate_refs": handoff["automatic_evidence_refs"], "automatic_gate_digests": automatic_digests, "reconciled_handoff_ref": handoff_ref, "next_action": "none", **terminal_projection, "result_digest": ""}
    result["result_digest"] = digest(result, omit="result_digest")
    publish_json_target(root, transaction_ref, transaction, result_ref, result)
    consistency = {key: result[key] for key in CONSISTENCY_KEYS if key in result and key not in {"status", "next_action", "result_digest"}}
    consistency.update({"result_ref": result_ref, "result_digest": bytes_digest((root / result_ref).read_bytes()), "consistency_digest": ""})
    consistency["consistency_digest"] = digest(consistency, omit="consistency_digest")
    publish_json_target(root, transaction_ref, transaction, consistency_ref, consistency)
    require("TRANSACTION_TERMINAL_TARGETS_INCOMPLETE", transaction["next_target_index"] == len(target_refs))
    transaction["phase"] = "consistency-published"; transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)
    transaction.update(phase="committed", residue_refs=[], residue_digests=[], attestation_ref=handoff["manual_qa_attestation_ref"], attestation_digest=bytes_digest((root / handoff["manual_qa_attestation_ref"]).read_bytes()))
    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest"); write_json(root, transaction_ref, transaction)
    return plan_directory


def make_record(kind: str) -> dict[str, Any]:
    run_id, execution_id, plan = "loki-run-v2:" + "a" * 64, "loki-execution-v2:" + "b" * 64, "planos/demo"
    handoff = {"schema_version": 2, "status": "ready-for-manual-qa", "run_id": run_id, "execution_id": execution_id, "plan_directory": plan, "automatic_evidence_refs": [f"{plan}/terminal.json"], "manual_qa_result_ref": f"{plan}/builds/manual-qa/result.json", "manual_qa_attestation_ref": f"{plan}/interaction/manual-qa/{run_id}/attestation.json", "task_refs": [f"{plan}/task-1.md"], "acceptance_criterion_refs": [f"{plan}/task-1.md#AC-1"], "gate_refs": [f"{plan}/gate.json"], "changed_target_refs": ["src/demo.txt"], "reason": None}
    statement = "The visible behavior matches the approved criterion."
    step = {"schema_version": 1, "id": "MQ-01", "source_kind": "acceptance-criterion", "source_ref": f"{plan}/task-1.md#AC-1", "source_order": 0, "title": statement, "environment": "Current consumer validation environment for <human_validation_gate>.", "prerequisites": "Automatic validation and the correlated ready handoff are current.", "initial_state": "The current implementation is loaded at the handoff target digests.", "actions": ["Exercise the behavior stated by AC-1.", "Compare the observation with the persisted acceptance-criterion statement."], "expected_result": statement, "success_signal": "The persisted acceptance-criterion statement is observably true.", "failure_signal": "The persisted acceptance-criterion statement is false, absent, or blocked.", "cleanup": "Restore the validation environment to its pre-test state.", "automation_limit": "The eligible handoff requires aggregate human confirmation."}
    assessment_statement = "I tested every applicable item and approve the result."
    assessment = {"schema_version": 1, "run_id": run_id, "execution_id": execution_id, "human_statement": assessment_statement, "statement_digest": bytes_digest(assessment_statement.encode("utf-8")), "dashboard_ref": f"{plan}/interaction/manual-qa/{run_id}/dashboard-presentation.json", "dashboard_digest": "sha256:" + "7" * 64, "applicable_steps_digest": digest([step]), "assessor_identity": ASSESSOR_IDENTITY, "assessment_owner": ASSESSMENT_OWNER, "evaluator_policy_id": EVALUATOR_POLICY_ID, "evaluator_policy_digest": EVALUATOR_POLICY_DIGEST, "decision": "approve", "rationale": "The pinned semantic assessor found an explicit completed aggregate declaration without a blocking signal.", "signals": {"explicit_completed_all": True, "ambiguous": False, "negated": False, "future_intent": False, "partial_scope": False}, "assessment_digest": ""}
    assessment["assessment_digest"] = digest(assessment, omit="assessment_digest")
    review_ref = f"{plan}/interaction/manual-qa/{run_id}/attestation-review.json"
    review = {"schema_version": 1, "run_id": run_id, "execution_id": execution_id, "reviewer_identity": ATTESTATION_REVIEWER_IDENTITY, "independent_agent_run_evidence_ref": f"{plan}/interaction/manual-qa/{run_id}/agent-runs/manual-qa-attestation-auditor.xml", "independent_agent_run_evidence_digest": "sha256:" + "8" * 64, "statement_digest": assessment["statement_digest"], "dashboard_ref": assessment["dashboard_ref"], "dashboard_digest": assessment["dashboard_digest"], "applicable_steps_digest": assessment["applicable_steps_digest"], "evaluator_policy_id": EVALUATOR_POLICY_ID, "evaluator_policy_digest": EVALUATOR_POLICY_DIGEST, "assessment_ref": f"{plan}/interaction/manual-qa/{run_id}/semantic-assessment.json", "assessment_digest": "sha256:" + "9" * 64, "signals": deepcopy(assessment["signals"]), "decision": "approve", "rationale": "Independent review confirms completed aggregate testing with no blocking semantic signal.", "confidence": "high", "completion_record": {"status": "completed", "validators": ["manual_qa_attestation_review-v1-closed-schema-and-correlation"], "gates": [], "risks": [], "success_destination": "loki-manual-qa orchestrator", "failure_destination": "loki-manual-qa terminal failure response"}, "review_digest": ""}
    review["review_digest"] = digest(review, omit="review_digest")
    attestation = {"schema_version": 1, "run_id": run_id, "execution_id": execution_id, "applicable_steps_digest": digest([step]), "demand_digest": "sha256:" + "c" * 64, "analysis_digest": "sha256:" + "d" * 64, "human_statement": "I tested everything and approve it.", "declaration": DECLARATION, "attestation_review_ref": review_ref, "attestation_review_digest": "sha256:" + "a" * 64, "recorded_at": "2026-08-01T12:00:00Z"}
    report = {"schema_version": 1, "report_id": "", "run_id": run_id, "execution_id": execution_id, "status": "resolved", "kind": "failure", "summary": "The visible criterion initially failed.", "impact": "The aggregate result could not be approved.", "next_action": "Revalidate the corrected terminal projection.", "recorded_at": "2026-08-01T11:00:00Z", "resolution_ref": f"{plan}/resolution.json", "resolution_digest": "sha256:" + "e" * 64, "resolved_at": "2026-08-01T11:30:00Z", "revalidation_refs": [f"{plan}/revalidation.json"], "revalidation_digests": ["sha256:" + "f" * 64]}
    report["report_id"] = "manual-qa-report-v1:" + digest(report_identity_material(report)).split(":", 1)[1]
    candidate_ref = f"{plan}/task-1.md#AC-1"
    fact_digest = "sha256:" + "6" * 64
    fact_statement = "The visible behavior matches the approved criterion."
    proposal = {"schema_version": 1, "run_id": run_id, "execution_id": execution_id, "caller": "loki-manual-qa", "agent": "runtime-qa", "allowed_writes": [], "candidate_ref": candidate_ref, "candidate_digest": fact_digest, "source_kind": "acceptance-criterion", "applicability": "applicable", "not_applicable_reason": None, "environment": f"Browser build with the visible demo route enabled for {candidate_ref}.", "prerequisites": f"Load the validated demo save at the start screen with source digest {fact_digest}.", "initial_state": "The demo starts before the changed interaction.", "actions": ["Activate the changed interaction from the validated demo route.", f"Bind observable fact {candidate_ref} at {fact_digest} exactly: {fact_statement}"], "expected_result": fact_statement, "success_signal": "The changed interaction becomes visibly complete.", "failure_signal": "The interaction is absent or visibly contradicted.", "cleanup": "Return the demo to its documented start screen.", "automation_limit": "Visual presentation requires direct human observation.", "evidence_refs": [f"{plan}/task-1.md"], "completion_record": {"status": "completed", "validators": ["proposal-schema-and-source-correlation"], "gates": [], "risks": [], "next_destination": "loki-manual-qa orchestrator"}}
    if kind == "handoff": return handoff
    if kind == "step": return step
    if kind == "attestation": return attestation
    if kind == "semantic-assessment": return assessment
    if kind == "attestation-review": return review
    if kind == "report-resolved": return report
    if kind == "runtime-qa-proposal": return proposal
    if kind == "runtime-qa-human-gate-not-applicable":
        proposal.update(source_kind="human-gate", applicability="not-applicable", not_applicable_reason="incorrect waiver")
        return proposal
    if kind == "dashboard":
        p = {"schema_version": 1, "run_id": run_id, "execution_id": execution_id, "plan_directory": plan, "state_ref": f"{plan}/tasks.md#loki_run_state", "state_digest": "sha256:" + "1" * 64, "handoff_ref": f"{plan}/tasks.md#loki_run_state.manual_qa_handoff", "handoff_digest": digest(handoff), "implementation_result_ref": f"{plan}/result.json", "implementation_result_digest": "sha256:" + "2" * 64, "implementation_dashboard_ref": f"{plan}/dashboard.json", "implementation_dashboard_digest": "sha256:" + "3" * 64, "implementation_consistency_ref": f"{plan}/consistency.json", "implementation_consistency_digest": "sha256:" + "4" * 64, "demand_ref": f"{plan}/demand.md", "demand_digest": attestation["demand_digest"], "analysis_ref": f"{plan}/analysis.md", "analysis_digest": attestation["analysis_digest"], "source_catalog_ref": f"{plan}/builds/manual-qa/source-catalog.json", "source_catalog_digest": "sha256:" + "5" * 64, "applicable_source_refs": [step["source_ref"]], "not_applicable_source_refs": [], "steps": [step], "applicable_steps_digest": digest([step]), "dashboard_digest": ""}
        p["dashboard_digest"] = digest(p, omit="dashboard_digest"); return p
    if kind == "interaction-attested":
        p = {"schema_version": 1, "run_id": run_id, "execution_id": execution_id, "status": "attested", "attestation_ref": handoff["manual_qa_attestation_ref"], "attestation_digest": "sha256:" + "e" * 64, "report_ref": None, "report_digest": None, "interaction_digest": ""}; p["interaction_digest"] = digest(p, omit="interaction_digest"); return p
    raise ContractError("FIXTURE_RECORD_KIND_INVALID")


VALIDATORS: dict[str, Callable[[Any], Any]] = {"handoff": validate_handoff, "source": validate_source, "source-catalog": validate_catalog, "runtime-qa-proposal": validate_proposal, "runtime-qa-human-gate-not-applicable": validate_proposal, "step": validate_step, "dashboard": validate_dashboard, "semantic-assessment": validate_semantic_assessment, "attestation-review": validate_attestation_review, "attestation": validate_attestation, "report-resolved": validate_report, "interaction-attested": validate_interaction, "transaction": validate_transaction, "result": validate_result, "consistency": validate_consistency}


def mutate(document: Any, mutation: dict[str, Any]) -> None:
    cursor = document
    for part in mutation["path"][:-1]: cursor = cursor[part]
    key = mutation["path"][-1]
    if mutation["op"] == "set": cursor[key] = mutation.get("value")
    elif mutation["op"] == "delete": del cursor[key]
    else: raise ContractError("FIXTURE_MUTATION_INVALID")


def self_test() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    scanned_commands = validate_manual_qa_command_ownership(ROOT)
    results.append({"id": "current-tree-manual-qa-exclusive-owner", "result": "accepted", "commands_scanned": len(scanned_commands)})
    with tempfile.TemporaryDirectory(prefix="loki-manual-owner-scan-") as temp:
        evil_root = Path(temp)
        evil_bundle = evil_root / "skills/loki-evil"
        evil_bundle.mkdir(parents=True)
        (evil_bundle / "SKILL.md").write_text("# evil\n\nDerive and present manual QA steps, then collect approval.\n", encoding="utf-8")
        try:
            validate_manual_qa_command_ownership(evil_root)
        except ContractError as exc:
            require("MANUAL_QA_EVIL_COMMAND_ERROR_MISMATCH", str(exc).startswith("MANUAL_QA_FOREIGN_OWNER:"))
        else:
            raise ContractError("MANUAL_QA_EVIL_COMMAND_ACCEPTED")
        results.append({"id": "current-tree-manual-qa-evil-command", "result": "expected-rejection"})
    synthetic_batches = {"initial": 3, "issue": 3, "terminal-reject": 4}
    for batch_kind, target_count in synthetic_batches.items():
        for resume_mode in ("normal", "recovery", "post-write"):
            for fault_index in range(target_count + 1):
                with tempfile.TemporaryDirectory(prefix=f"loki-manual-{batch_kind}-resume-") as temp:
                    root = Path(temp)
                    run_id = "loki-run-v2:" + "1" * 64
                    execution_id = "loki-execution-v2:" + "2" * 64
                    target_refs = [f"planos/resume/{batch_kind}/target-{index}.json" for index in range(target_count)]
                    intended_bytes = {ref: (json.dumps({"batch": batch_kind, "target": index}, sort_keys=True) + "\n").encode("utf-8") for index, ref in enumerate(target_refs)}
                    for ref in target_refs[:fault_index]:
                        path = root / ref
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(intended_bytes[ref])
                    if resume_mode == "post-write" and fault_index < target_count:
                        path = root / target_refs[fault_index]
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(intended_bytes[target_refs[fault_index]])
                    predecessor_id = None if batch_kind == "initial" else "manual-qa-transaction-v1:" + "3" * 64
                    predecessor_digest = None if batch_kind == "initial" else "sha256:" + "4" * 64
                    normal_phase = (
                        ("journal-created" if fault_index == 0 else "manual-publishing" if fault_index < target_count else "committed")
                        if batch_kind in {"initial", "issue"}
                        else {0: "journal-created", 1: "assessment-published", 2: "review-published", target_count: "committed"}.get(fault_index, "recovery-required")
                    )
                    phase = "recovery-required" if resume_mode != "normal" or normal_phase == "recovery-required" else normal_phase
                    published_refs = target_refs[:fault_index]
                    published_digests = [bytes_digest(intended_bytes[ref]) for ref in published_refs]
                    transaction = {"schema_version": 1, "run_id": run_id, "execution_id": execution_id, "batch_kind": batch_kind, "predecessor_transaction_id": predecessor_id, "predecessor_transaction_digest": predecessor_digest, "phase": phase, "next_target_index": fault_index, "owner": ASSESSMENT_OWNER, "target_refs": target_refs, "before_digests": ["sha256:" + "0" * 64] * target_count, "intended_after_digests": [bytes_digest(intended_bytes[ref]) for ref in target_refs], "published_refs": published_refs, "published_digests": published_digests, "residue_refs": published_refs if phase == "recovery-required" else [], "residue_digests": published_digests if phase == "recovery-required" else [], "attestation_ref": None, "attestation_digest": None, "transaction_digest": ""}
                    bind_transaction_identity(transaction)
                    transaction["transaction_digest"] = digest(transaction, omit="transaction_digest")
                    transaction_ref = f"planos/resume/{batch_kind}/transaction.json"
                    write_json(root, transaction_ref, transaction)
                    outcome = resume_transaction(root, transaction_ref, intended_bytes)
                    require("SYNTHETIC_BATCH_RESUME_FAILED", outcome["status"] in {"committed", "no-op"})
                    replay = resume_transaction(root, transaction_ref, intended_bytes)
                    require("SYNTHETIC_BATCH_REPLAY_FAILED", replay["status"] == "no-op")
                    results.append({"id": f"{batch_kind}-{resume_mode}-{fault_index:02d}", "result": "committed-then-no-op"})
    collision_base = {"schema_version": 1, "run_id": "loki-run-v2:" + "5" * 64, "execution_id": "loki-execution-v2:" + "6" * 64, "batch_kind": "issue", "target_refs": ["planos/resume/issue/report.json"]}
    intent = digest({"schema_version": 1, "batch_kind": collision_base["batch_kind"], "target_refs": collision_base["target_refs"]})
    open_id = transaction_identity(collision_base["run_id"], collision_base["execution_id"], "issue", intent, "manual-qa-transaction-v1:" + "7" * 64)
    resolved_id = transaction_identity(collision_base["run_id"], collision_base["execution_id"], "issue", intent, open_id)
    repeated_reject_id = transaction_identity(collision_base["run_id"], collision_base["execution_id"], "terminal-reject", digest({"schema_version": 1, "batch_kind": "terminal-reject", "target_refs": collision_base["target_refs"]}), resolved_id)
    approve_id = transaction_identity(collision_base["run_id"], collision_base["execution_id"], "terminal", digest({"schema_version": 1, "batch_kind": "terminal", "target_refs": collision_base["target_refs"]}), repeated_reject_id)
    require("TRANSACTION_TRANSITION_ID_COLLISION", len({open_id, resolved_id, repeated_reject_id, approve_id}) == 4)
    results.append({"id": "transaction-transition-identities-distinct", "result": "accepted"})
    with tempfile.TemporaryDirectory(prefix="loki-manual-resume-") as temp:
        checkpoint_root = Path(temp); checkpoint_plan = build_manual_fixture(checkpoint_root)
        committed = json.loads((checkpoint_root / checkpoint_plan / "builds/manual-qa/transaction.json").read_text(encoding="utf-8"))
        first_proposal = next(index for index, ref in enumerate(committed["target_refs"]) if "/proposals/" in ref)
        tasks_index = committed["target_refs"].index(f"{checkpoint_plan}/tasks.md")
        cursors = {"journal-created": 0, "assessment-published": 1, "review-published": 2, "attested": 3, "gates-promoted": tasks_index, "canonical-promoted": first_proposal, "consistency-published": len(committed["target_refs"]), "committed": len(committed["target_refs"])}
        for phase, cursor in cursors.items():
            checkpoint = deepcopy(committed); attested = phase not in {"journal-created", "assessment-published", "review-published"}
            checkpoint.update(phase=phase, next_target_index=cursor, published_refs=committed["target_refs"][:cursor], published_digests=committed["published_digests"][:cursor], attestation_ref=committed["attestation_ref"] if attested else None, attestation_digest=committed["attestation_digest"] if attested else None)
            checkpoint["transaction_digest"] = digest(checkpoint, omit="transaction_digest")
            require("RESUME_CHECKPOINT_CURSOR_MISMATCH", resume_transaction_checkpoint(checkpoint) == cursor)
            results.append({"id": f"resume-real-builder-{phase}", "result": "accepted"})
        result_path = checkpoint_root / checkpoint_plan / "builds/manual-qa/result.json"
        false_result = json.loads(result_path.read_text(encoding="utf-8"))
        false_result["promoted_gate_refs"] = []
        false_result["result_digest"] = digest(false_result, omit="result_digest")
        try:
            validate_result(false_result)
        except ContractError as exc:
            require("FALSE_COMPLETED_RESULT_ERROR_MISMATCH", str(exc) == "TERMINAL_PROJECTION_HUMAN_PROMOTION_EMPTY")
        else:
            raise ContractError("FALSE_COMPLETED_RESULT_ACCEPTED")
        results.append({"id": "false-completed-result-empty-human-promotion", "result": "expected-rejection"})
        consistency_path = checkpoint_root / checkpoint_plan / "builds/manual-qa/consistency.json"
        false_consistency = json.loads(consistency_path.read_text(encoding="utf-8"))
        false_consistency["covered_task_refs"] = []
        false_consistency["consistency_digest"] = digest(false_consistency, omit="consistency_digest")
        try:
            validate_consistency(false_consistency)
        except ContractError as exc:
            require("FALSE_COMPLETED_CONSISTENCY_ERROR_MISMATCH", str(exc) == "TERMINAL_PROJECTION_COVERAGE_EMPTY")
        else:
            raise ContractError("FALSE_COMPLETED_CONSISTENCY_ACCEPTED")
        results.append({"id": "false-completed-consistency-empty-coverage", "result": "expected-rejection"})
        terminal_blueprint = deepcopy(committed)
        terminal_intended = {
            ref: (checkpoint_root / ref.partition("#")[0]).read_bytes()
            for ref in committed["target_refs"]
        }
        terminal_review = json.loads(terminal_intended[committed["target_refs"][1]])
        terminal_agent_evidence_ref = terminal_review["independent_agent_run_evidence_ref"]
        terminal_agent_evidence_bytes = (checkpoint_root / terminal_agent_evidence_ref).read_bytes()
    for fault_index in range(len(terminal_blueprint["target_refs"]) + 1):
        with tempfile.TemporaryDirectory(prefix="loki-manual-real-terminal-resume-") as temp:
            resume_root = Path(temp)
            resume_plan = build_initial_fixture(resume_root)
            agent_evidence_path = resume_root / terminal_agent_evidence_ref
            agent_evidence_path.parent.mkdir(parents=True, exist_ok=True)
            agent_evidence_path.write_bytes(terminal_agent_evidence_bytes)
            transaction_ref = f"{resume_plan}/builds/manual-qa/transaction.json"
            predecessor_bytes = (resume_root / transaction_ref).read_bytes()
            predecessor = validate_transaction(json.loads(predecessor_bytes.decode("utf-8")))
            target_refs = terminal_blueprint["target_refs"]
            require(
                "REAL_TERMINAL_RESUME_BEFORE_FIXTURE_DRIFT",
                [frozen_target_digest(resume_root, ref) for ref in target_refs]
                == terminal_blueprint["before_digests"],
            )
            for ref in target_refs[:fault_index]:
                path = resume_root / ref.partition("#")[0]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(terminal_intended[ref])
            if fault_index < len(target_refs):
                crash_path = resume_root / target_refs[fault_index].partition("#")[0]
                crash_path.parent.mkdir(parents=True, exist_ok=True)
                crash_path.write_bytes(terminal_intended[target_refs[fault_index]])
            published_refs = target_refs[:fault_index]
            published_digests = [bytes_digest(terminal_intended[ref]) for ref in published_refs]
            transaction = deepcopy(terminal_blueprint)
            transaction.update(
                predecessor_transaction_id=predecessor["transaction_id"],
                predecessor_transaction_digest=bytes_digest(predecessor_bytes),
                phase="recovery-required",
                next_target_index=fault_index,
                published_refs=published_refs,
                published_digests=published_digests,
                residue_refs=published_refs,
                residue_digests=published_digests,
                attestation_ref=target_refs[2] if fault_index >= 3 else None,
                attestation_digest=published_digests[2] if fault_index >= 3 else None,
            )
            boundary = terminal_phase_for_cursor(transaction)
            if boundary is not None:
                transaction["phase"] = boundary
            transaction["transaction_digest"] = digest(transaction, omit="transaction_digest")
            write_json(resume_root, transaction_ref, transaction)
            validate_transaction(transaction)
            if fault_index == target_refs.index(f"{resume_plan}/tasks.md"):
                drift_ref = target_refs[fault_index]
                drift_path = resume_root / drift_ref
                original_bytes = drift_path.read_bytes()
                drift_path.write_bytes(original_bytes + b"concurrent drift\n")
                try:
                    resume_transaction(resume_root, transaction_ref, terminal_intended)
                except ContractError as exc:
                    require("BEFORE_WRITE_DRIFT_ERROR_MISMATCH", str(exc) == "TRANSACTION_BEFORE_WRITE_DRIFT")
                else:
                    raise ContractError("BEFORE_WRITE_DRIFT_ACCEPTED")
                drift_path.write_bytes(original_bytes)
                results.append({"id": "real-terminal-resume-blocks-tasks-before-write-drift", "result": "expected-rejection"})
            resumed = resume_transaction(resume_root, transaction_ref, terminal_intended)
            require("REAL_TERMINAL_RESUME_NOT_COMMITTED", resumed["status"] == "committed")
            validate_tree(resume_root, resume_plan)
            replay = resume_transaction(resume_root, transaction_ref, terminal_intended)
            require("REAL_TERMINAL_RESUME_REPLAY_NOT_NOOP", replay["status"] == "no-op")
            phase_label = boundary or "recovery-required"
            results.append({"id": f"real-terminal-resume-{fault_index:02d}-{phase_label}", "result": "committed-then-no-op"})
    record_doc = json.loads((FIXTURE_ROOT / "record-cases.json").read_text(encoding="utf-8"))
    for case in record_doc["cases"]:
        payload = make_record(case["record"])
        if case["mutation"]: mutate(payload, case["mutation"])
        try:
            VALIDATORS[case["record"]](payload)
            actual, error = "accept", None
        except ContractError as exc:
            actual, error = "reject", str(exc)
        require("FIXTURE_OUTCOME_MISMATCH", actual == case["expect"])
        require("FIXTURE_ERROR_MISMATCH", actual == "accept" or error == case["error"])
        results.append({"id": case["id"], "result": actual if actual == "accept" else "expected-rejection", "error": error})
    with tempfile.TemporaryDirectory(prefix="loki-manual-guide-") as temp:
        guide_root = Path(temp)
        guide_plan = build_initial_fixture(guide_root)
        catalog_path = guide_root / guide_plan / "builds/manual-qa/source-catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        require("GUIDE_ADVERSARIAL_FIXTURE_TOO_SMALL", len(catalog["sources"]) >= 2)
        changed_source = next(row for row in catalog["sources"] if row["source_kind"] == "changed-surface")
        require(
            "CHANGED_SOURCE_NOT_EXACT_TARGET_BYTES",
            changed_source["source_digest"] == bytes_digest((guide_root / changed_source["source_ref"]).read_bytes()),
        )
        require(
            "CHANGED_SOURCE_OBSERVABLE_PROVENANCE_MISSING",
            bool(changed_source["task_refs"])
            and bool(changed_source["acceptance_criterion_refs"] + changed_source["gate_refs"]),
        )
        results.append({"id": "changed-source-exact-target-byte-digest", "result": "accepted"})
        reused = deepcopy(catalog)
        source, target = reused["sources"][0], reused["sources"][1]
        for key in ("environment", "prerequisites", "initial_state", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit", "actions"):
            values = source[key] if isinstance(source[key], list) else [source[key]]
            rebound = [
                value.replace(source["source_ref"], target["source_ref"]).replace(
                    source["source_digest"], target["source_digest"]
                )
                for value in values
            ]
            target[key] = rebound if isinstance(source[key], list) else rebound[0]
        reused["catalog_digest"] = digest(reused, omit="catalog_digest")
        try:
            validate_catalog(reused)
        except ContractError as exc:
            require("GUIDE_REUSE_ERROR_MISMATCH", str(exc) in {"SOURCE_GUIDE_OBSERVABLE_FACT_UNBOUND", "CATALOG_MATERIALLY_REPEATED_GUIDE", "CATALOG_NEAR_DUPLICATE_GUIDE"})
        else:
            raise ContractError("GUIDE_REUSE_ACCEPTED")
        results.append({"id": "catalog-normalized-near-duplicate-guide", "result": "expected-rejection"})
        unrelated = deepcopy(catalog["sources"][0])
        unrelated["observable_fact_statements"][0] = "Nonsense unrelated to the persisted observable source fact."
        try:
            validate_source(unrelated)
        except ContractError as exc:
            require("GUIDE_UNRELATED_ERROR_MISMATCH", str(exc) == "SOURCE_GUIDE_OBSERVABLE_FACT_UNBOUND")
        else:
            raise ContractError("GUIDE_UNRELATED_SOURCE_ACCEPTED")
        results.append({"id": "source-guide-unrelated-fact", "result": "expected-rejection"})
        for field in GUIDE_FIELDS:
            nonsense = deepcopy(catalog["sources"][0])
            replacement = "Operate a generic interface and accept any visible response without consulting the persisted observable source fact."
            nonsense[field] = [replacement] if field == "actions" else replacement
            try:
                validate_source(nonsense)
            except ContractError as exc:
                require("GUIDE_FIELD_NONSENSE_ERROR_MISMATCH", str(exc) == f"SOURCE_GUIDE_FIELD_FACT_UNBOUND:{field}")
            else:
                raise ContractError(f"GUIDE_FIELD_NONSENSE_ACCEPTED:{field}")
            results.append({"id": f"source-guide-field-nonsense-{field}", "result": "expected-rejection"})
    transition_doc = json.loads((FIXTURE_ROOT / "transition-cases.json").read_text(encoding="utf-8"))
    semantic_classes: set[str] = set()
    for case in transition_doc["cases"]:
        closed("LANGUAGE_FIXTURE_SHAPE_INVALID", case, {"id", "statement", "signals", "rationale", "expected_status"})
        require("LANGUAGE_FIXTURE_STATEMENT_INVALID", nonempty(case["statement"]) and nonempty(case["rationale"]))
        closed("LANGUAGE_FIXTURE_SIGNALS_INVALID", case["signals"], ASSESSMENT_SIGNAL_KEYS)
        require("LANGUAGE_FIXTURE_EXPECTATION_INVALID", case["expected_status"] in {"created", "rejected"})
        semantic_classes.add(case["expected_status"])
        results.append({"id": case["id"], "result": "formal-audit-corpus-only"})
    require("LANGUAGE_FIXTURE_DIVERSITY_INVALID", semantic_classes == {"created", "rejected"})
    require("RUNTIME_SEMANTIC_CLASSIFIER_EXPOSED", "handle_attestation_intake" not in globals() and "assess_attestation_statement" not in globals())
    with tempfile.TemporaryDirectory(prefix="loki-manual-open-resolved-chain-") as temp:
        chain_root = Path(temp)
        chain_plan = build_initial_fixture(chain_root)
        chain_transaction_path = chain_root / chain_plan / "builds/manual-qa/transaction.json"
        initial_bytes = chain_transaction_path.read_bytes()
        initial_tx = validate_transaction(json.loads(initial_bytes))
        publish_issue_view(chain_root, chain_plan, kind="failure", resolved=False)
        open_bytes = chain_transaction_path.read_bytes()
        open_tx = validate_transaction(json.loads(open_bytes))
        require("OPEN_CHAIN_PREDECESSOR_INVALID", open_tx["predecessor_transaction_id"] == initial_tx["transaction_id"] and open_tx["predecessor_transaction_digest"] == bytes_digest(initial_bytes))
        precreate_external_resolution_fixture(chain_root, chain_plan)
        publish_issue_view(chain_root, chain_plan, kind="failure", resolved=True)
        resolved_tx = validate_transaction(json.loads(chain_transaction_path.read_bytes()))
        require("RESOLVED_CHAIN_PREDECESSOR_INVALID", resolved_tx["predecessor_transaction_id"] == open_tx["transaction_id"] and resolved_tx["predecessor_transaction_digest"] == bytes_digest(open_bytes) and resolved_tx["transaction_id"] != open_tx["transaction_id"])
        required_fresh_suffixes = ("/proposals/0.json", "/source-catalog.json", "/builds/manual-qa/dashboard.json", "/dashboard-presentation.json")
        require("RESOLVED_CHAIN_FRESH_VIEWS_MISSING", all(any(ref.endswith(suffix) for ref in resolved_tx["published_refs"]) for suffix in required_fresh_suffixes))
        validate_tree(chain_root, chain_plan)
        results.append({"id": "same-tree-open-resolved-fresh-rebuild", "result": "accepted"})
    with tempfile.TemporaryDirectory(prefix="loki-manual-reject-resume-") as temp:
        resume_root = Path(temp)
        resume_plan = build_initial_fixture(resume_root)
        rejected = _apply_pinned_assessment_fixture(
            resume_root,
            resume_plan,
            "Ambiguous fixture statement.",
            {"explicit_completed_all": False, "ambiguous": True, "negated": False, "future_intent": False, "partial_scope": False},
            "Pinned test setup marks the statement ambiguous.",
        )
        rejected_path = resume_root / rejected["transaction_ref"]
        rejected_one_bytes = rejected_path.read_bytes()
        rejected_one_tx = validate_transaction(json.loads(rejected_one_bytes))
        require("REJECT_BATCH_NOT_COMMITTED", rejected_one_tx["phase"] == "committed")
        validate_tree(resume_root, resume_plan)
        rejected_two = _apply_pinned_assessment_fixture(
            resume_root,
            resume_plan,
            "A second ambiguous fixture statement.",
            {"explicit_completed_all": False, "ambiguous": True, "negated": False, "future_intent": False, "partial_scope": False},
            "A second independent pinned review rejects ambiguity.",
        )
        rejected_two_bytes = rejected_path.read_bytes()
        rejected_two_tx = validate_transaction(json.loads(rejected_two_bytes))
        require("REJECT_CHAIN_PREDECESSOR_INVALID", rejected_two_tx["predecessor_transaction_id"] == rejected_one_tx["transaction_id"] and rejected_two_tx["predecessor_transaction_digest"] == bytes_digest(rejected_one_bytes) and rejected_two_tx["transaction_id"] != rejected_one_tx["transaction_id"])
        require("REJECT_CHAIN_CREATED_ATTESTATION", not (resume_root / resume_plan / "interaction/manual-qa" / rejected_two_tx["run_id"] / "attestation.json").exists())
        validate_tree(resume_root, resume_plan)
        accepted = _apply_pinned_assessment_fixture(
            resume_root,
            resume_plan,
            "Positive fixture statement.",
            {"explicit_completed_all": True, "ambiguous": False, "negated": False, "future_intent": False, "partial_scope": False},
            "Pinned test setup marks every applicable test complete.",
        )
        accepted_tx = validate_transaction(json.loads((resume_root / accepted["transaction_ref"]).read_text(encoding="utf-8")))
        require("REJECT_RESUME_ACCEPT_FAILED", accepted["status"] == "created" and accepted_tx["batch_kind"] == "terminal" and accepted_tx["predecessor_transaction_id"] == rejected_two["transaction_id"] and accepted_tx["predecessor_transaction_digest"] == bytes_digest(rejected_two_bytes))
        build_manual_fixture(resume_root, resume_plan, apply_acceptance=False)
        validate_tree(resume_root, resume_plan)
        final_tx = validate_transaction(json.loads(rejected_path.read_bytes()))
        final_intended = {ref: (resume_root / ref.partition("#")[0]).read_bytes() for ref in final_tx["target_refs"]}
        require("REJECT_CHAIN_TERMINAL_REPLAY_NOT_NOOP", resume_transaction(resume_root, rejected["transaction_ref"], final_intended)["status"] == "no-op")
        results.append({"id": "same-tree-reject-reject-accept-noop", "result": "accepted"})
    tree_doc = json.loads((FIXTURE_ROOT / "tree-cases.json").read_text(encoding="utf-8"))
    upstream = load_upstream()
    for case in tree_doc["cases"]:
        with tempfile.TemporaryDirectory(prefix="loki-manual-qa-") as temp:
            root = Path(temp)
            setup = case.get("setup", "completed")
            if setup == "completed": plan = build_manual_fixture(root)
            elif setup == "initial": plan = build_initial_fixture(root)
            elif setup == "paused": plan = build_initial_fixture(root, interaction_status="paused", result_status="in-progress")
            elif setup == "not-applicable": plan = build_initial_fixture(root, not_applicable_orders={2})
            elif setup in {"failure", "blocker", "resolved"}:
                plan = build_initial_fixture(root)
                if setup == "resolved":
                    precreate_external_resolution_fixture(root, plan)
                publish_issue_view(root, plan, kind="blocker" if setup == "blocker" else "failure", resolved=setup == "resolved")
            else: raise ContractError("TREE_FIXTURE_SETUP_INVALID")
            if case["mutation"] == "demand-bytes": (root / plan / "demanda.md").write_text("drifted demand\n", encoding="utf-8")
            elif case["mutation"] == "resolved-stale-presentation":
                ref = next((root / plan / "interaction/manual-qa").glob("*/dashboard-presentation.json"))
                ref.write_bytes(ref.read_bytes() + b"\n")
            elif case["mutation"] == "automatic-evidence-bytes": (root / plan / "evidence/terminal.json").write_text("{}\n", encoding="utf-8")
            elif case["mutation"] == "target-bytes": (root / "src/feature.txt").write_text("drifted target\n", encoding="utf-8")
            elif case["mutation"] == "validator-bytes":
                ref = root / plan / "evidence/task-1-validator.json"; doc = json.loads(ref.read_text()); doc["identity"] = "drifted-validator"; write_json(root, ref.relative_to(root).as_posix(), doc)
            elif case["mutation"] == "commit-drift":
                ref = root / plan / "result.json"; doc = json.loads(ref.read_text()); doc["next_action"] = "drift"; write_json(root, ref.relative_to(root).as_posix(), doc)
            elif case["mutation"] == "interaction-bytes":
                ref = next((root / plan / "interaction/manual-qa").glob("*/interaction.json")); doc = json.loads(ref.read_text()); doc["attestation_digest"] = "sha256:" + "0" * 64; write_json(root, ref.relative_to(root).as_posix(), doc)
            elif case["mutation"] == "review-decision-contradiction":
                run_dir = next((root / plan / "interaction/manual-qa").glob("*"))
                review_path = run_dir / "attestation-review.json"
                review = json.loads(review_path.read_text())
                review["signals"].update(explicit_completed_all=False, ambiguous=True)
                review["decision"] = "reject"
                review["review_digest"] = digest(review, omit="review_digest")
                write_json(root, review_path.relative_to(root).as_posix(), review)
            elif case["mutation"] in {"review-evidence-ad-hoc-json", "review-evidence-wrong-agent", "review-evidence-integrity-mismatch", "review-evidence-digest-drift"}:
                evidence_path = next((root / plan / "interaction/manual-qa").glob("*/agent-runs/manual-qa-attestation-auditor.xml"))
                if case["mutation"] == "review-evidence-ad-hoc-json":
                    evidence_path.write_text('{"status":"completed"}\n', encoding="utf-8")
                elif case["mutation"] == "review-evidence-wrong-agent":
                    evidence_path.write_text(evidence_path.read_text(encoding="utf-8").replace("manual-qa-attestation-auditor</agent_name>", "runtime-qa</agent_name>", 1), encoding="utf-8")
                elif case["mutation"] == "review-evidence-integrity-mismatch":
                    evidence_root = ET.fromstring(evidence_path.read_bytes())
                    evidence_root.find("./integrity/canonical_content_checksum").text = "sha256:" + "0" * 64
                    evidence_path.write_bytes(ET.tostring(evidence_root, encoding="utf-8", xml_declaration=True) + b"\n")
                else:
                    evidence_path.write_bytes(evidence_path.read_bytes() + b"\n")
            elif case["mutation"] == "illegal-transition":
                ref = next((root / plan / "interaction/manual-qa").glob("*/interaction.json")); doc = json.loads(ref.read_text()); doc["status"] = "issue-open"; doc["interaction_digest"] = digest(doc, omit="interaction_digest"); write_json(root, ref.relative_to(root).as_posix(), doc)
            elif case["mutation"] in {"transaction-target-omission", "transaction-target-reorder", "transaction-target-addition"} or (isinstance(case["mutation"], str) and case["mutation"].startswith("transaction-omit-")):
                tx_ref = root / plan / "builds/manual-qa/transaction.json"; tx = json.loads(tx_ref.read_text())
                aligned = ["target_refs", "before_digests", "intended_after_digests", "published_refs", "published_digests"]
                if case["mutation"] == "transaction-target-omission" or case["mutation"].startswith("transaction-omit-"):
                    suffix = case["mutation"].removeprefix("transaction-omit-")
                    patterns = {"proposal": "/proposals/", "catalog": "/source-catalog.json", "dashboard": "/builds/manual-qa/dashboard.json", "assessment": "/semantic-assessment.json", "interaction": "/interaction.json", "result": "/builds/manual-qa/result.json", "consistency": "/builds/manual-qa/consistency.json"}
                    remove_index = 0 if case["mutation"] == "transaction-target-omission" else next(index for index, ref in enumerate(tx["target_refs"]) if patterns[suffix] in ref)
                    for key in aligned: tx[key].pop(remove_index)
                elif case["mutation"] == "transaction-target-reorder":
                    for key in aligned: tx[key][0], tx[key][1] = tx[key][1], tx[key][0]
                else:
                    for key in ("target_refs", "published_refs"): tx[key].append(f"{plan}/unexpected.json")
                    for key in ("before_digests", "intended_after_digests", "published_digests"): tx[key].append("sha256:" + "9" * 64)
                tx["next_target_index"] = len(tx["published_refs"])
                bind_transaction_identity(tx)
                tx["transaction_digest"] = digest(tx, omit="transaction_digest"); write_json(root, tx_ref.relative_to(root).as_posix(), tx)
                result_ref = root / plan / "builds/manual-qa/result.json"; result = json.loads(result_ref.read_text()); result["transaction_id"] = tx["transaction_id"]; result["result_digest"] = digest(result, omit="result_digest"); write_json(root, result_ref.relative_to(root).as_posix(), result)
            elif case["mutation"] == "human-gate-not-applicable":
                catalog_ref = root / plan / "builds/manual-qa/source-catalog.json"; catalog = json.loads(catalog_ref.read_text()); source = next(row for row in catalog["sources"] if row["source_kind"] == "human-gate"); source.update(applicability="not-applicable", not_applicable_reason="incorrect waiver"); write_json(root, catalog_ref.relative_to(root).as_posix(), catalog)
            elif case["mutation"] == "changed-source-provenance-digest":
                catalog_ref = root / plan / "builds/manual-qa/source-catalog.json"
                catalog = json.loads(catalog_ref.read_text())
                source_index = next(index for index, row in enumerate(catalog["sources"]) if row["source_kind"] == "changed-surface")
                source = catalog["sources"][source_index]
                prior_digest = source["source_digest"]
                substituted_digest = "sha256:" + "9" * 64
                proposal_ref = root / source["runtime_qa_proposal_ref"]
                proposal = json.loads(proposal_ref.read_text())
                for key in ("environment", "prerequisites", "initial_state", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit"):
                    proposal[key] = proposal[key].replace(prior_digest, substituted_digest)
                proposal["actions"] = [item.replace(prior_digest, substituted_digest) for item in proposal["actions"]]
                proposal["candidate_digest"] = substituted_digest
                write_json(root, proposal_ref.relative_to(root).as_posix(), proposal)
                source["source_digest"] = substituted_digest
                source["runtime_qa_proposal_digest"] = bytes_digest(proposal_ref.read_bytes())
                for key in ("environment", "prerequisites", "initial_state", "expected_result", "success_signal", "failure_signal", "cleanup", "automation_limit"):
                    source[key] = source[key].replace(prior_digest, substituted_digest)
                source["actions"] = [item.replace(prior_digest, substituted_digest) for item in source["actions"]]
                catalog["candidate_digests"][source_index] = substituted_digest
                catalog["coverage_digest"] = digest(catalog_coverage_material(catalog))
                catalog["catalog_digest"] = digest(catalog, omit="catalog_digest")
                write_json(root, catalog_ref.relative_to(root).as_posix(), catalog)
            elif case["mutation"] == "partial-residue":
                tx_ref = root / plan / "builds/manual-qa/transaction.json"; tx = json.loads(tx_ref.read_text()); tx.update(phase="recovery-required", next_target_index=1, published_refs=tx["target_refs"][:1], published_digests=tx["intended_after_digests"][:1], residue_refs=tx["target_refs"][:1], residue_digests=tx["intended_after_digests"][:1]); tx["transaction_digest"] = digest(tx, omit="transaction_digest"); write_json(root, tx_ref.relative_to(root).as_posix(), tx)
                result_ref = root / plan / "builds/manual-qa/result.json"; result = json.loads(result_ref.read_text()); result["result_digest"] = digest(result, omit="result_digest"); write_json(root, result_ref.relative_to(root).as_posix(), result)
            elif case["mutation"] == "task-ac": upstream.mutate_fixture_markdown(root, f"{plan}/task-1.md", lambda doc: doc["task_contract"]["task_validation"]["acceptance_criteria"][0].update(statement="Changed criterion."))
            elif case["mutation"] == "handoff-v1": upstream.mutate_fixture_state(root, lambda state: state["manual_qa_handoff"].update(schema_version=1))
            try:
                if case["id"] == "real-tree-help-no-mutation":
                    help_result = handle_help(root, plan, "MQ-01")
                    require("HELP_BOUNDARY_STATUS_INVALID", help_result["status"] == "read-only-help" and help_result["bytes_before"] == help_result["bytes_after"])
                first = validate_tree(root, plan)
                second = validate_tree(root, plan)
                require("REPLAY_NOT_IDEMPOTENT", first["tree_digest"] == second["tree_digest"])
                accepted, error = True, None
            except (ContractError, ValueError) as exc:
                accepted, error = False, str(exc)
            require("TREE_FIXTURE_OUTCOME_MISMATCH", accepted is case["accept"])
            if not accepted and case["error"]:
                require(f"TREE_FIXTURE_ERROR_MISMATCH:{case['id']}:{case['error']}:{error}", error == case["error"])
            results.append({"id": case["id"], "result": "accepted" if accepted else "expected-rejection", "error": error})
    return {"schema_version": 1, "status": "passed", "fixture_files": list(FIXTURE_FILES), "cases_executed": len(results), "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--record", choices=sorted(VALIDATORS))
    parser.add_argument("--tree", metavar="PROJECT_ROOT")
    parser.add_argument("path", nargs="?")
    args = parser.parse_args()
    require("CLI_MODE_INVALID", sum((args.self_test, bool(args.record), bool(args.tree))) == 1)
    try:
        if args.self_test: output = self_test()
        elif args.record:
            require("CLI_PATH_REQUIRED", bool(args.path)); VALIDATORS[args.record](json.loads(Path(args.path).read_text(encoding="utf-8"))); output = {"schema_version": 1, "status": "passed", "record": args.record}
        else:
            require("CLI_PLAN_REQUIRED", nonempty(args.path)); output = validate_tree(Path(args.tree), args.path)
        print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    except (ContractError, OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True), file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
