#!/usr/bin/env python3
"""Validate current loki-implement-feature execution and manual-QA handoff records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "scripts/fixtures/implement-feature"
FIXTURE_FILES = (
    "input-path-cases.json",
    "state-resume-cases.json",
    "validation-cycle-cases.json",
    "response-dashboard-cases.json",
)
HEX = r"[0-9a-f]{64}"
SHA256_RE = re.compile(rf"sha256:{HEX}\Z")
RUN_RE = re.compile(rf"loki-run-v2:{HEX}\Z")
EXECUTION_RE = re.compile(rf"loki-execution-v2:{HEX}\Z")


class ContractError(ValueError):
    pass


def require(code: str, condition: bool) -> None:
    if not condition:
        raise ContractError(code)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def closed(code: str, value: Any, keys: set[str]) -> dict[str, Any]:
    require(code, isinstance(value, dict) and set(value) == keys)
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any, *, omit: str | None = None) -> str:
    material = deepcopy(value)
    if omit is not None:
        material.pop(omit, None)
    return "sha256:" + hashlib.sha256(canonical_bytes(material)).hexdigest()


def validate_digest(value: Any, code: str) -> None:
    require(code, isinstance(value, str) and SHA256_RE.fullmatch(value) is not None)


def validate_project_path(value: Any, code: str, *, below_planos: bool = False, fragment: bool = False) -> None:
    require(code, nonempty(value) and "\\" not in value)
    path, marker, suffix = value.partition("#")
    require(code, not marker or fragment)
    require(code, not marker or bool(suffix))
    pure = PurePosixPath(path)
    require(code, not pure.is_absolute() and ".." not in pure.parts and "." not in pure.parts)
    if below_planos:
        require(code, len(pure.parts) >= 2 and pure.parts[0] == "planos")


def require_contained(ref: str, plan_directory: str, code: str) -> None:
    validate_project_path(ref, code, fragment=True)
    path = PurePosixPath(ref.partition("#")[0])
    root = PurePosixPath(plan_directory)
    require(code, path == root or root in path.parents)


AUDIT_KEYS = {"schema_version", "frequency", "source", "policy_digest"}
IDENTITY_KEYS = {"schema_version", "command", "demand_digest", "analysis_digest", "plan_directory", "retry_limit", "audit_configuration"}
INPUT_KEYS = {"schema_version", "command_identity", "run_id", "execution_id", "demand_kind", "demand_ref", "analysis_ref", "state_ref", "result_ref", "dashboard_ref", "consistency_packet_ref"}


def validate_audit_configuration(value: Any) -> dict[str, Any]:
    audit = closed("AUDIT_CONFIGURATION_SHAPE_INVALID", value, AUDIT_KEYS)
    require("AUDIT_CONFIGURATION_SCHEMA_INVALID", audit["schema_version"] == 1)
    require("AUDIT_FREQUENCY_INVALID", audit["frequency"] in {"task", "phase", "plan"})
    require("AUDIT_SOURCE_INVALID", audit["source"] in {"default", "explicit"})
    require("AUDIT_DEFAULT_INVALID", not (audit["source"] == "default" and audit["frequency"] != "phase"))
    expected = digest({"schema_version": 1, "frequency": audit["frequency"], "source": audit["source"]})
    require("AUDIT_POLICY_DIGEST_INVALID", audit["policy_digest"] == expected)
    return audit


def validate_command_identity(value: Any) -> dict[str, Any]:
    identity = closed("COMMAND_IDENTITY_SHAPE_INVALID", value, IDENTITY_KEYS)
    require("COMMAND_IDENTITY_SCHEMA_INVALID", identity["schema_version"] == 2 and identity["command"] == "loki-implement-feature")
    validate_digest(identity["demand_digest"], "COMMAND_DEMAND_DIGEST_INVALID")
    validate_digest(identity["analysis_digest"], "COMMAND_ANALYSIS_DIGEST_INVALID")
    validate_project_path(identity["plan_directory"], "COMMAND_PLAN_DIRECTORY_INVALID", below_planos=True)
    require("COMMAND_RETRY_LIMIT_INVALID", isinstance(identity["retry_limit"], int) and not isinstance(identity["retry_limit"], bool) and identity["retry_limit"] >= 0)
    validate_audit_configuration(identity["audit_configuration"])
    return identity


def validate_execution_input(value: Any) -> dict[str, Any]:
    record = closed("EXECUTION_INPUT_SHAPE_INVALID", value, INPUT_KEYS)
    require("EXECUTION_INPUT_SCHEMA_INVALID", record["schema_version"] == 2)
    identity = validate_command_identity(record["command_identity"])
    require("EXECUTION_INPUT_RUN_ID_INVALID", isinstance(record["run_id"], str) and RUN_RE.fullmatch(record["run_id"]) is not None)
    require("EXECUTION_INPUT_EXECUTION_ID_INVALID", isinstance(record["execution_id"], str) and EXECUTION_RE.fullmatch(record["execution_id"]) is not None)
    require("EXECUTION_INPUT_DEMAND_KIND_INVALID", record["demand_kind"] in {"inline", "path"})
    if record["demand_kind"] == "inline":
        require("EXECUTION_INPUT_INLINE_REF_INVALID", record["demand_ref"] is None)
    else:
        validate_project_path(record["demand_ref"], "EXECUTION_INPUT_DEMAND_REF_INVALID")
    validate_project_path(record["analysis_ref"], "EXECUTION_INPUT_ANALYSIS_REF_INVALID")
    require("EXECUTION_INPUT_ANALYSIS_SUFFIX_INVALID", PurePosixPath(record["analysis_ref"]).suffix == ".md")
    for key in ("state_ref", "result_ref", "dashboard_ref", "consistency_packet_ref"):
        require_contained(record[key], identity["plan_directory"], f"EXECUTION_INPUT_{key.upper()}_INVALID")
    return record


HANDOFF_KEYS = {
    "schema_version", "status", "run_id", "execution_id", "plan_directory",
    "execution_input_ref", "execution_input_digest", "automatic_evidence_refs", "pending_human_gate_refs",
    "changed_target_refs", "reason",
}


def validate_manual_qa_handoff(value: Any, *, run_id: str | None = None, execution_id: str | None = None, plan_directory: str | None = None) -> dict[str, Any]:
    handoff = closed("MANUAL_QA_HANDOFF_SHAPE_INVALID", value, HANDOFF_KEYS)
    require("MANUAL_QA_HANDOFF_SCHEMA_INVALID", handoff["schema_version"] == 3)
    require("MANUAL_QA_HANDOFF_STATUS_INVALID", handoff["status"] in {"ready-for-manual-qa", "manual-qa-not-required", "manual-qa-not-evaluated"})
    require("MANUAL_QA_HANDOFF_RUN_ID_INVALID", isinstance(handoff["run_id"], str) and RUN_RE.fullmatch(handoff["run_id"]) is not None)
    require("MANUAL_QA_HANDOFF_EXECUTION_ID_INVALID", isinstance(handoff["execution_id"], str) and EXECUTION_RE.fullmatch(handoff["execution_id"]) is not None)
    validate_project_path(handoff["plan_directory"], "MANUAL_QA_HANDOFF_PLAN_INVALID", below_planos=True)
    require("MANUAL_QA_HANDOFF_IDENTITY_MISMATCH", (run_id is None or handoff["run_id"] == run_id) and (execution_id is None or handoff["execution_id"] == execution_id) and (plan_directory is None or handoff["plan_directory"] == plan_directory))
    require_contained(handoff["execution_input_ref"], handoff["plan_directory"], "MANUAL_QA_HANDOFF_INPUT_REF_INVALID")
    validate_digest(handoff["execution_input_digest"], "MANUAL_QA_HANDOFF_INPUT_DIGEST_INVALID")
    for key in ("automatic_evidence_refs", "pending_human_gate_refs", "changed_target_refs"):
        refs = handoff[key]
        require(f"MANUAL_QA_HANDOFF_{key.upper()}_INVALID", isinstance(refs, list) and len(refs) == len(set(refs)))
        for ref in refs:
            if key != "changed_target_refs":
                require_contained(ref, handoff["plan_directory"], f"MANUAL_QA_HANDOFF_{key.upper()}_INVALID")
            else:
                validate_project_path(ref, f"MANUAL_QA_HANDOFF_{key.upper()}_INVALID")
    if handoff["status"] == "ready-for-manual-qa":
        require("MANUAL_QA_READY_AUTOMATIC_EVIDENCE_EMPTY", bool(handoff["automatic_evidence_refs"]))
        require("MANUAL_QA_READY_HUMAN_GATES_EMPTY", bool(handoff["pending_human_gate_refs"]))
        require("MANUAL_QA_READY_REASON_INVALID", handoff["reason"] is None)
    else:
        require("MANUAL_QA_NONREADY_REASON_INVALID", nonempty(handoff["reason"]))
        require("MANUAL_QA_NONREADY_PENDING_GATES_INVALID", handoff["pending_human_gate_refs"] == [])
    return handoff


def validate_handoff_input_bytes(value: Any) -> None:
    pair = closed("MANUAL_QA_INPUT_PAIR_SHAPE_INVALID", value, {"handoff", "execution_input_text"})
    handoff = validate_manual_qa_handoff(pair["handoff"])
    require("MANUAL_QA_INPUT_TEXT_INVALID", isinstance(pair["execution_input_text"], str) and bool(pair["execution_input_text"]))
    observed = "sha256:" + hashlib.sha256(pair["execution_input_text"].encode("utf-8")).hexdigest()
    require("MANUAL_QA_HANDOFF_INPUT_DIGEST_MISMATCH", handoff["execution_input_digest"] == observed)


GATE_KEYS = {"schema_version", "gate_id", "task_ref", "kind", "instruction", "expected", "status", "evidence_refs"}


def validate_gate_record(value: Any) -> dict[str, Any]:
    gate = closed("GATE_RECORD_SHAPE_INVALID", value, GATE_KEYS)
    require("GATE_RECORD_SCHEMA_INVALID", gate["schema_version"] == 3)
    require("GATE_RECORD_ID_INVALID", nonempty(gate["gate_id"]))
    validate_project_path(gate["task_ref"], "GATE_RECORD_TASK_REF_INVALID")
    require("GATE_RECORD_KIND_INVALID", gate["kind"] in {"automatic", "human-validation"})
    require("GATE_RECORD_INSTRUCTION_INVALID", nonempty(gate["instruction"]))
    require("GATE_RECORD_EXPECTED_INVALID", nonempty(gate["expected"]))
    require("GATE_RECORD_EVIDENCE_INVALID", isinstance(gate["evidence_refs"], list) and len(gate["evidence_refs"]) == len(set(gate["evidence_refs"])))
    if gate["kind"] == "automatic":
        require("AUTOMATIC_GATE_STATUS_INVALID", gate["status"] in {"passed", "not-applicable"})
        require("AUTOMATIC_GATE_EVIDENCE_EMPTY", bool(gate["evidence_refs"]))
    else:
        require("HUMAN_GATE_STATUS_INVALID", gate["status"] in {"pending", "passed"})
        require("HUMAN_GATE_EVIDENCE_FORBIDDEN", gate["evidence_refs"] == [])
    return gate


STATE_KEYS = {
    "schema_version", "run_id", "execution_id", "command_identity_digest", "execution_input_digest",
    "audit_configuration", "status", "task_refs", "gate_refs", "gate_digests",
    "audit_checkpoint_refs", "result_ref", "dashboard_ref", "consistency_packet_ref",
    "terminal_evidence_refs", "manual_qa_handoff", "execution_metrics_ref",
    "execution_metrics_digest", "execution_metrics_status", "execution_metrics_degradation_reason",
    "next_action", "state_digest",
}

RESULT_KEYS = {
    "schema_version", "run_id", "execution_id", "status", "state_digest", "audit_configuration",
    "audit_checkpoint_refs", "gate_refs", "gate_digests", "task_results", "final_validator_refs",
    "terminal_evidence_refs", "manual_qa_handoff", "execution_metrics_ref", "execution_metrics_digest",
    "execution_metrics_status", "execution_metrics_degradation_reason", "next_action", "result_digest",
}

DASHBOARD_KEYS = {
    "schema_version", "run_id", "execution_id", "status", "audit_configuration",
    "audit_checkpoint_refs", "gate_refs", "gate_digests", "tasks", "final_validator_refs",
    "terminal_evidence_refs", "manual_qa_handoff", "execution_metrics_ref", "execution_metrics_digest",
    "execution_metrics_status", "execution_metrics_degradation_reason", "next_action", "dashboard_digest",
}

CONSISTENCY_KEYS = {
    "schema_version", "run_id", "execution_id", "status", "audit_configuration", "state_digest",
    "tasks_md_digest", "result_ref", "result_digest", "dashboard_ref", "dashboard_digest",
    "metrics_ref", "metrics_digest", "gate_refs", "gate_digests", "audit_checkpoint_refs",
    "audit_checkpoint_digests", "terminal_evidence_refs", "terminal_evidence_digests",
    "manual_qa_handoff", "validator_digest",
}

EXECUTION_STATUSES = {"running", "awaiting-manual-qa", "completed", "completed-with-limitations", "partial", "failed", "cancelled"}
TASK_STATUSES = {"pending", "passed", "unresolved", "skipped-dependency", "cancelled"}


def validate_ref_list(value: Any, plan_directory: str, code: str, *, fragment: bool = False) -> list[str]:
    require(code, isinstance(value, list) and len(value) == len(set(value)))
    for ref in value:
        require_contained(ref, plan_directory, code)
        if not fragment:
            require(code, "#" not in ref)
    return value


def validate_metrics_projection(record: dict[str, Any], *, prefix: str) -> None:
    status = record["execution_metrics_status"]
    ref = record["execution_metrics_ref"]
    value_digest = record["execution_metrics_digest"]
    reason = record["execution_metrics_degradation_reason"]
    require(f"{prefix}_METRICS_STATUS_INVALID", status in {"complete", "partial", "unavailable"})
    if status == "complete":
        require(f"{prefix}_METRICS_REASON_INVALID", reason is None)
        require(f"{prefix}_METRICS_REF_INVALID", nonempty(ref))
        validate_digest(value_digest, f"{prefix}_METRICS_DIGEST_INVALID")
    elif status == "partial":
        require(f"{prefix}_METRICS_REASON_INVALID", nonempty(reason))
        require(f"{prefix}_METRICS_REF_INVALID", nonempty(ref))
        validate_digest(value_digest, f"{prefix}_METRICS_DIGEST_INVALID")
    else:
        require(f"{prefix}_METRICS_REASON_INVALID", nonempty(reason))
        publication_failure = "publication failure" in reason.casefold()
        require(f"{prefix}_METRICS_PAIR_INVALID", (ref is None and value_digest is None) if publication_failure else (nonempty(ref) and isinstance(value_digest, str) and SHA256_RE.fullmatch(value_digest) is not None))


def validate_status_handoff(record: dict[str, Any], handoff: dict[str, Any], *, prefix: str) -> None:
    status = record["status"]
    require(f"{prefix}_STATUS_INVALID", status in EXECUTION_STATUSES)
    if status == "awaiting-manual-qa":
        require(f"{prefix}_READY_HANDOFF_REQUIRED", handoff["status"] == "ready-for-manual-qa" and record["next_action"] == "loki-manual-qa")
    elif status == "completed":
        require(f"{prefix}_COMPLETED_HANDOFF_INVALID", handoff["status"] in {"ready-for-manual-qa", "manual-qa-not-required"} and record["next_action"] == "none")
    elif status == "completed-with-limitations":
        require(f"{prefix}_LIMITED_HANDOFF_INVALID", handoff["status"] == "manual-qa-not-required" and record["next_action"] == "none")
    else:
        require(f"{prefix}_NONTERMINAL_HANDOFF_INVALID", handoff["status"] == "manual-qa-not-evaluated" and nonempty(record["next_action"]))


def validate_state(value: Any) -> dict[str, Any]:
    state = closed("STATE_SHAPE_INVALID", value, STATE_KEYS)
    require("STATE_SCHEMA_INVALID", state["schema_version"] == 4)
    require("STATE_RUN_ID_INVALID", isinstance(state["run_id"], str) and RUN_RE.fullmatch(state["run_id"]) is not None)
    require("STATE_EXECUTION_ID_INVALID", isinstance(state["execution_id"], str) and EXECUTION_RE.fullmatch(state["execution_id"]) is not None)
    validate_digest(state["command_identity_digest"], "STATE_COMMAND_IDENTITY_DIGEST_INVALID")
    validate_digest(state["execution_input_digest"], "STATE_EXECUTION_INPUT_DIGEST_INVALID")
    validate_audit_configuration(state["audit_configuration"])
    handoff = validate_manual_qa_handoff(state["manual_qa_handoff"], run_id=state["run_id"], execution_id=state["execution_id"])
    plan_directory = handoff["plan_directory"]
    validate_ref_list(state["task_refs"], plan_directory, "STATE_TASK_REFS_INVALID")
    validate_ref_list(state["gate_refs"], plan_directory, "STATE_GATE_REFS_INVALID", fragment=True)
    validate_ref_list(state["audit_checkpoint_refs"], plan_directory, "STATE_AUDIT_REFS_INVALID")
    validate_ref_list(state["terminal_evidence_refs"], plan_directory, "STATE_TERMINAL_EVIDENCE_REFS_INVALID")
    require("STATE_GATE_DIGESTS_INVALID", isinstance(state["gate_digests"], list) and len(state["gate_digests"]) == len(state["gate_refs"]) and all(SHA256_RE.fullmatch(item or "") for item in state["gate_digests"]))
    for key in ("result_ref", "dashboard_ref", "consistency_packet_ref"):
        require_contained(state[key], plan_directory, f"STATE_{key.upper()}_INVALID")
    require("STATE_HANDOFF_INPUT_DIGEST_MISMATCH", handoff["execution_input_digest"] == state["execution_input_digest"])
    require("STATE_HANDOFF_AUTOMATIC_EVIDENCE_MISMATCH", handoff["automatic_evidence_refs"] == state["terminal_evidence_refs"] or handoff["status"] == "manual-qa-not-evaluated")
    require("STATE_PENDING_GATE_REFS_INVALID", all(ref in state["gate_refs"] for ref in handoff["pending_human_gate_refs"]))
    validate_metrics_projection(state, prefix="STATE")
    if state["execution_metrics_ref"] is not None:
        require_contained(state["execution_metrics_ref"], plan_directory, "STATE_METRICS_REF_INVALID")
    validate_status_handoff(state, handoff, prefix="STATE")
    require("STATE_DIGEST_INVALID", state["state_digest"] == digest(state, omit="state_digest"))
    return state


def validate_shared_output(record: dict[str, Any], *, prefix: str) -> tuple[dict[str, Any], str]:
    require(f"{prefix}_RUN_ID_INVALID", isinstance(record["run_id"], str) and RUN_RE.fullmatch(record["run_id"]) is not None)
    require(f"{prefix}_EXECUTION_ID_INVALID", isinstance(record["execution_id"], str) and EXECUTION_RE.fullmatch(record["execution_id"]) is not None)
    validate_audit_configuration(record["audit_configuration"])
    handoff = validate_manual_qa_handoff(record["manual_qa_handoff"], run_id=record["run_id"], execution_id=record["execution_id"])
    plan_directory = handoff["plan_directory"]
    validate_ref_list(record["audit_checkpoint_refs"], plan_directory, f"{prefix}_AUDIT_REFS_INVALID")
    validate_ref_list(record["gate_refs"], plan_directory, f"{prefix}_GATE_REFS_INVALID", fragment=True)
    require(f"{prefix}_GATE_DIGESTS_INVALID", isinstance(record["gate_digests"], list) and len(record["gate_digests"]) == len(record["gate_refs"]) and all(SHA256_RE.fullmatch(item or "") for item in record["gate_digests"]))
    validate_ref_list(record["final_validator_refs"], plan_directory, f"{prefix}_FINAL_VALIDATOR_REFS_INVALID")
    validate_ref_list(record["terminal_evidence_refs"], plan_directory, f"{prefix}_TERMINAL_EVIDENCE_REFS_INVALID")
    validate_metrics_projection(record, prefix=prefix)
    if record["execution_metrics_ref"] is not None:
        require_contained(record["execution_metrics_ref"], plan_directory, f"{prefix}_METRICS_REF_INVALID")
    validate_status_handoff(record, handoff, prefix=prefix)
    return handoff, plan_directory


def validate_result(value: Any) -> dict[str, Any]:
    result = closed("RESULT_SHAPE_INVALID", value, RESULT_KEYS)
    require("RESULT_SCHEMA_INVALID", result["schema_version"] == 4)
    validate_digest(result["state_digest"], "RESULT_STATE_DIGEST_INVALID")
    _, plan_directory = validate_shared_output(result, prefix="RESULT")
    require("RESULT_TASK_RESULTS_INVALID", isinstance(result["task_results"], list) and bool(result["task_results"]))
    seen: set[str] = set()
    for row in result["task_results"]:
        closed("RESULT_TASK_ROW_SHAPE_INVALID", row, {"task_ref", "status", "evidence_refs"})
        require_contained(row["task_ref"], plan_directory, "RESULT_TASK_REF_INVALID")
        require("RESULT_TASK_DUPLICATE", row["task_ref"] not in seen); seen.add(row["task_ref"])
        require("RESULT_TASK_STATUS_INVALID", row["status"] in TASK_STATUSES)
        validate_ref_list(row["evidence_refs"], plan_directory, "RESULT_TASK_EVIDENCE_INVALID")
    require("RESULT_DIGEST_INVALID", result["result_digest"] == digest(result, omit="result_digest"))
    return result


def validate_dashboard(value: Any) -> dict[str, Any]:
    dashboard = closed("DASHBOARD_SHAPE_INVALID", value, DASHBOARD_KEYS)
    require("DASHBOARD_SCHEMA_INVALID", dashboard["schema_version"] == 4)
    _, plan_directory = validate_shared_output(dashboard, prefix="DASHBOARD")
    require("DASHBOARD_TASKS_INVALID", isinstance(dashboard["tasks"], list) and bool(dashboard["tasks"]))
    seen: set[str] = set()
    for row in dashboard["tasks"]:
        closed("DASHBOARD_TASK_ROW_SHAPE_INVALID", row, {"task_ref", "status"})
        require_contained(row["task_ref"], plan_directory, "DASHBOARD_TASK_REF_INVALID")
        require("DASHBOARD_TASK_DUPLICATE", row["task_ref"] not in seen); seen.add(row["task_ref"])
        require("DASHBOARD_TASK_STATUS_INVALID", row["status"] in TASK_STATUSES)
    require("DASHBOARD_DIGEST_INVALID", dashboard["dashboard_digest"] == digest(dashboard, omit="dashboard_digest"))
    return dashboard


def validate_consistency(value: Any) -> dict[str, Any]:
    packet = closed("CONSISTENCY_SHAPE_INVALID", value, CONSISTENCY_KEYS)
    require("CONSISTENCY_SCHEMA_INVALID", packet["schema_version"] == 3)
    require("CONSISTENCY_RUN_ID_INVALID", isinstance(packet["run_id"], str) and RUN_RE.fullmatch(packet["run_id"]) is not None)
    require("CONSISTENCY_EXECUTION_ID_INVALID", isinstance(packet["execution_id"], str) and EXECUTION_RE.fullmatch(packet["execution_id"]) is not None)
    require("CONSISTENCY_STATUS_INVALID", packet["status"] in EXECUTION_STATUSES)
    validate_audit_configuration(packet["audit_configuration"])
    handoff = validate_manual_qa_handoff(packet["manual_qa_handoff"], run_id=packet["run_id"], execution_id=packet["execution_id"])
    plan_directory = handoff["plan_directory"]
    for key in ("state_digest", "tasks_md_digest", "result_digest", "dashboard_digest", "validator_digest"):
        validate_digest(packet[key], f"CONSISTENCY_{key.upper()}_INVALID")
    for key in ("result_ref", "dashboard_ref"):
        require_contained(packet[key], plan_directory, f"CONSISTENCY_{key.upper()}_INVALID")
    if packet["metrics_ref"] is None:
        require("CONSISTENCY_METRICS_PAIR_INVALID", packet["metrics_digest"] is None)
    else:
        require_contained(packet["metrics_ref"], plan_directory, "CONSISTENCY_METRICS_REF_INVALID")
        validate_digest(packet["metrics_digest"], "CONSISTENCY_METRICS_DIGEST_INVALID")
    validate_ref_list(packet["gate_refs"], plan_directory, "CONSISTENCY_GATE_REFS_INVALID", fragment=True)
    require("CONSISTENCY_GATE_DIGESTS_INVALID", isinstance(packet["gate_digests"], list) and len(packet["gate_digests"]) == len(packet["gate_refs"]) and all(SHA256_RE.fullmatch(item or "") for item in packet["gate_digests"]))
    validate_ref_list(packet["audit_checkpoint_refs"], plan_directory, "CONSISTENCY_AUDIT_REFS_INVALID")
    require("CONSISTENCY_AUDIT_DIGESTS_INVALID", isinstance(packet["audit_checkpoint_digests"], list) and len(packet["audit_checkpoint_digests"]) == len(packet["audit_checkpoint_refs"]) and all(SHA256_RE.fullmatch(item or "") for item in packet["audit_checkpoint_digests"]))
    validate_ref_list(packet["terminal_evidence_refs"], plan_directory, "CONSISTENCY_TERMINAL_REFS_INVALID")
    require("CONSISTENCY_TERMINAL_DIGESTS_INVALID", isinstance(packet["terminal_evidence_digests"], list) and len(packet["terminal_evidence_digests"]) == len(packet["terminal_evidence_refs"]) and all(SHA256_RE.fullmatch(item or "") for item in packet["terminal_evidence_digests"]))
    return packet


def validate_consistency_bundle(value: Any) -> None:
    bundle = closed("BUNDLE_SHAPE_INVALID", value, {"command_identity", "execution_input_text", "tasks_md_text", "validator_digests", "state", "result", "dashboard", "consistency"})
    identity = validate_command_identity(bundle["command_identity"])
    require("BUNDLE_INPUT_TEXT_INVALID", isinstance(bundle["execution_input_text"], str) and bool(bundle["execution_input_text"]))
    require("BUNDLE_TASKS_TEXT_INVALID", isinstance(bundle["tasks_md_text"], str) and bool(bundle["tasks_md_text"]))
    require("BUNDLE_VALIDATOR_DIGESTS_INVALID", isinstance(bundle["validator_digests"], dict) and all(nonempty(k) and isinstance(v, str) and SHA256_RE.fullmatch(v) for k, v in bundle["validator_digests"].items()))
    state = validate_state(bundle["state"]); result = validate_result(bundle["result"]); dashboard = validate_dashboard(bundle["dashboard"]); packet = validate_consistency(bundle["consistency"])
    expected_input_digest = "sha256:" + hashlib.sha256(bundle["execution_input_text"].encode("utf-8")).hexdigest()
    require("BUNDLE_COMMAND_IDENTITY_DIGEST_MISMATCH", state["command_identity_digest"] == digest(identity))
    require("BUNDLE_EXECUTION_INPUT_DIGEST_MISMATCH", state["execution_input_digest"] == expected_input_digest == state["manual_qa_handoff"]["execution_input_digest"])
    for projection, prefix in ((result, "RESULT"), (dashboard, "DASHBOARD"), (packet, "CONSISTENCY")):
        require(f"BUNDLE_{prefix}_IDENTITY_MISMATCH", (projection["run_id"], projection["execution_id"]) == (state["run_id"], state["execution_id"]))
        require(f"BUNDLE_{prefix}_STATUS_MISMATCH", projection["status"] == state["status"])
        require(f"BUNDLE_{prefix}_AUDIT_CONFIGURATION_MISMATCH", projection["audit_configuration"] == state["audit_configuration"])
        require(f"BUNDLE_{prefix}_GATE_PARITY_MISMATCH", projection["gate_refs"] == state["gate_refs"] and projection["gate_digests"] == state["gate_digests"])
        require(f"BUNDLE_{prefix}_HANDOFF_MISMATCH", projection["manual_qa_handoff"] == state["manual_qa_handoff"])
    require("BUNDLE_RESULT_STATE_DIGEST_MISMATCH", result["state_digest"] == state["state_digest"])
    require("BUNDLE_TASK_PARITY_MISMATCH", [{"task_ref": row["task_ref"], "status": row["status"]} for row in result["task_results"]] == dashboard["tasks"])
    require("BUNDLE_AUDIT_REFS_MISMATCH", result["audit_checkpoint_refs"] == dashboard["audit_checkpoint_refs"] == packet["audit_checkpoint_refs"] == state["audit_checkpoint_refs"])
    require("BUNDLE_TERMINAL_REFS_MISMATCH", result["terminal_evidence_refs"] == dashboard["terminal_evidence_refs"] == packet["terminal_evidence_refs"] == state["terminal_evidence_refs"])
    require("BUNDLE_METRICS_PARITY_MISMATCH", (result["execution_metrics_ref"], result["execution_metrics_digest"], result["execution_metrics_status"], result["execution_metrics_degradation_reason"]) == (dashboard["execution_metrics_ref"], dashboard["execution_metrics_digest"], dashboard["execution_metrics_status"], dashboard["execution_metrics_degradation_reason"]) == (state["execution_metrics_ref"], state["execution_metrics_digest"], state["execution_metrics_status"], state["execution_metrics_degradation_reason"]))
    require("BUNDLE_CONSISTENCY_STATE_DIGEST_MISMATCH", packet["state_digest"] == state["state_digest"])
    require("BUNDLE_CONSISTENCY_TASKS_DIGEST_MISMATCH", packet["tasks_md_digest"] == "sha256:" + hashlib.sha256(bundle["tasks_md_text"].encode("utf-8")).hexdigest())
    require("BUNDLE_CONSISTENCY_RESULT_REF_MISMATCH", packet["result_ref"] == state["result_ref"])
    require("BUNDLE_CONSISTENCY_RESULT_DIGEST_MISMATCH", packet["result_digest"] == "sha256:" + hashlib.sha256(canonical_bytes(result)).hexdigest())
    require("BUNDLE_CONSISTENCY_DASHBOARD_REF_MISMATCH", packet["dashboard_ref"] == state["dashboard_ref"])
    require("BUNDLE_CONSISTENCY_DASHBOARD_DIGEST_MISMATCH", packet["dashboard_digest"] == "sha256:" + hashlib.sha256(canonical_bytes(dashboard)).hexdigest())
    require("BUNDLE_CONSISTENCY_METRICS_MISMATCH", (packet["metrics_ref"], packet["metrics_digest"]) == (state["execution_metrics_ref"], state["execution_metrics_digest"]))
    require("BUNDLE_AUDIT_DIGEST_COUNT_MISMATCH", len(packet["audit_checkpoint_digests"]) == len(state["audit_checkpoint_refs"]))
    require("BUNDLE_TERMINAL_DIGEST_COUNT_MISMATCH", len(packet["terminal_evidence_digests"]) == len(state["terminal_evidence_refs"]))
    require("BUNDLE_VALIDATOR_DIGEST_MISMATCH", packet["validator_digest"] == digest(bundle["validator_digests"]))


def canonical_fixture_bundle() -> dict[str, Any]:
    plan = "planos/p"
    run_id = "loki-run-v2:" + "a" * 64
    execution_id = "loki-execution-v2:" + "b" * 64
    audit = {"schema_version": 1, "frequency": "phase", "source": "default", "policy_digest": "sha256:e3aeea217ca7881865de40d29e0e28e95bc32f4255e2488597801a8909e3bd78"}
    identity = {"schema_version": 2, "command": "loki-implement-feature", "demand_digest": "sha256:" + "1" * 64, "analysis_digest": "sha256:" + "2" * 64, "plan_directory": plan, "retry_limit": 3, "audit_configuration": audit}
    execution_input_text = '{"schema_version":2}'
    input_digest = "sha256:" + hashlib.sha256(execution_input_text.encode("utf-8")).hexdigest()
    gate_ref = f"{plan}/task-1.md#gate:g1"
    terminal_ref = f"{plan}/builds/automatic.json"
    audit_ref = f"{plan}/builds/audit.json"
    metrics_ref = f"{plan}/builds/metrics/execution-metrics.json"
    handoff = {"schema_version": 3, "status": "ready-for-manual-qa", "run_id": run_id, "execution_id": execution_id, "plan_directory": plan, "execution_input_ref": f"{plan}/builds/execution-input-v2.json", "execution_input_digest": input_digest, "automatic_evidence_refs": [terminal_ref], "pending_human_gate_refs": [gate_ref], "changed_target_refs": ["src/app.py"], "reason": None}
    state = {"schema_version": 4, "run_id": run_id, "execution_id": execution_id, "command_identity_digest": digest(identity), "execution_input_digest": input_digest, "audit_configuration": audit, "status": "awaiting-manual-qa", "task_refs": [f"{plan}/task-1.md"], "gate_refs": [gate_ref], "gate_digests": ["sha256:" + "3" * 64], "audit_checkpoint_refs": [audit_ref], "result_ref": f"{plan}/builds/result.json", "dashboard_ref": f"{plan}/builds/dashboard.json", "consistency_packet_ref": f"{plan}/builds/consistency.json", "terminal_evidence_refs": [terminal_ref], "manual_qa_handoff": handoff, "execution_metrics_ref": metrics_ref, "execution_metrics_digest": "sha256:" + "4" * 64, "execution_metrics_status": "complete", "execution_metrics_degradation_reason": None, "next_action": "loki-manual-qa", "state_digest": ""}
    state["state_digest"] = digest(state, omit="state_digest")
    result = {"schema_version": 4, "run_id": run_id, "execution_id": execution_id, "status": state["status"], "state_digest": state["state_digest"], "audit_configuration": audit, "audit_checkpoint_refs": [audit_ref], "gate_refs": [gate_ref], "gate_digests": list(state["gate_digests"]), "task_results": [{"task_ref": f"{plan}/task-1.md", "status": "passed", "evidence_refs": [f"{plan}/builds/task-evidence.json"]}], "final_validator_refs": [f"{plan}/builds/final-validator.json"], "terminal_evidence_refs": [terminal_ref], "manual_qa_handoff": handoff, "execution_metrics_ref": metrics_ref, "execution_metrics_digest": state["execution_metrics_digest"], "execution_metrics_status": "complete", "execution_metrics_degradation_reason": None, "next_action": "loki-manual-qa", "result_digest": ""}
    result["result_digest"] = digest(result, omit="result_digest")
    dashboard = {"schema_version": 4, "run_id": run_id, "execution_id": execution_id, "status": state["status"], "audit_configuration": audit, "audit_checkpoint_refs": [audit_ref], "gate_refs": [gate_ref], "gate_digests": list(state["gate_digests"]), "tasks": [{"task_ref": f"{plan}/task-1.md", "status": "passed"}], "final_validator_refs": [f"{plan}/builds/final-validator.json"], "terminal_evidence_refs": [terminal_ref], "manual_qa_handoff": handoff, "execution_metrics_ref": metrics_ref, "execution_metrics_digest": state["execution_metrics_digest"], "execution_metrics_status": "complete", "execution_metrics_degradation_reason": None, "next_action": "loki-manual-qa", "dashboard_digest": ""}
    dashboard["dashboard_digest"] = digest(dashboard, omit="dashboard_digest")
    validator_digests = {f"{plan}/builds/primary-validator.json": "sha256:" + "5" * 64, f"{plan}/builds/final-validator.json": "sha256:" + "6" * 64}
    tasks_md_text = "# Canonical fixture tasks v4\n"
    consistency = {"schema_version": 3, "run_id": run_id, "execution_id": execution_id, "status": state["status"], "audit_configuration": audit, "state_digest": state["state_digest"], "tasks_md_digest": "sha256:" + hashlib.sha256(tasks_md_text.encode("utf-8")).hexdigest(), "result_ref": state["result_ref"], "result_digest": "sha256:" + hashlib.sha256(canonical_bytes(result)).hexdigest(), "dashboard_ref": state["dashboard_ref"], "dashboard_digest": "sha256:" + hashlib.sha256(canonical_bytes(dashboard)).hexdigest(), "metrics_ref": metrics_ref, "metrics_digest": state["execution_metrics_digest"], "gate_refs": [gate_ref], "gate_digests": list(state["gate_digests"]), "audit_checkpoint_refs": [audit_ref], "audit_checkpoint_digests": ["sha256:" + "7" * 64], "terminal_evidence_refs": [terminal_ref], "terminal_evidence_digests": ["sha256:" + "8" * 64], "manual_qa_handoff": handoff, "validator_digest": digest(validator_digests)}
    return {"command_identity": identity, "execution_input_text": execution_input_text, "tasks_md_text": tasks_md_text, "validator_digests": validator_digests, "state": state, "result": result, "dashboard": dashboard, "consistency": consistency}


def fixture_payload(case: dict[str, Any]) -> Any:
    factory = case.get("factory")
    if factory is None:
        return case["input"]
    bundle = canonical_fixture_bundle()
    if factory == "state": payload = bundle["state"]
    elif factory == "result": payload = bundle["result"]
    elif factory == "dashboard": payload = bundle["dashboard"]
    elif factory == "consistency": payload = bundle["consistency"]
    elif factory == "consistency-bundle": payload = bundle
    else: raise ContractError("FIXTURE_FACTORY_INVALID")
    mutation = case.get("mutation", "none")
    if mutation == "none": return payload
    target_name, _, operation = mutation.partition(":")
    if operation == "input-drift":
        payload["execution_input_text"] = '{"schema_version":2,"drift":true}'
        return payload
    target = payload[target_name] if factory == "consistency-bundle" else payload
    if operation.startswith("remove-"):
        target.pop(operation.removeprefix("remove-"), None)
    elif operation.startswith("extra-"):
        target[operation.removeprefix("extra-")] = "unexpected"
    elif operation == "status-divergence":
        target["status"] = "completed"; target["next_action"] = "none"; target["dashboard_digest"] = digest(target, omit="dashboard_digest")
    elif operation == "gate-divergence":
        target["gate_digests"] = ["sha256:" + "9" * 64]; target["dashboard_digest"] = digest(target, omit="dashboard_digest")
    else:
        raise ContractError("FIXTURE_MUTATION_INVALID")
    return payload


def load_cases(name: str) -> list[dict[str, Any]]:
    document = json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
    require("FIXTURE_ROOT_INVALID", isinstance(document, dict) and set(document) == {"schema_version", "cases"} and document["schema_version"] == 1)
    require("FIXTURE_CASES_INVALID", isinstance(document["cases"], list) and bool(document["cases"]))
    return document["cases"]


VALIDATORS = {
    "execution-input": validate_execution_input,
    "handoff": validate_manual_qa_handoff,
    "handoff-input-bytes": validate_handoff_input_bytes,
    "gate": validate_gate_record,
    "state": validate_state,
    "result": validate_result,
    "dashboard": validate_dashboard,
    "consistency": validate_consistency,
    "consistency-bundle": validate_consistency_bundle,
}


def self_test() -> dict[str, Any]:
    cases = [case for name in FIXTURE_FILES for case in load_cases(name)]
    seen: set[str] = set()
    results = []
    for case in cases:
        require("FIXTURE_ID_INVALID", nonempty(case.get("id")) and case["id"] not in seen)
        seen.add(case["id"])
        require("FIXTURE_VALIDATOR_INVALID", case.get("validator") in VALIDATORS)
        require("FIXTURE_EXPECTATION_INVALID", case.get("accept") in {True, False})
        try:
            VALIDATORS[case["validator"]](fixture_payload(case))
            accepted, error = True, None
        except (ContractError, KeyError, TypeError) as exc:
            accepted, error = False, str(exc)
        require(f"FIXTURE_OUTCOME_MISMATCH:{case['id']}:{error}", accepted is case["accept"])
        if not accepted and case.get("error"):
            require(f"FIXTURE_ERROR_MISMATCH:{case['id']}:{case['error']}:{error}", error == case["error"])
        results.append({"id": case["id"], "result": "accepted" if accepted else "expected-rejection", "error": error})
    require("FIXTURE_VALIDATOR_COVERAGE_INVALID", {case["validator"] for case in cases} == set(VALIDATORS))
    return {"schema_version": 1, "status": "passed", "fixture_files": list(FIXTURE_FILES), "cases_executed": len(results), "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--record", choices=sorted(VALIDATORS))
    parser.add_argument("path", nargs="?")
    args = parser.parse_args()
    require("CLI_MODE_INVALID", sum((args.self_test, bool(args.record))) == 1)
    try:
        if args.self_test:
            result = self_test()
        else:
            require("CLI_PATH_REQUIRED", nonempty(args.path))
            VALIDATORS[args.record](json.loads(Path(args.path).read_text(encoding="utf-8")))
            result = {"schema_version": 1, "status": "passed", "record": args.record}
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    except (ContractError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
