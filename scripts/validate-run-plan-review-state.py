#!/usr/bin/env python3
"""Validate standalone Loki Write Test review state embedded in Markdown."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


FREQUENCIES = ("write_agent_handoff", "task", "fase", "plano")
TERMINAL_SCOPES = ("task", "fase", "plano")
POLICY_SOURCES = {"explicit", "default", "propagated", "resumed"}
CHECKPOINT_STATUSES = {
    "scheduled",
    "dispatched",
    "completed-clean",
    "completed-with-findings",
    "skipped-no-material-write",
    "skipped-agent-unavailable",
    "failed-consultive",
    "outcome-unknown",
}
TERMINAL_CHECKPOINT_STATUSES = CHECKPOINT_STATUSES - {"scheduled", "dispatched"}
DEGRADED_CHECKPOINT_STATUSES = {
    "skipped-agent-unavailable",
    "failed-consultive",
    "outcome-unknown",
}
RECONCILIATION_STATUSES = {
    "not-evaluated",
    "reused-terminal",
    "reconcile-dispatched",
    "new-coverage-checkpoint-required",
    "policy-conflict",
    "outcome-unknown",
}
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
CHECKPOINT_ID_RE = re.compile(r"^review-checkpoint-v1:[0-9a-f]{64}$")
RAW_CLEAN_STATUSES = {"approved", "clean", "passed", "success", "no-findings"}
RAW_FINDING_STATUSES = {"blocked", "finding", "findings", "changes-requested"}
RAW_FAILURE_STATUSES = {"error", "failed", "failure", "timeout"}
FENCE_RE = re.compile(r"```(?:yaml|yml)?\s*\n(.*?)\n```", re.DOTALL)


class StateError(ValueError):
    """An actionable persisted-state validation failure."""


class InputError(ValueError):
    """An invocation path could not be read as an input file."""


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def effective_frequency(requested: str, terminal_scope: str) -> str:
    if requested not in FREQUENCIES:
        raise StateError(f"policy.requested_frequency: invalid value {requested!r}")
    if terminal_scope not in TERMINAL_SCOPES:
        raise StateError(f"policy.terminal_scope: invalid value {terminal_scope!r}")
    return FREQUENCIES[min(FREQUENCIES.index(requested), FREQUENCIES.index(terminal_scope))]


def normalize_paths(values: list[str], locator: str = "paths") -> list[str]:
    normalized: set[str] = set()
    for index, value in enumerate(values):
        normalized.add(validate_relative_posix_path(value, f"{locator}[{index}]"))
    return sorted(normalized)


def validate_relative_posix_path(value: Any, locator: str) -> str:
    if not isinstance(value, str) or not value:
        raise StateError(f"{locator}: non-empty path required")
    if "\\" in value or value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise StateError(f"{locator}: path must be package/plan-relative POSIX")
    segments = value.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise StateError(f"{locator}: path contains empty, dot, or traversal segment")
    return value


def is_material_handoff(
    *,
    category_is_write_agent: bool,
    task_scoped_writer: bool,
    terminal_completion: bool,
    changed_files: list[str],
    approved_targets: list[str],
    correlated_evidence_persisted: bool,
) -> tuple[bool, list[str]]:
    changed_targets = sorted(
        set(normalize_paths(changed_files, "materiality.changed_files"))
        & set(normalize_paths(approved_targets, "materiality.approved_targets"))
    )
    material = all(
        (
            category_is_write_agent,
            task_scoped_writer,
            terminal_completion,
            bool(changed_targets),
            correlated_evidence_persisted,
        )
    )
    return material, changed_targets


def checkpoint_identity(
    execution_id: str,
    policy_digest: str,
    boundary_type: str,
    boundary_ref: str,
    coverage_digest: str,
) -> str:
    digest = canonical_digest(
        [execution_id, policy_digest, boundary_type, boundary_ref, coverage_digest]
    ).split(":", 1)[1]
    return "review-checkpoint-v1:" + digest


def review_handoff_identity(checkpoint_id: str) -> str:
    if not CHECKPOINT_ID_RE.fullmatch(checkpoint_id):
        raise StateError("review_handoff_id: checkpoint identity is invalid")
    return "review-handoff-v1:" + checkpoint_id.split(":", 1)[1]


def resume_decision(checkpoint: dict[str, Any], current_coverage_digest: str) -> str:
    """Derive the only safe resume action from canonical persisted fields."""
    if checkpoint.get("coverage_digest") != current_coverage_digest:
        return "new-coverage-checkpoint-required"
    status = checkpoint.get("status")
    if status in TERMINAL_CHECKPOINT_STATUSES:
        return "reused-terminal"
    if status == "dispatched":
        return "reconcile-dispatched"
    if status == "scheduled":
        return "continue-scheduled"
    raise StateError(f"resume: invalid checkpoint status {status!r}")


def _scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return None
    if value in {"null", "~"}:
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value[0:1] in {"'", '"'}:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise StateError(f"invalid quoted scalar {value!r}") from exc
    if value.startswith("[") or value.startswith("{"):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise StateError(f"invalid flow value {value!r}") from exc
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    return value


def _mapping_pair(content: str, line_number: int) -> tuple[str, str]:
    if ":" not in content:
        raise StateError(f"line {line_number}: expected key: value")
    key, value = content.split(":", 1)
    key = key.strip()
    if not key:
        raise StateError(f"line {line_number}: empty mapping key")
    return key, value.strip()


def parse_yaml_subset(source: str) -> dict[str, Any]:
    """Parse the deterministic mapping/list subset used by Loki state blocks."""
    tokens: list[tuple[int, str, int]] = []
    for number, raw in enumerate(source.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#") or raw.strip() == "---":
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise StateError(f"line {number}: tabs are not allowed for indentation")
        indent = len(raw) - len(raw.lstrip(" "))
        tokens.append((indent, raw.strip(), number))
    if not tokens:
        raise StateError("empty YAML state block")

    def parse_node(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(tokens) or tokens[index][0] != indent:
            raise StateError("invalid indentation in YAML state block")
        is_list = tokens[index][1].startswith("-")
        result: Any = [] if is_list else {}
        while index < len(tokens):
            current_indent, content, number = tokens[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise StateError(f"line {number}: unexpected indentation")
            if is_list:
                if not content.startswith("-"):
                    break
                item_text = content[1:].strip()
                index += 1
                if not item_text:
                    if index >= len(tokens) or tokens[index][0] <= indent:
                        result.append(None)
                    else:
                        item, index = parse_node(index, tokens[index][0])
                        result.append(item)
                    continue
                if ":" in item_text:
                    key, raw_value = _mapping_pair(item_text, number)
                    item_map: dict[str, Any] = {}
                    if raw_value:
                        item_map[key] = _scalar(raw_value)
                    elif index < len(tokens) and tokens[index][0] > indent:
                        item_map[key], index = parse_node(index, tokens[index][0])
                    else:
                        item_map[key] = None
                    if index < len(tokens) and tokens[index][0] > indent:
                        continuation, index = parse_node(index, tokens[index][0])
                        if not isinstance(continuation, dict):
                            raise StateError(f"line {number}: list mapping continuation must be a mapping")
                        duplicate = set(item_map) & set(continuation)
                        if duplicate:
                            raise StateError(f"line {number}: duplicate key {sorted(duplicate)[0]}")
                        item_map.update(continuation)
                    result.append(item_map)
                else:
                    result.append(_scalar(item_text))
            else:
                if content.startswith("-"):
                    break
                key, raw_value = _mapping_pair(content, number)
                if key in result:
                    raise StateError(f"line {number}: duplicate key {key}")
                index += 1
                if raw_value:
                    result[key] = _scalar(raw_value)
                elif index < len(tokens) and tokens[index][0] > indent:
                    result[key], index = parse_node(index, tokens[index][0])
                else:
                    result[key] = None
        return result, index

    parsed, end = parse_node(0, tokens[0][0])
    if end != len(tokens) or not isinstance(parsed, dict):
        raise StateError("state block must contain exactly one root mapping")
    return parsed


def extract_state(path: Path, root_key: str) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"{path}: cannot read: {exc}") from exc
    matches: list[dict[str, Any]] = []
    for fenced in FENCE_RE.findall(text):
        if re.search(rf"(?m)^\s*{re.escape(root_key)}\s*:", fenced):
            parsed = parse_yaml_subset(fenced)
            value = parsed.get(root_key)
            if not isinstance(value, dict):
                raise StateError(f"{path}: {root_key} must be a mapping")
            matches.append(value)
    if len(matches) != 1:
        raise StateError(f"{path}: expected exactly one {root_key} fenced block, found {len(matches)}")
    return matches[0]


def _require(mapping: dict[str, Any], key: str, locator: str) -> Any:
    if key not in mapping:
        raise StateError(f"{locator}: missing {key}")
    return mapping[key]


def validate_policy(policy: dict[str, Any]) -> None:
    locator = "loki_plan_state.write_test_review.policy"
    required = {
        "schema_version",
        "requested_frequency",
        "effective_frequency",
        "source",
        "terminal_scope",
        "selected_agent",
        "policy_digest",
    }
    missing = sorted(required - set(policy))
    if missing:
        raise StateError(f"{locator}: missing {', '.join(missing)}")
    if set(policy) != required:
        raise StateError(f"{locator}: exact schema rejects extra keys")
    if type(policy["schema_version"]) is not int or policy["schema_version"] != 1:
        raise StateError(f"{locator}.schema_version: expected 1")
    requested = str(policy["requested_frequency"])
    terminal_scope = str(policy["terminal_scope"])
    expected_effective = effective_frequency(requested, terminal_scope)
    if policy["effective_frequency"] != expected_effective:
        raise StateError(
            f"{locator}.effective_frequency: expected {expected_effective!r}"
        )
    if policy["source"] not in POLICY_SOURCES:
        raise StateError(f"{locator}.source: invalid value {policy['source']!r}")
    if policy["source"] == "default" and requested != "task":
        raise StateError(f"{locator}: source=default requires requested_frequency='task'")
    selected = policy["selected_agent"]
    if not isinstance(selected, dict) or set(selected) != {"name", "selection_reason"}:
        raise StateError(f"{locator}.selected_agent: exact schema requires name and selection_reason")
    if not isinstance(selected.get("selection_reason"), str) or not selected["selection_reason"].strip():
        raise StateError(f"{locator}.selected_agent: selection_reason is required")
    selected_name = selected["name"]
    if selected_name is not None and (
        not isinstance(selected_name, str) or not selected_name.strip()
    ):
        raise StateError(f"{locator}.selected_agent.name: expected null or non-empty string")
    digest = policy["policy_digest"]
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise StateError(f"{locator}.policy_digest: invalid SHA-256")
    digest_input = {key: value for key, value in policy.items() if key != "policy_digest"}
    if digest != canonical_digest(digest_input):
        raise StateError(f"{locator}.policy_digest: digest mismatch")


def validate_checkpoint(
    checkpoint: dict[str, Any],
    policy_digest: str,
    effective_frequency_value: str,
    selected_agent_name: str | None,
) -> None:
    locator = f"review_checkpoint[{checkpoint.get('checkpoint_id', '<missing>')}]"
    required = {
        "schema_version",
        "checkpoint_id",
        "execution_id",
        "policy_digest",
        "boundary_type",
        "boundary_ref",
        "coverage_digest",
        "coverage_manifest",
        "covered_write_handoff_ids",
        "status",
        "review_agent_run_id",
        "review_handoff_id",
        "review_agent_raw_status",
        "execution_status_effect",
        "evidence_ref",
        "findings",
        "risk_refs",
        "backlog_refs",
        "reason",
    }
    missing = sorted(required - set(checkpoint))
    if missing:
        raise StateError(f"{locator}: missing {', '.join(missing)}")
    if set(checkpoint) != required:
        raise StateError(f"{locator}: exact schema rejects extra keys")
    if type(checkpoint["schema_version"]) is not int or checkpoint["schema_version"] != 1:
        raise StateError(f"{locator}.schema_version: expected 1")
    if checkpoint["policy_digest"] != policy_digest:
        raise StateError(f"{locator}.policy_digest: active policy mismatch")
    if not isinstance(checkpoint["execution_id"], str) or not checkpoint["execution_id"].strip():
        raise StateError(f"{locator}.execution_id: non-empty value required")
    if not isinstance(checkpoint["boundary_ref"], str) or not checkpoint["boundary_ref"].strip():
        raise StateError(f"{locator}.boundary_ref: non-empty value required")
    boundary_type = checkpoint["boundary_type"]
    if boundary_type not in FREQUENCIES:
        raise StateError(f"{locator}.boundary_type: invalid value {boundary_type!r}")
    if boundary_type != effective_frequency_value:
        raise StateError(f"{locator}.boundary_type: active effective frequency mismatch")
    status = checkpoint["status"]
    if status not in CHECKPOINT_STATUSES:
        raise StateError(f"{locator}.status: invalid value {status!r}")
    if checkpoint["execution_status_effect"] != "none":
        raise StateError(f"{locator}.execution_status_effect: must be 'none'")
    manifest = checkpoint["coverage_manifest"]
    if not isinstance(manifest, dict):
        raise StateError(f"{locator}.coverage_manifest: expected mapping")
    if set(manifest) != {"schema_version", "handoffs", "reviewer"}:
        raise StateError(f"{locator}.coverage_manifest: requires exactly schema_version, handoffs, reviewer")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise StateError(f"{locator}.coverage_manifest.schema_version: expected 1")
    reviewer = manifest["reviewer"]
    if not isinstance(reviewer, dict) or set(reviewer) != {
        "name",
        "contract_version",
        "selection_configuration_digest",
    }:
        raise StateError(f"{locator}.coverage_manifest.reviewer: incomplete schema")
    if reviewer["name"] is not None and (
        not isinstance(reviewer["name"], str) or not reviewer["name"].strip()
    ):
        raise StateError(f"{locator}.coverage_manifest.reviewer.name: expected null or non-empty string")
    if reviewer["name"] != selected_agent_name:
        raise StateError(f"{locator}.coverage_manifest.reviewer.name: active policy selection mismatch")
    if not isinstance(reviewer["contract_version"], str) or not reviewer["contract_version"].strip():
        raise StateError(f"{locator}.coverage_manifest.reviewer.contract_version: required")
    if not SHA256_RE.fullmatch(str(reviewer["selection_configuration_digest"])):
        raise StateError(f"{locator}.coverage_manifest.reviewer.selection_configuration_digest: invalid SHA-256")
    handoffs = manifest.get("handoffs", [])
    if not isinstance(handoffs, list):
        raise StateError(f"{locator}.coverage_manifest.handoffs: expected list")
    handoff_ids: list[str] = []
    for index, handoff in enumerate(handoffs):
        required_handoff = {"handoff_id", "completion_ref", "evidence_ref", "changed_files"}
        if not isinstance(handoff, dict) or set(handoff) != required_handoff:
            raise StateError(f"{locator}.coverage_manifest.handoffs[{index}]: incomplete handoff schema")
        if any(
            not isinstance(handoff.get(field), str) or not handoff[field].strip()
            for field in ("handoff_id", "completion_ref", "evidence_ref")
        ):
            raise StateError(f"{locator}.coverage_manifest.handoffs[{index}]: IDs and refs must be non-empty")
        handoff_ids.append(str(handoff["handoff_id"]))
        changed = handoff.get("changed_files", [])
        if not isinstance(changed, list) or not changed:
            raise StateError(f"{locator}.coverage_manifest.handoffs[{index}].changed_files: non-empty list required")
        paths = [item.get("path", "") for item in changed if isinstance(item, dict)]
        if paths != sorted(set(paths)):
            raise StateError(f"{locator}.coverage_manifest.handoffs[{index}].changed_files: paths must be sorted and unique")
        for changed_index, item in enumerate(changed):
            if (
                not isinstance(item, dict)
                or set(item) != {"path", "sha256"}
                or not isinstance(item.get("sha256"), str)
                or not SHA256_RE.fullmatch(item["sha256"])
            ):
                raise StateError(f"{locator}.coverage_manifest.handoffs[{index}].changed_files: invalid sha256")
            validate_relative_posix_path(
                item.get("path"),
                f"{locator}.coverage_manifest.handoffs[{index}].changed_files[{changed_index}].path",
            )
    if handoff_ids != sorted(set(handoff_ids)):
        raise StateError(f"{locator}.coverage_manifest.handoffs: IDs must be sorted and unique")
    if checkpoint["covered_write_handoff_ids"] != handoff_ids:
        raise StateError(f"{locator}.covered_write_handoff_ids: coverage mismatch")
    for field in ("findings", "risk_refs", "backlog_refs"):
        values = checkpoint[field]
        if (
            not isinstance(values, list)
            or any(not isinstance(value, str) or not value.strip() for value in values)
            or values != sorted(set(values))
        ):
            raise StateError(f"{locator}.{field}: non-empty strings must be sorted and unique")
    for field in (
        "review_agent_run_id",
        "review_handoff_id",
        "review_agent_raw_status",
        "evidence_ref",
    ):
        value = checkpoint[field]
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise StateError(f"{locator}.{field}: expected null or non-empty string")
    reason = checkpoint["reason"]
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        raise StateError(f"{locator}.reason: expected null or non-empty string")
    if checkpoint["coverage_digest"] != canonical_digest(manifest):
        raise StateError(f"{locator}.coverage_digest: digest mismatch")
    expected_id = checkpoint_identity(
        str(checkpoint["execution_id"]),
        str(checkpoint["policy_digest"]),
        str(boundary_type),
        str(checkpoint["boundary_ref"]),
        str(checkpoint["coverage_digest"]),
    )
    if checkpoint["checkpoint_id"] != expected_id or not CHECKPOINT_ID_RE.fullmatch(str(checkpoint["checkpoint_id"])):
        raise StateError(f"{locator}.checkpoint_id: deterministic identity mismatch")
    expected_review_handoff = review_handoff_identity(str(checkpoint["checkpoint_id"]))
    if status == "scheduled":
        forbidden = (
            checkpoint["review_agent_run_id"],
            checkpoint["review_handoff_id"],
            checkpoint["review_agent_raw_status"],
            checkpoint["evidence_ref"],
            checkpoint["reason"],
        )
        if any(value is not None for value in forbidden) or checkpoint["findings"] or checkpoint["risk_refs"] or checkpoint["backlog_refs"]:
            raise StateError(f"{locator}: scheduled checkpoint must not contain dispatch or result fields")
    if status == "dispatched":
        if selected_agent_name is None:
            raise StateError(f"{locator}: dispatched checkpoint requires selected agent")
        if checkpoint["review_handoff_id"] != expected_review_handoff:
            raise StateError(f"{locator}: dispatched checkpoint requires deterministic review_handoff_id")
        if checkpoint["review_agent_raw_status"] is not None or checkpoint["evidence_ref"] is not None or checkpoint["reason"] is not None:
            raise StateError(f"{locator}: dispatched checkpoint cannot contain terminal result fields")
        if checkpoint["findings"] or checkpoint["risk_refs"] or checkpoint["backlog_refs"]:
            raise StateError(f"{locator}: dispatched checkpoint cannot contain consultive result lists")
    if status != "skipped-no-material-write" and not handoff_ids:
        raise StateError(f"{locator}: status {status} requires non-empty material coverage")
    if status == "skipped-no-material-write":
        if handoff_ids:
            raise StateError(f"{locator}: skipped-no-material-write requires empty coverage")
        if checkpoint["review_handoff_id"] is not None or checkpoint["review_agent_run_id"] is not None:
            raise StateError(f"{locator}: skipped-no-material-write requires zero invocation")
        if checkpoint["review_agent_raw_status"] is not None or checkpoint["evidence_ref"] is not None or not checkpoint["reason"]:
            raise StateError(f"{locator}: skipped-no-material-write requires reason and no result fields")
    if status == "skipped-agent-unavailable":
        if selected_agent_name is not None or reviewer["name"] is not None:
            raise StateError(f"{locator}: skipped-agent-unavailable requires null selected reviewer")
        if checkpoint["review_handoff_id"] is not None or checkpoint["review_agent_run_id"] is not None:
            raise StateError(f"{locator}: skipped-agent-unavailable must not contain dispatch identity")
        if checkpoint["review_agent_raw_status"] is not None or checkpoint["evidence_ref"] is not None:
            raise StateError(f"{locator}: skipped-agent-unavailable must not contain reviewer result")
    if status == "completed-with-findings" and (
        not checkpoint["findings"] or not checkpoint["risk_refs"]
    ):
        raise StateError(f"{locator}: completed-with-findings requires findings and risk_refs")
    if status in {"completed-clean", "completed-with-findings"} and reason is not None:
        raise StateError(f"{locator}: completed reviewer result requires null reason")
    if status in DEGRADED_CHECKPOINT_STATUSES and (
        not checkpoint["reason"] or not checkpoint["risk_refs"]
    ):
        raise StateError(f"{locator}: degraded status requires reason and risk_refs")
    if status in {"completed-clean", "completed-with-findings", "failed-consultive"} and not checkpoint["evidence_ref"]:
        raise StateError(f"{locator}: terminal reviewer result requires evidence_ref")
    if status in {"completed-clean", "completed-with-findings", "failed-consultive", "outcome-unknown"}:
        if selected_agent_name is None:
            raise StateError(f"{locator}: dispatched reviewer result requires selected agent")
        if checkpoint["review_handoff_id"] != expected_review_handoff:
            raise StateError(f"{locator}: terminal dispatched result requires deterministic review_handoff_id")
    raw_status = str(checkpoint["review_agent_raw_status"] or "").lower()
    if status == "completed-clean":
        if checkpoint["findings"] or checkpoint["risk_refs"]:
            raise StateError(f"{locator}: raw blocked/findings cannot map to completed-clean")
    expected_status_for_raw = None
    if raw_status in RAW_CLEAN_STATUSES:
        expected_status_for_raw = "completed-clean"
    elif raw_status in RAW_FINDING_STATUSES:
        expected_status_for_raw = "completed-with-findings"
    elif raw_status in RAW_FAILURE_STATUSES:
        expected_status_for_raw = "failed-consultive"
    if expected_status_for_raw and status != expected_status_for_raw:
        raise StateError(
            f"{locator}: raw reviewer status {raw_status!r} requires {expected_status_for_raw}"
        )
    if status in {"completed-clean", "completed-with-findings", "failed-consultive"} and not raw_status:
        raise StateError(f"{locator}: terminal reviewer result requires raw status")
    if status == "outcome-unknown" and not checkpoint["review_handoff_id"]:
        raise StateError(f"{locator}: outcome-unknown must retain persisted dispatch identity")


def validate_states(plan_state: dict[str, Any], task_states: list[dict[str, Any]]) -> None:
    review = plan_state.get("write_test_review")
    if not isinstance(review, dict):
        raise StateError("loki_plan_state.write_test_review: missing mapping")
    required_review = {"policy", "checkpoints", "risks", "next_action"}
    missing_review = sorted(required_review - set(review))
    if missing_review:
        raise StateError(
            "loki_plan_state.write_test_review: missing " + ", ".join(missing_review)
        )
    allowed_review = required_review | {"state_errors"}
    if not set(review).issubset(allowed_review):
        raise StateError("loki_plan_state.write_test_review: exact schema rejects extra keys")
    risks = review["risks"]
    if (
        not isinstance(risks, list)
        or any(not isinstance(value, str) or not value.strip() for value in risks)
        or risks != sorted(set(risks))
    ):
        raise StateError(
            "loki_plan_state.write_test_review.risks: non-empty strings must be sorted and unique"
        )
    if not isinstance(review["next_action"], str) or not review["next_action"].strip():
        raise StateError("loki_plan_state.write_test_review.next_action: non-empty action required")
    policy = review.get("policy")
    if not isinstance(policy, dict):
        raise StateError("loki_plan_state.write_test_review.policy: missing mapping")
    validate_policy(policy)
    checkpoints = review.get("checkpoints")
    if not isinstance(checkpoints, list):
        raise StateError("loki_plan_state.write_test_review.checkpoints: expected list")
    seen: dict[str, dict[str, Any]] = {}
    seen_review_handoffs: set[str] = set()
    for checkpoint in checkpoints:
        if not isinstance(checkpoint, dict):
            raise StateError("loki_plan_state.write_test_review.checkpoints: item must be mapping")
        selected_name = policy["selected_agent"]["name"]
        validate_checkpoint(
            checkpoint,
            str(policy["policy_digest"]),
            str(policy["effective_frequency"]),
            selected_name,
        )
        checkpoint_id = str(checkpoint["checkpoint_id"])
        if checkpoint_id in seen:
            if seen[checkpoint_id] != checkpoint:
                raise StateError(f"review_checkpoint[{checkpoint_id}]: duplicate ID with conflicting content")
            raise StateError(f"review_checkpoint[{checkpoint_id}]: duplicate checkpoint")
        seen[checkpoint_id] = checkpoint
        review_handoff_id = checkpoint.get("review_handoff_id")
        if review_handoff_id:
            if review_handoff_id in seen_review_handoffs:
                raise StateError(f"review_checkpoint[{checkpoint_id}]: duplicate review_handoff_id")
            seen_review_handoffs.add(str(review_handoff_id))
    state_errors = review.get("state_errors", [])
    if not isinstance(state_errors, list):
        raise StateError("loki_plan_state.write_test_review.state_errors: expected list")
    required_state_error = {
        "code",
        "persisted_policy_digest",
        "supplied_requested_frequency",
        "reason",
        "next_action",
    }
    for error_index, error in enumerate(state_errors):
        error_locator = f"loki_plan_state.write_test_review.state_errors[{error_index}]"
        if not isinstance(error, dict) or set(error) != required_state_error:
            raise StateError(f"{error_locator}: incomplete or extra-key schema")
        if error["code"] not in {"policy-conflict", "checkpoint-integrity-conflict"}:
            raise StateError(f"{error_locator}.code: invalid value {error['code']!r}")
        if not isinstance(error["persisted_policy_digest"], str) or not SHA256_RE.fullmatch(
            error["persisted_policy_digest"]
        ):
            raise StateError(f"{error_locator}.persisted_policy_digest: invalid SHA-256")
        supplied = error["supplied_requested_frequency"]
        if supplied is not None and supplied not in FREQUENCIES:
            raise StateError(f"{error_locator}.supplied_requested_frequency: invalid value")
        for field in ("reason", "next_action"):
            if not isinstance(error[field], str) or not error[field].strip():
                raise StateError(f"{error_locator}.{field}: non-empty string required")
        raise StateError(
            f"loki_plan_state.write_test_review.state_errors: unresolved {error['code']}"
        )
    for index, task_state in enumerate(task_states):
        task_review = task_state.get("write_test_review")
        if not isinstance(task_review, dict):
            raise StateError(f"task_state[{index}].write_test_review: missing mapping")
        locator = f"task_state[{index}].write_test_review"
        required_task_review = {"policy_ref", "policy_digest", "local_coverage", "checkpoint_refs", "reconciliation"}
        missing_task = sorted(required_task_review - set(task_review))
        if missing_task:
            raise StateError(f"{locator}: missing {', '.join(missing_task)}")
        if set(task_review) != required_task_review:
            raise StateError(f"{locator}: exact schema rejects extra keys")
        if not isinstance(task_review["policy_ref"], str) or not task_review["policy_ref"].strip():
            raise StateError(f"{locator}.policy_ref: non-empty reference required")
        if task_review.get("policy_digest") != policy["policy_digest"]:
            raise StateError(f"{locator}.policy_digest: active policy mismatch")
        local = task_review["local_coverage"]
        required_local = {
            "boundary_type",
            "boundary_ref",
            "coverage_digest",
            "covered_write_handoff_ids",
            "changed_target_files",
            "completion_refs",
            "evidence_refs",
        }
        if not isinstance(local, dict) or set(local) != required_local:
            raise StateError(f"{locator}.local_coverage: incomplete schema")
        if (
            local["boundary_type"] != "task"
            or not isinstance(local["boundary_ref"], str)
            or not local["boundary_ref"].strip()
        ):
            raise StateError(f"{locator}.local_coverage: invalid task boundary")
        if not SHA256_RE.fullmatch(str(local["coverage_digest"])):
            raise StateError(f"{locator}.local_coverage.coverage_digest: invalid SHA-256")
        for field in ("covered_write_handoff_ids", "changed_target_files", "completion_refs", "evidence_refs"):
            values = local[field]
            if (
                not isinstance(values, list)
                or any(not isinstance(value, str) or not value.strip() for value in values)
                or values != sorted(set(values))
            ):
                raise StateError(
                    f"{locator}.local_coverage.{field}: non-empty strings must be sorted and unique"
                )
        for changed_index, path in enumerate(local["changed_target_files"]):
            validate_relative_posix_path(
                path, f"{locator}.local_coverage.changed_target_files[{changed_index}]"
            )
        refs = task_review.get("checkpoint_refs", [])
        if not isinstance(refs, list):
            raise StateError(f"{locator}.checkpoint_refs: expected list")
        ref_ids: list[str] = []
        ref_locators: list[str] = []
        refs_by_locator: dict[str, dict[str, Any]] = {}
        for ref in refs:
            required_ref = {
                "checkpoint_id",
                "checkpoint_ref",
                "boundary_type",
                "boundary_ref",
                "coverage_digest",
                "status",
            }
            if (
                not isinstance(ref, dict)
                or set(ref) != required_ref
                or not isinstance(ref.get("checkpoint_id"), str)
                or not ref["checkpoint_id"].strip()
                or not isinstance(ref.get("checkpoint_ref"), str)
                or not ref["checkpoint_ref"].strip()
            ):
                raise StateError(f"{locator}.checkpoint_refs: invalid reference")
            ref_ids.append(str(ref["checkpoint_id"]))
            ref_locators.append(str(ref["checkpoint_ref"]))
            if ref["checkpoint_id"] not in seen:
                raise StateError(f"{locator}.checkpoint_refs: unknown checkpoint {ref['checkpoint_id']}")
            canonical = seen[str(ref["checkpoint_id"])]
            for field in ("boundary_type", "boundary_ref", "coverage_digest", "status"):
                if ref.get(field) != canonical.get(field):
                    raise StateError(f"{locator}.checkpoint_refs: {field} mismatch")
            refs_by_locator[str(ref["checkpoint_ref"])] = canonical
        if len(ref_ids) != len(set(ref_ids)):
            raise StateError(f"{locator}.checkpoint_refs: duplicate reference")
        if len(ref_locators) != len(set(ref_locators)):
            raise StateError(f"{locator}.checkpoint_refs: duplicate checkpoint_ref locator")
        reconciliation = task_review.get("reconciliation", {})
        required_reconciliation = {
            "status",
            "previous_checkpoint_ref",
            "current_coverage_digest",
            "reason",
            "next_action",
        }
        if not isinstance(reconciliation, dict) or set(reconciliation) != required_reconciliation:
            raise StateError(f"{locator}.reconciliation: incomplete schema")
        status = reconciliation.get("status", "not-evaluated") if isinstance(reconciliation, dict) else ""
        if status not in RECONCILIATION_STATUSES:
            raise StateError(f"{locator}.reconciliation.status: invalid value {status!r}")
        if status == "policy-conflict":
            raise StateError(f"{locator}.reconciliation: unresolved policy-conflict")
        current_digest = reconciliation.get("current_coverage_digest")
        if not SHA256_RE.fullmatch(str(current_digest)):
            raise StateError(f"{locator}.reconciliation.current_coverage_digest: invalid SHA-256")
        if current_digest != local["coverage_digest"]:
            raise StateError(
                f"{locator}.reconciliation.current_coverage_digest: local coverage mismatch"
            )
        previous_ref = reconciliation.get("previous_checkpoint_ref")
        if previous_ref is not None and (
            not isinstance(previous_ref, str) or not previous_ref.strip()
        ):
            raise StateError(f"{locator}.reconciliation.previous_checkpoint_ref: expected null or non-empty string")
        reconciliation_reason = reconciliation.get("reason")
        if reconciliation_reason is not None and (
            not isinstance(reconciliation_reason, str) or not reconciliation_reason.strip()
        ):
            raise StateError(f"{locator}.reconciliation.reason: expected null or non-empty string")
        if status not in {"policy-conflict", "outcome-unknown"} and reconciliation_reason is not None:
            raise StateError(f"{locator}.reconciliation.reason: status {status} requires null reason")
        previous = refs_by_locator.get(str(previous_ref)) if previous_ref is not None else None
        if status in {"reused-terminal", "reconcile-dispatched", "new-coverage-checkpoint-required", "outcome-unknown"} and previous is None:
            raise StateError(f"{locator}.reconciliation: status {status} requires referenced previous checkpoint")
        if status == "reused-terminal" and (
            previous["status"] not in TERMINAL_CHECKPOINT_STATUSES
            or previous["coverage_digest"] != current_digest
        ):
            raise StateError(f"{locator}.reconciliation: reused-terminal requires matching terminal checkpoint")
        if status == "reconcile-dispatched" and (
            previous["status"] != "dispatched" or previous["coverage_digest"] != current_digest
        ):
            raise StateError(f"{locator}.reconciliation: reconcile-dispatched requires matching dispatched checkpoint")
        if status == "new-coverage-checkpoint-required" and previous["coverage_digest"] == current_digest:
            raise StateError(f"{locator}.reconciliation: new coverage requires a changed digest")
        if status == "outcome-unknown" and (
            previous["status"] != "outcome-unknown"
            or previous["coverage_digest"] != current_digest
            or not reconciliation.get("reason")
        ):
            raise StateError(f"{locator}.reconciliation: outcome-unknown must correlate to terminal unknown checkpoint")
        if not isinstance(reconciliation.get("next_action"), str) or not reconciliation["next_action"].strip():
            raise StateError(f"{locator}.reconciliation.next_action: non-empty action required")


def _policy(
    requested: str = "task", scope: str = "plano", agent_name: str | None = "quality-auditor"
) -> dict[str, Any]:
    policy: dict[str, Any] = {
        "schema_version": 1,
        "requested_frequency": requested,
        "effective_frequency": effective_frequency(requested, scope),
        "source": "explicit",
        "terminal_scope": scope,
        "selected_agent": {
            "name": agent_name,
            "selection_reason": (
                "compatible metadata" if agent_name is not None else "no compatible agent available"
            ),
        },
    }
    policy["policy_digest"] = canonical_digest(policy)
    return policy


def _checkpoint(policy: dict[str, Any], status: str = "completed-clean", handoffs: int = 1) -> dict[str, Any]:
    manifest = {
        "schema_version": 1,
        "handoffs": [
            {
                "handoff_id": f"handoff-{index}",
                "completion_ref": f"completion-{index}.md",
                "evidence_ref": f"evidence-{index}.xml",
                "changed_files": [
                    {"path": f"target-{index}.md", "sha256": "sha256:" + f"{index + 1:064x}"}
                ],
            }
            for index in range(handoffs)
        ],
        "reviewer": {
            "name": policy["selected_agent"]["name"],
            "contract_version": "1",
            "selection_configuration_digest": "sha256:" + "a" * 64,
        },
    }
    coverage_digest = canonical_digest(manifest)
    checkpoint: dict[str, Any] = {
        "schema_version": 1,
        "execution_id": "execution-1",
        "policy_digest": policy["policy_digest"],
        "boundary_type": policy["effective_frequency"],
        "boundary_ref": "plan-1",
        "coverage_digest": coverage_digest,
        "coverage_manifest": manifest,
        "covered_write_handoff_ids": [item["handoff_id"] for item in manifest["handoffs"]],
        "status": status,
        "review_agent_run_id": None,
        "review_handoff_id": None,
        "review_agent_raw_status": None,
        "execution_status_effect": "none",
        "evidence_ref": None,
        "findings": [],
        "risk_refs": [],
        "backlog_refs": [],
        "reason": None,
    }
    if status == "completed-with-findings":
        checkpoint["findings"] = ["finding-1"]
        checkpoint["risk_refs"] = ["risk-1"]
        checkpoint["review_agent_raw_status"] = "blocked"
    if status == "completed-clean":
        checkpoint["review_agent_raw_status"] = "clean"
    if status in {"completed-clean", "completed-with-findings", "failed-consultive"}:
        checkpoint["review_agent_run_id"] = "agent-run-1"
        checkpoint["evidence_ref"] = "review-evidence.xml"
    if status == "dispatched":
        checkpoint["review_agent_run_id"] = "agent-run-1"
    if status == "skipped-no-material-write":
        checkpoint["reason"] = "no material write"
    if status == "skipped-agent-unavailable":
        checkpoint["review_handoff_id"] = None
        checkpoint["review_agent_run_id"] = None
        checkpoint["evidence_ref"] = None
        checkpoint["reason"] = "no compatible Write Test Agent"
        checkpoint["risk_refs"] = ["risk-unavailable"]
    if status in {"failed-consultive", "outcome-unknown"}:
        checkpoint["review_agent_raw_status"] = "error" if status == "failed-consultive" else None
        checkpoint["reason"] = "review result unavailable"
        checkpoint["risk_refs"] = ["risk-review"]
        if status == "outcome-unknown":
            checkpoint["evidence_ref"] = None
    checkpoint["checkpoint_id"] = checkpoint_identity(
        checkpoint["execution_id"],
        checkpoint["policy_digest"],
        checkpoint["boundary_type"],
        checkpoint["boundary_ref"],
        checkpoint["coverage_digest"],
    )
    if status in {"dispatched", "completed-clean", "completed-with-findings", "failed-consultive", "outcome-unknown"}:
        checkpoint["review_handoff_id"] = review_handoff_identity(checkpoint["checkpoint_id"])
    return checkpoint


def _checkpoint_ref(checkpoint: dict[str, Any], locator: str = "tasks.md#checkpoint-1") -> dict[str, Any]:
    return {
        "checkpoint_id": checkpoint["checkpoint_id"],
        "checkpoint_ref": locator,
        "boundary_type": checkpoint["boundary_type"],
        "boundary_ref": checkpoint["boundary_ref"],
        "coverage_digest": checkpoint["coverage_digest"],
        "status": checkpoint["status"],
    }


def _plan_state(
    policy: dict[str, Any], checkpoints: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "write_test_review": {
            "policy": policy,
            "checkpoints": checkpoints,
            "risks": [],
            "next_action": "continue from canonical persisted state",
        }
    }


def _task_state(
    policy: dict[str, Any],
    checkpoint: dict[str, Any],
    reconciliation_status: str = "reused-terminal",
) -> dict[str, Any]:
    checkpoint_locator = "tasks.md#checkpoint-1"
    return {
        "write_test_review": {
            "policy_ref": "tasks.md#write-test-review-policy",
            "policy_digest": policy["policy_digest"],
            "local_coverage": {
                "boundary_type": "task",
                "boundary_ref": "task-1.1",
                "coverage_digest": checkpoint["coverage_digest"],
                "covered_write_handoff_ids": checkpoint["covered_write_handoff_ids"],
                "changed_target_files": ["target-0.md"] if checkpoint["covered_write_handoff_ids"] else [],
                "completion_refs": ["completion-0.md"] if checkpoint["covered_write_handoff_ids"] else [],
                "evidence_refs": ["evidence-0.xml"] if checkpoint["covered_write_handoff_ids"] else [],
            },
            "checkpoint_refs": [_checkpoint_ref(checkpoint, checkpoint_locator)],
            "reconciliation": {
                "status": reconciliation_status,
                "previous_checkpoint_ref": checkpoint_locator,
                "current_coverage_digest": checkpoint["coverage_digest"],
                "reason": "dispatch outcome could not be recovered"
                if reconciliation_status == "outcome-unknown"
                else None,
                "next_action": "continue from persisted checkpoint",
            },
        }
    }


def run_self_test() -> None:
    observed = 0
    for scope in TERMINAL_SCOPES:
        for requested in FREQUENCIES:
            expected = FREQUENCIES[min(FREQUENCIES.index(requested), FREQUENCIES.index(scope))]
            assert effective_frequency(requested, scope) == expected
            observed += 1
    assert observed == 12

    for mask in range(32):
        flags = [bool(mask & (1 << bit)) for bit in range(5)]
        material, changed = is_material_handoff(
            category_is_write_agent=flags[0],
            task_scoped_writer=flags[1],
            terminal_completion=flags[2],
            changed_files=["target.md"] if flags[3] else ["other.md"],
            approved_targets=["target.md"],
            correlated_evidence_persisted=flags[4],
        )
        assert material is all(flags)
        assert bool(changed) is flags[3]
    material, changed = is_material_handoff(
        category_is_write_agent=True,
        task_scoped_writer=True,
        terminal_completion=True,
        changed_files=["dir/target.md"],
        approved_targets=["dir/target.md"],
        correlated_evidence_persisted=True,
    )
    assert material and changed == ["dir/target.md"]
    for unsafe_path in ("/absolute.md", "../outside.md", "a/../b.md", "dir\\x.md"):
        try:
            is_material_handoff(
                category_is_write_agent=True,
                task_scoped_writer=True,
                terminal_completion=True,
                changed_files=[unsafe_path],
                approved_targets=[unsafe_path],
                correlated_evidence_persisted=True,
            )
        except StateError as exc:
            assert "path" in str(exc)
        else:
            raise AssertionError(f"unsafe materiality path accepted: {unsafe_path}")

    policy = _policy()
    valid_statuses = (
        "scheduled",
        "dispatched",
        "completed-clean",
        "completed-with-findings",
        "skipped-no-material-write",
        "failed-consultive",
        "outcome-unknown",
    )
    for status in valid_statuses:
        handoffs = 0 if status == "skipped-no-material-write" else 1
        validate_states(
            _plan_state(policy, [_checkpoint(policy, status, handoffs)]),
            [],
        )
    unavailable_policy = _policy(agent_name=None)
    validate_states(
        _plan_state(
            unavailable_policy,
            [_checkpoint(unavailable_policy, "skipped-agent-unavailable")],
        ),
        [],
    )

    valid_task_checkpoint = _checkpoint(policy)
    validate_states(
        _plan_state(policy, [valid_task_checkpoint]),
        [_task_state(policy, valid_task_checkpoint)],
    )

    changed = _checkpoint(policy)
    changed_manifest = copy.deepcopy(changed["coverage_manifest"])
    changed_manifest["handoffs"][0]["changed_files"][0]["sha256"] = "sha256:" + "f" * 64
    assert canonical_digest(changed_manifest) != changed["coverage_digest"]
    assert resume_decision(changed, changed["coverage_digest"]) == "reused-terminal"
    assert resume_decision(changed, canonical_digest(changed_manifest)) == "new-coverage-checkpoint-required"
    dispatched = _checkpoint(policy)
    dispatched["status"] = "dispatched"
    dispatched["review_agent_raw_status"] = None
    dispatched["evidence_ref"] = None
    assert resume_decision(dispatched, dispatched["coverage_digest"]) == "reconcile-dispatched"

    def expect_invalid(
        plan: dict[str, Any], tasks: list[dict[str, Any]], fragment: str
    ) -> None:
        try:
            validate_states(plan, tasks)
        except StateError as exc:
            assert fragment in str(exc), (fragment, str(exc))
        else:
            raise AssertionError(f"expected failure containing {fragment!r}")

    def expect_failure(mutator: Any, fragment: str) -> None:
        plan = _plan_state(copy.deepcopy(policy), [_checkpoint(policy)])
        tasks: list[dict[str, Any]] = []
        mutator(plan, tasks)
        expect_invalid(plan, tasks, fragment)

    def state_error(code: str = "policy-conflict") -> dict[str, Any]:
        return {
            "code": code,
            "persisted_policy_digest": policy["policy_digest"],
            "supplied_requested_frequency": "fase",
            "reason": "persisted and supplied policies conflict",
            "next_action": "resolve the active policy",
        }

    expect_failure(lambda plan, _: plan["write_test_review"]["policy"].update(requested_frequency="invalid"), "invalid value")
    expect_failure(lambda plan, _: plan["write_test_review"]["policy"].update(source="default", requested_frequency="fase", effective_frequency="fase"), "source=default")
    expect_failure(lambda plan, _: plan["write_test_review"]["policy"]["selected_agent"].pop("name"), "selected_agent")
    expect_failure(lambda plan, _: plan["write_test_review"]["policy"].update(policy_digest="sha256:" + "0" * 64), "digest mismatch")
    expect_failure(lambda plan, _: plan["write_test_review"]["policy"].update(extra="value"), "extra keys")
    expect_failure(lambda plan, _: plan["write_test_review"]["policy"].update(schema_version="1"), "schema_version")
    expect_failure(lambda plan, _: plan["write_test_review"].pop("risks"), "missing risks")
    expect_failure(lambda plan, _: plan["write_test_review"].pop("next_action"), "missing next_action")
    expect_failure(lambda plan, _: plan["write_test_review"].update(risks="risk"), "risks")
    expect_failure(lambda plan, _: plan["write_test_review"].update(next_action=""), "next_action")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(checkpoint_id="review-checkpoint-v1:" + "0" * 64), "identity mismatch")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(extra="value"), "extra keys")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(boundary_type="fase"), "effective frequency mismatch")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(execution_id=""), "execution_id")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(boundary_ref=""), "boundary_ref")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0]["covered_write_handoff_ids"].append("z"), "coverage mismatch")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0]["coverage_manifest"].pop("reviewer"), "requires exactly")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0]["coverage_manifest"]["handoffs"][0].pop("completion_ref"), "incomplete handoff schema")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0]["coverage_manifest"]["handoffs"][0].update(extra="value"), "incomplete handoff schema")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0]["coverage_manifest"]["handoffs"][0].update(completion_ref=1), "IDs and refs")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0]["coverage_manifest"]["handoffs"][0].update(evidence_ref=1), "IDs and refs")
    for unsafe_path in ("/absolute.md", "../outside.md", "dir\\windows.md", "a/../b.md"):
        expect_failure(
            lambda plan, _, path=unsafe_path: plan["write_test_review"]["checkpoints"][0]["coverage_manifest"]["handoffs"][0]["changed_files"][0].update(path=path),
            "path",
        )
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(execution_status_effect="blocked"), "must be 'none'")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(findings="finding"), "findings")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(risk_refs="risk"), "risk_refs")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(backlog_refs="backlog"), "backlog_refs")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(findings=["finding", "finding"]), "findings")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(reason="unexpected"), "requires null reason")
    expect_invalid(_plan_state(policy, [{**_checkpoint(policy, "completed-with-findings"), "reason": "unexpected"}]), [], "requires null reason")
    expect_invalid(_plan_state(policy, [{**_checkpoint(policy, "failed-consultive"), "reason": 7}]), [], "reason")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(evidence_ref=7), "evidence_ref")
    expect_failure(lambda plan, _: plan["write_test_review"].update(state_errors=[state_error()]), "policy-conflict")
    expect_failure(lambda plan, _: plan["write_test_review"].update(state_errors=[state_error("checkpoint-integrity-conflict")]), "checkpoint-integrity-conflict")
    expect_failure(lambda plan, _: plan["write_test_review"].update(state_errors={}), "expected list")
    expect_failure(lambda plan, _: plan["write_test_review"].update(state_errors="error"), "expected list")
    expect_failure(lambda plan, _: plan["write_test_review"].update(state_errors=["error"]), "incomplete or extra-key schema")
    expect_failure(lambda plan, _: plan["write_test_review"].update(state_errors=[{"code": "policy-conflict"}]), "incomplete or extra-key schema")
    expect_failure(lambda plan, _: plan["write_test_review"].update(state_errors=[state_error("unknown")]), "invalid value")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"].append(copy.deepcopy(plan["write_test_review"]["checkpoints"][0])), "duplicate checkpoint")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(status="dispatched", review_handoff_id=None), "requires deterministic review_handoff_id")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(review_agent_raw_status="blocked"), "requires completed-with-findings")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0].update(review_handoff_id="review-handoff-v1:" + "0" * 64), "deterministic review_handoff_id")
    expect_failure(lambda plan, _: plan["write_test_review"].update(checkpoints=[{**_checkpoint(policy), "status": "scheduled"}]), "scheduled checkpoint must not contain")
    for zero_status in (
        "scheduled",
        "dispatched",
        "completed-clean",
        "completed-with-findings",
        "failed-consultive",
        "outcome-unknown",
    ):
        expect_invalid(
            _plan_state(policy, [_checkpoint(policy, zero_status, 0)]),
            [],
            "requires non-empty material coverage",
        )
    expect_failure(lambda plan, _: plan["write_test_review"].update(checkpoints=[{**_checkpoint(policy, "skipped-no-material-write", 0), "reason": None}]), "requires reason")
    expect_invalid(
        _plan_state(
            unavailable_policy,
            [{**_checkpoint(unavailable_policy, "skipped-agent-unavailable"), "review_handoff_id": review_handoff_identity(_checkpoint(unavailable_policy, "skipped-agent-unavailable")["checkpoint_id"])}],
        ),
        [],
        "must not contain dispatch identity",
    )
    expect_failure(lambda plan, _: plan["write_test_review"].update(checkpoints=[_checkpoint(policy, "skipped-agent-unavailable")]), "requires null selected reviewer")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"][0]["coverage_manifest"]["reviewer"].update(name=None), "selection mismatch")
    null_reviewer_policy = _policy(agent_name=None)
    expect_invalid(
        _plan_state(
            null_reviewer_policy,
            [_checkpoint(null_reviewer_policy, "dispatched")],
        ),
        [],
        "requires selected agent",
    )
    expect_invalid(
        _plan_state(
            null_reviewer_policy,
            [_checkpoint(null_reviewer_policy, "completed-clean")],
        ),
        [],
        "requires selected agent",
    )
    expect_failure(lambda plan, _: plan["write_test_review"].update(checkpoints=[{**_checkpoint(policy, "outcome-unknown"), "review_handoff_id": None}]), "requires deterministic review_handoff_id")
    expect_failure(lambda plan, _: plan["write_test_review"]["checkpoints"].append({**copy.deepcopy(plan["write_test_review"]["checkpoints"][0]), "checkpoint_id": checkpoint_identity("execution-1", policy["policy_digest"], "task", "other", plan["write_test_review"]["checkpoints"][0]["coverage_digest"]), "boundary_ref": "other"}), "deterministic review_handoff_id")
    def add_unknown_checkpoint(_: dict[str, Any], tasks: list[dict[str, Any]]) -> None:
        state = _task_state(policy, _checkpoint(policy))
        state["write_test_review"]["checkpoint_refs"][0]["checkpoint_id"] = "missing"
        tasks.append(state)

    expect_failure(add_unknown_checkpoint, "unknown checkpoint")
    expect_invalid(_plan_state(policy, [_checkpoint(policy)]), [{"status": "pending"}], "missing mapping")
    expect_failure(lambda plan, tasks: tasks.append({"write_test_review": {"policy_ref": "tasks.md#policy", "policy_digest": policy["policy_digest"], "checkpoint_refs": [], "reconciliation": {"status": "not-evaluated", "previous_checkpoint_ref": None, "current_coverage_digest": "sha256:" + "0" * 64, "reason": None, "next_action": "continue"}}}), "missing local_coverage")

    terminal = _checkpoint(policy)
    terminal_plan = _plan_state(policy, [terminal])
    reused_without_ref = _task_state(policy, terminal)
    reused_without_ref["write_test_review"]["reconciliation"]["previous_checkpoint_ref"] = None
    expect_invalid(terminal_plan, [reused_without_ref], "requires referenced previous checkpoint")

    dispatched_checkpoint = _checkpoint(policy, "dispatched")
    dispatched_plan = _plan_state(policy, [dispatched_checkpoint])
    validate_states(
        dispatched_plan,
        [_task_state(policy, dispatched_checkpoint, "reconcile-dispatched")],
    )
    wrong_dispatched = _task_state(policy, terminal, "reconcile-dispatched")
    expect_invalid(terminal_plan, [wrong_dispatched], "requires matching dispatched checkpoint")

    unchanged_new_coverage = _task_state(policy, terminal, "new-coverage-checkpoint-required")
    expect_invalid(terminal_plan, [unchanged_new_coverage], "requires a changed digest")
    changed_new_coverage = _task_state(policy, terminal, "new-coverage-checkpoint-required")
    changed_new_coverage["write_test_review"]["reconciliation"]["current_coverage_digest"] = "sha256:" + "f" * 64
    changed_new_coverage["write_test_review"]["local_coverage"]["coverage_digest"] = "sha256:" + "f" * 64
    validate_states(terminal_plan, [changed_new_coverage])

    mismatched_local = _task_state(policy, terminal)
    mismatched_local["write_test_review"]["local_coverage"]["coverage_digest"] = "sha256:" + "e" * 64
    expect_invalid(terminal_plan, [mismatched_local], "local coverage mismatch")
    mismatched_changed_local = _task_state(policy, terminal, "new-coverage-checkpoint-required")
    mismatched_changed_local["write_test_review"]["reconciliation"]["current_coverage_digest"] = "sha256:" + "f" * 64
    expect_invalid(terminal_plan, [mismatched_changed_local], "local coverage mismatch")

    unknown_checkpoint = _checkpoint(policy, "outcome-unknown")
    unknown_plan = _plan_state(policy, [unknown_checkpoint])
    validate_states(
        unknown_plan,
        [_task_state(policy, unknown_checkpoint, "outcome-unknown")],
    )
    mismatched_unknown = _task_state(policy, terminal, "outcome-unknown")
    expect_invalid(terminal_plan, [mismatched_unknown], "must correlate to terminal unknown checkpoint")

    unsafe_local = _task_state(policy, terminal)
    unsafe_local["write_test_review"]["local_coverage"]["changed_target_files"] = ["../outside.md"]
    expect_invalid(terminal_plan, [unsafe_local], "path")

    extra_local = _task_state(policy, terminal)
    extra_local["write_test_review"]["local_coverage"]["extra"] = "value"
    expect_invalid(terminal_plan, [extra_local], "local_coverage: incomplete schema")
    extra_reconciliation = _task_state(policy, terminal)
    extra_reconciliation["write_test_review"]["reconciliation"]["extra"] = "value"
    expect_invalid(terminal_plan, [extra_reconciliation], "reconciliation: incomplete schema")
    extra_checkpoint_ref = _task_state(policy, terminal)
    extra_checkpoint_ref["write_test_review"]["checkpoint_refs"][0]["extra"] = "value"
    expect_invalid(terminal_plan, [extra_checkpoint_ref], "invalid reference")

    second_checkpoint = copy.deepcopy(terminal)
    second_checkpoint["boundary_ref"] = "plan-2"
    second_checkpoint["checkpoint_id"] = checkpoint_identity(
        second_checkpoint["execution_id"],
        second_checkpoint["policy_digest"],
        second_checkpoint["boundary_type"],
        second_checkpoint["boundary_ref"],
        second_checkpoint["coverage_digest"],
    )
    second_checkpoint["review_handoff_id"] = review_handoff_identity(
        second_checkpoint["checkpoint_id"]
    )
    duplicate_locator = _task_state(policy, terminal)
    duplicate_locator["write_test_review"]["checkpoint_refs"].append(
        _checkpoint_ref(second_checkpoint, "tasks.md#checkpoint-1")
    )
    expect_invalid(
        _plan_state(policy, [terminal, second_checkpoint]),
        [duplicate_locator],
        "duplicate checkpoint_ref locator",
    )

    parsed = parse_yaml_subset("root:\n  schema_version: 1\n  values: [\"a\", \"b\"]\n")
    assert parsed == {"root": {"schema_version": 1, "values": ["a", "b"]}}
    with tempfile.TemporaryDirectory() as directory:
        sample = Path(directory) / "tasks.md"
        sample.write_text("```yaml\nloki_plan_state:\n  status: running\n```\n", encoding="utf-8")
        assert extract_state(sample, "loki_plan_state")["status"] == "running"
    print("self-test: passed (12 clamps, 32 materiality cases, canonical output, path, status, resume, and correlation invariants)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tasks_md", nargs="?", type=Path, help="Markdown plan containing loki_plan_state")
    parser.add_argument("--task-file", action="append", default=[], type=Path, help="Associated task Markdown; repeatable")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic in-memory tests")
    args = parser.parse_args(argv)
    if args.self_test:
        try:
            run_self_test()
        except (AssertionError, StateError) as exc:
            print(f"self-test: failed: {exc}", file=sys.stderr)
            return 1
        return 0
    if args.tasks_md is None:
        parser.error("TASKS_MD is required unless --self-test is used")
    if not args.tasks_md.is_file():
        print(f"input error: {args.tasks_md} is not a readable file", file=sys.stderr)
        return 2
    task_files = args.task_file or sorted(args.tasks_md.parent.glob("task-*.md"))
    for task_file in task_files:
        if not task_file.is_file():
            print(f"input error: {task_file} is not a readable file", file=sys.stderr)
            return 2
    try:
        plan_state = extract_state(args.tasks_md, "loki_plan_state")
        task_states = [extract_state(path, "loki_task_state") for path in task_files]
        validate_states(plan_state, task_states)
    except InputError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    except StateError as exc:
        print(f"invalid state: {exc}", file=sys.stderr)
        return 1
    print(f"run-plan review state: ok ({args.tasks_md}, task_files={len(task_files)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
