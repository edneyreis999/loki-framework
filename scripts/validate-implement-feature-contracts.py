#!/usr/bin/env python3
"""Validate the current loki-implement-feature contract fixtures.

This validator is intentionally self-contained.  It does not import the
superseded run-plan validator and treats the five JSON fixture files beside it
as the executable examples of the current command/helper contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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
    "execution-metrics-cases.json",
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
    "metrics-exact",
    "metrics-estimated",
    "metrics-unavailable",
    "metrics-nested-spans",
    "metrics-absent-clock",
    "metrics-resume-no-double-count",
    "metrics-cumulative-not-agent",
    "metrics-telemetry-nonblocking",
    "metrics-missing-root-field",
    "metrics-extra-root-field",
    "metrics-digest-mismatch",
    "metrics-aggregate-mismatch",
    "metrics-orphan-span",
    "metrics-cyclic-span",
    "metrics-cumulative-per-agent",
    "metrics-unavailable-zero",
    "metrics-publication-failure",
    "metrics-publication-failure-invalid",
    "dashboard-publication-failure",
    "metrics-critical-path-truncated",
    "consistency-unknown-metrics-status",
    "materiality-invalid-before-auditor",
    "materiality-valid-independent",
    "consistency-divergence",
    "silence-running-not-aborted",
    "silence-unsupported-recorded",
    "no-cost-budget-or-auto-stop",
    "reject-state-v1",
    "reject-result-v1",
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
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SPAN_ID_RE = re.compile(r"^execution-span-v1:[0-9a-f]{64}$")
METRICS_ID_RE = re.compile(r"^execution-metrics-v1:[0-9a-f]{64}$")
TYPED_ID_RE = re.compile(r"^[a-z][a-z0-9-]*:[A-Za-z0-9][A-Za-z0-9._-]*$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
SPAN_KINDS = {"run", "phase", "task", "handoff", "validator", "gate", "audit", "reconciliation"}


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
    require("STATE_SCHEMA_SUPERSEDED", p.get("state_schema_version") == 2)
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
    required = {"summary", "units", "changed_files", "acceptance_criteria", "validators", "validation_cycles", "deviations", "inferred_targets", "learned_records", "decisions", "manual_test", "evidence", "risks", "resume", "execution_metrics_ref", "execution_metrics_digest", "execution_metrics_status", "execution_metrics_degradation_reason", "cost_resources"}
    require("DASHBOARD_CATEGORY_MISSING", required <= set(p))
    require("DASHBOARD_METRICS_STATUS_INVALID", p.get("execution_metrics_status") in {"complete", "partial", "unavailable"})
    validate_metrics_projection(p, "DASHBOARD")
    if p.get("execution_metrics_status") != "complete":
        require("DASHBOARD_METRICS_REASON_MISSING", nonempty(p.get("execution_metrics_degradation_reason")))
    cost = p.get("cost_resources", {})
    require("DASHBOARD_COST_CONTROL_FORBIDDEN", cost.get("token_budget") is None and cost.get("cost_budget") is None and cost.get("automatic_cost_stop") is False)
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


def rule_current_schema(p: dict[str, Any]) -> None:
    artifact = p.get("artifact")
    require("CURRENT_SCHEMA_ARTIFACT_INVALID", artifact in {"state", "result"})
    expected = 2
    require(f"{artifact.upper()}_SCHEMA_SUPERSEDED", p.get("schema_version") == expected)


def validate_usage(usage: Any) -> None:
    require("METRICS_USAGE_INVALID", isinstance(usage, dict))
    require("METRICS_USAGE_FIELDS_INVALID", set(usage) == {"status", "exact", "estimate", "unavailable_reason"})
    status = usage.get("status")
    require("METRICS_USAGE_STATUS_INVALID", status in {"exact", "estimated", "unavailable"})
    exact = usage.get("exact")
    estimate = usage.get("estimate")
    reason = usage.get("unavailable_reason")
    if status == "exact":
        require("METRICS_EXACT_MIXED", estimate is None and reason is None and isinstance(exact, dict))
        require("METRICS_EXACT_FIELDS_INVALID", set(exact) == {"source_scope", "source", "measured_at_utc", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens"})
        require("METRICS_EXACT_SCOPE_INVALID", exact.get("source_scope") == "verified-agent-run")
        require("METRICS_EXACT_SOURCE_MISSING", nonempty(exact.get("source")) and isinstance(exact.get("measured_at_utc"), str) and UTC_RE.fullmatch(exact["measured_at_utc"]))
        counters = [exact.get(key) for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")]
        require("METRICS_EXACT_COUNTER_INVALID", all(type(value) is int and value >= 0 for value in counters))
        require("METRICS_EXACT_TOTAL_INVALID", counters[4] == counters[0] + counters[2])
    elif status == "estimated":
        require("METRICS_ESTIMATE_MIXED", exact is None and reason is None and isinstance(estimate, dict))
        require("METRICS_ESTIMATE_FIELDS_INVALID", set(estimate) == {"method", "observable_payload_bytes", "estimated_tokens", "lower_bound_tokens", "upper_bound_tokens", "confidence", "scope", "sanitized_observable_only"})
        byte_count = estimate.get("observable_payload_bytes")
        require("METRICS_ESTIMATE_BYTES_INVALID", type(byte_count) is int and byte_count >= 0)
        require("METRICS_ESTIMATE_METHOD_INVALID", estimate.get("method") == "utf8-byte-estimate-v1")
        require(
            "METRICS_ESTIMATE_FORMULA_INVALID",
            estimate.get("estimated_tokens") == math.ceil(byte_count / 4)
            and estimate.get("lower_bound_tokens") == math.ceil(byte_count / 6)
            and estimate.get("upper_bound_tokens") == math.ceil(byte_count / 2),
        )
        require("METRICS_ESTIMATE_SCOPE_INVALID", estimate.get("confidence") == "low" and estimate.get("scope") == "partial" and estimate.get("sanitized_observable_only") is True)
    else:
        require("METRICS_UNAVAILABLE_INVALID", exact is None and estimate is None and nonempty(reason))


def metrics_hash(p: dict[str, Any]) -> str:
    canonical = {key: value for key, value in p.items() if key not in {"metrics_id", "metrics_digest"}}
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def rule_metrics(p: dict[str, Any]) -> None:
    root_keys = {"schema_version", "metrics_id", "run_id", "execution_id", "generated_at_utc", "status", "degradation_reason", "clock_provenance", "spans", "aggregates", "telemetry_changed_functional_status", "metrics_digest"}
    require("METRICS_ROOT_FIELDS_INVALID", set(p) == root_keys)
    require("METRICS_SCHEMA_INVALID", p.get("schema_version") == 1)
    require("METRICS_ID_INVALID", isinstance(p.get("metrics_id"), str) and METRICS_ID_RE.fullmatch(p["metrics_id"]))
    require("METRICS_RUN_ID_INVALID", isinstance(p.get("run_id"), str) and TYPED_ID_RE.fullmatch(p["run_id"]))
    require("METRICS_EXECUTION_ID_INVALID", isinstance(p.get("execution_id"), str) and TYPED_ID_RE.fullmatch(p["execution_id"]))
    require("METRICS_GENERATED_AT_INVALID", isinstance(p.get("generated_at_utc"), str) and UTC_RE.fullmatch(p["generated_at_utc"]))
    digest_hex = metrics_hash(p)
    require("METRICS_DIGEST_MISMATCH", p.get("metrics_id") == f"execution-metrics-v1:{digest_hex}" and p.get("metrics_digest") == f"sha256:{digest_hex}")
    require("METRICS_STATUS_INVALID", p.get("status") in {"complete", "partial", "unavailable"})
    if p.get("status") == "complete":
        require("METRICS_COMPLETE_REASON_INVALID", p.get("degradation_reason") is None)
    else:
        require("METRICS_DEGRADATION_REASON_MISSING", nonempty(p.get("degradation_reason")))
    clock_root = p.get("clock_provenance")
    require("METRICS_CLOCK_ROOT_FIELDS_INVALID", isinstance(clock_root, dict) and set(clock_root) == {"wall_clock", "monotonic_clock", "reason"})
    require("METRICS_CLOCK_ROOT_INVALID", clock_root.get("wall_clock") in {"observed", "partial", "unavailable"} and clock_root.get("monotonic_clock") in {"observed", "partial", "unavailable"})
    if "observed" == clock_root.get("wall_clock") == clock_root.get("monotonic_clock"):
        require("METRICS_CLOCK_ROOT_REASON_INVALID", clock_root.get("reason") is None)
    else:
        require("METRICS_CLOCK_ROOT_REASON_MISSING", nonempty(clock_root.get("reason")))
    spans = p.get("spans")
    require("METRICS_SPANS_INVALID", isinstance(spans, list) and bool(spans))
    ids = [span.get("span_id") for span in spans]
    require("METRICS_SPAN_ID_INVALID", len(ids) == len(set(ids)) and all(isinstance(item, str) and SPAN_ID_RE.fullmatch(item) for item in ids))
    roots = [span for span in spans if span.get("parent_span_id") is None]
    require("METRICS_ROOT_INVALID", len(roots) == 1 and roots[0].get("kind") == "run")
    span_map = {span["span_id"]: span for span in spans}
    replay_keys: set[tuple[Any, ...]] = set()
    for span in spans:
        span_keys = {"span_id", "kind", "parent_span_id", "owner", "status", "started_at_utc", "ended_at_utc", "monotonic_duration_ms", "clock_provenance", "clock_degradation_reason", "iteration", "replay", "replay_cause", "cause_span_id", "correlation_refs", "duplicates_child_usage", "usage", "validator_observation"}
        require("METRICS_SPAN_FIELDS_INVALID", set(span) == span_keys)
        require("METRICS_SPAN_KIND_INVALID", span.get("kind") in SPAN_KINDS)
        require("METRICS_SPAN_OWNER_MISSING", span.get("owner") == "orchestrator" or (isinstance(span.get("owner"), str) and TYPED_ID_RE.fullmatch(span["owner"])))
        require("METRICS_SPAN_STATUS_INVALID", span.get("status") in {"scheduled", "running", "completed", "partial", "blocked", "failed", "cancelled", "unavailable"})
        for time_key in ("started_at_utc", "ended_at_utc"):
            value = span.get(time_key)
            require("METRICS_SPAN_TIMESTAMP_INVALID", value is None or (isinstance(value, str) and UTC_RE.fullmatch(value)))
        require("METRICS_SPAN_ITERATION_INVALID", type(span.get("iteration")) is int and span["iteration"] >= 0)
        parent = span.get("parent_span_id")
        require("METRICS_PARENT_MISSING", parent is None or parent in span_map)
        require("METRICS_PARENT_USAGE_DUPLICATED", span.get("duplicates_child_usage") is False)
        clock = span.get("clock_provenance")
        require("METRICS_CLOCK_INVALID", clock in {"observed", "partial", "unavailable"})
        duration = span.get("monotonic_duration_ms")
        require("METRICS_DURATION_INVALID", duration is None or (type(duration) is int and duration >= 0))
        if clock == "observed":
            require("METRICS_CLOCK_REASON_INVALID", duration is not None and span.get("clock_degradation_reason") is None)
        else:
            require("METRICS_CLOCK_REASON_MISSING", nonempty(span.get("clock_degradation_reason")))
        require("METRICS_REPLAY_FLAG_INVALID", type(span.get("replay")) is bool)
        if span.get("replay"):
            require("METRICS_REPLAY_CAUSE_MISSING", nonempty(span.get("replay_cause")) and span.get("cause_span_id") in span_map)
            replay_key = (span.get("cause_span_id"), span.get("replay_cause"), span.get("iteration"), span.get("kind"))
            require("METRICS_REPLAY_CAUSE_DUPLICATE", replay_key not in replay_keys)
            replay_keys.add(replay_key)
        else:
            require("METRICS_REPLAY_CAUSE_INVALID", span.get("replay_cause") is None and span.get("cause_span_id") is None)
        refs = span.get("correlation_refs")
        require("METRICS_CORRELATION_REFS_INVALID", isinstance(refs, list) and len(refs) == len(set(refs)) and all(nonempty(item) for item in refs))
        validate_usage(span.get("usage"))
        if span.get("kind") == "validator":
            observation = span.get("validator_observation")
            require("METRICS_VALIDATOR_OBSERVATION_MISSING", isinstance(observation, dict))
            require("METRICS_VALIDATOR_FIELDS_INVALID", set(observation) == {"command", "validator_version", "input_digest", "policy_digest", "execution_mode", "replay_cause", "would_reuse"})
            require("METRICS_VALIDATOR_PROVENANCE_MISSING", all(nonempty(observation.get(key)) for key in ("command", "validator_version", "input_digest", "policy_digest")))
            require("METRICS_VALIDATOR_DIGEST_INVALID", SHA256_RE.fullmatch(observation["input_digest"]) and SHA256_RE.fullmatch(observation["policy_digest"]))
            require("METRICS_VALIDATOR_MODE_INVALID", observation.get("execution_mode") in {"executed", "referenced"} and type(observation.get("would_reuse")) is bool)
            require("METRICS_VALIDATOR_REPLAY_CAUSE_INVALID", observation.get("replay_cause") == span.get("replay_cause"))
        else:
            require("METRICS_VALIDATOR_OBSERVATION_FORBIDDEN", span.get("validator_observation") is None)
    for start in ids:
        seen: set[str] = set()
        current = start
        while current is not None:
            require("METRICS_SPAN_CYCLE", current not in seen)
            seen.add(current)
            current = span_map[current].get("parent_span_id")
    aggregates = p.get("aggregates")
    require("METRICS_AGGREGATES_INVALID", isinstance(aggregates, dict))
    aggregate_keys = {"exact_usage", "estimated_usage", "non_agent_observations", "counts", "durations", "critical_path_span_ids", "unavailable_reasons"}
    require("METRICS_AGGREGATE_FIELDS_INVALID", set(aggregates) == aggregate_keys)
    exact_keys = {"input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens"}
    estimate_keys = {"estimated_tokens", "lower_bound_tokens", "upper_bound_tokens", "observable_payload_bytes", "confidence"}
    require("METRICS_AGGREGATE_EXACT_FIELDS_INVALID", isinstance(aggregates.get("exact_usage"), dict) and set(aggregates["exact_usage"]) == exact_keys)
    require("METRICS_AGGREGATE_ESTIMATE_FIELDS_INVALID", isinstance(aggregates.get("estimated_usage"), dict) and set(aggregates["estimated_usage"]) == estimate_keys)
    exact_rows = [span["usage"]["exact"] for span in spans if span["usage"]["status"] == "exact"]
    expected_exact = {key: sum(row[key] for row in exact_rows) for key in exact_keys} if exact_rows else {key: None for key in exact_keys}
    require("METRICS_AGGREGATE_EXACT_MISMATCH", aggregates["exact_usage"] == expected_exact)
    estimate_rows = [span["usage"]["estimate"] for span in spans if span["usage"]["status"] == "estimated"]
    expected_estimate = {key: sum(row[key] for row in estimate_rows) for key in estimate_keys - {"confidence"}} if estimate_rows else {key: None for key in estimate_keys - {"confidence"}}
    expected_estimate["confidence"] = "low" if estimate_rows else "unavailable"
    require("METRICS_AGGREGATE_ESTIMATE_MISMATCH", aggregates["estimated_usage"] == expected_estimate)
    observations = aggregates.get("non_agent_observations")
    require("METRICS_NON_AGENT_OBSERVATIONS_INVALID", isinstance(observations, list))
    observation_keys = {"observation_id", "source", "source_scope", "measured_at_utc", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens", "allocated_per_agent"}
    for item in observations:
        require("METRICS_NON_AGENT_FIELDS_INVALID", isinstance(item, dict) and set(item) == observation_keys)
        require("METRICS_NON_AGENT_SCOPE_INVALID", item.get("source_scope") in {"cumulative", "account-window"} and item.get("allocated_per_agent") is False)
        require("METRICS_NON_AGENT_ID_INVALID", isinstance(item.get("observation_id"), str) and TYPED_ID_RE.fullmatch(item["observation_id"]) and nonempty(item.get("source")) and isinstance(item.get("measured_at_utc"), str) and UTC_RE.fullmatch(item["measured_at_utc"]))
        counters = [item.get(key) for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")]
        require("METRICS_NON_AGENT_COUNTER_INVALID", all(type(value) is int and value >= 0 for value in counters) and counters[4] == counters[0] + counters[2])
    counts = aggregates.get("counts")
    count_keys = {"agents", "handoffs", "validators_executed", "validators_referenced", "validators_repeated", "retries", "replays", "gates", "reconciliations"}
    require("METRICS_COUNT_FIELDS_INVALID", isinstance(counts, dict) and set(counts) == count_keys)
    early_unavailable = aggregates.get("unavailable_reasons")
    if isinstance(early_unavailable, list):
        for item in early_unavailable:
            if isinstance(item, dict) and isinstance(item.get("field"), str) and item["field"].startswith("counts."):
                key = item["field"].removeprefix("counts.")
                require("METRICS_UNAVAILABLE_ZERO", counts.get(key) != 0)
    derived_counts = {
        "agents": len({span["owner"] for span in spans}),
        "handoffs": sum(span["kind"] == "handoff" for span in spans),
        "validators_executed": sum(span["kind"] == "validator" and span["validator_observation"]["execution_mode"] == "executed" for span in spans),
        "validators_referenced": sum(span["kind"] == "validator" and span["validator_observation"]["execution_mode"] == "referenced" for span in spans),
        "validators_repeated": sum(span["kind"] == "validator" and span["replay"] for span in spans),
        "retries": sum(span["kind"] == "task" and span["iteration"] > 0 for span in spans),
        "replays": sum(span["replay"] for span in spans),
        "gates": sum(span["kind"] == "gate" for span in spans),
        "reconciliations": sum(span["kind"] == "reconciliation" for span in spans),
    }
    require("METRICS_COUNT_MISMATCH", counts == derived_counts)
    durations = aggregates.get("durations")
    duration_keys = {"elapsed_ms", "active_ms", "critical_path_ms"}
    require("METRICS_DURATION_FIELDS_INVALID", isinstance(durations, dict) and set(durations) == duration_keys)
    children = {span["parent_span_id"] for span in spans if span["parent_span_id"] is not None}
    children_by_parent: dict[str, list[str]] = {span_id: [] for span_id in ids}
    for span in spans:
        if span["parent_span_id"] is not None:
            children_by_parent[span["parent_span_id"]].append(span["span_id"])
    observed_leaves = [span for span in spans if span["span_id"] not in children and span["monotonic_duration_ms"] is not None]
    expected_elapsed = roots[0]["monotonic_duration_ms"]
    expected_active = sum(span["monotonic_duration_ms"] for span in observed_leaves) if observed_leaves else None
    require("METRICS_ELAPSED_MISMATCH", durations.get("elapsed_ms") == expected_elapsed)
    require("METRICS_ACTIVE_MISMATCH", durations.get("active_ms") == expected_active)
    critical_ids = aggregates.get("critical_path_span_ids")
    require("METRICS_CRITICAL_PATH_IDS_INVALID", isinstance(critical_ids, list) and len(critical_ids) == len(set(critical_ids)))
    candidate_paths: list[tuple[int, tuple[str, ...]]] = []
    def collect_complete_paths(span_id: str, path: tuple[str, ...]) -> None:
        current_path = path + (span_id,)
        descendants = sorted(children_by_parent[span_id])
        if descendants:
            for child_id in descendants:
                collect_complete_paths(child_id, current_path)
            return
        path_durations = [span_map[item]["monotonic_duration_ms"] for item in current_path]
        if all(type(value) is int for value in path_durations):
            candidate_paths.append((sum(path_durations), current_path))
    collect_complete_paths(roots[0]["span_id"], ())
    if candidate_paths:
        maximum_duration = max(score for score, _ in candidate_paths)
        expected_path = min(path for score, path in candidate_paths if score == maximum_duration)
        require("METRICS_CRITICAL_PATH_MISMATCH", critical_ids == list(expected_path) and durations.get("critical_path_ms") == maximum_duration)
    else:
        require("METRICS_CRITICAL_PATH_MISMATCH", critical_ids == [] and durations.get("critical_path_ms") is None)
    unavailable = aggregates.get("unavailable_reasons")
    require("METRICS_UNAVAILABLE_REASONS_INVALID", isinstance(unavailable, list) and all(isinstance(item, dict) and set(item) == {"field", "reason"} and nonempty(item.get("field")) and nonempty(item.get("reason")) for item in unavailable))
    reason_fields = [item["field"] for item in unavailable]
    require("METRICS_UNAVAILABLE_REASON_DUPLICATE", len(reason_fields) == len(set(reason_fields)))
    null_fields = {f"counts.{key}" for key, value in counts.items() if value is None} | {f"durations.{key}" for key, value in durations.items() if value is None}
    require("METRICS_UNAVAILABLE_REASON_COVERAGE", set(reason_fields) == null_fields)
    require("METRICS_TELEMETRY_BLOCKED_FUNCTION", p.get("telemetry_changed_functional_status") is False)


def rule_metrics_resume(p: dict[str, Any]) -> None:
    require("METRICS_RESUME_IDENTITY_INVALID", p.get("span_identity_reused") is True and p.get("iteration_preserved") is True)
    require("METRICS_RESUME_DOUBLE_COUNT", p.get("usage_counted_instances") == 1 and p.get("duration_counted_instances") == 1)


def rule_liveness(p: dict[str, Any]) -> None:
    if p.get("explicit_user_cancellation") is True:
        require("LIVENESS_CANCELLATION_CONFLATED", p.get("trigger") == "explicit-user-cancellation" and p.get("silence_policy_used") is False)
        return
    require("LIVENESS_TRIGGER_INVALID", p.get("trigger") == "silence-stop")
    require("LIVENESS_PROBE_MISSING", p.get("probe_recorded") is True and p.get("outcome") in {"running", "progress", "terminal", "unsupported", "unavailable"})
    if p.get("outcome") in {"running", "progress"}:
        require("LIVENESS_ACTIVE_ABORTED", p.get("stop_performed") is False)
    if p.get("outcome") in {"unsupported", "unavailable"}:
        require("LIVENESS_REASON_MISSING", nonempty(p.get("reason")) and p.get("heartbeat_invented") is False)


def rule_materiality_gate(p: dict[str, Any]) -> None:
    valid = p.get("profile_valid") is True and p.get("materiality_valid") is True
    require("MATERIALITY_GATE_INVALID", p.get("auditor_dispatched") is valid)
    require("MATERIALITY_TELEMETRY_COUPLED", p.get("telemetry_failure_changed_gate") is False)


def rule_cost_policy(p: dict[str, Any]) -> None:
    require("COST_BUDGET_FORBIDDEN", p.get("token_budget") is None and p.get("cost_budget") is None)
    require("COST_AUTO_STOP_FORBIDDEN", p.get("automatic_cost_stop") is False and p.get("metrics_measurement_only") is True)


def validate_metrics_projection(p: dict[str, Any], prefix: str) -> None:
    ref = p.get("execution_metrics_ref")
    digest = p.get("execution_metrics_digest")
    status = p.get("execution_metrics_status")
    reason = p.get("execution_metrics_degradation_reason")
    published = nonempty(ref) and isinstance(digest, str) and SHA256_RE.fullmatch(digest)
    publication_failed = ref is None and digest is None and status == "unavailable" and nonempty(reason) and "publication failure" in reason.lower()
    require(f"{prefix}_METRICS_PUBLICATION_INVALID", bool(published) != bool(publication_failed))
    if status == "complete":
        require(f"{prefix}_METRICS_COMPLETE_REASON_INVALID", reason is None)
    else:
        require(f"{prefix}_METRICS_REASON_MISSING", nonempty(reason))


def validate_consistency_packet(p: dict[str, Any]) -> None:
    required = {"schema_version", "state", "tasks", "terminal_evidence", "validations", "result", "dashboard", "metrics"}
    require("CONSISTENCY_PACKET_SHAPE_INVALID", set(p) == required and p.get("schema_version") == 1)
    state, result, dashboard, metrics = (p[name] for name in ("state", "result", "dashboard", "metrics"))
    require("CONSISTENCY_STATE_SCHEMA_SUPERSEDED", state.get("schema_version") == 2)
    require("CONSISTENCY_RESULT_SCHEMA_SUPERSEDED", result.get("schema_version") == 2)
    require("CONSISTENCY_METRICS_SCHEMA_INVALID", metrics.get("schema_version") == 1)
    require("CONSISTENCY_STATE_DIGEST_DIVERGENCE", result.get("state_digest") == state.get("state_digest"))
    statuses = [state.get("status"), p["terminal_evidence"].get("status"), p["validations"].get("status"), result.get("status"), dashboard.get("status")]
    require("CONSISTENCY_STATUS_DIVERGENCE", len(set(statuses)) == 1)
    refs = [state.get("execution_metrics_ref"), result.get("execution_metrics_ref"), dashboard.get("execution_metrics_ref"), metrics.get("ref")]
    digests = [state.get("execution_metrics_digest"), result.get("execution_metrics_digest"), dashboard.get("execution_metrics_digest"), metrics.get("digest")]
    metric_statuses = [state.get("execution_metrics_status"), result.get("execution_metrics_status"), dashboard.get("execution_metrics_status"), metrics.get("status")]
    require("CONSISTENCY_METRICS_STATUS_INVALID", all(status in {"complete", "partial", "unavailable"} for status in metric_statuses))
    require("CONSISTENCY_METRICS_REF_DIVERGENCE", len(set(refs)) == 1)
    require("CONSISTENCY_METRICS_DIGEST_DIVERGENCE", len(set(digests)) == 1)
    require("CONSISTENCY_METRICS_STATUS_DIVERGENCE", len(set(metric_statuses)) == 1)
    reasons = [state.get("execution_metrics_degradation_reason"), result.get("execution_metrics_degradation_reason"), dashboard.get("execution_metrics_degradation_reason"), metrics.get("degradation_reason")]
    require("CONSISTENCY_METRICS_REASON_DIVERGENCE", len(set(reasons)) == 1)
    for projection in (state, result, dashboard):
        validate_metrics_projection(projection, "CONSISTENCY")
    published = nonempty(metrics.get("ref")) and isinstance(metrics.get("digest"), str) and SHA256_RE.fullmatch(metrics["digest"])
    publication_failed = metrics.get("ref") is None and metrics.get("digest") is None and metrics.get("status") == "unavailable" and nonempty(metrics.get("degradation_reason")) and "publication failure" in metrics["degradation_reason"].lower()
    require("CONSISTENCY_METRICS_PUBLICATION_INVALID", bool(published) != bool(publication_failed))
    next_actions = [state.get("next_action"), result.get("next_action"), dashboard.get("next_action")]
    require("CONSISTENCY_NEXT_ACTION_DIVERGENCE", len(set(next_actions)) == 1 and nonempty(next_actions[0]))
    task_map = {task.get("task_ref"): task.get("status") for task in p.get("tasks", [])}
    dashboard_map = {task.get("task_ref"): task.get("persisted_status") for task in dashboard.get("tasks", [])}
    require("CONSISTENCY_TASK_DIVERGENCE", task_map == dashboard_map)
    require("CONSISTENCY_VALIDATOR_DIVERGENCE", p["validations"].get("validator_digest") == result.get("validator_digest") == dashboard.get("validator_digest"))
    require("CONSISTENCY_TELEMETRY_FUNCTIONAL_COUPLING", metrics.get("telemetry_changed_functional_status") is False)


def rule_consistency(p: dict[str, Any]) -> None:
    validate_consistency_packet(p)


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
    "current-schema": rule_current_schema,
    "metrics": rule_metrics,
    "metrics-resume": rule_metrics_resume,
    "liveness": rule_liveness,
    "materiality-gate": rule_materiality_gate,
    "cost-policy": rule_cost_policy,
    "consistency": rule_consistency,
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
    parser.add_argument("--consistency-packet", metavar="PATH", help="validate one executable cross-surface consistency packet")
    args = parser.parse_args()
    if args.self_test == bool(args.consistency_packet):
        parser.error("select exactly one of --self-test or --consistency-packet PATH")
    try:
        if args.self_test:
            result = self_test()
        else:
            document = json.loads(Path(args.consistency_packet).read_text(encoding="utf-8"))
            require("CONSISTENCY_WRAPPER_INVALID", set(document) == {"consistency_packet"} and isinstance(document["consistency_packet"], dict))
            validate_consistency_packet(document["consistency_packet"])
            result = {"status": "passed", "schema_version": 1, "packet": args.consistency_packet}
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    except (ContractError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
