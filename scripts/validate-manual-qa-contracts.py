#!/usr/bin/env python3
"""Validate current-only state-backed Manual QA and feedback contracts."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "scripts/fixtures/manual-qa"
HELPER_PATH = ROOT / "skills/lf-implement-feature-execution/scripts/loki_execution_state.py"
FIXTURE_FILES = (
    "record-cases.json",
    "transition-cases.json",
    "tree-cases.json",
    "approval-transaction-cases.json",
)
EXPECTED_FIXTURE_IDS = {
    "record-cases.json": frozenset({
        "eligible-state-gate-only",
        "eligible-state-fallback-only",
        "eligible-state-gate-and-fallback",
        "eligible-state-with-no-required-item-rejected",
        "terminal-not-required-is-zero-write",
        "running-state-is-not-eligible",
        "eligible-revision-must-be-positive-integer",
        "eligible-basis-must-be-exact-digest",
    }),
    "transition-cases.json": frozenset({
        "aggregate-approval-english",
        "aggregate-approval-portuguese",
        "problem-is-zero-write",
        "difficulty-is-zero-write",
        "help-id-is-zero-write-difficulty",
        "partial-is-zero-write-no-decision",
        "future-intent-is-zero-write-no-decision",
        "silence-is-zero-write-no-decision",
        "ambiguous-praise-is-zero-write-no-decision",
        "state-bound-problem-payload",
        "state-bound-difficulty-payload",
        "feedback-payload-rejects-stale-revision",
        "terminal-rejects-pending-human-gates",
    }),
    "tree-cases.json": frozenset({
        "state-only-small-feature-tree",
        "state-plus-distinct-immutable-evidence-tree",
        "parallel-mutable-view-rejected",
        "checklist-gate-only",
        "checklist-fallback-only",
        "checklist-required-items-do-not-consume-optional-cap",
        "checklist-ten-exploratory-valid",
        "checklist-eleven-exploratory-rejected",
    }),
    "approval-transaction-cases.json": frozenset({
        "eligibility-accepts-exact-full-gate-set",
        "eligibility-rejects-omitted-gate",
        "eligibility-rejects-extra-gate",
        "eligibility-rejects-empty-gate-set",
        "eligibility-rejects-reordered-gate-set",
        "approve-exact-basis-and-revision",
        "approve-fallback-basis",
        "approval-rejects-omitted-gate",
        "approval-rejects-extra-gate",
        "approval-rejects-empty-gate-set",
        "approval-rejects-reordered-gate-set",
        "reject-stale-eligible-revision",
        "reject-changed-basis-digest",
        "reject-changed-gate-set",
        "reject-unauthorized-actor",
        "reject-unproven-exclusive-owner",
        "exact-approval-replay-is-noop",
        "changed-approval-replay-collides",
    }),
}
ALL_AC_IDS = frozenset(f"AC-{index:03d}" for index in range(1, 40))
MANUAL_QA_COVERED_AC_IDS = frozenset({
    "AC-001", "AC-002", "AC-004", "AC-005", "AC-006", "AC-007",
})
REMOVED_FIXTURE = FIXTURE_ROOT / "checklist-reconciliation-cases.json"
CHECKLIST_ID_RE = re.compile(r"MQ-(?:0[1-9]|[1-9][0-9]+)\Z")
DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
PROBLEM_RE = re.compile(r"\b(?:failed|failure|broken|bug|blocker|blocked|falhou|erro|quebrou|problema|bloqueio)\b")
DIFFICULTY_RE = re.compile(r"\b(?:how|help|cannot|can't|unable|difficult|como|ajuda|nao consigo|não consigo|dificuldade)\b")
NEGATION_RE = re.compile(r"\b(?:not|never|didnt|did not|have not|havent|nao|não|nunca)\b")
FUTURE_RE = re.compile(r"\b(?:will test|going to test|testarei|vou testar|later|depois|ainda vou)\b")
PARTIAL_RE = re.compile(r"\b(?:some|part|partially|only|alguns|algumas|parte|parcialmente|so|só)\b")
UNCERTAIN_RE = re.compile(r"\b(?:maybe|probably|i think|perhaps|talvez|acho|parece)\b")
TESTED_RE = re.compile(r"\b(?:tested|completed|ran|finished|testei|executei|conclui|finalizei)\b")
AGGREGATE_RE = re.compile(r"\b(?:all|everything|entire|whole|full|tudo|todos|todas|completo|completa|aplicavel|aplicável)\b")
SUCCESS_RE = re.compile(r"\b(?:passed|worked|successful|approved|no issues|passou|aprovado|aprovada|funcionou|sucesso|sem problemas)\b")


class ContractError(ValueError):
    pass


def require(code: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise ContractError(code if not detail else f"{code}: {detail}")


def load_state_engine() -> Any:
    require("STATE_HELPER_MISSING", HELPER_PATH.is_file())
    spec = importlib.util.spec_from_file_location("loki_execution_state", HELPER_PATH)
    require("STATE_HELPER_IMPORT_INVALID", spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STATE = load_state_engine()


def helper_call(function: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        return function(*args, **kwargs)
    except STATE.StateContractError as exc:
        raise ContractError(exc.code) from exc


def closed(code: str, value: Any, keys: set[str]) -> dict[str, Any]:
    require(code, isinstance(value, dict) and set(value) == keys)
    return value


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_fixture(name: str) -> dict[str, Any]:
    value = json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
    return closed("FIXTURE_ROOT_INVALID", value, {"schema_version", "cases"})


def validate_fixture_id_catalog(name: str, ids: list[str]) -> None:
    require("FIXTURE_FILE_UNKNOWN", name in EXPECTED_FIXTURE_IDS, name)
    require("FIXTURE_ID_INVALID", all(nonempty(item) for item in ids))
    require("FIXTURE_ID_DUPLICATED", len(ids) == len(set(ids)), name)
    expected = EXPECTED_FIXTURE_IDS[name]
    actual = set(ids)
    unknown = sorted(actual - expected)
    missing = sorted(expected - actual)
    require("FIXTURE_ID_UNKNOWN", not unknown, ",".join(unknown))
    require("FIXTURE_ID_MISSING", not missing, ",".join(missing))


def validate_executed_fixture_ids(executed: set[str]) -> None:
    expected = set().union(*EXPECTED_FIXTURE_IDS.values())
    missing = sorted(expected - executed)
    unknown = sorted(executed - expected)
    require("FIXTURE_ID_UNEXECUTED", not missing, ",".join(missing))
    require("FIXTURE_EXECUTION_UNKNOWN", not unknown, ",".join(unknown))


def fixture_catalog_guard_self_test() -> None:
    name = "record-cases.json"
    valid = sorted(EXPECTED_FIXTURE_IDS[name])
    adversarial = (
        (valid + [valid[0]], "FIXTURE_ID_DUPLICATED"),
        (valid + ["unknown-fixture-id"], "FIXTURE_ID_UNKNOWN"),
        (valid[1:], "FIXTURE_ID_MISSING"),
    )
    for ids, expected_error in adversarial:
        try:
            validate_fixture_id_catalog(name, ids)
        except ContractError as exc:
            require(
                "FIXTURE_GUARD_SELF_TEST_INVALID",
                str(exc).partition(":")[0] == expected_error,
            )
        else:
            raise ContractError("FIXTURE_GUARD_SELF_TEST_MISSED_REJECTION")
    try:
        validate_executed_fixture_ids(
            set().union(*EXPECTED_FIXTURE_IDS.values()) - {valid[0]}
        )
    except ContractError as exc:
        require(
            "FIXTURE_GUARD_SELF_TEST_INVALID",
            str(exc).partition(":")[0] == "FIXTURE_ID_UNEXECUTED",
        )
    else:
        raise ContractError("FIXTURE_GUARD_SELF_TEST_MISSED_UNEXECUTED")


def request(operation: str, transition_id: str, revision: int, occurred_at: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "operation": operation,
        "transition_id": transition_id,
        "expected_revision": revision,
        "occurred_at": occurred_at,
        "payload": payload,
    }


def initial_payload(*, human_gate_count: int) -> dict[str, Any]:
    return {
        "identity": {
            "run_id": "run:manual-qa-test",
            "execution_id": "execution:manual-qa-test",
            "command_identity": {"command": "loki-implement-feature", "adapter": "codex"},
            "demand_ref": "planos/p/demanda.md",
            "demand_digest": "sha256:" + "1" * 64,
            "analysis_ref": "planos/p/analise-tecnica.md",
            "analysis_digest": "sha256:" + "2" * 64,
            "audit_configuration": {
                "frequency": "plan",
                "auditor_source": "agents/auditor.md",
                "policy_ref": "planos/p/plano.md#audit-policy",
            },
        },
        "plan_revision": {
            "plan_revision_ref": "planos/p/plano.md",
            "plan_revision_digest": "sha256:" + "3" * 64,
        },
        "tasks": [{
            "task_ref": "planos/p/task-1.md",
            "phase_ref": "planos/p/fase-1",
            "required": True,
            "validator_ref": "scripts/validate-feature.py",
        }],
        "phases": ["planos/p/fase-1"],
        "gates": [
            {"gate_ref": f"planos/p/task-1.md#human-gate-{index + 1}", "kind": "human-validation"}
            for index in range(human_gate_count)
        ],
        "audit_boundaries": [],
    }


def commit_required_task(path: Path, state: dict[str, Any]) -> dict[str, Any]:
    state, wrote = helper_call(
        STATE.apply_operation,
        path,
        request(
            "start_task_phase",
            "start-task-1",
            state["revision"],
            "2026-08-04T10:01:00+00:00",
            {
                "task_ref": "planos/p/task-1.md",
                "phase_ref": "planos/p/fase-1",
                "dependencies_passed": True,
                "prior_gates_passed": True,
            },
        ),
        actor="orchestrator",
        exclusive_owner=True,
    )
    require("START_TASK_WRITE_INVALID", wrote)
    state, wrote = helper_call(
        STATE.apply_operation,
        path,
        request(
            "commit_task_phase",
            "commit-task-1",
            state["revision"],
            "2026-08-04T10:02:00+00:00",
            {
                "task_ref": "planos/p/task-1.md",
                "task_status": "passed",
                "task_result": {
                    "summary": "Implementation and automatic validation passed.",
                    "responsible": "technical-implementer",
                    "delivery_refs": [],
                },
                "validation": {
                    "status": "passed",
                    "validator_ref": "scripts/validate-feature.py",
                    "evidence_refs": ["planos/p/builds/evidence/task-validator.json"],
                    "limitation": None,
                },
                "target_digests": [],
                "gates": state["gates"],
                "phase": {
                    "phase_ref": "planos/p/fase-1",
                    "status": "passed",
                    "result": {"summary": "Phase passed."},
                    "evidence_refs": [],
                },
                "implemented_outcomes": [{
                    "outcome_ref": "planos/p/task-1.md",
                    "summary": "Feature implemented.",
                    "source_refs": [],
                }],
                "effort_observations": [],
                "material_frictions": [],
                "blockers": {"assessment": "none-confirmed", "reason": None, "items": []},
                "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []},
                "next_steps": [],
                "optional_artifacts": [],
                "desired_targets_verified": True,
            },
        ),
        actor="state-writer",
        exclusive_owner=True,
    )
    require("COMMIT_TASK_WRITE_INVALID", wrote)
    return state


def build_state(path: Path, factory: str) -> dict[str, Any]:
    if factory in {"eligible-fallback-only", "eligible-neither", "terminal-not-required", "running"}:
        human_gate_count = 0
    elif factory in {"pre-eligibility-two-gates", "eligible-two-gates", "pre-terminal-pending-gates"}:
        human_gate_count = 2
    else:
        human_gate_count = 1
    state, wrote = helper_call(
        STATE.apply_operation,
        path,
        request("initialize", "initialize-run", 0, "2026-08-04T10:00:00+00:00", initial_payload(human_gate_count=human_gate_count)),
        actor="orchestrator",
        exclusive_owner=True,
    )
    require("INITIALIZE_WRITE_INVALID", wrote)
    if factory == "running":
        return state
    state = commit_required_task(path, state)
    if factory in {"pre-eligibility-two-gates", "pre-terminal-pending-gates"}:
        return state
    if factory == "terminal-not-required":
        state, wrote = helper_call(
            STATE.apply_operation,
            path,
            request(
                "publish_terminal",
                "publish-terminal",
                state["revision"],
                "2026-08-04T10:03:00+00:00",
                {
                    "status": "completed",
                    "terminal_reason": {"status": "observed", "summary": "No human QA is applicable.", "reason": None},
                    "implemented_outcomes": [],
                    "blockers": {"assessment": "none-confirmed", "reason": None, "items": []},
                    "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []},
                    "next_steps": [],
                    "terminal_truth_passed": True,
                },
            ),
            actor="orchestrator",
            exclusive_owner=True,
        )
        require("TERMINAL_WRITE_INVALID", wrote)
        return state

    gate_refs = [row["gate_ref"] for row in state["gates"]]
    limitation_refs = (
        ["planos/p/builds/evidence/manual-fallback.json"]
        if factory in {"eligible-fallback-only", "eligible-both", "eligible-with-limitation"}
        else []
    )
    if factory == "eligible-neither":
        gate_refs = []
        limitation_refs = []
    basis = STATE.bytes_digest(STATE.canonical_bytes({
        "run_id": state["identity"]["run_id"],
        "execution_id": state["identity"]["execution_id"],
        "plan_revision_digest": state["plan_revision"]["plan_revision_digest"],
        "tasks": [(row["task_ref"], row["status"], row["validation"]["status"]) for row in state["tasks"]],
        "gates": [(row["gate_ref"], row["status"]) for row in state["gates"]],
        "limitation_refs": limitation_refs,
    }))
    state, wrote = helper_call(
        STATE.apply_operation,
        path,
        request(
            "publish_manual_qa_eligibility",
            "publish-manual-qa-eligibility",
            state["revision"],
            "2026-08-04T10:03:00+00:00",
            {
                "basis_digest": basis,
                "applicable_gate_refs": gate_refs,
                "limitation_refs": limitation_refs,
            },
        ),
        actor="orchestrator",
        exclusive_owner=True,
    )
    require("ELIGIBILITY_WRITE_INVALID", wrote)
    return state


def validate_manual_qa_state(value: Any) -> str:
    require("MANUAL_QA_STATE_SHAPE_INVALID", isinstance(value, dict))
    qa = value.get("manual_qa")
    require("MANUAL_QA_STATE_SHAPE_INVALID", isinstance(qa, dict))
    if qa.get("eligibility_status") == "eligible":
        revision = qa.get("eligible_revision")
        require("MANUAL_QA_ELIGIBLE_REVISION_INVALID", isinstance(revision, int) and not isinstance(revision, bool) and revision >= 1)
        require("MANUAL_QA_ELIGIBILITY_BASIS_INVALID", isinstance(qa.get("eligibility_basis_digest"), str) and DIGEST_RE.fullmatch(qa["eligibility_basis_digest"]) is not None)
    state = helper_call(STATE.validate_state, value)
    qa = state["manual_qa"]
    if qa["eligibility_status"] == "eligible":
        require("MANUAL_QA_STATE_NOT_ELIGIBLE", state["status"] == "awaiting-manual-qa" and qa["eligible_revision"] == state["revision"])
        require("MANUAL_QA_REQUIRED_ITEMS_EMPTY", bool(qa["applicable_gate_refs"] or qa["limitation_refs"]))
        pending_human_gate_refs = [
            row["gate_ref"]
            for row in state["gates"]
            if row["kind"] == "human-validation" and row["status"] == "pending"
        ]
        require(
            "MANUAL_QA_GATE_SET_INVALID",
            qa["applicable_gate_refs"] == pending_human_gate_refs,
        )
        gates = {row["gate_ref"]: row for row in state["gates"]}
        require(
            "MANUAL_QA_GATE_SET_INVALID",
            all(
                ref in gates
                and gates[ref]["kind"] == "human-validation"
                and gates[ref]["status"] == "pending"
                for ref in qa["applicable_gate_refs"]
            ),
        )
        return "eligible"
    if qa["eligibility_status"] == "not-applicable":
        require("MANUAL_QA_STATE_NOT_ELIGIBLE", state["status"] in {"completed", "completed-with-limitations"})
        return "not-applicable"
    raise ContractError("MANUAL_QA_STATE_NOT_ELIGIBLE")


def classify_human_response(text: Any, *, help_id: str | None = None) -> str:
    if help_id is not None:
        require("HELP_ID_INVALID", CHECKLIST_ID_RE.fullmatch(help_id) is not None)
        return "difficulty"
    if not nonempty(text):
        return "no-decision"
    normalized = " ".join(text.strip().casefold().split())
    folded = unicodedata.normalize("NFKD", normalized).encode("ascii", "ignore").decode("ascii")
    if PROBLEM_RE.search(folded):
        return "problem"
    if DIFFICULTY_RE.search(folded):
        return "difficulty"
    if any(pattern.search(folded) for pattern in (NEGATION_RE, FUTURE_RE, PARTIAL_RE, UNCERTAIN_RE)):
        return "no-decision"
    if TESTED_RE.search(folded) and AGGREGATE_RE.search(folded) and SUCCESS_RE.search(folded):
        return "approved"
    return "no-decision"


def derive_checklist(human_gate_count: int, limitation_count: int, exploratory_count: int) -> list[dict[str, str]]:
    require("CHECKLIST_COUNTS_INVALID", all(isinstance(item, int) and not isinstance(item, bool) and item >= 0 for item in (human_gate_count, limitation_count, exploratory_count)))
    require("CHECKLIST_REQUIRED_ITEMS_EMPTY", human_gate_count + limitation_count > 0)
    require("CHECKLIST_EXPLORATORY_LIMIT_EXCEEDED", exploratory_count <= 10)
    kinds = ["human-gate"] * human_gate_count + ["required-fallback"] * limitation_count + ["optional-exploratory"] * exploratory_count
    return [
        {
            "id": f"MQ-{index:02d}",
            "kind": kind,
            "instruction": f"Execute {kind} {index}.",
            "expected": f"{kind} {index} succeeds.",
        }
        for index, kind in enumerate(kinds, start=1)
    ]


def render_checklist(items: list[dict[str, str]]) -> str:
    require("CHECKLIST_ID_INVALID", all(CHECKLIST_ID_RE.fullmatch(item["id"]) is not None for item in items))
    lines = ["## Playtest Checklist", ""]
    for item in items:
        marker = "optional exploratory" if item["kind"] == "optional-exploratory" else "required"
        lines.append(f"- {item['id']} ({marker}): {item['instruction']} Expected: {item['expected']}")
    return "\n".join(lines) + "\n"


FEEDBACK_KEYS = {
    "schema_version", "issue_kind", "plan_root", "run_id", "execution_id",
    "eligibility_basis_digest", "eligible_revision", "checklist_item_id",
    "instruction", "expected", "sanitized_description",
}


def validate_feedback_payload(value: Any, state: dict[str, Any], raw_feedback: str) -> dict[str, Any]:
    payload = closed("FEEDBACK_PAYLOAD_SHAPE_INVALID", value, FEEDBACK_KEYS)
    require("FEEDBACK_SCHEMA_INVALID", payload["schema_version"] == 1)
    require("FEEDBACK_ISSUE_KIND_INVALID", payload["issue_kind"] in {"problem", "difficulty"})
    require("FEEDBACK_PLAN_ROOT_INVALID", payload["plan_root"] == "planos/p")
    require("FEEDBACK_RUN_ID_MISMATCH", payload["run_id"] == state["identity"]["run_id"])
    require("FEEDBACK_EXECUTION_ID_MISMATCH", payload["execution_id"] == state["identity"]["execution_id"])
    require("FEEDBACK_BASIS_MISMATCH", payload["eligibility_basis_digest"] == state["manual_qa"]["eligibility_basis_digest"])
    require(
        "FEEDBACK_ELIGIBLE_REVISION_MISMATCH",
        isinstance(payload["eligible_revision"], int)
        and not isinstance(payload["eligible_revision"], bool)
        and payload["eligible_revision"] == state["manual_qa"]["eligible_revision"],
    )
    require("FEEDBACK_ITEM_ID_INVALID", CHECKLIST_ID_RE.fullmatch(payload["checklist_item_id"]) is not None)
    for key, maximum in (("instruction", 1000), ("expected", 1000), ("sanitized_description", 240)):
        require(f"FEEDBACK_{key.upper()}_INVALID", nonempty(payload[key]) and "\n" not in payload[key] and len(payload[key]) <= maximum and CONTROL_RE.search(payload[key]) is None)
    require("FEEDBACK_RAW_TEXT_MISMATCH", " ".join(raw_feedback.split()) == " ".join(payload["sanitized_description"].split()))
    require("FEEDBACK_STATE_NOT_ELIGIBLE", validate_manual_qa_state(state) == "eligible")
    return payload


def eligibility_request(state: dict[str, Any]) -> dict[str, Any]:
    gate_refs = [
        row["gate_ref"]
        for row in state["gates"]
        if row["kind"] == "human-validation" and row["status"] == "pending"
    ]
    basis = STATE.bytes_digest(STATE.canonical_bytes({
        "run_id": state["identity"]["run_id"],
        "execution_id": state["identity"]["execution_id"],
        "plan_revision_digest": state["plan_revision"]["plan_revision_digest"],
        "tasks": [
            (row["task_ref"], row["status"], row["validation"]["status"])
            for row in state["tasks"]
        ],
        "gates": [(row["gate_ref"], row["status"]) for row in state["gates"]],
        "limitation_refs": [],
    }))
    return request(
        "publish_manual_qa_eligibility",
        "publish-manual-qa-eligibility-adversarial",
        state["revision"],
        "2026-08-04T10:03:30+00:00",
        {
            "basis_digest": basis,
            "applicable_gate_refs": gate_refs,
            "limitation_refs": [],
        },
    )


def mutate_gate_refs(operation: dict[str, Any], mutation: str) -> None:
    refs = operation["payload"]["applicable_gate_refs"]
    if mutation == "omitted-gate":
        refs.pop()
    elif mutation == "extra-gate":
        refs.append("planos/p/task-1.md#human-gate-extra")
    elif mutation == "empty-gate-set":
        operation["payload"]["applicable_gate_refs"] = []
    elif mutation == "reordered-gate-set":
        operation["payload"]["applicable_gate_refs"] = list(reversed(refs))


def apply_eligibility_case(case: dict[str, Any], path: Path) -> tuple[str, int]:
    state = build_state(path, "pre-eligibility-two-gates")
    operation = eligibility_request(state)
    mutation = case.get("mutation", "none")
    mutate_gate_refs(operation, mutation)
    before = path.read_bytes()
    try:
        snapshot, wrote = helper_call(
            STATE.apply_operation,
            path,
            operation,
            actor="orchestrator",
            exclusive_owner=True,
        )
    except ContractError:
        require("ELIGIBILITY_REJECTION_EXPECTATION_INVALID", case["expected_writes"] == 0)
        require("ELIGIBILITY_REJECTION_WROTE_BYTES", path.read_bytes() == before)
        raise
    require("ELIGIBILITY_WRITE_COUNT_INVALID", int(wrote) == case["expected_writes"])
    require("ELIGIBILITY_STATUS_INVALID", snapshot["status"] == case["expected_status"])
    expected_refs = [row["gate_ref"] for row in state["gates"]]
    require(
        "ELIGIBILITY_FULL_GATE_SET_NOT_PERSISTED",
        snapshot["manual_qa"]["applicable_gate_refs"] == expected_refs,
    )
    return snapshot["status"], int(wrote)


def approval_request(state: dict[str, Any]) -> dict[str, Any]:
    qa = state["manual_qa"]
    return request(
        "approve_manual_qa",
        "approve-manual-qa",
        qa["eligible_revision"],
        "2026-08-04T10:04:00+00:00",
        {
            "decision_id": "decision-manual-qa",
            "basis_digest": qa["eligibility_basis_digest"],
            "applicable_gate_refs": copy.deepcopy(qa["applicable_gate_refs"]),
            "limitation_refs": copy.deepcopy(qa["limitation_refs"]),
            "terminal_summary": "The complete applicable Manual QA checklist passed.",
        },
    )


def apply_approval_case(case: dict[str, Any], path: Path, state: dict[str, Any]) -> tuple[str, int]:
    operation = approval_request(state)
    mutation = case.get("mutation", "none")
    actor = "human-authority"
    owner = True
    if mutation == "stale-revision":
        operation["expected_revision"] -= 1
    elif mutation == "changed-basis":
        operation["payload"]["basis_digest"] = "sha256:" + "f" * 64
    elif mutation == "changed-gates":
        operation["payload"]["applicable_gate_refs"].append("planos/p/task-1.md#human-gate-extra")
    elif mutation in {"omitted-gate", "extra-gate", "empty-gate-set", "reordered-gate-set"}:
        mutate_gate_refs(operation, mutation)
    elif mutation == "unauthorized-actor":
        actor = "orchestrator"
    elif mutation == "owner-unproven":
        owner = False
    before = path.read_bytes()
    try:
        snapshot, wrote = helper_call(
            STATE.apply_operation,
            path,
            operation,
            actor=actor,
            exclusive_owner=owner,
        )
    except ContractError:
        require("APPROVAL_REJECTION_EXPECTATION_INVALID", case["expected_writes"] == 0)
        require("APPROVAL_REJECTION_WROTE_BYTES", path.read_bytes() == before)
        raise
    require("APPROVAL_WRITE_COUNT_INVALID", int(wrote) == case["expected_writes"])
    require("APPROVAL_STATUS_INVALID", snapshot["status"] == case["expected_status"])
    decision = snapshot["human_decisions"][-1]
    require("APPROVAL_BASIS_NOT_BOUND", decision["basis_digest"] == state["manual_qa"]["eligibility_basis_digest"])
    require(
        "APPROVAL_GATE_SET_NOT_BOUND",
        decision["applicable_gate_refs"]
        == state["manual_qa"]["applicable_gate_refs"],
    )
    applicable_refs = set(state["manual_qa"]["applicable_gate_refs"])
    require(
        "APPROVAL_GATES_NOT_TERMINAL",
        all(
            row["status"] == "passed"
            for row in snapshot["gates"]
            if row["gate_ref"] in applicable_refs
        )
        and not any(
            row["kind"] == "human-validation" and row["status"] == "pending"
            for row in snapshot["gates"]
        ),
    )
    require("APPROVAL_DECISION_INVALID", decision["decision"] == "approved")
    require("APPROVAL_BYTES_UNCHANGED", wrote or path.read_bytes() == before)
    return snapshot["status"], int(wrote)


def apply_terminal_pending_gate_case(case: dict[str, Any], path: Path) -> None:
    require("TERMINAL_REJECTION_EXPECTATION_INVALID", case["expected_writes"] == 0)
    state = build_state(path, "pre-terminal-pending-gates")
    operation = request(
        "publish_terminal",
        "publish-terminal-with-pending-human-gates",
        state["revision"],
        "2026-08-04T10:03:30+00:00",
        {
            "status": "completed",
            "terminal_reason": {
                "status": "observed",
                "summary": "Implementation passed.",
                "reason": None,
            },
            "implemented_outcomes": copy.deepcopy(
                state["execution_summary"]["implemented_outcomes"]
            ),
            "blockers": {"assessment": "none-confirmed", "reason": None, "items": []},
            "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []},
            "next_steps": [],
            "terminal_truth_passed": True,
        },
    )
    before = path.read_bytes()
    try:
        helper_call(
            STATE.apply_operation,
            path,
            operation,
            actor="orchestrator",
            exclusive_owner=True,
        )
    except ContractError:
        require("TERMINAL_REJECTION_WROTE_BYTES", path.read_bytes() == before)
        raise
    raise ContractError("TERMINAL_PENDING_GATE_ACCEPTED")


def validate_tree(case: dict[str, Any]) -> None:
    paths = case["paths"]
    require("TREE_PATHS_INVALID", isinstance(paths, list) and paths and len(paths) == len(set(paths)))
    mutable = case.get("mutable_administrative_paths", ["planos/p/builds/execution-state.json"])
    require("MULTIPLE_MUTABLE_ADMINISTRATIVE_FILES", len(mutable) == 1)
    require("STATE_FILE_MISSING", mutable[0] == "planos/p/builds/execution-state.json")
    require("TREE_MUTABLE_COUNT_INVALID", case["expected_mutable_administrative_files"] == 1)


def run_case(case: dict[str, Any]) -> None:
    accept = case["accept"]
    expected_error = case.get("error")
    with tempfile.TemporaryDirectory(prefix="manual-qa-state-") as temporary:
        path = Path(temporary) / "execution-state.json"
        factory = case.get("factory", "eligible-gate-only")
        try:
            kind = case["kind"]
            if kind in {"state-route", "state-validation"}:
                state = build_state(path, factory)
                if case.get("mutation") == "boolean-eligible-revision":
                    state["manual_qa"]["eligible_revision"] = True
                    state["state_digest"] = STATE.state_digest(state)
                elif case.get("mutation") == "invalid-basis-digest":
                    state["manual_qa"]["eligibility_basis_digest"] = "invalid"
                    state["state_digest"] = STATE.state_digest(state)
                result = validate_manual_qa_state(state)
                require("STATE_ROUTE_RESULT_INVALID", result == case.get("expected", result))
            elif kind == "human-response":
                result = classify_human_response(case.get("text"), help_id=case.get("help_id"))
                require("HUMAN_RESPONSE_RESULT_INVALID", result == case["expected"])
                require("HUMAN_RESPONSE_WRITE_COUNT_INVALID", case["expected_writes"] == (1 if result == "approved" else 0))
            elif kind == "feedback-payload":
                state = build_state(path, "eligible-gate-only")
                payload = {
                    "schema_version": 1,
                    "issue_kind": case["issue_kind"],
                    "plan_root": "planos/p",
                    "run_id": state["identity"]["run_id"],
                    "execution_id": state["identity"]["execution_id"],
                    "eligibility_basis_digest": state["manual_qa"]["eligibility_basis_digest"],
                    "eligible_revision": state["manual_qa"]["eligible_revision"],
                    "checklist_item_id": "MQ-01",
                    "instruction": "Execute the primary flow.",
                    "expected": "The primary flow succeeds.",
                    "sanitized_description": case["description"],
                }
                if case.get("mutation") == "stale-revision":
                    payload["eligible_revision"] -= 1
                validate_feedback_payload(payload, state, case["description"])
                require("FEEDBACK_EFFECT_INVALID", case["expected_writes"] == 0 and case["expected_dispatches"] == 0)
            elif kind == "checklist-render":
                items = derive_checklist(case["human_gate_count"], case["limitation_count"], case["exploratory_count"])
                rendered = render_checklist(items)
                require("CHECKLIST_COUNT_INVALID", len(items) == case["expected_count"])
                require("CHECKLIST_HEADING_MISSING", rendered.startswith("## Playtest Checklist\n"))
            elif kind == "artifact-tree":
                validate_tree(case)
            elif kind == "eligibility-operation":
                apply_eligibility_case(case, path)
            elif kind == "approval-operation":
                state = build_state(path, factory)
                apply_approval_case(case, path, state)
            elif kind == "approval-replay":
                state = build_state(path, "eligible-gate-only")
                operation = approval_request(state)
                first, first_write = helper_call(STATE.apply_operation, path, operation, actor="human-authority", exclusive_owner=True)
                replay, replay_write = helper_call(STATE.apply_operation, path, operation, actor="human-authority", exclusive_owner=True)
                require("APPROVAL_REPLAY_INVALID", first["status"] == case["expected_status"] == replay["status"])
                require("APPROVAL_REPLAY_WRITE_INVALID", first_write is case["expected_first_write"] and replay_write is case["expected_replay_write"])
                require("APPROVAL_REPLAY_BYTES_INVALID", first == replay)
            elif kind == "approval-replay-changed-payload":
                require("APPROVAL_COLLISION_EXPECTATION_INVALID", case["expected_writes"] == 0)
                state = build_state(path, "eligible-two-gates")
                operation = approval_request(state)
                first, first_write = helper_call(
                    STATE.apply_operation,
                    path,
                    operation,
                    actor="human-authority",
                    exclusive_owner=True,
                )
                require("APPROVAL_REPLAY_FIRST_WRITE_INVALID", first_write is True)
                changed = copy.deepcopy(operation)
                changed["payload"]["terminal_summary"] = "Changed replay meaning."
                before = path.read_bytes()
                try:
                    helper_call(
                        STATE.apply_operation,
                        path,
                        changed,
                        actor="human-authority",
                        exclusive_owner=True,
                    )
                except ContractError:
                    require("APPROVAL_COLLISION_WROTE_BYTES", path.read_bytes() == before)
                    raise
                raise ContractError("APPROVAL_COLLISION_ACCEPTED")
            elif kind == "terminal-operation":
                apply_terminal_pending_gate_case(case, path)
            else:
                raise ContractError("FIXTURE_KIND_UNKNOWN")
        except (ContractError, STATE.StateContractError) as exc:
            code = exc.code if isinstance(exc, STATE.StateContractError) else str(exc).partition(":")[0]
            if accept:
                raise
            require("EXPECTED_ERROR_MISMATCH", code == expected_error, f"expected={expected_error} actual={code}")
        else:
            require("EXPECTED_REJECTION_MISSING", accept)


def validate_bundle_text() -> None:
    paths = [
        ROOT / "skills/loki-manual-qa/SKILL.md",
        ROOT / "skills/loki-manual-qa/references/execution.md",
        ROOT / "skills/loki-manual-qa/references/response.md",
        ROOT / "skills/loki-manual-qa/assets/response-template.md",
        ROOT / "skills/loki-feedback/SKILL.md",
        ROOT / "skills/loki-feedback/references/execution.md",
        ROOT / "skills/loki-feedback/references/response.md",
        ROOT / "skills/loki-feedback/references/diagnostic-output-and-forward-test.md",
        ROOT / "skills/loki-feedback/assets/response-template.md",
    ]
    texts = {path: path.read_text(encoding="utf-8") for path in paths}
    manual = "\n".join(text for path, text in texts.items() if "loki-manual-qa" in path.as_posix())
    feedback = "\n".join(text for path, text in texts.items() if "loki-feedback" in path.as_posix())
    for token in (
        "approve_manual_qa",
        "eligibility_basis_digest",
        "eligible_revision",
        "## Playtest Checklist",
        "python3 scripts/validate-manual-qa-contracts.py --self-test",
    ):
        require("MANUAL_QA_CONTRACT_TOKEN_MISSING", token in manual, token)
    for token in (
        "manual-qa-checklist-feedback",
        "eligibility_basis_digest",
        "eligible_revision",
        "framework-artifact-quality-auditor",
        "orchestrator",
        "runtime_effect",
    ):
        require("FEEDBACK_CONTRACT_TOKEN_MISSING", token in feedback, token)
    require("REMOVED_FIXTURE_STILL_PRESENT", not REMOVED_FIXTURE.exists())
    require("STATE_HELPER_API_MISSING", all(hasattr(STATE, name) for name in ("validate_state", "validate_request", "apply_operation")))
    require("MANUAL_QA_TEMPLATE_LINK_MISSING", "[assets/response-template.md](assets/response-template.md)" in texts[ROOT / "skills/loki-manual-qa/SKILL.md"])
    require("FEEDBACK_TEMPLATE_LINK_MISSING", "[assets/response-template.md](assets/response-template.md)" in texts[ROOT / "skills/loki-feedback/SKILL.md"])


def self_test() -> dict[str, Any]:
    validate_bundle_text()
    fixture_catalog_guard_self_test()
    seen: set[str] = set()
    executed: set[str] = set()
    ac: set[str] = set()
    count = 0
    for name in FIXTURE_FILES:
        fixture = load_fixture(name)
        require("FIXTURE_SCHEMA_INVALID", fixture["schema_version"] == 1)
        require("FIXTURE_CASES_INVALID", isinstance(fixture["cases"], list) and fixture["cases"])
        validate_fixture_id_catalog(
            name,
            [case.get("id") for case in fixture["cases"] if isinstance(case, dict)],
        )
        for case in fixture["cases"]:
            require("FIXTURE_CASE_INVALID", isinstance(case, dict) and nonempty(case.get("id")) and isinstance(case.get("accept"), bool))
            require("FIXTURE_ID_DUPLICATED", case["id"] not in seen)
            seen.add(case["id"])
            require("FIXTURE_AC_INVALID", isinstance(case.get("ac"), list) and case["ac"])
            require(
                "FIXTURE_AC_UNKNOWN",
                all(isinstance(item, str) and item in ALL_AC_IDS for item in case["ac"]),
                case["id"],
            )
            require(
                "FIXTURE_AC_OVERCLAIMED",
                set(case["ac"]) <= MANUAL_QA_COVERED_AC_IDS,
                case["id"],
            )
            ac.update(case["ac"])
            run_case(case)
            executed.add(case["id"])
            count += 1
    validate_executed_fixture_ids(executed)
    require("AC_COVERAGE_INCOMPLETE", ac == MANUAL_QA_COVERED_AC_IDS)
    return {
        "self_test": "passed",
        "contract": "manual-qa-state-only-v1",
        "state_helper": str(HELPER_PATH.relative_to(ROOT)),
        "fixtures": list(FIXTURE_FILES),
        "cases": count,
        "acceptance_criteria": sorted(ac),
        "acceptance_criteria_not_claimed": sorted(ALL_AC_IDS - ac),
        "acceptance_criteria_universe": sorted(ALL_AC_IDS),
        "fixture_guard_checks": ["duplicate", "missing", "unexecuted", "unknown"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", required=True)
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
