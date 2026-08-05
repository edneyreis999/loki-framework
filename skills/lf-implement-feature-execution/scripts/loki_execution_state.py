#!/usr/bin/env python3
"""Closed current-only execution-state v1 engine and pure renderers.

The file is intentionally standard-library-only and bundle-local.  It owns one
``execution-state.json`` per run.  Callers submit one of the closed typed
operations; no JSON Patch, compatibility reader, projection writer, or repair
path exists here.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping


SCHEMA_VERSION = 1
OPERATIONS = (
    "initialize",
    "start_task_phase",
    "prepare_task_write",
    "abandon_pending_write",
    "block_pending_write",
    "record_dispatch",
    "close_handoff",
    "commit_task_phase",
    "commit_audit",
    "commit_replan_ref",
    "reconcile_cancellation",
    "publish_manual_qa_eligibility",
    "approve_manual_qa",
    "publish_terminal",
)
TERMINAL_RUN_STATUSES = {
    "completed", "completed-with-limitations", "partial", "failed", "cancelled"
}
TASK_STATUSES = {"pending", "running", "passed", "failed", "blocked", "skipped", "cancelled"}
TERMINAL_TASK_STATUSES = {"passed", "failed", "blocked", "skipped", "cancelled"}
PHASE_STATUSES = {"pending", "running", "passed", "failed", "blocked", "cancelled"}
TERMINAL_PHASE_STATUSES = {"passed", "failed", "blocked", "cancelled"}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?[+-]\d{2}:\d{2}$")
MAX_TEXT = 4096


class StateContractError(RuntimeError):
    """Fail-closed contract error with a stable machine-readable code."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(code if not detail else f"{code}: {detail}")


