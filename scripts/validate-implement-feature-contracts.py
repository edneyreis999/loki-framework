#!/usr/bin/env python3
"""Validate current loki-implement-feature fixtures or one persisted real run.

The real-run mode derives every decision from files and bytes below an explicit
project root.  Caller-provided integrity booleans are not part of its closed
schemas.  The self-test exercises the five JSON corpora plus a materialized
fixture tree and adversarial on-disk mutations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import tempfile
from copy import deepcopy
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
    "dashboard-partial-unresolved",
    "dashboard-failed",
    "dashboard-needs-human-review-response-only",
    "dashboard-needs-human-review-failed-response-only",
    "dashboard-needs-human-review-invalid-locator",
    "dashboard-needs-human-review-duplicate-locator",
    "dashboard-needs-human-review-absent-locator",
    "dashboard-needs-human-review-absent-decision",
    "dashboard-needs-human-review-empty-decision",
    "dashboard-needs-human-review-uncorrelated-evidence",
    "dashboard-needs-human-review-invalid-persisted-status",
    "dashboard-needs-human-review-persisted-status-forbidden",
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
    "reject-command-identity-v1",
    "reject-execution-input-v1",
    "reject-state-v2",
    "reject-result-v2",
    "reject-consistency-v1",
    "audit-frequency-default-phase",
    "audit-frequency-explicit-task",
    "audit-frequency-explicit-plan",
    "audit-frequency-alias-rejected",
    "audit-checkpoint-current",
    "audit-checkpoint-writer-is-auditor",
    "audit-correction-incremental-replay",
    "audit-correction-full-replay",
    "planos-root-is-not-plan-directory",
}

TASK_STATUSES = {"pending", "passed", "unresolved", "skipped-dependency", "cancelled"}
PERSISTED_EXECUTION_STATUSES = {"running", "completed", "completed-with-limitations", "pending-human-validation", "partial", "failed", "cancelled"}
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
AUDIT_FREQUENCIES = {"task", "phase", "plan"}
RUN_ID_V2_RE = re.compile(r"^loki-run-v2:[0-9a-f]{64}$")
EXECUTION_ID_V2_RE = re.compile(r"^loki-execution-v2:[0-9a-f]{64}$")
AUDIT_ID_V1_RE = re.compile(r"^execution-audit-v1:[0-9a-f]{64}$")
AUTHORITATIVE_PATH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
AUTHORITATIVE_FRAGMENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@-]*$")


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


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def canonical_digest(value: Any) -> str:
    return f"sha256:{hashlib.sha256(canonical_bytes(value)).hexdigest()}"


def bytes_digest(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def closed_mapping(code: str, value: Any, keys: set[str]) -> dict[str, Any]:
    require(code, isinstance(value, dict) and set(value) == keys)
    return value


def validate_audit_configuration(value: Any) -> dict[str, Any]:
    config = closed_mapping(
        "AUDIT_CONFIGURATION_SHAPE_INVALID",
        value,
        {"schema_version", "frequency", "source", "policy_digest"},
    )
    require(
        "AUDIT_CONFIGURATION_SCHEMA_INVALID",
        type(config["schema_version"]) is int and config["schema_version"] == 1,
    )
    require("AUDIT_FREQUENCY_TYPE_INVALID", isinstance(config["frequency"], str))
    require("AUDIT_FREQUENCY_INVALID", config["frequency"] in AUDIT_FREQUENCIES)
    require(
        "AUDIT_FREQUENCY_SOURCE_TYPE_INVALID",
        isinstance(config["source"], str),
    )
    require("AUDIT_FREQUENCY_SOURCE_INVALID", config["source"] in {"default", "explicit"})
    require(
        "AUDIT_FREQUENCY_DEFAULT_INVALID",
        config["source"] != "default" or config["frequency"] == "phase",
    )
    expected = canonical_digest({key: config[key] for key in ("schema_version", "frequency", "source")})
    require("AUDIT_POLICY_DIGEST_INVALID", config["policy_digest"] == expected)
    return config


def validate_command_identity(value: Any) -> dict[str, Any]:
    identity = closed_mapping(
        "COMMAND_IDENTITY_SHAPE_INVALID",
        value,
        {
            "schema_version",
            "command",
            "demand_digest",
            "analysis_digest",
            "plan_directory",
            "retry_limit",
            "audit_configuration",
        },
    )
    require("COMMAND_IDENTITY_SCHEMA_SUPERSEDED", identity["schema_version"] == 2)
    require("COMMAND_IDENTITY_COMMAND_INVALID", identity["command"] == "loki-implement-feature")
    require("COMMAND_IDENTITY_DEMAND_DIGEST_INVALID", SHA256_RE.fullmatch(identity["demand_digest"]) is not None)
    require("COMMAND_IDENTITY_ANALYSIS_DIGEST_INVALID", SHA256_RE.fullmatch(identity["analysis_digest"]) is not None)
    require("COMMAND_IDENTITY_PLAN_INVALID", safe_plan_path(identity["plan_directory"]))
    require("COMMAND_IDENTITY_RETRY_INVALID", type(identity["retry_limit"]) is int and identity["retry_limit"] >= 0)
    validate_audit_configuration(identity["audit_configuration"])
    return identity


def derive_typed_id(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(canonical_bytes(value)).hexdigest()}"


def validate_execution_input(value: Any) -> dict[str, Any]:
    execution_input = closed_mapping(
        "EXECUTION_INPUT_SHAPE_INVALID",
        value,
        {
            "schema_version",
            "command_identity",
            "run_id",
            "execution_id",
            "demand_ref",
            "analysis_ref",
            "state_ref",
            "result_ref",
            "dashboard_ref",
            "consistency_packet_ref",
        },
    )
    require("EXECUTION_INPUT_SCHEMA_SUPERSEDED", execution_input["schema_version"] == 2)
    identity = validate_command_identity(execution_input["command_identity"])
    require("RUN_IDENTITY_INVALID", execution_input["run_id"] == derive_typed_id("loki-run-v2", identity))
    execution_identity = {"run_id": execution_input["run_id"], "command_identity": identity}
    require(
        "EXECUTION_IDENTITY_INVALID",
        execution_input["execution_id"] == derive_typed_id("loki-execution-v2", execution_identity),
    )
    require("RUN_ID_V2_INVALID", RUN_ID_V2_RE.fullmatch(execution_input["run_id"]) is not None)
    require("EXECUTION_ID_V2_INVALID", EXECUTION_ID_V2_RE.fullmatch(execution_input["execution_id"]) is not None)
    for key in ("demand_ref", "analysis_ref", "state_ref", "result_ref", "dashboard_ref", "consistency_packet_ref"):
        require("EXECUTION_INPUT_REF_INVALID", safe_relative_path(execution_input[key]))
    return execution_input


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
    return len(path.parts) > 1 and path.parts[:1] == ("planos",)


def safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        return False
    return all(segment not in {"", ".", ".."} for segment in value.split("/"))


def safe_authoritative_locator(value: Any) -> bool:
    if not isinstance(value, str) or value.count("#") != 1:
        return False
    path, fragment = value.split("#", 1)
    return (
        safe_relative_path(path)
        and PurePosixPath(path).suffix != ""
        and AUTHORITATIVE_PATH_RE.fullmatch(path) is not None
        and AUTHORITATIVE_FRAGMENT_RE.fullmatch(fragment) is not None
    )


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
    require("RESUME_SELF_ATTESTATION_FORBIDDEN", not ({"schema_valid", "state_digest_valid", "identity_matches", "canonical_contained"} & set(p)))
    require("STATE_SCHEMA_SUPERSEDED", p.get("state_schema_version") == 3)
    require("RESUME_SOURCE_INVALID", p.get("source") == "persisted-files")
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


def validate_response_status_projection(p: dict[str, Any]) -> None:
    status = p.get("status")
    require("DASHBOARD_STATUS_INVALID", status in PERSISTED_EXECUTION_STATUSES)
    response_status = p.get("response_status", status)
    require("RESPONSE_STATUS_INVALID", response_status in PERSISTED_EXECUTION_STATUSES | {"needs-human-review"})
    if response_status == "needs-human-review":
        require("RESPONSE_NORMATIVE_CONFLICT_STATUS_INVALID", status in {"partial", "failed"})
        conflict = p.get("normative_conflict")
        require("RESPONSE_NORMATIVE_CONFLICT_SHAPE_INVALID", isinstance(conflict, dict))
        require("RESPONSE_NORMATIVE_CONFLICT_SCHEMA_INVALID", type(conflict.get("schema_version")) is int and conflict["schema_version"] == 1)
        sources = conflict.get("authoritative_source_locators")
        require("RESPONSE_NORMATIVE_CONFLICT_LOCATOR_COUNT_INVALID", isinstance(sources, list) and len(sources) == 2)
        require("RESPONSE_NORMATIVE_CONFLICT_LOCATOR_ROW_INVALID", all(isinstance(row, dict) and set(row) == {"type", "locator"} and row.get("type") == "authoritative-source" for row in sources))
        locators = [row["locator"] for row in sources]
        require("RESPONSE_NORMATIVE_CONFLICT_LOCATOR_INVALID", all(safe_authoritative_locator(locator) for locator in locators))
        require("RESPONSE_NORMATIVE_CONFLICT_LOCATOR_DUPLICATE", len(set(locators)) == 2)
        require("RESPONSE_NORMATIVE_CONFLICT_DECISION_MISSING", nonempty(conflict.get("minimum_priority_decision")))
        require("RESPONSE_NORMATIVE_CONFLICT_SHAPE_INVALID", set(conflict) == {"schema_version", "authoritative_source_locators", "minimum_priority_decision"})
        evidence = p.get("evidence")
        require("RESPONSE_NORMATIVE_CONFLICT_EVIDENCE_UNCORRELATED", isinstance(evidence, list) and all(locator in evidence for locator in locators))
    else:
        require("RESPONSE_STATUS_DIVERGENCE", response_status == status)
        require("RESPONSE_NORMATIVE_CONFLICT_UNEXPECTED", "normative_conflict" not in p)


def rule_response_normative_conflict(p: dict[str, Any]) -> None:
    validate_response_status_projection(p)


def rule_dashboard(p: dict[str, Any]) -> None:
    status = p.get("status")
    validate_response_status_projection(p)
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
    require("DASHBOARD_UNIT_STATUS_INVALID", all(row.get("status") in {"pending", "completed", "unresolved", "skipped-dependency", "cancelled"} for row in task_rows))
    require("DASHBOARD_SYNTHETIC_SCOPE_FORBIDDEN", all(row.get("kind") == "task" for row in p.get("units", [])))


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
    expected_versions = {
        "command-identity": 2,
        "execution-input": 2,
        "state": 3,
        "result": 3,
        "consistency": 2,
    }
    require("CURRENT_SCHEMA_ARTIFACT_INVALID", artifact in expected_versions)
    expected = expected_versions[artifact]
    require(f"{artifact.upper()}_SCHEMA_SUPERSEDED", p.get("schema_version") == expected)


def rule_audit_configuration(p: dict[str, Any]) -> None:
    validate_audit_configuration(p)


AUDIT_CHECKPOINT_KEYS = {
    "schema_version",
    "audit_id",
    "run_id",
    "execution_id",
    "policy_digest",
    "frequency",
    "boundary_type",
    "boundary_ref",
    "iteration",
    "predecessor_audit_ref",
    "replay",
    "replay_cause",
    "membership_refs",
    "coverage_digest",
    "covered_handoff_refs",
    "covered_target_digests",
    "primary_validation_refs",
    "final_validator_refs",
    "auditor_identity",
    "writer_identities",
    "auditor_run_refs",
    "finding_refs",
    "correction_refs",
    "evidence_refs",
    "status",
    "next_action",
}


def audit_identity_material(checkpoint: dict[str, Any]) -> dict[str, Any]:
    return {
        key: checkpoint[key]
        for key in (
            "execution_id",
            "policy_digest",
            "boundary_type",
            "boundary_ref",
            "iteration",
            "coverage_digest",
        )
    }


def validate_audit_checkpoint(checkpoint: Any) -> dict[str, Any]:
    checkpoint = closed_mapping("AUDIT_CHECKPOINT_SHAPE_INVALID", checkpoint, AUDIT_CHECKPOINT_KEYS)
    require(
        "AUDIT_CHECKPOINT_SCHEMA_INVALID",
        type(checkpoint["schema_version"]) is int
        and checkpoint["schema_version"] == 1,
    )
    require(
        "AUDIT_CHECKPOINT_RUN_ID_INVALID",
        isinstance(checkpoint["run_id"], str)
        and RUN_ID_V2_RE.fullmatch(checkpoint["run_id"]) is not None,
    )
    require(
        "AUDIT_CHECKPOINT_EXECUTION_ID_INVALID",
        isinstance(checkpoint["execution_id"], str)
        and EXECUTION_ID_V2_RE.fullmatch(checkpoint["execution_id"]) is not None,
    )
    require(
        "AUDIT_CHECKPOINT_POLICY_DIGEST_INVALID",
        isinstance(checkpoint["policy_digest"], str)
        and SHA256_RE.fullmatch(checkpoint["policy_digest"]) is not None,
    )
    require(
        "AUDIT_CHECKPOINT_FREQUENCY_INVALID",
        isinstance(checkpoint["frequency"], str)
        and checkpoint["frequency"] in AUDIT_FREQUENCIES,
    )
    require(
        "AUDIT_CHECKPOINT_BOUNDARY_INVALID",
        isinstance(checkpoint["boundary_type"], str)
        and checkpoint["boundary_type"] in AUDIT_FREQUENCIES
        and nonempty(checkpoint["boundary_ref"]),
    )
    require("AUDIT_CHECKPOINT_ITERATION_INVALID", type(checkpoint["iteration"]) is int and checkpoint["iteration"] >= 0)
    require("AUDIT_CHECKPOINT_REPLAY_INVALID", type(checkpoint["replay"]) is bool)
    if checkpoint["replay"]:
        require("AUDIT_CHECKPOINT_PREDECESSOR_MISSING", nonempty(checkpoint["predecessor_audit_ref"]) and nonempty(checkpoint["replay_cause"]))
    else:
        require("AUDIT_CHECKPOINT_REPLAY_FIELDS_UNEXPECTED", checkpoint["predecessor_audit_ref"] is None and checkpoint["replay_cause"] is None)
    for key in (
        "membership_refs",
        "covered_handoff_refs",
        "covered_target_digests",
        "primary_validation_refs",
        "final_validator_refs",
        "writer_identities",
        "auditor_run_refs",
        "finding_refs",
        "correction_refs",
        "evidence_refs",
    ):
        require(
            "AUDIT_CHECKPOINT_LIST_INVALID",
            isinstance(checkpoint[key], list)
            and all(nonempty(item) for item in checkpoint[key])
            and len(checkpoint[key]) == len(set(checkpoint[key])),
        )
    require("AUDIT_CHECKPOINT_MEMBERSHIP_MISSING", bool(checkpoint["membership_refs"]))
    require(
        "AUDIT_CHECKPOINT_COVERAGE_INVALID",
        isinstance(checkpoint["coverage_digest"], str)
        and SHA256_RE.fullmatch(checkpoint["coverage_digest"]) is not None,
    )
    require("AUDIT_CHECKPOINT_AUDITOR_INVALID", nonempty(checkpoint["auditor_identity"]))
    require("AUDIT_CHECKPOINT_WRITER_MISSING", bool(checkpoint["writer_identities"]))
    require("AUDIT_CHECKPOINT_NOT_INDEPENDENT", checkpoint["auditor_identity"] not in checkpoint["writer_identities"])
    require(
        "AUDIT_CHECKPOINT_STATUS_INVALID",
        isinstance(checkpoint["status"], str)
        and checkpoint["status"]
        in {
            "approved",
            "finding",
            "inconclusive",
            "failed",
            "unavailable",
            "not-applicable",
            "cancelled",
        },
    )
    require("AUDIT_CHECKPOINT_NEXT_ACTION_MISSING", nonempty(checkpoint["next_action"]))
    expected_id = derive_typed_id("execution-audit-v1", audit_identity_material(checkpoint))
    require(
        "AUDIT_CHECKPOINT_ID_INVALID",
        isinstance(checkpoint["audit_id"], str)
        and checkpoint["audit_id"] == expected_id
        and AUDIT_ID_V1_RE.fullmatch(checkpoint["audit_id"]) is not None,
    )
    return checkpoint


def rule_audit_checkpoint(p: dict[str, Any]) -> None:
    validate_audit_checkpoint(p)


def rule_audit_replay(p: dict[str, Any]) -> None:
    require("AUDIT_CORRECTION_REPLAY_REQUIRED", not p.get("correction_refs") or p.get("replay") is True)
    if p.get("replay"):
        require("AUDIT_REPLAY_PREDECESSOR_MISSING", nonempty(p.get("predecessor_audit_ref")) and nonempty(p.get("replay_cause")))
        require("AUDIT_INCREMENTAL_REPLAY_FORBIDDEN", p.get("membership_refs") == p.get("required_membership_refs") and p.get("coverage_digest") == p.get("required_coverage_digest"))
        require("AUDIT_REPLAY_EVIDENCE_DUPLICATED", len(p.get("evidence_refs", [])) == len(set(p.get("evidence_refs", []))))


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
    required = {"schema_version", "audit_configuration", "state", "tasks", "terminal_evidence", "validations", "audits", "result", "dashboard", "metrics"}
    require("CONSISTENCY_PACKET_SHAPE_INVALID", set(p) == required and p.get("schema_version") == 2)
    audit_configuration = validate_audit_configuration(p["audit_configuration"])
    state, result, dashboard, metrics = (p[name] for name in ("state", "result", "dashboard", "metrics"))
    require("CONSISTENCY_STATE_SCHEMA_SUPERSEDED", state.get("schema_version") == 3)
    require("CONSISTENCY_RESULT_SCHEMA_SUPERSEDED", result.get("schema_version") == 3)
    require("CONSISTENCY_METRICS_SCHEMA_INVALID", metrics.get("schema_version") == 1)
    require("CONSISTENCY_AUDIT_CONFIGURATION_DIVERGENCE", state.get("audit_configuration") == result.get("audit_configuration") == dashboard.get("audit_configuration") == audit_configuration)
    require("CONSISTENCY_AUDITS_INVALID", isinstance(p["audits"], dict) and p["audits"].get("frequency") == audit_configuration["frequency"] and isinstance(p["audits"].get("checkpoint_refs"), list))
    require("CONSISTENCY_AUDIT_REFS_DIVERGENCE", state.get("audit_checkpoint_refs") == result.get("audit_checkpoint_refs") == dashboard.get("audit_checkpoint_refs") == p["audits"].get("checkpoint_refs"))
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


class RealRunReader:
    """Read run evidence from one real project root without trusting caller flags."""

    def __init__(self, project_root: Path) -> None:
        require("PROJECT_ROOT_INVALID", project_root.exists() and project_root.is_dir() and not project_root.is_symlink())
        self.root = project_root.resolve(strict=True)
        self._bytes: dict[str, bytes] = {}

    def normalize(self, value: str | Path) -> str:
        path = Path(value)
        if path.is_absolute():
            try:
                relative = path.relative_to(self.root)
            except ValueError as exc:
                raise ContractError("REF_OUTSIDE_PROJECT_ROOT") from exc
            value = relative.as_posix()
        else:
            value = path.as_posix()
        require("REF_PATH_UNSAFE", safe_relative_path(value))
        return value

    def read_bytes(self, value: str | Path) -> bytes:
        ref = self.normalize(value)
        if ref in self._bytes:
            return self._bytes[ref]
        current = self.root
        for part in PurePosixPath(ref).parts:
            current = current / part
            require("REF_SYMLINK_FORBIDDEN", not current.is_symlink())
        try:
            resolved = current.resolve(strict=True)
        except OSError as exc:
            raise ContractError(f"REF_MISSING:{ref}") from exc
        require("REF_OUTSIDE_PROJECT_ROOT", resolved.is_relative_to(self.root))
        require("REF_NOT_REGULAR_FILE", resolved.is_file())
        data = resolved.read_bytes()
        require("REF_EMPTY", bool(data))
        self._bytes[ref] = data
        return data

    def read_json(self, value: str | Path) -> dict[str, Any]:
        ref = self.normalize(value)
        try:
            document = json.loads(self.read_bytes(ref).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ContractError(f"JSON_REF_INVALID:{ref}") from exc
        require("JSON_ROOT_INVALID", isinstance(document, dict))
        return document

    def read_markdown_json(self, value: str | Path) -> dict[str, Any]:
        ref = self.normalize(value)
        try:
            text = self.read_bytes(ref).decode("utf-8")
        except UnicodeError as exc:
            raise ContractError(f"MARKDOWN_UTF8_INVALID:{ref}") from exc
        blocks = re.findall(r"```json\s*\n(.*?)\n```", text, flags=re.DOTALL)
        require("MARKDOWN_CONTRACT_BLOCK_INVALID", len(blocks) == 1)
        try:
            document = json.loads(blocks[0])
        except json.JSONDecodeError as exc:
            raise ContractError(f"MARKDOWN_CONTRACT_JSON_INVALID:{ref}") from exc
        require("MARKDOWN_CONTRACT_ROOT_INVALID", isinstance(document, dict))
        return document


STATE_V3_KEYS = {
    "schema_version",
    "run_id",
    "execution_id",
    "command_identity_digest",
    "execution_input_digest",
    "audit_configuration",
    "status",
    "task_refs",
    "audit_checkpoint_refs",
    "result_ref",
    "dashboard_ref",
    "consistency_packet_ref",
    "terminal_evidence_refs",
    "execution_metrics_ref",
    "execution_metrics_digest",
    "execution_metrics_status",
    "execution_metrics_degradation_reason",
    "next_action",
    "state_digest",
}
TASK_CONTRACT_KEYS = {
    "schema_version",
    "task_id",
    "phase",
    "status",
    "dependencies",
    "target_files",
    "writer_identity",
    "handoff_refs",
    "gate_refs",
    "audit_checkpoint_refs",
    "task_validation",
}
TASK_VALIDATION_KEYS = {"schema_version", "acceptance_criteria", "primary_route", "evidence_refs", "status"}
VALIDATOR_RECORD_KEYS = {"schema_version", "validator_id", "identity", "task_ref", "acceptance_criterion_refs", "evidence_refs", "result"}
HANDOFF_RECORD_KEYS = {"schema_version", "handoff_id", "task_ref", "writer_identity", "target_digests", "evidence_refs"}
GATE_RECORD_KEYS = {"schema_version", "gate_id", "task_ref", "status", "evidence_refs"}
RESULT_V3_KEYS = {
    "schema_version",
    "run_id",
    "execution_id",
    "status",
    "state_digest",
    "audit_configuration",
    "audit_checkpoint_refs",
    "task_results",
    "final_validator_refs",
    "terminal_evidence_refs",
    "execution_metrics_ref",
    "execution_metrics_digest",
    "execution_metrics_status",
    "execution_metrics_degradation_reason",
    "next_action",
    "result_digest",
}
DASHBOARD_V3_KEYS = {
    "schema_version",
    "run_id",
    "execution_id",
    "status",
    "audit_configuration",
    "audit_checkpoint_refs",
    "tasks",
    "final_validator_refs",
    "terminal_evidence_refs",
    "execution_metrics_ref",
    "execution_metrics_digest",
    "execution_metrics_status",
    "execution_metrics_degradation_reason",
    "next_action",
    "dashboard_digest",
}
TERMINAL_EVIDENCE_KEYS = {"schema_version", "run_id", "execution_id", "status", "task_statuses", "acceptance_criterion_refs", "validator_refs", "gate_refs", "audit_checkpoint_refs", "evidence_refs"}
CONSISTENCY_V2_KEYS = {
    "schema_version",
    "run_id",
    "execution_id",
    "status",
    "audit_configuration",
    "state_digest",
    "tasks_md_digest",
    "result_ref",
    "result_digest",
    "dashboard_ref",
    "dashboard_digest",
    "metrics_ref",
    "metrics_digest",
    "audit_checkpoint_refs",
    "audit_checkpoint_digests",
    "terminal_evidence_refs",
    "terminal_evidence_digests",
    "validator_digest",
}


def digest_without(record: dict[str, Any], key: str) -> str:
    return canonical_digest({name: value for name, value in record.items() if name != key})


def register_locator(index: dict[str, tuple[str, str]], ref: str, kind: str, identity: str) -> None:
    prior = index.get(ref)
    require("LOCATOR_IDENTITY_CONFLICT", prior is None or prior == (kind, identity))
    index[ref] = (kind, identity)


def validate_record_evidence(reader: RealRunReader, refs: Any) -> list[str]:
    require("EVIDENCE_REFS_INVALID", isinstance(refs, list) and len(refs) == len(set(refs)) and all(safe_relative_path(item) for item in refs))
    for ref in refs:
        reader.read_bytes(ref)
    return refs


def validate_real_run(project_root: Path, tasks_md: str | Path, invocation_input: str | Path) -> dict[str, Any]:
    reader = RealRunReader(project_root)
    tasks_ref = reader.normalize(tasks_md)
    invocation_ref = reader.normalize(invocation_input)
    require("TASKS_MD_PATH_INVALID", tasks_ref.endswith("/tasks.md") and safe_plan_path(str(PurePosixPath(tasks_ref).parent)))
    invocation = validate_execution_input(reader.read_json(invocation_ref))
    identity = invocation["command_identity"]
    require("PLAN_DIRECTORY_MISMATCH", identity["plan_directory"] == str(PurePosixPath(tasks_ref).parent))
    require("STATE_REF_MISMATCH", invocation["state_ref"] == tasks_ref)
    demand_bytes = reader.read_bytes(invocation["demand_ref"])
    analysis_bytes = reader.read_bytes(invocation["analysis_ref"])
    require("DEMAND_DIGEST_MISMATCH", identity["demand_digest"] == bytes_digest(demand_bytes))
    require("ANALYSIS_DIGEST_MISMATCH", identity["analysis_digest"] == bytes_digest(analysis_bytes))
    require("ANALYSIS_NOT_MARKDOWN", invocation["analysis_ref"].endswith(".md"))

    tasks_document = reader.read_markdown_json(tasks_ref)
    require("TASKS_MD_SHAPE_INVALID", set(tasks_document) == {"loki_run_plan", "loki_run_state"})
    plan = closed_mapping("RUN_PLAN_SHAPE_INVALID", tasks_document["loki_run_plan"], {"schema_version", "task_refs", "final_validator_refs"})
    require("RUN_PLAN_SCHEMA_INVALID", plan["schema_version"] == 1)
    task_refs = plan["task_refs"]
    require(
        "RUN_PLAN_TASK_REFS_INVALID",
        isinstance(task_refs, list)
        and bool(task_refs)
        and len(task_refs) == len(set(task_refs))
        and all(
            safe_plan_path(ref)
            and ref.endswith(".md")
            and str(PurePosixPath(ref).parent) == identity["plan_directory"]
            for ref in task_refs
        ),
    )
    final_validator_refs = plan["final_validator_refs"]
    require("RUN_PLAN_FINAL_VALIDATORS_INVALID", isinstance(final_validator_refs, list) and bool(final_validator_refs) and len(final_validator_refs) == len(set(final_validator_refs)))

    state = closed_mapping("STATE_V3_SHAPE_INVALID", tasks_document["loki_run_state"], STATE_V3_KEYS)
    require("STATE_SCHEMA_SUPERSEDED", state["schema_version"] == 3)
    require("STATE_RUN_ID_MISMATCH", state["run_id"] == invocation["run_id"])
    require("STATE_EXECUTION_ID_MISMATCH", state["execution_id"] == invocation["execution_id"])
    require("STATE_COMMAND_IDENTITY_DIGEST_MISMATCH", state["command_identity_digest"] == canonical_digest(identity))
    require("STATE_EXECUTION_INPUT_DIGEST_MISMATCH", state["execution_input_digest"] == bytes_digest(reader.read_bytes(invocation_ref)))
    state_audit_configuration = validate_audit_configuration(state["audit_configuration"])
    require(
        "STATE_AUDIT_CONFIGURATION_MISMATCH",
        state_audit_configuration == identity["audit_configuration"],
    )
    require("STATE_TASK_REFS_MISMATCH", state["task_refs"] == task_refs)
    require("STATE_RESULT_REF_MISMATCH", state["result_ref"] == invocation["result_ref"])
    require("STATE_DASHBOARD_REF_MISMATCH", state["dashboard_ref"] == invocation["dashboard_ref"])
    require("STATE_CONSISTENCY_REF_MISMATCH", state["consistency_packet_ref"] == invocation["consistency_packet_ref"])
    require("STATE_DIGEST_MISMATCH", state["state_digest"] == digest_without(state, "state_digest"))
    require("STATE_STATUS_INVALID", state["status"] in {"running", "completed", "completed-with-limitations", "pending-human-validation", "partial", "failed", "cancelled"})
    require("STATE_NEXT_ACTION_MISSING", nonempty(state["next_action"]))

    task_contracts: dict[str, dict[str, Any]] = {}
    task_ids: dict[str, str] = {}
    target_owner: dict[str, str] = {}
    locator_index: dict[str, tuple[str, str]] = {}
    validator_records: dict[str, dict[str, Any]] = {}
    handoff_records: dict[str, dict[str, Any]] = {}
    gate_records: dict[str, dict[str, Any]] = {}
    all_primary_validator_refs: list[str] = []
    all_handoff_refs: list[str] = []
    all_gate_refs: list[str] = []

    for task_ref in task_refs:
        task_document = reader.read_markdown_json(task_ref)
        require("TASK_DOCUMENT_SHAPE_INVALID", set(task_document) == {"task_contract"})
        task = closed_mapping("TASK_CONTRACT_SHAPE_INVALID", task_document["task_contract"], TASK_CONTRACT_KEYS)
        require("TASK_CONTRACT_SCHEMA_INVALID", task["schema_version"] == 1)
        require("TASK_ID_INVALID", nonempty(task["task_id"]) and task["task_id"] not in task_ids)
        task_ids[task["task_id"]] = task_ref
        require("TASK_PHASE_INVALID", nonempty(task["phase"]))
        require("TASK_STATUS_INVALID", task["status"] in TASK_STATUSES)
        require("TASK_DEPENDENCIES_INVALID", isinstance(task["dependencies"], list) and len(task["dependencies"]) == len(set(task["dependencies"])) and all(nonempty(item) for item in task["dependencies"]))
        require("TASK_TARGETS_INVALID", isinstance(task["target_files"], list) and bool(task["target_files"]) and len(task["target_files"]) == len(set(task["target_files"])) and all(safe_relative_path(item) for item in task["target_files"]))
        require("TASK_WRITER_IDENTITY_INVALID", nonempty(task["writer_identity"]))
        for target in task["target_files"]:
            require("TARGET_OWNER_CONFLICT", target not in target_owner)
            target_owner[target] = task_ref
        validation = closed_mapping("TASK_VALIDATION_SHAPE_INVALID", task["task_validation"], TASK_VALIDATION_KEYS)
        require("TASK_VALIDATION_SCHEMA_INVALID", validation["schema_version"] == 1)
        criteria = validation["acceptance_criteria"]
        require("TASK_AC_INVALID", isinstance(criteria, list) and bool(criteria) and all(isinstance(ac, dict) and set(ac) == {"id", "statement", "required"} and nonempty(ac["id"]) and nonempty(ac["statement"]) and type(ac["required"]) is bool for ac in criteria))
        ac_ids = [ac["id"] for ac in criteria]
        require("TASK_AC_DUPLICATE", len(ac_ids) == len(set(ac_ids)))
        route = closed_mapping("TASK_PRIMARY_ROUTE_INVALID", validation["primary_route"], {"type", "validator_ref"})
        require("TASK_PRIMARY_ROUTE_TYPE_INVALID", route["type"] in {"deterministic", "write_test_agent"})
        validator_ref = route["validator_ref"]
        validator = closed_mapping("VALIDATOR_RECORD_SHAPE_INVALID", reader.read_json(validator_ref), VALIDATOR_RECORD_KEYS)
        require("VALIDATOR_RECORD_SCHEMA_INVALID", validator["schema_version"] == 1)
        require("VALIDATOR_RECORD_TASK_MISMATCH", validator["task_ref"] == task_ref)
        require("VALIDATOR_RECORD_AC_MISMATCH", set(validator["acceptance_criterion_refs"]) == set(ac_ids))
        require("VALIDATOR_RECORD_RESULT_INVALID", validator["result"] in {"passed", "failed", "unavailable"})
        require("VALIDATOR_RECORD_IDENTITY_INVALID", nonempty(validator["validator_id"]) and nonempty(validator["identity"]))
        validate_record_evidence(reader, validator["evidence_refs"])
        register_locator(locator_index, validator_ref, "validator", validator["validator_id"])
        validator_records[validator_ref] = validator
        all_primary_validator_refs.append(validator_ref)
        validate_record_evidence(reader, validation["evidence_refs"])
        require("TASK_VALIDATION_STATUS_INVALID", validation["status"] in TASK_STATUSES)

        require("TASK_HANDOFF_REFS_INVALID", isinstance(task["handoff_refs"], list) and bool(task["handoff_refs"]) and len(task["handoff_refs"]) == len(set(task["handoff_refs"])))
        handoff_targets: set[str] = set()
        for handoff_ref in task["handoff_refs"]:
            handoff = closed_mapping("HANDOFF_RECORD_SHAPE_INVALID", reader.read_json(handoff_ref), HANDOFF_RECORD_KEYS)
            require("HANDOFF_RECORD_SCHEMA_INVALID", handoff["schema_version"] == 1)
            require("HANDOFF_TASK_MISMATCH", handoff["task_ref"] == task_ref)
            require("HANDOFF_WRITER_MISMATCH", handoff["writer_identity"] == task["writer_identity"])
            require("HANDOFF_ID_INVALID", nonempty(handoff["handoff_id"]))
            target_rows = handoff["target_digests"]
            require("HANDOFF_TARGET_DIGESTS_INVALID", isinstance(target_rows, list) and bool(target_rows) and all(isinstance(row, dict) and set(row) == {"path", "digest"} for row in target_rows))
            for row in target_rows:
                require("HANDOFF_TARGET_DUPLICATE", row["path"] not in handoff_targets)
                handoff_targets.add(row["path"])
                require("HANDOFF_TARGET_DIGEST_MISMATCH", row["digest"] == bytes_digest(reader.read_bytes(row["path"])))
            validate_record_evidence(reader, handoff["evidence_refs"])
            register_locator(locator_index, handoff_ref, "handoff", handoff["handoff_id"])
            handoff_records[handoff_ref] = handoff
            all_handoff_refs.append(handoff_ref)
        require("HANDOFF_TARGET_COVERAGE_INVALID", handoff_targets == set(task["target_files"]))

        require("TASK_GATE_REFS_INVALID", isinstance(task["gate_refs"], list) and len(task["gate_refs"]) == len(set(task["gate_refs"])))
        for gate_ref in task["gate_refs"]:
            gate = closed_mapping("GATE_RECORD_SHAPE_INVALID", reader.read_json(gate_ref), GATE_RECORD_KEYS)
            require("GATE_RECORD_SCHEMA_INVALID", gate["schema_version"] == 1)
            require("GATE_TASK_MISMATCH", gate["task_ref"] == task_ref)
            require("GATE_ID_INVALID", nonempty(gate["gate_id"]))
            require("GATE_STATUS_INVALID", gate["status"] in {"passed", "failed", "pending"})
            validate_record_evidence(reader, gate["evidence_refs"])
            register_locator(locator_index, gate_ref, "gate", gate["gate_id"])
            gate_records[gate_ref] = gate
            all_gate_refs.append(gate_ref)
        task_contracts[task_ref] = task

    require("TASK_DEPENDENCY_MISSING", all(dependency in task_ids for task in task_contracts.values() for dependency in task["dependencies"]))
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(task_id: str) -> None:
        require("TASK_DAG_CYCLE", task_id not in visiting)
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in task_contracts[task_ids[task_id]]["dependencies"]:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)
    for task_id in task_ids:
        visit(task_id)

    final_records: dict[str, dict[str, Any]] = {}
    for validator_ref in final_validator_refs:
        validator = closed_mapping("FINAL_VALIDATOR_SHAPE_INVALID", reader.read_json(validator_ref), VALIDATOR_RECORD_KEYS)
        require("FINAL_VALIDATOR_SCHEMA_INVALID", validator["schema_version"] == 1)
        require("FINAL_VALIDATOR_TASK_REF_INVALID", validator["task_ref"] is None)
        require("FINAL_VALIDATOR_IDENTITY_INVALID", nonempty(validator["validator_id"]) and nonempty(validator["identity"]))
        require("FINAL_VALIDATOR_RESULT_INVALID", validator["result"] in {"passed", "failed", "unavailable"})
        validate_record_evidence(reader, validator["evidence_refs"])
        register_locator(locator_index, validator_ref, "validator", validator["validator_id"])
        final_records[validator_ref] = validator

    frequency = identity["audit_configuration"]["frequency"]
    if frequency == "task":
        boundaries = [("task", ref, [ref]) for ref in task_refs]
    elif frequency == "phase":
        phase_names = list(dict.fromkeys(task_contracts[ref]["phase"] for ref in task_refs))
        boundaries = [("phase", f"phase:{phase}", [ref for ref in task_refs if task_contracts[ref]["phase"] == phase]) for phase in phase_names]
    else:
        boundaries = [("plan", identity["plan_directory"], list(task_refs))]
    checkpoint_refs = state["audit_checkpoint_refs"]
    require("STATE_AUDIT_REFS_INVALID", isinstance(checkpoint_refs, list) and len(checkpoint_refs) == len(set(checkpoint_refs)))
    task_checkpoint_union = list(dict.fromkeys(ref for task in task_contracts.values() for ref in task["audit_checkpoint_refs"]))
    require("TASK_AUDIT_REFS_DIVERGENCE", set(task_checkpoint_union) == set(checkpoint_refs))
    require("AUDIT_BOUNDARY_COUNT_MISMATCH", len(checkpoint_refs) == len(boundaries))
    checkpoint_records: dict[str, dict[str, Any]] = {}
    primary_identities = {record["identity"] for record in validator_records.values()}
    for checkpoint_ref, (boundary_type, boundary_ref, membership) in zip(checkpoint_refs, boundaries):
        checkpoint = validate_audit_checkpoint(reader.read_json(checkpoint_ref))
        require("AUDIT_RUN_ID_MISMATCH", checkpoint["run_id"] == invocation["run_id"])
        require("AUDIT_EXECUTION_ID_MISMATCH", checkpoint["execution_id"] == invocation["execution_id"])
        require("AUDIT_POLICY_MISMATCH", checkpoint["policy_digest"] == identity["audit_configuration"]["policy_digest"] and checkpoint["frequency"] == frequency)
        require("AUDIT_BOUNDARY_MISMATCH", checkpoint["boundary_type"] == boundary_type and checkpoint["boundary_ref"] == boundary_ref)
        require("AUDIT_MEMBERSHIP_MISMATCH", checkpoint["membership_refs"] == membership)
        expected_handoffs = [ref for task_ref in membership for ref in task_contracts[task_ref]["handoff_refs"]]
        expected_targets = [f"{row['path']}={row['digest']}" for ref in expected_handoffs for row in handoff_records[ref]["target_digests"]]
        expected_primary = [task_contracts[task_ref]["task_validation"]["primary_route"]["validator_ref"] for task_ref in membership]
        coverage = {
            "membership_refs": membership,
            "covered_handoff_refs": expected_handoffs,
            "covered_target_digests": expected_targets,
            "primary_validation_refs": expected_primary,
            "final_validator_refs": final_validator_refs,
        }
        require("AUDIT_COVERAGE_DIGEST_MISMATCH", checkpoint["coverage_digest"] == canonical_digest(coverage))
        require("AUDIT_HANDOFF_COVERAGE_MISMATCH", checkpoint["covered_handoff_refs"] == expected_handoffs)
        require("AUDIT_TARGET_COVERAGE_MISMATCH", checkpoint["covered_target_digests"] == expected_targets)
        require("AUDIT_PRIMARY_VALIDATION_COVERAGE_MISMATCH", checkpoint["primary_validation_refs"] == expected_primary)
        require("AUDIT_FINAL_VALIDATOR_COVERAGE_MISMATCH", checkpoint["final_validator_refs"] == final_validator_refs)
        expected_writers = list(dict.fromkeys(task_contracts[ref]["writer_identity"] for ref in membership))
        require("AUDIT_WRITER_COVERAGE_MISMATCH", checkpoint["writer_identities"] == expected_writers)
        require("AUDIT_PRIMARY_VALIDATOR_NOT_INDEPENDENT", checkpoint["auditor_identity"] not in primary_identities)
        validate_record_evidence(reader, checkpoint["auditor_run_refs"])
        validate_record_evidence(reader, checkpoint["finding_refs"])
        validate_record_evidence(reader, checkpoint["correction_refs"])
        validate_record_evidence(reader, checkpoint["evidence_refs"])
        require("AUDIT_INCREMENTAL_REPLAY_FORBIDDEN", not checkpoint["correction_refs"] or (checkpoint["replay"] and checkpoint["membership_refs"] == membership and checkpoint["coverage_digest"] == canonical_digest(coverage)))
        register_locator(locator_index, checkpoint_ref, "audit", checkpoint["audit_id"])
        checkpoint_records[checkpoint_ref] = checkpoint

    metrics = reader.read_json(state["execution_metrics_ref"])
    rule_metrics(metrics)
    require("METRICS_RUN_ID_MISMATCH", metrics["run_id"] == invocation["run_id"])
    require("METRICS_EXECUTION_ID_MISMATCH", metrics["execution_id"] == invocation["execution_id"])
    metrics_digest = bytes_digest(reader.read_bytes(state["execution_metrics_ref"]))
    require("STATE_METRICS_DIGEST_MISMATCH", state["execution_metrics_digest"] == metrics_digest)
    require("STATE_METRICS_STATUS_MISMATCH", state["execution_metrics_status"] == metrics["status"])
    require("STATE_METRICS_REASON_MISMATCH", state["execution_metrics_degradation_reason"] == metrics["degradation_reason"])

    terminal_records: dict[str, dict[str, Any]] = {}
    require("TERMINAL_EVIDENCE_REFS_INVALID", isinstance(state["terminal_evidence_refs"], list) and bool(state["terminal_evidence_refs"]) and len(state["terminal_evidence_refs"]) == len(set(state["terminal_evidence_refs"])))
    for evidence_ref in state["terminal_evidence_refs"]:
        evidence = closed_mapping("TERMINAL_EVIDENCE_SHAPE_INVALID", reader.read_json(evidence_ref), TERMINAL_EVIDENCE_KEYS)
        require("TERMINAL_EVIDENCE_SCHEMA_INVALID", evidence["schema_version"] == 1)
        require("TERMINAL_EVIDENCE_IDENTITY_MISMATCH", evidence["run_id"] == invocation["run_id"] and evidence["execution_id"] == invocation["execution_id"])
        require("TERMINAL_TASK_STATUS_MISMATCH", evidence["task_statuses"] == [{"task_ref": ref, "status": task_contracts[ref]["status"]} for ref in task_refs])
        expected_ac_refs = [f"{ref}#{ac['id']}" for ref in task_refs for ac in task_contracts[ref]["task_validation"]["acceptance_criteria"]]
        require("TERMINAL_AC_COVERAGE_MISMATCH", evidence["acceptance_criterion_refs"] == expected_ac_refs)
        require("TERMINAL_VALIDATOR_COVERAGE_MISMATCH", evidence["validator_refs"] == all_primary_validator_refs + final_validator_refs)
        require("TERMINAL_GATE_COVERAGE_MISMATCH", evidence["gate_refs"] == all_gate_refs)
        require("TERMINAL_AUDIT_COVERAGE_MISMATCH", evidence["audit_checkpoint_refs"] == checkpoint_refs)
        validate_record_evidence(reader, evidence["evidence_refs"])
        terminal_records[evidence_ref] = evidence

    result = closed_mapping("RESULT_V3_SHAPE_INVALID", reader.read_json(state["result_ref"]), RESULT_V3_KEYS)
    require("RESULT_SCHEMA_SUPERSEDED", result["schema_version"] == 3)
    require("RESULT_DIGEST_MISMATCH", result["result_digest"] == digest_without(result, "result_digest"))
    dashboard = closed_mapping("DASHBOARD_V3_SHAPE_INVALID", reader.read_json(state["dashboard_ref"]), DASHBOARD_V3_KEYS)
    require("DASHBOARD_SCHEMA_INVALID", dashboard["schema_version"] == 3)
    require("DASHBOARD_DIGEST_MISMATCH", dashboard["dashboard_digest"] == digest_without(dashboard, "dashboard_digest"))
    expected_task_results = [{"task_ref": ref, "status": task_contracts[ref]["status"], "evidence_refs": task_contracts[ref]["task_validation"]["evidence_refs"]} for ref in task_refs]
    expected_dashboard_tasks = [{"task_ref": ref, "status": task_contracts[ref]["status"]} for ref in task_refs]
    for projection, projection_name in ((result, "RESULT"), (dashboard, "DASHBOARD")):
        require(f"{projection_name}_RUN_ID_MISMATCH", projection["run_id"] == invocation["run_id"])
        require(f"{projection_name}_EXECUTION_ID_MISMATCH", projection["execution_id"] == invocation["execution_id"])
        require(f"{projection_name}_STATUS_MISMATCH", projection["status"] == state["status"])
        require(
            f"{projection_name}_AUDIT_CONFIGURATION_MISMATCH",
            projection["audit_configuration"]
            == state_audit_configuration
            == identity["audit_configuration"],
        )
        require(f"{projection_name}_AUDIT_REFS_MISMATCH", projection["audit_checkpoint_refs"] == checkpoint_refs)
        require(f"{projection_name}_FINAL_VALIDATORS_MISMATCH", projection["final_validator_refs"] == final_validator_refs)
        require(f"{projection_name}_TERMINAL_EVIDENCE_MISMATCH", projection["terminal_evidence_refs"] == state["terminal_evidence_refs"])
        require(f"{projection_name}_METRICS_REF_MISMATCH", projection["execution_metrics_ref"] == state["execution_metrics_ref"])
        require(f"{projection_name}_METRICS_DIGEST_MISMATCH", projection["execution_metrics_digest"] == metrics_digest)
        require(f"{projection_name}_METRICS_STATUS_MISMATCH", projection["execution_metrics_status"] == metrics["status"])
        require(f"{projection_name}_METRICS_REASON_MISMATCH", projection["execution_metrics_degradation_reason"] == metrics["degradation_reason"])
        require(f"{projection_name}_NEXT_ACTION_MISMATCH", projection["next_action"] == state["next_action"])
    require("RESULT_STATE_DIGEST_MISMATCH", result["state_digest"] == state["state_digest"])
    require("RESULT_TASKS_MISMATCH", result["task_results"] == expected_task_results)
    require("DASHBOARD_TASKS_MISMATCH", dashboard["tasks"] == expected_dashboard_tasks)

    packet = closed_mapping("CONSISTENCY_V2_SHAPE_INVALID", reader.read_json(invocation["consistency_packet_ref"]), CONSISTENCY_V2_KEYS)
    require("CONSISTENCY_SCHEMA_SUPERSEDED", packet["schema_version"] == 2)
    require("CONSISTENCY_IDENTITY_MISMATCH", packet["run_id"] == invocation["run_id"] and packet["execution_id"] == invocation["execution_id"])
    require("CONSISTENCY_STATUS_MISMATCH", packet["status"] == state["status"] == result["status"] == dashboard["status"])
    require(
        "CONSISTENCY_AUDIT_CONFIGURATION_MISMATCH",
        packet["audit_configuration"]
        == state_audit_configuration
        == identity["audit_configuration"],
    )
    require("CONSISTENCY_STATE_DIGEST_MISMATCH", packet["state_digest"] == state["state_digest"])
    require("CONSISTENCY_TASKS_MD_DIGEST_MISMATCH", packet["tasks_md_digest"] == bytes_digest(reader.read_bytes(tasks_ref)))
    require("CONSISTENCY_RESULT_MISMATCH", packet["result_ref"] == state["result_ref"] and packet["result_digest"] == bytes_digest(reader.read_bytes(state["result_ref"])))
    require("CONSISTENCY_DASHBOARD_MISMATCH", packet["dashboard_ref"] == state["dashboard_ref"] and packet["dashboard_digest"] == bytes_digest(reader.read_bytes(state["dashboard_ref"])))
    require("CONSISTENCY_METRICS_MISMATCH", packet["metrics_ref"] == state["execution_metrics_ref"] and packet["metrics_digest"] == metrics_digest)
    require("CONSISTENCY_AUDIT_REFS_MISMATCH", packet["audit_checkpoint_refs"] == checkpoint_refs)
    require("CONSISTENCY_AUDIT_DIGESTS_MISMATCH", packet["audit_checkpoint_digests"] == [bytes_digest(reader.read_bytes(ref)) for ref in checkpoint_refs])
    require("CONSISTENCY_TERMINAL_REFS_MISMATCH", packet["terminal_evidence_refs"] == state["terminal_evidence_refs"])
    require("CONSISTENCY_TERMINAL_DIGESTS_MISMATCH", packet["terminal_evidence_digests"] == [bytes_digest(reader.read_bytes(ref)) for ref in state["terminal_evidence_refs"]])
    validator_digest = canonical_digest({ref: bytes_digest(reader.read_bytes(ref)) for ref in all_primary_validator_refs + final_validator_refs})
    require("CONSISTENCY_VALIDATOR_DIGEST_MISMATCH", packet["validator_digest"] == validator_digest)
    require("TERMINAL_EVIDENCE_STATUS_MISMATCH", all(record["status"] == state["status"] for record in terminal_records.values()))

    if state["status"] in TERMINAL_SUCCESS:
        require("TERMINAL_TASK_INCOMPLETE", all(task["status"] == "passed" and task["task_validation"]["status"] == "passed" for task in task_contracts.values()))
        require("TERMINAL_VALIDATOR_INCOMPLETE", all(record["result"] == "passed" for record in list(validator_records.values()) + list(final_records.values())))
        require("TERMINAL_GATE_INCOMPLETE", all(record["status"] == "passed" for record in gate_records.values()))
        require("TERMINAL_AUDIT_INCOMPLETE", all(record["status"] in {"approved", "not-applicable"} for record in checkpoint_records.values()))

    return {
        "status": "passed",
        "schema_version": 1,
        "run_id": invocation["run_id"],
        "execution_id": invocation["execution_id"],
        "tasks": len(task_refs),
        "audit_boundaries": len(checkpoint_refs),
        "files_read": len(reader._bytes),
    }


def fixture_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def fixture_write_json(root: Path, ref: str, value: Any) -> None:
    path = root / ref
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(fixture_json_bytes(value))


def fixture_write_markdown_json(root: Path, ref: str, heading: str, value: Any) -> None:
    path = root / ref
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
    path.write_text(f"# {heading}\n\n```json\n{encoded}\n```\n", encoding="utf-8")


def fixture_audit_configuration(frequency: str, source: str) -> dict[str, Any]:
    configuration = {
        "schema_version": 1,
        "frequency": frequency,
        "source": source,
        "policy_digest": "",
    }
    configuration["policy_digest"] = canonical_digest(
        {
            key: configuration[key]
            for key in ("schema_version", "frequency", "source")
        }
    )
    return configuration


def build_real_run_fixture(root: Path, frequency: str = "phase", source: str = "default") -> tuple[str, str]:
    plan_dir = "planos/real-run"
    tasks_ref = f"{plan_dir}/tasks.md"
    invocation_ref = f"{plan_dir}/execution-input.json"
    demand_ref = f"{plan_dir}/demanda.md"
    analysis_ref = f"{plan_dir}/analise.md"
    task_ref = f"{plan_dir}/task-1.md"
    target_ref = "src/feature.txt"
    validator_ref = f"{plan_dir}/evidence/task-1-validator.json"
    final_validator_ref = f"{plan_dir}/evidence/final-validator.json"
    handoff_ref = f"{plan_dir}/evidence/task-1-handoff.json"
    gate_ref = f"{plan_dir}/evidence/task-1-gate.json"
    checkpoint_ref = f"{plan_dir}/evidence/phase-audit.json"
    terminal_ref = f"{plan_dir}/evidence/terminal.json"
    metrics_ref = f"{plan_dir}/evidence/execution-metrics.json"
    result_ref = f"{plan_dir}/result.json"
    dashboard_ref = f"{plan_dir}/dashboard.json"
    consistency_ref = f"{plan_dir}/consistency.json"
    evidence_ref = f"{plan_dir}/evidence/observed.log"
    audit_run_ref = f"{plan_dir}/evidence/auditor-run.log"

    (root / demand_ref).parent.mkdir(parents=True, exist_ok=True)
    (root / demand_ref).write_text("Implement the validated fixture.\n", encoding="utf-8")
    (root / analysis_ref).write_text("# Analysis\n\nDecision-complete fixture.\n", encoding="utf-8")
    (root / target_ref).parent.mkdir(parents=True, exist_ok=True)
    (root / target_ref).write_text("validated output\n", encoding="utf-8")
    (root / evidence_ref).parent.mkdir(parents=True, exist_ok=True)
    (root / evidence_ref).write_text("validator and acceptance evidence\n", encoding="utf-8")
    (root / audit_run_ref).write_text("independent audit observation\n", encoding="utf-8")

    audit_config = fixture_audit_configuration(frequency, source)
    identity = {
        "schema_version": 2,
        "command": "loki-implement-feature",
        "demand_digest": bytes_digest((root / demand_ref).read_bytes()),
        "analysis_digest": bytes_digest((root / analysis_ref).read_bytes()),
        "plan_directory": plan_dir,
        "retry_limit": 3,
        "audit_configuration": audit_config,
    }
    run_id = derive_typed_id("loki-run-v2", identity)
    execution_id = derive_typed_id("loki-execution-v2", {"run_id": run_id, "command_identity": identity})
    invocation = {
        "schema_version": 2,
        "command_identity": identity,
        "run_id": run_id,
        "execution_id": execution_id,
        "demand_ref": demand_ref,
        "analysis_ref": analysis_ref,
        "state_ref": tasks_ref,
        "result_ref": result_ref,
        "dashboard_ref": dashboard_ref,
        "consistency_packet_ref": consistency_ref,
    }
    fixture_write_json(root, invocation_ref, invocation)

    validator = {
        "schema_version": 1,
        "validator_id": "validator-v1:task-1",
        "identity": "deterministic-validator:task-1",
        "task_ref": task_ref,
        "acceptance_criterion_refs": ["AC-1"],
        "evidence_refs": [evidence_ref],
        "result": "passed",
    }
    final_validator = {
        "schema_version": 1,
        "validator_id": "validator-v1:final",
        "identity": "deterministic-validator:final",
        "task_ref": None,
        "acceptance_criterion_refs": [f"{task_ref}#AC-1"],
        "evidence_refs": [evidence_ref],
        "result": "passed",
    }
    handoff = {
        "schema_version": 1,
        "handoff_id": "handoff-v1:task-1",
        "task_ref": task_ref,
        "writer_identity": "writer:task-1",
        "target_digests": [{"path": target_ref, "digest": bytes_digest((root / target_ref).read_bytes())}],
        "evidence_refs": [evidence_ref],
    }
    gate = {
        "schema_version": 1,
        "gate_id": "gate-v1:approval",
        "task_ref": task_ref,
        "status": "passed",
        "evidence_refs": [evidence_ref],
    }
    fixture_write_json(root, validator_ref, validator)
    fixture_write_json(root, final_validator_ref, final_validator)
    fixture_write_json(root, handoff_ref, handoff)
    fixture_write_json(root, gate_ref, gate)

    if frequency == "task":
        boundary_type, boundary_ref, membership = "task", task_ref, [task_ref]
    elif frequency == "phase":
        boundary_type, boundary_ref, membership = "phase", "phase:fase1", [task_ref]
    else:
        boundary_type, boundary_ref, membership = "plan", plan_dir, [task_ref]
    target_digest_rows = [f"{target_ref}={handoff['target_digests'][0]['digest']}"]
    coverage = {
        "membership_refs": membership,
        "covered_handoff_refs": [handoff_ref],
        "covered_target_digests": target_digest_rows,
        "primary_validation_refs": [validator_ref],
        "final_validator_refs": [final_validator_ref],
    }
    checkpoint = {
        "schema_version": 1,
        "audit_id": "",
        "run_id": run_id,
        "execution_id": execution_id,
        "policy_digest": audit_config["policy_digest"],
        "frequency": frequency,
        "boundary_type": boundary_type,
        "boundary_ref": boundary_ref,
        "iteration": 0,
        "predecessor_audit_ref": None,
        "replay": False,
        "replay_cause": None,
        "membership_refs": membership,
        "coverage_digest": canonical_digest(coverage),
        "covered_handoff_refs": [handoff_ref],
        "covered_target_digests": target_digest_rows,
        "primary_validation_refs": [validator_ref],
        "final_validator_refs": [final_validator_ref],
        "auditor_identity": "auditor:independent",
        "writer_identities": ["writer:task-1"],
        "auditor_run_refs": [audit_run_ref],
        "finding_refs": [],
        "correction_refs": [],
        "evidence_refs": [evidence_ref],
        "status": "approved",
        "next_action": "reconcile terminal state",
    }
    checkpoint["audit_id"] = derive_typed_id("execution-audit-v1", audit_identity_material(checkpoint))
    fixture_write_json(root, checkpoint_ref, checkpoint)

    task_contract = {
        "schema_version": 1,
        "task_id": "task-1",
        "phase": "fase1",
        "status": "passed",
        "dependencies": [],
        "target_files": [target_ref],
        "writer_identity": "writer:task-1",
        "handoff_refs": [handoff_ref],
        "gate_refs": [gate_ref],
        "audit_checkpoint_refs": [checkpoint_ref],
        "task_validation": {
            "schema_version": 1,
            "acceptance_criteria": [{"id": "AC-1", "statement": "Real bytes are validated.", "required": True}],
            "primary_route": {"type": "deterministic", "validator_ref": validator_ref},
            "evidence_refs": [evidence_ref],
            "status": "passed",
        },
    }
    fixture_write_markdown_json(root, task_ref, "task-1", {"task_contract": task_contract})

    metrics_cases, _ = load_fixtures()
    metrics = deepcopy(next(case["payload"] for case in metrics_cases if case["id"] == "metrics-exact"))
    metrics["run_id"] = run_id
    metrics["execution_id"] = execution_id
    digest_hex = metrics_hash(metrics)
    metrics["metrics_id"] = f"execution-metrics-v1:{digest_hex}"
    metrics["metrics_digest"] = f"sha256:{digest_hex}"
    fixture_write_json(root, metrics_ref, metrics)
    metrics_bytes_digest = bytes_digest((root / metrics_ref).read_bytes())

    terminal = {
        "schema_version": 1,
        "run_id": run_id,
        "execution_id": execution_id,
        "status": "completed",
        "task_statuses": [{"task_ref": task_ref, "status": "passed"}],
        "acceptance_criterion_refs": [f"{task_ref}#AC-1"],
        "validator_refs": [validator_ref, final_validator_ref],
        "gate_refs": [gate_ref],
        "audit_checkpoint_refs": [checkpoint_ref],
        "evidence_refs": [evidence_ref],
    }
    fixture_write_json(root, terminal_ref, terminal)

    state = {
        "schema_version": 3,
        "run_id": run_id,
        "execution_id": execution_id,
        "command_identity_digest": canonical_digest(identity),
        "execution_input_digest": bytes_digest((root / invocation_ref).read_bytes()),
        "audit_configuration": deepcopy(audit_config),
        "status": "completed",
        "task_refs": [task_ref],
        "audit_checkpoint_refs": [checkpoint_ref],
        "result_ref": result_ref,
        "dashboard_ref": dashboard_ref,
        "consistency_packet_ref": consistency_ref,
        "terminal_evidence_refs": [terminal_ref],
        "execution_metrics_ref": metrics_ref,
        "execution_metrics_digest": metrics_bytes_digest,
        "execution_metrics_status": metrics["status"],
        "execution_metrics_degradation_reason": metrics["degradation_reason"],
        "next_action": "none",
        "state_digest": "",
    }
    state["state_digest"] = digest_without(state, "state_digest")
    result = {
        "schema_version": 3,
        "run_id": run_id,
        "execution_id": execution_id,
        "status": "completed",
        "state_digest": state["state_digest"],
        "audit_configuration": audit_config,
        "audit_checkpoint_refs": [checkpoint_ref],
        "task_results": [{"task_ref": task_ref, "status": "passed", "evidence_refs": [evidence_ref]}],
        "final_validator_refs": [final_validator_ref],
        "terminal_evidence_refs": [terminal_ref],
        "execution_metrics_ref": metrics_ref,
        "execution_metrics_digest": metrics_bytes_digest,
        "execution_metrics_status": metrics["status"],
        "execution_metrics_degradation_reason": metrics["degradation_reason"],
        "next_action": "none",
        "result_digest": "",
    }
    result["result_digest"] = digest_without(result, "result_digest")
    dashboard = {
        "schema_version": 3,
        "run_id": run_id,
        "execution_id": execution_id,
        "status": "completed",
        "audit_configuration": audit_config,
        "audit_checkpoint_refs": [checkpoint_ref],
        "tasks": [{"task_ref": task_ref, "status": "passed"}],
        "final_validator_refs": [final_validator_ref],
        "terminal_evidence_refs": [terminal_ref],
        "execution_metrics_ref": metrics_ref,
        "execution_metrics_digest": metrics_bytes_digest,
        "execution_metrics_status": metrics["status"],
        "execution_metrics_degradation_reason": metrics["degradation_reason"],
        "next_action": "none",
        "dashboard_digest": "",
    }
    dashboard["dashboard_digest"] = digest_without(dashboard, "dashboard_digest")
    fixture_write_json(root, result_ref, result)
    fixture_write_json(root, dashboard_ref, dashboard)
    fixture_write_markdown_json(root, tasks_ref, "Run plan", {"loki_run_plan": {"schema_version": 1, "task_refs": [task_ref], "final_validator_refs": [final_validator_ref]}, "loki_run_state": state})

    consistency = {
        "schema_version": 2,
        "run_id": run_id,
        "execution_id": execution_id,
        "status": "completed",
        "audit_configuration": audit_config,
        "state_digest": state["state_digest"],
        "tasks_md_digest": bytes_digest((root / tasks_ref).read_bytes()),
        "result_ref": result_ref,
        "result_digest": bytes_digest((root / result_ref).read_bytes()),
        "dashboard_ref": dashboard_ref,
        "dashboard_digest": bytes_digest((root / dashboard_ref).read_bytes()),
        "metrics_ref": metrics_ref,
        "metrics_digest": metrics_bytes_digest,
        "audit_checkpoint_refs": [checkpoint_ref],
        "audit_checkpoint_digests": [bytes_digest((root / checkpoint_ref).read_bytes())],
        "terminal_evidence_refs": [terminal_ref],
        "terminal_evidence_digests": [bytes_digest((root / terminal_ref).read_bytes())],
        "validator_digest": canonical_digest({ref: bytes_digest((root / ref).read_bytes()) for ref in [validator_ref, final_validator_ref]}),
    }
    fixture_write_json(root, consistency_ref, consistency)
    return tasks_ref, invocation_ref


def mutate_fixture_json(root: Path, ref: str, mutation: Callable[[dict[str, Any]], None]) -> None:
    document = json.loads((root / ref).read_text(encoding="utf-8"))
    mutation(document)
    fixture_write_json(root, ref, document)


def mutate_fixture_markdown(root: Path, ref: str, mutation: Callable[[dict[str, Any]], None]) -> None:
    reader = RealRunReader(root)
    document = reader.read_markdown_json(ref)
    mutation(document)
    fixture_write_markdown_json(root, ref, "Mutated contract", document)


def mutate_fixture_state(
    root: Path,
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    tasks_ref = "planos/real-run/tasks.md"
    document = RealRunReader(root).read_markdown_json(tasks_ref)
    state = document["loki_run_state"]
    mutation(state)
    if "state_digest" in state:
        state["state_digest"] = digest_without(state, "state_digest")
    fixture_write_markdown_json(root, tasks_ref, "Mutated contract", document)


def mutate_state_audit_configuration_field(
    root: Path,
    field: str,
    value: Any,
) -> None:
    mutate_fixture_state(
        root,
        lambda state: state["audit_configuration"].update(
            {field: deepcopy(value)}
        ),
    )


def mutate_state_audit_configuration_schema_version(
    root: Path,
    value: Any,
) -> None:
    def mutation(state: dict[str, Any]) -> None:
        configuration = state["audit_configuration"]
        configuration["schema_version"] = deepcopy(value)
        configuration["policy_digest"] = canonical_digest(
            {
                key: configuration[key]
                for key in ("schema_version", "frequency", "source")
            }
        )

    mutate_fixture_state(root, mutation)


def mutate_audit_checkpoint_field(
    root: Path,
    field: str,
    value: Any,
) -> None:
    mutate_fixture_json(
        root,
        "planos/real-run/evidence/phase-audit.json",
        lambda checkpoint: checkpoint.update({field: deepcopy(value)}),
    )


def mutate_terminal_audit_finding(root: Path) -> None:
    checkpoint_ref = "planos/real-run/evidence/phase-audit.json"
    mutate_fixture_json(root, checkpoint_ref, lambda doc: doc.update(status="finding"))
    mutate_fixture_json(
        root,
        "planos/real-run/consistency.json",
        lambda doc: doc.update(audit_checkpoint_digests=[bytes_digest((root / checkpoint_ref).read_bytes())]),
    )


def mutate_non_success_terminal_evidence_mismatch(root: Path) -> None:
    tasks_ref = "planos/real-run/tasks.md"
    result_ref = "planos/real-run/result.json"
    dashboard_ref = "planos/real-run/dashboard.json"
    consistency_ref = "planos/real-run/consistency.json"

    tasks_document = RealRunReader(root).read_markdown_json(tasks_ref)
    state = tasks_document["loki_run_state"]
    state["status"] = "failed"
    state["state_digest"] = digest_without(state, "state_digest")
    fixture_write_markdown_json(root, tasks_ref, "Mutated contract", tasks_document)

    result = json.loads((root / result_ref).read_text(encoding="utf-8"))
    result["status"] = "failed"
    result["state_digest"] = state["state_digest"]
    result["result_digest"] = digest_without(result, "result_digest")
    fixture_write_json(root, result_ref, result)

    dashboard = json.loads((root / dashboard_ref).read_text(encoding="utf-8"))
    dashboard["status"] = "failed"
    dashboard["dashboard_digest"] = digest_without(dashboard, "dashboard_digest")
    fixture_write_json(root, dashboard_ref, dashboard)

    consistency = json.loads((root / consistency_ref).read_text(encoding="utf-8"))
    consistency["status"] = "failed"
    consistency["state_digest"] = state["state_digest"]
    consistency["tasks_md_digest"] = bytes_digest((root / tasks_ref).read_bytes())
    consistency["result_digest"] = bytes_digest((root / result_ref).read_bytes())
    consistency["dashboard_digest"] = bytes_digest((root / dashboard_ref).read_bytes())
    fixture_write_json(root, consistency_ref, consistency)


def real_run_self_test() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="loki-real-run-") as temp:
        root = Path(temp)
        tasks_ref, invocation_ref = build_real_run_fixture(root)
        validate_real_run(root, tasks_ref, invocation_ref)
        results.append({"id": "real-run-positive", "result": "accepted"})
    for frequency in ("task", "plan"):
        with tempfile.TemporaryDirectory(prefix="loki-real-run-") as temp:
            root = Path(temp)
            tasks_ref, invocation_ref = build_real_run_fixture(root, frequency=frequency, source="explicit")
            validate_real_run(root, tasks_ref, invocation_ref)
            results.append({"id": f"real-run-{frequency}-boundary", "result": "accepted"})

    mutations: list[tuple[str, str, Callable[[Path], None]]] = [
        ("real-run-target-bytes", "HANDOFF_TARGET_DIGEST_MISMATCH", lambda root: (root / "src/feature.txt").write_text("mutated bytes\n", encoding="utf-8")),
        ("real-run-self-attested-flag", "EXECUTION_INPUT_SHAPE_INVALID", lambda root: mutate_fixture_json(root, "planos/real-run/execution-input.json", lambda doc: doc.update(schema_valid=True))),
        ("real-run-state-digest", "STATE_DIGEST_MISMATCH", lambda root: mutate_fixture_markdown(root, "planos/real-run/tasks.md", lambda doc: doc["loki_run_state"].update(state_digest="sha256:" + "0" * 64))),
        ("real-run-state-audit-configuration-missing", "STATE_V3_SHAPE_INVALID", lambda root: mutate_fixture_state(root, lambda state: state.pop("audit_configuration"))),
        ("real-run-state-extra-field", "STATE_V3_SHAPE_INVALID", lambda root: mutate_fixture_state(root, lambda state: state.update(unexpected_state_field=True))),
        ("real-run-state-audit-configuration-extra-field", "AUDIT_CONFIGURATION_SHAPE_INVALID", lambda root: mutate_fixture_state(root, lambda state: state["audit_configuration"].update(unexpected_configuration_field=True))),
        ("real-run-state-audit-frequency-divergence", "STATE_AUDIT_CONFIGURATION_MISMATCH", lambda root: mutate_fixture_state(root, lambda state: state.update(audit_configuration=fixture_audit_configuration("task", "explicit")))),
        ("real-run-state-audit-source-divergence", "STATE_AUDIT_CONFIGURATION_MISMATCH", lambda root: mutate_fixture_state(root, lambda state: state.update(audit_configuration=fixture_audit_configuration("phase", "explicit")))),
        ("real-run-state-audit-policy-digest-divergence", "AUDIT_POLICY_DIGEST_INVALID", lambda root: mutate_fixture_state(root, lambda state: state["audit_configuration"].update(policy_digest="sha256:" + "0" * 64))),
        ("real-run-state-audit-schema-version-boolean", "AUDIT_CONFIGURATION_SCHEMA_INVALID", lambda root: mutate_state_audit_configuration_schema_version(root, True)),
        ("real-run-demand-bytes", "DEMAND_DIGEST_MISMATCH", lambda root: (root / "planos/real-run/demanda.md").write_text("mutated demand\n", encoding="utf-8")),
        ("real-run-audit-membership", "AUDIT_MEMBERSHIP_MISMATCH", lambda root: mutate_fixture_json(root, "planos/real-run/evidence/phase-audit.json", lambda doc: doc.update(membership_refs=["planos/real-run/task-1.md", "planos/real-run/task-x.md"]))),
        ("real-run-writer-auditor", "AUDIT_CHECKPOINT_NOT_INDEPENDENT", lambda root: mutate_fixture_json(root, "planos/real-run/evidence/phase-audit.json", lambda doc: doc.update(auditor_identity="writer:task-1"))),
        ("real-run-dag-ref", "TASK_DEPENDENCY_MISSING", lambda root: mutate_fixture_markdown(root, "planos/real-run/task-1.md", lambda doc: doc["task_contract"].update(dependencies=["task-missing"]))),
        ("real-run-terminal-audit", "TERMINAL_AUDIT_INCOMPLETE", mutate_terminal_audit_finding),
        ("real-run-result-status", "RESULT_STATUS_MISMATCH", lambda root: mutate_fixture_json(root, "planos/real-run/result.json", lambda doc: (doc.update(status="failed"), doc.update(result_digest=digest_without(doc, "result_digest"))))),
        ("real-run-non-success-terminal-evidence", "TERMINAL_EVIDENCE_STATUS_MISMATCH", mutate_non_success_terminal_evidence_mismatch),
    ]
    malformed_audit_scalars: tuple[tuple[str, Any], ...] = (
        ("array", ["phase"]),
        ("object", {"value": "phase"}),
        ("number", 1),
        ("boolean", True),
        ("null", None),
    )
    for field, expected in (
        ("frequency", "AUDIT_FREQUENCY_TYPE_INVALID"),
        ("source", "AUDIT_FREQUENCY_SOURCE_TYPE_INVALID"),
    ):
        for type_name, value in malformed_audit_scalars:
            mutations.append(
                (
                    f"real-run-state-audit-{field}-{type_name}",
                    expected,
                    lambda root, field=field, value=value: (
                        mutate_state_audit_configuration_field(root, field, value)
                    ),
                )
            )
    malformed_checkpoint_fields: tuple[tuple[str, str, Any, str], ...] = (
        (
            "schema-version-boolean",
            "schema_version",
            True,
            "AUDIT_CHECKPOINT_SCHEMA_INVALID",
        ),
        (
            "run-id-array",
            "run_id",
            ["loki-run-v2:invalid"],
            "AUDIT_CHECKPOINT_RUN_ID_INVALID",
        ),
        (
            "execution-id-array",
            "execution_id",
            ["loki-execution-v2:invalid"],
            "AUDIT_CHECKPOINT_EXECUTION_ID_INVALID",
        ),
        (
            "policy-digest-array",
            "policy_digest",
            ["sha256:invalid"],
            "AUDIT_CHECKPOINT_POLICY_DIGEST_INVALID",
        ),
        (
            "frequency-array",
            "frequency",
            ["phase"],
            "AUDIT_CHECKPOINT_FREQUENCY_INVALID",
        ),
        (
            "boundary-type-array",
            "boundary_type",
            ["phase"],
            "AUDIT_CHECKPOINT_BOUNDARY_INVALID",
        ),
        (
            "coverage-digest-array",
            "coverage_digest",
            ["sha256:invalid"],
            "AUDIT_CHECKPOINT_COVERAGE_INVALID",
        ),
        (
            "status-array",
            "status",
            ["approved"],
            "AUDIT_CHECKPOINT_STATUS_INVALID",
        ),
        (
            "membership-object-item",
            "membership_refs",
            [{"value": "planos/real-run/task-1.md"}],
            "AUDIT_CHECKPOINT_LIST_INVALID",
        ),
        (
            "covered-target-digest-object-item",
            "covered_target_digests",
            [{"value": "src/feature.txt=sha256:invalid"}],
            "AUDIT_CHECKPOINT_LIST_INVALID",
        ),
    )
    for case_suffix, field, value, expected in malformed_checkpoint_fields:
        mutations.append(
            (
                f"real-run-checkpoint-{case_suffix}",
                expected,
                lambda root, field=field, value=value: (
                    mutate_audit_checkpoint_field(root, field, value)
                ),
            )
        )
    for case_id, expected, mutation in mutations:
        with tempfile.TemporaryDirectory(prefix="loki-real-run-") as temp:
            root = Path(temp)
            tasks_ref, invocation_ref = build_real_run_fixture(root)
            mutation(root)
            try:
                validate_real_run(root, tasks_ref, invocation_ref)
            except ContractError as exc:
                require("REAL_RUN_MUTATION_ERROR_MISMATCH", str(exc) == expected)
            else:
                raise ContractError(f"REAL_RUN_MUTATION_ACCEPTED:{case_id}")
            results.append({"id": case_id, "result": "expected-rejection"})
    with tempfile.TemporaryDirectory(prefix="loki-real-run-") as temp:
        root = Path(temp)
        tasks_ref, invocation_ref = build_real_run_fixture(root)
        target = root / "src/feature.txt"
        real_target = root / "src/real-feature.txt"
        target.rename(real_target)
        target.symlink_to(real_target)
        try:
            validate_real_run(root, tasks_ref, invocation_ref)
        except ContractError as exc:
            require("REAL_RUN_SYMLINK_ERROR_MISMATCH", str(exc) == "REF_SYMLINK_FORBIDDEN")
        else:
            raise ContractError("REAL_RUN_SYMLINK_ACCEPTED")
        results.append({"id": "real-run-symlink", "result": "expected-rejection"})
    return results


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
    "response-normative-conflict": rule_response_normative_conflict,
    "manual": rule_manual,
    "current-schema": rule_current_schema,
    "metrics": rule_metrics,
    "metrics-resume": rule_metrics_resume,
    "liveness": rule_liveness,
    "materiality-gate": rule_materiality_gate,
    "cost-policy": rule_cost_policy,
    "audit-configuration": rule_audit_configuration,
    "audit-checkpoint": rule_audit_checkpoint,
    "audit-replay": rule_audit_replay,
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
    require(
        "MATRIX_EXCLUSION_ROUTE_INVALID",
        all(item.get("routed_to") == "scripts/validate-install-loki-upgrade.py" and nonempty(item.get("reason")) for item in exclusions),
    )
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
    real_results = real_run_self_test()
    results.extend(real_results)
    return {
        "status": "passed",
        "schema_version": 1,
        "fixture_files": list(FIXTURE_FILES),
        "matrix_total": len(MATRIX_SCENARIOS),
        "matrix_implemented": len(MATRIX_SCENARIOS) - len(INSTALLER_EXCLUSIONS),
        "matrix_excluded": len(INSTALLER_EXCLUSIONS),
        "excluded_scenarios": sorted(INSTALLER_EXCLUSIONS),
        "exclusion_destination": "scripts/validate-install-loki-upgrade.py",
        "supplemental_required": sorted(REQUIRED_SUPPLEMENTAL),
        "cases_executed": len(results),
        "real_run_cases": len(real_results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run every current contract fixture")
    parser.add_argument("--consistency-packet", metavar="PATH", help="validate one executable cross-surface consistency packet")
    parser.add_argument("--project-root", metavar="PATH", help="project root containing one persisted run")
    parser.add_argument("--tasks-md", metavar="PATH", help="strict planos descendant tasks.md path")
    parser.add_argument("--invocation-input", metavar="PATH", help="normalized execution input v2 JSON path")
    args = parser.parse_args()
    real_mode = any((args.project_root, args.tasks_md, args.invocation_input))
    if sum((args.self_test, bool(args.consistency_packet), real_mode)) != 1:
        parser.error("select exactly one mode: --self-test, --consistency-packet PATH, or the three real-run arguments")
    if real_mode and not all((args.project_root, args.tasks_md, args.invocation_input)):
        parser.error("real-run mode requires --project-root, --tasks-md, and --invocation-input")
    try:
        if args.self_test:
            result = self_test()
        elif args.consistency_packet:
            document = json.loads(Path(args.consistency_packet).read_text(encoding="utf-8"))
            require("CONSISTENCY_WRAPPER_INVALID", set(document) == {"consistency_packet"} and isinstance(document["consistency_packet"], dict))
            validate_consistency_packet(document["consistency_packet"])
            result = {"status": "passed", "schema_version": 2, "packet": args.consistency_packet}
        else:
            result = validate_real_run(Path(args.project_root), args.tasks_md, args.invocation_input)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    except (ContractError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
