#!/usr/bin/env python3
"""Validate the current loki-implement-feature contract fixtures.

This validator is intentionally self-contained.  It does not import the
superseded run-plan validator and treats the four JSON fixture files beside it
as the executable examples of the current command/helper contracts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "scripts/fixtures/implement-feature"
FIXTURE_FILES = (
    "input-path-cases.json",
    "state-resume-cases.json",
    "validation-cycle-cases.json",
    "response-dashboard-cases.json",
)

MATRIX_SCENARIOS = (
    "Empty demand",
    "Missing/unreadable/non-Markdown analysis",
    "Material contradiction",
    "Target inferred beyond explicit demand",
    "Target absent from validated plan",
    "Absolute/traversing/backslash/symlink plan path",
    "Source-only valid plan directory",
    "Managed plan collision",
    "Valid resume",
    "Corrupt state",
    "New preflight",
    "Reused preflight",
    "Stale/expanded preflight",
    "Raw/private/secret preflight content",
    "Unsafe agent/run path identity",
    "Concurrent preflight publication",
    "Writer conflict",
    "Task without acceptance criterion",
    "Task without validation route",
    "Deterministic validation",
    "Write Test Agent validation",
    "Introduced/regression minor",
    "Introduced/regression medium or major",
    "Resolved medium/major with original Writer available",
    "Resolved medium/major without original Writer",
    "Learned file missing or invalid",
    "Exhausted medium/major retry",
    "Pre-existing failure",
    "Unknown attribution",
    "Optional soft-fail",
    "Required task validator unavailable",
    "Final regression",
    "Cancellation",
    "Human validation requested before DAG terminal",
    "Human validation at final reconciliation",
    "Ancillary Write Test Agent observation",
    "Per-task green/full-suite red",
    "Complete dashboard fixture",
    "Completion with failed AC/required validator",
    "Passed AC without evidence locator",
    "Manual step missing one required field",
    "Installed upgrade",
    "Upgrade fault after link mutation, before manifest publication",
)

INSTALLER_EXCLUSIONS = {
    "Installed upgrade",
    "Upgrade fault after link mutation, before manifest publication",
}
REQUIRED_SUPPLEMENTAL = {
    "invalid-demand-kind",
    "invalid-demand-utf8",
    "blocked-row-mapping",
    "learned-secret-content",
}

TASK_STATUSES = {"pending", "passed", "unresolved", "skipped-dependency", "cancelled"}
TERMINAL_SUCCESS = {"completed", "completed-with-limitations", "pending-human-validation"}
REQUIRED_MANUAL_FIELDS = {
    "evidence_or_acceptance_criterion_ref",
    "environment",
    "prerequisites",
    "initial_state",
    "action",
    "expected_observable_result",
    "success_signals",
    "failure_signals",
    "cleanup_or_restore",
    "automation_limitation",
}
SECRET_RE = re.compile(r"(?i)(private chain.of.thought|raw transcript|api[_ -]?key|password|secret\s*[:=])")
AGENT_PATH_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")
RUN_PATH_RE = re.compile(r"run-[0-9a-f]{32}")


class ContractError(ValueError):
    """A deterministic fixture or contract failure."""


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def list_nonempty(values: Any) -> bool:
    return isinstance(values, list) and bool(values) and all(nonempty(item) for item in values)


def reject(code: str, condition: bool) -> None:
    if condition:
        raise ContractError(code)


def require(code: str, condition: bool) -> None:
    if not condition:
        raise ContractError(code)


def rule_demand(p: dict[str, Any]) -> None:
    kind = p.get("kind")
    require("DEMAND_KIND_INVALID", kind in {"inline", "path"})
    require("DEMAND_UTF8_INVALID", p.get("valid_utf8") is True)
    require("DEMAND_EMPTY", nonempty(p.get("content")))
    if kind == "path":
        require("DEMAND_PATH_UNREADABLE", p.get("readable_regular_file") is True)
    require("DEMAND_KIND_AMBIGUOUS", p.get("classification_source") == "explicit-caller-or-adapter")


def rule_analysis(p: dict[str, Any]) -> None:
    require("ANALYSIS_INVALID", all(p.get(key) is True for key in ("exists", "readable", "regular", "nonempty")))
    require("ANALYSIS_NOT_MARKDOWN", isinstance(p.get("path"), str) and p["path"].endswith(".md"))


def rule_contradiction(p: dict[str, Any]) -> None:
    if p.get("material"):
        require("CONTRADICTION_REFS_MISSING", list_nonempty(p.get("source_refs")) and len(p["source_refs"]) >= 2)
        raise ContractError("MATERIAL_CONTRADICTION")


def rule_target(p: dict[str, Any]) -> None:
    planned = p.get("target") in p.get("planned_targets", [])
    require("TARGET_UNPLANNED", planned)
    if p.get("inferred"):
        decision = p.get("decision", {})
        require(
            "TARGET_DECISION_INCOMPLETE",
            all(nonempty(decision.get(key)) for key in ("rationale", "demand_or_ac_relation", "evidence", "impact", "validator")),
        )
    require("TARGET_WRITE_CHANGED_UNEXPECTEDLY", p.get("bytes_unchanged_on_rejection", True) is True)


def safe_plan_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        return False
    if any(segment in {"", ".", ".."} for segment in value.split("/")):
        return False
    path = PurePosixPath(value)
    return path.parts[:1] == ("planos",)


def rule_plan_path(p: dict[str, Any]) -> None:
    require("PLAN_PATH_UNSAFE", safe_plan_path(p.get("path")))
    require("PLAN_PATH_SYMLINK", p.get("symlink_ancestor") is False and p.get("destination_symlink") is False)
    require("PLAN_PATH_ESCAPE", p.get("canonical_contained") is True)
    require("PLAN_BASE_UNUSABLE", p.get("base_usable") is True)


def rule_plan_directory(p: dict[str, Any]) -> None:
    mode = p.get("mode")
    require("PLAN_DIRECTORY_MODE_INVALID", mode in {"cold-start", "resume"})
    if mode == "cold-start":
        require("COLD_START_MANAGED_COLLISION", p.get("managed_entries", []) == [])
        require("CREATE_EXCLUSIVE_REQUIRED", p.get("create_exclusive") is True)
    else:
        require("RESUME_STATE_MISSING", p.get("authoritative_state") is True)
        require("RESUME_IDENTITY_MISMATCH", p.get("matching_identity") is True)
        require("RESUME_DIGEST_MISMATCH", p.get("matching_input_digests") is True)


def rule_resume(p: dict[str, Any]) -> None:
    require("STATE_CORRUPT", p.get("schema_valid") is True and p.get("state_digest_valid") is True)
    require("RESUME_IDENTITY_MISMATCH", p.get("identity_matches") is True)
    require("RESUME_DUPLICATE_WRITE", p.get("duplicate_production_writes", 0) == 0)
    require("RESUME_DUPLICATE_PREFLIGHT", p.get("duplicate_preflights", 0) == 0)
    require("RESUME_DUPLICATE_CYCLE", p.get("duplicate_cycles", 0) == 0)
    require("CHAT_RECONSTRUCTION_FORBIDDEN", p.get("chat_reconstruction") is False)


def rule_preflight(p: dict[str, Any]) -> None:
    event = p.get("event")
    require("PREFLIGHT_EVENT_INVALID", event in {"created", "reused", "refreshed", "published"})
    require("PREFLIGHT_LOCATOR_MISSING", nonempty(p.get("locator")) and nonempty(p.get("digest")))
    require("PREFLIGHT_PATH_UNSAFE", AGENT_PATH_RE.fullmatch(p.get("agent_name_path", "")) is not None)
    require("PREFLIGHT_RUN_PATH_UNSAFE", RUN_PATH_RE.fullmatch(p.get("run_path_id", "")) is not None)
    require("PREFLIGHT_CONTENT_SENSITIVE", not SECRET_RE.search(json.dumps(p, sort_keys=True)))
    if event == "reused":
        require("PREFLIGHT_REUSE_INVALID", p.get("new_record") is False and p.get("coverage_contained") is True and p.get("sources_valid") is True)
    if event == "refreshed":
        require("PREFLIGHT_REFRESH_INVALID", p.get("old_immutable") is True and p.get("new_version", 0) > p.get("old_version", 0))
    if event == "published":
        require("PREFLIGHT_OVERWRITE", p.get("overwrite") is False)
        require("PREFLIGHT_RACE_INVALID", p.get("identical_reused") is True and p.get("different_digest_next_version") is True)


def rule_ownership(p: dict[str, Any]) -> None:
    owners = p.get("owners", [])
    require("OWNER_MISSING", list_nonempty(owners))
    require("WRITER_CONFLICT", len(set(owners)) == 1 or p.get("serialized") is True)


def rule_task(p: dict[str, Any]) -> None:
    criteria = p.get("acceptance_criteria")
    require("TASK_AC_MISSING", isinstance(criteria, list) and bool(criteria))
    require("TASK_AC_INVALID", all(isinstance(ac, dict) and nonempty(ac.get("id")) and nonempty(ac.get("statement")) for ac in criteria))
    route = p.get("primary_route")
    require("TASK_ROUTE_MISSING", isinstance(route, dict) and route.get("type") in {"deterministic", "write_test_agent"})
    require("TASK_VALIDATOR_REF_MISSING", nonempty(route.get("validator_ref")))
    require("TASK_STATUS_INVALID", p.get("status", "pending") in TASK_STATUSES)


def rule_deterministic_validation(p: dict[str, Any]) -> None:
    require("DETERMINISTIC_COMMAND_MISSING", nonempty(p.get("command")))
    require("DETERMINISTIC_RESULT_MISSING", p.get("result") in {"passed", "failed"})
    require("DETERMINISTIC_AC_MISSING", list_nonempty(p.get("acceptance_criterion_refs")))
    require("DETERMINISTIC_EVIDENCE_MISSING", list_nonempty(p.get("evidence_refs")))


def rule_cycle(p: dict[str, Any]) -> None:
    finding = p.get("finding", {})
    response = p.get("writer_response", {})
    require("CYCLE_SCHEMA_INVALID", finding.get("schema_version") == 1 and response.get("schema_version") == 1)
    require("CYCLE_IDENTITY_INVALID", nonempty(finding.get("cycle_id")) and response.get("finding_ref") == finding.get("locator"))
    require("CYCLE_AC_MISSING", list_nonempty(finding.get("acceptance_criterion_refs")))
    require("CYCLE_EVIDENCE_MISSING", list_nonempty(finding.get("evidence_refs")) and list_nonempty(response.get("evidence_refs")))
    require("CYCLE_OWNER_OVERWRITE", p.get("immutable_records") is True and p.get("distinct_owners") is True)
    classification = finding.get("classification")
    severity = finding.get("severity")
    require("CYCLE_CLASSIFICATION_INVALID", classification in {"pre-existing", "introduced", "regression", "unknown", "soft-fail"})
    require("CYCLE_SEVERITY_INVALID", (classification in {"introduced", "regression"} and severity in {"minor", "medium", "major"}) or (classification not in {"introduced", "regression"} and severity is None))
    retry = finding.get("retry_consumed")
    require("CYCLE_RETRY_INVALID", retry is (classification in {"introduced", "regression"} and severity in {"medium", "major"}))


def rule_retry(p: dict[str, Any]) -> None:
    severity = p.get("severity")
    require("RETRY_SEVERITY_INVALID", severity in {"minor", "medium", "major"})
    if severity == "minor":
        require("MINOR_RETRY_CONSUMED", p.get("consumed", 0) == 0)
        require("MINOR_SCHEDULER_YIELD_MISSING", p.get("scheduler_yield") is True)
    else:
        limit = p.get("retry_limit", 3)
        require("RETRY_LIMIT_INVALID", isinstance(limit, int) and limit >= 0)
        require("RETRY_BUDGET_EXCEEDED", 0 <= p.get("consumed", -1) <= limit)
        require("INITIAL_VALIDATION_MISSING", p.get("initial_validation") is True)


def rule_learned(p: dict[str, Any]) -> None:
    if p.get("status") == "missing":
        require("LEARNED_MISSING_CHANGED_TASK_RESULT", p.get("task_result_unchanged") is True)
        require("LEARNED_LIMITATION_MISSING", nonempty(p.get("dashboard_limitation")))
        return
    require("LEARNED_TRIGGER_INVALID", p.get("resolved_severity") in {"medium", "major"} and p.get("approved_retest") is True)
    require("LEARNED_OWNER_INVALID", p.get("owner") == "applicable-writer")
    require("LEARNED_COUNT_INVALID", p.get("files_for_finding") == 1)
    require("LEARNED_REFS_MISSING", all(nonempty(p.get(key)) for key in ("finding_ref", "writer_response_ref", "retest_ref")))
    require("LEARNED_SESSION_DEPENDENCY", p.get("transcript_required") is False)
    require("LEARNED_CONTENT_UNSAFE", not SECRET_RE.search(p.get("content", "")))
    require("LEARNED_CAUSE_UNSUPPORTED", p.get("cause_supported") is True)


def rule_scheduler(p: dict[str, Any]) -> None:
    require("FAILED_TASK_NOT_UNRESOLVED", p.get("failed_task_status") == "unresolved")
    require("TRANSITIVE_SKIP_INVALID", set(p.get("skipped", [])) == set(p.get("transitive_dependents", [])))
    require("INDEPENDENT_TASK_STOPPED", p.get("independent_continues") is True)


def rule_classification(p: dict[str, Any]) -> None:
    kind = p.get("classification")
    require("FAILURE_CLASSIFICATION_INVALID", kind in {"pre-existing", "unknown", "soft-fail"})
    require("FAILURE_RETRY_CONSUMED", p.get("retry_consumed") is False)
    if kind == "pre-existing":
        require("PREEXISTING_EVIDENCE_MISSING", p.get("comparable_analysis_evidence") is True and p.get("not_worsened") is True)
    if kind == "unknown":
        require("UNKNOWN_SCOPE_EXPANSION", p.get("scope_expanded") is False)
        require("UNKNOWN_DASHBOARD_INCOMPLETE", all(nonempty(p.get(key)) for key in ("observed", "evidence_gap", "affected_criterion", "investigation_recommendation")))
    if kind == "soft-fail":
        require("SOFT_FAIL_STATUS_INVALID", p.get("terminal_status") not in {"completed", "pending-human-validation"})


def rule_execution_state(p: dict[str, Any]) -> None:
    event = p.get("event")
    require("EXECUTION_EVENT_INVALID", event in {"validator-unavailable", "final-regression", "cancellation", "human-request", "ancillary-observation", "full-suite"})
    if event == "validator-unavailable":
        require("VALIDATOR_UNAVAILABLE_MAPPING", p.get("task_status") == "unresolved" and p.get("dependents_skipped") is True and p.get("independent_continues") is True)
    elif event == "final-regression":
        require("FINAL_REGRESSION_FALSE_SUCCESS", p.get("severity_policy_applied") is True and p.get("terminal_status") not in TERMINAL_SUCCESS)
    elif event == "cancellation":
        require("CANCELLATION_INVALID", p.get("dispatch_stopped") is True and p.get("checkpoint_persisted") is True and p.get("terminal_status") == "cancelled")
    elif event == "human-request":
        if p.get("dag_terminal"):
            require("HUMAN_FINAL_STATUS_INVALID", p.get("sole_remaining_condition") is True and p.get("terminal_status") == "pending-human-validation")
        else:
            require("HUMAN_REQUEST_INTERRUPTED_DAG", p.get("accumulated") is True and p.get("dispatch_interrupted") is False)
    elif event == "ancillary-observation":
        require("ANCILLARY_PROMOTED_TO_TASK_RESULT", p.get("linked_structured_finding") is False and p.get("projected_as") == "dashboard-risk")
    else:
        require("FULL_SUITE_FALSE_SUCCESS", p.get("task_green") is True and p.get("full_suite") == "failed" and p.get("terminal_status") not in TERMINAL_SUCCESS)


def rule_dashboard(p: dict[str, Any]) -> None:
    status = p.get("status")
    require("DASHBOARD_STATUS_INVALID", status in {"completed", "completed-with-limitations", "pending-human-validation", "partial", "blocked", "failed", "cancelled", "needs-human-review"})
    required = {"summary", "units", "changed_files", "acceptance_criteria", "validators", "validation_cycles", "deviations", "inferred_targets", "learned_records", "decisions", "manual_test", "evidence", "risks", "resume"}
    require("DASHBOARD_CATEGORY_MISSING", required <= set(p))
    for ac in p.get("acceptance_criteria", []):
        require("AC_STATE_INVALID", ac.get("state") in {"passed", "failed", "not-demonstrated", "not-applicable"})
        if ac.get("state") == "passed":
            require("PASSED_AC_EVIDENCE_MISSING", nonempty(ac.get("evidence")))
    failures = any(ac.get("state") in {"failed", "not-demonstrated"} for ac in p.get("acceptance_criteria", []))
    validator_failed = any(v.get("required") and v.get("result") != "passed" for v in p.get("validators", []))
    require("TERMINAL_FALSE_SUCCESS", not (status in TERMINAL_SUCCESS and (failures or validator_failed)))
    task_rows = [row for row in p.get("units", []) if row.get("kind") == "task"]
    require("TASK_BLOCKED_ROW_FORBIDDEN", all(row.get("status") != "blocked" for row in task_rows))
    blocked_rows = [row for row in p.get("units", []) if row.get("status") == "blocked"]
    if status == "blocked":
        require("BLOCKED_SCOPE_ROW_INVALID", len(blocked_rows) == 1 and str(blocked_rows[0].get("unit", "")).startswith("blocked-scope:") and nonempty(blocked_rows[0].get("state_ref")) and list_nonempty(blocked_rows[0].get("blockers")) and nonempty(blocked_rows[0].get("next_action")))
    else:
        require("BLOCKED_SCOPE_ROW_UNEXPECTED", not blocked_rows)


def rule_manual(p: dict[str, Any]) -> None:
    status = p.get("status")
    require("MANUAL_STATUS_INVALID", status in {"steps", "none"})
    if status == "none":
        require("MANUAL_NONE_REASON_MISSING", nonempty(p.get("reason")) and p.get("steps") == [])
        return
    require("MANUAL_STEPS_MISSING", isinstance(p.get("steps"), list) and bool(p["steps"]))
    for step in p["steps"]:
        require("MANUAL_FIELD_MISSING", REQUIRED_MANUAL_FIELDS <= set(step))
        require("MANUAL_FIELD_EMPTY", all(nonempty(step[key]) for key in REQUIRED_MANUAL_FIELDS - {"prerequisites", "success_signals", "failure_signals"}))
        require("MANUAL_SIGNALS_MISSING", list_nonempty(step["success_signals"]) and list_nonempty(step["failure_signals"]) and isinstance(step["prerequisites"], list))


RULES: dict[str, Callable[[dict[str, Any]], None]] = {
    "demand": rule_demand,
    "analysis": rule_analysis,
    "contradiction": rule_contradiction,
    "target": rule_target,
    "plan-path": rule_plan_path,
    "plan-directory": rule_plan_directory,
    "resume": rule_resume,
    "preflight": rule_preflight,
    "ownership": rule_ownership,
    "task": rule_task,
    "deterministic-validation": rule_deterministic_validation,
    "cycle": rule_cycle,
    "retry": rule_retry,
    "learned": rule_learned,
    "scheduler": rule_scheduler,
    "classification": rule_classification,
    "execution-state": rule_execution_state,
    "dashboard": rule_dashboard,
    "manual": rule_manual,
}


def load_fixtures() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cases: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for name in FIXTURE_FILES:
        path = FIXTURE_ROOT / name
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ContractError(f"FIXTURE_READ_INVALID:{name}:{exc}") from exc
        require("FIXTURE_SCHEMA_INVALID", document.get("schema_version") == 1)
        require("FIXTURE_CASES_INVALID", isinstance(document.get("cases"), list))
        cases.extend(document["cases"])
        exclusions.extend(document.get("matrix_exclusions", []))
    return cases, exclusions


def validate_coverage(cases: list[dict[str, Any]], exclusions: list[dict[str, Any]]) -> None:
    matrix = set(MATRIX_SCENARIOS)
    implemented = [case.get("scenario") for case in cases if case.get("matrix") is True]
    require("MATRIX_CASE_UNKNOWN", all(item in matrix for item in implemented))
    require("MATRIX_CASE_DUPLICATE", len(implemented) == len(set(implemented)))
    exclusion_names = [item.get("scenario") for item in exclusions]
    require("MATRIX_EXCLUSION_DUPLICATE", len(exclusion_names) == len(set(exclusion_names)))
    require("MATRIX_EXCLUSION_INVALID", set(exclusion_names) == INSTALLER_EXCLUSIONS)
    require("MATRIX_EXCLUSION_ROUTE_INVALID", all(item.get("routed_to") == "task-3.2" and nonempty(item.get("reason")) for item in exclusions))
    require("MATRIX_COVERAGE_INCOMPLETE", set(implemented) == matrix - INSTALLER_EXCLUSIONS)
    supplements = {case.get("id") for case in cases if case.get("matrix") is False}
    require("SUPPLEMENTAL_COVERAGE_INCOMPLETE", REQUIRED_SUPPLEMENTAL <= supplements)


def validate_case(case: dict[str, Any]) -> tuple[bool, str | None]:
    require("CASE_ID_MISSING", nonempty(case.get("id")))
    require("CASE_SCENARIO_MISSING", nonempty(case.get("scenario")))
    rule = case.get("rule")
    require("CASE_RULE_INVALID", rule in RULES)
    require("CASE_EXPECT_INVALID", case.get("expect") in {"accept", "reject"})
    require("CASE_PAYLOAD_INVALID", isinstance(case.get("payload"), dict))
    try:
        RULES[rule](case["payload"])
        accepted, code = True, None
    except ContractError as exc:
        accepted, code = False, str(exc)
    if case["expect"] == "accept":
        require("CASE_UNEXPECTED_REJECTION", accepted)
    else:
        require("CASE_UNEXPECTED_ACCEPTANCE", not accepted)
        require("CASE_ERROR_MISMATCH", code == case.get("error"))
    return accepted, code


def self_test() -> dict[str, Any]:
    cases, exclusions = load_fixtures()
    validate_coverage(cases, exclusions)
    results = []
    seen_ids: set[str] = set()
    for case in cases:
        require("CASE_ID_DUPLICATE", case.get("id") not in seen_ids)
        seen_ids.add(case["id"])
        accepted, code = validate_case(case)
        results.append({"id": case["id"], "result": "accepted" if accepted else "expected-rejection", "error": code})
    return {
        "status": "passed",
        "schema_version": 1,
        "fixture_files": list(FIXTURE_FILES),
        "matrix_total": len(MATRIX_SCENARIOS),
        "matrix_implemented": len(MATRIX_SCENARIOS) - len(INSTALLER_EXCLUSIONS),
        "matrix_excluded": len(INSTALLER_EXCLUSIONS),
        "excluded_scenarios": sorted(INSTALLER_EXCLUSIONS),
        "exclusion_destination": "task-3.2",
        "supplemental_required": sorted(REQUIRED_SUPPLEMENTAL),
        "cases_executed": len(results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run every current contract fixture")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("--self-test is required")
    try:
        print(json.dumps(self_test(), indent=2, sort_keys=True, ensure_ascii=False))
    except ContractError as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
