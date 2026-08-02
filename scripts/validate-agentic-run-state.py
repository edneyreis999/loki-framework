#!/usr/bin/env python3
"""Validate canonical Loki agentic XML run state."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


RESOLVED_GATE_STATUSES = {"resolved", "answered", "accepted", "none", "not_applicable"}
NON_WRITER_MODES = {"", "none", "read-only", "readonly", "proposal", "report"}
KNOWLEDGE_CAPTURE_STATES = {
    "captured",
    "partial",
    "failed",
    "unsupported",
    "skipped-nonmaterial",
}
EVIDENCE_SCHEMAS = {"6"}
CURRENT_RUN_STATUSES = {"completed", "blocked"}
TERMINAL_RUN_STATUSES = CURRENT_RUN_STATUSES
REVIEW_FREQUENCIES = ("write_agent_handoff", "task", "fase", "plano")
REVIEW_TERMINAL_SCOPES = ("task", "fase", "plano")
REVIEW_PROVENANCE = {"explicit", "default", "propagated", "resumed"}
REVIEW_STATUSES = {
    "scheduled", "dispatched", "completed-clean", "completed-with-findings",
    "skipped-no-material-write", "skipped-agent-unavailable",
    "failed-consultive", "outcome-unknown",
}
REVIEW_DEGRADED = {"skipped-agent-unavailable", "failed-consultive", "outcome-unknown"}
REVIEW_RISK_BACKLOG = REVIEW_DEGRADED | {"completed-with-findings"}
IMPLEMENT_FEATURE_TERMINAL_STATUSES = {
    "running",
    "completed",
    "completed-with-limitations",
    "partial",
    "failed",
    "cancelled",
    "awaiting-manual-qa",
}
IMPLEMENTATION_HANDOFF_PRETERMINAL_STATUSES = {"scheduled", "dispatched"}
IMPLEMENTATION_HANDOFF_STATUSES = (
    IMPLEMENTATION_HANDOFF_PRETERMINAL_STATUSES | IMPLEMENT_FEATURE_TERMINAL_STATUSES
)
RAW_CLEAN_STATUSES = {"approved", "clean", "passed", "success", "no-findings"}
RAW_FINDING_STATUSES = {"blocked", "finding", "findings", "changes-requested"}
RAW_FAILURE_STATUSES = {"error", "failed", "failure", "timeout"}
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
CHECKPOINT_RE = re.compile(r"^review-checkpoint-v1:[0-9a-f]{64}$")
EXECUTION_SPAN_RE = re.compile(r"^execution-span-v1:[0-9a-f]{64}$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
LOKI_RUN_RE = re.compile(r"^loki-run-v2:[0-9a-f]{64}$")
LOKI_EXECUTION_RE = re.compile(r"^loki-execution-v2:[0-9a-f]{64}$")
MANUAL_QA_HANDOFF_LIST_KEYS = (
    "automatic_evidence_refs",
    "task_refs",
    "acceptance_criterion_refs",
    "gate_refs",
    "changed_target_refs",
)
MANUAL_QA_HANDOFF_KEYS = {
    "schema_version",
    "status",
    "run_id",
    "execution_id",
    "plan_directory",
    "manual_qa_result_ref",
    "manual_qa_attestation_ref",
    "reason",
}.union(MANUAL_QA_HANDOFF_LIST_KEYS)
MANUAL_QA_HANDOFF_STATUSES = {
    "manual-qa-not-evaluated",
    "ready-for-manual-qa",
    "manual-qa-not-required",
}
TERMINAL_RECONCILIATION_BY_IMPLEMENTATION_STATUS = {
    "scheduled": ("blocked", "manual-qa-not-evaluated"),
    "dispatched": ("blocked", "manual-qa-not-evaluated"),
    "running": ("blocked", "manual-qa-not-evaluated"),
    "partial": ("blocked", "manual-qa-not-evaluated"),
    "failed": ("blocked", "manual-qa-not-evaluated"),
    "cancelled": ("blocked", "manual-qa-not-evaluated"),
    "awaiting-manual-qa": ("completed", "ready-for-manual-qa"),
    "completed": ("completed", "manual-qa-not-required"),
    "completed-with-limitations": ("completed", "manual-qa-not-required"),
}


def text(element: ET.Element | None) -> str:
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def child_text(parent: ET.Element, path: str) -> str:
    return text(parent.find(path))


def non_empty_children(parent: ET.Element, path: str) -> list[str]:
    return [text(child) for child in parent.findall(path) if text(child)]


def parse_boolean(raw: str) -> bool | None:
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    return None


def canonical_digest(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def documented_implement_feature_terminal_statuses() -> set[str]:
    """Read the current public response enum used by the unified handoff."""
    response_contract = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "loki-implement-feature"
        / "references"
        / "response.md"
    )
    source = response_contract.read_text(encoding="utf-8")
    match = re.search(
        r"^## Terminal Status\s*$\n(?P<body>.*?)(?=^## )",
        source,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError("loki-implement-feature response lacks Terminal Status section")
    return set(re.findall(r"^- `([^`]+)`", match.group("body"), flags=re.MULTILINE))


def validate_coverage_path(value: str, label: str, failures: list[str]) -> None:
    parts = value.split("/")
    if (
        not value
        or value.startswith("/")
        or "\\" in value
        or any(part in {"", ".", ".."} for part in parts)
    ):
        failures.append(f"{label}: unsafe coverage path")


def require_exact_children(
    parent: ET.Element | None, expected: set[str], label: str, failures: list[str]
) -> None:
    if parent is None:
        failures.append(f"{label}: missing block")
        return
    tags = [child.tag for child in parent]
    if len(tags) != len(expected) or set(tags) != expected:
        failures.append(f"{label}: unexpected, missing or duplicate fields")


def validate_manual_qa_handoff(
    root: ET.Element,
    label: str,
    failures: list[str],
    *,
    expected_plan_directory: str = "",
) -> dict[str, object]:
    nodes = root.findall("manual_qa_handoff")
    if len(nodes) != 1:
        failures.append(f"{label}: exactly one manual_qa_handoff is required")
        return {}
    handoff = nodes[0]
    require_exact_children(
        handoff, MANUAL_QA_HANDOFF_KEYS, f"{label}: manual_qa_handoff", failures
    )
    if handoff.attrib:
        failures.append(f"{label}: manual_qa_handoff has unexpected attributes")
    for child in handoff:
        if child.tag in MANUAL_QA_HANDOFF_LIST_KEYS:
            if child.attrib or any(
                ref.tag != "ref" or ref.attrib or len(ref) or not text(ref)
                for ref in child
            ):
                failures.append(f"{label}: invalid {child.tag} shape")
        elif child.attrib or len(child):
            failures.append(f"{label}: manual_qa_handoff/{child.tag} must be scalar")

    schema_version = child_text(handoff, "schema_version")
    status = child_text(handoff, "status")
    run_id = child_text(handoff, "run_id")
    execution_id = child_text(handoff, "execution_id")
    plan_directory = child_text(handoff, "plan_directory")
    automatic_evidence_refs = non_empty_children(
        handoff, "automatic_evidence_refs/ref"
    )
    task_refs = non_empty_children(handoff, "task_refs/ref")
    acceptance_criterion_refs = non_empty_children(
        handoff, "acceptance_criterion_refs/ref"
    )
    gate_refs = non_empty_children(handoff, "gate_refs/ref")
    changed_target_refs = non_empty_children(handoff, "changed_target_refs/ref")
    result_ref = child_text(handoff, "manual_qa_result_ref")
    attestation_ref = child_text(handoff, "manual_qa_attestation_ref")
    reason = child_text(handoff, "reason")

    if schema_version != "2":
        failures.append(f"{label}: manual_qa_handoff requires schema_version 2")
    if status not in MANUAL_QA_HANDOFF_STATUSES:
        failures.append(f"{label}: invalid manual_qa_handoff status {status!r}")
    if not LOKI_RUN_RE.fullmatch(run_id):
        failures.append(f"{label}: invalid manual_qa_handoff run_id")
    if not LOKI_EXECUTION_RE.fullmatch(execution_id):
        failures.append(f"{label}: invalid manual_qa_handoff execution_id")
    validate_coverage_path(
        plan_directory, f"{label}: manual_qa_handoff plan_directory", failures
    )
    if expected_plan_directory and plan_directory != expected_plan_directory:
        failures.append(f"{label}: manual_qa_handoff plan_directory mismatch")
    ordered_refs = {
        "automatic_evidence_refs": automatic_evidence_refs,
        "task_refs": task_refs,
        "acceptance_criterion_refs": acceptance_criterion_refs,
        "gate_refs": gate_refs,
        "changed_target_refs": changed_target_refs,
    }
    for field, refs in ordered_refs.items():
        if len(refs) != len(set(refs)):
            failures.append(f"{label}: duplicate manual_qa_handoff {field}")
        for ref in refs:
            validate_coverage_path(
                ref, f"{label}: manual_qa_handoff {field}", failures
            )
    if result_ref != f"{plan_directory}/builds/manual-qa/result.json":
        failures.append(f"{label}: manual_qa_handoff result anchor mismatch")
    if attestation_ref != (
        f"{plan_directory}/interaction/manual-qa/{run_id}/attestation.json"
    ):
        failures.append(f"{label}: manual_qa_handoff attestation anchor mismatch")
    if status == "ready-for-manual-qa":
        if reason:
            failures.append(f"{label}: ready manual_qa_handoff reason must be null")
    elif not reason:
        failures.append(f"{label}: non-ready manual_qa_handoff reason is required")
    if status != "manual-qa-not-evaluated" and not automatic_evidence_refs:
        failures.append(f"{label}: terminal manual_qa_handoff requires evidence")

    return {
        "schema_version": schema_version,
        "status": status,
        "run_id": run_id,
        "execution_id": execution_id,
        "plan_directory": plan_directory,
        "automatic_evidence_refs": automatic_evidence_refs,
        "manual_qa_result_ref": result_ref,
        "manual_qa_attestation_ref": attestation_ref,
        "task_refs": task_refs,
        "acceptance_criterion_refs": acceptance_criterion_refs,
        "gate_refs": gate_refs,
        "changed_target_refs": changed_target_refs,
        "reason": reason or None,
    }


def validate_terminal_reconciliation(
    run_status: str,
    implementation_status: str,
    manual_qa_status: str,
    label: str,
    failures: list[str],
) -> None:
    expected = TERMINAL_RECONCILIATION_BY_IMPLEMENTATION_STATUS.get(
        implementation_status
    )
    if expected is None:
        return
    actual = (run_status, manual_qa_status)
    if actual != expected:
        failures.append(
            f"{label}: invalid terminal reconciliation for implementation status "
            f"{implementation_status!r}; expected parent/manual-QA {expected!r}, "
            f"got {actual!r}"
        )


def validate_node_shape(
    node: ET.Element | None,
    label: str,
    expected_attrs: set[str],
    expected_children: dict[str, tuple[int, int | None]],
    failures: list[str],
) -> None:
    if node is None:
        failures.append(f"{label}: missing node")
        return
    if not set(node.attrib).issubset(expected_attrs):
        failures.append(f"{label}: unexpected attributes")
    counts = {tag: 0 for tag in expected_children}
    for child in node:
        if child.tag not in counts:
            failures.append(f"{label}: unknown child {child.tag!r}")
        else:
            counts[child.tag] += 1
    for tag, (minimum, maximum) in expected_children.items():
        if counts[tag] < minimum or (maximum is not None and counts[tag] > maximum):
            failures.append(f"{label}: invalid multiplicity for {tag}")


def validate_child_attributes(
    parent: ET.Element | None, child_name: str, allowed: set[str], label: str, failures: list[str]
) -> None:
    if parent is None:
        return
    for child in parent.findall(child_name):
        if not set(child.attrib).issubset(allowed):
            failures.append(f"{label}/{child_name}: unexpected attributes")


def validate_wtr_leafs(root: ET.Element, label: str, failures: list[str]) -> None:
    """Reject attributes/children on scalar WTR elements."""
    allowed = {"checkpoint_ref": {"checkpoint_id"}, "reason": {"required_for"}}
    scalar_tags = {"path", "sha256", "handoff_id", "completion_ref", "evidence_ref", "name", "contract_version", "selection_configuration_digest", "requested_frequency", "provenance", "execution_scope", "tasks_md", "status", "policy_ref", "policy_digest", "effective_frequency", "terminal_scope", "selected_agent_name", "selection_reason", "execution_id", "boundary_type", "boundary_ref", "coverage_digest", "review_handoff_id", "review_agent_run_id", "review_agent_raw_status", "execution_status_effect", "risk_ref", "backlog_ref", "checkpoint_id", "finding_id", "summary", "agent_run_id", "required_for", "code", "next_action", "reason"}
    for node in root.iter():
        if node is not root and len(node) > 0:
            allowed_container_attrs = {"checkpoint": {"checkpoint_id"}, "finding": {"finding_id"}, "checkpoint_ref": {"checkpoint_id"}, "reason": {"required_for"}, "coverage_manifest": {"schema_version"}, "implementation_handoff": {"schema_version"}, "state_error": {"code"}}
            if not set(node.attrib).issubset(allowed_container_attrs.get(node.tag, set())):
                failures.append(f"{label}/{node.tag}: unexpected attributes")
        if node.tag in scalar_tags or len(node) == 0:
            if len(node) != 0:
                failures.append(f"{label}/{node.tag}: scalar must not contain children")
            if node.tag in allowed:
                if not set(node.attrib).issubset(allowed[node.tag]):
                    failures.append(f"{label}/{node.tag}: unexpected attributes")
                if node.tag == "reason" and node.get("required_for") is not None and node.get("required_for") != "skipped-no-material-write skipped-agent-unavailable failed-consultive outcome-unknown":
                    failures.append(f"{label}/{node.tag}: invalid required_for")
            elif node.attrib:
                failures.append(f"{label}/{node.tag}: unexpected attributes")

def validate_wtr_containers(root: ET.Element, label: str, failures: list[str]) -> None:
    shapes = {
        "covered_write_handoff_ids": {"handoff_id"},
        "risk_refs": {"risk_ref"},
        "backlog_refs": {"backlog_ref"},
    }
    for node in root.iter():
        if node.tag in shapes:
            if any(child.tag not in shapes[node.tag] for child in node):
                failures.append(f"{label}/{node.tag}: unknown child")
                if node.tag == "reason" and node.get("required_for") is not None:
                    required = set(node.get("required_for", "").split())
                    if node.get("required_for") != "skipped-no-material-write skipped-agent-unavailable failed-consultive outcome-unknown":
                        failures.append(f"{label}/{node.tag}: invalid required_for")
            elif node.attrib:
                failures.append(f"{label}/{node.tag}: unexpected attributes")


def validate_manifest_wtr_shape(review: ET.Element, label: str, failures: list[str]) -> None:
    validate_node_shape(review, label, {"schema_version"}, {
        "request": (1, 1), "implementation_handoff": (1, 1), "reconciled_policy": (1, 1),
        "checkpoints": (1, 1), "risks": (1, 1), "state_errors": (1, 1), "next_action": (1, 1)
    }, failures)
    validate_node_shape(review.find("checkpoints"), f"{label}/checkpoints", set(), {"checkpoint": (1, None)}, failures)
    for checkpoint in review.findall("checkpoints/checkpoint"):
        validate_node_shape(checkpoint, f"{label}/checkpoint", {"checkpoint_id"}, {
            "execution_id": (1, 1), "policy_digest": (1, 1), "boundary_type": (1, 1), "boundary_ref": (1, 1),
            "coverage_digest": (1, 1), "coverage_manifest": (1, 1), "covered_write_handoff_ids": (1, 1),
            "findings": (0, 1), "status": (1, 1), "review_handoff_id": (1, 1), "review_agent_run_id": (1, 1),
            "review_agent_raw_status": (1, 1), "evidence_ref": (1, 1), "risk_refs": (1, 1),
            "backlog_refs": (1, 1), "execution_status_effect": (1, 1), "reason": (1, 1)
        }, failures)
        coverage = checkpoint.find("coverage_manifest")
        validate_node_shape(coverage, f"{label}/coverage_manifest", {"schema_version"}, {"handoffs": (1, 1), "reviewer": (1, 1)}, failures)
        validate_node_shape(coverage.find("handoffs") if coverage is not None else None, f"{label}/coverage_manifest/handoffs", set(), {"handoff": (0, None)}, failures)
        for handoff in (coverage.findall("handoffs/handoff") if coverage is not None else []):
            validate_node_shape(handoff, f"{label}/coverage/handoff", set(), {"handoff_id": (1, 1), "completion_ref": (1, 1), "evidence_ref": (1, 1), "changed_files": (1, 1)}, failures)
            changed = handoff.find("changed_files")
            validate_node_shape(changed, f"{label}/coverage/changed_files", set(), {"file": (1, None)}, failures)
            for file_node in (changed.findall("file") if changed is not None else []):
                validate_node_shape(file_node, f"{label}/coverage/file", set(), {"path": (1, 1), "sha256": (1, 1)}, failures)
        validate_node_shape(coverage.find("reviewer") if coverage is not None else None, f"{label}/coverage/reviewer", set(), {"name": (1, 1), "contract_version": (1, 1), "selection_configuration_digest": (1, 1)}, failures)
    validate_wtr_leafs(review, label, failures)
    validate_wtr_containers(review, label, failures)


def validate_projection_wtr_shape(review: ET.Element, label: str, failures: list[str], digest: bool = False) -> None:
    if digest:
        validate_node_shape(review, label, {"schema_version"}, {"policy_ref": (1, 1), "policy_digest": (1, 1), "requested_frequency": (1, 1), "effective_frequency": (1, 1), "checkpoints": (1, 1), "findings": (1, 1), "execution_status_effect": (1, 1), "state_errors": (1, 1)}, failures)
        container = review.find("checkpoints")
        validate_node_shape(container, f"{label}/checkpoints", set(), {"checkpoint": (1, None)}, failures)
        validate_node_shape(review.find("findings"), f"{label}/findings", set(), {"finding": (0, None)}, failures)
        validate_node_shape(review.find("state_errors"), f"{label}/state_errors", set(), {"state_error": (0, None)}, failures)
        for error in review.findall("state_errors/state_error"):
            validate_node_shape(error, f"{label}/state_error", {"code"}, {"reason": (1, 1), "next_action": (1, 1)}, failures)
        for finding in review.findall("findings/finding"):
            # Digest findings use attributes for identity and six singleton children.
            if set(finding.attrib) != {"finding_id"}:
                failures.append(f"{label}/finding: unexpected attributes")
            validate_node_shape(finding, f"{label}/finding", {"finding_id"}, {"checkpoint_id": (1, 1), "review_handoff_id": (1, 1), "agent_run_id": (1, 1), "evidence_ref": (1, 1), "risk_ref": (1, 1), "backlog_ref": (1, 1)}, failures)
        for checkpoint in review.findall("checkpoints/checkpoint"):
            validate_node_shape(checkpoint, f"{label}/checkpoint", {"checkpoint_id"}, {"execution_id": (1, 1), "policy_digest": (1, 1), "status": (1, 1), "boundary_type": (1, 1), "boundary_ref": (1, 1), "coverage_digest": (1, 1), "review_handoff_id": (1, 1), "review_agent_run_id": (1, 1), "review_agent_raw_status": (1, 1), "evidence_ref": (1, 1), "risk_refs": (1, 1), "backlog_refs": (1, 1), "reason": (1, 1)}, failures)
        validate_wtr_leafs(review, label, failures)
        validate_wtr_containers(review, label, failures)
    else:
        validate_node_shape(review, label, {"schema_version"}, {"policy_ref": (1, 1), "policy_digest": (1, 1), "execution_id": (1, 1), "checkpoint_ref": (1, 1), "coverage_digest": (1, 1), "covered_write_handoff_ids": (1, 1), "review_lineage": (1, 1), "outcome": (1, 1), "findings": (1, 1), "risk_refs": (1, 1), "backlog_refs": (1, 1)}, failures)
        validate_node_shape(review.find("checkpoint_ref"), f"{label}/checkpoint_ref", {"checkpoint_id"}, {}, failures)
        validate_node_shape(review.find("findings"), f"{label}/findings", set(), {"finding": (0, None)}, failures)
        for finding in review.findall("findings/finding"):
            validate_node_shape(finding, f"{label}/finding", {"finding_id"}, {"summary": (1, 1), "risk_ref": (1, 1), "backlog_ref": (1, 1)}, failures)
        validate_wtr_leafs(review, label, failures)
        validate_wtr_containers(review, label, failures)


def checkpoint_identity(
    execution_id: str,
    policy_digest: str,
    boundary_type: str,
    boundary_ref: str,
    coverage_digest: str,
) -> str:
    suffix = canonical_digest(
        [execution_id, policy_digest, boundary_type, boundary_ref, coverage_digest]
    ).split(":", 1)[1]
    return "review-checkpoint-v1:" + suffix


def parse_coverage_manifest(
    checkpoint: ET.Element,
    label: str,
    selected_agent_name: str,
    failures: list[str],
) -> dict[str, object]:
    coverage = checkpoint.find("coverage_manifest")
    if coverage is None or coverage.get("schema_version") != "1" or set(coverage.attrib) != {"schema_version"}:
        failures.append(f"{label}: checkpoint missing coverage_manifest schema 1")
        return {"schema_version": 1, "handoffs": [], "reviewer": {}}
    handoffs: list[dict[str, object]] = []
    handoff_ids: list[str] = []
    for handoff in coverage.findall("handoffs/handoff"):
        if set(handoff.attrib) or {
            child.tag for child in handoff
        } != {"handoff_id", "completion_ref", "evidence_ref", "changed_files"}:
            failures.append(f"{label}: coverage handoff has extra or missing fields")
        handoff_id = child_text(handoff, "handoff_id")
        completion_ref = child_text(handoff, "completion_ref")
        evidence_ref = child_text(handoff, "evidence_ref")
        changed_files: list[dict[str, str]] = []
        for changed in handoff.findall("changed_files/file"):
            if set(changed.attrib) or {child.tag for child in changed} != {"path", "sha256"}:
                failures.append(f"{label}: coverage changed file has extra or missing fields")
            path = child_text(changed, "path")
            sha256 = child_text(changed, "sha256")
            validate_coverage_path(path, f"{label}: coverage changed file path", failures)
            if not path or not SHA256_RE.fullmatch(sha256):
                failures.append(f"{label}: invalid coverage changed file")
            changed_files.append({"path": path, "sha256": sha256})
        paths = [item["path"] for item in changed_files]
        if not handoff_id or not completion_ref or not evidence_ref or not changed_files:
            failures.append(f"{label}: incomplete material coverage handoff")
        if paths != sorted(set(paths)):
            failures.append(f"{label}: coverage changed paths must be sorted and unique")
        handoff_ids.append(handoff_id)
        handoffs.append(
            {
                "handoff_id": handoff_id,
                "completion_ref": completion_ref,
                "evidence_ref": evidence_ref,
                "changed_files": changed_files,
            }
        )
    if handoff_ids != sorted(set(handoff_ids)):
        failures.append(f"{label}: coverage handoff IDs must be sorted and unique")
    reviewer = coverage.find("reviewer")
    if reviewer is None or set(reviewer.attrib) or {
        child.tag for child in reviewer
    } != {"name", "contract_version", "selection_configuration_digest"}:
        failures.append(f"{label}: coverage reviewer has extra or missing fields")
    reviewer_name = child_text(reviewer, "name") if reviewer is not None else ""
    contract_version = child_text(reviewer, "contract_version") if reviewer is not None else ""
    selection_digest = (
        child_text(reviewer, "selection_configuration_digest") if reviewer is not None else ""
    )
    if reviewer_name != selected_agent_name:
        failures.append(f"{label}: coverage reviewer does not match selected agent")
    if not contract_version or not SHA256_RE.fullmatch(selection_digest):
        failures.append(f"{label}: invalid coverage reviewer contract/configuration")
    return {
        "schema_version": 1,
        "handoffs": handoffs,
        "reviewer": {
            "name": reviewer_name or None,
            "contract_version": contract_version,
            "selection_configuration_digest": selection_digest,
        },
    }


def validate_manifest_review(
    root: ET.Element, label: str, failures: list[str]
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    if root.get("schema_version") != "4":
        return {}, {}
    review = root.find("write_test_review")
    if review is None or review.get("schema_version") != "1":
        failures.append(f"{label}: schema 4 missing write_test_review schema 1")
        return {}, {}
    validate_manifest_wtr_shape(review, f"{label}: write_test_review", failures)
    require_exact_children(
        review.find("request"), {"requested_frequency", "provenance"}, f"{label}: request", failures
    )
    require_exact_children(
        review.find("implementation_handoff"),
        {
            "handoff_id", "command", "demand_ref", "demand_digest",
            "analysis_file", "analysis_digest", "plan_directory", "status",
            "execution_state_ref", "execution_state_digest", "result_ref",
            "dashboard_ref", "next_action",
        },
        f"{label}: implementation_handoff",
        failures,
    )
    require_exact_children(
        review.find("reconciled_policy"),
        {"policy_ref", "policy_digest", "effective_frequency", "terminal_scope", "selected_agent_name", "selection_reason"},
        f"{label}: reconciled_policy",
        failures,
    )
    for name in ("request", "implementation_handoff", "reconciled_policy", "risks", "state_errors", "next_action"):
        node = review.find(name)
        if node is not None and node.attrib and name != "implementation_handoff":
            failures.append(f"{label}/{name}: unexpected attributes")
    validate_node_shape(review.find("risks"), f"{label}/risks", set(), {"risk_ref": (0, None)}, failures)
    validate_child_attributes(review.find("risks"), "risk_ref", set(), f"{label}/risks", failures)
    validate_node_shape(review.find("state_errors"), f"{label}/state_errors", set(), {"state_error": (0, None)}, failures)
    for error in review.findall("state_errors/state_error"):
        validate_node_shape(error, f"{label}/state_error", {"code"}, {"reason": (1, 1), "next_action": (1, 1)}, failures)
    requested = child_text(review, "request/requested_frequency")
    provenance = child_text(review, "request/provenance")
    effective = child_text(review, "reconciled_policy/effective_frequency")
    terminal_scope = child_text(review, "reconciled_policy/terminal_scope")
    selected_agent_name = child_text(review, "reconciled_policy/selected_agent_name")
    policy_digest = child_text(review, "reconciled_policy/policy_digest")
    policy_ref = child_text(review, "reconciled_policy/policy_ref")
    if requested not in REVIEW_FREQUENCIES:
        failures.append(f"{label}: invalid requested review frequency {requested!r}")
    if provenance not in REVIEW_PROVENANCE:
        failures.append(f"{label}: invalid review provenance {provenance!r}")
    if provenance == "default" and requested != "task":
        failures.append(f"{label}: default review provenance requires requested task")
    if terminal_scope not in REVIEW_TERMINAL_SCOPES:
        failures.append(f"{label}: invalid review terminal scope {terminal_scope!r}")
    if requested in REVIEW_FREQUENCIES and terminal_scope in REVIEW_TERMINAL_SCOPES:
        expected = REVIEW_FREQUENCIES[
            min(REVIEW_FREQUENCIES.index(requested), REVIEW_FREQUENCIES.index(terminal_scope))
        ]
        if effective != expected:
            failures.append(f"{label}: effective review frequency must be {expected!r}")
    if not SHA256_RE.fullmatch(policy_digest):
        failures.append(f"{label}: invalid review policy digest")
    canonical_policy = {
        "schema_version": 1,
        "requested_frequency": requested,
        "effective_frequency": effective,
        "source": provenance,
        "terminal_scope": terminal_scope,
        "selected_agent": {
            "name": selected_agent_name or None,
            "selection_reason": child_text(review, "reconciled_policy/selection_reason"),
        },
    }
    if policy_digest != canonical_digest(canonical_policy):
        failures.append(f"{label}: review policy digest mismatch")
    implementation_handoffs = review.findall("implementation_handoff")
    if len(implementation_handoffs) != 1:
        failures.append(f"{label}: exactly one implementation_handoff is required")
    handoff = implementation_handoffs[0] if len(implementation_handoffs) == 1 else None
    if handoff is not None:
        if handoff.get("schema_version") != "1" or set(handoff.attrib) != {"schema_version"}:
            failures.append(f"{label}: implementation_handoff must use only schema_version=1")
        if child_text(handoff, "command") != "loki-implement-feature":
            failures.append(f"{label}: implementation_handoff command must be loki-implement-feature")
        for field in (
            "handoff_id", "demand_ref", "demand_digest", "analysis_file",
            "analysis_digest", "plan_directory", "status", "next_action",
        ):
            if not child_text(handoff, field):
                failures.append(f"{label}: implementation handoff missing {field}")
        if not child_text(handoff, "handoff_id").startswith("implementation-handoff-v1:"):
            failures.append(f"{label}: invalid implementation handoff identity")
        if not child_text(handoff, "analysis_file").endswith(".md"):
            failures.append(f"{label}: implementation analysis_file must be Markdown")
        for field in ("demand_digest", "analysis_digest"):
            if not SHA256_RE.fullmatch(child_text(handoff, field)):
                failures.append(f"{label}: invalid implementation {field}")
        handoff_status = child_text(handoff, "status")
        if handoff_status not in IMPLEMENTATION_HANDOFF_STATUSES:
            failures.append(f"{label}: invalid implementation handoff status {handoff_status!r}")
        returned_fields = (
            "execution_state_ref", "execution_state_digest", "result_ref", "dashboard_ref"
        )
        returned = [child_text(handoff, field) for field in returned_fields]
        if handoff_status in IMPLEMENTATION_HANDOFF_PRETERMINAL_STATUSES:
            if any(value not in {"", "null"} for value in returned):
                failures.append(f"{label}: pre-terminal implementation handoff must keep returned fields null")
        else:
            if any(value in {"", "null"} for value in returned):
                failures.append(f"{label}: terminal implementation handoff requires returned refs")
            if returned[1] not in {"", "null"} and not SHA256_RE.fullmatch(returned[1]):
                failures.append(f"{label}: invalid execution_state_digest")
    if not policy_ref:
        failures.append(f"{label}: reconciled review policy missing policy_ref")
    if not child_text(review, "reconciled_policy/selection_reason"):
        failures.append(f"{label}: reconciled review policy missing selection_reason")
    checkpoints: dict[str, dict[str, str]] = {}
    for checkpoint in review.findall("checkpoints/checkpoint"):
        require_exact_children(
            checkpoint,
            {
                "execution_id", "policy_digest", "boundary_type", "boundary_ref",
                "coverage_digest", "coverage_manifest", "covered_write_handoff_ids",
                "status", "review_handoff_id", "review_agent_run_id",
                "review_agent_raw_status", "evidence_ref", "risk_refs", "backlog_refs",
                "execution_status_effect", "reason",
            },
            f"{label}: checkpoint",
            failures,
        )
        checkpoint_id = checkpoint.get("checkpoint_id", "")
        execution_id = child_text(checkpoint, "execution_id")
        checkpoint_policy_digest = child_text(checkpoint, "policy_digest")
        status = child_text(checkpoint, "status")
        boundary_type = child_text(checkpoint, "boundary_type")
        coverage_digest = child_text(checkpoint, "coverage_digest")
        covered = non_empty_children(checkpoint, "covered_write_handoff_ids/handoff_id")
        reason = child_text(checkpoint, "reason")
        review_handoff_id = child_text(checkpoint, "review_handoff_id")
        checkpoint_risk_refs = non_empty_children(checkpoint, "risk_refs/risk_ref")
        checkpoint_backlog_refs = non_empty_children(checkpoint, "backlog_refs/backlog_ref")
        coverage_manifest = parse_coverage_manifest(
            checkpoint, label, selected_agent_name, failures
        )
        canonical_coverage_digest = canonical_digest(coverage_manifest)
        if not CHECKPOINT_RE.fullmatch(checkpoint_id) or checkpoint_id in checkpoints:
            failures.append(f"{label}: invalid or duplicate review checkpoint_id {checkpoint_id!r}")
        if boundary_type != effective or not child_text(checkpoint, "boundary_ref"):
            failures.append(f"{label}: review checkpoint boundary does not match effective frequency")
        if not SHA256_RE.fullmatch(coverage_digest):
            failures.append(f"{label}: invalid review coverage digest for {checkpoint_id}")
        if coverage_digest != canonical_coverage_digest:
            failures.append(f"{label}: review coverage digest mismatch for {checkpoint_id}")
        if not execution_id:
            failures.append(f"{label}: review checkpoint missing execution_id")
        if checkpoint_policy_digest != policy_digest:
            failures.append(f"{label}: checkpoint policy digest does not match active policy")
        expected_checkpoint_id = checkpoint_identity(
            execution_id,
            checkpoint_policy_digest,
            boundary_type,
            child_text(checkpoint, "boundary_ref"),
            coverage_digest,
        )
        if checkpoint_id != expected_checkpoint_id:
            failures.append(f"{label}: review checkpoint deterministic identity mismatch")
        coverage_handoff_ids = [
            str(item["handoff_id"])
            for item in coverage_manifest.get("handoffs", [])  # type: ignore[union-attr]
        ]
        if covered != coverage_handoff_ids:
            failures.append(f"{label}: covered write handoff IDs do not match coverage manifest")
        if covered != sorted(set(covered)):
            failures.append(f"{label}: covered write handoff IDs must be sorted and unique")
        if status not in REVIEW_STATUSES:
            failures.append(f"{label}: invalid review checkpoint status {status!r}")
        if status == "skipped-no-material-write":
            if covered or review_handoff_id:
                failures.append(f"{label}: no-material checkpoint must have zero coverage and dispatch")
        elif not covered:
            failures.append(f"{label}: review checkpoint {status!r} requires material coverage")
        if status in REVIEW_DEGRADED and not reason:
            failures.append(f"{label}: degraded review checkpoint requires reason")
        if checkpoint_risk_refs != sorted(set(checkpoint_risk_refs)):
            failures.append(f"{label}: checkpoint risk refs must be sorted and unique")
        if checkpoint_backlog_refs != sorted(set(checkpoint_backlog_refs)):
            failures.append(f"{label}: checkpoint backlog refs must be sorted and unique")
        if status in REVIEW_DEGRADED and (
            len(checkpoint_risk_refs) != 1 or len(checkpoint_backlog_refs) != 1
        ):
            failures.append(
                f"{label}: degraded checkpoint requires exactly one risk_ref and backlog_ref"
            )
        if status == "completed-with-findings" and (
            not checkpoint_risk_refs or not checkpoint_backlog_refs
        ):
            failures.append(
                f"{label}: completed-with-findings requires risk and backlog refs"
            )
        if status not in REVIEW_RISK_BACKLOG and (
            checkpoint_risk_refs or checkpoint_backlog_refs
        ):
            failures.append(
                f"{label}: {status!r} checkpoint must not contain risk/backlog refs"
            )
        if status in {"dispatched", "completed-clean", "completed-with-findings", "failed-consultive", "outcome-unknown"} and not review_handoff_id:
            failures.append(f"{label}: dispatched review status requires review_handoff_id")
        if status in {"dispatched", "completed-clean", "completed-with-findings", "failed-consultive", "outcome-unknown"} and not selected_agent_name:
            failures.append(f"{label}: dispatched review status requires selected reviewer")
        if review_handoff_id and CHECKPOINT_RE.fullmatch(checkpoint_id):
            expected_handoff = "review-handoff-v1:" + checkpoint_id.split(":", 1)[1]
            if review_handoff_id != expected_handoff:
                failures.append(f"{label}: nondeterministic review_handoff_id for {checkpoint_id}")
        if child_text(checkpoint, "execution_status_effect") != "none":
            failures.append(f"{label}: review execution_status_effect must be none")
        checkpoints[checkpoint_id] = {
            "status": status,
            "execution_id": execution_id,
            "policy_digest": checkpoint_policy_digest,
            "coverage_digest": coverage_digest,
            "boundary_type": boundary_type,
            "boundary_ref": child_text(checkpoint, "boundary_ref"),
            "covered_ids": "\n".join(covered),
            "review_handoff_id": review_handoff_id,
            "review_agent_run_id": child_text(checkpoint, "review_agent_run_id"),
            "review_agent_raw_status": child_text(checkpoint, "review_agent_raw_status"),
            "evidence_ref": child_text(checkpoint, "evidence_ref"),
            "risk_refs": "\n".join(checkpoint_risk_refs),
            "backlog_refs": "\n".join(checkpoint_backlog_refs),
            "reason": reason,
        }
        review_agent_run_id = child_text(checkpoint, "review_agent_run_id")
        raw_status = child_text(checkpoint, "review_agent_raw_status").lower()
        evidence_ref = child_text(checkpoint, "evidence_ref")
        if status == "scheduled" and (
            review_handoff_id or review_agent_run_id or raw_status or evidence_ref or reason
        ):
            failures.append(
                f"{label}: scheduled checkpoint must not contain dispatch or result lineage"
            )
        if status == "dispatched" and (raw_status or evidence_ref or reason):
            failures.append(
                f"{label}: dispatched checkpoint must not contain terminal result fields"
            )
        if status == "skipped-no-material-write":
            if not reason or review_agent_run_id or raw_status or evidence_ref:
                failures.append(f"{label}: no-material checkpoint requires reason and zero reviewer lineage")
        if status == "skipped-agent-unavailable" and (
            review_handoff_id or review_agent_run_id or raw_status or evidence_ref
        ):
            failures.append(f"{label}: unavailable checkpoint must not contain dispatch lineage")
        if status == "skipped-agent-unavailable" and selected_agent_name:
            failures.append(f"{label}: unavailable checkpoint requires null selected reviewer")
        if status in {"completed-clean", "completed-with-findings", "failed-consultive"} and not evidence_ref:
            failures.append(f"{label}: terminal reviewer result requires evidence_ref")
        if status in {"completed-clean", "completed-with-findings"} and reason:
            failures.append(f"{label}: completed reviewer result requires null reason")
        expected_status_for_raw = None
        if raw_status in RAW_CLEAN_STATUSES:
            expected_status_for_raw = "completed-clean"
        elif raw_status in RAW_FINDING_STATUSES:
            expected_status_for_raw = "completed-with-findings"
        elif raw_status in RAW_FAILURE_STATUSES:
            expected_status_for_raw = "failed-consultive"
        if expected_status_for_raw and status != expected_status_for_raw:
            failures.append(
                f"{label}: raw reviewer status {raw_status!r} requires {expected_status_for_raw}"
            )
        if (
            status in {"completed-clean", "completed-with-findings", "failed-consultive"}
            and raw_status not in RAW_CLEAN_STATUSES | RAW_FINDING_STATUSES | RAW_FAILURE_STATUSES
        ):
            failures.append(f"{label}: unknown raw reviewer status cannot map to {status}")
        if status in {"completed-clean", "completed-with-findings", "failed-consultive"} and not raw_status:
            failures.append(f"{label}: terminal reviewer result requires raw status")
    risk_refs = non_empty_children(review, "risks/risk_ref")
    if risk_refs != sorted(set(risk_refs)):
        failures.append(f"{label}: review risk refs must be sorted and unique")
    checkpoint_risk_union = sorted({
        risk_ref
        for record in checkpoints.values()
        for risk_ref in record["risk_refs"].splitlines()
    })
    if risk_refs != checkpoint_risk_union:
        failures.append(f"{label}: global review risks must equal checkpoint risk refs")
    all_checkpoint_backlog_refs = [
        backlog_ref
        for record in checkpoints.values()
        for backlog_ref in record["backlog_refs"].splitlines()
    ]
    if len(all_checkpoint_backlog_refs) != len(set(all_checkpoint_backlog_refs)):
        failures.append(f"{label}: checkpoint backlog refs must be globally unique")
    for state_error in review.findall("state_errors/state_error"):
        code = state_error.get("code", "")
        failures.append(f"{label}: unresolved review state error {code or '<missing>'}")
    if not child_text(review, "next_action"):
        failures.append(f"{label}: review next_action is required")
    return {
        "policy_digest": policy_digest,
        "policy_ref": policy_ref,
        "requested": requested,
        "effective": effective,
        "risk_refs": "\n".join(risk_refs),
    }, checkpoints


def validate_report_review(
    path: Path,
    root: ET.Element,
    review_meta: dict[str, str],
    checkpoints: dict[str, dict[str, str]],
    failures: list[str],
) -> dict[str, dict[str, str]]:
    if root.get("schema_version") != "6":
        return {}
    review = root.find("write_test_review")
    if review is None or review.get("schema_version") != "1":
        failures.append(f"{path}: schema 6 missing write_test_review schema 1")
        return {}
    validate_projection_wtr_shape(review, f"{path}: write_test_review", failures)
    require_exact_children(
        review,
        {"policy_ref", "policy_digest", "execution_id", "checkpoint_ref", "coverage_digest", "covered_write_handoff_ids", "review_lineage", "outcome", "findings", "risk_refs", "backlog_refs"},
        f"{path}: write_test_review",
        failures,
    )
    require_exact_children(
        review.find("review_lineage"),
        {"review_handoff_id", "review_agent_run_id", "evidence_ref"},
        f"{path}: review_lineage",
        failures,
    )
    require_exact_children(
        review.find("outcome"),
        {"status", "review_agent_raw_status", "execution_status_effect", "reason"},
        f"{path}: outcome",
        failures,
    )
    if child_text(review, "policy_ref") != review_meta.get("policy_ref", ""):
        failures.append(f"{path}: review policy_ref does not match manifest")
    if child_text(review, "policy_digest") != review_meta.get("policy_digest", ""):
        failures.append(f"{path}: review policy digest does not match manifest")
    checkpoint_ref = review.find("checkpoint_ref")
    checkpoint_id = checkpoint_ref.get("checkpoint_id", "") if checkpoint_ref is not None else ""
    canonical = checkpoints.get(checkpoint_id)
    if canonical is None:
        failures.append(f"{path}: orphan review checkpoint reference {checkpoint_id!r}")
    else:
        if checkpoint_ref is None or not text(checkpoint_ref):
            failures.append(f"{path}: review checkpoint_ref locator is empty")
        comparisons = {
            "execution_id": child_text(review, "execution_id"),
            "coverage_digest": child_text(review, "coverage_digest"),
            "status": child_text(review, "outcome/status"),
            "review_handoff_id": child_text(review, "review_lineage/review_handoff_id"),
            "review_agent_run_id": child_text(review, "review_lineage/review_agent_run_id"),
            "review_agent_raw_status": child_text(review, "outcome/review_agent_raw_status"),
            "evidence_ref": child_text(review, "review_lineage/evidence_ref"),
            "reason": child_text(review, "outcome/reason"),
        }
        for field, value in comparisons.items():
            if value != canonical[field]:
                failures.append(f"{path}: review {field} does not match manifest checkpoint")
        report_covered = non_empty_children(review, "covered_write_handoff_ids/handoff_id")
        if "\n".join(report_covered) != canonical["covered_ids"]:
            failures.append(f"{path}: covered write handoff IDs do not match manifest checkpoint")
        report_risk_refs = non_empty_children(review, "risk_refs/risk_ref")
        report_backlog_refs = non_empty_children(review, "backlog_refs/backlog_ref")
        if "\n".join(report_risk_refs) != canonical["risk_refs"]:
            failures.append(f"{path}: review risk refs do not match manifest checkpoint")
        if "\n".join(report_backlog_refs) != canonical["backlog_refs"]:
            failures.append(f"{path}: review backlog refs do not match manifest checkpoint")
    if child_text(review, "outcome/execution_status_effect") != "none":
        failures.append(f"{path}: consultive review altered execution status")
    outcome_status = child_text(review, "outcome/status")
    raw_status = child_text(review, "outcome/review_agent_raw_status").lower()
    findings_map: dict[str, dict[str, str]] = {}
    finding_ids: set[str] = set()
    for finding in review.findall("findings/finding"):
        finding_id = finding.get("finding_id", "")
        risk_ref = child_text(finding, "risk_ref")
        backlog_ref = child_text(finding, "backlog_ref")
        if not finding_id or finding_id in finding_ids:
            failures.append(f"{path}: missing or duplicate review finding_id {finding_id!r}")
        finding_ids.add(finding_id)
        if not child_text(finding, "summary") or not risk_ref or not backlog_ref:
            failures.append(f"{path}: review finding missing risk/backlog lineage")
        if canonical is not None and (
            risk_ref not in canonical["risk_refs"].splitlines()
            or backlog_ref not in canonical["backlog_refs"].splitlines()
        ):
            failures.append(f"{path}: review finding refs absent from manifest checkpoint")
        if finding_id:
            findings_map[finding_id] = {
                "checkpoint_id": checkpoint_id,
                "review_handoff_id": child_text(review, "review_lineage/review_handoff_id"),
                "agent_run_id": child_text(review, "review_lineage/review_agent_run_id"),
                "evidence_ref": child_text(review, "review_lineage/evidence_ref"),
                "risk_ref": risk_ref,
                "backlog_ref": backlog_ref,
            }
    if finding_ids and outcome_status != "completed-with-findings":
        failures.append(f"{path}: findings require completed-with-findings outcome")
    if outcome_status == "completed-with-findings" and canonical is not None:
        finding_risks = sorted({record["risk_ref"] for record in findings_map.values()})
        finding_backlogs = sorted({record["backlog_ref"] for record in findings_map.values()})
        if finding_risks != canonical["risk_refs"].splitlines():
            failures.append(f"{path}: findings do not cover canonical checkpoint risks")
        if finding_backlogs != canonical["backlog_refs"].splitlines():
            failures.append(f"{path}: findings do not cover canonical checkpoint backlog refs")
    expected_status_for_raw = None
    if raw_status in RAW_CLEAN_STATUSES:
        expected_status_for_raw = "completed-clean"
    elif raw_status in RAW_FINDING_STATUSES:
        expected_status_for_raw = "completed-with-findings"
    elif raw_status in RAW_FAILURE_STATUSES:
        expected_status_for_raw = "failed-consultive"
    if expected_status_for_raw and outcome_status != expected_status_for_raw:
        failures.append(
            f"{path}: raw reviewer status {raw_status!r} requires {expected_status_for_raw}"
        )
    if outcome_status == "completed-with-findings" and not finding_ids:
        failures.append(f"{path}: completed-with-findings requires at least one finding")
    return findings_map


def knowledge_record(
    element: ET.Element,
    label: str,
    failures: list[str],
    *,
    run_id: str = "",
    agent_run_id: str = "",
    handoff_id: str = "",
) -> dict[str, str | bool | None]:
    record: dict[str, str | bool | None] = {
        "capture_id": child_text(element, "capture_id"),
        "run_id": child_text(element, "run_id") or run_id,
        "agent_run_id": child_text(element, "agent_run_id") or agent_run_id,
        "handoff_id": child_text(element, "handoff_id") or handoff_id,
        "material": parse_boolean(child_text(element, "material")),
        "target_entry": child_text(element, "target_entry"),
        "state": child_text(element, "state"),
        "reason": child_text(element, "reason"),
        "minimum_next_path": child_text(element, "minimum_next_path"),
    }
    for field in ("capture_id", "run_id", "agent_run_id", "handoff_id", "target_entry"):
        if not record[field]:
            failures.append(f"{label}: knowledge capture missing {field}")
    if record["material"] is None:
        failures.append(f"{label}: knowledge material must be true or false")
    if record["state"] not in KNOWLEDGE_CAPTURE_STATES:
        failures.append(f"{label}: invalid execution knowledge state {record['state']!r}")
    if record["state"] == "skipped-nonmaterial" and record["material"] is not False:
        failures.append(f"{label}: skipped-nonmaterial requires material=false")
    if record["state"] != "captured" and (
        not record["reason"] or not record["minimum_next_path"]
    ):
        failures.append(f"{label}: degraded knowledge state requires reason and minimum_next_path")
    return record


def validate_knowledge_entry_file(path: Path) -> list[str]:
    validator_path = Path(__file__).with_name("validate-execution-knowledge.py")
    spec = importlib.util.spec_from_file_location("loki_execution_knowledge_validator", validator_path)
    if spec is None or spec.loader is None:
        return [f"{path}: execution-knowledge validator cannot be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate(path)


def parse_xml_file(path: Path) -> ET.Element:
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"{path}: XML parse error: {exc}") from exc


def parse_all_xml(run_dir: Path) -> dict[Path, ET.Element]:
    xml_paths = sorted(run_dir.rglob("*.xml"))
    if not xml_paths:
        raise ValueError(f"{run_dir}: no XML state files found")
    return {path: parse_xml_file(path) for path in xml_paths}


def validate_selected_agents(root: ET.Element, label: str, failures: list[str]) -> None:
    for selected in root.findall(".//selected_agent"):
        name = selected.attrib.get("name", child_text(selected, "agent_name")) or "<unnamed>"
        if not child_text(selected, "selection_reason"):
            failures.append(f"{label}: selected agent {name} missing selection_reason")


def validate_decision_gates(root: ET.Element, label: str, failures: list[str]) -> None:
    for gate in root.findall(".//decision_gate"):
        category = child_text(gate, "category") or gate.attrib.get("category", "")
        status = (child_text(gate, "status") or gate.attrib.get("status", "")).lower()
        if category == "must_ask_now" and status not in RESOLVED_GATE_STATUSES:
            gate_id = gate.attrib.get("id", child_text(gate, "id")) or "<missing-id>"
            failures.append(f"{label}: unresolved must_ask_now gate {gate_id}")


def validate_manifest_handoffs(root: ET.Element, failures: list[str]) -> dict[str, str]:
    seen_agent_runs: set[str] = set()
    seen_handoffs: set[str] = set()
    parents: dict[str, str] = {}
    for handoff in root.findall("handoffs/handoff"):
        agent_run_id = child_text(handoff, "agent_run_id")
        handoff_id = child_text(handoff, "handoff_id")
        if not agent_run_id:
            failures.append("agentic-run-manifest.xml: handoff missing agent_run_id")
        elif agent_run_id in seen_agent_runs:
            failures.append(
                f"agentic-run-manifest.xml: duplicate handoff agent_run_id {agent_run_id}"
            )
        else:
            seen_agent_runs.add(agent_run_id)

        if not handoff_id:
            failures.append("agentic-run-manifest.xml: handoff missing handoff_id")
        elif handoff_id in seen_handoffs:
            failures.append(
                f"agentic-run-manifest.xml: duplicate handoff_id {handoff_id}"
            )
        else:
            seen_handoffs.add(handoff_id)
        evidence_id = child_text(handoff, "evidence_id")
        evidence_path = child_text(handoff, "evidence_manifest_path")
        if not evidence_id or not evidence_path:
            failures.append("agentic-run-manifest.xml: canonical handoff missing evidence lineage")
        parent = child_text(handoff, "depends_on_handoff_id")
        if parent and handoff_id:
            parents[handoff_id] = parent
    for handoff_id in parents:
        visited: set[str] = set()
        current = handoff_id
        while current in parents:
            if current in visited:
                failures.append(f"agentic-run-manifest.xml: cyclic handoff lineage at {current}")
                break
            visited.add(current)
            current = parents[current]
    return {
        child_text(h, "handoff_id"): child_text(h, "agent_run_id")
        for h in root.findall("handoffs/handoff")
    }


def validate_report_v6_observability(
    path: Path, root: ET.Element, failures: list[str]
) -> None:
    """Validate current report-v6 timing, usage and correlation blocks."""
    timing = root.find("timing")
    require_exact_children(
        timing,
        {"span_id", "parent_span_id", "started_at_utc", "ended_at_utc", "monotonic_duration_ms", "clock_provenance", "clock_degradation_reason"},
        f"{path}: timing",
        failures,
    )
    span_id = child_text(root, "timing/span_id")
    if not EXECUTION_SPAN_RE.fullmatch(span_id):
        failures.append(f"{path}: invalid timing span_id")
    parent_span = child_text(root, "timing/parent_span_id")
    if parent_span not in {"", "null"} and not EXECUTION_SPAN_RE.fullmatch(parent_span):
        failures.append(f"{path}: invalid timing parent_span_id")
    clock = child_text(root, "timing/clock_provenance")
    if clock not in {"observed", "partial", "unavailable"}:
        failures.append(f"{path}: invalid timing clock provenance")
    duration = child_text(root, "timing/monotonic_duration_ms")
    if duration not in {"", "null"}:
        try:
            if int(duration) < 0:
                raise ValueError
        except ValueError:
            failures.append(f"{path}: invalid monotonic duration")
    elif not child_text(root, "timing/clock_degradation_reason"):
        failures.append(f"{path}: unavailable duration requires clock reason")

    usage = root.find("usage")
    require_exact_children(
        usage,
        {"metrics_ref", "metrics_digest", "metrics_status", "span_id", "usage_status", "exact_source", "estimate_method", "unavailable_reason"},
        f"{path}: usage",
        failures,
    )
    if not child_text(root, "usage/metrics_ref") or not SHA256_RE.fullmatch(child_text(root, "usage/metrics_digest")):
        failures.append(f"{path}: usage metrics ref/digest invalid")
    if child_text(root, "usage/metrics_status") not in {"complete", "partial", "unavailable"}:
        failures.append(f"{path}: invalid usage metrics status")
    if child_text(root, "usage/span_id") != span_id:
        failures.append(f"{path}: usage span does not match timing span")
    usage_status = child_text(root, "usage/usage_status")
    exact_source = child_text(root, "usage/exact_source")
    estimate_method = child_text(root, "usage/estimate_method")
    unavailable_reason = child_text(root, "usage/unavailable_reason")
    if usage_status == "exact":
        if not exact_source or estimate_method not in {"", "null"} or unavailable_reason not in {"", "null"}:
            failures.append(f"{path}: exact usage provenance is mixed or missing")
    elif usage_status == "estimated":
        if estimate_method != "utf8-byte-estimate-v1" or exact_source not in {"", "null"} or unavailable_reason not in {"", "null"}:
            failures.append(f"{path}: estimated usage provenance is mixed or invalid")
    elif usage_status == "unavailable":
        if exact_source not in {"", "null"} or estimate_method not in {"", "null"} or not unavailable_reason:
            failures.append(f"{path}: unavailable usage requires an unmixed reason")
    else:
        failures.append(f"{path}: invalid usage status")

    replay = root.find("replay_validator_correlation")
    require_exact_children(
        replay,
        {"iteration", "replay", "replay_cause", "cause_span_id", "validator_span_id", "validator_command", "validator_version", "validator_input_digest", "validator_policy_digest", "execution_mode", "would_reuse"},
        f"{path}: replay_validator_correlation",
        failures,
    )
    try:
        if int(child_text(root, "replay_validator_correlation/iteration")) < 0:
            raise ValueError
    except ValueError:
        failures.append(f"{path}: invalid replay iteration")
    replay_value = child_text(root, "replay_validator_correlation/replay")
    if replay_value not in {"true", "false"}:
        failures.append(f"{path}: replay must be true or false")
    if replay_value == "true" and (
        not child_text(root, "replay_validator_correlation/replay_cause")
        or not EXECUTION_SPAN_RE.fullmatch(child_text(root, "replay_validator_correlation/cause_span_id"))
    ):
        failures.append(f"{path}: replay requires cause and typed cause span")
    mode = child_text(root, "replay_validator_correlation/execution_mode")
    if mode not in {"executed", "referenced", "not-applicable"}:
        failures.append(f"{path}: invalid validator execution mode")
    if child_text(root, "replay_validator_correlation/would_reuse") not in {"true", "false", "not-applicable"}:
        failures.append(f"{path}: would_reuse is observation-only true/false/not-applicable")

    materiality = root.find("materiality_precheck_correlation")
    require_exact_children(
        materiality,
        {"profile_ref", "profile_digest", "materiality_ref", "materiality_digest", "status", "auditor_dispatch"},
        f"{path}: materiality_precheck_correlation",
        failures,
    )
    materiality_status = child_text(root, "materiality_precheck_correlation/status")
    auditor_dispatch = child_text(root, "materiality_precheck_correlation/auditor_dispatch")
    if (materiality_status, auditor_dispatch) not in {("valid", "permitted"), ("invalid", "blocked"), ("not-applicable", "not-applicable")}:
        failures.append(f"{path}: invalid materiality-to-Auditor gate")
    if materiality_status in {"valid", "invalid"}:
        for field in ("profile_ref", "materiality_ref"):
            if not child_text(root, f"materiality_precheck_correlation/{field}"):
                failures.append(f"{path}: materiality precheck missing {field}")
        for field in ("profile_digest", "materiality_digest"):
            if not SHA256_RE.fullmatch(child_text(root, f"materiality_precheck_correlation/{field}")):
                failures.append(f"{path}: materiality precheck invalid {field}")
    elif any(child_text(root, f"materiality_precheck_correlation/{field}") not in {"", "null"} for field in ("profile_ref", "profile_digest", "materiality_ref", "materiality_digest")):
        failures.append(f"{path}: not-applicable materiality correlation must not invent refs")

    probe = root.find("liveness_probe")
    require_exact_children(
        probe,
        {"required_before_silence_stop", "trigger", "observed_at_utc", "adapter", "source", "outcome", "reason", "silence_stop_permitted"},
        f"{path}: liveness_probe",
        failures,
    )
    required = child_text(root, "liveness_probe/required_before_silence_stop")
    trigger = child_text(root, "liveness_probe/trigger")
    outcome = child_text(root, "liveness_probe/outcome")
    permitted = child_text(root, "liveness_probe/silence_stop_permitted")
    if required not in {"true", "false"}:
        failures.append(f"{path}: liveness required flag must be boolean")
    if trigger == "silence-stop":
        if required != "true":
            failures.append(f"{path}: silence-stop trigger requires a recorded liveness probe")
        if outcome not in {"running", "progress", "terminal", "unsupported", "unavailable"}:
            failures.append(f"{path}: required silence probe missing observed outcome")
        observed = child_text(root, "liveness_probe/observed_at_utc")
        if not UTC_RE.fullmatch(observed) or not child_text(root, "liveness_probe/adapter") or child_text(root, "liveness_probe/source") in {"", "null"}:
            failures.append(f"{path}: required silence probe missing UTC timestamp/adapter/source")
        if outcome in {"running", "progress"} and permitted != "false":
            failures.append(f"{path}: running/progress forbids silence stop")
        if outcome in {"unsupported", "unavailable"} and child_text(root, "liveness_probe/reason") in {"", "null"}:
            failures.append(f"{path}: degraded liveness probe requires reason")
        if outcome in {"terminal", "unsupported", "unavailable"} and permitted not in {"true", "false"}:
            failures.append(f"{path}: policy stop decision requires a recorded probe result")
    elif trigger == "explicit-user-cancellation":
        if required != "false" or outcome != "not-required" or permitted != "not-applicable":
            failures.append(f"{path}: explicit cancellation must remain separate from silence probe")
    elif trigger == "none":
        if required != "false" or outcome != "not-required" or permitted != "not-applicable":
            failures.append(f"{path}: no silence candidate requires not-required probe")
    else:
        failures.append(f"{path}: invalid liveness trigger")
    if any(node.tag in {"token_budget", "cost_budget", "automatic_cost_stop"} for node in root.iter()):
        failures.append(f"{path}: report metrics must not define budgets or automatic cost stops")


def validate_report(
    path: Path,
    root: ET.Element,
    failures: list[str],
    review_meta: dict[str, str],
    review_checkpoints: dict[str, dict[str, str]],
) -> tuple[str, str, list[str], dict[str, str | bool | None] | None, dict[str, dict[str, str]]]:
    agent_run_id = child_text(root, "identity/agent_run_id")
    handoff_id = child_text(root, "identity/handoff_id")
    owner = child_text(root, "identity/owner")
    group_id = child_text(root, "identity/parallel_group_id")
    write_mode = child_text(root, "write_contract/write_mode").lower()
    target_files = non_empty_children(root, "write_contract/target_files/target_file")
    allowed_writes = non_empty_children(root, "write_contract/allowed_writes/allowed_write")
    validators = root.findall("validators/validator")
    gates = root.findall("gates/gate")

    if not agent_run_id:
        failures.append(f"{path}: missing identity/agent_run_id")
    if not handoff_id:
        failures.append(f"{path}: missing identity/handoff_id")
    if not child_text(root, "selection/selection_reason"):
        failures.append(f"{path}: missing selection/selection_reason")
    schema_version = root.get("schema_version", "")
    if schema_version in EVIDENCE_SCHEMAS:
        for field in ("evidence_manifest_path", "evidence_status", "capture_trigger", "capture_target"):
            if not child_text(root, f"evidence/{field}"):
                failures.append(f"{path}: schema {schema_version} missing evidence/{field}")
    if schema_version == "6":
        knowledge = root.find("execution_knowledge")
        if knowledge is None:
            failures.append(f"{path}: schema {schema_version} missing execution_knowledge")
            knowledge_record_value = None
        else:
            knowledge_record_value = knowledge_record(
                knowledge,
                str(path),
                failures,
                run_id=child_text(root, "identity/run_id"),
                agent_run_id=agent_run_id,
                handoff_id=handoff_id,
            )
    else:
        knowledge_record_value = None
    if root.find("freshness_signature") is None:
        failures.append(f"{path}: missing freshness_signature")
    if schema_version == "6":
        validate_report_v6_observability(path, root, failures)

    if write_mode not in NON_WRITER_MODES:
        if not owner:
            failures.append(f"{path}: writer missing identity/owner")
        if not target_files:
            failures.append(f"{path}: writer missing target_files")
        if not allowed_writes:
            failures.append(f"{path}: writer missing allowed_writes")
        if not validators:
            failures.append(f"{path}: writer missing validators")
        if not gates:
            failures.append(f"{path}: writer missing gates")

    completion = root.find("completion")
    if completion is None:
        failures.append(f"{path}: missing completion")
    else:
        if not child_text(completion, "status"):
            failures.append(f"{path}: completion missing status")
        if not child_text(completion, "report_path"):
            failures.append(f"{path}: completion missing report_path")
        if not non_empty_children(completion, "evidence/item"):
            failures.append(f"{path}: completion missing evidence item")

    review_findings = validate_report_review(
        path, root, review_meta, review_checkpoints, failures
    )
    return agent_run_id, group_id, target_files, knowledge_record_value, review_findings


def validate_reports(
    roots: dict[Path, ET.Element],
    run_dir: Path,
    failures: list[str],
    manifest_handoffs: dict[str, str],
    review_meta: dict[str, str],
    review_checkpoints: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, str | bool | None]], dict[str, dict[str, str]]]:
    seen_agent_runs: set[str] = set()
    seen_handoffs: set[str] = set()
    target_files_by_group: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    report_roots = {
        path: root for path, root in roots.items() if root.tag == "agent_run_report"
    }
    if not report_roots:
        if manifest_handoffs:
            failures.append(f"{run_dir}: no agent_run_report XML files found")
        return {}, {}

    knowledge_records: dict[str, dict[str, str | bool | None]] = {}
    review_findings: dict[str, dict[str, str]] = {}

    for path, root in report_roots.items():
        agent_run_id = child_text(root, "identity/agent_run_id")
        handoff_id = child_text(root, "identity/handoff_id")
        if agent_run_id:
            if agent_run_id in seen_agent_runs:
                failures.append(f"{path}: duplicate agent_run_id {agent_run_id}")
            seen_agent_runs.add(agent_run_id)
        if handoff_id:
            if handoff_id in seen_handoffs:
                failures.append(f"{path}: duplicate handoff_id {handoff_id}")
            seen_handoffs.add(handoff_id)

        report_agent_run_id, group_id, target_files, report_knowledge, report_findings = validate_report(
            path, root, failures, review_meta, review_checkpoints
        )
        for finding_id, finding in report_findings.items():
            if finding_id in review_findings:
                failures.append(f"{path}: duplicate cross-report review finding_id {finding_id}")
            review_findings[finding_id] = finding
        if root.get("schema_version") in EVIDENCE_SCHEMAS and handoff_id:
            expected_agent_run = manifest_handoffs.get(handoff_id)
            if expected_agent_run != report_agent_run_id:
                failures.append(f"{path}: handoff correlation does not match manifest")
        if group_id:
            for target_file in target_files:
                target_files_by_group[group_id][target_file].append(report_agent_run_id)
        if report_knowledge:
            capture_id = str(report_knowledge["capture_id"])
            if capture_id in knowledge_records:
                failures.append(f"{path}: duplicate report knowledge capture_id {capture_id}")
            knowledge_records[capture_id] = report_knowledge

    for group_id, files in target_files_by_group.items():
        for target_file, agent_runs in files.items():
            unique_runs = sorted({run for run in agent_runs if run})
            if len(unique_runs) > 1:
                failures.append(
                    "parallel target conflict: "
                    f"group {group_id} target {target_file} used by "
                    + ", ".join(unique_runs)
                )
    return knowledge_records, review_findings


def validate_digest(
    roots: dict[Path, ET.Element],
    failures: list[str],
    review_meta: dict[str, str],
    review_checkpoints: dict[str, dict[str, str]],
) -> tuple[str, str, str, dict[str, dict[str, str | bool | None]], dict[str, dict[str, str]], dict[str, object]]:
    digest_roots = [(path, root) for path, root in roots.items() if root.tag == "agentic_run_digest"]
    if not digest_roots:
        return "", "", "", {}, {}, {}
    if len(digest_roots) > 1:
        failures.append("multiple agentic_run_digest XML files found")
    path, root = digest_roots[0]
    schema_version = root.get("schema_version", "")
    digest_run_id = child_text(root, "digest/run_id")
    digest_status = child_text(root, "digest/status").lower()
    if schema_version != "4":
        failures.append(f"{path}: requires digest schema 4, got {schema_version or '<missing>'}")
        return digest_run_id, schema_version, digest_status, {}, {}, {}
    if digest_status not in CURRENT_RUN_STATUSES:
        failures.append(f"{path}: invalid schema-{schema_version} digest status {digest_status!r}")
    manual_qa_handoff = validate_manual_qa_handoff(root, str(path), failures)
    records: dict[str, dict[str, str | bool | None]] = {}
    for capture in root.findall("execution_knowledge_captures/capture"):
        record = knowledge_record(
            capture, str(path), failures, run_id=child_text(root, "digest/run_id")
        )
        capture_id = str(record["capture_id"])
        if capture_id in records:
            failures.append(f"{path}: duplicate digest capture_id {capture_id}")
        records[capture_id] = record
    findings_map: dict[str, dict[str, str]] = {}
    if schema_version == "4":
        review = root.find("write_test_review")
        if review is None or review.get("schema_version") != "1":
            failures.append(f"{path}: schema 4 digest missing write_test_review schema 1")
        else:
            validate_projection_wtr_shape(review, f"{path}: write_test_review", failures, digest=True)
            require_exact_children(
                review,
                {"policy_ref", "policy_digest", "requested_frequency", "effective_frequency", "checkpoints", "findings", "execution_status_effect", "state_errors"},
                f"{path}: write_test_review",
                failures,
            )
            if child_text(review, "policy_ref") != review_meta.get("policy_ref", ""):
                failures.append(f"{path}: digest review policy_ref mismatch")
            if child_text(review, "policy_digest") != review_meta.get("policy_digest", ""):
                failures.append(f"{path}: digest review policy mismatch")
            if child_text(review, "requested_frequency") != review_meta.get("requested", ""):
                failures.append(f"{path}: digest requested review frequency mismatch")
            if child_text(review, "effective_frequency") != review_meta.get("effective", ""):
                failures.append(f"{path}: digest effective review frequency mismatch")
            if child_text(review, "execution_status_effect") != "none":
                failures.append(f"{path}: digest consultive review altered execution status")
            seen_checkpoint_ids: set[str] = set()
            for checkpoint in review.findall("checkpoints/checkpoint"):
                require_exact_children(
                    checkpoint,
                    {"execution_id", "policy_digest", "status", "boundary_type", "boundary_ref", "coverage_digest", "review_handoff_id", "review_agent_run_id", "review_agent_raw_status", "evidence_ref", "risk_refs", "backlog_refs", "reason"},
                    f"{path}: digest checkpoint",
                    failures,
                )
                checkpoint_id = checkpoint.get("checkpoint_id", "")
                if not checkpoint_id or checkpoint_id in seen_checkpoint_ids:
                    failures.append(f"{path}: missing or duplicate digest review checkpoint {checkpoint_id!r}")
                seen_checkpoint_ids.add(checkpoint_id)
                canonical = review_checkpoints.get(checkpoint_id)
                if canonical is None:
                    failures.append(f"{path}: digest orphan review checkpoint {checkpoint_id!r}")
                elif (
                    child_text(checkpoint, "execution_id") != canonical["execution_id"]
                    or child_text(checkpoint, "policy_digest") != canonical["policy_digest"]
                    or child_text(checkpoint, "status") != canonical["status"]
                    or child_text(checkpoint, "coverage_digest") != canonical["coverage_digest"]
                    or child_text(checkpoint, "boundary_type") != canonical["boundary_type"]
                    or child_text(checkpoint, "boundary_ref") != canonical["boundary_ref"]
                    or child_text(checkpoint, "review_handoff_id") != canonical["review_handoff_id"]
                    or child_text(checkpoint, "review_agent_run_id") != canonical["review_agent_run_id"]
                    or child_text(checkpoint, "review_agent_raw_status") != canonical["review_agent_raw_status"]
                    or child_text(checkpoint, "evidence_ref") != canonical["evidence_ref"]
                    or "\n".join(non_empty_children(checkpoint, "risk_refs/risk_ref")) != canonical["risk_refs"]
                    or "\n".join(non_empty_children(checkpoint, "backlog_refs/backlog_ref")) != canonical["backlog_refs"]
                    or child_text(checkpoint, "reason") != canonical["reason"]
                ):
                    failures.append(f"{path}: digest review checkpoint mismatch {checkpoint_id}")
            if seen_checkpoint_ids != set(review_checkpoints):
                failures.append(f"{path}: digest review checkpoint set does not match manifest")
            seen_finding_ids: set[str] = set()
            finding_checkpoint_ids: set[str] = set()
            for finding in review.findall("findings/finding"):
                checkpoint_id = child_text(finding, "checkpoint_id")
                backlog_ref = child_text(finding, "backlog_ref")
                finding_id = finding.get("finding_id", "")
                if not finding_id or finding_id in seen_finding_ids:
                    failures.append(f"{path}: missing or duplicate digest finding_id {finding_id!r}")
                seen_finding_ids.add(finding_id)
                canonical = review_checkpoints.get(checkpoint_id)
                finding_checkpoint_ids.add(checkpoint_id)
                if (
                    canonical is None
                    or canonical["status"] != "completed-with-findings"
                    or not child_text(finding, "risk_ref")
                    or not backlog_ref
                    or child_text(finding, "risk_ref") not in canonical["risk_refs"].splitlines()
                    or backlog_ref not in canonical["backlog_refs"].splitlines()
                    or child_text(finding, "review_handoff_id") != canonical["review_handoff_id"]
                    or child_text(finding, "agent_run_id") != canonical["review_agent_run_id"]
                    or child_text(finding, "evidence_ref") != canonical["evidence_ref"]
                ):
                    failures.append(f"{path}: digest finding missing checkpoint/risk/backlog lineage")
                if finding_id:
                    findings_map[finding_id] = {
                        "checkpoint_id": checkpoint_id,
                        "review_handoff_id": child_text(finding, "review_handoff_id"),
                        "agent_run_id": child_text(finding, "agent_run_id"),
                        "evidence_ref": child_text(finding, "evidence_ref"),
                        "risk_ref": child_text(finding, "risk_ref"),
                        "backlog_ref": backlog_ref,
                    }
            required_finding_checkpoints = {
                checkpoint_id
                for checkpoint_id, record in review_checkpoints.items()
                if record["status"] == "completed-with-findings"
            }
            if not required_finding_checkpoints.issubset(finding_checkpoint_ids):
                failures.append(f"{path}: completed-with-findings checkpoint missing digest finding")
            for state_error in review.findall("state_errors/state_error"):
                failures.append(
                    f"{path}: unresolved review state error {state_error.get('code', '<missing>')}"
                )
    return (
        digest_run_id,
        schema_version,
        digest_status,
        records,
        findings_map,
        manual_qa_handoff,
    )


def compare_capture_records(
    source_name: str,
    expected: dict[str, str | bool | None],
    actual: dict[str, str | bool | None],
    failures: list[str],
) -> None:
    for field in ("capture_id", "run_id", "agent_run_id", "handoff_id", "material", "target_entry", "state"):
        if expected.get(field) != actual.get(field):
            failures.append(
                f"execution knowledge mismatch in {source_name} for capture "
                f"{expected.get('capture_id')}: {field} expected {expected.get(field)!r}, "
                f"got {actual.get(field)!r}"
            )
    if expected.get("state") != "captured":
        for field in ("reason", "minimum_next_path"):
            if expected.get(field) != actual.get(field):
                failures.append(
                    f"execution knowledge mismatch in {source_name} for capture "
                    f"{expected.get('capture_id')}: {field} expected "
                    f"{expected.get(field)!r}, got {actual.get(field)!r}"
                )


def validate_current_knowledge_lineage(
    run_dir: Path,
    run_id: str,
    manifest_records: dict[str, dict[str, str | bool | None]],
    report_records: dict[str, dict[str, str | bool | None]],
    digest_run_id: str,
    digest_schema: str,
    digest_status: str,
    digest_records: dict[str, dict[str, str | bool | None]],
    digest_required: bool,
    run_status: str,
    expected_digest_schema: str,
    failures: list[str],
) -> None:
    if digest_required and digest_schema != expected_digest_schema:
        failures.append(
            f"{run_dir}: terminal current run requires agentic_run_digest schema {expected_digest_schema}"
        )
    if digest_run_id and digest_run_id != run_id:
        failures.append(f"{run_dir}: digest run_id does not match manifest run_id")
    if digest_required and digest_status != run_status:
        failures.append(f"{run_dir}: terminal digest status does not match manifest run status")

    for capture_id, manifest_record in manifest_records.items():
        report_record = report_records.get(capture_id)
        if report_record is None:
            failures.append(f"{run_dir}: capture {capture_id} missing schema-4 report record")
        else:
            compare_capture_records("report", manifest_record, report_record, failures)
        if digest_run_id:
            digest_record = digest_records.get(capture_id)
            if digest_record is None:
                failures.append(f"{run_dir}: capture {capture_id} missing current digest record")
            else:
                compare_capture_records("digest", manifest_record, digest_record, failures)

        if manifest_record.get("state") != "captured":
            continue
        target_raw = str(manifest_record.get("target_entry") or "")
        target = Path(target_raw)
        target = target.resolve() if target.is_absolute() else (run_dir / target).resolve()
        if not target.is_file():
            failures.append(f"{run_dir}: captured target does not exist: {target_raw}")
            continue
        for failure in validate_knowledge_entry_file(target):
            failures.append(f"captured entry invalid: {failure}")
        try:
            entry = parse_xml_file(target)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        entry_values: dict[str, str | bool | None] = {
            "capture_id": child_text(entry, "identity/capture_id"),
            "run_id": child_text(entry, "identity/run_id"),
            "agent_run_id": child_text(entry, "identity/agent_run_id"),
            "handoff_id": child_text(entry, "identity/handoff_id"),
            "material": parse_boolean(child_text(entry, "materiality/material")),
            "target_entry": child_text(entry, "lineage/target_entry"),
            "state": child_text(entry, "capture/state"),
        }
        declared_run_raw = child_text(entry, "identity/run_directory")
        declared_run_path = Path(declared_run_raw)
        if declared_run_path.is_absolute():
            declared_run = declared_run_path.resolve()
        else:
            declared_run = (target.resolve().parents[2] / declared_run_path).resolve()
        if declared_run != run_dir.resolve():
            failures.append(
                f"captured entry {capture_id}: identity/run_directory does not match actual run_dir"
            )
        compare_capture_records("entry", manifest_record, entry_values, failures)

    extra_reports = sorted(set(report_records) - set(manifest_records))
    extra_digests = sorted(set(digest_records) - set(manifest_records))
    if extra_reports:
        failures.append(f"{run_dir}: report capture IDs absent from manifest: {', '.join(extra_reports)}")
    if extra_digests:
        failures.append(f"{run_dir}: digest capture IDs absent from manifest: {', '.join(extra_digests)}")


def parse_review_backlog(path: Path, failures: list[str]) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if line.strip().startswith("| ID | Checkpoint | Review Handoff |")),
        None,
    )
    if header_index is None:
        return {}
    rows: dict[str, dict[str, str]] = {}
    fields = (
        "backlog_ref", "checkpoint_id", "review_handoff_id", "agent_run_id",
        "evidence_ref", "coverage_digest", "risk_ref", "status", "reason",
        "description", "suggested_owner",
    )
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            break
        values = [value.strip().strip("`") for value in line.strip().strip("|").split("|")]
        if len(values) != len(fields):
            failures.append(f"{path}: malformed consultive review backlog row")
            continue
        record = dict(zip(fields, values))
        backlog_ref = record["backlog_ref"]
        if not backlog_ref or backlog_ref in rows:
            failures.append(f"{path}: missing or duplicate consultive backlog ID {backlog_ref!r}")
            continue
        rows[backlog_ref] = record
    return rows


def validate_run_dir(run_dir: Path) -> list[str]:
    failures: list[str] = []
    roots = parse_all_xml(run_dir)
    manifest_records: dict[str, dict[str, str | bool | None]] = {}
    current_schema = False
    run_id = ""
    digest_required = False
    run_status = ""
    manifest_schema = ""
    review_meta: dict[str, str] = {}
    review_checkpoints: dict[str, dict[str, str]] = {}
    manifest_manual_qa_handoff: dict[str, object] = {}

    manifest_path = run_dir / "agentic-run-manifest.xml"
    manifest = roots.get(manifest_path)
    if manifest is None:
        failures.append(f"{manifest_path}: required run manifest is missing")
    else:
        manifest_schema = manifest.get("schema_version", "")
        if manifest_schema != "4":
            failures.append(
                f"{manifest_path}: requires manifest schema 4, got {manifest_schema or '<missing>'}"
            )
        for path, root in roots.items():
            if root.tag == "agent_run_report" and root.get("schema_version") != "6":
                failures.append(
                    f"{path}: requires report schema 6, got {root.get('schema_version') or '<missing>'}"
                )
            if root.tag == "agentic_run_digest" and root.get("schema_version") != "4":
                failures.append(
                    f"{path}: requires digest schema 4, got {root.get('schema_version') or '<missing>'}"
                )
        if manifest.find("freshness_signature") is None:
            failures.append(f"{manifest_path}: missing freshness_signature")
        validate_selected_agents(manifest, str(manifest_path), failures)
        manifest_handoffs = validate_manifest_handoffs(manifest, failures)
        review_meta, review_checkpoints = validate_manifest_review(
            manifest, str(manifest_path), failures
        )
        manifest_manual_qa_handoff = validate_manual_qa_handoff(
            manifest,
            str(manifest_path),
            failures,
            expected_plan_directory=child_text(
                manifest, "write_test_review/implementation_handoff/plan_directory"
            ),
        )
        if manifest_schema == "4":
            current_schema = True
            run_id = child_text(manifest, "run/run_id")
            run_status = child_text(manifest, "run/status").lower()
            if run_status not in CURRENT_RUN_STATUSES:
                failures.append(f"{manifest_path}: invalid current run/status {run_status!r}")
            digest_required = run_status in TERMINAL_RUN_STATUSES
            if not run_id:
                failures.append(f"{manifest_path}: current schema missing run/run_id")
            policy = manifest.find("execution_knowledge_policy")
            if policy is None:
                failures.append(f"{manifest_path}: current schema missing execution_knowledge_policy")
            elif child_text(policy, "promotion_owner") != "loki-continuous-improvement":
                failures.append(f"{manifest_path}: invalid execution knowledge promotion owner")
            seen_targets: set[str] = set()
            for capture in manifest.findall("execution_knowledge_captures/capture"):
                record = knowledge_record(
                    capture, str(manifest_path), failures, run_id=run_id
                )
                capture_id = str(record["capture_id"])
                target = str(record["target_entry"])
                target_path = Path(target)
                target_path = (
                    target_path.resolve()
                    if target_path.is_absolute()
                    else (run_dir / target_path).resolve()
                )
                expected_target = (
                    run_dir.resolve()
                    / "execution-knowledge"
                    / "entries"
                    / f"{capture_id}.xml"
                )
                if target_path != expected_target:
                    failures.append(
                        f"{manifest_path}: capture {capture_id} target must resolve exactly inside actual run_dir"
                    )
                if capture_id in manifest_records:
                    failures.append(f"{manifest_path}: duplicate capture_id {capture_id!r}")
                manifest_records[capture_id] = record
                if not target or target in seen_targets:
                    failures.append(f"{manifest_path}: missing or duplicate knowledge target {target!r}")
                seen_targets.add(target)
    if manifest is None:
        manifest_handoffs = {}

    for path, root in roots.items():
        validate_decision_gates(root, str(path), failures)
        if root.tag == "agentic_analysis_manifest":
            validate_selected_agents(root, str(path), failures)

    if run_status == "blocked":
        consultive_handoff_ids = {
            checkpoint["review_handoff_id"]
            for checkpoint in review_checkpoints.values()
            if checkpoint["review_handoff_id"]
        }
        blocking_evidence = (
            manifest_manual_qa_handoff.get("status")
            == "manual-qa-not-evaluated"
        )
        if manifest is not None:
            blocking_evidence = blocking_evidence or any(
                child_text(handoff, "status").lower() in {"blocked", "failed"}
                and child_text(handoff, "handoff_id") not in consultive_handoff_ids
                for handoff in manifest.findall("handoffs/handoff")
            ) or any(
                child_text(validator, "status").lower() in {"blocked", "failed"}
                for validator in manifest.findall("validators/validator")
            ) or any(
                child_text(gate, "status").lower() in {"blocked", "failed"}
                for gate in manifest.findall("decision_gates/decision_gate")
            )
        for root in roots.values():
            if blocking_evidence:
                break
            if root.tag == "agent_run_report" and root.get("schema_version") == "6":
                handoff_id = child_text(root, "identity/handoff_id")
                correlated = manifest_handoffs.get(handoff_id) == child_text(
                    root, "identity/agent_run_id"
                )
                if correlated and handoff_id not in consultive_handoff_ids:
                    blocking_evidence = any(
                        child_text(validator, "status").lower() in {"blocked", "failed"}
                        for validator in root.findall("validators/validator")
                    ) or any(
                        child_text(gate, "status").lower() in {"blocked", "failed"}
                        for gate in root.findall("gates/gate")
                    ) or any(
                        text(blocker)
                        for blocker in root.findall("completion/blockers/blocker")
                    )
            elif (
                root.tag == "agentic_run_digest"
                and root.get("schema_version") == "4"
                and child_text(root, "digest/run_id") == run_id
            ):
                blocking_evidence = any(
                    child_text(validator, "status").lower() in {"blocked", "failed"}
                    for validator in root.findall("validators/validator")
                ) or any(
                    child_text(gate, "status").lower() in {"blocked", "failed"}
                    for gate in root.findall("human_gates/gate")
                )
        if not blocking_evidence:
            failures.append(
                f"{manifest_path}: outer blocked status lacks non-consultive blocker evidence"
            )

    report_records, report_findings = validate_reports(
        roots,
        run_dir,
        failures,
        manifest_handoffs,
        review_meta,
        review_checkpoints,
    )
    (
        digest_run_id,
        digest_schema,
        digest_status,
        digest_records,
        digest_findings,
        digest_manual_qa_handoff,
    ) = validate_digest(roots, failures, review_meta, review_checkpoints)
    if manifest_manual_qa_handoff != digest_manual_qa_handoff:
        failures.append(
            f"{run_dir}: manifest and digest manual_qa_handoff projections differ"
        )
    if manifest is not None:
        validate_terminal_reconciliation(
            run_status,
            child_text(
                manifest, "write_test_review/implementation_handoff/status"
            ),
            str(manifest_manual_qa_handoff.get("status") or ""),
            str(manifest_path),
            failures,
        )
    if current_schema:
        validate_current_knowledge_lineage(
            run_dir,
            run_id,
            manifest_records,
            report_records,
            digest_run_id,
            digest_schema,
            digest_status,
            digest_records,
            digest_required,
            run_status,
            "4" if manifest_schema == "4" else "3",
            failures,
        )
    if report_findings != digest_findings:
        failures.append(f"{run_dir}: report and digest review finding lineage mismatch")
    if any(
        checkpoint["status"] == "completed-with-findings"
        for checkpoint in review_checkpoints.values()
    ) and not report_findings:
        failures.append(
            f"{run_dir}: completed-with-findings checkpoint lacks report/digest finding lineage"
        )
    consultive_checkpoints = {
        checkpoint_id: checkpoint
        for checkpoint_id, checkpoint in review_checkpoints.items()
        if checkpoint["status"] in REVIEW_RISK_BACKLOG
    }
    if consultive_checkpoints and digest_schema != "4":
        failures.append(
            f"{run_dir}: consultive finding/degraded checkpoints require digest schema 4"
        )
    expected_backlog_rows: dict[str, tuple[str, dict[str, str], str]] = {}
    for checkpoint_id, checkpoint in consultive_checkpoints.items():
        if checkpoint["status"] in REVIEW_DEGRADED:
            backlog_ref = checkpoint["backlog_refs"]
            risk_ref = checkpoint["risk_refs"]
            if backlog_ref:
                expected_backlog_rows[backlog_ref] = (checkpoint_id, checkpoint, risk_ref)
    for finding in report_findings.values():
        checkpoint = review_checkpoints.get(finding["checkpoint_id"])
        if checkpoint is not None:
            expected_backlog_rows[finding["backlog_ref"]] = (
                finding["checkpoint_id"], checkpoint, finding["risk_ref"]
            )
    if expected_backlog_rows:
        backlog_path = run_dir / "backlog.md"
        backlog_rows = parse_review_backlog(backlog_path, failures)
        for backlog_ref, (checkpoint_id, checkpoint, risk_ref) in sorted(expected_backlog_rows.items()):
            row = backlog_rows.get(backlog_ref)
            if row is None:
                failures.append(f"{backlog_path}: missing structured lineage row for {backlog_ref}")
                continue
            expected = {
                "checkpoint_id": checkpoint_id,
                "review_handoff_id": checkpoint["review_handoff_id"],
                "agent_run_id": checkpoint["review_agent_run_id"],
                "evidence_ref": checkpoint["evidence_ref"],
                "coverage_digest": checkpoint["coverage_digest"],
                "risk_ref": risk_ref,
                "status": checkpoint["status"],
                "reason": checkpoint["reason"],
            }
            for field, value in expected.items():
                if row[field] != value:
                    failures.append(
                        f"{backlog_path}: outcome {backlog_ref} {field} does not match canonical lineage"
                    )
    return failures


def run_self_test() -> None:
    assert CURRENT_RUN_STATUSES == {"completed", "blocked"}
    execution_id = "execution-self-test"
    policy_digest = canonical_digest(
        {
            "schema_version": 1,
            "requested_frequency": "plano",
            "effective_frequency": "plano",
            "source": "explicit",
            "terminal_scope": "plano",
            "selected_agent": {
                "name": "quality-auditor",
                "selection_reason": "compatible metadata",
            },
        }
    )
    coverage_manifest = {
        "schema_version": 1,
        "handoffs": [
            {
                "handoff_id": "write-1",
                "completion_ref": "completion/write-1.md",
                "evidence_ref": "evidence/write-1.xml",
                "changed_files": [
                    {"path": "target.md", "sha256": "sha256:" + "d" * 64}
                ],
            }
        ],
        "reviewer": {
            "name": "quality-auditor",
            "contract_version": "1",
            "selection_configuration_digest": "sha256:" + "e" * 64,
        },
    }
    coverage_digest = canonical_digest(coverage_manifest)
    checkpoint_id = checkpoint_identity(
        execution_id, policy_digest, "plano", "plan-self-test", coverage_digest
    )
    review_handoff_id = "review-handoff-v1:" + checkpoint_id.split(":", 1)[1]
    implementation_handoff = f"""<implementation_handoff schema_version="1"><handoff_id>implementation-handoff-v1:{'a' * 64}</handoff_id><command>loki-implement-feature</command><demand_ref>demand.md</demand_ref><demand_digest>sha256:{'b' * 64}</demand_digest><analysis_file>analise/technical-analysis.md</analysis_file><analysis_digest>sha256:{'c' * 64}</analysis_digest><plan_directory>implementation</plan_directory><status>awaiting-manual-qa</status><execution_state_ref>implementation/tasks.md#loki-run-state</execution_state_ref><execution_state_digest>sha256:{'d' * 64}</execution_state_digest><result_ref>implementation/builds/result.md</result_ref><dashboard_ref>implementation/builds/dashboard.md</dashboard_ref><next_action>return terminal dashboard</next_action></implementation_handoff>"""
    manual_run_id = "loki-run-v2:" + "1" * 64
    manual_execution_id = "loki-execution-v2:" + "2" * 64
    manual_qa_handoff = f"""<manual_qa_handoff><schema_version>2</schema_version><status>ready-for-manual-qa</status><run_id>{manual_run_id}</run_id><execution_id>{manual_execution_id}</execution_id><plan_directory>implementation</plan_directory><automatic_evidence_refs><ref>evidence/terminal-1.json</ref><ref>evidence/terminal-2.json</ref></automatic_evidence_refs><manual_qa_result_ref>implementation/builds/manual-qa/result.json</manual_qa_result_ref><manual_qa_attestation_ref>implementation/interaction/manual-qa/{manual_run_id}/attestation.json</manual_qa_attestation_ref><task_refs><ref>tasks.md#task-1</ref><ref>tasks.md#task-2</ref></task_refs><acceptance_criterion_refs><ref>tasks.md#ac-1</ref><ref>tasks.md#ac-2</ref></acceptance_criterion_refs><gate_refs><ref>tasks.md#gate-1</ref><ref>tasks.md#gate-2</ref></gate_refs><changed_target_refs><ref>src/one.py</ref><ref>src/two.py</ref></changed_target_refs><reason/></manual_qa_handoff>"""
    legacy = """<?xml version="1.0"?><agentic_run_manifest schema_version="1"><freshness_signature/></agentic_run_manifest>"""
    current = f"""<?xml version="1.0"?>
<agentic_run_manifest schema_version="4">
  <run><run_id>run-self-test</run_id><status>completed</status></run>
  <freshness_signature/>
  <execution_knowledge_policy><promotion_owner>loki-continuous-improvement</promotion_owner></execution_knowledge_policy>
  <write_test_review schema_version="1">
    <request><requested_frequency>plano</requested_frequency><provenance>explicit</provenance></request>
    {implementation_handoff}
    <reconciled_policy><policy_ref>tasks.md#policy</policy_ref><policy_digest>{policy_digest}</policy_digest><effective_frequency>plano</effective_frequency><terminal_scope>plano</terminal_scope><selected_agent_name>quality-auditor</selected_agent_name><selection_reason>compatible metadata</selection_reason></reconciled_policy>
    <checkpoints><checkpoint checkpoint_id="{checkpoint_id}"><execution_id>{execution_id}</execution_id><policy_digest>{policy_digest}</policy_digest><boundary_type>plano</boundary_type><boundary_ref>plan-self-test</boundary_ref><coverage_digest>{coverage_digest}</coverage_digest><coverage_manifest schema_version="1"><handoffs><handoff><handoff_id>write-1</handoff_id><completion_ref>completion/write-1.md</completion_ref><evidence_ref>evidence/write-1.xml</evidence_ref><changed_files><file><path>target.md</path><sha256>{coverage_manifest['handoffs'][0]['changed_files'][0]['sha256']}</sha256></file></changed_files></handoff></handoffs><reviewer><name>quality-auditor</name><contract_version>1</contract_version><selection_configuration_digest>{coverage_manifest['reviewer']['selection_configuration_digest']}</selection_configuration_digest></reviewer></coverage_manifest><covered_write_handoff_ids><handoff_id>write-1</handoff_id></covered_write_handoff_ids><status>completed-clean</status><review_handoff_id>{review_handoff_id}</review_handoff_id><review_agent_run_id>review-run-1</review_agent_run_id><review_agent_raw_status>clean</review_agent_raw_status><evidence_ref>evidence/review.xml</evidence_ref><risk_refs/><backlog_refs/><execution_status_effect>none</execution_status_effect><reason/></checkpoint></checkpoints>
    <risks/><state_errors/><next_action>continue</next_action>
  </write_test_review>
  {manual_qa_handoff}
</agentic_run_manifest>"""

    current_digest = f"""<?xml version="1.0"?>
<agentic_run_digest schema_version="4"><digest><run_id>run-self-test</run_id><status>completed</status></digest>
<execution_knowledge_captures/>
<write_test_review schema_version="1"><policy_ref>tasks.md#policy</policy_ref><policy_digest>{policy_digest}</policy_digest><requested_frequency>plano</requested_frequency><effective_frequency>plano</effective_frequency><checkpoints><checkpoint checkpoint_id="{checkpoint_id}"><execution_id>{execution_id}</execution_id><policy_digest>{policy_digest}</policy_digest><status>completed-clean</status><boundary_type>plano</boundary_type><boundary_ref>plan-self-test</boundary_ref><coverage_digest>{coverage_digest}</coverage_digest><review_handoff_id>{review_handoff_id}</review_handoff_id><review_agent_run_id>review-run-1</review_agent_run_id><review_agent_raw_status>clean</review_agent_raw_status><evidence_ref>evidence/review.xml</evidence_ref><risk_refs/><backlog_refs/><reason/></checkpoint></checkpoints><findings/><execution_status_effect>none</execution_status_effect><state_errors/></write_test_review>
{manual_qa_handoff}</agentic_run_digest>"""

    def validate_fixture(source: str, digest_source: str | None = None) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            (run_dir / "agentic-run-manifest.xml").write_text(source, encoding="utf-8")
            if digest_source is None and 'schema_version="4"' in source:
                source_status = child_text(ET.fromstring(source), "run/status")
                digest_source = current_digest.replace(
                    "<status>completed</status>",
                    f"<status>{source_status}</status>",
                    1,
                )
            if digest_source is not None:
                (run_dir / "agentic-run-digest.xml").write_text(
                    digest_source, encoding="utf-8"
                )
            return validate_run_dir(run_dir)

    legacy_failures = validate_fixture(legacy)
    assert any("requires manifest schema 4" in failure for failure in legacy_failures)
    unknown_manifest_failures = validate_fixture(
        legacy.replace('schema_version="1"', 'schema_version="99"')
    )
    assert any("requires manifest schema 4" in failure for failure in unknown_manifest_failures)
    current_failures = validate_fixture(current)
    assert current_failures == [], current_failures
    documented_terminal_statuses = documented_implement_feature_terminal_statuses()
    assert documented_terminal_statuses == IMPLEMENT_FEATURE_TERMINAL_STATUSES, (
        "implementation handoff terminal status drift",
        sorted(documented_terminal_statuses),
        sorted(IMPLEMENT_FEATURE_TERMINAL_STATUSES),
    )

    def handoff_fixture_for_status(status: str) -> str:
        candidate = implementation_handoff.replace(
            "<status>awaiting-manual-qa</status>", f"<status>{status}</status>"
        )
        if status in IMPLEMENTATION_HANDOFF_PRETERMINAL_STATUSES:
            for field in (
                "execution_state_ref",
                "execution_state_digest",
                "result_ref",
                "dashboard_ref",
            ):
                candidate = re.sub(
                    rf"<{field}>.*?</{field}>",
                    f"<{field}>null</{field}>",
                    candidate,
                )
        return current.replace(implementation_handoff, candidate)

    def manual_qa_fixture_for_status(status: str) -> str:
        candidate = manual_qa_handoff.replace(
            "<status>ready-for-manual-qa</status>", f"<status>{status}</status>"
        )
        if status != "ready-for-manual-qa":
            candidate = candidate.replace(
                "<reason/>", f"<reason>{status} reconciliation</reason>"
            )
        return candidate

    def reconciliation_failures(
        implementation_status: str, parent_status: str, manual_qa_status: str
    ) -> list[str]:
        manifest_source = handoff_fixture_for_status(implementation_status)
        manual_source = manual_qa_fixture_for_status(manual_qa_status)
        manifest_source = manifest_source.replace(
            manual_qa_handoff, manual_source
        ).replace(
            "<run><run_id>run-self-test</run_id><status>completed</status></run>",
            f"<run><run_id>run-self-test</run_id><status>{parent_status}</status></run>",
            1,
        )
        digest_source = current_digest.replace(
            manual_qa_handoff, manual_source
        ).replace(
            "<digest><run_id>run-self-test</run_id><status>completed</status></digest>",
            f"<digest><run_id>run-self-test</run_id><status>{parent_status}</status></digest>",
            1,
        )
        return validate_fixture(manifest_source, digest_source)

    reconciliation_negative_count = 0
    for implementation_status, expected in sorted(
        TERMINAL_RECONCILIATION_BY_IMPLEMENTATION_STATUS.items()
    ):
        positive_failures = reconciliation_failures(
            implementation_status, expected[0], expected[1]
        )
        assert positive_failures == [], (
            implementation_status,
            expected,
            positive_failures,
        )
        for parent_status in sorted(CURRENT_RUN_STATUSES):
            for manual_qa_status in sorted(MANUAL_QA_HANDOFF_STATUSES):
                if (parent_status, manual_qa_status) == expected:
                    continue
                combination_failures = reconciliation_failures(
                    implementation_status, parent_status, manual_qa_status
                )
                assert any(
                    "invalid terminal reconciliation" in failure
                    for failure in combination_failures
                ), (
                    implementation_status,
                    parent_status,
                    manual_qa_status,
                    combination_failures,
                )
                reconciliation_negative_count += 1

    invalid_implementation_statuses = (
        RESOLVED_GATE_STATUSES
        | KNOWLEDGE_CAPTURE_STATES
        | CURRENT_RUN_STATUSES
        | REVIEW_STATUSES
        | RAW_CLEAN_STATUSES
        | RAW_FINDING_STATUSES
        | RAW_FAILURE_STATUSES
    ) - IMPLEMENTATION_HANDOFF_STATUSES | {
        "",
        "COMPLETED",
        "completed_with_limitations",
        "unknown",
    }
    for status in sorted(invalid_implementation_statuses):
        status_failures = validate_fixture(handoff_fixture_for_status(status))
        assert any(
            "invalid implementation handoff status" in failure
            for failure in status_failures
        ), (status, status_failures)
    checkpoint_record = {
        checkpoint_id: {
            "status": "completed-with-findings",
            "execution_id": execution_id,
            "policy_digest": policy_digest,
            "coverage_digest": coverage_digest,
            "boundary_type": "plano",
            "boundary_ref": "plan-self-test",
            "covered_ids": "write-1",
            "review_handoff_id": review_handoff_id,
            "review_agent_run_id": "review-run-1",
            "review_agent_raw_status": "blocked",
            "evidence_ref": "evidence/review.xml",
            "risk_refs": "risk-1",
            "backlog_refs": "WTR-1",
            "reason": "",
        }
    }
    report_review = ET.fromstring(f"""
<agent_run_report schema_version="6"><write_test_review schema_version="1">
  <policy_ref>tasks.md#policy</policy_ref><policy_digest>{policy_digest}</policy_digest><execution_id>{execution_id}</execution_id><checkpoint_ref checkpoint_id="{checkpoint_id}">tasks.md#checkpoint</checkpoint_ref><coverage_digest>{coverage_digest}</coverage_digest>
  <covered_write_handoff_ids><handoff_id>write-1</handoff_id></covered_write_handoff_ids><review_lineage><review_handoff_id>{review_handoff_id}</review_handoff_id><review_agent_run_id>review-run-1</review_agent_run_id><evidence_ref>evidence/review.xml</evidence_ref></review_lineage>
  <outcome><status>completed-with-findings</status><review_agent_raw_status>blocked</review_agent_raw_status><execution_status_effect>none</execution_status_effect><reason/></outcome>
  <findings><finding finding_id="finding-1"><summary>consultive</summary><risk_ref>risk-1</risk_ref><backlog_ref>WTR-1</backlog_ref></finding></findings>
  <risk_refs><risk_ref>risk-1</risk_ref></risk_refs><backlog_refs><backlog_ref>WTR-1</backlog_ref></backlog_refs>
</write_test_review></agent_run_report>""")
    report_failures: list[str] = []
    expected_finding = {
        "checkpoint_id": checkpoint_id,
        "review_handoff_id": review_handoff_id,
        "agent_run_id": "review-run-1",
        "evidence_ref": "evidence/review.xml",
        "risk_ref": "risk-1",
        "backlog_ref": "WTR-1",
    }
    assert validate_report_review(
        Path("report.xml"), report_review, {"policy_digest": policy_digest, "policy_ref": "tasks.md#policy", "requested": "plano", "effective": "plano"}, checkpoint_record, report_failures
    ) == {"finding-1": expected_finding}
    assert report_failures == [], report_failures
    observability = ET.fromstring(f"""
<agent_run_report schema_version="6">
  <timing><span_id>execution-span-v1:{'1' * 64}</span_id><parent_span_id>null</parent_span_id><started_at_utc>null</started_at_utc><ended_at_utc>null</ended_at_utc><monotonic_duration_ms>null</monotonic_duration_ms><clock_provenance>unavailable</clock_provenance><clock_degradation_reason>adapter clock unavailable</clock_degradation_reason></timing>
  <usage><metrics_ref>builds/metrics/execution-metrics.json</metrics_ref><metrics_digest>sha256:{'2' * 64}</metrics_digest><metrics_status>unavailable</metrics_status><span_id>execution-span-v1:{'1' * 64}</span_id><usage_status>unavailable</usage_status><exact_source>null</exact_source><estimate_method>null</estimate_method><unavailable_reason>run-scoped counter unavailable</unavailable_reason></usage>
  <replay_validator_correlation><iteration>0</iteration><replay>false</replay><replay_cause>null</replay_cause><cause_span_id>null</cause_span_id><validator_span_id>null</validator_span_id><validator_command>null</validator_command><validator_version>null</validator_version><validator_input_digest>null</validator_input_digest><validator_policy_digest>null</validator_policy_digest><execution_mode>not-applicable</execution_mode><would_reuse>not-applicable</would_reuse></replay_validator_correlation>
  <materiality_precheck_correlation><profile_ref>builds/profile.yaml</profile_ref><profile_digest>sha256:{'3' * 64}</profile_digest><materiality_ref>builds/materiality.yaml</materiality_ref><materiality_digest>sha256:{'4' * 64}</materiality_digest><status>valid</status><auditor_dispatch>permitted</auditor_dispatch></materiality_precheck_correlation>
  <liveness_probe><required_before_silence_stop>false</required_before_silence_stop><trigger>none</trigger><observed_at_utc>null</observed_at_utc><adapter>generic</adapter><source>null</source><outcome>not-required</outcome><reason>null</reason><silence_stop_permitted>not-applicable</silence_stop_permitted></liveness_probe>
</agent_run_report>""")
    observability_failures: list[str] = []
    validate_report_v6_observability(Path("report-v6.xml"), observability, observability_failures)
    assert observability_failures == [], observability_failures
    bypassed_liveness = copy.deepcopy(observability)
    bypassed_liveness.find("liveness_probe/trigger").text = "silence-stop"
    bypassed_liveness.find("liveness_probe/required_before_silence_stop").text = "false"
    bypassed_liveness.find("liveness_probe/outcome").text = "terminal"
    bypassed_liveness.find("liveness_probe/silence_stop_permitted").text = "true"
    bypassed_liveness_failures: list[str] = []
    validate_report_v6_observability(Path("report-v6.xml"), bypassed_liveness, bypassed_liveness_failures)
    assert any("silence-stop trigger requires" in failure for failure in bypassed_liveness_failures), bypassed_liveness_failures
    invalid_materiality = copy.deepcopy(observability)
    invalid_materiality.find("materiality_precheck_correlation/status").text = "invalid"
    invalid_materiality_failures: list[str] = []
    validate_report_v6_observability(Path("report-v6.xml"), invalid_materiality, invalid_materiality_failures)
    assert any("materiality-to-Auditor gate" in failure for failure in invalid_materiality_failures)
    def assert_report_invalid(mutator: object) -> None:
        candidate = copy.deepcopy(report_review)
        mutator(candidate)  # type: ignore[operator]
        candidate_failures: list[str] = []
        validate_report_review(
            Path("report.xml"),
            candidate,
            {"policy_digest": policy_digest, "policy_ref": "tasks.md#policy", "requested": "plano", "effective": "plano"},
            checkpoint_record,
            candidate_failures,
        )
        assert candidate_failures

    assert_report_invalid(lambda root: root.find("write_test_review/findings").clear())
    assert_report_invalid(lambda root: setattr(root.find("write_test_review/checkpoint_ref"), "text", ""))
    def duplicate_report_coverage(root: ET.Element) -> None:
        element = ET.Element("handoff_id")
        element.text = "write-1"
        root.find("write_test_review/covered_write_handoff_ids").append(element)
    assert_report_invalid(duplicate_report_coverage)
    def duplicate_report_finding(root: ET.Element) -> None:
        findings = root.find("write_test_review/findings")
        findings.append(copy.deepcopy(findings.find("finding")))
    assert_report_invalid(duplicate_report_finding)
    assert_report_invalid(lambda root: root.find("write_test_review").set("evil", "1"))
    assert_report_invalid(lambda root: root.find("write_test_review/findings/finding").set("evil", "1"))
    def duplicate_report_summary(root: ET.Element) -> None:
        summary = root.find("write_test_review/findings/finding/summary")
        root.find("write_test_review/findings/finding").append(copy.deepcopy(summary))
    assert_report_invalid(duplicate_report_summary)
    assert_report_invalid(lambda root: root.find("write_test_review/findings").set("evil", "1"))
    assert_report_invalid(
        lambda root: setattr(
            root.find("write_test_review/outcome/review_agent_raw_status"), "text", "approved"
        )
    )
    assert_report_invalid(
        lambda root: setattr(
            root.find("write_test_review/outcome/review_agent_raw_status"), "text", "clean"
        )
    )
    def assert_clean_report_invalid(*, raw_status: str = "", keep_finding: bool = False) -> None:
        candidate = copy.deepcopy(report_review)
        candidate.find("write_test_review/outcome/status").text = "completed-clean"
        candidate.find("write_test_review/outcome/review_agent_raw_status").text = raw_status
        if not keep_finding:
            candidate.find("write_test_review/findings").clear()
        clean_checkpoint = copy.deepcopy(checkpoint_record)
        clean_checkpoint[checkpoint_id]["status"] = "completed-clean"
        candidate_failures: list[str] = []
        validate_report_review(
            Path("report.xml"),
            candidate,
            {"policy_digest": policy_digest, "policy_ref": "tasks.md#policy", "requested": "plano", "effective": "plano"},
            clean_checkpoint,
            candidate_failures,
        )
        assert candidate_failures

    assert_clean_report_invalid(keep_finding=True)
    assert_clean_report_invalid(raw_status="blocked")
    assert_clean_report_invalid(raw_status="findings")
    digest_review = ET.fromstring(f"""
<agentic_run_digest schema_version="4"><digest><run_id>run-self-test</run_id><status>completed</status></digest>
<write_test_review schema_version="1"><policy_ref>tasks.md#policy</policy_ref><policy_digest>{policy_digest}</policy_digest><requested_frequency>plano</requested_frequency><effective_frequency>plano</effective_frequency><checkpoints><checkpoint checkpoint_id="{checkpoint_id}"><execution_id>{execution_id}</execution_id><policy_digest>{policy_digest}</policy_digest><status>completed-with-findings</status><boundary_type>plano</boundary_type><boundary_ref>plan-self-test</boundary_ref><coverage_digest>{coverage_digest}</coverage_digest><review_handoff_id>{review_handoff_id}</review_handoff_id><review_agent_run_id>review-run-1</review_agent_run_id><review_agent_raw_status>blocked</review_agent_raw_status><evidence_ref>evidence/review.xml</evidence_ref><risk_refs><risk_ref>risk-1</risk_ref></risk_refs><backlog_refs><backlog_ref>WTR-1</backlog_ref></backlog_refs><reason/></checkpoint></checkpoints><findings><finding finding_id="finding-1"><checkpoint_id>{checkpoint_id}</checkpoint_id><review_handoff_id>{review_handoff_id}</review_handoff_id><agent_run_id>review-run-1</agent_run_id><evidence_ref>evidence/review.xml</evidence_ref><risk_ref>risk-1</risk_ref><backlog_ref>WTR-1</backlog_ref></finding></findings><execution_status_effect>none</execution_status_effect><state_errors/></write_test_review>{manual_qa_handoff}</agentic_run_digest>""")
    digest_failures: list[str] = []
    digest_result = validate_digest(
        {Path("digest.xml"): digest_review}, digest_failures, {"policy_digest": policy_digest, "policy_ref": "tasks.md#policy", "requested": "plano", "effective": "plano"}, checkpoint_record
    )
    assert digest_failures == [] and digest_result[4] == {"finding-1": expected_finding}
    def assert_digest_invalid(mutator: object) -> None:
        candidate = copy.deepcopy(digest_review)
        mutator(candidate)  # type: ignore[operator]
        candidate_failures: list[str] = []
        validate_digest(
            {Path("digest.xml"): candidate},
            candidate_failures,
            {"policy_digest": policy_digest, "policy_ref": "tasks.md#policy", "requested": "plano", "effective": "plano"},
            checkpoint_record,
        )
        assert candidate_failures

    assert_digest_invalid(lambda root: setattr(root.find("write_test_review/requested_frequency"), "text", "fase"))
    assert_digest_invalid(lambda root: setattr(root.find("write_test_review/findings/finding/evidence_ref"), "text", ""))
    def duplicate_digest_checkpoint(root: ET.Element) -> None:
        checkpoints = root.find("write_test_review/checkpoints")
        checkpoints.append(copy.deepcopy(checkpoints.find("checkpoint")))
    assert_digest_invalid(duplicate_digest_checkpoint)
    assert_digest_invalid(lambda root: root.find("write_test_review").set("evil", "1"))
    assert_digest_invalid(lambda root: root.find("write_test_review/checkpoints/checkpoint").set("evil", "1"))
    assert_digest_invalid(lambda root: root.find("write_test_review/findings/finding").set("evil", "1"))
    def duplicate_digest_risk(root: ET.Element) -> None:
        risk = ET.Element("risk_ref")
        risk.text = "risk-1"
        root.find("write_test_review/checkpoints/checkpoint/risk_refs").append(risk)
    assert_digest_invalid(duplicate_digest_risk)

    def degraded_sources(status: str) -> tuple[str, str, str]:
        selected_agent = None if status == "skipped-agent-unavailable" else "quality-auditor"
        degraded_policy_digest = canonical_digest(
            {
                "schema_version": 1,
                "requested_frequency": "plano",
                "effective_frequency": "plano",
                "source": "explicit",
                "terminal_scope": "plano",
                "selected_agent": {
                    "name": selected_agent,
                    "selection_reason": "compatible metadata",
                },
            }
        )
        degraded_coverage = copy.deepcopy(coverage_manifest)
        degraded_coverage["reviewer"]["name"] = selected_agent  # type: ignore[index]
        degraded_coverage_digest = canonical_digest(degraded_coverage)
        degraded_checkpoint_id = checkpoint_identity(
            execution_id,
            degraded_policy_digest,
            "plano",
            "plan-self-test",
            degraded_coverage_digest,
        )
        handoff = (
            "" if status == "skipped-agent-unavailable"
            else "review-handoff-v1:" + degraded_checkpoint_id.split(":", 1)[1]
        )
        agent_run = "" if status == "skipped-agent-unavailable" else "review-run-1"
        raw_status = "error" if status == "failed-consultive" else ""
        evidence = "evidence/review.xml" if status == "failed-consultive" else ""
        selected_xml = selected_agent or ""
        manifest_source = f"""<?xml version="1.0"?>
<agentic_run_manifest schema_version="4"><run><run_id>run-self-test</run_id><status>completed</status></run><freshness_signature/><execution_knowledge_policy><promotion_owner>loki-continuous-improvement</promotion_owner></execution_knowledge_policy><write_test_review schema_version="1"><request><requested_frequency>plano</requested_frequency><provenance>explicit</provenance></request>{implementation_handoff}<reconciled_policy><policy_ref>tasks.md#policy</policy_ref><policy_digest>{degraded_policy_digest}</policy_digest><effective_frequency>plano</effective_frequency><terminal_scope>plano</terminal_scope><selected_agent_name>{selected_xml}</selected_agent_name><selection_reason>compatible metadata</selection_reason></reconciled_policy><checkpoints><checkpoint checkpoint_id="{degraded_checkpoint_id}"><execution_id>{execution_id}</execution_id><policy_digest>{degraded_policy_digest}</policy_digest><boundary_type>plano</boundary_type><boundary_ref>plan-self-test</boundary_ref><coverage_digest>{degraded_coverage_digest}</coverage_digest><coverage_manifest schema_version="1"><handoffs><handoff><handoff_id>write-1</handoff_id><completion_ref>completion/write-1.md</completion_ref><evidence_ref>evidence/write-1.xml</evidence_ref><changed_files><file><path>target.md</path><sha256>{degraded_coverage['handoffs'][0]['changed_files'][0]['sha256']}</sha256></file></changed_files></handoff></handoffs><reviewer><name>{selected_xml}</name><contract_version>1</contract_version><selection_configuration_digest>{degraded_coverage['reviewer']['selection_configuration_digest']}</selection_configuration_digest></reviewer></coverage_manifest><covered_write_handoff_ids><handoff_id>write-1</handoff_id></covered_write_handoff_ids><status>{status}</status><review_handoff_id>{handoff}</review_handoff_id><review_agent_run_id>{agent_run}</review_agent_run_id><review_agent_raw_status>{raw_status}</review_agent_raw_status><evidence_ref>{evidence}</evidence_ref><risk_refs><risk_ref>risk-degraded</risk_ref></risk_refs><backlog_refs><backlog_ref>WTR-DEGRADED</backlog_ref></backlog_refs><execution_status_effect>none</execution_status_effect><reason>review degraded</reason></checkpoint></checkpoints><risks><risk_ref>risk-degraded</risk_ref></risks><state_errors/><next_action>continue</next_action></write_test_review>{manual_qa_handoff}</agentic_run_manifest>"""
        digest_source = f"""<?xml version="1.0"?>
<agentic_run_digest schema_version="4"><digest><run_id>run-self-test</run_id><status>completed</status></digest>
<write_test_review schema_version="1"><policy_ref>tasks.md#policy</policy_ref><policy_digest>{degraded_policy_digest}</policy_digest><requested_frequency>plano</requested_frequency><effective_frequency>plano</effective_frequency><checkpoints><checkpoint checkpoint_id="{degraded_checkpoint_id}"><execution_id>{execution_id}</execution_id><policy_digest>{degraded_policy_digest}</policy_digest><status>{status}</status><boundary_type>plano</boundary_type><boundary_ref>plan-self-test</boundary_ref><coverage_digest>{degraded_coverage_digest}</coverage_digest><review_handoff_id>{handoff}</review_handoff_id><review_agent_run_id>{agent_run}</review_agent_run_id><review_agent_raw_status>{raw_status}</review_agent_raw_status><evidence_ref>{evidence}</evidence_ref><risk_refs><risk_ref>risk-degraded</risk_ref></risk_refs><backlog_refs><backlog_ref>WTR-DEGRADED</backlog_ref></backlog_refs><reason>review degraded</reason></checkpoint></checkpoints><findings/><execution_status_effect>none</execution_status_effect><state_errors/></write_test_review>{manual_qa_handoff}</agentic_run_digest>"""
        backlog_source = f"""## Consultive Write Test Outcomes

| ID | Checkpoint | Review Handoff | Agent Run | Evidence | Coverage | Risk | Status | Reason | Description | Suggested Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WTR-DEGRADED | {degraded_checkpoint_id} | {handoff} | {agent_run} | {evidence} | {degraded_coverage_digest} | risk-degraded | {status} | review degraded | degraded outcome | orchestrator |
"""
        return manifest_source, digest_source, backlog_source

    def validate_degraded_full_run(status: str, *, mutation: str = "") -> list[str]:
        manifest_source, digest_source, backlog_source = degraded_sources(status)
        if mutation == "missing-digest-risk":
            digest_source = digest_source.replace("<risk_ref>risk-degraded</risk_ref>", "")
        elif mutation == "missing-backlog":
            backlog_source = ""
        elif mutation == "legacy-digest":
            digest_source = "<?xml version=\"1.0\"?><agentic_run_digest schema_version=\"3\"><digest><run_id>run-self-test</run_id><status>running</status></digest></agentic_run_digest>"
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            (run_dir / "agentic-run-manifest.xml").write_text(manifest_source, encoding="utf-8")
            (run_dir / "agentic-run-digest.xml").write_text(digest_source, encoding="utf-8")
            if backlog_source:
                (run_dir / "backlog.md").write_text(backlog_source, encoding="utf-8")
            return validate_run_dir(run_dir)

    for degraded_status in sorted(REVIEW_DEGRADED):
        assert validate_degraded_full_run(degraded_status) == [], degraded_status
        assert validate_degraded_full_run(degraded_status, mutation="missing-digest-risk")
        assert validate_degraded_full_run(degraded_status, mutation="missing-backlog")
    legacy_digest_failures = validate_degraded_full_run("failed-consultive", mutation="legacy-digest")
    assert any("requires digest schema 4" in failure for failure in legacy_digest_failures)
    with tempfile.TemporaryDirectory() as directory:
        run_dir = Path(directory)
        (run_dir / "agentic-run-manifest.xml").write_text(current, encoding="utf-8")
        (run_dir / "legacy-report.xml").write_text(
            '<?xml version="1.0"?><agent_run_report schema_version="5"/>', encoding="utf-8"
        )
        report_schema_failures = validate_run_dir(run_dir)
        assert any("requires report schema 6" in failure for failure in report_schema_failures)
        (run_dir / "unknown-report.xml").write_text(
            '<?xml version="1.0"?><agent_run_report schema_version="99"/>', encoding="utf-8"
        )
        unknown_report_failures = validate_run_dir(run_dir)
        assert any("requires report schema 6" in failure for failure in unknown_report_failures)
    with tempfile.TemporaryDirectory() as directory:
        run_dir = Path(directory)
        (run_dir / "agentic-run-manifest.xml").write_text(current, encoding="utf-8")
        (run_dir / "unknown-digest.xml").write_text(
            '<?xml version="1.0"?><agentic_run_digest schema_version="99"/>', encoding="utf-8"
        )
        unknown_digest_failures = validate_run_dir(run_dir)
        assert any("requires digest schema 4" in failure for failure in unknown_digest_failures)
    consultive_blocker = current.replace(
        "<status>completed</status>", "<status>blocked</status>", 1
    ).replace(
        "<freshness_signature/>",
        f"<freshness_signature/><handoffs><handoff><handoff_id>{review_handoff_id}</handoff_id><agent_run_id>review-run-1</agent_run_id><evidence_id>review-evidence</evidence_id><evidence_manifest_path>evidence/review.xml</evidence_manifest_path><status>blocked</status><blockers><blocker>consultive review blocked</blocker></blockers></handoff></handoffs>",
    )
    consultive_blocker_failures = validate_fixture(consultive_blocker)
    assert any(
        "outer blocked status lacks non-consultive blocker evidence" in failure
        for failure in consultive_blocker_failures
    )
    with tempfile.TemporaryDirectory() as directory:
        run_dir = Path(directory)
        blocked_manifest = current.replace(
            "<status>completed</status>", "<status>blocked</status>", 1
        )
        blocked_digest = current_digest.replace(
            "<status>completed</status>", "<status>blocked</status>", 1
        )
        (run_dir / "agentic-run-manifest.xml").write_text(
            blocked_manifest, encoding="utf-8"
        )
        (run_dir / "agentic-run-digest.xml").write_text(
            blocked_digest, encoding="utf-8"
        )
        (run_dir / "consultive-review.xml").write_text(
            f"""<?xml version="1.0"?><agent_session_evidence><identity><handoff_id>{review_handoff_id}</handoff_id></identity><blockers><blocker>raw reviewer blocker</blocker></blockers><validators><validator><status>failed</status></validator></validators></agent_session_evidence>""",
            encoding="utf-8",
        )
        separated_blocker_failures = validate_run_dir(run_dir)
        assert any(
            "outer blocked status lacks non-consultive blocker evidence" in failure
            for failure in separated_blocker_failures
        )
        (run_dir / "real-blocker.xml").write_text(
            """<?xml version="1.0"?><runtime_validation><identity><handoff_id>runtime-validator</handoff_id></identity><blockers><blocker>real validator blocker</blocker></blockers></runtime_validation>""",
            encoding="utf-8",
        )
        unrecognized_blocker_failures = validate_run_dir(run_dir)
        assert any(
            "outer blocked status lacks non-consultive blocker evidence" in failure
            for failure in unrecognized_blocker_failures
        )
        (run_dir / "real-blocker.xml").write_text(
            """<?xml version="1.0"?><runtime_validation><identity><handoff_id>runtime-validator</handoff_id></identity><validators><validator><status>failed</status></validator></validators></runtime_validation>""",
            encoding="utf-8",
        )
        unrecognized_validator_failures = validate_run_dir(run_dir)
        assert any(
            "outer blocked status lacks non-consultive blocker evidence" in failure
            for failure in unrecognized_validator_failures
        )
        injected_wtr_manifest = blocked_manifest.replace(
            "</write_test_review>",
            "<injected><validators><validator><status>failed</status></validator></validators></injected></write_test_review>",
        )
        (run_dir / "agentic-run-manifest.xml").write_text(
            injected_wtr_manifest, encoding="utf-8"
        )
        injected_wtr_failures = validate_run_dir(run_dir)
        assert any(
            "outer blocked status lacks non-consultive blocker evidence" in failure
            for failure in injected_wtr_failures
        )
        injected_unknown_manifest = blocked_manifest.replace(
            "</agentic_run_manifest>",
            "<unknown><blockers><blocker>fabricated blocker</blocker></blockers></unknown></agentic_run_manifest>",
        )
        (run_dir / "agentic-run-manifest.xml").write_text(
            injected_unknown_manifest, encoding="utf-8"
        )
        injected_unknown_failures = validate_run_dir(run_dir)
        assert any(
            "outer blocked status lacks non-consultive blocker evidence" in failure
            for failure in injected_unknown_failures
        )
        recognized_validator_manifest = blocked_manifest.replace(
            "</agentic_run_manifest>",
            "<validators><validator><status>failed</status></validator></validators></agentic_run_manifest>",
        )
        (run_dir / "agentic-run-manifest.xml").write_text(
            recognized_validator_manifest, encoding="utf-8"
        )
        independent_validator_failures = validate_run_dir(run_dir)
        assert not any(
            "outer blocked status lacks non-consultive blocker evidence" in failure
            for failure in independent_validator_failures
        )
    scheduled = (
        current.replace("completed-clean", "scheduled")
        .replace(f"<review_handoff_id>{review_handoff_id}</review_handoff_id>", "<review_handoff_id/>")
        .replace("<review_agent_run_id>review-run-1</review_agent_run_id>", "<review_agent_run_id/>")
        .replace("<evidence_ref>evidence/review.xml</evidence_ref>", "<evidence_ref/>")
    )
    dispatched = current.replace("completed-clean", "dispatched").replace(
        "<evidence_ref>evidence/review.xml</evidence_ref>", "<evidence_ref/>"
    )
    negative_cases = {
        "effective": current.replace("<effective_frequency>plano", "<effective_frequency>fase"),
        "lineage": current.replace(f"<review_handoff_id>{review_handoff_id}", "<review_handoff_id>"),
        "consultive": current.replace("<execution_status_effect>none", "<execution_status_effect>blocked"),
        "coverage": current.replace("<handoff_id>write-1</handoff_id>", ""),
        "policy-conflict": current.replace("<state_errors/>", "<state_errors><state_error code=\"policy-conflict\"/></state_errors>"),
        "default-provenance": current.replace("<provenance>explicit", "<provenance>default"),
        "outer-blocked": current.replace("<status>completed", "<status>blocked", 1),
        "nondeterministic-review-handoff": current.replace(review_handoff_id, "review-handoff-v1:" + "d" * 64),
        "unsorted-coverage": current.replace("<handoff_id>write-1</handoff_id>", "<handoff_id>write-1</handoff_id><handoff_id>write-0</handoff_id>"),
        "clean-missing-evidence": current.replace("<evidence_ref>evidence/review.xml</evidence_ref>", "<evidence_ref/>", 1),
        "unavailable-with-dispatch": current.replace("completed-clean", "skipped-agent-unavailable"),
        "executor-status": current.replace(
            implementation_handoff,
            implementation_handoff.replace(
                "<status>awaiting-manual-qa</status>", "<status>BANANA</status>"
            ),
        ),
        "duplicate-implementation-handoff": current.replace(
            implementation_handoff, implementation_handoff + implementation_handoff
        ),
        "wrong-implementation-command": current.replace(
            "<command>loki-implement-feature</command>",
            "<command>loki-other</command>",
        ),
        "non-markdown-analysis": current.replace(
            "<analysis_file>analise/technical-analysis.md</analysis_file>",
            "<analysis_file>analise/technical-analysis.txt</analysis_file>",
        ),
        "dispatched-with-returned-state": current.replace(
            implementation_handoff,
            implementation_handoff.replace(
                "<status>awaiting-manual-qa</status>",
                "<status>dispatched</status>",
            ),
        ),
        "forged-policy-digest": current.replace(policy_digest, "sha256:" + "f" * 64),
        "forged-coverage-digest": current.replace(coverage_digest, "sha256:" + "f" * 64),
        "forged-checkpoint-id": current.replace(
            checkpoint_id, "review-checkpoint-v1:" + "f" * 64
        ),
        "absolute-coverage-path": current.replace(
            "<path>target.md</path>", "<path>/tmp/x</path>"
        ),
        "parent-coverage-path": current.replace(
            "<path>target.md</path>", "<path>../x</path>"
        ),
        "coverage-extra-field": current.replace(
            "<path>target.md</path>", "<path>target.md</path><unexpected>evil</unexpected>"
        ),
        "raw-unknown-terminal": current.replace(
            "<review_agent_raw_status>clean</review_agent_raw_status>",
            "<review_agent_raw_status>BANANA</review_agent_raw_status>",
        ),
        "duplicate-policy-field": current.replace(
            f"<policy_digest>{policy_digest}</policy_digest>",
            f"<policy_digest>{policy_digest}</policy_digest><policy_digest>{policy_digest}</policy_digest>",
            1,
        ),
        "duplicate-checkpoint-status": current.replace(
            "<status>completed-clean</status>",
            "<status>completed-clean</status><status>failed</status>",
            1,
        ),
        "outer-running": current.replace(
            "<run><run_id>run-self-test</run_id><status>completed</status>",
            "<run><run_id>run-self-test</run_id><status>running</status>",
        ),
        "outer-draft": current.replace(
            "<run><run_id>run-self-test</run_id><status>completed</status>",
            "<run><run_id>run-self-test</run_id><status>draft</status>",
        ),
        "outer-pending-human": current.replace(
            "<run><run_id>run-self-test</run_id><status>completed</status>",
            "<run><run_id>run-self-test</run_id><status>pending-human-validation</status>",
        ),
        "missing-manual-qa-handoff": current.replace(manual_qa_handoff, ""),
        "duplicate-manual-qa-handoff": current.replace(
            manual_qa_handoff, manual_qa_handoff + manual_qa_handoff
        ),
        "superseded-manual-qa-schema": current.replace(
            "<schema_version>2</schema_version>",
            "<schema_version>1</schema_version>",
            1,
        ),
        "manual-qa-extra-key": current.replace(
            "</manual_qa_handoff>", "<handoff_digest>sha256:evil</handoff_digest></manual_qa_handoff>", 1
        ),
        "manual-qa-missing-automatic-evidence-refs": current.replace(
            "<automatic_evidence_refs><ref>evidence/terminal-1.json</ref><ref>evidence/terminal-2.json</ref></automatic_evidence_refs>",
            "",
            1,
        ),
        "manual-qa-missing-task-refs": current.replace(
            "<task_refs><ref>tasks.md#task-1</ref><ref>tasks.md#task-2</ref></task_refs>",
            "",
            1,
        ),
        "manual-qa-missing-acceptance-criterion-refs": current.replace(
            "<acceptance_criterion_refs><ref>tasks.md#ac-1</ref><ref>tasks.md#ac-2</ref></acceptance_criterion_refs>",
            "",
            1,
        ),
        "manual-qa-missing-gate-refs": current.replace(
            "<gate_refs><ref>tasks.md#gate-1</ref><ref>tasks.md#gate-2</ref></gate_refs>",
            "",
            1,
        ),
        "manual-qa-missing-changed-target-refs": current.replace(
            "<changed_target_refs><ref>src/one.py</ref><ref>src/two.py</ref></changed_target_refs>",
            "",
            1,
        ),
        "manual-qa-wrong-run": current.replace(manual_run_id, "run-untyped", 1),
        "manual-qa-wrong-execution": current.replace(
            manual_execution_id, "execution-untyped", 1
        ),
        "manual-qa-wrong-plan": current.replace(
            "<plan_directory>implementation</plan_directory>",
            "<plan_directory>other-plan</plan_directory>",
            1,
        ),
        "manual-qa-wrong-result-anchor": current.replace(
            "implementation/builds/manual-qa/result.json",
            "implementation/builds/manual-qa/other.json",
            1,
        ),
        "manual-qa-wrong-attestation-anchor": current.replace(
            f"implementation/interaction/manual-qa/{manual_run_id}/attestation.json",
            "implementation/interaction/manual-qa/wrong/attestation.json",
            1,
        ),
        "manual-qa-ready-with-reason": current.replace(
            "<reason/></manual_qa_handoff>",
            "<reason>must be null</reason></manual_qa_handoff>",
            1,
        ),
        "manual-qa-ready-without-evidence": current.replace(
            "<automatic_evidence_refs><ref>evidence/terminal-1.json</ref><ref>evidence/terminal-2.json</ref></automatic_evidence_refs>",
            "<automatic_evidence_refs/>",
            1,
        ),
        "manual-qa-not-required-without-reason": current.replace(
            "<status>ready-for-manual-qa</status>",
            "<status>manual-qa-not-required</status>",
            1,
        ),
        "scheduled-with-handoff": scheduled.replace("<review_handoff_id/>", f"<review_handoff_id>{review_handoff_id}</review_handoff_id>"),
        "scheduled-with-run": scheduled.replace("<review_agent_run_id/>", "<review_agent_run_id>review-run-1</review_agent_run_id>"),
        "scheduled-with-evidence": scheduled.replace("<evidence_ref/>", "<evidence_ref>evidence/review.xml</evidence_ref>"),
        "scheduled-with-reason": scheduled.replace("<reason/>", "<reason>premature</reason>"),
        "dispatched-with-evidence": dispatched.replace("<evidence_ref/>", "<evidence_ref>evidence/review.xml</evidence_ref>"),
        "dispatched-with-reason": dispatched.replace("<reason/>", "<reason>premature</reason>"),
    }
    for name, source in negative_cases.items():
        failures = validate_fixture(source)
        assert failures, f"negative fixture accepted: {name}"
    drift_digest = current_digest.replace(
        "implementation/builds/manual-qa/result.json",
        "implementation/builds/manual-qa/drift.json",
        1,
    )
    drift_failures = validate_fixture(current, drift_digest)
    assert any(
        "manifest and digest manual_qa_handoff projections differ" in failure
        for failure in drift_failures
    )
    ordered_array_drifts = {
        "automatic_evidence_refs": (
            "<automatic_evidence_refs><ref>evidence/terminal-1.json</ref><ref>evidence/terminal-2.json</ref></automatic_evidence_refs>",
            "<automatic_evidence_refs><ref>evidence/terminal-2.json</ref><ref>evidence/terminal-1.json</ref></automatic_evidence_refs>",
        ),
        "task_refs": (
            "<task_refs><ref>tasks.md#task-1</ref><ref>tasks.md#task-2</ref></task_refs>",
            "<task_refs><ref>tasks.md#task-2</ref><ref>tasks.md#task-1</ref></task_refs>",
        ),
        "acceptance_criterion_refs": (
            "<acceptance_criterion_refs><ref>tasks.md#ac-1</ref><ref>tasks.md#ac-2</ref></acceptance_criterion_refs>",
            "<acceptance_criterion_refs><ref>tasks.md#ac-2</ref><ref>tasks.md#ac-1</ref></acceptance_criterion_refs>",
        ),
        "gate_refs": (
            "<gate_refs><ref>tasks.md#gate-1</ref><ref>tasks.md#gate-2</ref></gate_refs>",
            "<gate_refs><ref>tasks.md#gate-2</ref><ref>tasks.md#gate-1</ref></gate_refs>",
        ),
        "changed_target_refs": (
            "<changed_target_refs><ref>src/one.py</ref><ref>src/two.py</ref></changed_target_refs>",
            "<changed_target_refs><ref>src/two.py</ref><ref>src/one.py</ref></changed_target_refs>",
        ),
    }
    for field, (ordered, reordered) in ordered_array_drifts.items():
        array_drift_failures = validate_fixture(
            current, current_digest.replace(ordered, reordered, 1)
        )
        assert any(
            "manifest and digest manual_qa_handoff projections differ" in failure
            for failure in array_drift_failures
        ), f"manual_qa_handoff array drift accepted: {field}"
    blocked_manual_qa_handoff = manual_qa_fixture_for_status(
        "manual-qa-not-evaluated"
    )
    blocked_manifest = handoff_fixture_for_status("failed").replace(
        manual_qa_handoff, blocked_manual_qa_handoff
    ).replace(
        "<run><run_id>run-self-test</run_id><status>completed</status></run>",
        "<run><run_id>run-self-test</run_id><status>blocked</status></run>",
        1,
    ).replace(
        "</agentic_run_manifest>",
        "<validators><validator><status>failed</status></validator></validators></agentic_run_manifest>",
    )
    blocked_digest = current_digest.replace(
        manual_qa_handoff, blocked_manual_qa_handoff
    ).replace(
        "<digest><run_id>run-self-test</run_id><status>completed</status></digest>",
        "<digest><run_id>run-self-test</run_id><status>blocked</status></digest>",
        1,
    )
    assert validate_fixture(blocked_manifest, blocked_digest) == []
    consultive_only_blocked = current.replace(
        "<status>completed</status>", "<status>blocked</status>", 1
    ).replace(
        "<freshness_signature/>",
        f"<freshness_signature/><handoffs><handoff><handoff_id>{review_handoff_id}</handoff_id><agent_run_id>review-run-1</agent_run_id><evidence_id>review-evidence</evidence_id><evidence_manifest_path>evidence/review.xml</evidence_manifest_path><status>blocked</status></handoff></handoffs>",
    )
    consultive_failures = validate_fixture(consultive_only_blocked)
    assert any(
        "outer blocked status lacks non-consultive blocker evidence" in failure
        for failure in consultive_failures
    )
    print(
        "self-test: passed "
        f"({len(TERMINAL_RECONCILIATION_BY_IMPLEMENTATION_STATUS)} terminal reconciliations "
        f"positive; {reconciliation_negative_count} invalid combinations negative; "
        f"{len(invalid_implementation_statuses)} invalid implementation statuses negative; "
        "canonical schemas positive; legacy/unknown schemas and contract violations negative)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate canonical Loki agentic XML run state."
    )
    parser.add_argument("run_dir", nargs="?", help="Directory containing agentic-run-manifest.xml")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic canonical-contract fixtures")
    args = parser.parse_args()

    if args.self_test:
        try:
            run_self_test()
        except (AssertionError, OSError, ValueError, ET.ParseError) as exc:
            print(f"self-test failed: {exc}", file=sys.stderr)
            return 1
        return 0
    if args.run_dir is None:
        parser.error("run_dir is required unless --self-test is used")

    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        print(f"error: run directory does not exist: {run_dir}", file=sys.stderr)
        return 1

    try:
        failures = validate_run_dir(run_dir)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("agentic run-state validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("agentic run-state validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
