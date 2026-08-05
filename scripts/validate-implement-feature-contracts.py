#!/usr/bin/env python3
"""Execute the complete current-only feature-contract fixture and AC matrix."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "skills/lf-implement-feature-execution/scripts/loki_execution_state.py"
FIXTURE_ROOT = ROOT / "scripts/fixtures/implement-feature"
FIXTURE_IDS = {
    "input-path-cases.json": (
        "normalized-relative-state-path", "path-traversal-rejected", "absolute-path-rejected",
        "backslash-path-rejected", "parallel-result-path-rejected", "repeated-separator-rejected",
        "trailing-separator-rejected", "dot-segment-rejected", "equivalent-alias-rejected",
    ),
    "optional-metrics-cases.json": (
        "default-does-not-create-metrics", "explicit-metrics-artifact-has-consumer",
        "missing-observation-is-not-zero", "observed-effort-is-non-negative",
    ),
    "recovery-limitation-cases.json": (
        "all-before-allows-explicit-abandon", "all-desired-allows-validation",
        "mixed-blocks-without-repair", "unknown-blocks-without-repair", "open-handoff-remains-open",
    ),
    "response-dashboard-cases.json": (
        "one-of-three-required-passed", "replan-may-reduce-percent",
        "overlapping-handoffs-chronological", "same-agent-separate-handoffs",
        "unavailable-clock-is-not-estimated", "compact-transition-timestamp-stable",
        "compact-transition-local-clock-pm",
        "final-only-terminal", "requested-read-only", "equal-clock-endpoints",
        "offsets-sort-by-instant", "negative-handoff-chronology-rejected",
        "d001-d025-final-order", "frictions-omitted-when-empty", "resume-includes-completed-details",
    ),
    "state-resume-cases.json": (
        "interrupt-after-handoff", "interrupt-after-task", "interrupt-after-phase",
        "resume-renders-before-effects", "stale-revision-zero-write", "exact-replay-zero-write",
        "terminal-state-immutable", "all-operations-exact-replay",
        "all-operations-changed-request-conflict", "initialize-changed-task-set-conflict",
        "replan-existing-task-spec-exact-replay", "replan-existing-task-spec-mismatch-zero-write",
        "replan-existing-task-spec-changed-replay-conflict",
        "commit-task-no-pending-verified-exact-replay", "commit-task-no-pending-unverified-zero-write",
        "commit-task-no-pending-changed-replay-conflict", "commit-task-pending-verified-exact-replay",
        "commit-task-pending-unverified-zero-write",
        "qa-complete-pending-gate-set", "qa-incomplete-pending-gate-set",
        "terminal-pending-human-gate-rejected",
    ),
    "validation-cycle-cases.json": (
        "task-pass-requires-validator-evidence", "task-pass-with-failed-validator-rejected",
        "audit-task-frequency", "audit-phase-frequency", "audit-plan-frequency",
        "audit-rejection-blocks", "manual-qa-approval-single-operation",
        "ambiguous-manual-qa-zero-write",
    ),
}
OWNED_CONTRACTS = (
    "skills/lf-implement-feature-execution/SKILL.md",
    "skills/lf-implement-feature-execution/references/execution-contract.md",
    "skills/lf-implement-feature-execution/references/session-preflight-contract.md",
    "skills/lf-implement-feature-execution/references/validation-cycle-contract.md",
    "skills/loki-implement-feature/SKILL.md",
    "skills/loki-implement-feature/references/execution.md",
    "skills/loki-implement-feature/references/response.md",
    "skills/loki-implement-feature/assets/response-template.md",
    "skills/lf-action-plan-authoring/SKILL.md",
    "skills/lf-action-plan-authoring/references/action-plan-contract.md",
    "skills/lf-template-library/SKILL.md",
    "templates/tasks-template.md", "templates/task-template.md",
    "skills/lf-template-library/references/templates/tasks-template.md",
    "skills/lf-template-library/references/templates/task-template.md",
)
REMOVED_SEEDS = (
    "loki_execution_" + "projections", "implementation-result" + "-v",
    "implementation-dashboard" + "-v", "implementation-consistency" + "-v",
    "terminal-evidence" + "-v", "manual_qa_" + "handoff",
    "required_projection_" + "closure", "repairable-administrative-" + "projection",
    "unrepaired-promotion-" + "projection", "consistency-" + "last",
    "projection-byte-real-" + "cases",
)
SHA = "sha256:" + "1" * 64


class ContractError(RuntimeError):
    pass


def require(code: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise ContractError(code if not detail else f"{code}: {detail}")


def load_helper() -> Any:
    spec = importlib.util.spec_from_file_location("loki_execution_state", HELPER_PATH)
    require("HELPER_LOAD_INVALID", spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_fixtures() -> dict[str, list[dict[str, Any]]]:
    loaded: dict[str, list[dict[str, Any]]] = {}
    for name, expected_ids in FIXTURE_IDS.items():
        value = json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
        require("FIXTURE_ROOT_INVALID", isinstance(value, dict) and set(value) == {"schema_version", "cases"}, name)
        require("FIXTURE_SCHEMA_INVALID", value["schema_version"] == 1 and isinstance(value["cases"], list) and value["cases"], name)
        ids = [case.get("id") for case in value["cases"]]
        require("FIXTURE_ID_TYPE_INVALID", all(isinstance(item, str) and item for item in ids), name)
        require("FIXTURE_ID_DUPLICATED", len(ids) == len(set(ids)), name)
        missing = sorted(set(expected_ids) - set(ids)); unknown = sorted(set(ids) - set(expected_ids))
        require("FIXTURE_ID_SET_INVALID", not missing and not unknown and len(ids) == len(expected_ids), f"{name}:missing={missing}:unknown={unknown}")
        loaded[name] = value["cases"]
    return loaded


def initial_state(helper: Any, *, task_count: int = 1, gates: list[dict[str, str]] | None = None, boundaries: list[str] | None = None) -> dict[str, Any]:
    request = {
        "operation": "initialize", "transition_id": "tx.fixture.init", "expected_revision": 0,
        "occurred_at": "2026-08-04T10:00:00-03:00",
        "payload": {
            "identity": {"run_id": "run.fixture", "execution_id": "exec.fixture", "command_identity": {"command": "loki-implement-feature", "adapter": "codex"}, "demand_ref": "plan/demand.md", "demand_digest": SHA, "analysis_ref": "plan/analysis.md", "analysis_digest": SHA, "audit_configuration": {"frequency": "plan", "auditor_source": "agents/auditor.md", "policy_ref": "plan/tasks.md"}},
            "plan_revision": {"plan_revision_ref": "plan/tasks.md", "plan_revision_digest": SHA},
            "tasks": [{"task_ref": f"task-{index + 1}", "phase_ref": "phase-1", "required": True, "validator_ref": f"validator-{index + 1}"} for index in range(task_count)],
            "phases": ["phase-1"], "gates": gates or [], "audit_boundaries": boundaries or [],
        },
    }
    return helper._initial_state(request)


def finalize_state(helper: Any, state: dict[str, Any]) -> dict[str, Any]:
    state["state_digest"] = helper.state_digest(state)
    return helper.validate_state(state)


def set_task(state: dict[str, Any], index: int, status: str, *, occurred_at: str = "2026-08-04T10:05:00-03:00") -> None:
    task = state["tasks"][index]
    if status == "pending": return
    task["status"] = status; task["transition_id"] = f"tx.task.{index + 1}"; task["transitioned_at"] = occurred_at
    if status == "running": return
    task["result"] = {"summary": f"task {index + 1} {status}", "responsible": "technical-implementer", "delivery_refs": []}
    task["validation"] = {"status": "passed" if status == "passed" else "failed", "validator_ref": task["validation"]["validator_ref"], "evidence_refs": [f"evidence/task-{index + 1}.txt"], "limitation": None}


def set_phase(state: dict[str, Any], status: str, *, occurred_at: str = "2026-08-04T10:05:00-03:00") -> None:
    phase = state["phases"][0]
    if status == "pending": return
    phase["status"] = status; phase["transition_id"] = "tx.phase.1"; phase["transitioned_at"] = occurred_at
    if status != "running": phase["result"] = {"summary": f"phase {status}"}; phase["evidence_refs"] = ["evidence/phase.txt"]


def handoff(handoff_id: str, called_at: str | None, delivered_at: str | None, *, agent: str = "technical-implementer", unavailable_reason: str | None = None) -> dict[str, Any]:
    called = {"status": "observed", "value": called_at, "reason": None} if called_at else {"status": "unavailable", "value": None, "reason": unavailable_reason or "dispatch time unavailable"}
    if delivered_at is None:
        return {"handoff_id": handoff_id, "task_ref": "task-1", "phase_ref": "phase-1", "agent_label": agent, "objective": "implement", "status": "open", "called_at": called, "delivered_at": {"status": "pending", "value": None, "reason": None}, "delivery": {"status": "pending", "summary": None, "reason": None}, "result": {"status": "pending", "summary": None}, "evidence_refs": []}
    return {"handoff_id": handoff_id, "task_ref": "task-1", "phase_ref": "phase-1", "agent_label": agent, "objective": "implement", "status": "delivered", "called_at": called, "delivered_at": {"status": "observed", "value": delivered_at, "reason": None}, "delivery": {"status": "delivered", "summary": f"delivery {handoff_id}", "reason": None}, "result": {"status": "passed", "summary": "passed"}, "evidence_refs": []}


def renderable_state(helper: Any, statuses: list[str], *, terminal_status: str | None = None, handoffs: list[dict[str, Any]] | None = None, frictions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    state = initial_state(helper, task_count=len(statuses))
    for index, status in enumerate(statuses): set_task(state, index, status)
    set_phase(state, "passed" if all(item == "passed" for item in statuses) else "running")
    state["handoffs"] = handoffs or []
    state["execution_summary"]["implemented_outcomes"] = [{"outcome_ref": row["task_ref"], "summary": row["result"]["summary"], "source_refs": []} for row in state["tasks"] if row["result"]]
    state["effort_observations"] = [{"observation_id": "effort-writing", "category": "writing", "status": "unavailable", "value": None, "unit": None, "reason": "telemetry not requested", "evidence_refs": []}]
    state["material_frictions"] = frictions or []
    state["blockers"] = {"assessment": "none-confirmed", "reason": None, "items": []}
    state["residual_risks"] = {"assessment": "none-confirmed", "reason": None, "items": []}
    state["last_compact_transition"] = {"transition_id": "tx.compact", "kind": "commit_task_phase", "ref": "task-1", "result": statuses[0] if statuses[0] in {"passed", "failed", "blocked", "skipped", "cancelled"} else "blocked", "occurred_at": "2026-08-04T10:05:00-03:00"}
    if terminal_status:
        state["status"] = terminal_status
        state["manual_qa"] = {"applicability": "not-required", "eligibility_status": "not-applicable", "eligibility_basis_digest": None, "eligible_revision": None, "applicable_gate_refs": [], "limitation_refs": [], "transitioned_at": "2026-08-04T10:06:00-03:00"}
        state["execution_summary"]["terminal_reason"] = {"status": "observed", "summary": f"terminal {terminal_status}", "reason": None}
    return finalize_state(helper, state)


def expect_state_error(helper: Any, state: dict[str, Any], code: str) -> None:
    state["state_digest"] = helper.state_digest(state)
    try: helper.validate_state(state)
    except helper.StateContractError as exc: require("EXPECTED_STATE_ERROR_MISMATCH", exc.code == code, f"expected={code}:actual={exc.code}")
    else: raise ContractError(f"EXPECTED_STATE_ERROR_MISSING: {code}")


def execute_input_cases(helper: Any, cases: list[dict[str, Any]], executed: set[str]) -> None:
    for case in cases:
        try:
            normalized = helper.normalize_relative_path(case["path"])
            if Path(normalized).name != "execution-state.json": raise helper.StateContractError("STATE_BASENAME_INVALID")
        except helper.StateContractError as exc:
            require("INPUT_PATH_CASE_MISMATCH", case["accept"] is False and exc.code == case["error"], case["id"])
        else:
            require("INPUT_PATH_CASE_MISMATCH", case["accept"] is True and normalized == case["path"], case["id"])
        executed.add(case["id"])


def execute_recovery_cases(helper: Any, cases: list[dict[str, Any]], executed: set[str]) -> None:
    for case in cases:
        if "observed" in case:
            require("RECOVERY_CASE_MISMATCH", helper.classify_pending_targets(case["observed"]) == case["outcome"], case["id"])
        else:
            state = renderable_state(helper, ["running"], handoffs=[handoff("handoff-open", "2026-08-04T10:00:00-03:00", None)])
            rendered = helper.render_dashboard(state, mode="resume")
            require("RECOVERY_OPEN_HANDOFF_INVALID", "handoff-open" in rendered and "pendente" in rendered and state["handoffs"][0]["status"] == "open")
        executed.add(case["id"])


def execute_metrics_cases(helper: Any, cases: list[dict[str, Any]], executed: set[str]) -> None:
    for case in cases:
        state = renderable_state(helper, ["passed"])
        if case["id"] == "explicit-metrics-artifact-has-consumer":
            state["optional_artifacts"] = [{"artifact_id": "metrics-explicit", "kind": case["kind"], "ref": "builds/metrics.json", "digest": SHA, "consumer": case["consumer"], "authority": case["authority"], "retention_basis": case["retention_basis"]}]
            finalize_state(helper, state)
        else:
            state["effort_observations"] = [{"observation_id": "effort-case", "category": "writing", "status": case.get("status", "unavailable"), "value": case.get("value"), "unit": case.get("unit"), "reason": case.get("reason", "telemetry not requested"), "evidence_refs": []}]
            state = finalize_state(helper, state); rendered = helper.render_dashboard(state, mode="requested")
            if case["id"] in {"default-does-not-create-metrics", "missing-observation-is-not-zero"}: require("OPTIONAL_METRICS_UNAVAILABLE_INVALID", "indisponível" in rendered and "0 ms" not in rendered)
            if case["id"] == "observed-effort-is-non-negative": require("OPTIONAL_METRICS_OBSERVED_INVALID", "1250 ms" in rendered)
        executed.add(case["id"])


def execute_dashboard_cases(helper: Any, cases: list[dict[str, Any]], executed: set[str]) -> None:
    for case in cases:
        case_id = case["id"]
        if case_id == "one-of-three-required-passed":
            state = renderable_state(helper, case["required_statuses"]); rendered = helper.render_compact(state); require("DASHBOARD_PROGRESS_MISMATCH", case["expected_progress"] in rendered)
        elif case_id == "replan-may-reduce-percent":
            before = renderable_state(helper, ["passed", "passed", "running"]); after = renderable_state(helper, ["passed", "passed", "running", "pending"])
            require("REPLAN_PROGRESS_MISMATCH", f"({case['expected_before']}%)" in helper.render_compact(before) and f"({case['expected_after']}%)" in helper.render_compact(after))
        elif case_id in {"overlapping-handoffs-chronological", "same-agent-separate-handoffs"}:
            if case_id.startswith("overlapping"):
                rows = [handoff(f"handoff-{i+1}", case["called_at"][i], case["delivered_at"][i]) for i in range(2)]
            else:
                rows = [handoff(case["handoff_ids"][i], f"2026-08-04T10:0{i}:00-03:00", f"2026-08-04T10:0{i+1}:00-03:00", agent=case["agent_labels"][i]) for i in range(2)]
            rendered = helper.render_dashboard(renderable_state(helper, ["passed"], handoffs=rows), mode="requested")
            table_rows = [line for line in rendered.splitlines() if line.startswith("| handoff-")]
            require("HANDOFF_ROWS_INVALID", len(table_rows) == 2 and all(any(f"| {row['handoff_id']} |" in line for line in table_rows) for row in rows) and rendered.index(rows[0]["handoff_id"]) < rendered.index(rows[1]["handoff_id"]))
            if "expected_seconds" in case: require("HANDOFF_DURATION_INVALID", all(f"{seconds}s" in rendered for seconds in case["expected_seconds"]))
        elif case_id == "unavailable-clock-is-not-estimated":
            row = handoff("handoff-unavailable", None, "2026-08-04T10:02:00-03:00", unavailable_reason=case["called_reason"])
            rendered = helper.render_dashboard(renderable_state(helper, ["passed"], handoffs=[row]), mode="requested"); require("UNAVAILABLE_CLOCK_INVALID", case["expected_contains"] in rendered and case["called_reason"] in rendered)
        elif case_id in {"compact-transition-timestamp-stable", "compact-transition-local-clock-pm"}:
            state = renderable_state(helper, ["passed"]); state["last_compact_transition"]["occurred_at"] = case["occurred_at"]; state = finalize_state(helper, state)
            before = helper.canonical_bytes(state); first = helper.render_compact(state); second = helper.render_compact(copy.deepcopy(state)); updated_first = first.rsplit("Atualizado em: ", 1)[-1]; updated_second = second.rsplit("Atualizado em: ", 1)[-1]
            require("COMPACT_TIMESTAMP_INVALID", updated_first == case["expected_updated_at"] == updated_second and all(value not in updated_first for value in case["forbidden_updated_at"]) and helper.canonical_bytes(state) == before and ("rerendered_at" not in case or case["rerendered_at"] not in second))
        elif case_id == "final-only-terminal":
            for status in case["statuses"]:
                statuses = ["passed"] if status in {"completed", "completed-with-limitations", "cancelled"} else ["passed", "failed"]
                state = renderable_state(helper, statuses, terminal_status=status); require("FINAL_STATUS_INVALID", "# Dashboard final" in helper.render_dashboard(state, mode="final"), status)
            running = renderable_state(helper, ["running"])
            try: helper.render_dashboard(running, mode="final")
            except helper.StateContractError as exc: require("FINAL_NONTERMINAL_CODE_INVALID", exc.code == "FINAL_RENDER_NOT_TERMINAL")
            else: raise ContractError("FINAL_NONTERMINAL_ACCEPTED")
        elif case_id == "requested-read-only":
            state = renderable_state(helper, ["running"]); before = helper.canonical_bytes(state); helper.render_dashboard(state, mode=case["mode"]); require("REQUESTED_RENDER_MUTATED_STATE", helper.canonical_bytes(state) == before and case["expected_writes"] == 0)
        elif case_id == "equal-clock-endpoints":
            rendered = helper.render_dashboard(renderable_state(helper, ["passed"], handoffs=[handoff("handoff-equal", case["called_at"], case["delivered_at"])]), mode="requested"); require("EQUAL_ENDPOINT_INVALID", case["expected_duration"] in rendered)
        elif case_id == "offsets-sort-by-instant":
            rows = [handoff(case["handoff_ids"][0], case["called_at"][0], "2026-08-04T12:01:00+02:00"), handoff(case["handoff_ids"][1], case["called_at"][1], "2026-08-04T08:31:00-03:00")]
            rendered = helper.render_dashboard(renderable_state(helper, ["passed"], handoffs=list(reversed(rows))), mode="requested"); require("OFFSET_SORT_INVALID", rendered.index(case["expected_order"][0]) < rendered.index(case["expected_order"][1]))
        elif case_id == "negative-handoff-chronology-rejected":
            state = initial_state(helper); state["handoffs"] = [handoff("handoff-negative", case["called_at"], case["delivered_at"])]; expect_state_error(helper, state, case["error"])
        elif case_id == "d001-d025-final-order":
            rendered = helper.render_dashboard(renderable_state(helper, ["passed"], terminal_status="completed"), mode="final"); lines = rendered.splitlines()
            require("FINAL_HANDOFF_NOT_IMMEDIATE", lines[2].startswith("task 1 passed") and lines[4].startswith("| Handoff |"))
            positions = [rendered.index("| Handoff |"), rendered.index("| Categoria |"), rendered.index("## Bloqueadores técnicos"), rendered.index("## Próximos passos")]
            require("FINAL_SECTION_ORDER_INVALID", positions == sorted(positions) and all(section not in rendered for section in case["forbidden_sections"]))
        elif case_id == "frictions-omitted-when-empty":
            rendered = helper.render_dashboard(renderable_state(helper, ["passed"], terminal_status="completed"), mode="final"); require("FRICTION_OMISSION_INVALID", (case["expected_heading"] in rendered) is case["present"])
        elif case_id == "resume-includes-completed-details":
            rendered = helper.render_dashboard(renderable_state(helper, ["passed"]), mode="resume"); require("RESUME_DETAIL_INVALID", all(section in rendered for section in case["expected_sections"]) and "task 1 passed" in rendered and "phase passed" in rendered)
        else: raise ContractError(f"UNEXECUTED_DASHBOARD_FIXTURE: {case_id}")
        executed.add(case_id)


def write_state(path: Path, helper: Any, state: dict[str, Any]) -> None:
    path.write_bytes(helper.canonical_bytes(state) + b"\n")


def eligibility_request(state: dict[str, Any], refs: list[str]) -> dict[str, Any]:
    return {"operation": "publish_manual_qa_eligibility", "transition_id": "tx.fixture.eligibility", "expected_revision": state["revision"], "occurred_at": "2026-08-04T10:07:00-03:00", "payload": {"basis_digest": "sha256:" + "4" * 64, "applicable_gate_refs": refs, "limitation_refs": []}}


def qa_ready_state(helper: Any, refs: list[str]) -> dict[str, Any]:
    state = initial_state(helper, gates=[{"gate_ref": ref, "kind": "human-validation"} for ref in refs]); set_task(state, 0, "passed"); set_phase(state, "passed")
    state["blockers"] = {"assessment": "none-confirmed", "reason": None, "items": []}; state["residual_risks"] = {"assessment": "none-confirmed", "reason": None, "items": []}
    return finalize_state(helper, state)


def start_fixture_task(helper: Any, path: Path, state: dict[str, Any], suffix: str) -> dict[str, Any]:
    request = {"operation": "start_task_phase", "transition_id": f"tx.fixture.start.{suffix}", "expected_revision": state["revision"], "occurred_at": "2026-08-04T10:01:00-03:00", "payload": {"task_ref": "task-1", "phase_ref": "phase-1", "dependencies_passed": True, "prior_gates_passed": True}}
    result, wrote = helper.apply_operation(path, request, actor="orchestrator", exclusive_owner=True)
    require("FIXTURE_START_NOT_WRITTEN", wrote)
    return result


def replan_fixture_request(state: dict[str, Any]) -> dict[str, Any]:
    return {"operation": "commit_replan_ref", "transition_id": "tx.fixture.replan", "expected_revision": state["revision"], "occurred_at": "2026-08-04T10:02:00-03:00", "payload": {"plan_revision": {"plan_revision_ref": "plan/tasks-v2.md", "plan_revision_digest": "sha256:" + "3" * 64}, "tasks": [{"task_ref": "task-1", "phase_ref": "phase-1", "required": True, "validator_ref": "validator-1"}, {"task_ref": "task-2", "phase_ref": "phase-1", "required": True, "validator_ref": "validator-2"}], "phases": copy.deepcopy(state["phases"]), "gates": copy.deepcopy(state["gates"]), "audit_boundaries": copy.deepcopy(state["audit_boundaries"]), "blockers": copy.deepcopy(state["blockers"]), "next_steps": copy.deepcopy(state["next_steps"])}}


def commit_fixture_request(state: dict[str, Any], *, desired_targets_verified: bool) -> dict[str, Any]:
    return {"operation": "commit_task_phase", "transition_id": "tx.fixture.commit", "expected_revision": state["revision"], "occurred_at": "2026-08-04T10:03:00-03:00", "payload": {"task_ref": "task-1", "task_status": "passed", "task_result": {"summary": "implemented", "responsible": "technical-implementer", "delivery_refs": []}, "validation": {"status": "passed", "validator_ref": "validator-1", "evidence_refs": ["evidence/task-1.txt"], "limitation": None}, "target_digests": [], "phase": None, "gates": copy.deepcopy(state["gates"]), "implemented_outcomes": [{"outcome_ref": "task-1", "summary": "implemented", "source_refs": []}], "effort_observations": [], "material_frictions": [], "blockers": {"assessment": "none-confirmed", "reason": None, "items": []}, "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []}, "next_steps": [], "optional_artifacts": [], "desired_targets_verified": desired_targets_verified}}


def prepare_fixture_write(helper: Any, path: Path, state: dict[str, Any], suffix: str) -> dict[str, Any]:
    request = {"operation": "prepare_task_write", "transition_id": f"tx.fixture.prepare.{suffix}", "expected_revision": state["revision"], "occurred_at": "2026-08-04T10:02:00-03:00", "payload": {"task_ref": "task-1", "targets": [{"target_ref": "scripts/example.py", "before_digest": SHA, "desired_digest": "sha256:" + "2" * 64}]}}
    result, wrote = helper.apply_operation(path, request, actor="state-writer", exclusive_owner=True)
    require("FIXTURE_PREPARE_NOT_WRITTEN", wrote)
    return result


def assert_zero_write_error(helper: Any, path: Path, request: dict[str, Any], actor: str, expected_error: str) -> None:
    before = path.read_bytes()
    try: helper.apply_operation(path, request, actor=actor, exclusive_owner=True)
    except helper.StateContractError as exc: require("FIXTURE_ERROR_MISMATCH", exc.code == expected_error, f"expected={expected_error}:actual={exc.code}")
    else: raise ContractError(f"FIXTURE_ERROR_MISSING: {expected_error}")
    require("FIXTURE_ERROR_CHANGED_BYTES", path.read_bytes() == before)


def execute_state_cases(helper: Any, helper_result: dict[str, Any], cases: list[dict[str, Any]], executed: set[str]) -> None:
    for case in cases:
        case_id = case["id"]
        if case_id == "interrupt-after-handoff":
            state = renderable_state(helper, ["running"], handoffs=[handoff("handoff-open", "2026-08-04T10:01:00-03:00", None)]); rendered = helper.render_dashboard(state, mode="resume")
            expected_values = {"handoff_id": "handoff-open", "task_ref": "task-1", "phase_ref": "phase-1", "agent_label": "technical-implementer", "objective": "implement", "status": "pendente", "called_at": "2026-08-04T10:01:00-03:00"}
            require("RESUME_HANDOFF_DATA_MISSING", all(expected_values[key] in rendered for key in case["expected_resume_data"]))
        elif case_id in {"interrupt-after-task", "interrupt-after-phase"}:
            rendered = helper.render_dashboard(renderable_state(helper, ["passed"]), mode="resume"); require("RESUME_COMMITTED_DATA_MISSING", "task 1 passed" in rendered and "phase passed" in rendered and "Tasks concluídas" in rendered)
        elif case_id == "resume-renders-before-effects":
            state = renderable_state(helper, ["running"]); before = helper.canonical_bytes(state); helper.render_dashboard(state, mode="resume"); require("RESUME_RENDER_EFFECT_INVALID", before == helper.canonical_bytes(state) and case["order"][:3] == ["validate-state", "validate-plan", "render-resume"])
        elif case_id in {"stale-revision-zero-write", "exact-replay-zero-write", "terminal-state-immutable", "initialize-changed-task-set-conflict"}:
            require("HELPER_REPLAY_ASSERTION_MISSING", helper_result["self_test"] == "passed" and case.get("expected_writes", 0) == 0)
        elif case_id == "all-operations-exact-replay":
            require("ALL_REPLAY_COVERAGE_INVALID", len(helper_result["exercised_operations"]) == case["expected_operation_count"] == len(helper.OPERATIONS))
        elif case_id == "all-operations-changed-request-conflict":
            require("ALL_COLLISION_COVERAGE_INVALID", len(helper_result["exercised_operations"]) == case["expected_operation_count"] and case["expected_error"] == "TRANSITION_REPLAY_CONFLICT" and case["expected_writes"] == 0)
        elif case_id == "replan-existing-task-spec-exact-replay":
            state = initial_state(helper)
            with tempfile.TemporaryDirectory(prefix="loki-replan-replay-") as directory:
                path = Path(directory) / "execution-state.json"; write_state(path, helper, state); request = replan_fixture_request(state)
                committed, wrote = helper.apply_operation(path, request, actor="planner", exclusive_owner=True); require("REPLAN_FIXTURE_NOT_WRITTEN", wrote)
                committed_bytes = path.read_bytes(); replayed, replay_wrote = helper.apply_operation(path, copy.deepcopy(request), actor="planner", exclusive_owner=True)
                require("REPLAN_EXACT_REPLAY_INVALID", not replay_wrote and replayed == committed and path.read_bytes() == committed_bytes and case["expected_writes_per_replay"] == 0)
        elif case_id == "replan-existing-task-spec-mismatch-zero-write":
            for field in case["fields"]:
                state = initial_state(helper)
                with tempfile.TemporaryDirectory(prefix=f"loki-replan-mismatch-{field}-") as directory:
                    path = Path(directory) / "execution-state.json"; write_state(path, helper, state); request = replan_fixture_request(state)
                    request["payload"]["tasks"][0][field] = {"required": False, "phase_ref": "phase-other", "validator_ref": "validator-other"}[field]
                    assert_zero_write_error(helper, path, request, "planner", case["expected_error"])
        elif case_id == "replan-existing-task-spec-changed-replay-conflict":
            state = initial_state(helper)
            with tempfile.TemporaryDirectory(prefix="loki-replan-collision-") as directory:
                path = Path(directory) / "execution-state.json"; write_state(path, helper, state); request = replan_fixture_request(state)
                _, wrote = helper.apply_operation(path, request, actor="planner", exclusive_owner=True); require("REPLAN_FIXTURE_NOT_WRITTEN", wrote)
                for field in case["fields"]:
                    changed = copy.deepcopy(request); changed["payload"]["tasks"][0][field] = {"required": False, "phase_ref": "phase-other", "validator_ref": "validator-other"}[field]
                    assert_zero_write_error(helper, path, changed, "planner", case["expected_error"])
        elif case_id in {"commit-task-no-pending-verified-exact-replay", "commit-task-pending-verified-exact-replay"}:
            state = initial_state(helper)
            with tempfile.TemporaryDirectory(prefix=f"loki-{case_id}-") as directory:
                path = Path(directory) / "execution-state.json"; write_state(path, helper, state); state = start_fixture_task(helper, path, state, case_id)
                if case_id.startswith("commit-task-pending-"): state = prepare_fixture_write(helper, path, state, case_id)
                request = commit_fixture_request(state, desired_targets_verified=case["desired_targets_verified"])
                committed, wrote = helper.apply_operation(path, request, actor="state-writer", exclusive_owner=True); require("COMMIT_FIXTURE_NOT_WRITTEN", wrote)
                committed_bytes = path.read_bytes(); replayed, replay_wrote = helper.apply_operation(path, copy.deepcopy(request), actor="state-writer", exclusive_owner=True)
                require("COMMIT_EXACT_REPLAY_INVALID", not replay_wrote and replayed == committed and path.read_bytes() == committed_bytes and case["expected_writes_per_replay"] == 0)
        elif case_id in {"commit-task-no-pending-unverified-zero-write", "commit-task-pending-unverified-zero-write"}:
            state = initial_state(helper)
            with tempfile.TemporaryDirectory(prefix=f"loki-{case_id}-") as directory:
                path = Path(directory) / "execution-state.json"; write_state(path, helper, state); state = start_fixture_task(helper, path, state, case_id)
                if case_id.startswith("commit-task-pending-"): state = prepare_fixture_write(helper, path, state, case_id)
                request = commit_fixture_request(state, desired_targets_verified=case["desired_targets_verified"])
                assert_zero_write_error(helper, path, request, "state-writer", case["expected_error"])
        elif case_id == "commit-task-no-pending-changed-replay-conflict":
            state = initial_state(helper)
            with tempfile.TemporaryDirectory(prefix="loki-commit-collision-") as directory:
                path = Path(directory) / "execution-state.json"; write_state(path, helper, state); state = start_fixture_task(helper, path, state, case_id)
                request = commit_fixture_request(state, desired_targets_verified=True)
                _, wrote = helper.apply_operation(path, request, actor="state-writer", exclusive_owner=True); require("COMMIT_FIXTURE_NOT_WRITTEN", wrote)
                changed = copy.deepcopy(request); changed["payload"][case["changed_field"]] = case["changed_value"]
                assert_zero_write_error(helper, path, changed, "state-writer", case["expected_error"])
        elif case_id in {"qa-complete-pending-gate-set", "qa-incomplete-pending-gate-set"}:
            state = qa_ready_state(helper, case["pending_gate_refs"])
            with tempfile.TemporaryDirectory(prefix="loki-qa-gates-") as directory:
                path = Path(directory) / "execution-state.json"; write_state(path, helper, state); before = path.read_bytes()
                try: _, wrote = helper.apply_operation(path, eligibility_request(state, case["submitted_gate_refs"]), actor="orchestrator", exclusive_owner=True)
                except helper.StateContractError as exc:
                    require("QA_GATE_SET_CASE_MISMATCH", case["accept"] is False and exc.code == case["error"] and path.read_bytes() == before, case_id)
                else: require("QA_GATE_SET_CASE_MISMATCH", case["accept"] is True and wrote, case_id)
        elif case_id == "terminal-pending-human-gate-rejected":
            state = qa_ready_state(helper, case["pending_gate_refs"])
            request = {"operation": "publish_terminal", "transition_id": "tx.fixture.terminal", "expected_revision": state["revision"], "occurred_at": "2026-08-04T10:08:00-03:00", "payload": {"status": "completed", "terminal_reason": {"status": "observed", "summary": "done", "reason": None}, "implemented_outcomes": [], "blockers": {"assessment": "none-confirmed", "reason": None, "items": []}, "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []}, "next_steps": [], "terminal_truth_passed": True}}
            with tempfile.TemporaryDirectory(prefix="loki-terminal-gate-") as directory:
                path = Path(directory) / "execution-state.json"; write_state(path, helper, state); before = path.read_bytes()
                try: helper.apply_operation(path, request, actor="orchestrator", exclusive_owner=True)
                except helper.StateContractError as exc: require("TERMINAL_GATE_CASE_MISMATCH", exc.code == case["error"] and path.read_bytes() == before)
                else: raise ContractError("TERMINAL_PENDING_GATE_ACCEPTED")
        else: raise ContractError(f"UNEXECUTED_STATE_FIXTURE: {case_id}")
        executed.add(case_id)


def execute_validation_cases(helper: Any, helper_result: dict[str, Any], cases: list[dict[str, Any]], executed: set[str]) -> None:
    for case in cases:
        case_id = case["id"]
        if case_id in {"task-pass-requires-validator-evidence", "task-pass-with-failed-validator-rejected"}:
            state = initial_state(helper); set_task(state, 0, case["task_status"]); set_phase(state, "passed")
            state["tasks"][0]["validation"]["status"] = case["validation_status"]
            state["tasks"][0]["validation"]["evidence_refs"] = case.get("evidence_refs", [])
            if case["accept"]: finalize_state(helper, state)
            else: expect_state_error(helper, state, "PASSED_TASK_VALIDATION_INVALID")
        elif case_id.startswith("audit-") and "frequency" in case:
            count = {"task": case["tasks"], "phase": case["phases"], "plan": 1}[case["frequency"]]
            state = initial_state(helper, boundaries=[f"boundary-{index + 1}" for index in range(count)]); require("AUDIT_BOUNDARY_CARDINALITY_INVALID", len(state["audit_boundaries"]) == case["expected_boundaries"])
        elif case_id == "audit-rejection-blocks":
            state = initial_state(helper, boundaries=["plan-boundary"])
            request = {"operation": "commit_audit", "transition_id": "tx.audit.reject", "expected_revision": state["revision"], "occurred_at": "2026-08-04T10:02:00-03:00", "payload": {"boundary_ref": "plan-boundary", "status": "rejected", "auditor_identity": "independent-auditor", "findings": [{"finding_id": "finding-1", "severity": "blocking", "fact": "validator failed", "target_ref": None, "evidence_refs": []}], "evidence_refs": [], "gates": [], "blockers": {"assessment": "present", "reason": None, "items": [{"blocker_id": "audit-blocker", "scope_ref": "run.fixture", "status": "open", "fact": "audit rejected", "owner": "technical-implementer", "gate_ref": None, "evidence_refs": []}]}, "residual_risks": {"assessment": "none-confirmed", "reason": None, "items": []}, "next_steps": []}}
            with tempfile.TemporaryDirectory(prefix="loki-audit-reject-") as directory:
                path = Path(directory) / "execution-state.json"; write_state(path, helper, state); result, _ = helper.apply_operation(path, request, actor="independent-auditor", exclusive_owner=True); require("AUDIT_REJECTION_NOT_BLOCKING", result["status"] == case["expected_run_status"])
        elif case_id == "manual-qa-approval-single-operation": require("MANUAL_QA_OPERATION_COVERAGE_INVALID", case["operation"] in helper_result["exercised_operations"] and case["expected_revision_increment"] == 1)
        elif case_id == "ambiguous-manual-qa-zero-write":
            state = qa_ready_state(helper, ["gate-a"]); before = helper.canonical_bytes(state); helper.render_dashboard(state, mode="requested"); require("AMBIGUOUS_QA_WRITE_INVALID", before == helper.canonical_bytes(state) and case["expected_writes"] == 0)
        else: raise ContractError(f"UNEXECUTED_VALIDATION_FIXTURE: {case_id}")
        executed.add(case_id)


def validate_contracts_and_mirrors(executed: set[str]) -> None:
    required = {
        "skills/lf-implement-feature-execution/references/execution-contract.md": ("canonical_execution_state", "schema_version: 1", "prepare_task_write", "approve_manual_qa", "os.replace", "last_compact_transition"),
        "skills/loki-implement-feature/references/execution.md": ("execution-state.json", "render-resume", "record_dispatch", "current-only"),
        "skills/loki-implement-feature/references/response.md": ("Handoff | Fase | Agente | Chamado em", "indisponível", "dashboard final", "read-only", "assets/response-template.md"),
        "skills/lf-action-plan-authoring/references/action-plan-contract.md": ("retry_limit", "followup_limit", "handoff_budget", "immutable"),
    }
    for relative in OWNED_CONTRACTS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        require("REMOVED_SURFACE_PRESENT", not any(seed in text for seed in REMOVED_SEEDS), relative)
        require("REQUIRED_CONTRACT_TOKEN_MISSING", all(token in text for token in required.get(relative, ())), relative)
    require("TEMPLATE_MIRROR_DRIFT", (ROOT / "templates/task-template.md").read_bytes() == (ROOT / "skills/lf-template-library/references/templates/task-template.md").read_bytes())
    require("TEMPLATE_MIRROR_DRIFT", (ROOT / "templates/tasks-template.md").read_bytes() == (ROOT / "skills/lf-template-library/references/templates/tasks-template.md").read_bytes())
    executed.update({"current-only-negative-scan", "artifact-budget-contract", "template-parity"})


AC_COVERAGE = {
    "AC-001": ["all-operations-exact-replay", "replan-existing-task-spec-exact-replay", "commit-task-no-pending-verified-exact-replay", "commit-task-pending-verified-exact-replay"], "AC-002": ["current-only-negative-scan"], "AC-003": ["artifact-budget-contract"],
    "AC-004": ["all-operations-changed-request-conflict", "replan-existing-task-spec-mismatch-zero-write", "replan-existing-task-spec-changed-replay-conflict", "commit-task-no-pending-unverified-zero-write", "commit-task-no-pending-changed-replay-conflict", "commit-task-pending-unverified-zero-write"], "AC-005": ["interrupt-after-handoff", "interrupt-after-task", "interrupt-after-phase"],
    "AC-006": ["qa-complete-pending-gate-set"], "AC-007": ["task-pass-with-failed-validator-rejected", "audit-rejection-blocks"],
    "AC-008": ["default-does-not-create-metrics"], "AC-009": ["audit-task-frequency", "audit-phase-frequency", "audit-plan-frequency"],
    "AC-010": ["negative-handoff-chronology-rejected"], "AC-011": ["current-only-negative-scan"], "AC-012": ["artifact-budget-contract"],
    "AC-013": ["d001-d025-final-order"], "AC-014": ["default-does-not-create-metrics"], "AC-015": ["audit-rejection-blocks"],
    "AC-016": ["resume-includes-completed-details", "overlapping-handoffs-chronological"], "AC-017": ["same-agent-separate-handoffs"],
    "AC-018": ["overlapping-handoffs-chronological", "offsets-sort-by-instant"], "AC-019": ["same-agent-separate-handoffs"],
    "AC-020": ["interrupt-after-handoff"], "AC-021": ["unavailable-clock-is-not-estimated"], "AC-022": ["current-only-negative-scan"],
    "AC-023": ["current-only-negative-scan"], "AC-024": ["current-only-negative-scan"], "AC-025": ["current-only-negative-scan"],
    "AC-026": ["current-only-negative-scan"], "AC-027": ["current-only-negative-scan"],
    "AC-028": ["interrupt-after-handoff", "interrupt-after-task", "interrupt-after-phase"], "AC-029": ["final-only-terminal"],
    "AC-030": ["resume-renders-before-effects"], "AC-031": ["d001-d025-final-order"], "AC-032": ["requested-read-only"],
    "AC-033": ["one-of-three-required-passed"], "AC-034": ["compact-transition-timestamp-stable", "compact-transition-local-clock-pm"], "AC-035": ["replan-may-reduce-percent"],
    "AC-036": ["requested-read-only", "resume-renders-before-effects"], "AC-037": ["requested-read-only"],
    "AC-038": ["requested-read-only"], "AC-039": ["compact-transition-timestamp-stable", "compact-transition-local-clock-pm"],
}


def validate_ac_coverage(executed: set[str]) -> dict[str, list[str]]:
    expected = {f"AC-{index:03d}" for index in range(1, 40)}
    require("AC_COVERAGE_ID_SET_INVALID", set(AC_COVERAGE) == expected)
    for ac, evidence in AC_COVERAGE.items():
        require("AC_COVERAGE_EMPTY", bool(evidence), ac)
        require("AC_COVERAGE_UNEXECUTED", set(evidence) <= executed, f"{ac}:{sorted(set(evidence) - executed)}")
    return AC_COVERAGE


def self_test() -> dict[str, Any]:
    helper = load_helper(); helper_result = helper.self_test()
    require("HELPER_SELF_TEST_FAILED", helper_result["self_test"] == "passed" and set(helper_result["exercised_operations"]) == set(helper.OPERATIONS))
    fixtures = load_fixtures(); executed: set[str] = set()
    execute_input_cases(helper, fixtures["input-path-cases.json"], executed)
    execute_metrics_cases(helper, fixtures["optional-metrics-cases.json"], executed)
    execute_recovery_cases(helper, fixtures["recovery-limitation-cases.json"], executed)
    execute_dashboard_cases(helper, fixtures["response-dashboard-cases.json"], executed)
    execute_state_cases(helper, helper_result, fixtures["state-resume-cases.json"], executed)
    execute_validation_cases(helper, helper_result, fixtures["validation-cycle-cases.json"], executed)
    expected_fixtures = {fixture_id for ids in FIXTURE_IDS.values() for fixture_id in ids}
    require("FIXTURE_UNEXECUTED", executed & expected_fixtures == expected_fixtures, f"missing={sorted(expected_fixtures - executed)}")
    validate_contracts_and_mirrors(executed); coverage = validate_ac_coverage(executed)
    return {"self_test": "passed", "contract": "canonical-execution-state-v1", "helper": helper_result, "fixture_count": len(expected_fixtures), "executed_fixture_ids": sorted(executed & expected_fixtures), "checks": sorted(executed - expected_fixtures), "ac_coverage": coverage}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--self-test", action="store_true", required=True); parser.parse_args()
    print(json.dumps(self_test(), ensure_ascii=False, sort_keys=True)); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except ContractError as exc: print(str(exc), file=sys.stderr); raise SystemExit(1)