def _require(code: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise StateContractError(code, detail)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def bytes_digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def state_digest(state: Mapping[str, Any]) -> str:
    body = dict(state)
    body.pop("state_digest", None)
    return bytes_digest(canonical_bytes(body))


def _closed(code: str, value: Any, keys: Iterable[str]) -> dict[str, Any]:
    expected = set(keys)
    _require(code, isinstance(value, dict))
    _require(code, set(value) == expected, f"expected={sorted(expected)} actual={sorted(value)}")
    return value


def _list(code: str, value: Any, *, maximum: int, nonempty: bool = False) -> list[Any]:
    _require(code, isinstance(value, list) and len(value) <= maximum)
    _require(code, not nonempty or bool(value))
    return value


def _text(code: str, value: Any, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    _require(code, isinstance(value, str) and len(value) <= MAX_TEXT)
    _require(code, all(ord(ch) >= 32 or ch in "\n\t" for ch in value))
    return value


def _stable_id(code: str, value: Any) -> str:
    _require(code, isinstance(value, str) and ID_RE.fullmatch(value) is not None)
    return value


def _digest(code: str, value: Any, *, absent: bool = False, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if absent and value == "absent":
        return value
    _require(code, isinstance(value, str) and DIGEST_RE.fullmatch(value) is not None)
    return value


def _timestamp(code: str, value: Any, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    _require(code, isinstance(value, str) and RFC3339_RE.fullmatch(value) is not None)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise StateContractError(code, str(exc)) from exc
    _require(code, parsed.tzinfo is not None and parsed.utcoffset() is not None and parsed.isoformat() == value)
    return value


def _ref(code: str, value: Any, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    _require(code, isinstance(value, str) and 0 < len(value) <= 1024)
    _require(code, "\\" not in value and not value.startswith("/") and "\x00" not in value)
    path = PurePosixPath(value)
    _require(code, not any(part in ("", ".", "..") for part in path.parts))
    _require(code, path.as_posix() == value)
    return value


def normalize_relative_path(value: Any) -> str:
    """Return one canonical root-relative POSIX path or fail closed."""
    return _ref("STATE_PATH_INVALID", value)  # type: ignore[return-value]


def classify_pending_targets(observed: Iterable[str]) -> str:
    """Classify a cold-resume product-write snapshot without side effects."""
    values = list(observed)
    _require("PENDING_OBSERVATION_INVALID", bool(values) and all(item in {"before", "desired", "unknown"} for item in values))
    unique = set(values)
    if unique == {"before"}: return "abandon-or-retry"
    if unique == {"desired"}: return "validate-and-commit"
    return "block_pending_write"


def _unique(code: str, values: Iterable[Any], key: Callable[[Any], Any] = lambda item: item) -> None:
    observed = [key(item) for item in values]
    _require(code, len(observed) == len(set(observed)))


def _refs(code: str, value: Any) -> list[str]:
    values = _list(code, value, maximum=64)
    for item in values:
        _ref(code, item)
    _unique(code, values)
    return values


def _nullable_limitation(code: str, value: Any) -> None:
    if value is None:
        return
    item = _closed(code, value, {"limitation_id", "fact", "effect", "evidence_refs"})
    _stable_id(code, item["limitation_id"]); _text(code, item["fact"]); _text(code, item["effect"])
    _refs(code, item["evidence_refs"])


def _observed_value(code: str, value: Any, *, pending: bool = False) -> None:
    keys = {"status", "value", "reason"}
    item = _closed(code, value, keys)
    allowed = {"observed", "unavailable"} | ({"pending"} if pending else set())
    _require(code, item["status"] in allowed)
    if item["status"] == "observed":
        _timestamp(code, item["value"]); _require(code, item["reason"] is None)
    elif item["status"] == "pending":
        _require(code, item["value"] is None and item["reason"] is None)
    else:
        _require(code, item["value"] is None); _text(code, item["reason"])


def _assessment(code: str, value: Any, *, kind: str) -> None:
    item = _closed(code, value, {"assessment", "reason", "items"})
    _require(code, item["assessment"] in {"present", "none-confirmed", "unavailable"})
    if item["assessment"] == "unavailable": _text(code, item["reason"])
    else: _require(code, item["reason"] is None)
    items = _list(code, item["items"], maximum=512)
    id_key = "blocker_id" if kind == "blocker" else "risk_id"
    status_set = {"open", "resolved"} if kind == "blocker" else {"current", "accepted", "mitigated"}
    for record in items:
        row = _closed(code, record, {id_key, "scope_ref", "status", "fact", "owner", "gate_ref", "evidence_refs"})
        _stable_id(code, row[id_key]); _ref(code, row["scope_ref"]); _require(code, row["status"] in status_set)
        _text(code, row["fact"]); _text(code, row["owner"], nullable=True); _ref(code, row["gate_ref"], nullable=True)
        _refs(code, row["evidence_refs"])
    _unique(code, items, lambda row: row[id_key])
    if item["assessment"] == "none-confirmed": _require(code, not items)
    if item["assessment"] == "present": _require(code, bool(items))


STATE_KEYS = {
    "schema_version", "identity", "plan_revision", "revision", "state_digest", "status", "updated_at",
    "last_transition", "last_compact_transition", "pending_transition", "execution_summary", "tasks", "phases",
    "handoffs", "gates", "audit_boundaries", "manual_qa", "human_decisions", "effort_observations",
    "material_frictions", "blockers", "residual_risks", "next_steps", "optional_artifacts",
}


def validate_state(value: Any, *, verify_digest: bool = True) -> dict[str, Any]:
    state = _closed("STATE_SHAPE_INVALID", value, STATE_KEYS)
    _require("STATE_SCHEMA_INVALID", state["schema_version"] == SCHEMA_VERSION)
    identity = _closed("IDENTITY_SHAPE_INVALID", state["identity"], {
        "run_id", "execution_id", "command_identity", "demand_ref", "demand_digest",
        "analysis_ref", "analysis_digest", "audit_configuration",
    })
    _stable_id("RUN_ID_INVALID", identity["run_id"]); _stable_id("EXECUTION_ID_INVALID", identity["execution_id"])
    command = _closed("COMMAND_IDENTITY_INVALID", identity["command_identity"], {"command", "adapter"})
    _require("COMMAND_IDENTITY_INVALID", command["command"] == "loki-implement-feature" and command["adapter"] in {"codex", "claude-code", "other"})
    _ref("DEMAND_REF_INVALID", identity["demand_ref"]); _digest("DEMAND_DIGEST_INVALID", identity["demand_digest"])
    _ref("ANALYSIS_REF_INVALID", identity["analysis_ref"]); _digest("ANALYSIS_DIGEST_INVALID", identity["analysis_digest"])
    audit = _closed("AUDIT_CONFIGURATION_INVALID", identity["audit_configuration"], {"frequency", "auditor_source", "policy_ref"})
    _require("AUDIT_FREQUENCY_INVALID", audit["frequency"] in {"task", "phase", "plan"}); _ref("AUDITOR_SOURCE_INVALID", audit["auditor_source"]); _ref("AUDIT_POLICY_REF_INVALID", audit["policy_ref"])
    plan = _closed("PLAN_REVISION_INVALID", state["plan_revision"], {"plan_revision_ref", "plan_revision_digest"})
    _ref("PLAN_REVISION_REF_INVALID", plan["plan_revision_ref"]); _digest("PLAN_REVISION_DIGEST_INVALID", plan["plan_revision_digest"])
    _require("REVISION_INVALID", isinstance(state["revision"], int) and not isinstance(state["revision"], bool) and state["revision"] >= 1)
    _digest("STATE_DIGEST_INVALID", state["state_digest"])
    _require("STATUS_INVALID", state["status"] in {"running", "blocked", "awaiting-manual-qa"} | TERMINAL_RUN_STATUSES)
    _timestamp("UPDATED_AT_INVALID", state["updated_at"])
    transition = _closed("LAST_TRANSITION_INVALID", state["last_transition"], {"transition_id", "kind", "ref", "outcome", "occurred_at"})
    _stable_id("LAST_TRANSITION_ID_INVALID", transition["transition_id"]); _require("LAST_TRANSITION_KIND_INVALID", transition["kind"] in OPERATIONS)
    _ref("LAST_TRANSITION_REF_INVALID", transition["ref"]); _require("LAST_TRANSITION_OUTCOME_INVALID", transition["outcome"] == "committed"); _timestamp("LAST_TRANSITION_TIME_INVALID", transition["occurred_at"])
    compact = state["last_compact_transition"]
    if compact is not None:
        compact = _closed("LAST_COMPACT_INVALID", compact, {"transition_id", "kind", "ref", "result", "occurred_at"})
        _stable_id("LAST_COMPACT_INVALID", compact["transition_id"]); _require("LAST_COMPACT_INVALID", compact["kind"] == "commit_task_phase")
        _ref("LAST_COMPACT_INVALID", compact["ref"]); _require("LAST_COMPACT_INVALID", compact["result"] in TERMINAL_TASK_STATUSES); _timestamp("LAST_COMPACT_INVALID", compact["occurred_at"])
    pending = state["pending_transition"]
    if pending is not None:
        pending = _closed("PENDING_TRANSITION_INVALID", pending, {"transition_id", "operation", "task_ref", "targets", "status"})
        _stable_id("PENDING_TRANSITION_INVALID", pending["transition_id"]); _require("PENDING_TRANSITION_INVALID", pending["operation"] == "prepare_task_write")
        _ref("PENDING_TRANSITION_INVALID", pending["task_ref"]); _require("PENDING_TRANSITION_INVALID", pending["status"] in {"prepared", "blocked"})
        targets = _list("PENDING_TARGETS_INVALID", pending["targets"], maximum=64, nonempty=True)
        for target in targets:
            target = _closed("PENDING_TARGET_INVALID", target, {"target_ref", "before_digest", "desired_digest"})
            _ref("PENDING_TARGET_INVALID", target["target_ref"]); _digest("PENDING_TARGET_INVALID", target["before_digest"], absent=True); _digest("PENDING_TARGET_INVALID", target["desired_digest"], absent=True)
        _unique("PENDING_TARGET_DUPLICATED", targets, lambda item: item["target_ref"])
    summary = _closed("EXECUTION_SUMMARY_INVALID", state["execution_summary"], {"implemented_outcomes", "terminal_reason"})
    outcomes = _list("IMPLEMENTED_OUTCOMES_INVALID", summary["implemented_outcomes"], maximum=512)
    for row in outcomes:
        row = _closed("IMPLEMENTED_OUTCOME_INVALID", row, {"outcome_ref", "summary", "source_refs"}); _ref("IMPLEMENTED_OUTCOME_INVALID", row["outcome_ref"]); _text("IMPLEMENTED_OUTCOME_INVALID", row["summary"]); _refs("IMPLEMENTED_OUTCOME_INVALID", row["source_refs"])
    _unique("IMPLEMENTED_OUTCOME_DUPLICATED", outcomes, lambda row: row["outcome_ref"])
    terminal_reason = summary["terminal_reason"]
    if terminal_reason is not None:
        terminal_reason = _closed("TERMINAL_REASON_INVALID", terminal_reason, {"status", "summary", "reason"})
        _require("TERMINAL_REASON_INVALID", terminal_reason["status"] in {"observed", "unavailable"}); _text("TERMINAL_REASON_INVALID", terminal_reason["summary"], nullable=True)
        if terminal_reason["status"] == "unavailable": _text("TERMINAL_REASON_INVALID", terminal_reason["reason"])
        else: _require("TERMINAL_REASON_INVALID", terminal_reason["reason"] is None)

    tasks = _list("TASKS_INVALID", state["tasks"], maximum=512, nonempty=True)
    for task in tasks:
        task = _closed("TASK_INVALID", task, {"task_ref", "phase_ref", "required", "status", "transition_id", "result", "transitioned_at", "validation", "target_digests"})
        _ref("TASK_INVALID", task["task_ref"]); _ref("TASK_INVALID", task["phase_ref"]); _require("TASK_INVALID", isinstance(task["required"], bool)); _require("TASK_INVALID", task["status"] in TASK_STATUSES)
        if task["status"] == "pending": _require("TASK_PENDING_INVALID", task["transition_id"] is None and task["result"] is None and task["transitioned_at"] is None)
        elif task["status"] == "running": _stable_id("TASK_RUNNING_INVALID", task["transition_id"]); _require("TASK_RUNNING_INVALID", task["result"] is None); _timestamp("TASK_RUNNING_INVALID", task["transitioned_at"])
        else:
            _stable_id("TASK_TERMINAL_INVALID", task["transition_id"]); _timestamp("TASK_TERMINAL_INVALID", task["transitioned_at"])
            result = _closed("TASK_RESULT_INVALID", task["result"], {"summary", "responsible", "delivery_refs"}); _text("TASK_RESULT_INVALID", result["summary"]); _text("TASK_RESULT_INVALID", result["responsible"]); _refs("TASK_RESULT_INVALID", result["delivery_refs"])
        validation = _closed("TASK_VALIDATION_INVALID", task["validation"], {"status", "validator_ref", "evidence_refs", "limitation"})
        _require("TASK_VALIDATION_INVALID", validation["status"] in {"pending", "passed", "failed", "unavailable"}); _ref("TASK_VALIDATION_INVALID", validation["validator_ref"]); _refs("TASK_VALIDATION_INVALID", validation["evidence_refs"]); _nullable_limitation("TASK_VALIDATION_INVALID", validation["limitation"])
        if task["status"] == "passed": _require("PASSED_TASK_VALIDATION_INVALID", validation["status"] == "passed")
        if validation["status"] == "unavailable": _require("UNAVAILABLE_VALIDATION_LIMITATION_MISSING", validation["limitation"] is not None)
        digests = _list("TASK_TARGET_DIGESTS_INVALID", task["target_digests"], maximum=64)
        for row in digests:
            row = _closed("TASK_TARGET_DIGEST_INVALID", row, {"target_ref", "digest"}); _ref("TASK_TARGET_DIGEST_INVALID", row["target_ref"]); _digest("TASK_TARGET_DIGEST_INVALID", row["digest"], absent=True)
        _unique("TASK_TARGET_DIGEST_DUPLICATED", digests, lambda row: row["target_ref"])
    _unique("TASK_REF_DUPLICATED", tasks, lambda row: row["task_ref"])
    task_refs = {row["task_ref"] for row in tasks}

    phases = _list("PHASES_INVALID", state["phases"], maximum=128, nonempty=True)
    for phase in phases:
        phase = _closed("PHASE_INVALID", phase, {"phase_ref", "status", "transition_id", "result", "transitioned_at", "evidence_refs"})
        _ref("PHASE_INVALID", phase["phase_ref"]); _require("PHASE_INVALID", phase["status"] in PHASE_STATUSES); _refs("PHASE_INVALID", phase["evidence_refs"])
        if phase["status"] == "pending": _require("PHASE_PENDING_INVALID", phase["transition_id"] is None and phase["result"] is None and phase["transitioned_at"] is None)
        elif phase["status"] == "running": _stable_id("PHASE_RUNNING_INVALID", phase["transition_id"]); _require("PHASE_RUNNING_INVALID", phase["result"] is None); _timestamp("PHASE_RUNNING_INVALID", phase["transitioned_at"])
        else:
            _stable_id("PHASE_TERMINAL_INVALID", phase["transition_id"]); _timestamp("PHASE_TERMINAL_INVALID", phase["transitioned_at"])
            result = _closed("PHASE_RESULT_INVALID", phase["result"], {"summary"}); _text("PHASE_RESULT_INVALID", result["summary"])
    _unique("PHASE_REF_DUPLICATED", phases, lambda row: row["phase_ref"])
    phase_refs = {row["phase_ref"] for row in phases}; _require("TASK_PHASE_UNKNOWN", all(row["phase_ref"] in phase_refs for row in tasks))

    handoffs = _list("HANDOFFS_INVALID", state["handoffs"], maximum=2048)
    for handoff in handoffs:
        handoff = _closed("HANDOFF_INVALID", handoff, {"handoff_id", "task_ref", "phase_ref", "agent_label", "objective", "status", "called_at", "delivered_at", "delivery", "result", "evidence_refs"})
        _stable_id("HANDOFF_INVALID", handoff["handoff_id"]); _ref("HANDOFF_INVALID", handoff["task_ref"], nullable=True); _ref("HANDOFF_INVALID", handoff["phase_ref"]); _text("HANDOFF_INVALID", handoff["agent_label"]); _text("HANDOFF_INVALID", handoff["objective"])
        _require("HANDOFF_TASK_UNKNOWN", handoff["task_ref"] is None or handoff["task_ref"] in task_refs)
        _require("HANDOFF_INVALID", handoff["status"] in {"open", "delivered", "failed", "cancelled", "timed-out", "unknown"}); _observed_value("HANDOFF_CALLED_INVALID", handoff["called_at"]); _observed_value("HANDOFF_DELIVERED_INVALID", handoff["delivered_at"], pending=True)
        delivery = _closed("HANDOFF_DELIVERY_INVALID", handoff["delivery"], {"status", "summary", "reason"}); _require("HANDOFF_DELIVERY_INVALID", delivery["status"] in {"pending", "delivered", "not-delivered", "unavailable"}); _text("HANDOFF_DELIVERY_INVALID", delivery["summary"], nullable=True); _text("HANDOFF_DELIVERY_INVALID", delivery["reason"], nullable=True)
        result = _closed("HANDOFF_RESULT_INVALID", handoff["result"], {"status", "summary"}); _require("HANDOFF_RESULT_INVALID", result["status"] in {"pending", "passed", "failed", "blocked", "cancelled", "timed-out", "unknown"}); _text("HANDOFF_RESULT_INVALID", result["summary"], nullable=True); _refs("HANDOFF_INVALID", handoff["evidence_refs"])
        if handoff["status"] == "open": _require("HANDOFF_OPEN_INVALID", handoff["delivered_at"]["status"] == "pending" and delivery["status"] == "pending" and result["status"] == "pending")
        else:
            _require("HANDOFF_TERMINAL_INVALID", handoff["delivered_at"]["status"] != "pending" and delivery["status"] != "pending" and result["status"] != "pending")
            if handoff["called_at"]["status"] == "observed" and handoff["delivered_at"]["status"] == "observed":
                called = datetime.fromisoformat(handoff["called_at"]["value"])
                delivered = datetime.fromisoformat(handoff["delivered_at"]["value"])
                _require("HANDOFF_NEGATIVE_CHRONOLOGY", delivered >= called, handoff["handoff_id"])
    _unique("HANDOFF_ID_DUPLICATED", handoffs, lambda row: row["handoff_id"])

    gates = _list("GATES_INVALID", state["gates"], maximum=512)
    for gate in gates:
        gate = _closed("GATE_INVALID", gate, {"gate_ref", "kind", "status", "transition_id", "evidence_refs", "limitation"}); _ref("GATE_INVALID", gate["gate_ref"]); _require("GATE_INVALID", gate["kind"] in {"automatic", "human-validation"}); _require("GATE_INVALID", gate["status"] in {"pending", "passed", "failed", "not-applicable", "unavailable"}); _refs("GATE_INVALID", gate["evidence_refs"]); _nullable_limitation("GATE_INVALID", gate["limitation"])
        if gate["status"] == "pending": _require("GATE_INVALID", gate["transition_id"] is None)
        else: _stable_id("GATE_INVALID", gate["transition_id"])
    _unique("GATE_REF_DUPLICATED", gates, lambda row: row["gate_ref"])

    boundaries = _list("AUDIT_BOUNDARIES_INVALID", state["audit_boundaries"], maximum=512)
    for boundary in boundaries:
        boundary = _closed("AUDIT_BOUNDARY_INVALID", boundary, {"boundary_ref", "status", "auditor_identity", "findings", "evidence_refs", "transition_id", "transitioned_at"}); _ref("AUDIT_BOUNDARY_INVALID", boundary["boundary_ref"]); _require("AUDIT_BOUNDARY_INVALID", boundary["status"] in {"pending", "approved", "rejected", "not-applicable", "unavailable"}); _text("AUDIT_BOUNDARY_INVALID", boundary["auditor_identity"], nullable=True); _refs("AUDIT_BOUNDARY_INVALID", boundary["evidence_refs"])
        findings = _list("AUDIT_FINDINGS_INVALID", boundary["findings"], maximum=128)
        for finding in findings:
            finding = _closed("AUDIT_FINDING_INVALID", finding, {"finding_id", "severity", "fact", "target_ref", "evidence_refs"}); _stable_id("AUDIT_FINDING_INVALID", finding["finding_id"]); _require("AUDIT_FINDING_INVALID", finding["severity"] in {"blocking", "non-blocking"}); _text("AUDIT_FINDING_INVALID", finding["fact"]); _ref("AUDIT_FINDING_INVALID", finding["target_ref"], nullable=True); _refs("AUDIT_FINDING_INVALID", finding["evidence_refs"])
        _unique("AUDIT_FINDING_DUPLICATED", findings, lambda row: row["finding_id"])
        if boundary["status"] == "pending": _require("AUDIT_BOUNDARY_PENDING_INVALID", boundary["auditor_identity"] is None and not findings and boundary["transition_id"] is None and boundary["transitioned_at"] is None)
        else:
            _stable_id("AUDIT_BOUNDARY_TERMINAL_INVALID", boundary["transition_id"]); _timestamp("AUDIT_BOUNDARY_TERMINAL_INVALID", boundary["transitioned_at"])
            if boundary["status"] in {"approved", "rejected"}: _text("AUDIT_IDENTITY_MISSING", boundary["auditor_identity"])
    _unique("AUDIT_BOUNDARY_DUPLICATED", boundaries, lambda row: row["boundary_ref"])

    qa = _closed("MANUAL_QA_INVALID", state["manual_qa"], {"applicability", "eligibility_status", "eligibility_basis_digest", "eligible_revision", "applicable_gate_refs", "limitation_refs", "transitioned_at"})
    _require("MANUAL_QA_INVALID", qa["applicability"] in {"pending", "required", "not-required"}); _require("MANUAL_QA_INVALID", qa["eligibility_status"] in {"pending", "eligible", "not-applicable"}); _refs("MANUAL_QA_INVALID", qa["applicable_gate_refs"]); _refs("MANUAL_QA_INVALID", qa["limitation_refs"]); _digest("MANUAL_QA_INVALID", qa["eligibility_basis_digest"], nullable=True); _timestamp("MANUAL_QA_INVALID", qa["transitioned_at"], nullable=True)
    if qa["eligibility_status"] == "eligible": _require("MANUAL_QA_ELIGIBILITY_INVALID", qa["applicability"] == "required" and isinstance(qa["eligible_revision"], int) and qa["eligible_revision"] >= 1 and qa["eligibility_basis_digest"] is not None and qa["transitioned_at"] is not None)
    elif qa["eligibility_status"] == "pending": _require("MANUAL_QA_PENDING_INVALID", qa["applicability"] == "pending" and qa["eligibility_basis_digest"] is None and qa["eligible_revision"] is None and qa["transitioned_at"] is None)
    else: _require("MANUAL_QA_NOT_APPLICABLE_INVALID", qa["applicability"] == "not-required" and qa["eligibility_basis_digest"] is None and qa["eligible_revision"] is None and qa["transitioned_at"] is not None)
    if state["status"] == "awaiting-manual-qa": _require("AWAITING_QA_BASIS_INVALID", qa["eligibility_status"] == "eligible")

    decisions = _list("HUMAN_DECISIONS_INVALID", state["human_decisions"], maximum=64)
    for row in decisions:
        row = _closed("HUMAN_DECISION_INVALID", row, {"decision_id", "kind", "decision", "basis_digest", "applicable_gate_refs", "limitation_refs", "decided_at"}); _stable_id("HUMAN_DECISION_INVALID", row["decision_id"]); _require("HUMAN_DECISION_INVALID", row["kind"] == "manual-qa" and row["decision"] == "approved"); _digest("HUMAN_DECISION_INVALID", row["basis_digest"]); _refs("HUMAN_DECISION_INVALID", row["applicable_gate_refs"]); _refs("HUMAN_DECISION_INVALID", row["limitation_refs"]); _timestamp("HUMAN_DECISION_INVALID", row["decided_at"])
    _unique("HUMAN_DECISION_DUPLICATED", decisions, lambda row: row["decision_id"])

    effort = _list("EFFORT_OBSERVATIONS_INVALID", state["effort_observations"], maximum=512)
    for row in effort:
        row = _closed("EFFORT_OBSERVATION_INVALID", row, {"observation_id", "category", "status", "value", "unit", "reason", "evidence_refs"}); _stable_id("EFFORT_OBSERVATION_INVALID", row["observation_id"]); _require("EFFORT_OBSERVATION_INVALID", row["category"] in {"writing", "correction", "audit-interval"} and row["status"] in {"observed", "unavailable"}); _refs("EFFORT_OBSERVATION_INVALID", row["evidence_refs"])
        if row["status"] == "observed": _require("EFFORT_OBSERVATION_INVALID", isinstance(row["value"], int) and not isinstance(row["value"], bool) and row["value"] >= 0 and row["unit"] == "milliseconds" and row["reason"] is None)
        else: _require("EFFORT_OBSERVATION_INVALID", row["value"] is None and row["unit"] is None); _text("EFFORT_OBSERVATION_INVALID", row["reason"])
    _unique("EFFORT_OBSERVATION_DUPLICATED", effort, lambda row: row["observation_id"])

    frictions = _list("MATERIAL_FRICTIONS_INVALID", state["material_frictions"], maximum=512)
    for row in frictions:
        row = _closed("MATERIAL_FRICTION_INVALID", row, {"friction_id", "fact", "inference", "preventive_action", "scope_ref", "evidence_refs"}); _stable_id("MATERIAL_FRICTION_INVALID", row["friction_id"]); _text("MATERIAL_FRICTION_INVALID", row["fact"]); _text("MATERIAL_FRICTION_INVALID", row["inference"]); _text("MATERIAL_FRICTION_INVALID", row["preventive_action"]); _ref("MATERIAL_FRICTION_INVALID", row["scope_ref"]); _refs("MATERIAL_FRICTION_INVALID", row["evidence_refs"])
    _unique("MATERIAL_FRICTION_DUPLICATED", frictions, lambda row: row["friction_id"])
    _assessment("BLOCKERS_INVALID", state["blockers"], kind="blocker"); _assessment("RISKS_INVALID", state["residual_risks"], kind="risk")
    steps = _list("NEXT_STEPS_INVALID", state["next_steps"], maximum=512)
    for row in steps:
        row = _closed("NEXT_STEP_INVALID", row, {"next_step_id", "scope_ref", "action", "owner", "gate_ref", "status"}); _stable_id("NEXT_STEP_INVALID", row["next_step_id"]); _ref("NEXT_STEP_INVALID", row["scope_ref"]); _text("NEXT_STEP_INVALID", row["action"]); _text("NEXT_STEP_INVALID", row["owner"]); _ref("NEXT_STEP_INVALID", row["gate_ref"], nullable=True); _require("NEXT_STEP_INVALID", row["status"] in {"pending", "completed", "not-applicable"})
    _unique("NEXT_STEP_DUPLICATED", steps, lambda row: row["next_step_id"])
    artifacts = _list("OPTIONAL_ARTIFACTS_INVALID", state["optional_artifacts"], maximum=32)
    for row in artifacts:
        row = _closed("OPTIONAL_ARTIFACT_INVALID", row, {"artifact_id", "kind", "ref", "digest", "consumer", "authority", "retention_basis"}); _stable_id("OPTIONAL_ARTIFACT_INVALID", row["artifact_id"]); _require("OPTIONAL_ARTIFACT_INVALID", row["kind"] in {"detailed-metrics", "session-evidence", "execution-knowledge", "retrospective"}); _ref("OPTIONAL_ARTIFACT_INVALID", row["ref"]); _digest("OPTIONAL_ARTIFACT_INVALID", row["digest"]); _text("OPTIONAL_ARTIFACT_INVALID", row["consumer"]); _text("OPTIONAL_ARTIFACT_INVALID", row["authority"]); _text("OPTIONAL_ARTIFACT_INVALID", row["retention_basis"])
    _unique("OPTIONAL_ARTIFACT_DUPLICATED", artifacts, lambda row: row["artifact_id"])
    if state["status"] == "blocked": _require("BLOCKED_WITHOUT_BLOCKER", any(row["status"] == "open" for row in state["blockers"]["items"]))
    if state["status"] in TERMINAL_RUN_STATUSES:
        _require("TERMINAL_WITH_PENDING_WRITE", state["pending_transition"] is None)
        _require("TERMINAL_WITH_PENDING_HUMAN_GATE", not any(row["kind"] == "human-validation" and row["status"] == "pending" for row in state["gates"]))
    if verify_digest: _require("STATE_DIGEST_MISMATCH", state["state_digest"] == state_digest(state))
    return state


def _index(records: list[dict[str, Any]], key: str, value: str, code: str) -> dict[str, Any]:
    matches = [record for record in records if record[key] == value]
    _require(code, len(matches) == 1, value)
    return matches[0]


def _last(state: dict[str, Any], request: dict[str, Any], ref: str) -> None:
    state["last_transition"] = {"transition_id": request["transition_id"], "kind": request["operation"], "ref": ref, "outcome": "committed", "occurred_at": request["occurred_at"]}
    state["updated_at"] = request["occurred_at"]


def _empty_assessment() -> dict[str, Any]:
    return {"assessment": "unavailable", "reason": "not assessed yet", "items": []}


def _initial_state(request: dict[str, Any]) -> dict[str, Any]:
    payload = _closed("INITIALIZE_PAYLOAD_INVALID", request["payload"], {"identity", "plan_revision", "tasks", "phases", "gates", "audit_boundaries"})
    state = {
        "schema_version": 1, "identity": copy.deepcopy(payload["identity"]), "plan_revision": copy.deepcopy(payload["plan_revision"]),
        "revision": 1, "state_digest": "sha256:" + "0" * 64, "status": "running", "updated_at": request["occurred_at"],
        "last_transition": {"transition_id": request["transition_id"], "kind": "initialize", "ref": payload["identity"]["run_id"], "outcome": "committed", "occurred_at": request["occurred_at"]},
        "last_compact_transition": None, "pending_transition": None,
        "execution_summary": {"implemented_outcomes": [], "terminal_reason": None},
        "tasks": [], "phases": [], "handoffs": [], "gates": [], "audit_boundaries": [],
        "manual_qa": {"applicability": "pending", "eligibility_status": "pending", "eligibility_basis_digest": None, "eligible_revision": None, "applicable_gate_refs": [], "limitation_refs": [], "transitioned_at": None},
        "human_decisions": [], "effort_observations": [], "material_frictions": [],
        "blockers": _empty_assessment(), "residual_risks": _empty_assessment(), "next_steps": [], "optional_artifacts": [],
    }
    for task in _list("INITIAL_TASKS_INVALID", payload["tasks"], maximum=512, nonempty=True):
        task = _closed("INITIAL_TASK_INVALID", task, {"task_ref", "phase_ref", "required", "validator_ref"})
        state["tasks"].append({"task_ref": task["task_ref"], "phase_ref": task["phase_ref"], "required": task["required"], "status": "pending", "transition_id": None, "result": None, "transitioned_at": None, "validation": {"status": "pending", "validator_ref": task["validator_ref"], "evidence_refs": [], "limitation": None}, "target_digests": []})
    for phase in _list("INITIAL_PHASES_INVALID", payload["phases"], maximum=128, nonempty=True):
        _ref("INITIAL_PHASE_INVALID", phase)
        state["phases"].append({"phase_ref": phase, "status": "pending", "transition_id": None, "result": None, "transitioned_at": None, "evidence_refs": []})
    for gate in _list("INITIAL_GATES_INVALID", payload["gates"], maximum=512):
        gate = _closed("INITIAL_GATE_INVALID", gate, {"gate_ref", "kind"})
        state["gates"].append({"gate_ref": gate["gate_ref"], "kind": gate["kind"], "status": "pending", "transition_id": None, "evidence_refs": [], "limitation": None})
    for boundary in _list("INITIAL_AUDITS_INVALID", payload["audit_boundaries"], maximum=512):
        _ref("INITIAL_AUDIT_INVALID", boundary)
        state["audit_boundaries"].append({"boundary_ref": boundary, "status": "pending", "auditor_identity": None, "findings": [], "evidence_refs": [], "transition_id": None, "transitioned_at": None})
    state["state_digest"] = state_digest(state)
    return validate_state(state)


REQUEST_KEYS = {"operation", "transition_id", "expected_revision", "occurred_at", "payload"}


def validate_request(value: Any) -> dict[str, Any]:
    request = _closed("OPERATION_REQUEST_INVALID", value, REQUEST_KEYS)
    _require("OPERATION_INVALID", request["operation"] in OPERATIONS); _stable_id("TRANSITION_ID_INVALID", request["transition_id"])
    _require("EXPECTED_REVISION_INVALID", isinstance(request["expected_revision"], int) and not isinstance(request["expected_revision"], bool) and request["expected_revision"] >= 0)
    _timestamp("OPERATION_TIMESTAMP_INVALID", request["occurred_at"]); _require("OPERATION_PAYLOAD_INVALID", isinstance(request["payload"], dict))
    return request


ROLE_BY_OPERATION = {
    "initialize": {"orchestrator"}, "start_task_phase": {"orchestrator"}, "prepare_task_write": {"state-writer"},
    "abandon_pending_write": {"state-writer"}, "block_pending_write": {"state-writer"}, "record_dispatch": {"orchestrator"},
    "close_handoff": {"orchestrator"}, "commit_task_phase": {"state-writer"}, "commit_audit": {"independent-auditor"},
    "commit_replan_ref": {"planner"}, "reconcile_cancellation": {"orchestrator"},
    "publish_manual_qa_eligibility": {"orchestrator"}, "approve_manual_qa": {"human-authority"}, "publish_terminal": {"orchestrator"},
}


def _apply(current: dict[str, Any], request: dict[str, Any], actor: str) -> dict[str, Any]:
    op = request["operation"]; payload = request["payload"]
    _require("ACTOR_UNAUTHORIZED", actor in ROLE_BY_OPERATION[op], f"{actor}:{op}")
    _require("TERMINAL_STATE_IMMUTABLE", current["status"] not in TERMINAL_RUN_STATUSES)
    desired = copy.deepcopy(current)
    if op == "start_task_phase":
        payload = _closed("START_PAYLOAD_INVALID", payload, {"task_ref", "phase_ref", "dependencies_passed", "prior_gates_passed"})
        _require("START_PRECONDITION_INVALID", payload["dependencies_passed"] is True and payload["prior_gates_passed"] is True and desired["pending_transition"] is None and desired["status"] == "running")
        task = _index(desired["tasks"], "task_ref", payload["task_ref"], "TASK_NOT_FOUND"); phase = _index(desired["phases"], "phase_ref", payload["phase_ref"], "PHASE_NOT_FOUND")
        _require("TASK_PHASE_MISMATCH", task["phase_ref"] == phase["phase_ref"]); _require("TASK_NOT_PENDING", task["status"] == "pending"); _require("PHASE_NOT_STARTABLE", phase["status"] in {"pending", "running"})
        task.update(status="running", transition_id=request["transition_id"], transitioned_at=request["occurred_at"])
        if phase["status"] == "pending": phase.update(status="running", transition_id=request["transition_id"], transitioned_at=request["occurred_at"])
        _last(desired, request, task["task_ref"])
    elif op == "prepare_task_write":
        payload = _closed("PREPARE_WRITE_PAYLOAD_INVALID", payload, {"task_ref", "targets"}); task = _index(desired["tasks"], "task_ref", payload["task_ref"], "TASK_NOT_FOUND")
        _require("PREPARE_WRITE_PRECONDITION_INVALID", desired["status"] == "running" and task["status"] == "running" and desired["pending_transition"] is None)
        desired["pending_transition"] = {"transition_id": request["transition_id"], "operation": op, "task_ref": task["task_ref"], "targets": copy.deepcopy(payload["targets"]), "status": "prepared"}; _last(desired, request, task["task_ref"])
    elif op == "abandon_pending_write":
        payload = _closed("ABANDON_PAYLOAD_INVALID", payload, {"task_ref", "all_targets_match_before"}); pending = desired["pending_transition"]
        _require("ABANDON_PRECONDITION_INVALID", pending is not None and pending["status"] == "prepared" and pending["task_ref"] == payload["task_ref"] and payload["all_targets_match_before"] is True)
        desired["pending_transition"] = None; _last(desired, request, payload["task_ref"])
    elif op == "block_pending_write":
        payload = _closed("BLOCK_WRITE_PAYLOAD_INVALID", payload, {"task_ref", "blocker", "risk", "next_step"}); pending = desired["pending_transition"]
        _require("BLOCK_WRITE_PRECONDITION_INVALID", pending is not None and pending["status"] == "prepared" and pending["task_ref"] == payload["task_ref"])
        pending["status"] = "blocked"; desired["status"] = "blocked"; desired["blockers"] = {"assessment": "present", "reason": None, "items": [copy.deepcopy(payload["blocker"])]}; desired["residual_risks"] = {"assessment": "present", "reason": None, "items": [copy.deepcopy(payload["risk"])]}; desired["next_steps"] = [copy.deepcopy(payload["next_step"])]; _last(desired, request, payload["task_ref"])
    elif op == "record_dispatch":
        payload = _closed("DISPATCH_PAYLOAD_INVALID", payload, {"handoff_id", "task_ref", "phase_ref", "agent_label", "objective", "called_at", "budget_permits"})
        _require("DISPATCH_PRECONDITION_INVALID", desired["status"] == "running" and payload["budget_permits"] is True and all(row["handoff_id"] != payload["handoff_id"] for row in desired["handoffs"]))
        if payload["task_ref"] is not None: _require("DISPATCH_TASK_NOT_RUNNING", _index(desired["tasks"], "task_ref", payload["task_ref"], "TASK_NOT_FOUND")["status"] == "running")
        _index(desired["phases"], "phase_ref", payload["phase_ref"], "PHASE_NOT_FOUND")
        desired["handoffs"].append({"handoff_id": payload["handoff_id"], "task_ref": payload["task_ref"], "phase_ref": payload["phase_ref"], "agent_label": payload["agent_label"], "objective": payload["objective"], "status": "open", "called_at": copy.deepcopy(payload["called_at"]), "delivered_at": {"status": "pending", "value": None, "reason": None}, "delivery": {"status": "pending", "summary": None, "reason": None}, "result": {"status": "pending", "summary": None}, "evidence_refs": []}); _last(desired, request, payload["handoff_id"])
    elif op == "close_handoff":
        payload = _closed("CLOSE_HANDOFF_PAYLOAD_INVALID", payload, {"handoff_id", "status", "delivered_at", "delivery", "result", "evidence_refs"}); handoff = _index(desired["handoffs"], "handoff_id", payload["handoff_id"], "HANDOFF_NOT_FOUND")
        _require("HANDOFF_NOT_OPEN", handoff["status"] == "open"); handoff.update(status=payload["status"], delivered_at=copy.deepcopy(payload["delivered_at"]), delivery=copy.deepcopy(payload["delivery"]), result=copy.deepcopy(payload["result"]), evidence_refs=copy.deepcopy(payload["evidence_refs"])); _last(desired, request, payload["handoff_id"])
    elif op == "commit_task_phase":
        payload = _closed("COMMIT_TASK_PAYLOAD_INVALID", payload, {"task_ref", "task_status", "task_result", "validation", "target_digests", "phase", "gates", "implemented_outcomes", "effort_observations", "material_frictions", "blockers", "residual_risks", "next_steps", "optional_artifacts", "desired_targets_verified"}); task = _index(desired["tasks"], "task_ref", payload["task_ref"], "TASK_NOT_FOUND")
        _require("TASK_NOT_RUNNING", task["status"] == "running"); _require("TASK_STATUS_NOT_TERMINAL", payload["task_status"] in TERMINAL_TASK_STATUSES)
        _require("DESIRED_TARGETS_NOT_VERIFIED", payload["desired_targets_verified"] is True)
        if desired["pending_transition"] is not None: _require("PENDING_WRITE_NOT_VERIFIED", desired["pending_transition"]["task_ref"] == task["task_ref"])
        task.update(status=payload["task_status"], transition_id=request["transition_id"], result=copy.deepcopy(payload["task_result"]), transitioned_at=request["occurred_at"], validation=copy.deepcopy(payload["validation"]), target_digests=copy.deepcopy(payload["target_digests"])); desired["pending_transition"] = None
        ref = task["task_ref"]
        if payload["phase"] is not None:
            phase_payload = _closed("COMMIT_PHASE_PAYLOAD_INVALID", payload["phase"], {"phase_ref", "status", "result", "evidence_refs"}); phase = _index(desired["phases"], "phase_ref", phase_payload["phase_ref"], "PHASE_NOT_FOUND")
            _require("PHASE_NOT_RUNNING", phase["status"] == "running"); phase.update(status=phase_payload["status"], transition_id=request["transition_id"], result=copy.deepcopy(phase_payload["result"]), transitioned_at=request["occurred_at"], evidence_refs=copy.deepcopy(phase_payload["evidence_refs"])); ref = phase["phase_ref"]
        desired["gates"] = copy.deepcopy(payload["gates"]); desired["execution_summary"]["implemented_outcomes"] = copy.deepcopy(payload["implemented_outcomes"]); desired["effort_observations"] = copy.deepcopy(payload["effort_observations"]); desired["material_frictions"] = copy.deepcopy(payload["material_frictions"]); desired["blockers"] = copy.deepcopy(payload["blockers"]); desired["residual_risks"] = copy.deepcopy(payload["residual_risks"]); desired["next_steps"] = copy.deepcopy(payload["next_steps"]); desired["optional_artifacts"] = copy.deepcopy(payload["optional_artifacts"])
        desired["status"] = "blocked" if any(row["status"] == "open" for row in desired["blockers"]["items"]) else "running"
        desired["last_compact_transition"] = {"transition_id": request["transition_id"], "kind": op, "ref": ref, "result": payload["task_status"] if payload["phase"] is None else payload["phase"]["status"], "occurred_at": request["occurred_at"]}; _last(desired, request, ref)
    elif op == "commit_audit":
        payload = _closed("AUDIT_PAYLOAD_INVALID", payload, {"boundary_ref", "status", "auditor_identity", "findings", "evidence_refs", "gates", "blockers", "residual_risks", "next_steps"}); boundary = _index(desired["audit_boundaries"], "boundary_ref", payload["boundary_ref"], "AUDIT_BOUNDARY_NOT_FOUND")
        _require("AUDIT_BOUNDARY_NOT_PENDING", boundary["status"] == "pending"); boundary.update(status=payload["status"], auditor_identity=payload["auditor_identity"], findings=copy.deepcopy(payload["findings"]), evidence_refs=copy.deepcopy(payload["evidence_refs"]), transition_id=request["transition_id"], transitioned_at=request["occurred_at"])
        desired["gates"] = copy.deepcopy(payload["gates"]); desired["blockers"] = copy.deepcopy(payload["blockers"]); desired["residual_risks"] = copy.deepcopy(payload["residual_risks"]); desired["next_steps"] = copy.deepcopy(payload["next_steps"])
        if payload["status"] == "rejected":
            _require("AUDIT_REJECTION_WITHOUT_BLOCKER", desired["blockers"]["assessment"] == "present" and any(row["status"] == "open" for row in desired["blockers"]["items"]))
            desired["status"] = "blocked"
        elif desired["status"] == "blocked" and not any(row["status"] == "open" for row in desired["blockers"]["items"]):
            desired["status"] = "running"
        _last(desired, request, payload["boundary_ref"])
    elif op == "commit_replan_ref":
        payload = _closed("REPLAN_PAYLOAD_INVALID", payload, {"plan_revision", "tasks", "phases", "gates", "audit_boundaries", "blockers", "next_steps"})
        _require("REPLAN_PRECONDITION_INVALID", desired["pending_transition"] is None and not any(row["status"] == "open" for row in desired["handoffs"]))
        existing_tasks = {row["task_ref"]: row for row in desired["tasks"]}
        for spec in payload["tasks"]:
            if spec["task_ref"] in existing_tasks:
                existing = existing_tasks[spec["task_ref"]]
                _require("REPLAN_EXISTING_TASK_SPEC_MISMATCH", spec["phase_ref"] == existing["phase_ref"] and spec["required"] == existing["required"] and spec["validator_ref"] == existing["validation"]["validator_ref"], spec["task_ref"])
        desired["plan_revision"] = copy.deepcopy(payload["plan_revision"]); new_tasks=[]
        for spec in payload["tasks"]:
            if spec["task_ref"] in existing_tasks: new_tasks.append(existing_tasks[spec["task_ref"]])
            else: new_tasks.append({"task_ref": spec["task_ref"], "phase_ref": spec["phase_ref"], "required": spec["required"], "status": "pending", "transition_id": None, "result": None, "transitioned_at": None, "validation": {"status": "pending", "validator_ref": spec["validator_ref"], "evidence_refs": [], "limitation": None}, "target_digests": []})
        _require("REPLAN_REMOVES_STARTED_TASK", all(ref in {row["task_ref"] for row in new_tasks} or row["status"] == "pending" for ref,row in existing_tasks.items())); desired["tasks"] = new_tasks
        desired["phases"] = copy.deepcopy(payload["phases"]); desired["gates"] = copy.deepcopy(payload["gates"]); desired["audit_boundaries"] = copy.deepcopy(payload["audit_boundaries"]); desired["blockers"] = copy.deepcopy(payload["blockers"]); desired["next_steps"] = copy.deepcopy(payload["next_steps"]); desired["status"] = "running"; _last(desired, request, payload["plan_revision"]["plan_revision_ref"])
    elif op == "reconcile_cancellation":
        payload = _closed("CANCELLATION_PAYLOAD_INVALID", payload, {"reason", "blockers", "residual_risks", "next_steps", "all_handoffs_terminal_or_unknown"}); _require("CANCELLATION_PRECONDITION_INVALID", desired["pending_transition"] is None and payload["all_handoffs_terminal_or_unknown"] is True)
        desired["status"] = "cancelled"; desired["execution_summary"]["terminal_reason"] = copy.deepcopy(payload["reason"]); desired["blockers"] = copy.deepcopy(payload["blockers"]); desired["residual_risks"] = copy.deepcopy(payload["residual_risks"]); desired["next_steps"] = copy.deepcopy(payload["next_steps"]); _last(desired, request, desired["identity"]["run_id"])
    elif op == "publish_manual_qa_eligibility":
        payload = _closed("QA_ELIGIBILITY_PAYLOAD_INVALID", payload, {"basis_digest", "applicable_gate_refs", "limitation_refs"})
        applicable_pending = [row["gate_ref"] for row in desired["gates"] if row["kind"] == "human-validation" and row["status"] == "pending"]
        _require("QA_APPLICABLE_GATE_SET_MISMATCH", payload["applicable_gate_refs"] == applicable_pending)
        _require("QA_ELIGIBILITY_PRECONDITION_INVALID", desired["status"] == "running" and desired["pending_transition"] is None and not any(row["status"] == "open" for row in desired["handoffs"]) and all(not row["required"] or row["status"] == "passed" for row in desired["tasks"]) and all(row["status"] in {"approved", "not-applicable"} for row in desired["audit_boundaries"]) and all(row["status"] in {"passed", "not-applicable", "unavailable"} or (row["kind"] == "human-validation" and row["status"] == "pending") for row in desired["gates"]) and not any(row["status"] == "open" for row in desired["blockers"]["items"]))
        desired["status"] = "awaiting-manual-qa"; desired["manual_qa"] = {"applicability": "required", "eligibility_status": "eligible", "eligibility_basis_digest": payload["basis_digest"], "eligible_revision": current["revision"] + 1, "applicable_gate_refs": copy.deepcopy(payload["applicable_gate_refs"]), "limitation_refs": copy.deepcopy(payload["limitation_refs"]), "transitioned_at": request["occurred_at"]}; _last(desired, request, desired["identity"]["run_id"])
    elif op == "approve_manual_qa":
        payload = _closed("QA_APPROVAL_PAYLOAD_INVALID", payload, {"decision_id", "basis_digest", "applicable_gate_refs", "limitation_refs", "terminal_summary"}); qa = desired["manual_qa"]
        _require("QA_APPROVAL_PRECONDITION_INVALID", desired["status"] == "awaiting-manual-qa" and qa["eligible_revision"] == current["revision"] and qa["eligibility_basis_digest"] == payload["basis_digest"] and qa["applicable_gate_refs"] == payload["applicable_gate_refs"] and qa["limitation_refs"] == payload["limitation_refs"])
        for ref in payload["applicable_gate_refs"]:
            gate = _index(desired["gates"], "gate_ref", ref, "GATE_NOT_FOUND"); _require("QA_GATE_NOT_PENDING", gate["kind"] == "human-validation" and gate["status"] == "pending"); gate.update(status="passed", transition_id=request["transition_id"], evidence_refs=[])
        desired["human_decisions"].append({"decision_id": payload["decision_id"], "kind": "manual-qa", "decision": "approved", "basis_digest": payload["basis_digest"], "applicable_gate_refs": copy.deepcopy(payload["applicable_gate_refs"]), "limitation_refs": copy.deepcopy(payload["limitation_refs"]), "decided_at": request["occurred_at"]}); desired["status"] = "completed-with-limitations" if payload["limitation_refs"] else "completed"; desired["execution_summary"]["terminal_reason"] = {"status": "observed", "summary": payload["terminal_summary"], "reason": None}; _last(desired, request, desired["identity"]["run_id"])
    elif op == "publish_terminal":
        payload = _closed("TERMINAL_PAYLOAD_INVALID", payload, {"status", "terminal_reason", "implemented_outcomes", "blockers", "residual_risks", "next_steps", "terminal_truth_passed"}); _require("TERMINAL_PRECONDITION_INVALID", payload["terminal_truth_passed"] is True and payload["status"] in {"completed", "completed-with-limitations", "partial", "failed"} and desired["pending_transition"] is None and not any(row["status"] == "open" for row in desired["handoffs"]))
        _require("TERMINAL_WITH_PENDING_HUMAN_GATE", not any(row["kind"] == "human-validation" and row["status"] == "pending" for row in desired["gates"]))
        required_tasks = [row for row in desired["tasks"] if row["required"]]
        accepted = any(row["status"] == "passed" for row in required_tasks)
        complete_tasks = all(row["status"] == "passed" for row in required_tasks)
        complete_audits = all(row["status"] in {"approved", "not-applicable"} for row in desired["audit_boundaries"])
        complete_gates = all(row["status"] in {"passed", "not-applicable"} for row in desired["gates"])
        has_limitation = any(row["validation"]["limitation"] is not None for row in desired["tasks"]) or any(row["limitation"] is not None for row in desired["gates"])
        if payload["status"] == "completed": _require("COMPLETED_TRUTH_INVALID", complete_tasks and complete_audits and complete_gates and not has_limitation and payload["blockers"]["assessment"] == "none-confirmed")
        elif payload["status"] == "completed-with-limitations": _require("LIMITED_COMPLETION_TRUTH_INVALID", complete_tasks and complete_audits and complete_gates and has_limitation and payload["blockers"]["assessment"] == "none-confirmed")
        elif payload["status"] == "partial": _require("PARTIAL_TRUTH_INVALID", accepted and not complete_tasks)
        else: _require("FAILED_TRUTH_INVALID", not complete_tasks)
        desired["status"] = payload["status"]; desired["manual_qa"] = {"applicability": "not-required", "eligibility_status": "not-applicable", "eligibility_basis_digest": None, "eligible_revision": None, "applicable_gate_refs": [], "limitation_refs": [], "transitioned_at": request["occurred_at"]}; desired["execution_summary"] = {"implemented_outcomes": copy.deepcopy(payload["implemented_outcomes"]), "terminal_reason": copy.deepcopy(payload["terminal_reason"])}; desired["blockers"] = copy.deepcopy(payload["blockers"]); desired["residual_risks"] = copy.deepcopy(payload["residual_risks"]); desired["next_steps"] = copy.deepcopy(payload["next_steps"]); _last(desired, request, desired["identity"]["run_id"])
    else:
        raise StateContractError("OPERATION_NOT_IMPLEMENTED", op)
    desired["revision"] = current["revision"] + 1; desired["state_digest"] = state_digest(desired)
    return validate_state(desired)


def _replay_metadata_matches(current: dict[str, Any], request: dict[str, Any]) -> bool:
    return (
        current["revision"] == request["expected_revision"] + 1
        and current["updated_at"] == request["occurred_at"]
        and current["last_transition"]["transition_id"] == request["transition_id"]
        and current["last_transition"]["kind"] == request["operation"]
        and current["last_transition"]["occurred_at"] == request["occurred_at"]
    )


def _exact_replay_matches(current: dict[str, Any], request: dict[str, Any]) -> bool:
    """Compare the complete canonical request with its immediately committed state."""
    if not _replay_metadata_matches(current, request): return False
    payload = request["payload"]; op = request["operation"]
    try:
        if op == "start_task_phase":
            payload = _closed("REPLAY", payload, {"task_ref", "phase_ref", "dependencies_passed", "prior_gates_passed"})
            task = _index(current["tasks"], "task_ref", payload["task_ref"], "REPLAY")
            return payload["dependencies_passed"] is True and payload["prior_gates_passed"] is True and task["phase_ref"] == payload["phase_ref"] and task["status"] == "running" and task["transition_id"] == request["transition_id"] and task["transitioned_at"] == request["occurred_at"]
        if op == "prepare_task_write":
            payload = _closed("REPLAY", payload, {"task_ref", "targets"})
            return current["pending_transition"] == {"transition_id": request["transition_id"], "operation": op, "task_ref": payload["task_ref"], "targets": payload["targets"], "status": "prepared"}
        if op == "abandon_pending_write":
            payload = _closed("REPLAY", payload, {"task_ref", "all_targets_match_before"})
            return payload["all_targets_match_before"] is True and current["pending_transition"] is None and current["last_transition"]["ref"] == payload["task_ref"]
        if op == "block_pending_write":
            payload = _closed("REPLAY", payload, {"task_ref", "blocker", "risk", "next_step"})
            pending = current["pending_transition"]
            return pending is not None and pending["task_ref"] == payload["task_ref"] and pending["status"] == "blocked" and current["status"] == "blocked" and current["blockers"] == {"assessment": "present", "reason": None, "items": [payload["blocker"]]} and current["residual_risks"] == {"assessment": "present", "reason": None, "items": [payload["risk"]]} and current["next_steps"] == [payload["next_step"]]
        if op == "record_dispatch":
            payload = _closed("REPLAY", payload, {"handoff_id", "task_ref", "phase_ref", "agent_label", "objective", "called_at", "budget_permits"})
            handoff = _index(current["handoffs"], "handoff_id", payload["handoff_id"], "REPLAY")
            return payload["budget_permits"] is True and handoff == {"handoff_id": payload["handoff_id"], "task_ref": payload["task_ref"], "phase_ref": payload["phase_ref"], "agent_label": payload["agent_label"], "objective": payload["objective"], "status": "open", "called_at": payload["called_at"], "delivered_at": {"status": "pending", "value": None, "reason": None}, "delivery": {"status": "pending", "summary": None, "reason": None}, "result": {"status": "pending", "summary": None}, "evidence_refs": []}
        if op == "close_handoff":
            payload = _closed("REPLAY", payload, {"handoff_id", "status", "delivered_at", "delivery", "result", "evidence_refs"})
            handoff = _index(current["handoffs"], "handoff_id", payload["handoff_id"], "REPLAY")
            return all(handoff[key] == payload[key] for key in ("status", "delivered_at", "delivery", "result", "evidence_refs"))
        if op == "commit_task_phase":
            payload = _closed("REPLAY", payload, {"task_ref", "task_status", "task_result", "validation", "target_digests", "phase", "gates", "implemented_outcomes", "effort_observations", "material_frictions", "blockers", "residual_risks", "next_steps", "optional_artifacts", "desired_targets_verified"})
            task = _index(current["tasks"], "task_ref", payload["task_ref"], "REPLAY")
            matches = payload["desired_targets_verified"] is True and current["pending_transition"] is None and task["status"] == payload["task_status"] and task["result"] == payload["task_result"] and task["validation"] == payload["validation"] and task["target_digests"] == payload["target_digests"] and task["transition_id"] == request["transition_id"] and task["transitioned_at"] == request["occurred_at"] and current["gates"] == payload["gates"] and current["execution_summary"]["implemented_outcomes"] == payload["implemented_outcomes"] and current["effort_observations"] == payload["effort_observations"] and current["material_frictions"] == payload["material_frictions"] and current["blockers"] == payload["blockers"] and current["residual_risks"] == payload["residual_risks"] and current["next_steps"] == payload["next_steps"] and current["optional_artifacts"] == payload["optional_artifacts"]
            if payload["phase"] is not None:
                phase = _index(current["phases"], "phase_ref", payload["phase"]["phase_ref"], "REPLAY")
                matches = matches and phase["status"] == payload["phase"]["status"] and phase["result"] == payload["phase"]["result"] and phase["evidence_refs"] == payload["phase"]["evidence_refs"] and phase["transition_id"] == request["transition_id"] and phase["transitioned_at"] == request["occurred_at"]
            return matches
        if op == "commit_audit":
            payload = _closed("REPLAY", payload, {"boundary_ref", "status", "auditor_identity", "findings", "evidence_refs", "gates", "blockers", "residual_risks", "next_steps"})
            boundary = _index(current["audit_boundaries"], "boundary_ref", payload["boundary_ref"], "REPLAY")
            return boundary == {"boundary_ref": payload["boundary_ref"], "status": payload["status"], "auditor_identity": payload["auditor_identity"], "findings": payload["findings"], "evidence_refs": payload["evidence_refs"], "transition_id": request["transition_id"], "transitioned_at": request["occurred_at"]} and current["gates"] == payload["gates"] and current["blockers"] == payload["blockers"] and current["residual_risks"] == payload["residual_risks"] and current["next_steps"] == payload["next_steps"]
        if op == "commit_replan_ref":
            payload = _closed("REPLAY", payload, {"plan_revision", "tasks", "phases", "gates", "audit_boundaries", "blockers", "next_steps"})
            projected = [{"task_ref": row["task_ref"], "phase_ref": row["phase_ref"], "required": row["required"], "validator_ref": row["validation"]["validator_ref"]} for row in current["tasks"]]
            return current["plan_revision"] == payload["plan_revision"] and projected == payload["tasks"] and current["phases"] == payload["phases"] and current["gates"] == payload["gates"] and current["audit_boundaries"] == payload["audit_boundaries"] and current["blockers"] == payload["blockers"] and current["next_steps"] == payload["next_steps"]
        if op == "reconcile_cancellation":
            payload = _closed("REPLAY", payload, {"reason", "blockers", "residual_risks", "next_steps", "all_handoffs_terminal_or_unknown"})
            return payload["all_handoffs_terminal_or_unknown"] is True and current["status"] == "cancelled" and current["execution_summary"]["terminal_reason"] == payload["reason"] and current["blockers"] == payload["blockers"] and current["residual_risks"] == payload["residual_risks"] and current["next_steps"] == payload["next_steps"]
        if op == "publish_manual_qa_eligibility":
            payload = _closed("REPLAY", payload, {"basis_digest", "applicable_gate_refs", "limitation_refs"})
            qa = current["manual_qa"]
            return current["status"] == "awaiting-manual-qa" and qa["eligibility_basis_digest"] == payload["basis_digest"] and qa["eligible_revision"] == current["revision"] and qa["applicable_gate_refs"] == payload["applicable_gate_refs"] and qa["limitation_refs"] == payload["limitation_refs"] and qa["transitioned_at"] == request["occurred_at"]
        if op == "approve_manual_qa":
            payload = _closed("REPLAY", payload, {"decision_id", "basis_digest", "applicable_gate_refs", "limitation_refs", "terminal_summary"})
            decision = _index(current["human_decisions"], "decision_id", payload["decision_id"], "REPLAY")
            return decision == {"decision_id": payload["decision_id"], "kind": "manual-qa", "decision": "approved", "basis_digest": payload["basis_digest"], "applicable_gate_refs": payload["applicable_gate_refs"], "limitation_refs": payload["limitation_refs"], "decided_at": request["occurred_at"]} and current["execution_summary"]["terminal_reason"] == {"status": "observed", "summary": payload["terminal_summary"], "reason": None}
        if op == "publish_terminal":
            payload = _closed("REPLAY", payload, {"status", "terminal_reason", "implemented_outcomes", "blockers", "residual_risks", "next_steps", "terminal_truth_passed"})
            return payload["terminal_truth_passed"] is True and current["status"] == payload["status"] and current["execution_summary"] == {"implemented_outcomes": payload["implemented_outcomes"], "terminal_reason": payload["terminal_reason"]} and current["blockers"] == payload["blockers"] and current["residual_risks"] == payload["residual_risks"] and current["next_steps"] == payload["next_steps"]
    except (KeyError, StateContractError, TypeError):
        return False
    return False


def _read_state(path: Path) -> tuple[bytes, dict[str, Any]]:
    _require("STATE_PATH_MISSING", path.is_file() and not path.is_symlink(), str(path))
    raw = path.read_bytes()
    try: value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise StateContractError("STATE_JSON_INVALID", str(exc)) from exc
    return raw, validate_state(value)


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try: os.fsync(descriptor)
    finally: os.close(descriptor)


def _atomic_replace(path: Path, desired: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(desired); stream.flush(); os.fsync(stream.fileno())
        _require("TEMP_BYTES_MISMATCH", temporary.read_bytes() == desired)
        os.replace(temporary, path); _fsync_directory(path.parent)
    finally:
        if temporary.exists(): temporary.unlink()


def apply_operation(path: str | Path, request_value: Any, *, actor: str, exclusive_owner: bool) -> tuple[dict[str, Any], bool]:
    """Validate, CAS, and atomically commit one typed operation.

    Returns ``(validated_snapshot, wrote)``. Exact replay of the immediately
    committed transition returns ``wrote=False``. Callers must establish the
    single per-run owner; this function deliberately does not pretend CAS is a
    cross-process lock.
    """
    _require("EXCLUSIVE_OWNER_UNPROVEN", exclusive_owner is True)
    request = validate_request(request_value); path = Path(path)
    _require("STATE_PARENT_INVALID", path.parent.is_dir() and not path.parent.is_symlink())
    if request["operation"] == "initialize":
        _require("INITIALIZE_REVISION_INVALID", request["expected_revision"] == 0)
        desired = _initial_state(request)
        if path.exists():
            _, current = _read_state(path)
            if current == desired:
                return current, False
            raise StateContractError("TRANSITION_REPLAY_CONFLICT", request["transition_id"])
        _atomic_replace(path, canonical_bytes(desired) + b"\n")
        return _read_state(path)[1], True
    before_bytes, current = _read_state(path)
    if current["last_transition"]["transition_id"] == request["transition_id"]:
        if current["last_transition"]["kind"] == request["operation"] and _exact_replay_matches(current, request): return current, False
        raise StateContractError("TRANSITION_REPLAY_CONFLICT", request["transition_id"])
    _require("REVISION_CAS_MISMATCH", current["revision"] == request["expected_revision"])
    before_digest = bytes_digest(before_bytes)
    desired = _apply(current, request, actor)
    confirm_bytes, confirm = _read_state(path)
    _require("STATE_CHANGED_DURING_OPERATION", confirm["revision"] == current["revision"] and bytes_digest(confirm_bytes) == before_digest)
    _atomic_replace(path, canonical_bytes(desired) + b"\n")
    return _read_state(path)[1], True


def _progress(state: Mapping[str, Any]) -> tuple[int, int, int]:
    required = [task for task in state["tasks"] if task["required"]]
    complete = sum(task["status"] == "passed" for task in required)
    percent = int((Decimal(complete * 100) / Decimal(len(required))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)) if required else 0
    return complete, len(required), percent


def _compact_local_clock(value: str) -> str:
    observed = datetime.fromisoformat(value)
    meridiem = "AM" if observed.hour < 12 else "PM"
    hour = observed.hour % 12 or 12
    return f"{hour:02d}:{observed.minute:02d} {meridiem}"


def _duration(handoff: Mapping[str, Any]) -> str:
    called = handoff["called_at"]; delivered = handoff["delivered_at"]
    if called["status"] != "observed": return f"indisponível ({called['reason']})"
    if delivered["status"] == "pending": return "em andamento"
    if delivered["status"] != "observed": return f"indisponível ({delivered['reason']})"
    elapsed = datetime.fromisoformat(delivered["value"]) - datetime.fromisoformat(called["value"])
    return f"{int(elapsed.total_seconds())}s"


def render_compact(state_value: Any) -> str:
    state = validate_state(copy.deepcopy(state_value)); compact = state["last_compact_transition"]
    _require("COMPACT_NOT_AVAILABLE", compact is not None)
    completed, total, percent = _progress(state); phases_done = sum(row["status"] == "passed" for row in state["phases"]); active = sum(row["status"] == "open" for row in state["handoffs"])
    return f"Progresso: {completed}/{total} tasks ({percent}%) | Fase: {phases_done}/{len(state['phases'])} | Estado: {state['status']} | Última: {compact['ref']} {compact['result']} | Handoffs ativos: {active} | Atualizado em: {_compact_local_clock(compact['occurred_at'])}"


def _assessment_text(value: Mapping[str, Any], noun: str) -> list[str]:
    if value["assessment"] == "none-confirmed": return [f"- {noun}: nenhum"]
    if value["assessment"] == "unavailable": return [f"- {noun}: indisponível ({value['reason']})"]
    return [f"- {noun}: {row['fact']} — owner: {row['owner'] or 'indisponível'}" for row in value["items"]]


def render_dashboard(state_value: Any, *, mode: str) -> str:
    """Pure resume/requested/final renderer over one validated snapshot."""
    state = validate_state(copy.deepcopy(state_value)); _require("RENDER_MODE_INVALID", mode in {"resume", "requested", "final"})
    if mode == "final": _require("FINAL_RENDER_NOT_TERMINAL", state["status"] in TERMINAL_RUN_STATUSES)
    completed, total, percent = _progress(state)
    title = {"resume": "Dashboard de retomada", "requested": "Dashboard atual", "final": "Dashboard final"}[mode]
    terminal = state["execution_summary"]["terminal_reason"]
    delivered_summary = "; ".join(row["summary"] for row in state["execution_summary"]["implemented_outcomes"]) or "Nenhuma entrega aceita foi registrada"
    opening = f"{delivered_summary}. Estado da execução: {state['status']}."
    if terminal and terminal["summary"] and terminal["summary"] not in opening: opening += f" {terminal['summary']}"
    lines = [f"# {title}", "", opening, "", "| Handoff | Fase | Agente | Chamado em | Entregue em | Tempo de relógio | Entrega | Resultado |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    indexed_handoffs = list(enumerate(state["handoffs"]))
    indexed_handoffs.sort(key=lambda pair: (0, datetime.fromisoformat(pair[1]["called_at"]["value"]).timestamp(), pair[0]) if pair[1]["called_at"]["status"] == "observed" else (1, 0, pair[0]))
    for _, row in indexed_handoffs:
        called = row["called_at"]["value"] if row["called_at"]["status"] == "observed" else f"indisponível ({row['called_at']['reason']})"
        if row["delivered_at"]["status"] == "pending": delivered = "pendente"
        elif row["delivered_at"]["status"] == "observed": delivered = row["delivered_at"]["value"]
        else: delivered = f"indisponível ({row['delivered_at']['reason']})"
        delivery = row["delivery"]["summary"] or (f"indisponível ({row['delivery']['reason']})" if row["delivery"]["status"] == "unavailable" else row["delivery"]["status"])
        lines.append(f"| {row['handoff_id']} | {row['phase_ref']} | {row['agent_label']} | {called} | {delivered} | {_duration(row)} | {delivery} | {row['result']['summary'] or row['result']['status']} |")
    if not state["handoffs"]: lines.append("| nenhum | — | — | — | — | — | — | — |")
    lines += ["", f"Progresso estrutural: {completed}/{total} tasks ({percent}%).", "", "## Esforço", "", "| Categoria | Total gasto | Evidência |", "| --- | --- | --- |"]
    labels = {"writing": "Escrita", "correction": "Correção", "audit-interval": "Auditoria / intervalos"}
    for category in ("writing", "correction", "audit-interval"):
        rows = [row for row in state["effort_observations"] if row["category"] == category]
        if rows and all(row["status"] == "observed" for row in rows): total_ms = sum(row["value"] for row in rows); rendered = f"{total_ms} ms"; evidence = ", ".join(ref for row in rows for ref in row["evidence_refs"]) or "estado canônico"
        else:
            reason = next((row["reason"] for row in rows if row["status"] == "unavailable"), "observação não coletada")
            rendered = f"indisponível ({reason})"; evidence = "estado canônico"
        lines.append(f"| {labels[category]} | {rendered} | {evidence} |")
    if state["material_frictions"]:
        lines += ["", "## Fricções materiais", ""] + [f"- {row['fact']} — inferência: {row['inference']} — prevenção: {row['preventive_action']}" for row in state["material_frictions"]]
    lines += ["", "## Bloqueadores técnicos e risco residual", ""] + _assessment_text(state["blockers"], "Bloqueador técnico") + _assessment_text(state["residual_risks"], "Risco residual")
    lines += ["", "## Próximos passos", ""]
    lines += [f"- {row['action']} — owner: {row['owner']} — gate: {row['gate_ref'] or 'nenhum'}" for row in state["next_steps"]] or ["- nenhuma ação"]
    if mode == "resume":
        running = [row["task_ref"] for row in state["tasks"] if row["status"] == "running"]
        pending = state["pending_transition"]["task_ref"] if state["pending_transition"] else None
        completed_tasks = [row for row in state["tasks"] if row["status"] in TERMINAL_TASK_STATUSES]
        completed_phases = [row for row in state["phases"] if row["status"] in TERMINAL_PHASE_STATUSES]
        lines += ["", "## Tasks concluídas", "", "| Task | Fase | Estado | Resultado | Validação |", "| --- | --- | --- | --- | --- |"]
        lines += [f"| {row['task_ref']} | {row['phase_ref']} | {row['status']} | {row['result']['summary']} | {row['validation']['status']} |" for row in completed_tasks] or ["| nenhuma | — | — | — | — |"]
        lines += ["", "## Fases concluídas", "", "| Fase | Estado | Resultado |", "| --- | --- | --- |"]
        lines += [f"| {row['phase_ref']} | {row['status']} | {row['result']['summary']} |" for row in completed_phases] or ["| nenhuma | — | — |"]
        lines += ["", "## Ponto de retomada", "", f"- Task em execução: {running[0] if running else 'nenhuma'}", f"- Transição de escrita pendente: {pending or 'nenhuma'}", f"- Handoffs abertos: {sum(row['status'] == 'open' for row in state['handoffs'])}"]
    return "\n".join(lines) + "\n"


def self_test() -> dict[str, Any]:
    import tempfile as _tempfile
    digest = "sha256:" + "1" * 64; now = "2026-08-04T10:00:00-03:00"
    init = {"operation": "initialize", "transition_id": "tx.init", "expected_revision": 0, "occurred_at": now, "payload": {"identity": {"run_id": "run.test", "execution_id": "exec.test", "command_identity": {"command": "loki-implement-feature", "adapter": "codex"}, "demand_ref": "plan/demand.md", "demand_digest": digest, "analysis_ref": "plan/analysis.md", "analysis_digest": digest, "audit_configuration": {"frequency": "plan", "auditor_source": "agents/auditor.md", "policy_ref": "plan/tasks.md"}}, "plan_revision": {"plan_revision_ref": "plan/tasks.md", "plan_revision_digest": digest}, "tasks": [{"task_ref": "task-1", "phase_ref": "phase-1", "required": True, "validator_ref": "validator-1"}], "phases": ["phase-1"], "gates": [], "audit_boundaries": []}}
    exercised: set[str] = set()

    def checked(target: Path, request: dict[str, Any], actor: str) -> dict[str, Any]:
        snapshot, wrote = apply_operation(target, request, actor=actor, exclusive_owner=True)
        _require("SELF_TEST_OPERATION_WRITE", wrote, request["operation"])
        committed_bytes = target.read_bytes()
        replay, replay_wrote = apply_operation(target, copy.deepcopy(request), actor=actor, exclusive_owner=True)
        _require("SELF_TEST_EXACT_REPLAY", not replay_wrote and replay == snapshot and target.read_bytes() == committed_bytes, request["operation"])
        collision = copy.deepcopy(request)
        collision["occurred_at"] = (datetime.fromisoformat(request["occurred_at"]) + timedelta(seconds=1)).isoformat()
        try: apply_operation(target, collision, actor=actor, exclusive_owner=True)
        except StateContractError as exc: _require("SELF_TEST_REPLAY_CONFLICT_CODE", exc.code == "TRANSITION_REPLAY_CONFLICT", request["operation"])
        else: raise StateContractError("SELF_TEST_CHANGED_REPLAY_ACCEPTED", request["operation"])
        _require("SELF_TEST_REPLAY_CONFLICT_ZERO_WRITE", target.read_bytes() == committed_bytes, request["operation"])
        exercised.add(request["operation"])
        return snapshot

    with _tempfile.TemporaryDirectory(prefix="loki-state-self-test-") as directory:
        path = Path(directory) / "execution-state.json"
        state = checked(path, init, "orchestrator"); _require("SELF_TEST_INIT", state["revision"] == 1)
        changed_init = copy.deepcopy(init); changed_init["payload"]["tasks"].append({"task_ref": "task-2", "phase_ref": "phase-1", "required": True, "validator_ref": "validator-2"})
        initial_bytes = path.read_bytes()
        try: apply_operation(path, changed_init, actor="orchestrator", exclusive_owner=True)
        except StateContractError as exc: _require("SELF_TEST_INITIALIZE_SET_CONFLICT", exc.code == "TRANSITION_REPLAY_CONFLICT")
        else: raise StateContractError("SELF_TEST_CHANGED_INITIALIZE_ACCEPTED")
        _require("SELF_TEST_INITIALIZE_CONFLICT_ZERO_WRITE", path.read_bytes() == initial_bytes)
        start = {"operation": "start_task_phase", "transition_id": "tx.start", "expected_revision": 1, "occurred_at": "2026-08-04T10:01:00-03:00", "payload": {"task_ref": "task-1", "phase_ref": "phase-1", "dependencies_passed": True, "prior_gates_passed": True}}
        state = checked(path, start, "orchestrator")
        dispatch = {"operation": "record_dispatch", "transition_id": "tx.dispatch", "expected_revision": 2, "occurred_at": "2026-08-04T10:02:00-03:00", "payload": {"handoff_id": "handoff-1", "task_ref": "task-1", "phase_ref": "phase-1", "agent_label": "technical-implementer", "objective": "implement target", "called_at": {"status": "observed", "value": "2026-08-04T10:02:00-03:00", "reason": None}, "budget_permits": True}}
        state = checked(path, dispatch, "orchestrator")
        close = {"operation": "close_handoff", "transition_id": "tx.close", "expected_revision": 3, "occurred_at": "2026-08-04T10:04:00-03:00", "payload": {"handoff_id": "handoff-1", "status": "delivered", "delivered_at": {"status": "observed", "value": "2026-08-04T10:04:00-03:00", "reason": None}, "delivery": {"status": "delivered", "summary": "target implemented", "reason": None}, "result": {"status": "passed", "summary": "passed"}, "evidence_refs": ["evidence/check.txt"]}}
        state = checked(path, close, "orchestrator")
        commit = {"operation": "commit_task_phase", "transition_id": "tx.commit", "expected_revision": 4, "occurred_at": "2026-08-04T10:05:00-03:00", "payload": {"task_ref": "task-1", "task_status": "passed", "task_result": {"summary": "implemented", "responsible": "technical-implementer", "delivery_refs": ["evidence/check.txt"]}, "validation": {"status": "passed", "validator_ref": "validator-1", "evidence_refs": ["evidence/check.txt"], "limitation": None}, "target_digests": [], "phase": {"phase_ref": "phase-1", "status": "passed", "result": {"summary": "phase passed"}, "evidence_refs": ["evidence/check.txt"]}, "gates": [], "implemented_outcomes": [{"outcome_ref": "task-1", "summary": "implemented", "source_refs": ["evidence/check.txt"]}], "effort_observations": [{"observation_id": "effort-writing", "category": "writing", "status": "unavailable", "value": None, "unit": None, "reason": "telemetry not requested", "evidence_refs": []}], "material_frictions": [], "blockers": {"assessment": "none-confirmed", "reason": None, "items": []}, "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []}, "next_steps": [], "optional_artifacts": [], "desired_targets_verified": True}}
        state = checked(path, commit, "state-writer")
        compact = render_compact(state); _require("SELF_TEST_COMPACT", "1/1 tasks (100%)" in compact and "Atualizado em: 10:05 AM" in compact and "2026-08-04" not in compact and "-03:00" not in compact and now not in compact)
        requested = render_dashboard(state, mode="requested"); _require("SELF_TEST_REQUESTED", "120s" in requested and "indisponível (telemetry not requested)" in requested)
        before = path.read_bytes()
        try: apply_operation(path, {**start, "transition_id": "tx.stale"}, actor="orchestrator", exclusive_owner=True)
        except StateContractError as exc: _require("SELF_TEST_STALE_CODE", exc.code == "REVISION_CAS_MISMATCH")
        else: raise StateContractError("SELF_TEST_STALE_ACCEPTED")
        _require("SELF_TEST_ZERO_WRITE", path.read_bytes() == before)
    def fresh(suffix: str, *, boundaries: list[str] | None = None) -> tuple[_tempfile.TemporaryDirectory[str], Path, dict[str, Any]]:
        holder = _tempfile.TemporaryDirectory(prefix=f"loki-state-{suffix}-")
        target = Path(holder.name) / "execution-state.json"
        request = copy.deepcopy(init); request["transition_id"] = f"tx.init.{suffix}"; request["payload"]["identity"]["run_id"] = f"run.{suffix}"; request["payload"]["identity"]["execution_id"] = f"exec.{suffix}"; request["payload"]["audit_boundaries"] = boundaries or []
        snapshot = checked(target, request, "orchestrator")
        return holder, target, snapshot

    def start_only(target: Path, snapshot: dict[str, Any], suffix: str) -> dict[str, Any]:
        request = {"operation": "start_task_phase", "transition_id": f"tx.start.{suffix}", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:01:00-03:00", "payload": {"task_ref": "task-1", "phase_ref": "phase-1", "dependencies_passed": True, "prior_gates_passed": True}}
        return checked(target, request, "orchestrator")

    def commit_only(target: Path, snapshot: dict[str, Any], suffix: str) -> dict[str, Any]:
        request = copy.deepcopy(commit); request["transition_id"] = f"tx.commit.{suffix}"; request["expected_revision"] = snapshot["revision"]; request["occurred_at"] = "2026-08-04T11:02:00-03:00"
        return checked(target, request, "state-writer")

    holder, target, snapshot = fresh("pending")
    try:
        snapshot = start_only(target, snapshot, "pending")
        prepare = {"operation": "prepare_task_write", "transition_id": "tx.prepare.one", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:02:00-03:00", "payload": {"task_ref": "task-1", "targets": [{"target_ref": "scripts/example.py", "before_digest": digest, "desired_digest": "sha256:" + "2" * 64}]}}
        snapshot = checked(target, prepare, "state-writer")
        abandon = {"operation": "abandon_pending_write", "transition_id": "tx.abandon", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:03:00-03:00", "payload": {"task_ref": "task-1", "all_targets_match_before": True}}
        snapshot = checked(target, abandon, "state-writer")
        prepare["transition_id"] = "tx.prepare.two"; prepare["expected_revision"] = snapshot["revision"]
        snapshot = checked(target, prepare, "state-writer")
        block = {"operation": "block_pending_write", "transition_id": "tx.block", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:04:00-03:00", "payload": {"task_ref": "task-1", "blocker": {"blocker_id": "blocker.pending", "scope_ref": "task-1", "status": "open", "fact": "target bytes are mixed", "owner": "orchestrator", "gate_ref": None, "evidence_refs": []}, "risk": {"risk_id": "risk.pending", "scope_ref": "task-1", "status": "current", "fact": "product effect is unresolved", "owner": "orchestrator", "gate_ref": None, "evidence_refs": []}, "next_step": {"next_step_id": "step.pending", "scope_ref": "task-1", "action": "resolve target bytes", "owner": "orchestrator", "gate_ref": None, "status": "pending"}}}
        snapshot = checked(target, block, "state-writer"); _require("SELF_TEST_PENDING_BLOCK", snapshot["status"] == "blocked" and snapshot["pending_transition"]["status"] == "blocked")
    finally: holder.cleanup()

    holder, target, snapshot = fresh("audit", boundaries=["plan-boundary"])
    try:
        audit_request = {"operation": "commit_audit", "transition_id": "tx.audit", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:05:00-03:00", "payload": {"boundary_ref": "plan-boundary", "status": "approved", "auditor_identity": "independent-auditor", "findings": [], "evidence_refs": ["evidence/audit.txt"], "gates": [], "blockers": {"assessment": "none-confirmed", "reason": None, "items": []}, "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []}, "next_steps": []}}
        snapshot = checked(target, audit_request, "independent-auditor"); _require("SELF_TEST_AUDIT", snapshot["audit_boundaries"][0]["status"] == "approved")
    finally: holder.cleanup()

    holder, target, snapshot = fresh("replan")
    try:
        replan = {"operation": "commit_replan_ref", "transition_id": "tx.replan", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:06:00-03:00", "payload": {"plan_revision": {"plan_revision_ref": "plan/tasks-v2.md", "plan_revision_digest": "sha256:" + "3" * 64}, "tasks": [{"task_ref": "task-1", "phase_ref": "phase-1", "required": True, "validator_ref": "validator-1"}, {"task_ref": "task-2", "phase_ref": "phase-1", "required": True, "validator_ref": "validator-2"}], "phases": copy.deepcopy(snapshot["phases"]), "gates": [], "audit_boundaries": [], "blockers": {"assessment": "unavailable", "reason": "not assessed yet", "items": []}, "next_steps": []}}
        snapshot = checked(target, replan, "planner"); _require("SELF_TEST_REPLAN", len(snapshot["tasks"]) == 2)
    finally: holder.cleanup()

    holder, target, snapshot = fresh("cancel")
    try:
        cancel = {"operation": "reconcile_cancellation", "transition_id": "tx.cancel", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:07:00-03:00", "payload": {"reason": {"status": "observed", "summary": "cancelled by authority", "reason": None}, "blockers": {"assessment": "none-confirmed", "reason": None, "items": []}, "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []}, "next_steps": [], "all_handoffs_terminal_or_unknown": True}}
        snapshot = checked(target, cancel, "orchestrator"); _require("SELF_TEST_CANCEL", snapshot["status"] == "cancelled")
    finally: holder.cleanup()

    holder, target, snapshot = fresh("qa")
    try:
        snapshot = commit_only(target, start_only(target, snapshot, "qa"), "qa")
        basis = "sha256:" + "4" * 64
        eligible = {"operation": "publish_manual_qa_eligibility", "transition_id": "tx.qa.eligible", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:03:00-03:00", "payload": {"basis_digest": basis, "applicable_gate_refs": [], "limitation_refs": []}}
        snapshot = checked(target, eligible, "orchestrator")
        approve = {"operation": "approve_manual_qa", "transition_id": "tx.qa.approve", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:04:00-03:00", "payload": {"decision_id": "decision.qa", "basis_digest": basis, "applicable_gate_refs": [], "limitation_refs": [], "terminal_summary": "implementation and manual QA passed"}}
        snapshot = checked(target, approve, "human-authority"); _require("SELF_TEST_QA", snapshot["status"] == "completed")
        final_view = render_dashboard(snapshot, mode="final"); _require("SELF_TEST_FINAL_RENDER", "Dashboard final" in final_view)
    finally: holder.cleanup()

    holder, target, snapshot = fresh("terminal")
    try:
        snapshot = commit_only(target, start_only(target, snapshot, "terminal"), "terminal")
        terminal = {"operation": "publish_terminal", "transition_id": "tx.terminal", "expected_revision": snapshot["revision"], "occurred_at": "2026-08-04T11:04:00-03:00", "payload": {"status": "completed", "terminal_reason": {"status": "observed", "summary": "implementation passed", "reason": None}, "implemented_outcomes": copy.deepcopy(snapshot["execution_summary"]["implemented_outcomes"]), "blockers": {"assessment": "none-confirmed", "reason": None, "items": []}, "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []}, "next_steps": [], "terminal_truth_passed": True}}
        snapshot = checked(target, terminal, "orchestrator"); _require("SELF_TEST_TERMINAL", snapshot["status"] == "completed" and snapshot["manual_qa"]["eligibility_status"] == "not-applicable")
    finally: holder.cleanup()
    _require("SELF_TEST_OPERATION_COVERAGE", exercised == set(OPERATIONS), f"missing={sorted(set(OPERATIONS) - exercised)}")
    return {"self_test": "passed", "schema_version": 1, "operations": list(OPERATIONS), "exercised_operations": sorted(exercised), "render_modes": ["compact", "resume", "requested", "final"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--self-test", action="store_true"); parser.add_argument("--state"); parser.add_argument("--operation"); parser.add_argument("--actor"); parser.add_argument("--render", choices=("compact", "resume", "requested", "final")); parser.add_argument("--exclusive-owner", action="store_true")
    args = parser.parse_args()
    if args.self_test: print(json.dumps(self_test(), ensure_ascii=False, sort_keys=True)); return 0
    _require("STATE_ARGUMENT_REQUIRED", bool(args.state))
    if args.render:
        _, state = _read_state(Path(args.state)); print(render_compact(state) if args.render == "compact" else render_dashboard(state, mode=args.render), end=""); return 0
    _require("OPERATION_ARGUMENT_REQUIRED", bool(args.operation) and bool(args.actor))
    request = json.loads(Path(args.operation).read_text(encoding="utf-8")); state, wrote = apply_operation(args.state, request, actor=args.actor, exclusive_owner=args.exclusive_owner); print(json.dumps({"status": "committed" if wrote else "replayed", "revision": state["revision"], "state_digest": state["state_digest"]}, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
