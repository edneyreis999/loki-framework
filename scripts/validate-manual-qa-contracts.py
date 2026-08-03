#!/usr/bin/env python3
"""Validate the current direct-playtest loki-manual-qa contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "scripts/fixtures/manual-qa"
FIXTURE_FILES = ("record-cases.json", "transition-cases.json", "tree-cases.json")
HEX = r"[0-9a-f]{64}"
RUN_RE = re.compile(rf"loki-run-v2:{HEX}\Z")
EXEC_RE = re.compile(rf"loki-execution-v2:{HEX}\Z")
DIGEST_RE = re.compile(rf"sha256:{HEX}\Z")
CHECKLIST_ID_RE = re.compile(r"MQ-(?:0[1-9]|[1-9][0-9]+)\Z")
ZERO_WRITE_KINDS = {"blocked-preflight", "not-applicable", "problem", "help", "no-decision"}
PROBLEM_PHRASES = ("failed", "failure", "blocker", "broken", "falhou", "erro", "bloqueio", "quebrou")
NEGATION_RE = re.compile(r"\b(?:not|never|didnt|did not|have not|havent|nao|nunca)\b")
FUTURE_RE = re.compile(r"\b(?:will test|going to test|testarei|vou testar|later|depois|ainda vou)\b")
PARTIAL_RE = re.compile(r"\b(?:some|part|partially|only|alguns|algumas|parte|parcialmente|so)\b")
UNCERTAIN_RE = re.compile(r"\b(?:maybe|probably|i think|perhaps|talvez|acho|parece)\b")
HELP_RE = re.compile(r"\b(?:how|help|explain|como|ajuda|explique)\b.*\bMQ-(?:0[1-9]|[1-9][0-9]+)\b", re.IGNORECASE)
EN_TESTED_RE = re.compile(r"\b(?:tested|completed|ran|finished)\b")
EN_AGGREGATE_RE = re.compile(r"\b(?:all|everything|entire|whole|full)\b")
EN_SUCCESS_RE = re.compile(r"\b(?:passed|worked|successful|approved|no issues)\b")
PT_TESTED_RE = re.compile(r"\b(?:testei|executei|conclui|finalizei)\b")
PT_AGGREGATE_RE = re.compile(r"\b(?:tudo|todos|todas|completo|completa|aplicavel)\b")
PT_SUCCESS_RE = re.compile(r"\b(?:passou|aprovado|aprovada|funcionou|sucesso|sem problemas)\b")


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


def validate_plan_path(value: Any, code: str = "PLAN_DIRECTORY_INVALID") -> None:
    require(code, nonempty(value) and "\\" not in value and "#" not in value)
    pure = PurePosixPath(value)
    require(code, not pure.is_absolute() and ".." not in pure.parts and "." not in pure.parts)
    require(code, len(pure.parts) >= 2 and pure.parts[0] == "planos")


def validate_locator(value: Any, plan_directory: str, code: str) -> None:
    require(code, nonempty(value) and "\\" not in value)
    path = value.partition("#")[0]
    pure = PurePosixPath(path)
    root = PurePosixPath(plan_directory)
    require(code, not pure.is_absolute() and ".." not in pure.parts and "." not in pure.parts)
    require(code, pure == root or root in pure.parents)


HANDOFF_KEYS = {
    "schema_version", "status", "run_id", "execution_id", "plan_directory",
    "execution_input_ref", "execution_input_digest", "automatic_evidence_refs", "pending_human_gate_refs",
    "changed_target_refs", "reason",
}


def validate_handoff(value: Any) -> dict[str, Any]:
    handoff = closed("HANDOFF_SHAPE_INVALID", value, HANDOFF_KEYS)
    require("HANDOFF_SCHEMA_INVALID", handoff["schema_version"] == 3)
    require("HANDOFF_STATUS_INVALID", handoff["status"] in {"ready-for-manual-qa", "manual-qa-not-required", "manual-qa-not-evaluated"})
    require("HANDOFF_RUN_ID_INVALID", isinstance(handoff["run_id"], str) and RUN_RE.fullmatch(handoff["run_id"]) is not None)
    require("HANDOFF_EXECUTION_ID_INVALID", isinstance(handoff["execution_id"], str) and EXEC_RE.fullmatch(handoff["execution_id"]) is not None)
    validate_plan_path(handoff["plan_directory"])
    validate_locator(handoff["execution_input_ref"], handoff["plan_directory"], "HANDOFF_INPUT_REF_INVALID")
    require("HANDOFF_INPUT_DIGEST_INVALID", isinstance(handoff["execution_input_digest"], str) and DIGEST_RE.fullmatch(handoff["execution_input_digest"]) is not None)
    for key in ("automatic_evidence_refs", "pending_human_gate_refs", "changed_target_refs"):
        refs = handoff[key]
        require(f"HANDOFF_{key.upper()}_INVALID", isinstance(refs, list) and len(refs) == len(set(refs)))
        for ref in refs:
            if key == "changed_target_refs":
                require(f"HANDOFF_{key.upper()}_INVALID", nonempty(ref) and "\\" not in ref and "#" not in ref)
                pure = PurePosixPath(ref)
                require(f"HANDOFF_{key.upper()}_INVALID", not pure.is_absolute() and ".." not in pure.parts and "." not in pure.parts)
            else:
                validate_locator(ref, handoff["plan_directory"], f"HANDOFF_{key.upper()}_INVALID")
    if handoff["status"] == "ready-for-manual-qa":
        require("HANDOFF_READY_EVIDENCE_EMPTY", bool(handoff["automatic_evidence_refs"]))
        require("HANDOFF_READY_HUMAN_GATES_EMPTY", bool(handoff["pending_human_gate_refs"]))
        require("HANDOFF_READY_REASON_INVALID", handoff["reason"] is None)
    else:
        require("HANDOFF_NONREADY_REASON_INVALID", nonempty(handoff["reason"]))
        require("HANDOFF_NONREADY_PENDING_GATES_INVALID", handoff["pending_human_gate_refs"] == [])
        if handoff["status"] == "manual-qa-not-required":
            require("HANDOFF_NOT_REQUIRED_EVIDENCE_EMPTY", bool(handoff["automatic_evidence_refs"]))
    return handoff


def validate_handoff_input_bytes(value: Any) -> None:
    pair = closed("HANDOFF_INPUT_PAIR_SHAPE_INVALID", value, {"handoff", "execution_input_text"})
    handoff = validate_handoff(pair["handoff"])
    require("HANDOFF_INPUT_TEXT_INVALID", isinstance(pair["execution_input_text"], str) and bool(pair["execution_input_text"]))
    observed = "sha256:" + hashlib.sha256(pair["execution_input_text"].encode("utf-8")).hexdigest()
    require("HANDOFF_INPUT_DIGEST_MISMATCH", handoff["execution_input_digest"] == observed)


GATE_KEYS = {"schema_version", "gate_id", "task_ref", "kind", "instruction", "expected", "status", "evidence_refs"}


def validate_gate(value: Any) -> dict[str, Any]:
    gate = closed("GATE_SHAPE_INVALID", value, GATE_KEYS)
    require("GATE_SCHEMA_INVALID", gate["schema_version"] == 3)
    require("GATE_ID_INVALID", nonempty(gate["gate_id"]))
    require("GATE_TASK_REF_INVALID", nonempty(gate["task_ref"]))
    require("GATE_KIND_INVALID", gate["kind"] in {"automatic", "human-validation"})
    require("GATE_INSTRUCTION_INVALID", nonempty(gate["instruction"]))
    require("GATE_EXPECTED_INVALID", nonempty(gate["expected"]))
    require("GATE_EVIDENCE_INVALID", isinstance(gate["evidence_refs"], list) and len(gate["evidence_refs"]) == len(set(gate["evidence_refs"])))
    if gate["kind"] == "automatic":
        require("AUTOMATIC_GATE_STATUS_INVALID", gate["status"] in {"passed", "not-applicable"})
        require("AUTOMATIC_GATE_EVIDENCE_EMPTY", bool(gate["evidence_refs"]))
    else:
        require("HUMAN_GATE_STATUS_INVALID", gate["status"] in {"pending", "passed"})
        require("HUMAN_GATE_EVIDENCE_FORBIDDEN", gate["evidence_refs"] == [])
    return gate


EVIDENCE_KEYS = {"schema_version", "control_id", "status", "evidence_ref", "evidence_digest"}


def validate_automatic_evidence(value: Any) -> dict[str, Any]:
    row = closed("AUTOMATIC_EVIDENCE_SHAPE_INVALID", value, EVIDENCE_KEYS)
    require("AUTOMATIC_EVIDENCE_SCHEMA_INVALID", row["schema_version"] == 1)
    require("AUTOMATIC_EVIDENCE_ID_INVALID", nonempty(row["control_id"]))
    require("AUTOMATIC_EVIDENCE_STATUS_INVALID", row["status"] in {"passed", "not-applicable"})
    require("AUTOMATIC_EVIDENCE_REF_INVALID", nonempty(row["evidence_ref"]))
    require("AUTOMATIC_EVIDENCE_DIGEST_INVALID", isinstance(row["evidence_digest"], str) and DIGEST_RE.fullmatch(row["evidence_digest"]) is not None)
    return row


STATE_KEYS = {
    "schema_version", "run_id", "execution_id", "command_identity_digest", "execution_input_digest",
    "audit_configuration", "status", "task_refs", "gate_refs", "gate_digests",
    "audit_checkpoint_refs", "result_ref", "dashboard_ref", "consistency_packet_ref",
    "terminal_evidence_refs", "manual_qa_handoff", "execution_metrics_ref",
    "execution_metrics_digest", "execution_metrics_status", "execution_metrics_degradation_reason",
    "next_action", "state_digest",
}
AUDIT_KEYS = {"schema_version", "frequency", "source", "policy_digest"}
ADMISSION_KEYS = {"state", "execution_input_text", "automatic_evidence", "gate_records"}
ADMISSION_AUTOMATIC_KEYS = {"ref", "record", "evidence_text"}
ADMISSION_GATE_KEYS = {"ref", "record"}


def validate_audit_configuration(value: Any) -> dict[str, Any]:
    audit = closed("ADMISSION_AUDIT_SHAPE_INVALID", value, AUDIT_KEYS)
    require("ADMISSION_AUDIT_SCHEMA_INVALID", audit["schema_version"] == 1)
    require("ADMISSION_AUDIT_FREQUENCY_INVALID", audit["frequency"] in {"task", "phase", "plan"})
    require("ADMISSION_AUDIT_SOURCE_INVALID", audit["source"] in {"default", "explicit"})
    require("ADMISSION_AUDIT_DEFAULT_INVALID", not (audit["source"] == "default" and audit["frequency"] != "phase"))
    expected = digest({"schema_version": 1, "frequency": audit["frequency"], "source": audit["source"]})
    require("ADMISSION_AUDIT_POLICY_DIGEST_INVALID", audit["policy_digest"] == expected)
    return audit


def validate_state_ref_list(value: Any, plan_directory: str, code: str) -> list[str]:
    require(code, isinstance(value, list) and len(value) == len(set(value)))
    for ref in value:
        validate_locator(ref, plan_directory, code)
    return value


def validate_admission(value: Any) -> dict[str, Any]:
    packet = closed("ADMISSION_SHAPE_INVALID", value, ADMISSION_KEYS)
    state = closed("ADMISSION_STATE_SHAPE_INVALID", packet["state"], STATE_KEYS)
    require("ADMISSION_STATE_SCHEMA_INVALID", state["schema_version"] == 4)
    require("ADMISSION_STATE_RUN_ID_INVALID", isinstance(state["run_id"], str) and RUN_RE.fullmatch(state["run_id"]) is not None)
    require("ADMISSION_STATE_EXECUTION_ID_INVALID", isinstance(state["execution_id"], str) and EXEC_RE.fullmatch(state["execution_id"]) is not None)
    require("ADMISSION_COMMAND_IDENTITY_DIGEST_INVALID", isinstance(state["command_identity_digest"], str) and DIGEST_RE.fullmatch(state["command_identity_digest"]) is not None)
    require("ADMISSION_STATE_INPUT_DIGEST_INVALID", isinstance(state["execution_input_digest"], str) and DIGEST_RE.fullmatch(state["execution_input_digest"]) is not None)
    validate_audit_configuration(state["audit_configuration"])

    handoff = validate_handoff(state["manual_qa_handoff"])
    plan_directory = handoff["plan_directory"]
    require(
        "ADMISSION_IDENTITY_MISMATCH",
        (handoff["run_id"], handoff["execution_id"]) == (state["run_id"], state["execution_id"]),
    )
    require("ADMISSION_INPUT_TEXT_INVALID", isinstance(packet["execution_input_text"], str) and bool(packet["execution_input_text"]))
    observed_input_digest = "sha256:" + hashlib.sha256(packet["execution_input_text"].encode("utf-8")).hexdigest()
    require(
        "ADMISSION_INPUT_DIGEST_MISMATCH",
        observed_input_digest == handoff["execution_input_digest"] == state["execution_input_digest"],
    )

    for key in ("task_refs", "gate_refs", "audit_checkpoint_refs", "terminal_evidence_refs"):
        validate_state_ref_list(state[key], plan_directory, f"ADMISSION_{key.upper()}_INVALID")
    require(
        "ADMISSION_GATE_DIGESTS_INVALID",
        isinstance(state["gate_digests"], list)
        and len(state["gate_digests"]) == len(state["gate_refs"])
        and all(isinstance(item, str) and DIGEST_RE.fullmatch(item) is not None for item in state["gate_digests"]),
    )
    for key in ("result_ref", "dashboard_ref", "consistency_packet_ref"):
        validate_locator(state[key], plan_directory, f"ADMISSION_{key.upper()}_INVALID")
    require(
        "ADMISSION_TERMINAL_EVIDENCE_MISMATCH",
        state["terminal_evidence_refs"] == handoff["automatic_evidence_refs"],
    )

    require("ADMISSION_AUTOMATIC_EVIDENCE_INVALID", isinstance(packet["automatic_evidence"], list))
    automatic_refs: list[str] = []
    for value_entry in packet["automatic_evidence"]:
        entry = closed("ADMISSION_AUTOMATIC_ENTRY_SHAPE_INVALID", value_entry, ADMISSION_AUTOMATIC_KEYS)
        validate_locator(entry["ref"], plan_directory, "ADMISSION_AUTOMATIC_REF_INVALID")
        require("ADMISSION_AUTOMATIC_REF_DUPLICATE", entry["ref"] not in automatic_refs)
        automatic_refs.append(entry["ref"])
        record = validate_automatic_evidence(entry["record"])
        validate_locator(record["evidence_ref"], plan_directory, "ADMISSION_AUTOMATIC_EVIDENCE_REF_INVALID")
        require("ADMISSION_AUTOMATIC_TEXT_INVALID", isinstance(entry["evidence_text"], str) and bool(entry["evidence_text"]))
        observed_evidence_digest = "sha256:" + hashlib.sha256(entry["evidence_text"].encode("utf-8")).hexdigest()
        require("ADMISSION_AUTOMATIC_EVIDENCE_DIGEST_MISMATCH", record["evidence_digest"] == observed_evidence_digest)
    require("ADMISSION_AUTOMATIC_COVERAGE_MISMATCH", automatic_refs == handoff["automatic_evidence_refs"])

    require("ADMISSION_GATE_RECORDS_INVALID", isinstance(packet["gate_records"], list))
    gate_refs: list[str] = []
    gate_records: list[dict[str, Any]] = []
    for value_entry in packet["gate_records"]:
        entry = closed("ADMISSION_GATE_ENTRY_SHAPE_INVALID", value_entry, ADMISSION_GATE_KEYS)
        validate_locator(entry["ref"], plan_directory, "ADMISSION_GATE_REF_INVALID")
        require("ADMISSION_GATE_REF_DUPLICATE", entry["ref"] not in gate_refs)
        gate_refs.append(entry["ref"])
        record = validate_gate(entry["record"])
        validate_locator(record["task_ref"], plan_directory, "ADMISSION_GATE_TASK_REF_INVALID")
        gate_records.append(record)
    require("ADMISSION_GATE_COVERAGE_MISMATCH", gate_refs == state["gate_refs"])
    require(
        "ADMISSION_GATE_DIGEST_MISMATCH",
        state["gate_digests"] == [digest(record) for record in gate_records],
    )

    if state["status"] == "awaiting-manual-qa":
        require("ADMISSION_AWAITING_HANDOFF_INVALID", handoff["status"] == "ready-for-manual-qa")
        require("ADMISSION_AWAITING_NEXT_ACTION_INVALID", state["next_action"] == "loki-manual-qa")
        pending_refs = [
            ref for ref, record in zip(gate_refs, gate_records)
            if record["kind"] == "human-validation" and record["status"] == "pending"
        ]
        require("ADMISSION_READY_PENDING_GATES_INVALID", bool(pending_refs) and pending_refs == handoff["pending_human_gate_refs"])
        route = {"status": "ready-for-playtest", "writes": 0, "checklist": True, "feedback_prompt": False}
    elif state["status"] in {"completed", "completed-with-limitations"}:
        require("ADMISSION_TERMINAL_HANDOFF_INVALID", handoff["status"] == "manual-qa-not-required")
        require("ADMISSION_TERMINAL_NEXT_ACTION_INVALID", state["next_action"] == "none")
        require("ADMISSION_TERMINAL_HUMAN_GATE_INVALID", all(record["kind"] != "human-validation" for record in gate_records))
        route = {"status": "not-applicable", "writes": 0, "checklist": False, "feedback_prompt": False}
    else:
        raise ContractError("ADMISSION_STATE_STATUS_INVALID")

    require("ADMISSION_STATE_DIGEST_INVALID", state["state_digest"] == digest(state, omit="state_digest"))
    return route


CANDIDATE_KEYS = {
    "source_ref", "instruction", "expected", "demand_relevance", "regression_risk",
    "changed_target_order", "source_order",
}


def validate_candidate(value: Any) -> dict[str, Any]:
    row = closed("DERIVED_CANDIDATE_SHAPE_INVALID", value, CANDIDATE_KEYS)
    require("DERIVED_CANDIDATE_SOURCE_INVALID", nonempty(row["source_ref"]))
    require("DERIVED_CANDIDATE_INSTRUCTION_INVALID", nonempty(row["instruction"]))
    require("DERIVED_CANDIDATE_EXPECTED_INVALID", nonempty(row["expected"]))
    require("DERIVED_CANDIDATE_RELEVANCE_INVALID", isinstance(row["demand_relevance"], int) and 0 <= row["demand_relevance"] <= 2)
    require("DERIVED_CANDIDATE_RISK_INVALID", isinstance(row["regression_risk"], int) and 0 <= row["regression_risk"] <= 2)
    require("DERIVED_CANDIDATE_TARGET_ORDER_INVALID", isinstance(row["changed_target_order"], int) and row["changed_target_order"] >= 0)
    require("DERIVED_CANDIDATE_SOURCE_ORDER_INVALID", isinstance(row["source_order"], int) and row["source_order"] >= 0)
    return row


def derive_checklist(human_gates: Any, candidates: Any) -> list[dict[str, str]]:
    require("CHECKLIST_HUMAN_GATES_INVALID", isinstance(human_gates, list) and bool(human_gates))
    gates = [validate_gate(item) for item in human_gates]
    require("CHECKLIST_NONPENDING_HUMAN_GATE", all(item["kind"] == "human-validation" and item["status"] == "pending" for item in gates))
    require("CHECKLIST_CANDIDATES_INVALID", isinstance(candidates, list))
    derived = [validate_candidate(item) for item in candidates]
    derived.sort(key=lambda item: (-item["demand_relevance"], -item["regression_risk"], item["changed_target_order"], item["source_order"]))
    selected: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in derived:
        semantic_key = (item["instruction"].strip().casefold(), item["expected"].strip().casefold())
        if semantic_key in seen:
            continue
        seen.add(semantic_key)
        selected.append(item)
        if len(selected) == 5:
            break
    checklist = []
    for gate in gates:
        checklist.append({"id": f"MQ-{len(checklist) + 1:02d}", "kind": "human-gate", "instruction": gate["instruction"], "expected": gate["expected"]})
    for item in selected:
        checklist.append({"id": f"MQ-{len(checklist) + 1:02d}", "kind": "derived-test", "instruction": item["instruction"], "expected": item["expected"]})
    require("CHECKLIST_ID_INVALID", all(CHECKLIST_ID_RE.fullmatch(item["id"]) for item in checklist))
    require("CHECKLIST_DERIVED_LIMIT_EXCEEDED", sum(item["kind"] == "derived-test" for item in checklist) <= 5)
    return checklist


def classify_response(text: Any, *, help_id: str | None = None) -> str:
    if help_id is not None:
        require("HELP_ID_INVALID", CHECKLIST_ID_RE.fullmatch(help_id) is not None)
        return "help"
    if not nonempty(text):
        return "no-decision"
    raw_normalized = " ".join(text.strip().split())
    normalized = unicodedata.normalize("NFKD", raw_normalized.casefold()).encode("ascii", "ignore").decode("ascii")
    if any(token in normalized for token in PROBLEM_PHRASES):
        return "problem"
    if HELP_RE.search(raw_normalized):
        return "help"
    if NEGATION_RE.search(normalized) or FUTURE_RE.search(normalized) or PARTIAL_RE.search(normalized) or UNCERTAIN_RE.search(normalized):
        return "no-decision"
    english_approval = EN_TESTED_RE.search(normalized) and EN_AGGREGATE_RE.search(normalized) and EN_SUCCESS_RE.search(normalized)
    portuguese_approval = PT_TESTED_RE.search(normalized) and PT_AGGREGATE_RE.search(normalized) and PT_SUCCESS_RE.search(normalized)
    if english_approval or portuguese_approval:
        return "approved"
    return "no-decision"


def classify_preflight(*, automatic_controls_passed: bool, pending_human_gate_count: int) -> dict[str, Any]:
    require("PREFLIGHT_GATE_COUNT_INVALID", isinstance(pending_human_gate_count, int) and pending_human_gate_count >= 0)
    if not automatic_controls_passed:
        return {"status": "blocked-preflight", "writes": 0, "feedback_prompt": True}
    if pending_human_gate_count == 0:
        return {"status": "blocked-preflight", "writes": 0, "feedback_prompt": True}
    return {"status": "ready-for-playtest", "writes": 0, "feedback_prompt": False}


def feedback_prompt(plan_directory: str, summary: str) -> str:
    validate_plan_path(plan_directory)
    require("FEEDBACK_SUMMARY_INVALID", nonempty(summary) and "\n" not in summary and len(summary) <= 240)
    return f"Use loki-feedback for plan {plan_directory}. Problem summary: {summary}. Diagnose and recommend the next authorized workflow; do not transition the plan automatically."


TERMINAL_STATE_KEYS = {"state_schema_version", "result_schema_version", "dashboard_schema_version", "consistency_schema_version", "status", "gate_refs", "gate_digests"}


def validate_terminal_packet(value: Any) -> dict[str, Any]:
    packet = closed("TERMINAL_PACKET_SHAPE_INVALID", value, {"plan_directory", "state_ref", "result_ref", "dashboard_ref", "consistency_ref", "before", "after", "publish_order", "writes"})
    validate_plan_path(packet["plan_directory"])
    before = closed("TERMINAL_BEFORE_SHAPE_INVALID", packet["before"], TERMINAL_STATE_KEYS)
    after = closed("TERMINAL_AFTER_SHAPE_INVALID", packet["after"], TERMINAL_STATE_KEYS)
    require("TERMINAL_SCHEMA_VERSIONS_INVALID", (before["state_schema_version"], before["result_schema_version"], before["dashboard_schema_version"], before["consistency_schema_version"]) == (4, 4, 4, 3) == (after["state_schema_version"], after["result_schema_version"], after["dashboard_schema_version"], after["consistency_schema_version"]))
    require("TERMINAL_BEFORE_STATUS_INVALID", before["status"] == "awaiting-manual-qa")
    require("TERMINAL_AFTER_STATUS_INVALID", after["status"] == "completed")
    require("TERMINAL_GATE_REFS_CHANGED", after["gate_refs"] == before["gate_refs"] and bool(after["gate_refs"]) and len(after["gate_refs"]) == len(set(after["gate_refs"])))
    for ref in after["gate_refs"]:
        validate_locator(ref, packet["plan_directory"], "TERMINAL_GATE_REF_INVALID")
    require("TERMINAL_GATE_DIGESTS_INVALID", isinstance(after["gate_digests"], list) and len(after["gate_digests"]) == len(after["gate_refs"]) and all(DIGEST_RE.fullmatch(item or "") for item in after["gate_digests"]))
    require("TERMINAL_BEFORE_GATE_DIGESTS_INVALID", isinstance(before["gate_digests"], list) and len(before["gate_digests"]) == len(before["gate_refs"]) and all(DIGEST_RE.fullmatch(item or "") for item in before["gate_digests"]))
    require("TERMINAL_GATE_DIGESTS_UNCHANGED", all(left != right for left, right in zip(before["gate_digests"], after["gate_digests"])))
    for key in ("state_ref", "result_ref", "dashboard_ref", "consistency_ref"):
        validate_locator(packet[key], packet["plan_directory"], f"TERMINAL_{key.upper()}_INVALID")
        require(f"TERMINAL_{key.upper()}_FRAGMENT_FORBIDDEN", "#" not in packet[key])
    require("TERMINAL_STATE_REF_INVALID", packet["state_ref"] == f'{packet["plan_directory"]}/tasks.md')
    gate_files = list(dict.fromkeys(ref.partition("#")[0] for ref in after["gate_refs"]))
    expected_order = [*gate_files, packet["state_ref"], packet["result_ref"], packet["dashboard_ref"], packet["consistency_ref"]]
    require("TERMINAL_TARGETS_NOT_DISTINCT", len(expected_order) == len(set(expected_order)))
    require("TERMINAL_PUBLISH_ORDER_INVALID", packet["publish_order"] == expected_order)
    require("TERMINAL_WRITES_INVALID", isinstance(packet["writes"], int) and packet["writes"] == len(packet["publish_order"]))
    return packet


def canonical_terminal_not_required_admission() -> dict[str, Any]:
    plan_directory = "planos/feature-a"
    run_id = "loki-run-v2:" + "a" * 64
    execution_id = "loki-execution-v2:" + "b" * 64
    execution_input_text = '{"schema_version":2}'
    execution_input_digest = "sha256:" + hashlib.sha256(execution_input_text.encode("utf-8")).hexdigest()
    evidence_text = "unit-tests passed\n"
    evidence_digest = "sha256:" + hashlib.sha256(evidence_text.encode("utf-8")).hexdigest()
    automatic_ref = f"{plan_directory}/builds/automatic-unit-tests.json"
    automatic_record = {
        "schema_version": 1,
        "control_id": "unit-tests",
        "status": "passed",
        "evidence_ref": f"{plan_directory}/builds/unit-tests.log",
        "evidence_digest": evidence_digest,
    }
    gate_ref = f"{plan_directory}/task-1.md#gate:unit-tests"
    gate_record = {
        "schema_version": 3,
        "gate_id": "unit-tests",
        "task_ref": f"{plan_directory}/task-1.md",
        "kind": "automatic",
        "instruction": "Run the unit-test suite for the completed implementation.",
        "expected": "The suite exits successfully with no failed test.",
        "status": "passed",
        "evidence_refs": [f"{plan_directory}/builds/unit-tests.log"],
    }
    handoff = {
        "schema_version": 3,
        "status": "manual-qa-not-required",
        "run_id": run_id,
        "execution_id": execution_id,
        "plan_directory": plan_directory,
        "execution_input_ref": f"{plan_directory}/builds/execution-input-v2.json",
        "execution_input_digest": execution_input_digest,
        "automatic_evidence_refs": [automatic_ref],
        "pending_human_gate_refs": [],
        "changed_target_refs": ["src/app.py"],
        "reason": "No human-validation gate applies to this completed execution.",
    }
    audit = {
        "schema_version": 1,
        "frequency": "phase",
        "source": "default",
        "policy_digest": digest({"schema_version": 1, "frequency": "phase", "source": "default"}),
    }
    state = {
        "schema_version": 4,
        "run_id": run_id,
        "execution_id": execution_id,
        "command_identity_digest": "sha256:" + "1" * 64,
        "execution_input_digest": execution_input_digest,
        "audit_configuration": audit,
        "status": "completed",
        "task_refs": [f"{plan_directory}/task-1.md"],
        "gate_refs": [gate_ref],
        "gate_digests": [digest(gate_record)],
        "audit_checkpoint_refs": [f"{plan_directory}/builds/audit.json"],
        "result_ref": f"{plan_directory}/builds/result.json",
        "dashboard_ref": f"{plan_directory}/builds/dashboard.json",
        "consistency_packet_ref": f"{plan_directory}/builds/consistency.json",
        "terminal_evidence_refs": [automatic_ref],
        "manual_qa_handoff": handoff,
        "execution_metrics_ref": f"{plan_directory}/builds/metrics/execution-metrics.json",
        "execution_metrics_digest": "sha256:" + "2" * 64,
        "execution_metrics_status": "complete",
        "execution_metrics_degradation_reason": None,
        "next_action": "none",
        "state_digest": "",
    }
    state["state_digest"] = digest(state, omit="state_digest")
    return {
        "state": state,
        "execution_input_text": execution_input_text,
        "automatic_evidence": [{"ref": automatic_ref, "record": automatic_record, "evidence_text": evidence_text}],
        "gate_records": [{"ref": gate_ref, "record": gate_record}],
    }


def canonical_ready_admission() -> dict[str, Any]:
    packet = canonical_terminal_not_required_admission()
    state = packet["state"]
    handoff = state["manual_qa_handoff"]
    gate_entry = packet["gate_records"][0]
    gate_record = gate_entry["record"]
    state["status"] = "awaiting-manual-qa"
    state["next_action"] = "loki-manual-qa"
    handoff["status"] = "ready-for-manual-qa"
    handoff["pending_human_gate_refs"] = [gate_entry["ref"]]
    handoff["reason"] = None
    gate_record["kind"] = "human-validation"
    gate_record["status"] = "pending"
    gate_record["evidence_refs"] = []
    state["gate_digests"] = [digest(gate_record)]
    state["state_digest"] = digest(state, omit="state_digest")
    return packet


def fixture_payload(case: dict[str, Any]) -> Any:
    if case.get("factory") == "terminal-not-required-admission":
        payload = canonical_terminal_not_required_admission()
    elif case.get("factory") == "terminal-limited-not-required-admission":
        payload = canonical_terminal_not_required_admission()
        payload["state"]["status"] = "completed-with-limitations"
        payload["state"]["state_digest"] = digest(payload["state"], omit="state_digest")
    elif case.get("factory") == "ready-admission":
        payload = canonical_ready_admission()
    else:
        payload = deepcopy(case.get("input"))
    for mutation in case.get("mutations", []):
        cursor = payload
        path = mutation["path"]
        require("FIXTURE_MUTATION_PATH_INVALID", isinstance(path, list) and bool(path))
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = mutation["value"]
    return payload


def load_fixture_file(name: str) -> list[dict[str, Any]]:
    document = json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
    require("FIXTURE_ROOT_INVALID", isinstance(document, dict) and set(document) == {"schema_version", "cases"} and document["schema_version"] == 1)
    require("FIXTURE_CASES_INVALID", isinstance(document["cases"], list) and bool(document["cases"]))
    return document["cases"]


def run_case(case: dict[str, Any]) -> tuple[bool, str | None]:
    kind = case.get("kind")
    try:
        payload = fixture_payload(case)
        if kind == "handoff":
            validate_handoff(payload)
        elif kind == "handoff-input-bytes":
            validate_handoff_input_bytes(payload)
        elif kind == "gate":
            validate_gate(payload)
        elif kind == "automatic-evidence":
            validate_automatic_evidence(payload)
        elif kind == "admission-route":
            result = validate_admission(payload)
            require("ADMISSION_ROUTE_MISMATCH", result == case["expected"])
        elif kind == "checklist":
            result = derive_checklist(case["human_gates"], case["derived_candidates"])
            require("CHECKLIST_EXPECTED_INVALID", result == case["expected"])
        elif kind == "response":
            result = classify_response(case.get("text"), help_id=case.get("help_id"))
            require("RESPONSE_CLASSIFICATION_MISMATCH", result == case["expected"])
            expected_writes = 1 if result == "approved" else 0
            require("ZERO_WRITE_CONTRACT_INVALID", case["writes"] == expected_writes)
        elif kind == "preflight-route":
            result = classify_preflight(automatic_controls_passed=case["automatic_controls_passed"], pending_human_gate_count=case["pending_human_gate_count"])
            require("PREFLIGHT_ROUTE_MISMATCH", result == case["expected"])
        elif kind == "feedback":
            result = feedback_prompt(case["plan_directory"], case["summary"])
            require("FEEDBACK_PROMPT_MISMATCH", result == case["expected"])
            require("FEEDBACK_WRITE_FORBIDDEN", case["writes"] == 0 and case["dispatched"] is False)
        elif kind == "terminal":
            validate_terminal_packet(payload)
        elif kind == "forbidden-form":
            serialized = json.dumps(payload, sort_keys=True)
            require("SUPERSEDED_FORM_ACCEPTED", not any(token in serialized for token in ("manual_qa_result_ref", "manual_qa_attestation_ref", "source_catalog_ref", "transaction_id", "attestation_ref")))
        else:
            raise ContractError("FIXTURE_KIND_INVALID")
        return True, None
    except (ContractError, KeyError, TypeError) as exc:
        return False, str(exc)


def self_test() -> dict[str, Any]:
    cases = [case for name in FIXTURE_FILES for case in load_fixture_file(name)]
    seen: set[str] = set()
    results = []
    required_kinds = {"handoff", "handoff-input-bytes", "gate", "automatic-evidence", "admission-route", "checklist", "response", "preflight-route", "feedback", "terminal", "forbidden-form"}
    for case in cases:
        require("FIXTURE_ID_INVALID", nonempty(case.get("id")) and case["id"] not in seen)
        seen.add(case["id"])
        require("FIXTURE_EXPECTATION_INVALID", case.get("accept") in {True, False})
        accepted, error = run_case(case)
        require(f"FIXTURE_OUTCOME_MISMATCH:{case['id']}:{error}", accepted is case["accept"])
        if not accepted and case.get("error"):
            require(f"FIXTURE_ERROR_MISMATCH:{case['id']}:{case['error']}:{error}", error == case["error"])
        results.append({"id": case["id"], "result": "accepted" if accepted else "expected-rejection", "error": error})
    require("FIXTURE_KIND_COVERAGE_INVALID", {case["kind"] for case in cases} == required_kinds)
    return {"schema_version": 1, "status": "passed", "fixture_files": list(FIXTURE_FILES), "cases_executed": len(results), "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--admission", metavar="PATH")
    parser.add_argument("--handoff", metavar="PATH")
    parser.add_argument("--gate", metavar="PATH")
    parser.add_argument("--terminal-packet", metavar="PATH")
    args = parser.parse_args()
    require("CLI_MODE_INVALID", sum((args.self_test, bool(args.admission), bool(args.handoff), bool(args.gate), bool(args.terminal_packet))) == 1)
    try:
        if args.self_test:
            result = self_test()
        elif args.admission:
            route = validate_admission(json.loads(Path(args.admission).read_text(encoding="utf-8")))
            result = {"schema_version": 1, "status": "passed", "record": "admission", "route": route}
        elif args.handoff:
            validate_handoff(json.loads(Path(args.handoff).read_text(encoding="utf-8"))); result = {"schema_version": 1, "status": "passed", "record": "handoff"}
        elif args.gate:
            validate_gate(json.loads(Path(args.gate).read_text(encoding="utf-8"))); result = {"schema_version": 1, "status": "passed", "record": "gate"}
        else:
            validate_terminal_packet(json.loads(Path(args.terminal_packet).read_text(encoding="utf-8"))); result = {"schema_version": 1, "status": "passed", "record": "terminal-packet"}
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    except (ContractError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
